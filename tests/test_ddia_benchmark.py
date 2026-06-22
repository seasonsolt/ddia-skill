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


def coding_case_text(*, case_id: str, category: str) -> str:
    return f"""# Coding Case: {case_id}

Case ID: {case_id}
Category: {category}
Language: Java
Primary DDIA topics: transactions, replication, fault tolerance

## Scenario

A Java service handles a user-facing write path where an apparently simple implementation hides a data-systems correctness problem.

## Flawed Java

```java
class ExampleService {{
    void handle(String id) {{
        System.out.println("processed " + id);
    }}
}}
```

## Task

Review the code and propose a patch that improves correctness without pretending that a library call can remove distributed-systems trade-offs.

## Expected DDIA Reasoning

The answer should discuss the source of truth, atomicity boundaries, failure modes, retries, idempotency, and observable verification.

## Strong Patch Signals

- Names the durable source of truth and preserves invariants across failures.
- Adds concrete retry, idempotency, or reconciliation behavior with tests.

## Weak Patch Patterns

- Treats a cache, lock, or callback as proof that the data is correct.
- Ignores crash windows, duplicate requests, or replica lag.

## Scoring Notes

- Award credit for explicit failure-mode reasoning before tool choices.
- Penalize patches that move the race without defining a correctness boundary.
"""


def make_complete_coding_ab_assets(root: pathlib.Path) -> None:
    write(
        root / "evaluation/coding-ab/README.md",
        """# DDIA Coding A/B Evaluation

## Purpose

Compare Java coding review answers from a control prompt against answers that use ddia-system-design reasoning.

## Method

Run each coding case twice with hidden control and treatment labels, then score the patch quality before revealing the mapping.

## Case Set

- evaluation/coding-ab/cases/checkout-cache-as-truth.md
- evaluation/coding-ab/cases/payment-exactly-once-trap.md
- evaluation/coding-ab/cases/order-outbox-missing.md
- evaluation/coding-ab/cases/profile-replica-lag.md
- evaluation/coding-ab/cases/redis-distributed-lock-money-transfer.md

## Limitations

This benchmark checks coding-review behavior, not statistical significance.
""",
    )
    write(
        root / "evaluation/coding-ab/control-instructions.md",
        """# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill.
""",
    )
    write(
        root / "evaluation/coding-ab/treatment-instructions.md",
        """# Coding Treatment Instructions

Use ddia-system-design for the Java coding case.

Frame the patch around assumptions, source of truth, consistency, failure modes, transactions, idempotency, operations, and tests.
""",
    )
    write(
        root / "evaluation/coding-ab/blind-llm-judge.md",
        """# Blind LLM Judge

## Scoring Order

Score Response A and Response B before revealing which response is control or treatment.

## Dimensions

1. Correctness invariant
2. Source-of-truth boundary
3. Failure-mode handling
4. Idempotency and retry safety
5. Operational verification
6. Java patch quality
7. Anti-pattern resistance

Base dimensions receive 0, 1, or 2 points.
For bad coding cases, anti-pattern resistance is null and the total is out of 12.
For adversarial coding cases, anti-pattern resistance receives 0, 1, or 2 points and the total is out of 14.

Bad coding cases pass at 10 out of 12 with every base dimension above 0.
Adversarial coding cases pass at 12 out of 14 with every dimension above 0 and 2 points in anti-pattern resistance.

## Mapping Reveal

Reveal the mapping only after all dimensions, notes, and pass decisions are recorded.
""",
    )
    write(
        root / "evaluation/coding-ab/results-template.md",
        """# DDIA Coding A/B Results Template

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
| checkout-cache-as-truth | bad |  |  |  |  |  |
| payment-exactly-once-trap | adversarial |  |  |  |  |  |
| order-outbox-missing | bad |  |  |  |  |  |
| profile-replica-lag | bad |  |  |  |  |  |
| redis-distributed-lock-money-transfer | adversarial |  |  |  |  |  |

## Dimension Differences

Record correctness invariant, source-of-truth boundary, failure-mode handling, idempotency and retry safety, operational verification, Java patch quality, and anti-pattern resistance. Scores use the blind judge rubric where base dimensions receive 0, 1, or 2 points.

## Response Archive

Preserve Response A and Response B for every coding case.

## Overall Decision

- Total control score:
- Total treatment score:
- Total lift:
- Limitations:
""",
    )
    cases = {
        "checkout-cache-as-truth": "bad",
        "payment-exactly-once-trap": "adversarial",
        "order-outbox-missing": "bad",
        "profile-replica-lag": "bad",
        "redis-distributed-lock-money-transfer": "adversarial",
    }
    for case_id, category in cases.items():
        write(
            root / f"evaluation/coding-ab/cases/{case_id}.md",
            coding_case_text(case_id=case_id, category=category),
        )


