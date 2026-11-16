# Drama Skills 项目安装

- 来源：https://github.com/zenstory-ai/drama-skills
- 上游版本：0.9.2
- 固定提交：fdb7b7c58017e3eae64eca382c2a85ede368dab0
- 安装日期：2026-10-26
- 范围：当前项目 `.agents/skills/`，共 11 个面向创作者的技能。
- 许可证：MIT，原文保留在 `drama-skills-LICENSE`。

下一轮对话可直接使用 `$short-drama` 初始化或继续短剧项目，也可按阶段调用：

| 技能 | 用途 |
| --- | --- |
| `$short-drama` | 项目初始化、跨阶段路由、创作台 |
| `$short-drama-develop` | 创意开发、改编、分集规划 |
| `$short-drama-novel-analyze` | 原著分析 |
| `$short-drama-write` | 剧本写作与修改 |
| `$short-drama-assets` | 角色、场景、道具与视觉设定 |
| `$short-drama-image-prompts` | 图片提示词 |
| `$short-drama-storyboard` | 分镜与关键帧 |
| `$short-drama-video-prompts` | 视频提示词 |
| `$short-drama-produce` | 媒体生产 |
| `$short-drama-edit` | 剪辑成片 |
| `$short-drama-review` | 审查 |

安装不等于已开始创作或媒体生产。实际生产需配置对应供应商适配器与凭据；剪辑另需 ffmpeg / ffprobe。使用每个技能前读取该目录的 SKILL.md 及所需引用文件。
