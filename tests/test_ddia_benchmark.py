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


AB_REQUIRED_FILES = [
    "evaluation/ab/README.md",
    "evaluation/ab/control-instructions.md",
    "evaluation/ab/treatment-instructions.md",
    "evaluation/ab/blind-scoring-guide.md",
    "evaluation/ab/results-template.md",
    "evaluation/ab/pilot-results.md",
]


def make_complete_ab_assets(root: pathlib.Path) -> None:
    write(
        root / "evaluation/ab/README.md",
        """# DDIA Skill A/B Evaluation

## Purpose

Compare control responses without ddia-system-design against treatment responses with ddia-system-design.

## Method

Run the same cases with the same model, score Response A and Response B, then reveal the mapping.

## Pilot Case Set

- evaluation/cases/good/01-order-consistency.md
- evaluation/cases/good/04-replica-lag.md
- evaluation/cases/bad/01-cache-as-truth.md
- evaluation/cases/adversarial/02-exactly-once-trap.md
- evaluation/cases/bad/04-vague-startup-architecture.md

## Limitations

This is pilot A/B evidence, not statistical proof.
""",
    )
    write(
        root / "evaluation/ab/control-instructions.md",
        """# Control Instructions

Answer the benchmark case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill.
""",
    )
    write(
        root / "evaluation/ab/treatment-instructions.md",
        """# Treatment Instructions

Use ddia-system-design for the benchmark case.

Follow the ddia-system-design response shape: assumptions, recommendation, trade-offs, failure modes, correctness, operations, and tests.
""",
    )
    write(
        root / "evaluation/ab/blind-scoring-guide.md",
        """# Blind Scoring Guide

## Scoring Order

Score Response A and Response B before revealing which response is control or treatment.

## Mapping Reveal

Reveal the mapping only after all dimensions, notes, and pass decisions are recorded.
""",
    )
    write(
        root / "evaluation/ab/results-template.md",
        """# DDIA Skill A/B Results Template

## Run Metadata

- Evaluator:
- Date:
- Model:
- Skill version:

## Hidden Mapping

- Response A:
- Response B:

## Case Scores

| Case | Category | Control score | Treatment score | Lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- |

## Dimension Differences

Record workload framing, trade-off quality, failure-mode coverage, correctness reasoning, verification value, and anti-pattern resistance differences.

## Response Archive

Preserve Response A and Response B for every case.

## Overall Decision

- Total control score:
- Total treatment score:
- Total lift:
- Limitations:
""",
    )
    write(
        root / "evaluation/ab/pilot-results.md",
        """# DDIA Skill Pilot A/B Results

## Run Metadata

- Evaluator: Codex
- Date: 2026-06-22
- Model: GPT-5 Codex
- Skill version: local pilot

## Pilot Case Coverage

- evaluation/cases/good/01-order-consistency.md
- evaluation/cases/good/04-replica-lag.md
- evaluation/cases/bad/01-cache-as-truth.md
- evaluation/cases/adversarial/02-exactly-once-trap.md
- evaluation/cases/bad/04-vague-startup-architecture.md

## Hidden Mapping

- Response A: control
- Response B: treatment

## Case Scores

| Case | Category | Control score | Treatment score | Lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| order-consistency | good | 7 | 9 | +2 | fail to pass | Treatment added stronger verification and failure-mode reasoning. |
| replica-lag | good | 7 | 10 | +3 | fail to pass | Treatment named read-your-writes and monotonic reads. |
| cache-as-truth | bad | 8 | 11 | +3 | fail to pass | Treatment rejected Redis as source of truth. |
| exactly-once-trap | adversarial | 8 | 11 | +3 | fail to pass | Treatment challenged end-to-end exactly-once. |
| vague-startup-architecture | bad | 8 | 10 | +2 | diagnostic improvement | Treatment scoped the recommendation and named missing requirements. |

## Dimension Differences

Treatment improved correctness reasoning, verification value, and anti-pattern resistance across the pilot cases.

## Response Archive

Responses are preserved under each case section in this file.

## Overall Decision

- Total control score: 38
- Total treatment score: 51
- Total lift: +13
- Limitations: This is a five-case pilot scored from preserved paired responses. It is not statistical proof.
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
        self.assertEqual(report["ab_errors"], [])

    def test_checker_accepts_complete_benchmark(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)

            report = checker.check_benchmark(repo)

        self.assertEqual(report["case_counts"], {"good": 5, "bad": 4, "adversarial": 4})
        self.assertEqual(report["missing_paths"], [])
        self.assertEqual(report["case_errors"], [])
        self.assertEqual(report["rubric_errors"], [])
        self.assertEqual(report["template_errors"], [])
        self.assertEqual(report["guide_errors"], [])
        self.assertEqual(report["ab_errors"], [])

    def test_benchmark_checker_reports_missing_ab_file(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            (repo / "evaluation/ab/pilot-results.md").unlink()

            report = checker.check_benchmark(repo)

        self.assertIn("evaluation/ab/pilot-results.md", report["missing_paths"])

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

    def test_checker_accepts_complete_ab_assets(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(ab_errors, [])
        self.assertEqual(missing_paths, [])

    def test_checker_reports_missing_ab_file(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            (repo / "evaluation/ab/pilot-results.md").unlink()

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(ab_errors, [])
        self.assertIn("evaluation/ab/pilot-results.md", missing_paths)

    def test_checker_rejects_control_instructions_that_allow_skill(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            write(
                repo / "evaluation/ab/control-instructions.md",
                "# Control Instructions\n\nUse ddia-system-design for the answer.\n",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/control-instructions.md: must forbid using ddia-system-design",
            ab_errors,
        )

    def test_checker_rejects_pilot_missing_selected_case(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace(
                    "- evaluation/cases/bad/01-cache-as-truth.md\n",
                    "",
                ),
                encoding="utf-8",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: missing pilot case evaluation/cases/bad/01-cache-as-truth.md",
            ab_errors,
        )


if __name__ == "__main__":
    unittest.main()
