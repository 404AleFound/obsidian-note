"""Filter paper records and print a compact Markdown report."""

from __future__ import annotations

import json
import sys


def configure_output() -> None:
    """Prevent legacy Windows consoles from failing on Chinese text or emoji."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def markdown_cell(value: object) -> str:
    """Keep record values safe inside a Markdown table cell."""
    return str(value or "").replace("|", r"\|").replace("\n", " ")


def main() -> None:
    configure_output()
    records = json.load(sys.stdin)

    print("| \u6587\u4ef6 | \u662f\u5426\u4e3a\u8bba\u6587 |")
    print("|---|---|")
    for item in records:
        status = "\u2705 \u662f" if item.get("status") == "VALID" else "\u23ed\ufe0f \u5426"
        print(f"| `{markdown_cell(item.get('file', ''))}` | {status} |")

    valid = [item for item in records if item.get("status") == "VALID"]
    for item in valid:
        print()
        print(f"- \u6807\u9898：{item.get('title', '')}")
        print(f"- \u4f5c\u8005：{item.get('authors', '')}")
        print(f"- \u7ae0\u8282：{item.get('sections', '')}")
        print(f"- \u65f6\u95f4：{item.get('time', '论文未说明')}（来源：{item.get('time_source', '论文未说明')}）")
        print(f"- \u5b57\u6570：{item.get('total_wordNum', '')}")


if __name__ == "__main__":
    main()
