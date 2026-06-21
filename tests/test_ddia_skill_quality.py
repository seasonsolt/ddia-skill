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
