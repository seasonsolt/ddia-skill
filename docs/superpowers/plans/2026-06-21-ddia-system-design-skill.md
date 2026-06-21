# DDIA System Design Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a versioned, installable Codex skill that turns Designing Data-Intensive Applications concepts into practical backend architecture review workflows.

**Architecture:** The repo stores extraction tools, reading notes, evaluation prompts, and the source skill package under `skills/ddia-system-design/`. Extracted PDF text stays under `tmp/ddia-extract/` and is ignored by Git; committed files contain original notes, checklists, and skill instructions only. The final task installs the skill by syncing the repo package to `/Users/Thin/.codex/skills/ddia-system-design`.

**Tech Stack:** Markdown skill files, Python standard library, `pypdf` from the bundled Codex Python runtime, `unittest`, and the existing skill-creator validation scripts.

---

## Scope Check

This is one focused subsystem: a DDIA-inspired Codex skill for backend engineers and architects. It does not build a web app, a PDF reader, or a searchable book database. The plan creates enough extraction and verification tooling to support careful line-by-line reading without committing copyrighted source text.

## Target Skill

- Skill source path: `/Users/Thin/Documents/ddia/skills/ddia-system-design`
- Installed skill path: `/Users/Thin/.codex/skills/ddia-system-design`
- Primary user: backend engineers and software architects designing or reviewing data-intensive systems.
- Main outcome: when a future Codex task asks about architecture, databases, distributed systems, consistency, replication, partitioning, streaming, batch processing, or correctness, the skill guides the agent through concrete DDIA-style trade-off analysis.

## File Structure

- `/Users/Thin/Documents/ddia/.gitignore`: keeps private PDF extraction output and build artifacts out of Git.
- `/Users/Thin/Documents/ddia/scripts/extract_ddia_structure.py`: reads the PDF outline and writes a non-copyright-sensitive JSON structure.
- `/Users/Thin/Documents/ddia/scripts/extract_ddia_text_for_private_notes.py`: extracts private page text into `tmp/ddia-extract/` for local line-by-line reading.
- `/Users/Thin/Documents/ddia/scripts/make_ddia_reading_ledger.py`: creates a chapter-by-chapter ledger from the outline.
- `/Users/Thin/Documents/ddia/scripts/check_ddia_ledger.py`: verifies that the ledger has complete original notes for all 12 chapters.
- `/Users/Thin/Documents/ddia/scripts/check_ddia_skill_quality.py`: verifies skill structure, references, trigger coverage, and evaluation assets.
- `/Users/Thin/Documents/ddia/tests/`: deterministic unit tests for the scripts and skill package.
- `/Users/Thin/Documents/ddia/docs/ddia-reading-protocol.md`: the process for reading the local PDF line by line and writing original notes.
- `/Users/Thin/Documents/ddia/analysis/ddia-reading-ledger.md`: original extraction notes organized by chapter.
- `/Users/Thin/Documents/ddia/evaluation/`: prompts, rubric, and results template for usefulness testing.
- `/Users/Thin/Documents/ddia/skills/ddia-system-design/SKILL.md`: concise trigger and workflow instructions for the skill.
- `/Users/Thin/Documents/ddia/skills/ddia-system-design/references/topic-map.md`: DDIA topic map by engineering problem.
- `/Users/Thin/Documents/ddia/skills/ddia-system-design/references/system-design-principles.md`: original principles extracted from the reading ledger.
- `/Users/Thin/Documents/ddia/skills/ddia-system-design/references/architecture-review-checklists.md`: reusable review checklists.
- `/Users/Thin/Documents/ddia/skills/ddia-system-design/agents/openai.yaml`: UI metadata generated from skill content.

---

### Task 1: Add Project Guardrails And PDF Structure Extraction

**Files:**
- Create: `/Users/Thin/Documents/ddia/.gitignore`
- Create: `/Users/Thin/Documents/ddia/scripts/extract_ddia_structure.py`
- Create: `/Users/Thin/Documents/ddia/tests/test_extract_ddia_structure.py`
- Output when running: `/Users/Thin/Documents/ddia/build/ddia-outline.json`

- [ ] **Step 1: Write the failing test**

Create `/Users/Thin/Documents/ddia/tests/test_extract_ddia_structure.py`:

```python
import importlib.util
import json
import os
import pathlib
import tempfile
import unittest


REPO = pathlib.Path(__file__).resolve().parents[1]
PDF_PATH = pathlib.Path(
    os.environ.get(
        "DDIA_PDF_PATH",
        "/Users/Thin/Library/Mobile Documents/com~apple~CloudDocs/学习/分布式/designing-data-intensive-applications.pdf",
    )
)


def load_module():
    module_path = REPO / "scripts" / "extract_ddia_structure.py"
    spec = importlib.util.spec_from_file_location("extract_ddia_structure", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExtractDdiaStructureTest(unittest.TestCase):
    def test_extracts_expected_ddia_outline(self):
        self.assertTrue(PDF_PATH.exists(), f"Missing PDF: {PDF_PATH}")
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            output = pathlib.Path(tmp) / "outline.json"
            data = module.extract_structure(PDF_PATH)
            module.write_json(data, output)
            written = json.loads(output.read_text(encoding="utf-8"))

        chapter_titles = [
            item["title"]
            for item in written["outline"]
            if item["depth"] == 1 and item["title"].startswith("Chapter ")
        ]

        self.assertEqual(written["metadata"]["title"], "Designing Data-Intensive Applications")
        self.assertEqual(written["page_count"], 613)
        self.assertEqual(len(chapter_titles), 12)
        self.assertIn("Chapter 5. Replication", chapter_titles)
        self.assertIn("Chapter 9. Consistency and Consensus", chapter_titles)
        self.assertIn("Chapter 12. The Future of Data Systems", chapter_titles)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_extract_ddia_structure -v
```

Expected: FAIL with a missing file error for `scripts/extract_ddia_structure.py`.

