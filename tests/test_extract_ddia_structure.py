import importlib.util
import json
import os
import pathlib
import tempfile
import unittest
from unittest import mock


REPO = pathlib.Path(__file__).resolve().parents[1]
PDF_PATH = pathlib.Path(
    os.environ.get(
        "DDIA_PDF_PATH",
        "/Users/Thin/Library/Mobile Documents/com~apple~CloudDocs/学习/分布式/designing-data-intensive-applications.pdf",
    )
)


def load_module(module_path: pathlib.Path | None = None):
    module_path = module_path or REPO / "scripts" / "extract_ddia_structure.py"
    spec = importlib.util.spec_from_file_location("extract_ddia_structure", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load extract_ddia_structure module from {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeDestination:
    def __init__(self, title):
        self.title = title


class FakeReader:
    def __init__(self, outline, pages_by_destination=None, failing_destination=None):
        self.outline = outline
        self.pages_by_destination = pages_by_destination or {}
        self.failing_destination = failing_destination

    def get_destination_page_number(self, item):
        if item is self.failing_destination:
            raise ValueError("destination is not attached to this reader")
        return self.pages_by_destination[item]


class ExtractDdiaStructureTest(unittest.TestCase):
    def test_normalize_metadata_strips_pdf_slashes_and_lowercases_first_key_letter(self):
        module = load_module()

        metadata = module.normalize_metadata(
            {
                "/Title": "Designing Data-Intensive Applications",
                "/Author": "Martin Kleppmann",
                "customKey": 42,
            }
        )

        self.assertEqual(
            metadata,
            {
                "title": "Designing Data-Intensive Applications",
                "author": "Martin Kleppmann",
                "customKey": "42",
            },
        )

    def test_normalize_metadata_returns_empty_dict_for_missing_metadata(self):
        module = load_module()

        self.assertEqual(module.normalize_metadata(None), {})

    def test_write_json_creates_parent_directory_and_preserves_unicode(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            output = pathlib.Path(tmp) / "nested" / "outline.json"
            module.write_json({"title": "分布式", "page_count": 1}, output)

            self.assertEqual(
                output.read_text(encoding="utf-8"),
                '{\n  "title": "分布式",\n  "page_count": 1\n}\n',
            )

    def test_flatten_outline_keeps_depth_title_and_one_based_pages(self):
        module = load_module()
        preface = FakeDestination("Preface")
        chapter = FakeDestination("Chapter 1. Reliable, Scalable, and Maintainable Applications")
        section = FakeDestination("Thinking About Data Systems")
        reader = FakeReader(
            [preface, [chapter, [section]]],
            {
                preface: 12,
                chapter: 30,
                section: 31,
            },
        )

        self.assertEqual(
            module.flatten_outline(reader),
            [
                {"depth": 0, "title": "Preface", "page": 13},
                {
                    "depth": 1,
                    "title": "Chapter 1. Reliable, Scalable, and Maintainable Applications",
                    "page": 31,
                },
                {"depth": 2, "title": "Thinking About Data Systems", "page": 32},
            ],
        )

    def test_flatten_outline_uses_none_when_destination_page_lookup_fails(self):
        module = load_module()
        missing_destination = FakeDestination("Missing page")
        reader = FakeReader([missing_destination], failing_destination=missing_destination)

        self.assertEqual(
            module.flatten_outline(reader),
            [{"depth": 0, "title": "Missing page", "page": None}],
        )

    def test_load_module_reports_unavailable_loader_clearly(self):
        with mock.patch("importlib.util.spec_from_file_location", return_value=None):
            with self.assertRaisesRegex(ImportError, "Unable to load extract_ddia_structure module"):
                load_module(pathlib.Path("missing.py"))

    def test_extracts_expected_ddia_outline_from_local_pdf(self):
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
