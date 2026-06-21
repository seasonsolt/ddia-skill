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