- [ ] **Step 3: Write the extractor implementation**

Create `/Users/Thin/Documents/ddia/scripts/extract_ddia_structure.py`:

```python
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
```

- [ ] **Step 4: Add Git guardrails**

Create `/Users/Thin/Documents/ddia/.gitignore`:

```gitignore
build/
tmp/
__pycache__/
.pytest_cache/
*.pyc
```

- [ ] **Step 5: Run the test to verify it passes**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_extract_ddia_structure -v
```

Expected: PASS for `test_extracts_expected_ddia_outline`.

- [ ] **Step 6: Generate the outline artifact**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/extract_ddia_structure.py \
  --pdf "/Users/Thin/Library/Mobile Documents/com~apple~CloudDocs/学习/分布式/designing-data-intensive-applications.pdf" \
  --output build/ddia-outline.json
```

Expected output:

```text
Wrote build/ddia-outline.json with 613 pages and 210 outline rows
```

- [ ] **Step 7: Commit the task**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add .gitignore scripts/extract_ddia_structure.py tests/test_extract_ddia_structure.py
git commit -m "chore: add ddia outline extraction"
```

---

### Task 2: Add Private Text Extraction And Reading Protocol

**Files:**
- Create: `/Users/Thin/Documents/ddia/scripts/extract_ddia_text_for_private_notes.py`
- Create: `/Users/Thin/Documents/ddia/tests/test_extract_ddia_text_for_private_notes.py`
- Create: `/Users/Thin/Documents/ddia/docs/ddia-reading-protocol.md`
- Output when running: `/Users/Thin/Documents/ddia/tmp/ddia-extract/pages/page-001.txt`
- Output when running: `/Users/Thin/Documents/ddia/tmp/ddia-extract/index.json`

- [ ] **Step 1: Write the failing test**

Create `/Users/Thin/Documents/ddia/tests/test_extract_ddia_text_for_private_notes.py`:

```python
import importlib.util
import pathlib
import tempfile
import unittest


REPO = pathlib.Path(__file__).resolve().parents[1]


