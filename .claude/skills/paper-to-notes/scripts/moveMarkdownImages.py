"""Copy local Markdown images into each document's assets directory."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote


IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)")


def image_references(text: str) -> list[str]:
    return [first or second for first, second in IMAGE_RE.findall(text)]


def is_remote(reference: str) -> bool:
    lowered = reference.lower().strip()
    return lowered.startswith(("http://", "https://", "data:", "//", "#"))


def destination_name(source: Path, assets: Path, used: set[str]) -> str:
    name = source.name
    candidate = name
    if candidate in used or (assets / candidate).exists():
        digest = hashlib.sha1(str(source).encode("utf-8")).hexdigest()[:8]
        candidate = f"{source.stem}-{digest}{source.suffix}"
    used.add(candidate)
    return candidate


def process_markdown(path: Path, dry_run: bool = False) -> dict[str, int]:
    text = path.read_text(encoding="utf-8")
    references = image_references(text)
    assets = path.parent / "assets"
    used: set[str] = set()
    assigned: dict[Path, str] = {}
    copied = skipped = missing = changed = 0

    for reference in references:
        if is_remote(reference):
            skipped += 1
            continue

        reference_path = Path(unquote(reference.split("#", 1)[0]))
        if reference_path.is_absolute():
            source = reference_path.resolve()
        else:
            source = (path.parent / reference_path).resolve()
        if not source.is_file():
            missing += 1
            continue

        if source.parent == assets.resolve():
            skipped += 1
            continue

        name = assigned.get(source)
        if name is None:
            name = destination_name(source, assets, used)
            assigned[source] = name
        target = assets / name
        new_reference = f"assets/{name}"
        if reference != new_reference:
            text = text.replace(reference, new_reference)
            changed += 1
        if not dry_run:
            assets.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        copied += 1

    if changed and not dry_run:
        path.write_text(text, encoding="utf-8", newline="")

    return {"copied": copied, "skipped": skipped, "missing": missing, "changed": changed}


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--dry-run", action="store_true", help="只扫描，不复制图片或修改 Markdown")
    args = parser.parse_args()

    totals = {"files": 0, "copied": 0, "skipped": 0, "missing": 0, "changed": 0}
    for path in sorted(args.root.resolve().rglob("*.md")):
        if "assets" in path.parts:
            continue
        result = process_markdown(path, args.dry_run)
        totals["files"] += 1
        for key, value in result.items():
            totals[key] += value
        if any(result.values()):
            print(f"{path}: {result}")

    print(f"总计: {totals}")


if __name__ == "__main__":
    main()
