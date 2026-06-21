import importlib.util
import pathlib
import textwrap
import unittest


REPO = pathlib.Path(__file__).resolve().parents[1]


def load_script(name: str):
    module_path = REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def complete_chapter(reviewed: str = "yes") -> str:
    return textwrap.dedent(
        f"""
        ## Chapter 1. Example

        Reviewed: {reviewed}

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
        ledger = (
            textwrap.dedent(
                """
            # DDIA Reading Ledger

            """
            )
            + complete_chapter()
        )
        report = checker.check_ledger_text(ledger, required_chapters=1)
        self.assertEqual(report["missing_chapters"], [])
        self.assertEqual(report["incomplete_chapters"], [])

    def test_checker_reports_missing_required_chapter(self):
        checker = load_script("check_ddia_ledger")
        report = checker.check_ledger_text(complete_chapter(), required_chapters=2)
        self.assertEqual(report["missing_chapters"], ["Chapter 2."])

    def test_checker_rejects_reviewed_no(self):
        checker = load_script("check_ddia_ledger")
        report = checker.check_ledger_text(complete_chapter(reviewed="no"), required_chapters=1)
        self.assertEqual(report["incomplete_chapters"], ["Chapter 1. Example"])

    def test_checker_rejects_missing_field(self):
        checker = load_script("check_ddia_ledger")
        ledger = complete_chapter().replace("### Failure modes", "### Missing field", 1)
        report = checker.check_ledger_text(ledger, required_chapters=1)
        self.assertEqual(report["incomplete_chapters"], ["Chapter 1. Example"])

    def test_checker_rejects_too_few_bullets(self):
        checker = load_script("check_ddia_ledger")
        ledger = complete_chapter().replace("- Separate correctness needs from convenience preferences.\n", "", 1)
        report = checker.check_ledger_text(ledger, required_chapters=1)
        self.assertEqual(report["incomplete_chapters"], ["Chapter 1. Example"])

    def test_checker_does_not_count_reviewed_yes_inside_bullet(self):
        checker = load_script("check_ddia_ledger")
        ledger = complete_chapter(reviewed="no").replace(
            "- Pick storage based on query shape.",
            "- Reviewed: yes appears here, but the chapter is not reviewed.",
            1,
        )
        report = checker.check_ledger_text(ledger, required_chapters=1)
        self.assertEqual(report["incomplete_chapters"], ["Chapter 1. Example"])


if __name__ == "__main__":
    unittest.main()
