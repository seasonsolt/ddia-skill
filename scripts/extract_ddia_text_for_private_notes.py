#!/usr/bin/env python3
import argparse
import json
import pathlib
import subprocess
from typing import Any

from pypdf import PdfReader


DEFAULT_PDF = pathlib.Path(
    "/Users/Thin/Library/Mobile Documents/com~apple~CloudDocs/学习/分布式/designing-data-intensive-applications.pdf"
)


def page_filename(page_number: int) -> str:
    return f"page-{page_number:03d}.txt"


def write_page_text(output_dir: pathlib.Path, page_number: int, text: str) -> pathlib.Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    page_path = output_dir / page_filename(page_number)
    page_path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return page_path


def ensure_private_output_dir(output_dir: pathlib.Path, repo_root: pathlib.Path = pathlib.Path.cwd()) -> None:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    default_private_dir = repo_root / "tmp" / "ddia-extract"

    if output_dir == default_private_dir or output_dir.is_relative_to(default_private_dir):
        return

    result = subprocess.run(
        ["git", "check-ignore", "-q", "--", str(output_dir)],
        cwd=repo_root,
        check=False,
    )
    if result.returncode == 0:
        return

    raise ValueError(
        f"Refusing to write extracted DDIA text to non-private output directory: {output_dir}"
    )


def extract_private_text(
    pdf_path: pathlib.Path,
    output_dir: pathlib.Path,
    enforce_private_output: bool = True,
) -> dict[str, Any]:
    if enforce_private_output:
        ensure_private_output_dir(output_dir)

    reader = PdfReader(str(pdf_path))
    pages_dir = output_dir / "pages"
    page_rows: list[dict[str, Any]] = []

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        page_path = write_page_text(pages_dir, index, text)
        page_rows.append(
            {
                "page": index,
                "file": str(page_path),
                "character_count": len(text),
                "line_count": len(text.splitlines()),
            }
        )

    index_data = {
        "source_pdf": str(pdf_path),
        "page_count": len(reader.pages),
        "pages": page_rows,
        "copyright_note": "Private local extraction for reading notes. Do not commit tmp/ddia-extract.",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.json").write_text(
        json.dumps(index_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return index_data


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract DDIA text into ignored private files.")
    parser.add_argument("--pdf", type=pathlib.Path, default=DEFAULT_PDF)
    parser.add_argument("--output-dir", type=pathlib.Path, default=pathlib.Path("tmp/ddia-extract"))
    args = parser.parse_args()

    data = extract_private_text(args.pdf, args.output_dir)
    print(f"Wrote private text for {data['page_count']} pages under {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