def load_module():
    module_path = REPO / "scripts" / "extract_ddia_text_for_private_notes.py"
    spec = importlib.util.spec_from_file_location("extract_ddia_text_for_private_notes", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExtractDdiaTextForPrivateNotesTest(unittest.TestCase):
    def test_page_filename_is_stable(self):
        module = load_module()
        self.assertEqual(module.page_filename(1), "page-001.txt")
        self.assertEqual(module.page_filename(99), "page-099.txt")
        self.assertEqual(module.page_filename(613), "page-613.txt")

    def test_write_page_text_creates_private_files(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = pathlib.Path(tmp)
            page_path = module.write_page_text(output_dir, 7, "alpha\nbeta")
            self.assertEqual(page_path.name, "page-007.txt")
            self.assertEqual(page_path.read_text(encoding="utf-8"), "alpha\nbeta\n")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_extract_ddia_text_for_private_notes -v
```

Expected: FAIL with a missing file error for `scripts/extract_ddia_text_for_private_notes.py`.

- [ ] **Step 3: Write the private extraction script**

Create `/Users/Thin/Documents/ddia/scripts/extract_ddia_text_for_private_notes.py`:

```python
#!/usr/bin/env python3
import argparse
import json
import pathlib
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


def extract_private_text(pdf_path: pathlib.Path, output_dir: pathlib.Path) -> dict[str, Any]:
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
```

- [ ] **Step 4: Write the reading protocol**

Create `/Users/Thin/Documents/ddia/docs/ddia-reading-protocol.md`:

```markdown
# DDIA Reading Protocol

This repository may read the local DDIA PDF to create an original Codex skill. The final committed skill must not contain long copied passages from the book.

## Source

- Local PDF: `/Users/Thin/Library/Mobile Documents/com~apple~CloudDocs/学习/分布式/designing-data-intensive-applications.pdf`
- Private extracted text: `/Users/Thin/Documents/ddia/tmp/ddia-extract/pages/`
- Committed original notes: `/Users/Thin/Documents/ddia/analysis/ddia-reading-ledger.md`

## Reading Method

Read pages in order inside each chapter. For every chapter, write original notes in the ledger using these fields:

- `Target engineering decisions`: real decisions a backend engineer or architect makes.
- `Failure modes`: ways a design can break under load, faults, concurrency, or operations.
- `Trade-offs`: explicit cost, correctness, latency, complexity, and operability choices.
- `Review questions`: questions a future Codex agent should ask before recommending a design.
- `Skill guidance`: concise instructions that can be moved into the skill references.

## Copyright Discipline

- Use original wording in committed files.
- Keep copied source text only in `tmp/ddia-extract/`, which is ignored by Git.
- Keep direct quotations out of the skill unless a short phrase is necessary and clearly attributed.
- Prefer concepts, checklists, and decision frameworks over book summaries.

## Coverage Standard

The ledger is complete when all 12 chapters are marked `Reviewed: yes`, each chapter has at least three bullets in every field, and each bullet gives practical guidance rather than a paraphrased sentence.
```

- [ ] **Step 5: Run the tests to verify they pass**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_extract_ddia_text_for_private_notes -v
```

Expected: PASS for both text extraction helper tests.

- [ ] **Step 6: Extract private page text**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/extract_ddia_text_for_private_notes.py \
  --pdf "/Users/Thin/Library/Mobile Documents/com~apple~CloudDocs/学习/分布式/designing-data-intensive-applications.pdf" \
  --output-dir tmp/ddia-extract
```

Expected output:

```text
Wrote private text for 613 pages under tmp/ddia-extract
```

- [ ] **Step 7: Confirm private text is ignored**

Run:

```bash
cd /Users/Thin/Documents/ddia
git status --short tmp/ddia-extract
```

Expected: no output.

- [ ] **Step 8: Commit the task**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add scripts/extract_ddia_text_for_private_notes.py tests/test_extract_ddia_text_for_private_notes.py docs/ddia-reading-protocol.md
git commit -m "chore: add private ddia reading extraction"
```

---

### Task 3: Create And Verify The DDIA Reading Ledger

**Files:**
- Create: `/Users/Thin/Documents/ddia/scripts/make_ddia_reading_ledger.py`
- Create: `/Users/Thin/Documents/ddia/scripts/check_ddia_ledger.py`
- Create: `/Users/Thin/Documents/ddia/tests/test_ddia_reading_ledger.py`
- Create after running: `/Users/Thin/Documents/ddia/analysis/ddia-reading-ledger.md`

- [ ] **Step 1: Write the failing test**

Create `/Users/Thin/Documents/ddia/tests/test_ddia_reading_ledger.py`:

```python
import importlib.util
import pathlib
import tempfile
import textwrap
import unittest


REPO = pathlib.Path(__file__).resolve().parents[1]


def load_script(name: str):
    module_path = REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DdiaReadingLedgerTest(unittest.TestCase):
    def test_make_ledger_uses_chapter_rows(self):
        module = load_script("make_ddia_reading_ledger")
        outline = {
            "outline": [
                {"depth": 1, "title": "Chapter 1. Reliable, Scalable, and Maintainable Applications", "page": 25},
                {"depth": 1, "title": "Chapter 2. Data Models and Query Languages", "page": 49},
            ]
        }
        ledger = module.render_ledger(outline)
        self.assertIn("## Chapter 1. Reliable, Scalable, and Maintainable Applications", ledger)
        self.assertIn("Reviewed: no", ledger)
        self.assertIn("Target engineering decisions", ledger)

    def test_checker_accepts_complete_chapter_notes(self):
        checker = load_script("check_ddia_ledger")
        ledger = textwrap.dedent(
            """
            # DDIA Reading Ledger

            ## Chapter 1. Example

            Reviewed: yes

            ### Target engineering decisions
            - Pick storage based on query shape.
            - Name the workload before choosing tools.
            - Separate correctness needs from convenience preferences.

            ### Failure modes
            - Backpressure can hide until queues grow without bounds.
            - Retry loops can amplify overload.
            - Operational tasks can fail when ownership is unclear.

            ### Trade-offs
            - Stronger guarantees often cost latency or availability.
            - More indexes improve reads while slowing writes.
            - Denormalization improves locality while adding update risk.

            ### Review questions
            - What load metric describes the hard part of this system?
            - Which reads must observe the caller's writes?
            - How will operators detect lag before users report it?

            ### Skill guidance
            - Ask for workload shape before recommending storage.
            - Surface consistency and operability trade-offs together.
            - Convert abstract guarantees into user-visible behavior.
            """
        )
        report = checker.check_ledger_text(ledger, required_chapters=1)
        self.assertEqual(report["missing_chapters"], [])
        self.assertEqual(report["incomplete_chapters"], [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_reading_ledger -v
```

Expected: FAIL with missing files for the two ledger scripts.

- [ ] **Step 3: Write the ledger generator**

Create `/Users/Thin/Documents/ddia/scripts/make_ddia_reading_ledger.py`:

```python
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
```

- [ ] **Step 4: Write the ledger checker**

Create `/Users/Thin/Documents/ddia/scripts/check_ddia_ledger.py`:

```python
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
```

- [ ] **Step 5: Run the test to verify it passes**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_reading_ledger -v
```

Expected: PASS for both ledger tests.

- [ ] **Step 6: Generate the ledger**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/make_ddia_reading_ledger.py \
  --outline build/ddia-outline.json \
  --output analysis/ddia-reading-ledger.md
```

Expected output:

```text
Wrote analysis/ddia-reading-ledger.md
```

- [ ] **Step 7: Read DDIA line by line and complete original notes**

Use the private page files under `/Users/Thin/Documents/ddia/tmp/ddia-extract/pages/`. Read each chapter's page range in order and update `/Users/Thin/Documents/ddia/analysis/ddia-reading-ledger.md`.

Use these chapter ranges from the extracted outline:

```text
Chapter 1: pages 25-48
Chapter 2: pages 49-90
Chapter 3: pages 91-132
Chapter 4: pages 133-166
Chapter 5: pages 173-220
Chapter 6: pages 221-242
Chapter 7: pages 243-294
Chapter 8: pages 295-342
Chapter 9: pages 343-406
Chapter 10: pages 411-460
Chapter 11: pages 461-510
Chapter 12: pages 511-574
```

For each chapter:

```text
1. Read the private page text in increasing page order.
2. Convert concepts into original engineering guidance.
3. Add at least three bullets under every ledger field.
4. Mark `Reviewed: yes` only after the chapter pages have been read.
5. Do not paste source paragraphs into the ledger.
```

- [ ] **Step 8: Verify ledger coverage**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_ledger.py \
  --ledger analysis/ddia-reading-ledger.md
```

Expected output shape:

```json
{
  "chapter_count": 12,
  "missing_chapters": [],
  "incomplete_chapters": []
}
```

Expected command status: exit code 0.

- [ ] **Step 9: Commit the task**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add scripts/make_ddia_reading_ledger.py scripts/check_ddia_ledger.py tests/test_ddia_reading_ledger.py analysis/ddia-reading-ledger.md
git commit -m "docs: add original ddia reading ledger"
```

---

### Task 4: Scaffold The Skill Package

**Files:**
- Create directory through script: `/Users/Thin/Documents/ddia/skills/ddia-system-design`
- Create through script: `/Users/Thin/Documents/ddia/skills/ddia-system-design/SKILL.md`
- Create through script: `/Users/Thin/Documents/ddia/skills/ddia-system-design/references/`
- Create through script: `/Users/Thin/Documents/ddia/skills/ddia-system-design/agents/openai.yaml`

- [ ] **Step 1: Initialize the skill package**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  /Users/Thin/.codex/skills/.system/skill-creator/scripts/init_skill.py ddia-system-design \
  --path /Users/Thin/Documents/ddia/skills \
  --resources references \
  --interface display_name="DDIA System Design" \
  --interface short_description="Apply DDIA-style backend architecture review." \
  --interface default_prompt="Use DDIA system design to review this architecture for trade-offs, failure modes, and verification steps."
```

Expected: a new `/Users/Thin/Documents/ddia/skills/ddia-system-design` folder with `SKILL.md`, `references/`, and `agents/openai.yaml`.

- [ ] **Step 2: Verify scaffold files exist**

Run:

```bash
cd /Users/Thin/Documents/ddia
test -f skills/ddia-system-design/SKILL.md
test -d skills/ddia-system-design/references
test -f skills/ddia-system-design/agents/openai.yaml
```

Expected: no output and exit code 0.

- [ ] **Step 3: Commit the scaffold**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add skills/ddia-system-design
git commit -m "chore: scaffold ddia system design skill"
```

---

### Task 5: Write The Skill Instructions And References

**Files:**
- Modify: `/Users/Thin/Documents/ddia/skills/ddia-system-design/SKILL.md`
- Create: `/Users/Thin/Documents/ddia/skills/ddia-system-design/references/topic-map.md`
- Create: `/Users/Thin/Documents/ddia/skills/ddia-system-design/references/system-design-principles.md`
- Create: `/Users/Thin/Documents/ddia/skills/ddia-system-design/references/architecture-review-checklists.md`
- Create: `/Users/Thin/Documents/ddia/tests/test_ddia_skill_content.py`

- [ ] **Step 1: Write the failing skill content test**

Create `/Users/Thin/Documents/ddia/tests/test_ddia_skill_content.py`:

```python
import pathlib
import re
import unittest


REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "ddia-system-design"


class DdiaSkillContentTest(unittest.TestCase):
    def test_skill_frontmatter_and_reference_links(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: ddia-system-design", text)
        self.assertIn("description:", text)
        self.assertIn("references/topic-map.md", text)
        self.assertIn("references/system-design-principles.md", text)
        self.assertIn("references/architecture-review-checklists.md", text)

    def test_references_cover_core_backend_topics(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [
                SKILL / "references" / "topic-map.md",
                SKILL / "references" / "system-design-principles.md",
                SKILL / "references" / "architecture-review-checklists.md",
            ]
        ).lower()
        required_terms = [
            "reliability",
            "scalability",
            "maintainability",
            "replication",
            "partitioning",
            "transactions",
            "isolation",
            "linearizability",
            "consensus",
            "stream processing",
            "batch processing",
            "derived data",
        ]
        for term in required_terms:
            self.assertIn(term, combined)

    def test_skill_has_no_empty_bullets(self):
        for path in [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"(?m)^-\s*$", text), f"Empty bullet in {path}")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_skill_content -v
```

Expected: FAIL because the scaffolded skill content does not yet link the required references.

- [ ] **Step 3: Replace `SKILL.md` with concise trigger and workflow instructions**

Write `/Users/Thin/Documents/ddia/skills/ddia-system-design/SKILL.md` with this structure and original wording derived from the completed ledger:

```markdown
---
name: ddia-system-design
description: Apply Designing Data-Intensive Applications inspired architecture reasoning for backend engineering and system design. Use when reviewing or designing data-intensive systems, database choices, storage/indexing, replication, partitioning, transactions, isolation levels, distributed faults, consistency, consensus, batch processing, stream processing, derived data, correctness, reliability, scalability, maintainability, or operational trade-offs.
---

# DDIA System Design

Use this skill to turn a backend architecture question into explicit workload assumptions, data model choices, consistency requirements, failure modes, and verification steps.

## Core Workflow

1. Frame the system goal in terms of data, users, writes, reads, latency, durability, and operational ownership.
2. Name the workload before choosing tools: request rate, data size, hot keys, fan-out, read/write ratio, freshness needs, and recovery objectives.
3. Separate facts from choices: required correctness guarantees, acceptable staleness, acceptable data loss, and business-visible failure behavior.
4. Analyze the design through four lenses: reliability, scalability, maintainability, and evolvability.
5. Surface trade-offs explicitly. Do not recommend a database, queue, cache, or consensus mechanism without explaining the cost.
6. Convert abstract guarantees into tests, observability signals, and runbook checks.

## Load References Selectively

- Read `references/topic-map.md` when mapping a user problem to relevant DDIA themes.
- Read `references/system-design-principles.md` when making or reviewing architecture decisions.
- Read `references/architecture-review-checklists.md` when the user asks for a review, critique, design doc, or failure-mode analysis.

## Response Shape

Prefer this structure unless the user asks for a different format:

1. Assumptions and workload shape
2. Recommendation
3. Key trade-offs
4. Failure modes
5. Consistency and correctness implications
6. Operational checks
7. Tests or experiments to validate the design

## Guardrails

- Ask for missing workload and correctness requirements before making a strong recommendation.
- Avoid one-size-fits-all answers such as always using Kafka, microservices, NoSQL, or strong consistency.
- Treat caches, indexes, replicas, materialized views, and streams as derived data that can become stale or incorrect.
- Discuss human operations: deployment, recovery, backfills, schema evolution, monitoring, and incident response.
- Keep direct book quotations out of responses unless the user explicitly asks for a short cited quote.
```

- [ ] **Step 4: Write `topic-map.md` from the ledger**

Create `/Users/Thin/Documents/ddia/skills/ddia-system-design/references/topic-map.md` using this section structure:

```markdown
# DDIA Topic Map For Backend Architecture

Use this map to connect a user's architecture problem to the right review lens.

## Reliability, Scalability, Maintainability

- Use for: system health, load growth, operational maturity, change safety, and complexity control.
- Ask: what can fail, how will the system keep serving users, and how will operators understand it?
- Watch for: unclear load metrics, unbounded queues, hidden coupling, manual recovery, and designs that cannot evolve.

## Data Models And Query Languages

- Use for: relational versus document modeling, graph-shaped relationships, query flexibility, and schema ownership.
- Ask: which access patterns are primary, which relationships change, and which invariants the model must protect.
- Watch for: embedding data that needs independent updates, joins pushed into application code, and models chosen for convenience rather than query shape.

## Storage And Retrieval

- Use for: indexing, write amplification, read latency, analytics layout, and OLTP versus OLAP boundaries.
- Ask: whether the workload is point lookup, range scan, full-text search, aggregation, or analytical scan.
- Watch for: indexes that slow writes, compaction costs, cache dependence, and mixing transactional and analytical workloads without isolation.

## Encoding And Evolution

- Use for: schema evolution, API compatibility, event formats, and rolling deployments.
- Ask: whether old and new producers and consumers can coexist during deployment.
- Watch for: language-specific encodings, ambiguous JSON contracts, and changes that break stored records or asynchronous messages.

## Replication

- Use for: read scaling, high availability, failover, multi-region writes, and replica lag.
- Ask: which reads need fresh data and what users observe during failover or network delay.
- Watch for: stale reads, non-monotonic reads, conflict resolution gaps, split ownership, and assuming asynchronous replicas are current.

## Partitioning

- Use for: large data sets, high throughput, hot keys, secondary indexes, and rebalancing.
- Ask: what key distributes load, what queries cross partitions, and how rebalancing affects availability.
- Watch for: skew, celebrity keys, global secondary index cost, manual routing, and operationally risky repartitioning.

## Transactions And Isolation

- Use for: invariants, concurrent updates, financial correctness, inventory, booking, and workflow state.
- Ask: which anomalies are unacceptable and whether single-object guarantees are enough.
- Watch for: lost updates, write skew, phantoms, read-modify-write races, and assuming "transaction" means serializable behavior.

## Distributed Faults

- Use for: timeouts, retries, clocks, process pauses, network partitions, and partial failure.
- Ask: what the system knows, what it only suspects, and how it behaves when messages are delayed.
- Watch for: unsafe timeout assumptions, wall-clock ordering, retry storms, and failure detectors treated as truth.

## Consistency And Consensus

- Use for: leader election, locks, uniqueness, ordering, coordination, and linearizable operations.
- Ask: which operations require a single up-to-date view and what availability cost is acceptable.
- Watch for: global locks, unsafe leases, split-brain risk, two-phase commit blocking, and hidden consensus requirements.

## Batch Processing

- Use for: backfills, analytics, reconciliation, offline joins, and large-scale derived views.
- Ask: whether the job can be rerun, how intermediate state is stored, and how outputs replace old results.
- Watch for: non-idempotent outputs, expensive shuffles, unclear data snapshots, and unrecoverable partial writes.

## Stream Processing

- Use for: event-driven systems, CDC, real-time materialized views, alerting, and near-real-time joins.
- Ask: event time versus processing time, ordering guarantees, replay strategy, and exactly-once expectations.
- Watch for: duplicate events, poison messages, late data, partition ordering assumptions, and state restoration gaps.

## Derived Data And Correctness

- Use for: caches, search indexes, materialized views, denormalized tables, and data integration.
- Ask: source of truth, derivation path, repair mechanism, and verification strategy.
- Watch for: silent divergence, missing reconciliation, privacy leakage, and derived state treated as authoritative.
```

- [ ] **Step 5: Write `system-design-principles.md` from the ledger**

Create `/Users/Thin/Documents/ddia/skills/ddia-system-design/references/system-design-principles.md` using this section structure:

```markdown
# System Design Principles

These principles are original engineering guidance extracted from DDIA reading notes.

## Start With Workload Shape

- Define load with concrete dimensions: request rate, write rate, read fan-out, data volume, key distribution, peak-to-average ratio, and growth rate.
- Choose representative operations before choosing storage. A system optimized for point lookups can be poor for range scans or aggregations.
- Include operational load: deployments, backfills, failover, rebalancing, compaction, and schema migrations.

## Treat Guarantees As Product Behavior

- Translate consistency terms into user-visible outcomes, such as whether a user sees their own write after refresh.
- Decide which anomalies are acceptable before selecting isolation levels or replication modes.
- Stronger guarantees often move cost into coordination, latency, reduced availability, or operational complexity.

## Model Derived Data Explicitly

- Caches, replicas, indexes, search documents, materialized views, and stream outputs are derived data.
- Every derived data path needs a source of truth, update mechanism, lag signal, and repair procedure.
- If derived state can affect correctness, add reconciliation instead of relying only on happy-path propagation.

## Design For Partial Failure

- In distributed systems, some components can continue while others are slow, paused, partitioned, or unreachable.
- Timeouts detect uncertainty, not truth. Retried operations need idempotency or deduplication.
- Clocks are useful for measurement and ordering hints, but correctness should not depend on perfectly synchronized wall time unless the system proves that bound.

## Make Evolution A First-Class Requirement

- Store and transmit data in formats that allow old and new code to coexist.
- Plan for rolling deploys, replaying old events, reading old records, and adding optional fields.
- Prefer explicit contracts over language-specific serialization formats that couple producers and consumers.

## Prefer Simple Ownership Boundaries

- Put invariants near the data and transaction boundary that protects them.
- Avoid splitting a strongly consistent invariant across services unless the design includes coordination or compensation.
- Keep operational ownership clear: someone must know how to backfill, repair, monitor, and recover each data path.

## Review Storage Choices By Access Pattern

- Relational models fit many-to-one and many-to-many relationships when joins and constraints matter.
- Document models fit locality and whole-document access when independent updates are limited.
- Graph models fit highly connected data with traversal-heavy queries.
- LSM-style storage often favors write throughput and compression at the cost of compaction behavior.
- B-tree-style storage often favors predictable point and range reads with different write and space costs.

## Review Replication Choices By Failure Behavior

- Synchronous replication can reduce data loss but increases write latency and availability risk.
- Asynchronous replication improves availability and latency but introduces lag and stale reads.
- Multi-leader replication can support multi-region writes but requires explicit conflict handling.
- Leaderless quorum systems need careful reasoning about read/write quorums, stale replicas, sloppy quorum behavior, and concurrent writes.

## Review Partitioning Choices By Skew And Query Routing

- Hash partitioning spreads keys but weakens range locality.
- Range partitioning preserves ordering but can create hot partitions.
- Secondary indexes either scatter writes or scatter reads; both costs should be visible.
- Rebalancing should be observable, rate-limited, reversible, and planned around operational risk.

## Review Transactions By Anomaly

- Read committed, snapshot isolation, and serializable isolation prevent different anomaly sets.
- Lost updates, write skew, and phantoms should be tested with concurrent operations, not assumed away.
- Single-object atomicity does not protect multi-object invariants.
- Application-level checks outside the database transaction can be invalidated by concurrent writes.

## Review Streams By Replay And Time

- Event logs are useful when consumers need replay, ordering per partition, and independent consumption.
- Stream processors should define event time, processing time, late data behavior, state storage, and recovery.
- Exactly-once claims usually depend on idempotent sinks, transactions, or deduplication; ask where duplicates are eliminated.
- CDC and event sourcing can keep systems in sync, but they also create schema evolution and backfill obligations.
```

- [ ] **Step 6: Write `architecture-review-checklists.md` from the ledger**

Create `/Users/Thin/Documents/ddia/skills/ddia-system-design/references/architecture-review-checklists.md` using this section structure:

```markdown
# Architecture Review Checklists

Use these checklists when reviewing a backend design, system design answer, architecture document, or production migration.

## Workload Checklist

- What are the primary reads and writes?
- What are p50, p95, and p99 latency goals?
- What is the expected data volume now and after one year?
- Which keys, tenants, users, or regions may become hot?
- Which operations must keep working during degraded dependency behavior?
- Which backfills, migrations, or analytical jobs will compete with serving traffic?

## Data Model Checklist

- Which entities need independent updates?
- Which relationships are many-to-one or many-to-many?
- Which invariants must be enforced by storage rather than application convention?
- Which queries require joins, graph traversal, search, or aggregation?
- How will schema changes roll out across old and new application versions?

## Replication And Consistency Checklist

- Which reads can be stale and which must be current?
- Does the user need read-your-writes, monotonic reads, or consistent prefix reads?
- What happens during leader failover?
- How are write conflicts detected and resolved?
- What observability shows replica lag and replication failure?

## Partitioning Checklist

- What partition key distributes load for the hardest write path?
- Which queries cross partitions?
- How are secondary indexes partitioned?
- What is the hot-key mitigation plan?
- How does rebalancing happen without causing an incident?

## Transaction And Correctness Checklist

- Which invariants span multiple rows, documents, services, or partitions?
- Which isolation level is required to protect those invariants?
- Can concurrent requests cause lost update, write skew, or phantom anomalies?
- Are retries idempotent?
- Are uniqueness, balance, inventory, quota, and booking constraints tested under concurrency?

## Distributed Failure Checklist

- Which calls have timeouts, and what happens after timeout?
- Can retries amplify overload?
- What happens when a process pauses after taking a lock or lease?
- Does any correctness decision depend on wall-clock time?
- What is the behavior under network partition, packet delay, duplicate messages, and reordered messages?

## Batch And Stream Checklist

- Can the job or consumer be safely replayed?
- Are outputs idempotent or transactionally committed?
- How are late, duplicate, missing, or out-of-order events handled?
- Where is stream processor state stored and restored?
- How are backfills coordinated with live updates?

## Derived Data Checklist

- What is the source of truth?
- How is derived state updated?
- How is lag measured?
- How is divergence detected?
- How is corrupted derived state rebuilt?
- What user or business action is unsafe while derived state is stale?

## Recommendation Checklist

- State the recommendation in one paragraph.
- List the top three trade-offs.
- Name the most likely failure mode.
- Name the operational signal that would reveal that failure mode.
- Give one test or experiment that can falsify the recommendation.
```

- [ ] **Step 7: Regenerate UI metadata**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  /Users/Thin/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py \
  /Users/Thin/Documents/ddia/skills/ddia-system-design \
  --interface display_name="DDIA System Design" \
  --interface short_description="Apply DDIA-style backend architecture review." \
  --interface default_prompt="Use DDIA system design to review this architecture for trade-offs, failure modes, and verification steps."
```

Expected: `skills/ddia-system-design/agents/openai.yaml` is updated without errors.

- [ ] **Step 8: Run the skill content test to verify it passes**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_skill_content -v
```

Expected: PASS for all skill content tests.

- [ ] **Step 9: Validate the skill folder**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  /Users/Thin/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/Thin/Documents/ddia/skills/ddia-system-design
```

Expected: validation succeeds with no errors.

- [ ] **Step 10: Commit the task**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add skills/ddia-system-design tests/test_ddia_skill_content.py
git commit -m "feat: add ddia system design skill content"
```

---

### Task 6: Add Usefulness Evaluation Suite

**Files:**
- Create: `/Users/Thin/Documents/ddia/evaluation/rubric.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/prompts/01-order-consistency.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/prompts/02-event-pipeline.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/prompts/03-database-choice.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/prompts/04-replica-lag.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/prompts/05-derived-data.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/results-template.md`
- Create: `/Users/Thin/Documents/ddia/scripts/check_ddia_skill_quality.py`
- Create: `/Users/Thin/Documents/ddia/tests/test_ddia_skill_quality.py`

- [ ] **Step 1: Write the failing quality test**

Create `/Users/Thin/Documents/ddia/tests/test_ddia_skill_quality.py`:

```python
import importlib.util
import pathlib
import unittest


REPO = pathlib.Path(__file__).resolve().parents[1]


def load_checker():
    module_path = REPO / "scripts" / "check_ddia_skill_quality.py"
    spec = importlib.util.spec_from_file_location("check_ddia_skill_quality", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DdiaSkillQualityTest(unittest.TestCase):
    def test_quality_checker_accepts_complete_assets(self):
        checker = load_checker()
        report = checker.check_repo(REPO)
        self.assertEqual(report["missing_files"], [])
        self.assertEqual(report["missing_terms"], [])
        self.assertEqual(report["prompt_count"], 5)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_skill_quality -v
```

Expected: FAIL with a missing file error for `scripts/check_ddia_skill_quality.py`.

- [ ] **Step 3: Write the evaluation rubric**

Create `/Users/Thin/Documents/ddia/evaluation/rubric.md`:

```markdown
# DDIA Skill Usefulness Rubric

Score each response from 0 to 2 on each dimension.

## Dimensions

1. Workload framing: identifies reads, writes, load, latency, data volume, and growth assumptions.
2. Trade-off quality: explains costs rather than naming a tool as automatically correct.
3. Failure-mode coverage: names concrete ways the design can fail under concurrency, faults, lag, overload, or operations.
4. Correctness reasoning: discusses isolation, consistency, idempotency, ordering, or reconciliation where relevant.
5. Verification value: gives tests, metrics, experiments, or runbook checks that can validate the design.

## Passing Standard

A prompt passes when the response scores at least 8 out of 10 and has no dimension scored 0.

The skill passes the evaluation suite when all five prompts pass.
```

- [ ] **Step 4: Write evaluation prompts**

Create `/Users/Thin/Documents/ddia/evaluation/prompts/01-order-consistency.md`:

```markdown
# Prompt 1: Order Consistency

Use the DDIA system design skill to review this design:

We are building an order service. Users can place orders, cancel orders, and view order history. Inventory is stored in another service. The proposal uses a relational database for orders, Redis for order status caching, and asynchronous events to update inventory. Review the design for consistency risks, failure modes, and verification steps.
```

Create `/Users/Thin/Documents/ddia/evaluation/prompts/02-event-pipeline.md`:

```markdown
# Prompt 2: Event Pipeline

Use the DDIA system design skill to design a clickstream ingestion pipeline. The product needs near-real-time dashboards, replayable raw events, late event handling, and daily batch reports. Recommend an architecture and explain trade-offs, failure modes, and correctness checks.
```

Create `/Users/Thin/Documents/ddia/evaluation/prompts/03-database-choice.md`:

```markdown
# Prompt 3: Database Choice

Use the DDIA system design skill to compare relational, document, and graph databases for a team collaboration product with users, organizations, projects, tasks, comments, mentions, permissions, and audit history. Give a recommendation and explain which assumptions would change it.
```

Create `/Users/Thin/Documents/ddia/evaluation/prompts/04-replica-lag.md`:

```markdown
# Prompt 4: Replica Lag

Use the DDIA system design skill to diagnose this production issue:

After moving read traffic to replicas, users sometimes update profile settings and then immediately see old values. Support also reports non-monotonic behavior when users refresh quickly. Explain likely causes, design options, trade-offs, and observability checks.
```

Create `/Users/Thin/Documents/ddia/evaluation/prompts/05-derived-data.md`:

```markdown
# Prompt 5: Derived Data

Use the DDIA system design skill to review a search indexing design:

PostgreSQL is the source of truth. A background worker sends changes to Elasticsearch. Product wants search results to affect billing workflow decisions. Review the correctness risks and propose a safer architecture.
```

- [ ] **Step 5: Write the results template**

Create `/Users/Thin/Documents/ddia/evaluation/results-template.md`:

```markdown
# DDIA Skill Evaluation Results

Evaluator:
Date:
Skill version:

## Prompt 1: Order Consistency

- Workload framing:
- Trade-off quality:
- Failure-mode coverage:
- Correctness reasoning:
- Verification value:
- Pass:
- Notes:

## Prompt 2: Event Pipeline

- Workload framing:
- Trade-off quality:
- Failure-mode coverage:
- Correctness reasoning:
- Verification value:
- Pass:
- Notes:

## Prompt 3: Database Choice

- Workload framing:
- Trade-off quality:
- Failure-mode coverage:
- Correctness reasoning:
- Verification value:
- Pass:
- Notes:

## Prompt 4: Replica Lag

- Workload framing:
- Trade-off quality:
- Failure-mode coverage:
- Correctness reasoning:
- Verification value:
- Pass:
- Notes:

## Prompt 5: Derived Data

- Workload framing:
- Trade-off quality:
- Failure-mode coverage:
- Correctness reasoning:
- Verification value:
- Pass:
- Notes:

## Overall Decision

- All prompts passed:
- Skill changes needed:
```

- [ ] **Step 6: Write the quality checker**

Create `/Users/Thin/Documents/ddia/scripts/check_ddia_skill_quality.py`:

```python
#!/usr/bin/env python3
import argparse
import json
import pathlib
from typing import Any


REQUIRED_FILES = [
    "skills/ddia-system-design/SKILL.md",
    "skills/ddia-system-design/references/topic-map.md",
    "skills/ddia-system-design/references/system-design-principles.md",
    "skills/ddia-system-design/references/architecture-review-checklists.md",
    "skills/ddia-system-design/agents/openai.yaml",
    "evaluation/rubric.md",
    "evaluation/prompts/01-order-consistency.md",
    "evaluation/prompts/02-event-pipeline.md",
    "evaluation/prompts/03-database-choice.md",
    "evaluation/prompts/04-replica-lag.md",
    "evaluation/prompts/05-derived-data.md",
    "evaluation/results-template.md",
]

REQUIRED_TERMS = [
    "reliability",
    "scalability",
    "maintainability",
    "replication",
    "partitioning",
    "transactions",
    "isolation",
    "linearizability",
    "consensus",
    "batch processing",
    "stream processing",
    "derived data",
]


def read_existing_text(repo: pathlib.Path, relative_paths: list[str]) -> str:
    chunks = []
    for relative in relative_paths:
        path = repo / relative
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks).lower()


def check_repo(repo: pathlib.Path) -> dict[str, Any]:
    missing_files = [relative for relative in REQUIRED_FILES if not (repo / relative).exists()]
    skill_text = read_existing_text(
        repo,
        [
            "skills/ddia-system-design/SKILL.md",
            "skills/ddia-system-design/references/topic-map.md",
            "skills/ddia-system-design/references/system-design-principles.md",
            "skills/ddia-system-design/references/architecture-review-checklists.md",
        ],
    )
    missing_terms = [term for term in REQUIRED_TERMS if term not in skill_text]
    prompt_count = len(list((repo / "evaluation" / "prompts").glob("*.md"))) if (repo / "evaluation" / "prompts").exists() else 0
    return {
        "missing_files": missing_files,
        "missing_terms": missing_terms,
        "prompt_count": prompt_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check DDIA skill quality assets.")
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path("."))
    args = parser.parse_args()

    report = check_repo(args.repo.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["missing_files"] or report["missing_terms"] or report["prompt_count"] != 5:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 7: Run the quality tests to verify they pass**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_skill_quality -v
```

Expected: PASS for `test_quality_checker_accepts_complete_assets`.

- [ ] **Step 8: Run the quality checker**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_skill_quality.py --repo /Users/Thin/Documents/ddia
```

Expected output:

```json
{
  "missing_files": [],
  "missing_terms": [],
  "prompt_count": 5
}
```

- [ ] **Step 9: Commit the task**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add evaluation scripts/check_ddia_skill_quality.py tests/test_ddia_skill_quality.py
git commit -m "test: add ddia skill usefulness evaluation"
```

---

### Task 7: Validate, Install, And Smoke Test The Skill

**Files:**
- Read: `/Users/Thin/Documents/ddia/skills/ddia-system-design`
- Create or update: `/Users/Thin/.codex/skills/ddia-system-design`
- Create from template: `/Users/Thin/Documents/ddia/evaluation/results.md`

- [ ] **Step 1: Run all deterministic tests**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Validate skill metadata**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  /Users/Thin/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/Thin/Documents/ddia/skills/ddia-system-design
```

Expected: validation succeeds with no errors.

- [ ] **Step 3: Check ledger coverage**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_ledger.py \
  --ledger analysis/ddia-reading-ledger.md
```

Expected: exit code 0 and empty `missing_chapters` plus empty `incomplete_chapters`.

- [ ] **Step 4: Check quality assets**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_skill_quality.py --repo /Users/Thin/Documents/ddia
```

Expected: exit code 0 and no missing files or terms.

- [ ] **Step 5: Install the skill**

Run:

```bash
mkdir -p /Users/Thin/.codex/skills/ddia-system-design
rsync -a --delete /Users/Thin/Documents/ddia/skills/ddia-system-design/ /Users/Thin/.codex/skills/ddia-system-design/
```

Expected: no output and exit code 0.

- [ ] **Step 6: Verify installed files**

Run:

```bash
test -f /Users/Thin/.codex/skills/ddia-system-design/SKILL.md
test -f /Users/Thin/.codex/skills/ddia-system-design/references/topic-map.md
test -f /Users/Thin/.codex/skills/ddia-system-design/references/system-design-principles.md
test -f /Users/Thin/.codex/skills/ddia-system-design/references/architecture-review-checklists.md
test -f /Users/Thin/.codex/skills/ddia-system-design/agents/openai.yaml
```

Expected: no output and exit code 0.

- [ ] **Step 7: Run manual usefulness evaluation**

Create `/Users/Thin/Documents/ddia/evaluation/results.md` by copying `/Users/Thin/Documents/ddia/evaluation/results-template.md`.

For each prompt under `/Users/Thin/Documents/ddia/evaluation/prompts/`, start a fresh Codex interaction and ask it to use `/Users/Thin/.codex/skills/ddia-system-design`. Score the response using `/Users/Thin/Documents/ddia/evaluation/rubric.md`.

Passing score:

```text
Each prompt score is at least 8 out of 10.
No rubric dimension is scored 0.
All five prompts pass.
```

- [ ] **Step 8: Improve the skill if evaluation fails**

If any prompt fails, update the specific reference file that lacked guidance:

```text
Database choice weakness -> references/topic-map.md or references/system-design-principles.md
Failure-mode weakness -> references/architecture-review-checklists.md
Correctness weakness -> references/system-design-principles.md
Verification weakness -> references/architecture-review-checklists.md
Trigger weakness -> SKILL.md frontmatter description
```

After edits, rerun:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  /Users/Thin/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/Thin/Documents/ddia/skills/ddia-system-design
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_skill_quality.py --repo /Users/Thin/Documents/ddia
rsync -a --delete /Users/Thin/Documents/ddia/skills/ddia-system-design/ /Users/Thin/.codex/skills/ddia-system-design/
```

Expected: all commands succeed before repeating manual evaluation.

- [ ] **Step 9: Commit final evaluation results**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add evaluation/results.md skills/ddia-system-design
git commit -m "test: record ddia skill evaluation results"
```

---

## Final Verification Checklist

Run these commands before declaring the skill complete:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  /Users/Thin/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/Thin/Documents/ddia/skills/ddia-system-design
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_ledger.py --ledger analysis/ddia-reading-ledger.md
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_skill_quality.py --repo /Users/Thin/Documents/ddia
```

Expected:

```text
All unit tests pass.
Skill validation succeeds.
Ledger coverage check exits 0.
Quality checker exits 0.
Manual evaluation passes all five prompts with rubric scores at or above the passing standard.
```
