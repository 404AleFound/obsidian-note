"""Scan Markdown files and emit one paper-detection record per file."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


SECTION_NAMES = {
    "abstract": "Abstract",
    "摘要": "Abstract",
    "introduction": "Introduction",
    "引言": "Introduction",
    "background": "Background",
    "method": "Method",
    "methods": "Methods",
    "methodology": "Methodology",
    "model": "Model",
    "experiments": "Experiments",
    "experiment": "Experiment",
    "results": "Results",
    "result": "Results",
    "discussion": "Discussion",
    "conclusion": "Conclusion",
    "conclusions": "Conclusion",
    "结论": "Conclusion",
    "references": "References",
    "参考文献": "References",
}


def clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip(" -|:")


def title_of(text: str) -> str:
    match = re.search(r"(?m)^#\s+(.+?)\s*$", text[:6000])
    return clean(match.group(1)) if match else ""


def authors_of(text: str, title: str) -> str:
    if not title:
        return ""
    start = text.find(title)
    end_match = re.search(r"(?im)^#{1,6}\s*(abstract|摘要|introduction|引言)\b", text[start + len(title):])
    end = start + len(title) + end_match.start() if end_match else start + 5000
    block = text[start + len(title):end]
    names: list[str] = []
    for raw_line in block.splitlines():
        line = re.split(
            r"<sup|\s{2,}|\s+(?:Google|University|Research|Institute|Department)\b",
            raw_line,
            maxsplit=1,
        )[0]
        line = clean(line)
        if not line or line.startswith("#") or "@" in line:
            continue
        match = re.search(r"\b([A-Z][A-Za-z'’-]+(?:\s+[A-Z][A-Za-z'’-]+){1,3})\b", line)
        if match:
            name = match.group(1)
            if name not in names:
                names.append(name)
    return ", ".join(names[:3]) + (" ..." if len(names) > 3 else "")


def sections_of(text: str) -> str:
    found: list[str] = []
    for raw in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*$", text):
        key = re.sub(r"^[\d.\s]+", "", clean(raw)).lower()
        for candidate, label in SECTION_NAMES.items():
            if key == candidate or key.startswith(candidate + " "):
                if label not in found:
                    found.append(label)
                break
    return ", ".join(found)


def publication_time(text: str, filename: str = "") -> tuple[str, str]:
    match = re.search(r"(?im)^(?:time|date|published|year)\s*:\s*([^\n]+)", text[:3000])
    if match:
        return clean(match.group(1)), "论文正文"
    match = re.search(r"\b(19|20)\d{2}[/.-](0?[1-9]|1[0-2])\b", text[:6000])
    if match:
        return match.group(0).replace(".", "/").replace("-", "/"), "论文正文"
    arxiv = re.search(r"(?<!\d)(\d{2})(0[1-9]|1[0-2])\.\d{4,5}(?:v\d+)?", filename)
    if arxiv:
        return f"20{arxiv.group(1)}/{arxiv.group(2)}", "文件名 arXiv ID 推断"
    return "论文未说明", "论文未说明"


def inspect(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    title = title_of(text)
    authors = authors_of(text, title)
    sections = sections_of(text)
    has_content = bool(re.search(r"(?is)\b(abstract|摘要|introduction|引言)\b", text[:12000])) or len(text.split()) >= 200
    valid = bool(title and authors and has_content)
    missing = []
    if not title:
        missing.append("title")
    if not authors:
        missing.append("authors")
    if not has_content:
        missing.append("abstract_or_body")
    time, time_source = publication_time(text, path.name)
    return {
        "file": path.name,
        "status": "VALID" if valid else "NOT_VALID",
        "title": title,
        "authors": authors,
        "sections": sections,
        "time": time,
        "time_source": time_source,
        "total_wordNum": len(re.findall(r"\b\w+\b", text, flags=re.UNICODE)),
        "incomplete_reason": ", ".join(missing) or None,
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    records = [inspect(path) for path in sorted(Path.cwd().glob("*.md"))]
    print(json.dumps(records, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
