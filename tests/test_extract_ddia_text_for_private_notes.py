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
