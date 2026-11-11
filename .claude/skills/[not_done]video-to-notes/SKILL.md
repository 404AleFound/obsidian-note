---
name: video-to-notes
description: 用户直接发来一个 YouTube / YouTube Shorts / youtu.be / Bilibili / b23.tv 或其他视频链接时，立即开始处理，不要问用户想干什么。生成带时间戳的笔记和报告，并发布到本地 HTML、Notion 或 Obsidian。也用于视频转录、摘要、字幕、报告、发布、同步与看板。
---

# Video to Notes

把视频链接变成「带时间戳的摘要 + 报告」，优先下载现成字幕；只有字幕缺失时才回退到本地 Whisper 转录。

## 运行前提

- 公共依赖（`yt-dlp`、`imageio-ffmpeg`）已声明在仓库根目录 `pyproject.toml`，由 `uv sync` 一键恢复。
- 业务代码在本目录 `ytlt/`，通过 `uv run python .claude/skills/video-to-notes/run.py ...` 调用，无需单独安装。
- 本地 Whisper 转录是可选项，模型权重说明见 [README.md](README.md)。

## 行为准则

- 一条只含受支持视频链接的消息 = 完整请求，立刻开始，绝不回复「你想让我对这个链接做什么？」。
- YouTube watch / Shorts / live / `youtu.be` 一视同仁；传 URL 给处理器时保留 `t`、`list` 等查询参数。
- 用户说「只下载 / 只翻译 / 只提取字幕」等更窄的目标时，只做那件事，不强行走完整报告流程。
- 第一次安全尝试前，不要问 cookies、语言、输出位置；只有具体失败证明需要用户输入时才问。
- 写任何关于视频的结论前，先读 `metadata.json` 和完整的 `transcript.txt`。

## 裸链接流程

1. 先处理成本地产物，无论配置的发布目标是什么：

   ```bash
   uv run python .claude/skills/video-to-notes/run.py process "VIDEO_URL" --environment local
   ```

   这样能保证在 `summary.md` 和 `tags.json` 存在之前，不会把不完整的报告发布出去。

2. 读取返回的 `metadata.json` 和完整的 `transcript.txt`。
3. 写一份以「结论先行」的 `summary.md`，以及 `tags.json`（3–8 个主题标签）：
   - `summary.md` 的每个关键点都用真实时间戳开头，如 `- [mm:ss-mm:ss] 主要结论。`；超过 1 小时的视频用 `[hh:mm:ss-hh:mm:ss]`。
   - 不编造字幕里没有的时间戳精度。
   - `tags.json` 只放转录支持的主题/实体/行业/方法，剔除 `youtube`、`video-report`、`manual_subtitle` 这类来源标签。
4. 两个文件都就绪后再 finalize（二选一）：
   - 本地：`uv run python .claude/skills/video-to-notes/run.py finalize "VIDEO_FOLDER" --environment local`
   - Obsidian：设置 `OBSIDIAN_VAULT_PATH`（或传 `--obsidian-vault`）后 `uv run python .claude/skills/video-to-notes/run.py finalize "VIDEO_FOLDER" --environment obsidian`
5. 返回面向读者的主产物：Obsidian 笔记路径 / `obsidian://` URI，或本地 `report.html` 路径。远程发布时附带本地报告作为存档。

不要停在 `process`；它的 HTML 只是初步产物，要等 summary、tags、`finalize` 都完成后才算完成。

## 目标选择

读 `<workspace>/config.json` 里的 `preferences.output_environment`（若存在）：

- `local` → 本地 finalize。
- `obsidian` → 发布到 Obsidian vault。
- `notion` → 需要 `NOTION_TOKEN` + 恰好一个 Notion 目标 ID。

用户显式指定目标时覆盖该配置。远程发布不可用时，保留已完成的本地报告、说明具体阻塞点、返回本地路径；除非 publisher 返回了 URL/路径，否则绝不声称远程同步成功。

## 失败处理

- 元数据或字幕因需要鉴权而失败 → 用可用浏览器 cookies 重试；没有可用 cookie 源时才问用户。
- 无字幕且未装 Whisper → 报告「无可用字幕、未配置 Whisper」，并指向 [README.md](README.md) 的本地转录一节。绝不拿网页搜索片段或页面元数据冒充缺失的转录；拿不到转录就如实报告失败。
- 源视频私密 / 已删除 / 地区受限 / 不支持 → 报告具体原因，保留已产出的产物。

## 已有报告与看板

对已处理的文件夹，按需更新 `summary.md` 或 `tags.json` 后运行：

```bash
uv run python .claude/skills/video-to-notes/run.py finalize "VIDEO_FOLDER"
```

看板：

```bash
uv run python .claude/skills/video-to-notes/run.py rebuild-index
uv run python .claude/skills/video-to-notes/run.py serve --open
```

服务器默认只绑 `127.0.0.1`，除非用户明确要求对外暴露。

## 收尾回复

进度更新保持简短、面向结果，不要倒下载/转码/逐文件日志（除非解释失败）。

完成后用紧凑格式：

```text
已完成：VIDEO_TITLE

报告：PRIMARY_REPORT_URL_OR_PATH
本地报告：/absolute/path/to/report.html   # 远程目标时附上

摘要：一段结论先行的概述。

关键点
- [mm:ss-mm:ss] 主要结论。
- [mm:ss-mm:ss] 第二个结论。

备注：仅影响可信度的注意事项或发布失败。
```

不要把完整转录贴进聊天；留在报告或发布目标里。
