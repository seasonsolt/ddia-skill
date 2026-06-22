import importlib.util
import pathlib
import tempfile
import unittest


REPO = pathlib.Path(__file__).resolve().parents[1]


def load_checker():
    module_path = REPO / "scripts" / "check_ddia_benchmark.py"
    spec = importlib.util.spec_from_file_location("check_ddia_benchmark", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def case_text(
    *,
    title: str,
    category: str,
    pass_mode: str = "must-pass",
    scoring_profile: str = "good",
) -> str:
    return f"""# Case: {title}

Category: {category}
Pass mode: {pass_mode}
Scoring profile: {scoring_profile}

## Prompt

Use the DDIA system design skill to review a backend architecture scenario with enough detail to evaluate workload framing, trade-offs, failure modes, correctness, and verification.

## Bad Premise Or Trap

No deliberate trap; this case checks normal DDIA-style system design reasoning.

## Weak Answer Patterns

- Recommends a tool before describing workload and correctness requirements.
- Skips concrete failure modes and verification steps.

## Strong Answer Signals

- Frames reads, writes, data volume, latency, and growth assumptions.
- Names trade-offs, failure modes, correctness implications, and validation checks.

## Scoring Notes

- Score answer quality with the rubric in evaluation/rubrics/answer-quality.md.
- Score process compliance only when the process is observable.
"""


def make_complete_benchmark(root: pathlib.Path) -> None:
    for index in range(1, 6):
        write(
            root / f"evaluation/cases/good/{index:02d}-good-case.md",
            case_text(title=f"Good Case {index}", category="good", scoring_profile="good"),
        )
    for index in range(1, 5):
        write(
            root / f"evaluation/cases/bad/{index:02d}-bad-case.md",
            case_text(title=f"Bad Case {index}", category="bad", scoring_profile="anti-pattern"),
        )
        write(
            root / f"evaluation/cases/adversarial/{index:02d}-adversarial-case.md",
            case_text(
                title=f"Adversarial Case {index}",
                category="adversarial",
                scoring_profile="anti-pattern",
            ),
        )

    write(
        root / "evaluation/rubrics/answer-quality.md",
        """# Answer Quality Rubric

## Dimensions

1. Workload framing
2. Trade-off quality
3. Failure-mode coverage
4. Correctness reasoning
5. Verification value
6. Anti-pattern resistance

## Passing Standards

- Good cases pass at 8 out of 10 with no zero dimensions.
- Bad and adversarial cases pass at 10 out of 12 with anti-pattern resistance scored 2.
""",
    )
    write(
        root / "evaluation/rubrics/process-compliance.md",
        """# Process Compliance Rubric

## Dimensions

1. Skill material usage
2. Assumption framing
3. Missing requirement questions
4. Response structure
5. Verification conversion
""",
    )
    write(
        root / "evaluation/results/template.md",
        """# DDIA Skill Benchmark Results

## Run Metadata

- Evaluator:
- Date:
- Skill version:

## Answer Quality

## Process Compliance

## Regression Notes

## Overall Decision
""",
    )
    write(
        root / "evaluation/benchmark-guide.md",
        """# DDIA Skill Benchmark Guide

## Purpose

Use this benchmark to prove usefulness and drive iteration.

## How To Run

Run every case in evaluation/cases and score the response.

## How To Score

Use answer quality and process compliance separately.

## Regression Review

Compare the new results against the previous benchmark result.
""",
    )


class DdiaBenchmarkTest(unittest.TestCase):
    def test_current_repo_benchmark_is_complete(self):
        checker = load_checker()

        report = checker.check_benchmark(REPO)

        self.assertEqual(report["case_counts"], {"good": 5, "bad": 4, "adversarial": 4})
        self.assertEqual(report["missing_paths"], [])
        self.assertEqual(report["case_errors"], [])
        self.assertEqual(report["rubric_errors"], [])
        self.assertEqual(report["template_errors"], [])
        self.assertEqual(report["guide_errors"], [])

    def test_checker_accepts_complete_benchmark(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)

            report = checker.check_benchmark(repo)

        self.assertEqual(report["case_counts"], {"good": 5, "bad": 4, "adversarial": 4})
        self.assertEqual(report["missing_paths"], [])
        self.assertEqual(report["case_errors"], [])
        self.assertEqual(report["rubric_errors"], [])
        self.assertEqual(report["template_errors"], [])
        self.assertEqual(report["guide_errors"], [])

    def test_checker_rejects_missing_required_case_section(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            case_path = repo / "evaluation/cases/bad/01-bad-case.md"
            case_path.write_text(
                case_path.read_text(encoding="utf-8").replace("## Strong Answer Signals", "## Strong Signals"),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/cases/bad/01-bad-case.md: missing section Strong Answer Signals",
            report["case_errors"],
        )

    def test_checker_rejects_wrong_case_category(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            case_path = repo / "evaluation/cases/adversarial/01-adversarial-case.md"
            case_path.write_text(
                case_path.read_text(encoding="utf-8").replace("Category: adversarial", "Category: good"),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/cases/adversarial/01-adversarial-case.md: expected Category: adversarial",
            report["case_errors"],
        )

    def test_checker_requires_anti_pattern_profile_for_bad_cases(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            case_path = repo / "evaluation/cases/bad/02-bad-case.md"
            case_path.write_text(
                case_path.read_text(encoding="utf-8").replace(
                    "Scoring profile: anti-pattern",
                    "Scoring profile: good",
                ),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/cases/bad/02-bad-case.md: expected Scoring profile: anti-pattern",
            report["case_errors"],
        )

    def test_checker_rejects_missing_answer_quality_dimension(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            rubric_path = repo / "evaluation/rubrics/answer-quality.md"
            rubric_path.write_text(
                rubric_path.read_text(encoding="utf-8").replace("6. Anti-pattern resistance\n", ""),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/rubrics/answer-quality.md: missing dimension Anti-pattern resistance",
            report["rubric_errors"],
        )


if __name__ == "__main__":
    unittest.main()
