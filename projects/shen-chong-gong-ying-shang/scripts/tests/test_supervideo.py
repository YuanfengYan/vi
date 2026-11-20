"""Real local HTTP transport, fake service and disposable projects; no production calls."""
import base64
import contextlib
import io
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import supervideo as sv

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6kAAAAABJRU5ErkJggg==")
MP4 = b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00isomiso2" + b"\x00\x00\x00\x08mdat"
OPTION = "00000000-0000-4000-8000-000000000002"
REAL_PARSER = sv.parser_module(Path(__file__).resolve().parents[2])


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_json(self, data, code=200):
        payload = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        s = self.server
        s.requests.append(("GET", self.path, self.headers.get("Authorization")))
        if self.path == "/v1/generation/resolutions":
            return self.send_json({"data": {"revision": s.revision, "defaultOptionId": OPTION,
                "options": [] if s.empty_catalog else [{"id": OPTION, "name": "420P", "megapixels": .3,
                    "supportedModes": ["t2v", "i2v", "r2v", "fl2v"]}]}})
        if self.path == "/media/result.mp4":
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", str(len(MP4) + (100 if s.truncate else 0)))
            self.end_headers()
            self.wfile.write(MP4)
            self.close_connection = True
            return
        if self.path.startswith("/v1/generation-jobs/"):
            if getattr(s, "redirect_jobs", False):
                self.send_response(302)
                self.send_header("Location", s.base + "/token-trap")
                self.end_headers()
                return
            if s.expire_once:
                s.expire_once = False
                return self.send_json({"code": "invalid_token"}, 401)
            status = s.job_status
            return self.send_json({"data": {"id": self.path.rsplit("/", 1)[-1], "status": status,
                "output": {"media": [{"mimeType": "video/mp4", "url": s.base + "/media/result.mp4",
                                      "playbackUrl": s.base + "/wrong.m3u8"}]}}})
        self.send_json({"code": "not_found"}, 404)

    def do_PUT(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        self.server.requests.append(("PUT", self.path, self.headers.get("Authorization")))
        self.server.uploads.append({"body": data, "filename": self.headers.get("x-upload-filename")})
        if getattr(self.server, "change_catalog_on_upload", False):
            self.server.revision += 1
        self.send_json({"data": {"storageKey": "owned/" + str(len(self.server.uploads))}}, 201)

    def do_POST(self):
        s = self.server
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        s.requests.append(("POST", self.path, self.headers.get("Authorization")))
        if self.path == "/v2/auth/login":
            s.logins += 1
            if body.get("password") != "test-password$#中文":
                return self.send_json({"code": "invalid_credentials", "detail": body.get("password")}, 401)
            user = body.get("email") or body.get("identifier")
            if "@" in user and "email" not in body:
                return self.send_json({"code": "invalid_credentials"}, 401)
            return self.send_json({"data": {"accessToken": "private-token-" + user, "user": {"id": user}}})
        if self.path == "/v1/generation-jobs/quotes":
            s.quotes.append(body)
            return self.send_json({"data": {"quoteId": "quote-1", "totalCredits": 3,
                                            "availableCredits": 100}}, 201)
        if self.path == "/v1/generation-jobs":
            s.submissions.append(body)
            key = self.headers["Idempotency-Key"]
            if s.rejection:
                return self.send_json({"code": s.rejection}, 403)
            if key not in s.accepted:
                s.accepted[key] = {"id": "job-" + str(len(s.accepted) + 1), "body": body}
            elif s.accepted[key]["body"] != body:
                return self.send_json({"code": "idempotency_conflict"}, 409)
            if s.lose_submit_response:
                s.lose_submit_response = False
                self.connection.shutdown(socket.SHUT_RDWR)
                self.connection.close()
                return
            return self.send_json({"data": {"id": s.accepted[key]["id"],
                                            "status": getattr(s, 'submit_status', 'queued')}}, 202)
        self.send_json({"code": "not_found"}, 404)


class GenerationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.base = "http://127.0.0.1:" + str(self.server.server_port)
        for k in ("requests", "uploads", "quotes", "submissions"):
            setattr(self.server, k, [])
        self.server.accepted = {}
        self.server.logins, self.server.revision = 0, 23
        self.server.empty_catalog = self.server.truncate = self.server.expire_once = False
        self.server.lose_submit_response = False
        self.server.job_status = "succeeded"
        self.server.rejection = None
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        patcher = patch.object(sv, "parser_module", return_value=REAL_PARSER)
        patcher.start()
        self.addCleanup(patcher.stop)
        (self.root / ".env.local").write_text(
            f"SUPERVIDEO_BASE_URL={self.server.base}\nSUPERVIDEO_ACCOUNT=user-a\n"
            "SUPERVIDEO_PASSWORD='test-password$#中文'\nSUPERVIDEO_POLL_SECONDS=0.01\n"
            "SUPERVIDEO_WAIT_SECONDS=0.02\n", encoding="utf-8")
        self.ep = self.root / "剧集/EP001"
        self.ep.mkdir(parents=True)
        (self.root / "short-drama.json").write_text(json.dumps({"format": {"aspect_ratio": "16:9",
            "prompt_language": "en"}}), encoding="utf-8")
        self.asset = "输入/参考图/角色设定.png"
        asset = self.root / self.asset
        asset.parent.mkdir(parents=True)
        asset.write_bytes(PNG)

    def runner(self, **env):
        return sv.Runner(self.root, sv.Config(self.root, environ=env))

    def render(self, runner=None):
        runner = runner or self.runner()
        runner.execute("run", "EP001")
        return runner.execute("collect", "EP001")

    def write(self, mode="t2v", second=False):
        purpose = {"i2v": ["起始帧"], "fl2v": ["起始帧", "结束帧"],
                   "r2v": ["主体", "空间布局"], "t2v": []}[mode]
        # Different source files avoid duplicate same-path/same-role reference bindings.
        (self.root / "输入/参考图/场景.png").write_bytes(PNG)
        paths = [self.asset, "输入/参考图/场景.png"]
        refs = "；".join(f"REF-TEST-{i+1}（顺序：{i+1}）· {paths[i]}《测试参考图{i+1}》"
                        f"（用途：{p}；控制：外观；不得控制：动作）" for i, p in enumerate(purpose)) or "无"
        def section(n):
            return (f"## MOTION-EP001-{n:03} · 测试\n\n- 时长：5s\n- 生成方式："
                    f"{'图生视频' if purpose else '文生视频'}\n- 输入参考图：{refs}\n\n"
                    "### 可复制提示词\n\n> A quiet cinematic shot.\n")
        text = "# 测试提示词\n\n" + section(1)
        if second:
            text += "\n" + section(2)
        (self.ep / "视频提示词.md").write_text(text, encoding="utf-8")

    def state(self, runner):
        folder, _ = runner.folder("EP001")
        return json.loads((folder / "state.json").read_text(encoding="utf-8"))

    def error(self, code, fn):
        with self.assertRaises(sv.Failure) as cm:
            fn()
        self.assertEqual(cm.exception.code, code)

    def test_config_is_literal_and_environment_has_priority(self):
        c = sv.Config(self.root, environ={"SUPERVIDEO_ACCOUNT": "someone@example.com"})
        self.assertEqual(c.password, "test-password$#中文")
        self.assertEqual(c.account, "someone@example.com")

    def test_email_login_matches_deployed_web_contract(self):
        self.write()
        runner = self.runner(SUPERVIDEO_ACCOUNT="someone@example.com")
        result = self.render(runner)
        self.assertEqual(result["tasks"][0]["status"], "downloaded")
        self.assertEqual(runner.client.user_id, "someone@example.com")

    def test_missing_password_stops_before_network(self):
        self.write()
        self.error("missing_credentials", lambda: self.runner(SUPERVIDEO_PASSWORD="").execute("run", "EP001"))
        self.assertEqual(self.server.requests, [])

    def test_prepare_has_no_login_upload_quote_or_submit(self):
        self.write("r2v")
        result = self.runner().prepare("EP001")
        self.assertEqual(result["tasks"][0]["mode"], "r2v")
        self.assertEqual(result["resolutionRevision"], 23)
        self.assertTrue(all(method == "GET" for method, _, _ in self.server.requests))
        self.assertEqual(self.server.logins, 0)

    def test_all_four_modes_compile_and_download(self):
        for mode in ["t2v", "i2v", "r2v", "fl2v"]:
            with self.subTest(mode=mode):
                # Isolated accounts also isolate existing state between mode variants.
                self.write(mode)
                runner = self.runner(SUPERVIDEO_ACCOUNT="user-" + mode)
                output = self.ep / "制作成果/video/MOTION-EP001-001.mp4"
                output.unlink(missing_ok=True)
                result = self.render(runner)
                inp = self.server.submissions[-1]["input"]
                self.assertEqual(inp["mode"], mode)
                self.assertEqual(inp["workflow"], "hot")
                self.assertFalse(inp["acceleratorEnabled"])
                self.assertEqual(inp["steps"], 15)
                self.assertEqual(inp["title"], "MOTION-EP001 -第1段")
                self.assertEqual(inp["aspectRatio"], "16:9")
                self.assertFalse(inp["optimizePrompt"])
                self.assertEqual(inp["audioMode"], "generate")
                if mode == "i2v":
                    self.assertIn("imageStorageKey", inp)
                if mode in {"r2v", "fl2v"}:
                    self.assertEqual([r["index"] for r in inp["referenceMedia"]], [0, 1])
                self.assertEqual(result["tasks"][0]["status"], "downloaded")
                self.assertEqual(output.read_bytes(), MP4)
        self.assertTrue(all(auth is None for _, path, auth in self.server.requests if path == "/media/result.mp4"))
        self.assertTrue(any("%" in u["filename"] for u in self.server.uploads))

    def test_episode_titles_count_groups_and_survive_entry_selection(self):
        self.write(second=True)
        source = self.ep / "视频提示词.md"
        text = source.read_text(encoding="utf-8")
        third = text[text.index("## MOTION-EP001-002"):].replace(
            "MOTION-EP001-002", "MOTION-EP001-003")
        text += "\n" + third + (
            "\n## GROUP-EP001-01-R2 · Combined\n\n"
            "- 成员：MOTION-EP001-001、MOTION-EP001-002\n- 时长：10s\n"
            "- 输入参考图：无\n\n### 可复制提示词\n\n> Two continuous shots.\n")
        source.write_text(text, encoding="utf-8")
        jobs = sv.build_jobs(self.root, "EP001")
        self.assertEqual([(j["source_entry"], j["task_title"]) for j in jobs], [
            ("GROUP-EP001-01-R2", "MOTION-EP001 -第1段"),
            ("MOTION-EP001-003", "MOTION-EP001 -第2段")])
        selected = sv.build_jobs(self.root, "EP001", [
            "MOTION-EP001-003", "GROUP-EP001-01-R2"])
        self.assertEqual([j["task_title"] for j in selected], [
            "MOTION-EP001 -第2段", "MOTION-EP001 -第1段"])
        runner = self.runner()
        runner.execute("run", "EP001", ["MOTION-EP001-003"])
        self.assertEqual(self.server.submissions[-1]["input"]["title"], "MOTION-EP001 -第2段")
        self.assertEqual(runner.prepare("EP001")["tasks"][1]["title"], "MOTION-EP001 -第2段")

    def test_upload_cache_and_completed_tasks_are_reused(self):
        self.write("r2v", second=True)
        runner = self.runner()
        self.render(runner)
        self.assertEqual(len(self.server.uploads), 2)
        self.assertEqual(len(self.server.accepted), 2)
        runner.execute("run", "EP001")
        self.assertEqual(len(self.server.accepted), 2)
        self.assertEqual(len(self.server.submissions), 2)

    def test_lost_submission_response_replays_exact_request(self):
        self.write()
        self.server.lose_submit_response = True
        self.error("network_error", lambda: self.runner().execute("run", "EP001"))
        self.assertEqual(len(self.server.accepted), 1)
        self.runner().execute("run", "EP001")
        self.assertEqual(len(self.server.accepted), 1)
        self.assertEqual(self.server.submissions[0], self.server.submissions[1])
        self.assertEqual(len(self.server.quotes), 1)

    def test_collect_checks_once_without_waiting_and_can_download_after_source_edit(self):
        self.write()
        self.server.job_status = "running"
        runner = self.runner()
        queued = runner.execute("run", "EP001")
        self.assertEqual(queued["tasks"][0]["status"], "queued")
        active = runner.execute("collect", "EP001")
        self.assertEqual(active["tasks"][0]["status"], "running")
        self.assertEqual(sum(path.startswith('/v1/generation-jobs/') and method == 'GET'
                             for method, path, _ in self.server.requests), 1)
        self.assertFalse(list(self.ep.rglob('*.mp4')))
        (self.ep / "视频提示词.md").write_text("旧资料被修改", encoding="utf-8")
        self.server.job_status = "succeeded"
        result = self.runner().execute("collect", "EP001")
        self.assertEqual(result["tasks"][0]["status"], "downloaded")
        self.assertEqual(len(self.server.submissions), 1)

    def test_partial_download_is_removed_and_collect_recovers(self):
        self.write()
        self.server.truncate = True
        self.runner().execute("run", "EP001")
        self.error("invalid_video_download", lambda: self.runner().execute("collect", "EP001"))
        self.assertEqual(list(self.ep.rglob("*.part")), [])
        self.assertEqual(list(self.ep.rglob("*.mp4")), [])
        self.server.truncate = False
        self.runner().execute("collect", "EP001")
        self.assertEqual(len(list(self.ep.rglob("*.mp4"))), 1)
        self.assertEqual(len(self.server.submissions), 1)

    def test_collect_restores_missing_completed_file(self):
        self.write()
        runner = self.runner()
        self.render(runner)
        next(self.ep.rglob("*.mp4")).unlink()
        runner.execute("collect", "EP001")
        self.assertEqual(len(list(self.ep.rglob("*.mp4"))), 1)
        self.assertEqual(len(self.server.submissions), 1)

    def test_source_changes_never_create_automatic_retake(self):
        self.write()
        runner = self.runner()
        original = runner.execute("run", "EP001")
        original_record = self.state(runner)["tasks"]["MOTION-EP001-001"]
        f = self.ep / "视频提示词.md"
        f.write_text(f.read_text(encoding="utf-8").replace("quiet", "loud"), encoding="utf-8")
        result = self.runner().execute("run", "EP001")
        self.assertEqual(result["tasks"][0]["job_id"], original["tasks"][0]["job_id"])
        self.assertFalse(result["tasks"][0]["current_source_matches"])
        saved = self.state(runner)["tasks"]["MOTION-EP001-001"]
        self.assertEqual(saved["input"], original_record["input"])
        self.assertEqual(saved["fingerprint"], original_record["fingerprint"])
        self.assertEqual(len(self.server.accepted), 1)

    def test_failed_task_and_membership_rejection_do_not_retry(self):
        self.write()
        self.server.rejection = "generation_membership_required"
        self.error("generation_membership_required", lambda: self.runner().execute("run", "EP001"))
        self.error("task_requires_review", lambda: self.runner().execute("run", "EP001"))
        self.assertEqual(len(self.server.submissions), 1)

    def test_remote_failure_is_terminal(self):
        self.write()
        self.server.job_status = "failed"
        self.runner().execute("run", "EP001")
        self.error("generation_failed", lambda: self.runner().execute("collect", "EP001"))
        result = self.runner().execute("run", "EP001")
        self.assertEqual(result["tasks"][0]["status"], "failed")
        self.assertEqual(len(self.server.submissions), 1)

    def test_reauthentication_is_bounded_and_preserves_owner(self):
        self.write()
        self.server.expire_once = True
        self.render()
        self.assertEqual(self.server.logins, 2)
        self.assertEqual(len(self.server.accepted), 1)

    def test_account_switch_isolates_state(self):
        self.write()
        self.runner().execute("run", "EP001")
        result = self.runner(SUPERVIDEO_ACCOUNT="user-b").execute("status", "EP001")
        self.assertEqual(result["tasks"], [])
        self.assertEqual(len(self.server.accepted), 1)

    def test_no_secrets_or_signed_urls_are_persisted(self):
        self.write("r2v")
        runner = self.runner()
        self.render(runner)
        content = json.dumps(self.state(runner), ensure_ascii=False)
        self.assertNotIn("test-password", content)
        self.assertNotIn("private-token", content)
        self.assertNotIn("/media/result.mp4", content)

    def test_bad_login_cli_does_not_print_password_or_traceback(self):
        self.write()
        out, err = io.StringIO(), io.StringIO()
        with patch.dict(sv.os.environ, {"SUPERVIDEO_PASSWORD": "wrong-secret"}), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            result = sv.main(["run", "--project", str(self.root)])
        self.assertEqual(result, 2)
        self.assertIn("invalid_credentials", err.getvalue())
        self.assertNotIn("wrong-secret", out.getvalue() + err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())

    def test_inactive_missing_or_mixed_inputs_block_before_login(self):
        self.write("i2v")
        f = self.ep / "视频提示词.md"
        text = f.read_text(encoding="utf-8")
        f.write_text("> 版本提示：本文件对应旧版 60 秒剧本，当前停用。\n" + text, encoding="utf-8")
        self.error("inactive_source", lambda: self.runner().execute("run", "EP001"))
        self.assertEqual(self.server.requests, [])
        self.error("mixed_reference_roles", lambda: sv.mode_for([
            {"role": "first_frame"}, {"role": "reference_image"}]))
        f.write_text(text, encoding="utf-8")
        (self.root / self.asset).unlink()
        with self.assertRaises(FileNotFoundError):
            sv.build_jobs(self.root, "EP001")
        self.assertEqual(self.server.requests, [])

    def test_empty_resolution_catalog_never_falls_back(self):
        self.write()
        self.server.empty_catalog = True
        self.error("resolution_unavailable", lambda: self.runner().execute("run", "EP001"))
        self.assertEqual(len(self.server.quotes), 0)

    def test_catalog_change_during_preparation_stops_before_quote(self):
        self.write("r2v")
        self.server.change_catalog_on_upload = True
        self.error("resolution_changed", lambda: self.runner().execute("run", "EP001"))
        self.assertEqual(len(self.server.quotes), 0)
        self.assertEqual(len(self.server.submissions), 0)

    def test_existing_output_is_preserved(self):
        self.write()
        target = self.ep / "制作成果/video/MOTION-EP001-001.mp4"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"original")
        self.error("output_exists", lambda: self.runner().execute("run", "EP001"))
        self.assertEqual(target.read_bytes(), b"original")
        self.assertEqual(len(self.server.submissions), 0)

    def test_input_file_changed_after_preflight_is_not_uploaded(self):
        self.write("r2v")
        jobs = sv.build_jobs(self.root, "EP001")
        (self.root / self.asset).write_bytes(PNG + b"changed")
        runner = self.runner()
        self.error("input_changed", lambda: runner.upload(jobs[0], {"uploads": {}}, lambda: None))
        self.assertEqual(self.server.requests, [])

    def test_api_redirect_is_not_followed_with_bearer_token(self):
        self.write()
        self.server.redirect_jobs = True
        self.runner().execute("run", "EP001")
        self.error("http_error", lambda: self.runner().execute("collect", "EP001"))
        self.assertFalse(any(path == "/token-trap" for _, path, _ in self.server.requests))
        self.assertEqual(len(self.server.accepted), 1)

    def test_invalid_config_and_url_do_not_echo_secrets(self):
        self.error("invalid_url", lambda: self.runner(SUPERVIDEO_BASE_URL="https://user:secret@example.com"))
        self.error("invalid_local_config", lambda: self.runner(SUPERVIDEO_REQUEST_TIMEOUT="nan"))

    def test_run_returns_ids_without_any_status_or_media_request(self):
        self.write(second=True)
        self.server.job_status = "running"
        runner = self.runner()
        result = runner.execute("run", "EP001")
        self.assertEqual([t['status'] for t in result['tasks']], ['queued', 'queued'])
        self.assertTrue(all(t['job_id'] for t in result['tasks']))
        self.assertFalse(any(method == 'GET' and path.startswith('/v1/generation-jobs/')
                             for method, path, _ in self.server.requests))
        self.assertFalse(any(path.startswith('/media/') for _, path, _ in self.server.requests))
        self.assertFalse(list(self.ep.rglob('*.mp4')))
        runner.execute("run", "EP001")
        self.assertEqual(len(self.server.submissions), 2)
        self.assertFalse(any(method == 'GET' and path.startswith('/v1/generation-jobs/')
                             for method, path, _ in self.server.requests))

    def test_status_never_downloads_even_when_finished(self):
        self.write()
        runner = self.runner()
        runner.execute('run', 'EP001')
        result = runner.execute('status', 'EP001')
        self.assertEqual(result['tasks'][0]['status'], 'succeeded')
        self.assertFalse(list(self.ep.rglob('*.mp4')))
        self.assertFalse(any(path.startswith('/media/') for _, path, _ in self.server.requests))

    def test_already_finished_submission_still_requires_explicit_download(self):
        self.write()
        self.server.submit_status = 'succeeded'
        result = self.runner().execute('run', 'EP001')
        self.assertEqual(result['tasks'][0]['status'], 'succeeded')
        self.assertFalse(any(method == 'GET' and path.startswith('/v1/generation-jobs/')
                             for method, path, _ in self.server.requests))
        self.assertFalse(any(path.startswith('/media/') for _, path, _ in self.server.requests))
        self.assertFalse(list(self.ep.rglob('*.mp4')))

    def test_video_language_precedes_image_prompt_language(self):
        self.write()
        p = self.root / 'short-drama.json'
        config = json.loads(p.read_text(encoding='utf-8'))
        config['creator_authority'] = {'production_profile': {'choices': {'video_prompt_language': 'zh-CN'}}}
        p.write_text(json.dumps(config), encoding='utf-8')
        job = sv.build_jobs(self.root, 'EP001')[0]
        self.assertEqual(job['parameters']['prompt_language'], 'zh-CN')

    def test_group_replaces_its_members_and_overlapping_selection_is_rejected(self):
        self.write(second=True)
        f = self.ep / "视频提示词.md"
        f.write_text(f.read_text(encoding="utf-8") + "\n## GROUP-EP001-01 · 分组\n\n"
                     "- 成员：MOTION-EP001-001、MOTION-EP001-002\n- 时长：10s\n"
                     "- 输入参考图：无\n\n### 可复制提示词\n\n> Two shots.\n", encoding="utf-8")
        jobs = sv.build_jobs(self.root, "EP001")
        self.assertEqual([j["source_entry"] for j in jobs], ["GROUP-EP001-01"])
        self.error("overlapping_selection", lambda: sv.build_jobs(self.root, "EP001",
                    ["GROUP-EP001-01", "MOTION-EP001-001"]))

    def test_system_lock_rejects_concurrent_run(self):
        with sv.state_lock(self.root / "locks"):
            self.error("already_running", lambda: self.enter_lock())

    def enter_lock(self):
        with sv.state_lock(self.root / "locks"):
            pass


if __name__ == "__main__":
    unittest.main()
