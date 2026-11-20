# SuperVideo 视频生成

使用 Python 3.10 或更新版本，无额外 Python 依赖。脚本使用本工作区的
`short-drama-produce` 解析器，项目移动时须保留工作区 `.agents/skills/`。

## 填写账号

编辑项目根目录 `.env.local`：

```dotenv
SUPERVIDEO_BASE_URL=https://api.isupervideo.com
SUPERVIDEO_ACCOUNT=你的用户名或邮箱
SUPERVIDEO_PASSWORD=你的密码
SUPERVIDEO_CHANNEL_ID=
SUPERVIDEO_RESOLUTION_OPTION_ID=
```

`.env.local` 已建立并忽略提交；`.env.local.example` 是空白模板。
密码含首尾空格时用一对单引号或双引号包围。`#`、`$`、反斜线和中文在值内原样保留，
不进行 shell 展开或转义；注释单独占行。进程环境变量覆盖同名文件配置，空值也会覆盖。

账号支持邮箱、用户名。登录令牌只保存在当前进程内。所有命令均不会弹出输入或确认。
渠道留空采用 SuperVideo 默认渠道，其他渠道的账号须填注册渠道 ID。
分辨率留空读取服务器默认档；需要指定时将 `prepare` 输出的 `available_resolutions` 中的选项 ID 填入配置。
会员和积分由服务端校验，脚本不自动变更档位或购买权益。

## 命令

从项目根目录运行；从其他目录运行时指定脚本的绝对路径即可，默认项目仍为脚本所在项目。

```powershell
python -X utf8 scripts/supervideo.py prepare --episode EP001
python -X utf8 scripts/supervideo.py run --episode EP001
python -X utf8 scripts/supervideo.py status --episode EP001
python -X utf8 scripts/supervideo.py collect --episode EP001
```

- `prepare`：只核对资料并读取公开分辨率目录，不登录、不上传、不创建报价或生成任务。
- `run`：实际上传、报价并顺序提交本批；每段拿到任务 ID 后立即保存并继续下一段，最终返回 ID 清单。不查询任务状态、不轮询、不等待完成、不自动下载。
  报价和提交回执输出到标准错误，最终 ID 清单以 JSON 输出到标准输出。
- `status`：账号自动登录后查询已有任务，不创建报价或提交任务。
- `collect`：仅在用户主动要求下载时运行。每段只查询一次，已完成才下载，未完成就返回当前状态，不持续等待，也不创建报价或生成任务。

单独选择条目可重复传入 `--entry MOTION-EP001-018` 或 `--entry GROUP-EP001-01`。
默认以合生分组替代组内成员，避免同一段重复生成。每次生成段限项目配置允许的整数秒数。

生成方式按文档参考用途决定：无参考为 `t2v`，单起始帧为 `i2v`，首尾帧为 `fl2v`，
主体/构图等参考及参考音频为 `r2v`。混合首尾帧和主体参考会被拦截，请在文档中选好用途。
参考图仍可通过现有 Markdown 链接跳转，脚本直接读取 `REF-...` 绑定。

EP001 已完成新版 90 秒资料：18 镜、15 个提交任务。旧 60 秒归档及 001–011 首帧已移出项目；新镜为 012–029。
只生成第一个视频时执行 `run --episode EP001 --entry GROUP-EP001-01`，提交 6 秒开场。
脚本不会自动改动剧情、提示词或参考用途。

## 提示词与语言

新写或修订的视频提示词统一使用工作区 `h3-prompt-expert` 技能生成，可复制正文使用英文，保留官方 H3 字段与素材标签；角色对白、VO、OS 与指定画内文字保持剧本中文原句。
项目 `video_prompt_language=en` 优先于图片提示词的语言配置；创作者说明仍使用中文。切换输出模式不自动翻译已有文档，后续修订按英文规则输出。
90 秒版英文历史稿保留在 `.short-drama/versions/EP001-h3-en/`。2026-11-19 按用户要求清空全部本地视频任务记录；已下载的 90 秒版开场视频与检查帧保留。
任务名称使用 `MOTION-<集号> -第<N>段`，例如 `MOTION-EP001 -第2段`。按整集生成顺序编号，合生分组计一段，`--entry` 单选或调整选择顺序不改变段号；`prepare` 可预览名称。条目 ID 和输出文件名不变，已有任务保留历史名称和请求。

## 输出与恢复

- 视频：`剧集/EP001/制作成果/video/<MOTION或GROUP编号>.mp4`。
- 本机记录：`.short-drama/production/supervideo/<账号及接口摘要>/EP001/state.json`。
- 状态保存提示词及输入参数、摘要、上传后的存储键、报价 ID、幂等键、任务号及完成文件摘要；不保存密码、JWT 或下载签名地址。
- 请求失败或进程中断后，重新运行 `run` 恢复原提交；已有任务号的条目直接返回原 ID，不查询、不下载、不重拍。
- 提交响应丢失、尚未拿到任务号时，重新运行 `run` 重放相同输入和幂等键。
  此时 `collect` 只显示提交中状态，不猜测任务号或创建新任务。
- 用户要求查询时用 `status`；用户要求下载时才用 `collect`。已下载文件丢失时，可显式用 `collect` 取回。
- 尚未取得任务号的请求如发生输入变更，或被服务端拒绝，停止该条提交。已取得任务号的请求始终保留历史输入；`current_source_matches` 表示当前文稿是否匹配原请求，改稿不会自动重拍。
- 已下载视频若被手工改动，显式取回时会拒绝覆盖。需要重拍时建立新版条目，不要删除状态以重复扣费。
- `.part` 下载文件不视为完成；失败时清理，成功验证 MP4 头及长度后原子写入目标。

可在 `.env.local` 调整单次网络请求超时 `SUPERVIDEO_REQUEST_TIMEOUT`（默认 90 秒）。
旧配置 `SUPERVIDEO_POLL_SECONDS` 和 `SUPERVIDEO_WAIT_SECONDS` 已不再使用，保留它们也不会触发轮询。
同一账号和剧集使用系统文件锁，拒绝同时运行两个命令；进程退出会自动释放锁。

## 离线测试

```powershell
python -X utf8 -m unittest discover -s scripts/tests -v
```

测试只请求本机模拟 HTTP 服务，使用临时项目和虚构账号，不调用线上付费接口。

## 当前独立生成规则

所有剧集每个分镜独立生成，最短 3 秒，不再使用 GROUP。EP001 为 18 段、90 秒，第一段 MOTION-EP001-012，第二段 MOTION-EP001-013；EP002 为 10 段、90 秒。上文 GROUP 示例仅适用于历史记录，当前禁止提交合生组。

## 视频生成质量

新请求统一关闭快速抽卡（`acceleratorEnabled=false`），采用用户指定的 `steps=15`。平台将 15 步归为普通档，清晰度独立读取现有配置。已提交任务保留原参数，不自动重拍。
