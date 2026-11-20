#!/usr/bin/env python3
"""Non-interactive SuperVideo client. Requires Python 3.10+; stdlib only."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import http.client
import importlib.util
import json
import math
import mimetypes
import os
from pathlib import Path
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

DEFAULT_BASE = "https://api.isupervideo.com"
DEFAULT_CHANNEL = "172c1482-00b4-4bb2-89e4-e8bde879c77c"
TERMINAL = {"succeeded", "failed", "cancelled"}
MAX_VIDEO_BYTES = 512 * 1024 * 1024


class Failure(Exception):
    """Only locally authored messages and bounded API codes reach the console."""
    def __init__(self, code, detail="", status=None):
        self.code, self.detail, self.status = code, detail, status
        super().__init__(code)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with tmp.open("x", encoding="utf-8", newline="\n") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def local_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise Failure("path_outside_project", "文件路径必须位于当前项目内")
    return path


@contextlib.contextmanager
def state_lock(folder):
    """OS-held lock releases on process death; no stale PID lock to delete."""
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "client.lock").open("a+b") as f:
        f.seek(0, 2)
        if f.tell() == 0:
            f.write(b"0")
            f.flush()
        f.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise Failure("already_running", "本集已有脚本运行，请勿同时启动第二次") from None
        try:
            yield
        finally:
            f.seek(0)
            if os.name == "nt":
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(f, fcntl.LOCK_UN)


class Config:
    def __init__(self, root, environ=None):
        values = {}
        path = root / ".env.local"
        if path.exists():
            for line in path.read_text(encoding="utf-8-sig").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, sep, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if not sep or not re.fullmatch(r"SUPERVIDEO_[A-Z0-9_]+", key):
                    raise Failure("invalid_local_config", ".env.local 每行应为 SUPERVIDEO_变量名=值")
                if value[:1] in {"'", '"'}:
                    if len(value) < 2 or value[-1] != value[0]:
                        raise Failure("invalid_local_config", ".env.local 存在未闭合的引号")
                    value = value[1:-1]
                values[key] = value
        env = os.environ if environ is None else environ
        values.update({k: v for k, v in env.items() if k.startswith("SUPERVIDEO_")})
        self.base = (values.get("SUPERVIDEO_BASE_URL") or DEFAULT_BASE).rstrip("/")
        valid_url(self.base)
        parsed = urllib.parse.urlsplit(self.base)
        if parsed.query or parsed.fragment:
            raise Failure("invalid_base_url", "接口地址不得包含查询参数或片段")
        self.account = values.get("SUPERVIDEO_ACCOUNT", "")
        self.password = values.get("SUPERVIDEO_PASSWORD", "")
        self.channel = values.get("SUPERVIDEO_CHANNEL_ID") or DEFAULT_CHANNEL
        self.resolution = values.get("SUPERVIDEO_RESOLUTION_OPTION_ID", "")
        # Legacy POLL_SECONDS/WAIT_SECONDS values are ignored: generation is submit-only.
        self.request_timeout = self.number(values, "REQUEST_TIMEOUT", 90, 1, 900)

    @staticmethod
    def number(values, key, default, low, high):
        name = "SUPERVIDEO_" + key
        try:
            n = float(values.get(name) or default)
            if not math.isfinite(n) or not low <= n <= high:
                raise ValueError
            return n
        except ValueError:
            raise Failure("invalid_local_config", name + " 超出允许范围") from None


def valid_url(url):
    try:
        p = urllib.parse.urlsplit(url)
        local_http = p.scheme == "http" and p.hostname in {"localhost", "127.0.0.1", "::1"}
        if not p.hostname or p.username or p.password or not (p.scheme == "https" or local_http):
            raise ValueError
        _ = p.port
    except ValueError:
        raise Failure("invalid_url", "接口和下载地址须为 HTTPS；本机测试允许 HTTP") from None


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    def __init__(self, config):
        self.config, self.token, self.user_id = config, None, None
        self.opener = urllib.request.build_opener(NoRedirect())

    def login(self):
        for name, value in (("ACCOUNT", self.config.account), ("PASSWORD", self.config.password)):
            if not value:
                raise Failure("missing_credentials", "请在 .env.local 填写 SUPERVIDEO_" + name)
        # The deployed web client uses email; newer backends also accept identifier
        # for usernames. Preserve compatibility with the live email login contract.
        account_field = "email" if "@" in self.config.account else "identifier"
        result = self.request("POST", "/v2/auth/login", {
            account_field: self.config.account, "password": self.config.password}, auth=False)
        user_id = str(result.get("user", {}).get("id", ""))
        token = result.get("accessToken")
        if not user_id or not isinstance(token, str) or not token:
            raise Failure("invalid_login_response", "登录接口缺少用户 ID 或访问令牌")
        if self.user_id and self.user_id != user_id:
            raise Failure("account_changed", "重新登录的用户发生变化，已停止执行")
        self.user_id, self.token = user_id, token

    def request(self, method, path, body=None, *, auth=True, key=None, raw=False, filename=None):
        if auth and not self.token:
            self.login()
        data = body if raw else (json.dumps(body, ensure_ascii=False).encode("utf-8")
                                  if body is not None else None)
        for attempt in range(2):
            headers = {"Accept": "application/json", "X-Channel-Id": self.config.channel,
                       "X-Request-Id": str(uuid.uuid4())}
            if auth:
                headers["Authorization"] = "Bearer " + self.token
            if data is not None:
                headers["Content-Type"] = (mimetypes.guess_type(filename or "")[0]
                                           if raw else "application/json") or "application/octet-stream"
            if filename:
                headers["x-upload-filename"] = urllib.parse.quote(filename, safe="")
            if key:
                headers["Idempotency-Key"] = key
            req = urllib.request.Request(self.config.base + path, data=data, headers=headers, method=method)
            try:
                with self.opener.open(req, timeout=self.config.request_timeout) as response:
                    payload = response.read(8 * 1024 * 1024 + 1)
                if len(payload) > 8 * 1024 * 1024:
                    raise Failure("response_too_large")
                result = json.loads(payload)
                if not isinstance(result, dict):
                    raise Failure("invalid_api_response")
                value = result.get("data", result)
                if not isinstance(value, dict):
                    raise Failure("invalid_api_response")
                return value
            except urllib.error.HTTPError as e:
                if e.code == 401 and auth and attempt == 0:
                    self.login()
                    continue
                # Never propagate server text, URLs, headers, credentials or bodies.
                code = "http_error"
                try:
                    problem = json.loads(e.read(65536))
                    candidate = problem.get("code", "http_error")
                    if re.fullmatch(r"[a-zA-Z0-9_.:-]{1,100}", str(candidate)):
                        code = candidate
                except (ValueError, AttributeError):
                    pass
                hints = {
                    "invalid_credentials": "登录失败：请核对项目 .env.local 中的账号、密码及注册渠道",
                    "auth_rate_limited": "登录请求达到限制，请稍后重试",
                    "generation_membership_required": "当前账号权益不支持所选时长或分辨率",
                    "generation_resolution_unavailable": "分辨率目录已变化，请重新运行 prepare 核对",
                    "generation_quote_expired": "报价已失效，已停止提交并保留原请求记录",
                }
                raise Failure(code, hints.get(code, ""), status=e.code) from None
            except (urllib.error.URLError, TimeoutError, socket.timeout, OSError, http.client.HTTPException):
                raise Failure("network_error", "请求未得到可靠响应，保留原任务与幂等键后重试") from None
            except (ValueError, UnicodeError):
                raise Failure("invalid_api_response") from None
        raise Failure("authentication_failed")

    def job(self, job_id):
        return self.request("GET", "/v1/generation-jobs/" + urllib.parse.quote(job_id, safe=""))

    def resolutions(self, selected="", mode=None, catalog=None):
        catalog = catalog if catalog is not None else self.request("GET", "/v1/generation/resolutions", auth=False)
        selected = selected or self.config.resolution or catalog.get("defaultOptionId")
        option = next((o for o in catalog.get("options", []) if o.get("id") == selected), None)
        if not option or (mode and mode not in option.get("supportedModes", [])):
            raise Failure("resolution_unavailable", "所选分辨率已停用或不支持本次生成模式")
        return {"resolutionOptionId": option["id"], "resolutionRevision": catalog["revision"],
                "megapixels": option["megapixels"]}, option["name"]


def parser_module(root):
    for ancestor in (root, *root.parents):
        script = ancestor / ".agents/skills/short-drama-produce/scripts/production_tool.py"
        if script.is_file():
            spec = importlib.util.spec_from_file_location("short_drama_production_parser", script)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise Failure("parser_missing", "找不到工作区的 short-drama-produce 文档解析器")


def field(section, name):
    match = re.search(r"(?m)^-\s*" + re.escape(name) + r"[：:]\s*(.*?)\s*$", section)
    return match[1] if match else ""


def mode_for(bindings):
    roles = [b["role"] for b in bindings]
    if not roles:
        return "t2v"
    if roles == ["first_frame"]:
        return "i2v"
    if len(roles) == 2 and set(roles) == {"first_frame", "last_frame"}:
        return "fl2v"
    if set(roles) <= {"reference_image", "reference_audio", "reference_video"}:
        counts = {kind: roles.count("reference_" + kind) for kind in ("image", "audio", "video")}
        if counts["image"] > 9 or counts["audio"] > 3 or counts["video"] > 3:
            raise Failure("reference_limit", "参考素材超过接口槽位上限")
        return "r2v"
    raise Failure("mixed_reference_roles", "首尾帧不能与主体参考混传；请先调整提示词的参考用途")


def build_jobs(root, episode, entries=None):
    if not re.fullmatch(r"EP[0-9]{3,6}", episode):
        raise Failure("invalid_episode", "剧集编号应为 EP001 等格式")
    source = f"剧集/{episode}/视频提示词.md"
    document = local_path(root, source).read_text(encoding="utf-8-sig")
    if re.search(r"(?m)^>[^\n]*版本[^\n]*(?:停用|对应旧版|待按新版)", document):
        raise Failure("inactive_source", "视频提示词仍为停用旧版，请先完成新版资料")
    parser = parser_module(root)
    ids = re.findall(r"(?m)^##\s+((?:MOTION|GROUP)-[A-Z0-9-]+)(?:\s+·[^\n]*)?\s*$", document)
    if not ids or len(ids) != len(set(ids)):
        raise Failure("invalid_entries", "未找到唯一的 MOTION 或 GROUP 条目")
    sections = {i: parser._markdown_section(document, i) for i in ids}
    groups, membership = {}, {}
    for i in ids:
        if not i.startswith("GROUP-"):
            continue
        members = re.findall(r"MOTION-[A-Z0-9-]+", field(sections[i], "成员"))
        if not members or len(members) != len(set(members)):
            raise Failure("invalid_group", "合生分组须列出唯一成员")
        for member in members:
            if member not in sections or member in membership:
                raise Failure("invalid_group", "合生分组存在缺失或重复覆盖的成员")
            membership[member] = i
        groups[i] = members
    motion_order = [i for i in ids if i.startswith("MOTION-")]
    for members in groups.values():
        start = motion_order.index(members[0])
        if motion_order[start:start + len(members)] != members:
            raise Failure("invalid_group", "合生分组成员必须按文档顺序连续排列")
    # Number the complete episode before applying --entry filters. A multi-shot
    # group counts as one video, even when its section follows the single shots.
    episode_order = list(dict.fromkeys(membership.get(i, i) for i in ids))
    selected = list(entries or episode_order)
    if len(selected) != len(set(selected)) or any(i not in ids for i in selected):
        raise Failure("invalid_selection", "选择了不存在或重复的条目")
    if any(i in membership and membership[i] in selected for i in selected):
        raise Failure("overlapping_selection", "不能同时提交合生分组及其成员")
    project = json.loads((root / "short-drama.json").read_text(encoding="utf-8-sig"))
    if groups and project.get("creator_authority", {}).get("production_profile", {}).get(
            "choices", {}).get("multi_shot_containers") is False:
        raise Failure("groups_disabled", "项目禁止合生，请移除 GROUP 并逐镜独立提交")
    ratio = project.get("format", {}).get("aspect_ratio", "16:9")
    limits = project.get("creator_authority", {}).get("production_profile", {}).get("choices", {}).get(
        "native_duration_seconds", {"min": 4, "max": 15})

    def duration(i):
        match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(?:s|秒)", field(sections[i], "时长"))
        if not match:
            raise Failure("invalid_duration", "每条视频提示词须标明秒数，如 时长：6s")
        n = float(match[1])
        if not n.is_integer():
            raise Failure("invalid_duration", "当前报价接口要求整数秒，请调整镜长")
        return int(n)

    jobs = []
    for i in selected:
        n = duration(i)
        if not limits["min"] <= n <= limits["max"]:
            raise Failure("invalid_duration", "生成段时长不在项目模型允许区间内")
        if i in groups and sum(duration(m) for m in groups[i]) != n:
            raise Failure("group_duration_mismatch", "分组时长与成员时长之和不一致")
        if re.search(r"待补参考图|待续接|不可提交|PLAN-[A-Z0-9-]+", sections[i]):
            raise Failure("pending_references", "条目仍有待补参考或不可提交标记")
        job = parser._normalize_job(root, {
            "job_id": i + "-video", "modality": "video", "adapter": "supervideo",
            "source": source, "source_entry": i,
            "outputs": [f"剧集/{episode}/制作成果/video/{i}.mp4"],
            "parameters": {"duration": n, "ratio": ratio,
                           "acceleratorEnabled": False, "steps": 15, "prompt_language": project.get(
                "creator_authority", {}).get("production_profile", {}).get("choices", {}).get(
                    "video_prompt_language", project.get("format", {}).get("prompt_language", "en"))}})
        job["mode"] = mode_for(job["reference_bindings"])
        job["task_title"] = f"MOTION-{episode} -第{episode_order.index(membership.get(i, i)) + 1}段"
        jobs.append(job)
    return jobs


class Runner:
    def __init__(self, root, config, client=None, progress=None):
        self.root, self.config = root, config
        self.client = client or Client(config)
        self.progress = progress or (lambda event: None)

    def folder(self, episode):
        if not self.client.user_id:
            self.client.login()
        identity = {"base": self.config.base, "channel": self.config.channel,
                    "user_id": self.client.user_id}
        return (self.root / ".short-drama/production/supervideo" / digest(identity) / episode), identity

    def prepare(self, episode, entries=None):
        jobs = build_jobs(self.root, episode, entries)
        catalog = self.client.request("GET", "/v1/generation/resolutions", auth=False)
        resolution, name = self.client.resolutions(catalog=catalog)
        catalog_modes = {j["mode"] for j in jobs}
        # The public catalogue can restrict modes per option.
        for mode in catalog_modes:
            self.client.resolutions(resolution["resolutionOptionId"], mode, catalog=catalog)
        return {"episode": episode, "resolution": name, **resolution,
                "available_resolutions": [{"id": o["id"], "name": o["name"],
                    "requiresMembership": o.get("requiresMembership", False)} for o in catalog["options"]],
                "total_seconds": sum(j["parameters"]["duration"] for j in jobs),
                "tasks": [{"entry": j["source_entry"], "title": j["task_title"], "mode": j["mode"],
                           "duration": j["parameters"]["duration"], "output": j["outputs"][0],
                           "references": j["references"]} for j in jobs]}

    def upload(self, job, book, save):
        refs = []
        counters = {"image": 0, "video": 0, "audio": 0}
        bindings = job["reference_bindings"]
        if job["mode"] == "fl2v":
            bindings = sorted(bindings, key=lambda b: b["role"] != "first_frame")
        for binding in bindings:
            path = local_path(self.root, binding["path"])
            data = path.read_bytes()
            h = hashlib.sha256(data).hexdigest()
            if h != job["inputs"][binding["path"]]:
                raise Failure("input_changed", "参考素材在检查后发生变化，已停止提交")
            mime = mimetypes.guess_type(path.name)[0]
            if not mime or mime.split("/")[0] not in counters:
                raise Failure("unsupported_media")
            kind = mime.split("/")[0]
            cache_key = digest({"sha256": h, "mime": mime, "name": path.name})
            cached = book["uploads"].get(cache_key)
            if not cached:
                result = self.client.request("PUT", "/v1/generation-jobs/input-images/upload", data,
                                             raw=True, filename=path.name)
                if not isinstance(result.get("storageKey"), str) or not result["storageKey"]:
                    raise Failure("invalid_upload_response")
                cached = {"storageKey": result["storageKey"], "sha256": h}
                book["uploads"][cache_key] = cached
                save()
            refs.append({"scope": "segment", "kind": kind, "index": counters[kind],
                         "filename": path.name, "mimeType": mime, "sizeBytes": len(data),
                         "storageKey": cached["storageKey"]})
            counters[kind] += 1
        return refs

    def input(self, job, refs, resolution):
        value = {"title": job["task_title"], "workflow": "hot", "mode": job["mode"],
                 "prompt": job["prompt"], "duration": job["parameters"]["duration"],
                 "aspectRatio": job["parameters"]["ratio"], "audioMode": "generate",
                 "acceleratorEnabled": False, "steps": 15,
                 "optimizePrompt": False, **resolution}
        if job["mode"] == "i2v":
            value.update(imageStorageKey=refs[0]["storageKey"], imageName=refs[0]["filename"],
                         imageMime=refs[0]["mimeType"])
        elif refs:
            value.update(referenceMedia=refs, commonEnabled=False, refImageSize="match")
        return value

    def download(self, remote, record, save):
        media = remote.get("output", {}).get("media", [])
        candidates = [m for m in media if m.get("mimeType") == "video/mp4"]
        if len(candidates) != 1:
            raise Failure("invalid_video_output", "任务须返回一个可下载的 MP4 原始视频")
        url = candidates[0].get("originalUrl") or candidates[0].get("url")
        if not isinstance(url, str):
            raise Failure("missing_download_url")
        target = local_path(self.root, record["output"])
        if target.exists():
            if record.get("sha256") and file_hash(target) == record["sha256"]:
                record["status"] = "downloaded"
                save()
                return
            raise Failure("output_exists", "输出文件已存在且不属于当前完成记录，已保留原文件")
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(target.name + ".part")
        try:
            response = None
            for _ in range(6):
                valid_url(url)
                try:
                    # Deliberately no API authorization or channel headers on media requests.
                    response = self.client.opener.open(urllib.request.Request(url),
                                                        timeout=self.config.request_timeout)
                    break
                except urllib.error.HTTPError as e:
                    if e.code in {301, 302, 303, 307, 308} and e.headers.get("Location"):
                        url = urllib.parse.urljoin(url, e.headers["Location"])
                        e.close()
                        continue
                    raise Failure("download_http_error", status=e.code) from None
            if response is None:
                raise Failure("download_redirect_limit")
            with response, tmp.open("wb") as f:
                expected = response.headers.get("Content-Length")
                size, header = 0, b""
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    size += len(block)
                    if size > MAX_VIDEO_BYTES:
                        raise Failure("video_too_large")
                    if len(header) < 32:
                        header += block[:32 - len(header)]
                    f.write(block)
                if size < 12 or (expected is not None and size != int(expected)) or header[4:8] != b"ftyp":
                    raise Failure("invalid_video_download", "下载文件不完整或不是 MP4")
                f.flush()
                os.fsync(f.fileno())
            h = file_hash(tmp)
            # Save the expected hash before the rename to recover a crash between these steps.
            record["sha256"] = h
            save()
            os.replace(tmp, target)
            record["status"] = "downloaded"
            save()
        except (OSError, urllib.error.URLError, TimeoutError, ValueError, http.client.IncompleteRead):
            raise Failure("download_interrupted", "下载中断；使用 collect 取回同一任务") from None
        finally:
            tmp.unlink(missing_ok=True)

    def collect_ready(self, record, save):
        """One explicit readiness check; download only if already succeeded."""
        remote = self.client.job(record["job_id"])
        status = remote.get("status")
        if status not in TERMINAL | {"queued", "assigned", "running"}:
            raise Failure("invalid_job_status")
        record["status"] = status
        save()
        if status == "succeeded":
            self.download(remote, record, save)
        elif status in {"failed", "cancelled"}:
            raise Failure("generation_" + status, "任务已结束；不会自动创建新的付费尝试")

    def execute(self, command, episode, entries=None):
        # Collect/status deliberately do not depend on current (possibly edited) source files.
        jobs = build_jobs(self.root, episode, entries) if command == "run" else []
        if not re.fullmatch(r"EP[0-9]{3,6}", episode):
            raise Failure("invalid_episode")
        folder, identity = self.folder(episode)
        with state_lock(folder):
            state_file = folder / "state.json"
            book = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else {
                "schema_version": 1, "identity": identity, "uploads": {}, "tasks": {}}
            if book["identity"] != identity:
                raise Failure("state_identity_mismatch")
            save = lambda: atomic_json(state_file, book)
            if command != "run":
                if entries and any(i not in book["tasks"] for i in entries):
                    raise Failure("unknown_task", "当前账号没有该条目的生成记录")
                selected = entries or list(book["tasks"])
                if not selected:
                    return {"episode": episode, "tasks": [], "message": "当前账号尚无本集任务"}
                for i in selected:
                    record = book["tasks"][i]
                    if command == "collect" and record["status"] == "downloaded":
                        path = local_path(self.root, record["output"])
                        if not path.exists():
                            record["status"] = "succeeded"
                            save()
                        elif file_hash(path) != record.get("sha256"):
                            raise Failure("output_modified", "已完成视频被修改，已保留原文件")
                    if record.get("job_id") and record["status"] != "downloaded":
                        if command == "status":
                            remote = self.client.job(record["job_id"])
                            status = remote.get("status")
                            if status not in TERMINAL | {"queued", "assigned", "running"}:
                                raise Failure("invalid_job_status")
                            record["status"] = status
                            save()
                        else:
                            self.collect_ready(record, save)
                return self.summary(book, episode, selected)

            batch_resolution = None
            for job in jobs:
                entry = job["source_entry"]
                record = book["tasks"].get(entry)
                if record:
                    if record.get("job_id"):
                        # Keep the exact historical request intact after editorial changes.
                        # Repeated run neither polls/downloads nor automatically submits a retake.
                        record["current_source_matches"] = (
                            record["fingerprint"] == job["fingerprint"] and
                            record["resolution_selection"] == self.config.resolution)
                        save()
                        continue
                    if record["fingerprint"] != job["fingerprint"] or record["resolution_selection"] != self.config.resolution:
                        raise Failure("inputs_changed", "已有任务的提示词、素材或分辨率选择已变更；请使用 collect 取回旧任务，另建新版条目")
                    if record["status"] in {"failed", "cancelled", "rejected"}:
                        raise Failure("task_requires_review", "已有失败或被拒绝的任务，已停止自动新增提交")
                else:
                    if local_path(self.root, job["outputs"][0]).exists():
                        raise Failure("output_exists", "目标文件已存在，已停止覆盖")
                    resolution, name = self.client.resolutions(mode=job["mode"])
                    if batch_resolution is not None and resolution != batch_resolution:
                        raise Failure("resolution_changed", "本批运行期间分辨率目录已变化，已停止新增提交")
                    batch_resolution = resolution
                    record = {"fingerprint": job["fingerprint"], "resolution_selection": self.config.resolution,
                              "resolution_name": name, "resolution": resolution,
                              "input_hashes": job["inputs"], "prompt_sha256": digest(job["prompt"]),
                              "status": "preparing", "output": job["outputs"][0],
                              "quote_key": "quote:" + uuid.uuid4().hex,
                              "submit_key": "generation:" + uuid.uuid4().hex}
                    book["tasks"][entry] = record
                    save()
                try:
                    if "input" not in record:
                        refs = self.upload(job, book, save)
                        record["input"] = self.input(job, refs, record["resolution"])
                        save()
                    if not record.get("quote_id"):
                        inp = record["input"]
                        current_resolution, _ = self.client.resolutions(
                            record["resolution"]["resolutionOptionId"], job["mode"])
                        if current_resolution != record["resolution"]:
                            raise Failure("resolution_changed", "分辨率目录版本已变化，已停止本次提交，请重新核对配置与任务")
                        quote = self.client.request("POST", "/v1/generation-jobs/quotes", {
                            "input": inp, "pricing": {"capability": "standard", "durationSeconds": inp["duration"],
                                "resolution": "480p" if inp["megapixels"] <= .5 else "720p" if inp["megapixels"] <= 1 else "1080p",
                                "fps": 24, "priority": "normal", "outputCount": 1, "addons": []}}, key=record["quote_key"])
                        if not quote.get("quoteId"):
                            raise Failure("invalid_quote_response")
                        record.update(quote_id=quote["quoteId"], credits=quote.get("totalCredits"))
                        save()
                        self.progress({"entry": entry, "status": "quoted", "credits": record["credits"]})
                    # Persist the complete exact request before sending; run replays it after lost responses.
                    record["status"] = "submitting"
                    save()
                    result = self.client.request("POST", "/v1/generation-jobs", {
                        "input": record["input"], "quoteId": record["quote_id"]}, key=record["submit_key"])
                    if not result.get("id"):
                        raise Failure("invalid_submit_response")
                    initial_status = result.get("status", "queued")
                    if initial_status not in TERMINAL | {"queued", "assigned", "running"}:
                        initial_status = "queued"
                    record.update(job_id=result["id"], status=initial_status, current_source_matches=True)
                    save()
                    self.progress({"entry": entry, "job_id": record["job_id"], "status": initial_status})
                except Failure as e:
                    record["last_error"] = {"code": e.code, "http_status": e.status}
                    if e.status is not None and 400 <= e.status < 500 and e.status not in {408, 429} and not record.get("job_id"):
                        record["status"] = "rejected"
                    save()
                    raise
            return self.summary(book, episode, [j["source_entry"] for j in jobs])

    @staticmethod
    def summary(book, episode, selected):
        return {"episode": episode, "tasks": [{"entry": i, "status": book["tasks"][i]["status"],
                "job_id": book["tasks"][i].get("job_id"), "output": book["tasks"][i]["output"],
                "credits": book["tasks"][i].get("credits"),
                "current_source_matches": book["tasks"][i].get("current_source_matches")} for i in selected]}


def main(argv=None):
    p = argparse.ArgumentParser(description="SuperVideo 非交互视频生成；run 仅提交并记录任务 ID，collect 按需下载")
    p.add_argument("command", choices=["prepare", "run", "status", "collect"])
    p.add_argument("--episode", default="EP001")
    p.add_argument("--entry", action="append", help="可重复指定 MOTION-/GROUP- 条目")
    p.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    args = p.parse_args(argv)
    try:
        root = args.project.resolve()
        runner = Runner(root, Config(root), progress=lambda event: print(
            json.dumps(event, ensure_ascii=False), file=sys.stderr, flush=True))
        result = (runner.prepare(args.episode, args.entry) if args.command == "prepare" else
                  runner.execute(args.command, args.episode, args.entry))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Failure as e:
        print(json.dumps({"error": {"code": e.code, "message": e.detail,
                                     "http_status": e.status}}, ensure_ascii=False), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print('{"error":{"code":"interrupted","message":"已中断；通过 run 恢复原提交，明确需要下载时使用 collect"}}', file=sys.stderr)
        return 130
    except Exception:
        # Do not let tracebacks expose request URLs, local credentials or response bodies.
        print('{"error":{"code":"local_or_contract_error","message":"检查文档格式、路径及本地状态文件；未自动新增重试"}}', file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
