#!/usr/bin/env python3
"""拒绝 note-writer 写入指定笔记目录之外的文件。

Claude Code 的 PreToolUse Hook 会把工具调用 JSON 通过 stdin 传入。
退出码 2 表示拒绝本次工具调用。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def project_root() -> Path:
    configured_root = os.environ.get("CLAUDE_PROJECT_DIR")
    if configured_root:
        return Path(configured_root).expanduser().resolve()
    return Path.cwd().resolve()


def deny(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError) as exc:
        return deny(f"无法读取 Write Hook 输入：{exc}")

    tool_input = payload.get("tool_input") or {}
    raw_path = tool_input.get("file_path") or tool_input.get("path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        return deny("Write 调用缺少有效的 file_path。")

    root = project_root()
    target = Path(raw_path).expanduser()
    if not target.is_absolute():
        target = root / target
    target = target.resolve()

    allowed_root = (root / "01-assay-note").resolve()
    try:
        target.relative_to(allowed_root)
    except ValueError:
        return deny(
            "note-writer 只能写入 01-assay-note/ 下的 output_path；"
            "论文 PDF、MinerU Markdown 和其他目录均为只读。"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
