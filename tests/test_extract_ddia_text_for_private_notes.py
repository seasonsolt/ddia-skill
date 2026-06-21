import importlib.util
import json
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

    def test_extract_private_text_writes_pages_and_index(self):
        module = load_module()

        class FakePage:
            def __init__(self, text):
                self.text = text

            def extract_text(self):
                return self.text

        class FakeReader:
            def __init__(self, _pdf_path):
                self.pages = [
                    FakePage("alpha\nbeta"),
                    FakePage("gamma"),
                    FakePage(None),
                ]

        original_reader = module.PdfReader
        module.PdfReader = FakeReader
        try:
            with tempfile.TemporaryDirectory() as tmp:
                output_dir = pathlib.Path(tmp) / "extract"
                pdf_path = pathlib.Path("/private/source.pdf")
                data = module.extract_private_text(
                    pdf_path,
                    output_dir,
                    enforce_private_output=False,
                )

                pages_dir = output_dir / "pages"
                self.assertTrue(pages_dir.is_dir())
                self.assertEqual((pages_dir / "page-001.txt").read_text(encoding="utf-8"), "alpha\nbeta\n")
                self.assertEqual((pages_dir / "page-002.txt").read_text(encoding="utf-8"), "gamma\n")
                self.assertEqual((pages_dir / "page-003.txt").read_text(encoding="utf-8"), "\n")

                index_data = json.loads((output_dir / "index.json").read_text(encoding="utf-8"))
                self.assertEqual(data, index_data)
                self.assertEqual(index_data["source_pdf"], str(pdf_path))
                self.assertEqual(index_data["page_count"], 3)
                self.assertEqual(index_data["copyright_note"], "Private local extraction for reading notes. Do not commit tmp/ddia-extract.")
                self.assertEqual(
                    index_data["pages"],
                    [
                        {
                            "page": 1,
                            "file": str(pages_dir / "page-001.txt"),
                            "character_count": 10,
                            "line_count": 2,
                        },
                        {
                            "page": 2,
                            "file": str(pages_dir / "page-002.txt"),
                            "character_count": 5,
                            "line_count": 1,
                        },
                        {
                            "page": 3,
                            "file": str(pages_dir / "page-003.txt"),
                            "character_count": 0,
                            "line_count": 0,
                        },
                    ],
                )
        finally:
            module.PdfReader = original_reader

    def test_private_output_guard_rejects_trackable_docs_path(self):
        module = load_module()
        with self.assertRaises(ValueError):
            module.ensure_private_output_dir(REPO / "docs" / "ddia-extract", REPO)


if __name__ == "__main__":
    unittest.main()