def valid_judge_payload(case_id: str = "checkout-cache-as-truth") -> dict:
    scores = {
        "correctness_invariant": 2,
        "source_of_truth_boundary": 2,
        "failure_mode_handling": 2,
        "idempotency_retry_safety": 2,
        "operational_verification": 1,
        "java_patch_quality": 2,
    }
    if case_id in {"payment-exactly-once-trap", "redis-distributed-lock-money-transfer"}:
        scores["anti_pattern_resistance"] = 2
    else:
        scores["anti_pattern_resistance"] = None
    total = sum(score for score in scores.values() if score is not None)

    def response_result() -> dict:
        return {
            "scores": scores.copy(),
            "total": total,
            "pass": True,
            "rationale": "This response preserves durable invariants and handles realistic failure modes.",
        }

    return {
        "case_id": case_id,
        "response_a": response_result(),
        "response_b": response_result(),
    }


class DdiaBenchmarkTest(unittest.TestCase):
    def test_readme_mentions_coding_ab_benchmark(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        guide = (REPO / "evaluation/benchmark-guide.md").read_text(encoding="utf-8")

        self.assertIn("Coding A/B Benchmark", readme)
        self.assertIn("evaluation/coding-ab", readme)
        self.assertIn("coding A/B", guide)
        self.assertIn("Java patch", guide)

    def test_coding_ab_judge_dimensions_match_payload_schema(self):
        checker = load_checker()

        self.assertEqual(
            checker.CODING_AB_JUDGE_DIMENSIONS,
            [
                "Correctness invariant",
                "Source-of-truth boundary",
                "Failure-mode handling",
                "Idempotency and retry safety",
                "Operational verification",
                "Java patch quality",
                "Anti-pattern resistance",
            ],
        )

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
        self.assertEqual(report["coding_ab_missing_paths"], [])
        self.assertEqual(report["coding_ab_errors"], [])

    def test_current_repo_coding_ab_assets_are_complete(self):
        checker = load_checker()

        missing_paths, coding_ab_errors = checker.validate_coding_ab_assets(REPO)

        self.assertEqual(missing_paths, [])
        self.assertEqual(coding_ab_errors, [])

    def test_checker_accepts_complete_benchmark(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            make_complete_coding_ab_assets(repo)

            report = checker.check_benchmark(repo)

        self.assertEqual(report["case_counts"], {"good": 5, "bad": 4, "adversarial": 4})
        self.assertEqual(report["missing_paths"], [])
        self.assertEqual(report["case_errors"], [])
        self.assertEqual(report["rubric_errors"], [])
        self.assertEqual(report["template_errors"], [])
        self.assertEqual(report["guide_errors"], [])
        self.assertEqual(report["ab_errors"], [])
        self.assertEqual(report["coding_ab_missing_paths"], [])
        self.assertEqual(report["coding_ab_errors"], [])

    def test_benchmark_checker_reports_missing_ab_file(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            make_complete_coding_ab_assets(repo)
            (repo / "evaluation/ab/pilot-results.md").unlink()

            report = checker.check_benchmark(repo)

        self.assertIn("evaluation/ab/pilot-results.md", report["missing_paths"])

    def test_checker_rejects_missing_required_case_section(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            make_complete_coding_ab_assets(repo)
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
            make_complete_ab_assets(repo)
            make_complete_coding_ab_assets(repo)
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
            make_complete_ab_assets(repo)
            make_complete_coding_ab_assets(repo)
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
            make_complete_ab_assets(repo)
            make_complete_coding_ab_assets(repo)
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

    def test_checker_accepts_complete_coding_ab_assets(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_coding_ab_assets(repo)

            missing_paths, coding_ab_errors = checker.validate_coding_ab_assets(repo)

        self.assertEqual(coding_ab_errors, [])
        self.assertEqual(missing_paths, [])

    def test_checker_rejects_coding_case_without_java_block(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_coding_ab_assets(repo)
            case_path = repo / "evaluation/coding-ab/cases/checkout-cache-as-truth.md"
            case_path.write_text(
                case_path.read_text(encoding="utf-8").replace("```java", "```"),
                encoding="utf-8",
            )

            missing_paths, coding_ab_errors = checker.validate_coding_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/coding-ab/cases/checkout-cache-as-truth.md: section Flawed Java must include a java code block",
            coding_ab_errors,
        )

    def test_checker_rejects_coding_case_with_empty_java_block(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_coding_ab_assets(repo)
            case_path = repo / "evaluation/coding-ab/cases/checkout-cache-as-truth.md"
            case_path.write_text(
                case_path.read_text(encoding="utf-8").replace(
                    """```java
class ExampleService {
    void handle(String id) {
        System.out.println("processed " + id);
    }
}
```""",
                    """```java
```""",
                ),
                encoding="utf-8",
            )

            missing_paths, coding_ab_errors = checker.validate_coding_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/coding-ab/cases/checkout-cache-as-truth.md: section Flawed Java must include non-empty java code",
            coding_ab_errors,
        )

    def test_checker_rejects_results_template_missing_coding_case(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_coding_ab_assets(repo)
            template_path = repo / "evaluation/coding-ab/results-template.md"
            template_path.write_text(
                template_path.read_text(encoding="utf-8").replace(
                    "| profile-replica-lag | bad |  |  |  |  |  |\n",
                    "",
                ),
                encoding="utf-8",
            )

            missing_paths, coding_ab_errors = checker.validate_coding_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/coding-ab/results-template.md: missing case profile-replica-lag",
            coding_ab_errors,
        )

    def test_checker_rejects_results_template_case_only_in_prose(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_coding_ab_assets(repo)
            template_path = repo / "evaluation/coding-ab/results-template.md"
            template_text = template_path.read_text(encoding="utf-8")
            template_path.write_text(
                template_text.replace(
                    "| profile-replica-lag | bad |  |  |  |  |  |\n",
                    "",
                )
                + "\n<!-- profile-replica-lag is intentionally mentioned outside the table. -->\n",
                encoding="utf-8",
            )

            missing_paths, coding_ab_errors = checker.validate_coding_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/coding-ab/results-template.md: missing case profile-replica-lag",
            coding_ab_errors,
        )

    def test_checker_rejects_judge_without_score_scale(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_coding_ab_assets(repo)
            judge_path = repo / "evaluation/coding-ab/blind-llm-judge.md"
            judge_path.write_text(
                judge_path.read_text(encoding="utf-8")
                .replace("Base dimensions receive 0, 1, or 2 points.\n", "")
                .replace(
                    "For adversarial coding cases, anti-pattern resistance receives 0, 1, or 2 points "
                    "and the total is out of 14.\n",
                    "For adversarial coding cases, anti-pattern resistance contributes to the total out of 14.\n",
                ),
                encoding="utf-8",
            )

            missing_paths, coding_ab_errors = checker.validate_coding_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/coding-ab/blind-llm-judge.md: missing phrase 0, 1, or 2 points",
            coding_ab_errors,
        )

    def test_checker_accepts_valid_coding_ab_judge_payload(self):
        checker = load_checker()

        errors = checker.validate_coding_ab_judge_result_payload(valid_judge_payload())

        self.assertEqual(errors, [])

    def test_checker_rejects_coding_ab_judge_total_mismatch(self):
        checker = load_checker()
        payload = valid_judge_payload()
        payload["response_a"]["total"] = 10

        errors = checker.validate_coding_ab_judge_result_payload(payload)

        self.assertIn("response_a: total 10 does not match score sum 11", errors)

    def test_checker_rejects_coding_ab_judge_score_out_of_bounds(self):
        checker = load_checker()
        payload = valid_judge_payload()
        payload["response_b"]["scores"]["java_patch_quality"] = 3

        errors = checker.validate_coding_ab_judge_result_payload(payload)

        self.assertIn("response_b: java_patch_quality must be 0, 1, or 2", errors)

    def test_checker_rejects_coding_ab_judge_mapping_leak(self):
        checker = load_checker()
        payload = valid_judge_payload()
        payload["response_a"]["mapping"] = "control"
        payload["response_b"]["variant"] = "treatment"

        errors = checker.validate_coding_ab_judge_result_payload(payload)

        self.assertIn("response_a: must not reveal control or treatment mapping", errors)
        self.assertIn("response_b: must not reveal control or treatment mapping", errors)

    def test_checker_accepts_valid_bad_coding_ab_judge_payload(self):
        checker = load_checker()

        errors = checker.validate_coding_ab_judge_result_payload(valid_judge_payload("checkout-cache-as-truth"))

        self.assertEqual(errors, [])

    def test_checker_accepts_valid_adversarial_coding_ab_judge_payload(self):
        checker = load_checker()

        errors = checker.validate_coding_ab_judge_result_payload(
            valid_judge_payload("payment-exactly-once-trap")
        )

        self.assertEqual(errors, [])

    def test_checker_rejects_coding_ab_judge_false_pass(self):
        checker = load_checker()
        payload = valid_judge_payload()
        for score_key in [
            "correctness_invariant",
            "source_of_truth_boundary",
            "failure_mode_handling",
            "idempotency_retry_safety",
            "operational_verification",
            "java_patch_quality",
        ]:
            payload["response_a"]["scores"][score_key] = 0
        payload["response_a"]["total"] = 0
        payload["response_a"]["pass"] = True

        errors = checker.validate_coding_ab_judge_result_payload(payload)

        self.assertIn("response_a: pass True does not match computed pass False", errors)

    def test_checker_rejects_bad_coding_ab_judge_numeric_anti_pattern_score(self):
        checker = load_checker()
        payload = valid_judge_payload("checkout-cache-as-truth")
        payload["response_a"]["scores"]["anti_pattern_resistance"] = 2

        errors = checker.validate_coding_ab_judge_result_payload(payload)

        self.assertIn(
            "response_a: anti_pattern_resistance must be null for non-adversarial coding cases",
            errors,
        )

    def test_checker_rejects_adversarial_coding_ab_judge_null_anti_pattern_score(self):
        checker = load_checker()
        payload = valid_judge_payload("payment-exactly-once-trap")
        payload["response_a"]["scores"]["anti_pattern_resistance"] = None
        payload["response_a"]["total"] = 12
        payload["response_a"]["pass"] = False

        errors = checker.validate_coding_ab_judge_result_payload(payload)

        self.assertIn(
            "response_a: anti_pattern_resistance must be 0, 1, or 2 for adversarial coding cases",
            errors,
        )

    def test_checker_rejects_coding_ab_judge_unknown_case_id(self):
        checker = load_checker()
        payload = valid_judge_payload()
        payload["case_id"] = "unknown-case"

        errors = checker.validate_coding_ab_judge_result_payload(payload)

        self.assertIn("case_id: unknown coding A/B case unknown-case", errors)

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
