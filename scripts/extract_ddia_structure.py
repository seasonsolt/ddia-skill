#!/usr/bin/env python3
import argparse
import json
import pathlib
from typing import Any

from pypdf import PdfReader


DEFAULT_PDF = pathlib.Path(
    "/Users/Thin/Library/Mobile Documents/com~apple~CloudDocs/学习/分布式/designing-data-intensive-applications.pdf"
)


def normalize_metadata(metadata: Any) -> dict[str, str]:
    if not metadata:
        return {}

    normalized: dict[str, str] = {}
    for key, value in dict(metadata).items():
        clean_key = str(key).lstrip("/")
        normalized[clean_key[:1].lower() + clean_key[1:]] = str(value)
    return normalized


def flatten_outline(reader: PdfReader) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def walk(items: list[Any], depth: int) -> None:
        for item in items:
            if isinstance(item, list):
                walk(item, depth + 1)
                continue

            title = getattr(item, "title", str(item)).strip()
            try:
                page = reader.get_destination_page_number(item) + 1
            except Exception:
                page = None

            rows.append({"depth": depth, "title": title, "page": page})

    walk(reader.outline, 0)
    return rows


def extract_structure(pdf_path: pathlib.Path) -> dict[str, Any]:
    reader = PdfReader(str(pdf_path))
    outline = flatten_outline(reader)
    return {
        "source_pdf": str(pdf_path),
        "page_count": len(reader.pages),
        "metadata": normalize_metadata(reader.metadata),
        "outline": outline,
    }


def write_json(data: dict[str, Any], output_path: pathlib.Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract non-sensitive DDIA PDF structure.")
    parser.add_argument("--pdf", type=pathlib.Path, default=DEFAULT_PDF)
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("build/ddia-outline.json"),
    )
    args = parser.parse_args()

    data = extract_structure(args.pdf)
    write_json(data, args.output)
    print(f"Wrote {args.output} with {data['page_count']} pages and {len(data['outline'])} outline rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
