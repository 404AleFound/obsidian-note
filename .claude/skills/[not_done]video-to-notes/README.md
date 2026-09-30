# video-to-notes 技能说明

视频转「带时间戳的笔记 + 报告」技能。业务代码在本目录 `ytlt/`，公共依赖在仓库根目录 `pyproject.toml`。

## 一键恢复环境

在仓库根目录 `D:\19816\obsidian-note` 下：

```bash
uv sync                    # 装 yt-dlp + imageio-ffmpeg（业务代码在 skill 目录，无需安装）
uv run python .claude/skills/video-to-notes/run.py --help
```

## 输出位置

`process` 的输出（`processed/` 报告目录、`dashboard.html` 看板、`index.json` 索引）写到**仓库根 `obsidian-note/`**（即 Obsidian vault），而不是 skill 目录。`config.json` 固定在 skill 目录内，与输出位置解耦。

## 本地转录（可选，需要模型权重）

默认走「字幕直接下载」，**无需任何模型权重**。仅当视频没有可用字幕时才需要本地 Whisper 转录。

本机已下载 `large-v3-turbo` 权重，位于 `obsidian-note/.models/large-v3-turbo`，config.json 里用相对路径 `.models/large-v3-turbo` 引用。

安装运行时（会带入 ctranslate2 / onnxruntime / numpy 等）：

```bash
uv sync --extra whisper
```

无字幕视频转录（用 config 里的模型 + CPU，当前 `device: cpu`）：

```bash
uv run python .claude/skills/video-to-notes/run.py process "VIDEO_URL" --force-transcribe --environment local
```

> GPU 加速：本机 RTX 4060 需先补装 cuBLAS（`uv add nvidia-cublas-cu12` 或 NVIDIA CUDA Toolkit），再把 config.json 的 `device` 改回 `cuda`、`compute_type` 改回 `int8_float16`。

## 硬件 / 模型选择

| 本机规格 | 后端 | 默认模型 |
|---|---|---|
| 有可下载字幕 | 无 | 直接用字幕，最快最省 |
| NVIDIA CUDA ≥10GB 显存 | faster-whisper | `large-v3-turbo` |
| CPU / 集成显卡 | faster-whisper | `Systran/faster-whisper-small`（慢但可用） |

更多细节见 `ytlt/spec.py` 的 `MODEL_MATRIX`。

## 验证

```bash
uv run python -m pytest .claude/skills/video-to-notes/tests -q
```

## 目录结构

```text
video-to-notes/
├── SKILL.md          # 技能触发与工作流
├── README.md         # 本文件（环境与模型权重说明）
├── config.json       # 默认配置（相对路径 + CPU 兜底），与输出位置解耦
├── run.py            # 技能入口脚本（sys.path 指向 ytlt，无需安装）
├── ytlt/             # 业务代码（纯标准库，仅依赖 yt-dlp）
└── tests/            # 单元测试（含 conftest.py 让测试可 import ytlt）
```
