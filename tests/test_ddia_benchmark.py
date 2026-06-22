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

This is pilot A/B evidence, not statistical proof. The current pilot has self-evaluation bias, response-shape/rubric alignment risk, a single model, a single run per arm, no variance estimate, non-random case selection, and no repeated runs. It also scores answer quality only; it does not score the process-compliance rubric.

A stronger study would use independent blinded scoring, repeated randomized runs, and more than one model.
""",
    )
    write(
        root / "evaluation/ab/control-instructions.md",
        """# Control Instructions

Answer the benchmark case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill.

Use your general backend architecture knowledge. Use whatever clear answer structure you normally would for a backend architecture review.
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

Score the substance of the answer, not the mere presence of headings. A response should earn points when it actually explains workload, trade-offs, failure modes, correctness, and verification.

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

| Case | Category | Control score | Treatment score | Lift | Control normalized | Treatment normalized | Normalized lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Dimension Differences

Record workload framing, trade-off quality, failure-mode coverage, correctness reasoning, verification value, and anti-pattern resistance differences.

## Response Archive

Preserve Response A and Response B for every case.

## Limitations

- Self-evaluation bias:
- Response-shape/rubric alignment:
- Single model:
- Single run:
- No variance estimate:
- Non-random case selection:
- Process-compliance rubric not scored:

## Overall Decision

- Total control score:
- Total treatment score:
- Total lift:
- Mean normalized control:
- Mean normalized treatment:
- Mean normalized lift:
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

| Case | Category | Control score | Treatment score | Lift | Control normalized | Treatment normalized | Normalized lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| order-consistency | good | 7/10 | 9/10 | +2 | 70.0% | 90.0% | +20.0 pp | fail to pass | Treatment added stronger verification and failure-mode reasoning. |
| replica-lag | good | 7/10 | 10/10 | +3 | 70.0% | 100.0% | +30.0 pp | fail to pass | Treatment named read-your-writes and monotonic reads. |
| cache-as-truth | bad | 8/12 | 11/12 | +3 | 66.7% | 91.7% | +25.0 pp | fail to pass | Treatment rejected Redis as source of truth. |
| exactly-once-trap | adversarial | 8/12 | 11/12 | +3 | 66.7% | 91.7% | +25.0 pp | fail to pass | Treatment challenged end-to-end exactly-once. |
| vague-startup-architecture | bad | 8/12 | 10/12 | +2 | 66.7% | 83.3% | +16.7 pp | diagnostic improvement | Treatment scoped the recommendation and named missing requirements. |

## Dimension Differences

Treatment improved correctness reasoning, verification value, and anti-pattern resistance across the pilot cases.

## Response Archive

Responses are preserved under each case section in this file.

## Limitations

- Self-evaluation bias: the same agent family generated and scored the pilot, so scores may favor the skill-enabled response style.
- Response-shape/rubric alignment: treatment instructions ask for sections that map closely to the answer-quality rubric.
- Single model: the pilot only covers GPT-5 Codex.
- Single run: each case has one control response and one treatment response.
- No variance estimate: the pilot does not report repeated-run mean, minimum, maximum, or range.
- Non-random case selection: the five cases were selected for coverage, not sampled randomly.
- Process-compliance rubric not scored: this pilot scores answer quality only.

## Overall Decision

- Total control score: 38
- Total treatment score: 51
- Total lift: +13
- Mean normalized control: 68.0%
- Mean normalized treatment: 91.3%
- Mean normalized lift: +23.3 pp
- Limitations: In one five-case paired pilot run, treatment scored higher than control and four must-pass cases crossed the pass threshold. This is directional pilot evidence, not statistical proof.
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

    def test_checker_rejects_pilot_score_total_drift(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace(
                    "- Total treatment score: 51",
                    "- Total treatment score: 50",
                ),
                encoding="utf-8",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: total treatment score 50 does not equal case sum 51",
            ab_errors,
        )

    def test_checker_rejects_pilot_missing_score_row_for_required_case(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_text = pilot_path.read_text(encoding="utf-8")
            pilot_text = pilot_text.replace(
                "| cache-as-truth | bad | 8/12 | 11/12 | +3 | 66.7% | 91.7% | +25.0 pp | fail to pass | Treatment rejected Redis as source of truth. |\n",
                "",
            )
            pilot_text = pilot_text.replace("- Total control score: 38", "- Total control score: 30")
            pilot_text = pilot_text.replace("- Total treatment score: 51", "- Total treatment score: 40")
            pilot_text = pilot_text.replace("- Total lift: +13", "- Total lift: +10")
            pilot_text = pilot_text.replace("- Mean normalized control: 68.0%", "- Mean normalized control: 68.4%")
            pilot_text = pilot_text.replace("- Mean normalized treatment: 91.3%", "- Mean normalized treatment: 91.3%")
            pilot_text = pilot_text.replace("- Mean normalized lift: +23.3 pp", "- Mean normalized lift: +22.9 pp")
            pilot_path.write_text(pilot_text, encoding="utf-8")

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: missing score row for cache-as-truth",
            ab_errors,
        )

    def test_checker_rejects_pilot_score_zero_denominator(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace("7/10", "7/0", 1),
                encoding="utf-8",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: order-consistency score denominator must be greater than 0",
            ab_errors,
        )

    def test_checker_rejects_pilot_normalized_score_drift(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace("70.0%", "71.0%", 1),
                encoding="utf-8",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: order-consistency control normalized 71.0% does not match 70.0%",
            ab_errors,
        )

    def test_checker_rejects_pilot_missing_normalized_scores(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace("Control normalized", "Control percent"),
                encoding="utf-8",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: missing score column Control normalized",
            ab_errors,
        )

    def test_checker_rejects_pilot_missing_required_limitation(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace(
                    "- No variance estimate: the pilot does not report repeated-run mean, minimum, maximum, or range.\n",
                    "",
                ),
                encoding="utf-8",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: missing limitation No variance estimate",
            ab_errors,
        )

    def test_checker_rejects_control_instructions_that_ban_structured_answers(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            write(
                repo / "evaluation/ab/control-instructions.md",
                """# Control Instructions

Answer the benchmark case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill.

Do not use the DDIA skill workflow, DDIA reference files, or DDIA skill response shape.
""",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/control-instructions.md: must allow ordinary structured architecture reasoning",
            ab_errors,
        )


if __name__ == "__main__":
    unittest.main()
