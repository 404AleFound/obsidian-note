#!/usr/bin/env python3
"""技能入口：以脚本方式直接调用 ytlt 业务代码，无需把业务代码装成包。

用法（从仓库根目录 D:\\19816\\obsidian-note 运行）：

    uv run python .claude/skills/video-to-notes/run.py process "VIDEO_URL" --environment local

yt-dlp / imageio-ffmpeg 等公共库由根目录 pyproject.toml + uv sync 提供。
"""

import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent

# 把本文件所在目录加入 sys.path，使 `import ytlt` 可用
sys.path.insert(0, str(SKILL_DIR))

from ytlt.cli import main  # noqa: E402
from ytlt.spec import default_workspace  # noqa: E402


def _seed_config() -> None:
    """把 skill 目录里的默认 config.json 播种到 workspace（仓库根），若 workspace 还没有。"""
    skill_config = SKILL_DIR / "config.json"
    workspace_config = default_workspace() / "config.json"
    if skill_config.exists() and not workspace_config.exists():
        shutil.copyfile(skill_config, workspace_config)


if __name__ == "__main__":
    _seed_config()
    raise SystemExit(main())
