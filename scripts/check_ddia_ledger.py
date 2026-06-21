#!/usr/bin/env python3
import argparse
import json
import pathlib
import re
from typing import Any


FIELD_NAMES = [
    "Target engineering decisions",
    "Failure modes",
    "Trade-offs",
    "Review questions",
    "Skill guidance",
]


def split_chapters(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^## (Chapter \d+\. .+)$", text, flags=re.MULTILINE))
    chapters: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        chapters.append((match.group(1), text[start:end]))
    return chapters


def count_field_bullets(chapter_text: str, field: str) -> int:
    pattern = rf"^### {re.escape(field)}\n(?P<body>.*?)(?=^### |^## |\Z)"
    match = re.search(pattern, chapter_text, flags=re.MULTILINE | re.DOTALL)
    if not match:
        return 0
    return len([line for line in match.group("body").splitlines() if line.startswith("- ") and len(line.strip()) > 2])


def check_ledger_text(text: str, required_chapters: int = 12) -> dict[str, Any]:
    chapters = split_chapters(text)
    missing_chapters = []
    incomplete_chapters = []

    for number in range(1, required_chapters + 1):
        prefix = f"Chapter {number}. "
        if not any(title.startswith(prefix) for title, _ in chapters):
            missing_chapters.append(prefix.rstrip())

    for title, chapter_text in chapters:
        reviewed = "Reviewed: yes" in chapter_text
        enough_bullets = all(count_field_bullets(chapter_text, field) >= 3 for field in FIELD_NAMES)
        if not reviewed or not enough_bullets:
            incomplete_chapters.append(title)

    return {
        "chapter_count": len(chapters),
        "missing_chapters": missing_chapters,
        "incomplete_chapters": incomplete_chapters,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check DDIA reading ledger coverage.")
    parser.add_argument("--ledger", type=pathlib.Path, default=pathlib.Path("analysis/ddia-reading-ledger.md"))
    args = parser.parse_args()

    report = check_ledger_text(args.ledger.read_text(encoding="utf-8"))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["missing_chapters"] or report["incomplete_chapters"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
