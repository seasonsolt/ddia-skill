#!/usr/bin/env python3
import argparse
import json
import pathlib
from typing import Any


FIELD_NAMES = [
    "Target engineering decisions",
    "Failure modes",
    "Trade-offs",
    "Review questions",
    "Skill guidance",
]


def chapter_rows(outline_data: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in outline_data["outline"]
        if item["depth"] == 1 and item["title"].startswith("Chapter ")
    ]


def render_ledger(outline_data: dict[str, Any]) -> str:
    lines = [
        "# DDIA Reading Ledger",
        "",
        "Original notes extracted from line-by-line reading of the local DDIA PDF.",
        "Do not paste long source passages into this file.",
        "",
    ]

    for row in chapter_rows(outline_data):
        lines.extend(
            [
                f"## {row['title']}",
                "",
                f"Start page: {row['page']}",
                "",
                "Reviewed: no",
                "",
            ]
        )
        for field in FIELD_NAMES:
            lines.extend([f"### {field}", "- ", "- ", "- ", ""])

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a DDIA reading ledger from outline JSON.")
    parser.add_argument("--outline", type=pathlib.Path, default=pathlib.Path("build/ddia-outline.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("analysis/ddia-reading-ledger.md"))
    args = parser.parse_args()

    outline_data = json.loads(args.outline.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_ledger(outline_data), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
