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


def load_prompt_renderer():
    module_path = REPO / "scripts" / "render_coding_ab_prompt.py"
    spec = importlib.util.spec_from_file_location("render_coding_ab_prompt", module_path)
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


EXPANDED_CASES = {
    "evaluation/cases/good/06-quantitative-workload-capacity.md": case_text(
        title="Quantitative Workload Capacity",
        category="good",
        scoring_profile="good",
    ),
    "evaluation/cases/good/07-batch-backfill-reconciliation.md": case_text(
        title="Batch Backfill Reconciliation",
        category="good",
        scoring_profile="good",
    ),
    "evaluation/cases/good/08-schema-evolution-rollout.md": case_text(
        title="Schema Evolution Rollout",
        category="good",
        scoring_profile="good",
    ),
    "evaluation/cases/good/09-correct-cache-use.md": case_text(
        title="Correct Cache Use",
        category="good",
        scoring_profile="good",
    ),
    "evaluation/cases/good/10-observability-runbook.md": case_text(
        title="Observability Runbook",
        category="good",
        scoring_profile="good",
    ),
    "evaluation/cases/good/11-idempotency-outbox.md": case_text(
        title="Idempotency Outbox",
        category="good",
        scoring_profile="good",
    ),
    "evaluation/cases/bad/05-capacity-cost-handwave.md": case_text(
        title="Capacity Cost Handwave",
        category="bad",
        scoring_profile="anti-pattern",
    ),
    "evaluation/cases/adversarial/05-global-linearizable-writes.md": case_text(
        title="Global Linearizable Writes",
        category="adversarial",
        scoring_profile="anti-pattern",
    ),
}


COVERAGE_MATRIX = """The benchmark intentionally covers these DDIA-style backend design behaviors:

- Source-of-truth and derived-data boundaries: `good/01-order-consistency.md`, `bad/01-cache-as-truth.md`, `good/05-derived-data.md`
- Event pipeline correctness: `good/02-event-pipeline.md`, `good/11-idempotency-outbox.md`, `adversarial/02-exactly-once-trap.md`
- Storage and database choice: `good/03-database-choice.md`
- Schema evolution and compatibility: `good/08-schema-evolution-rollout.md`, `adversarial/04-schema-evolution-trap.md`
- Replication and consistency: `good/04-replica-lag.md`, `bad/02-replica-lag-denial.md`, `adversarial/05-global-linearizable-writes.md`
- Partitioning and hot spots: `bad/03-hot-partition.md`
- Transactions, coordination, and consensus: `adversarial/03-distributed-lock-trap.md`
- Quantitative workload and cost reasoning: `good/06-quantitative-workload-capacity.md`, `bad/05-capacity-cost-handwave.md`
- Batch/backfill and reconciliation: `good/07-batch-backfill-reconciliation.md`
- Correct cache use: `good/09-correct-cache-use.md`
- Observability and operations: `good/10-observability-runbook.md`
- Ambiguous requirements and requirement discovery: `bad/04-vague-startup-architecture.md`, `adversarial/01-tool-first-trap.md`"""


BASE_CASES = [
    (
        "evaluation/cases/good/01-order-consistency.md",
        "Order Consistency",
        "good",
        "good",
    ),
    (
        "evaluation/cases/good/02-event-pipeline.md",
        "Event Pipeline",
        "good",
        "good",
    ),
    (
        "evaluation/cases/good/03-database-choice.md",
        "Database Choice",
        "good",
        "good",
    ),
    (
        "evaluation/cases/good/04-replica-lag.md",
        "Replica Lag",
        "good",
        "good",
    ),
    (
        "evaluation/cases/good/05-derived-data.md",
        "Derived Data",
        "good",
        "good",
    ),
    (
        "evaluation/cases/bad/01-cache-as-truth.md",
        "Cache As Truth",
        "bad",
        "anti-pattern",
    ),
    (
        "evaluation/cases/bad/02-replica-lag-denial.md",
        "Replica Lag Denial",
        "bad",
        "anti-pattern",
    ),
    (
        "evaluation/cases/bad/03-hot-partition.md",
        "Hot Partition",
        "bad",
        "anti-pattern",
    ),
    (
        "evaluation/cases/bad/04-vague-startup-architecture.md",
        "Vague Startup Architecture",
        "bad",
        "anti-pattern",
    ),
    (
        "evaluation/cases/adversarial/01-tool-first-trap.md",
        "Tool First Trap",
        "adversarial",
        "anti-pattern",
    ),
    (
        "evaluation/cases/adversarial/02-exactly-once-trap.md",
        "Exactly Once Trap",
        "adversarial",
        "anti-pattern",
    ),
    (
        "evaluation/cases/adversarial/03-distributed-lock-trap.md",
        "Distributed Lock Trap",
        "adversarial",
        "anti-pattern",
    ),
    (
        "evaluation/cases/adversarial/04-schema-evolution-trap.md",
        "Schema Evolution Trap",
        "adversarial",
        "anti-pattern",
    ),
]


def make_complete_benchmark(root: pathlib.Path) -> None:
    for relative, title, category, scoring_profile in BASE_CASES:
        write(
            root / relative,
            case_text(title=title, category=category, scoring_profile=scoring_profile),
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
        f"""# DDIA Skill Benchmark Guide

## Purpose

Use this benchmark to provide evidence of usefulness and drive iteration.

## Coverage Matrix

{COVERAGE_MATRIX}

## How To Run

Run every case in evaluation/cases and score the response.

## How To Score

Use answer quality and process compliance separately.

## Regression Review

Compare the new results against the previous benchmark result.
""",
    )
    for relative, text in EXPANDED_CASES.items():
        write(root / relative, text)

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
    cases = EXPECTED_EXPANDED_CODING_AB_CASES
    case_list = "\n".join(f"- evaluation/coding-ab/cases/{case_id}.md" for case_id in cases)
    score_rows = "\n".join(
        f"| {case_id} | {category} |  |  |  |  |  |" for case_id, category in cases.items()
    )
    coverage_topics = {
        "good-cache-aside-product-preview": "Correct cache use, Source-of-truth boundary",
        "good-outbox-relay-idempotent-consumer": "Transactional outbox, Idempotent consumer",
        "good-replica-session-token-routing": "Read-your-writes, Replica lag",
        "good-expand-contract-schema-rollout": "Schema evolution",
        "checkout-cache-as-truth": "Correct cache use, Source-of-truth boundary",
        "order-outbox-missing": "Transactional outbox, External side effects",
        "profile-replica-lag": "Read-your-writes, Replica lag",
        "seat-booking-write-skew": "Isolation and write skew",
        "schema-migration-breaking-reader": "Schema evolution",
        "stream-consumer-non-idempotent": "Stream replay and duplicate delivery, Idempotent consumer",
        "hot-partition-tenant-counter": "Partitioning and hot keys",
        "retry-storm-no-dlq": "Backpressure and poison messages",
        "missing-reconciliation-observability": "Observability and reconciliation",
        "payment-exactly-once-trap": "External side effects, Idempotent consumer",
        "redis-distributed-lock-money-transfer": "Distributed locks and fencing",
        "multi-region-last-write-wins-profile": "Multi-region conflict resolution",
        "elasticsearch-authorization-trap": "Derived data authorization",
        "kafka-total-ordering-trap": "Ordering guarantees",
    }
    coverage_rows = "\n".join(
        f"| {case_id} | {cases[case_id]} | {coverage_topics[case_id]} |" for case_id in cases
    )
    coverage_case_refs = ", ".join(f"`{case_id}`" for case_id in cases)
    write(
        root / "evaluation/coding-ab/README.md",
        f"""# DDIA Coding A/B Evaluation

## Purpose

Compare Java coding review answers from a control prompt against answers that use ddia-system-design reasoning.

## Method

Run each coding case twice with hidden control and treatment labels, then score the patch quality before revealing the mapping.

## Case Set

{case_list}

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
        f"""# DDIA Coding A/B Results Template

## Run Metadata

- Evaluator:
- Date:
- Model:
- Skill version:

## Hidden Mapping

- Response A:
- Response B:

## Case Scores

Use the blind judge rubric: base dimensions are worth up to 12 points. Adversarial coding cases add anti-pattern resistance for a maximum score of 14. Pass criteria are governed by evaluation/coding-ab/blind-llm-judge.md.

| Case | Category | Control score | Treatment score | Lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- |
{score_rows}

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
    write(
        root / "evaluation/coding-ab/coverage-matrix.md",
        f"""# Coding A/B Coverage Matrix

## Coverage Matrix

| Case | Category | Topics |
| --- | --- | --- |
{coverage_rows}

Case refs: {coverage_case_refs}
""",
    )
    for case_id, category in cases.items():
        write(
            root / f"evaluation/coding-ab/cases/{case_id}.md",
            coding_case_text(case_id=case_id, category=category),
        )


EXPECTED_EXPANDED_CODING_AB_CASES = {
    "good-cache-aside-product-preview": "good",
    "good-outbox-relay-idempotent-consumer": "good",
    "good-replica-session-token-routing": "good",
    "good-expand-contract-schema-rollout": "good",
    "checkout-cache-as-truth": "bad",
    "order-outbox-missing": "bad",
    "profile-replica-lag": "bad",
    "seat-booking-write-skew": "bad",
    "schema-migration-breaking-reader": "bad",
    "stream-consumer-non-idempotent": "bad",
    "hot-partition-tenant-counter": "bad",
    "retry-storm-no-dlq": "bad",
    "missing-reconciliation-observability": "bad",
    "payment-exactly-once-trap": "adversarial",
    "redis-distributed-lock-money-transfer": "adversarial",
    "multi-region-last-write-wins-profile": "adversarial",
    "elasticsearch-authorization-trap": "adversarial",
    "kafka-total-ordering-trap": "adversarial",
}


EXPECTED_CODING_COVERAGE_TOPICS = {
    "Correct cache use",
    "Source-of-truth boundary",
    "Transactional outbox",
    "Idempotent consumer",
    "Read-your-writes",
    "Replica lag",
    "Isolation and write skew",
    "Schema evolution",
    "Stream replay and duplicate delivery",
    "Partitioning and hot keys",
    "Backpressure and poison messages",
    "Observability and reconciliation",
    "External side effects",
    "Distributed locks and fencing",
    "Multi-region conflict resolution",
    "Derived data authorization",
    "Ordering guarantees",
}


def valid_judge_payload(case_id: str = "checkout-cache-as-truth") -> dict:
    scores = {
        "correctness_invariant": 2,
        "source_of_truth_boundary": 2,
        "failure_mode_handling": 2,
        "idempotency_retry_safety": 2,
        "operational_verification": 1,
        "java_patch_quality": 2,
    }
    if EXPECTED_EXPANDED_CODING_AB_CASES.get(case_id) == "adversarial":
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

        self.assertEqual(report["case_counts"], {"good": 11, "bad": 5, "adversarial": 5})
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

    def test_coding_ab_case_registry_covers_expanded_suite(self):
        checker = load_checker()

        self.assertEqual(checker.CODING_AB_CASES, EXPECTED_EXPANDED_CODING_AB_CASES)
        self.assertEqual(checker.CODING_AB_EXPECTED_CATEGORY_COUNTS, {"good": 4, "bad": 9, "adversarial": 5})

    def test_coding_ab_coverage_matrix_covers_required_topics(self):
        checker = load_checker()
        matrix_path = REPO / "evaluation" / "coding-ab" / "coverage-matrix.md"
        matrix_text = matrix_path.read_text(encoding="utf-8")

        for case_id in EXPECTED_EXPANDED_CODING_AB_CASES:
            self.assertIn(f"| {case_id} |", matrix_text)

        for topic in EXPECTED_CODING_COVERAGE_TOPICS:
            self.assertIn(topic, matrix_text)

        missing_paths, coding_ab_errors = checker.validate_coding_ab_assets(REPO)
        self.assertEqual(missing_paths, [])
        self.assertEqual(coding_ab_errors, [])

    def test_coding_ab_results_template_has_every_case_row(self):
        template = (REPO / "evaluation" / "coding-ab" / "results-template.md").read_text(encoding="utf-8")

        for case_id in EXPECTED_EXPANDED_CODING_AB_CASES:
            self.assertIn(f"| {case_id} |", template)

    def test_coding_ab_prompt_renderer_strips_judge_only_sections(self):
        renderer = load_prompt_renderer()
        case_path = REPO / "evaluation" / "coding-ab" / "cases" / "checkout-cache-as-truth.md"

        prompt = renderer.render_prompt(
            repo=REPO,
            case_path=case_path,
            arm="control",
            skill_path=REPO / "skills" / "ddia-system-design" / "SKILL.md",
        )

        self.assertIn("## Scenario", prompt)
        self.assertIn("## Java Code", prompt)
        self.assertIn("## Task", prompt)
        self.assertIn("Coding Control Instructions", prompt)
        self.assertNotIn("# Coding Case", prompt)
        self.assertNotIn("Case ID:", prompt)
        self.assertNotIn("Primary DDIA topics", prompt)
        self.assertNotIn("## Flawed Java", prompt)
        self.assertNotIn("Expected DDIA Reasoning", prompt)
        self.assertNotIn("Strong Patch Signals", prompt)
        self.assertNotIn("Weak Patch Patterns", prompt)
        self.assertNotIn("Scoring Notes", prompt)

    def test_coding_ab_treatment_prompt_includes_skill_text_but_no_judge_key(self):
        renderer = load_prompt_renderer()
        case_path = REPO / "evaluation" / "coding-ab" / "cases" / "checkout-cache-as-truth.md"

        prompt = renderer.render_prompt(
            repo=REPO,
            case_path=case_path,
            arm="treatment",
            skill_path=REPO / "skills" / "ddia-system-design" / "SKILL.md",
        )

        self.assertIn("Coding Treatment Instructions", prompt)
        self.assertIn("# DDIA System Design", prompt)
        self.assertIn("## Scenario", prompt)
        self.assertIn("## Java Code", prompt)
        self.assertNotIn("# Coding Case", prompt)
        self.assertNotIn("Case ID:", prompt)
        self.assertNotIn("Primary DDIA topics", prompt)
        self.assertNotIn("## Flawed Java", prompt)
        self.assertNotIn("Expected DDIA Reasoning", prompt)
        self.assertNotIn("Strong Patch Signals", prompt)

    def test_checker_accepts_complete_benchmark(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            make_complete_coding_ab_assets(repo)

            report = checker.check_benchmark(repo)

        self.assertEqual(report["case_counts"], {"good": 11, "bad": 5, "adversarial": 5})
        self.assertEqual(report["missing_paths"], [])
        self.assertEqual(report["case_errors"], [])
        self.assertEqual(report["rubric_errors"], [])
        self.assertEqual(report["template_errors"], [])
        self.assertEqual(report["guide_errors"], [])
        self.assertEqual(report["ab_errors"], [])
        self.assertEqual(report["coding_ab_missing_paths"], [])
        self.assertEqual(report["coding_ab_errors"], [])

    def test_checker_rejects_missing_coverage_matrix(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            guide_path = repo / "evaluation/benchmark-guide.md"
            guide_path.write_text(
                guide_path.read_text(encoding="utf-8").replace(
                    f"## Coverage Matrix\n\n{COVERAGE_MATRIX}\n\n",
                    "",
                ),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/benchmark-guide.md: missing section Coverage Matrix",
            report["guide_errors"],
        )

    def test_checker_rejects_coverage_matrix_missing_case(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            guide_path = repo / "evaluation/benchmark-guide.md"
            guide_path.write_text(
                guide_path.read_text(encoding="utf-8").replace(
                    "`good/11-idempotency-outbox.md`",
                    "",
                ),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/benchmark-guide.md: coverage matrix missing case good/11-idempotency-outbox.md",
            report["guide_errors"],
        )

    def test_checker_rejects_coverage_matrix_unknown_case(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            guide_path = repo / "evaluation/benchmark-guide.md"
            guide_path.write_text(
                guide_path.read_text(encoding="utf-8").replace(
                    "`good/03-database-choice.md`",
                    "`good/03-database-choice.md`, `good/99-unknown.md`",
                ),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/benchmark-guide.md: coverage matrix unknown case good/99-unknown.md",
            report["guide_errors"],
        )

    def test_checker_rejects_coverage_matrix_duplicate_case(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            guide_path = repo / "evaluation/benchmark-guide.md"
            guide_path.write_text(
                guide_path.read_text(encoding="utf-8").replace(
                    "`good/03-database-choice.md`",
                    "`good/03-database-choice.md`, `good/03-database-choice.md`",
                ),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/benchmark-guide.md: coverage matrix duplicates case good/03-database-choice.md",
            report["guide_errors"],
        )

    def test_checker_rejects_coverage_matrix_wrong_topic(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            guide_path = repo / "evaluation/benchmark-guide.md"
            guide_text = guide_path.read_text(encoding="utf-8")
            guide_text = guide_text.replace(
                "- Partitioning and hot spots: `bad/03-hot-partition.md`",
                "- Partitioning and hot spots: `bad/03-hot-partition.md`, `adversarial/03-distributed-lock-trap.md`",
            )
            guide_text = guide_text.replace(
                "- Transactions, coordination, and consensus: `adversarial/03-distributed-lock-trap.md`",
                "- Transactions, coordination, and consensus:",
            )
            guide_path.write_text(guide_text, encoding="utf-8")

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/benchmark-guide.md: coverage matrix must list adversarial/03-distributed-lock-trap.md under Transactions, coordination, and consensus",
            report["guide_errors"],
        )

    def test_checker_reports_missing_required_expanded_case(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            missing_case = repo / "evaluation/cases/good/06-quantitative-workload-capacity.md"
            missing_case.unlink()

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/cases/good/06-quantitative-workload-capacity.md: missing required case",
            report["case_errors"],
        )

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
            case_path = repo / "evaluation/cases/bad/01-cache-as-truth.md"
            case_path.write_text(
                case_path.read_text(encoding="utf-8").replace("## Strong Answer Signals", "## Strong Signals"),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/cases/bad/01-cache-as-truth.md: missing section Strong Answer Signals",
            report["case_errors"],
        )

    def test_checker_rejects_wrong_case_category(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            case_path = repo / "evaluation/cases/adversarial/01-tool-first-trap.md"
            case_path.write_text(
                case_path.read_text(encoding="utf-8").replace("Category: adversarial", "Category: good"),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/cases/adversarial/01-tool-first-trap.md: expected Category: adversarial",
            report["case_errors"],
        )

    def test_checker_requires_anti_pattern_profile_for_bad_cases(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            case_path = repo / "evaluation/cases/bad/02-replica-lag-denial.md"
            case_path.write_text(
                case_path.read_text(encoding="utf-8").replace(
                    "Scoring profile: anti-pattern",
                    "Scoring profile: good",
                ),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/cases/bad/02-replica-lag-denial.md: expected Scoring profile: anti-pattern",
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

    def test_checker_rejects_duplicate_coding_coverage_row(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_coding_ab_assets(repo)
            matrix_path = repo / "evaluation/coding-ab/coverage-matrix.md"
            matrix_path.write_text(
                matrix_path.read_text(encoding="utf-8")
                + "| good-cache-aside-product-preview | good | Correct cache use |\n",
                encoding="utf-8",
            )

            missing_paths, coding_ab_errors = checker.validate_coding_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/coding-ab/coverage-matrix.md: duplicate coverage row for good-cache-aside-product-preview",
            coding_ab_errors,
        )

    def test_checker_rejects_wrong_coding_coverage_category(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_coding_ab_assets(repo)
            matrix_path = repo / "evaluation/coding-ab/coverage-matrix.md"
            matrix_path.write_text(
                matrix_path.read_text(encoding="utf-8").replace(
                    "| payment-exactly-once-trap | adversarial | External side effects, Idempotent consumer |",
                    "| payment-exactly-once-trap | good | External side effects, Idempotent consumer |",
                ),
                encoding="utf-8",
            )

            missing_paths, coding_ab_errors = checker.validate_coding_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/coding-ab/coverage-matrix.md: payment-exactly-once-trap expected category adversarial, found good",
            coding_ab_errors,
        )

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

    def test_checker_rejects_results_template_without_adversarial_max_14_wording(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_coding_ab_assets(repo)
            template_path = repo / "evaluation/coding-ab/results-template.md"
            template_path.write_text(
                template_path.read_text(encoding="utf-8").replace(
                    "Use the blind judge rubric: base dimensions are worth up to 12 points. "
                    "Adversarial coding cases add anti-pattern resistance for a maximum score of 14. "
                    "Pass criteria are governed by evaluation/coding-ab/blind-llm-judge.md.\n\n",
                    "",
                ),
                encoding="utf-8",
            )

            missing_paths, coding_ab_errors = checker.validate_coding_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/coding-ab/results-template.md: must explain adversarial coding cases have max 14",
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

    def test_checker_rejects_coding_ab_judge_top_level_mapping_leak(self):
        checker = load_checker()
        payload = valid_judge_payload()
        payload["mapping"] = {"response_a": "control", "response_b": "treatment"}

        errors = checker.validate_coding_ab_judge_result_payload(payload)

        self.assertIn("payload: must not reveal control or treatment mapping", errors)

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

    def test_checker_rejects_pilot_unexpected_score_row(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_text = pilot_path.read_text(encoding="utf-8")
            pilot_text = pilot_text.replace(
                "| vague-startup-architecture | bad | 8/12 | 10/12 | +2 | 66.7% | 83.3% | +16.7 pp | diagnostic improvement | Treatment scoped the recommendation and named missing requirements. |\n",
                "| vague-startup-architecture | bad | 8/12 | 10/12 | +2 | 66.7% | 83.3% | +16.7 pp | diagnostic improvement | Treatment scoped the recommendation and named missing requirements. |\n"
                "| invented-case | good | 1/10 | 2/10 | +1 | 10.0% | 20.0% | +10.0 pp | no change | Extra row. |\n",
            )
            pilot_text = pilot_text.replace("- Total control score: 38", "- Total control score: 39")
            pilot_text = pilot_text.replace("- Total treatment score: 51", "- Total treatment score: 53")
            pilot_text = pilot_text.replace("- Total lift: +13", "- Total lift: +14")
            pilot_text = pilot_text.replace("- Mean normalized control: 68.0%", "- Mean normalized control: 58.4%")
            pilot_text = pilot_text.replace("- Mean normalized treatment: 91.3%", "- Mean normalized treatment: 79.5%")
            pilot_text = pilot_text.replace("- Mean normalized lift: +23.3 pp", "- Mean normalized lift: +21.1 pp")
            pilot_path.write_text(pilot_text, encoding="utf-8")

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: unexpected score row for invented-case",
            ab_errors,
        )

    def test_checker_rejects_pilot_unparseable_score_row(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace("7/10", "7", 1),
                encoding="utf-8",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: unparseable score row for order-consistency",
            ab_errors,
        )

    def test_checker_rejects_pilot_truncated_score_row(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace(
                    "| order-consistency | good | 7/10 | 9/10 | +2 | 70.0% | 90.0% | +20.0 pp | fail to pass | Treatment added stronger verification and failure-mode reasoning. |",
                    "| order-consistency | good | 7/10 | 9/10 | +2 | 70.0% | 90.0% | +20.0 pp |",
                ),
                encoding="utf-8",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: malformed score row for order-consistency",
            ab_errors,
        )

    def test_checker_rejects_pilot_duplicate_score_row(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_text = pilot_path.read_text(encoding="utf-8")
            pilot_text = pilot_text.replace(
                "| order-consistency | good | 7/10 | 9/10 | +2 | 70.0% | 90.0% | +20.0 pp | fail to pass | Treatment added stronger verification and failure-mode reasoning. |",
                "| order-consistency | good | 7/10 | 9/10 | +2 | 70.0% | 90.0% | +20.0 pp | fail to pass | Treatment added stronger verification and failure-mode reasoning. |\n"
                "| order-consistency | good | 7/10 | 9/10 | +2 | 70.0% | 90.0% | +20.0 pp | fail to pass | Treatment added stronger verification and failure-mode reasoning. |\n",
            )
            pilot_text = pilot_text.replace("- Total control score: 38", "- Total control score: 45")
            pilot_text = pilot_text.replace("- Total treatment score: 51", "- Total treatment score: 60")
            pilot_text = pilot_text.replace("- Total lift: +13", "- Total lift: +15")
            pilot_text = pilot_text.replace("- Mean normalized control: 68.0%", "- Mean normalized control: 68.3%")
            pilot_text = pilot_text.replace("- Mean normalized treatment: 91.3%", "- Mean normalized treatment: 91.1%")
            pilot_text = pilot_text.replace("- Mean normalized lift: +23.3 pp", "- Mean normalized lift: +22.8 pp")
            pilot_path.write_text(pilot_text, encoding="utf-8")

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: duplicate score row for order-consistency",
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

    def test_checker_rejects_pilot_score_above_denominator(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_text = pilot_path.read_text(encoding="utf-8")
            pilot_text = pilot_text.replace(
                "| order-consistency | good | 7/10 | 9/10 | +2 | 70.0% | 90.0% | +20.0 pp | fail to pass | Treatment added stronger verification and failure-mode reasoning. |",
                "| order-consistency | good | 11/10 | 12/10 | +1 | 110.0% | 120.0% | +10.0 pp | fail to pass | Treatment added stronger verification and failure-mode reasoning. |",
            )
            pilot_text = pilot_text.replace("- Total control score: 38", "- Total control score: 42")
            pilot_text = pilot_text.replace("- Total treatment score: 51", "- Total treatment score: 54")
            pilot_text = pilot_text.replace("- Total lift: +13", "- Total lift: +12")
            pilot_text = pilot_text.replace("- Mean normalized control: 68.0%", "- Mean normalized control: 76.0%")
            pilot_text = pilot_text.replace("- Mean normalized treatment: 91.3%", "- Mean normalized treatment: 97.3%")
            pilot_text = pilot_text.replace("- Mean normalized lift: +23.3 pp", "- Mean normalized lift: +21.3 pp")
            pilot_path.write_text(pilot_text, encoding="utf-8")

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: order-consistency control score must be between 0 and 10",
            ab_errors,
        )
        self.assertIn(
            "evaluation/ab/pilot-results.md: order-consistency treatment score must be between 0 and 10",
            ab_errors,
        )

    def test_checker_rejects_pilot_score_denominator_mismatch(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_text = pilot_path.read_text(encoding="utf-8")
            pilot_text = pilot_text.replace(
                "| order-consistency | good | 7/10 | 9/10 | +2 | 70.0% | 90.0% | +20.0 pp | fail to pass | Treatment added stronger verification and failure-mode reasoning. |",
                "| order-consistency | good | 7/10 | 9/12 | +2 | 70.0% | 75.0% | +5.0 pp | fail to pass | Treatment added stronger verification and failure-mode reasoning. |",
            )
            pilot_text = pilot_text.replace("- Mean normalized treatment: 91.3%", "- Mean normalized treatment: 88.3%")
            pilot_text = pilot_text.replace("- Mean normalized lift: +23.3 pp", "- Mean normalized lift: +20.3 pp")
            pilot_path.write_text(pilot_text, encoding="utf-8")

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: order-consistency control and treatment denominators must match",
            ab_errors,
        )

    def test_checker_rejects_pilot_wrong_category_denominator(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_text = pilot_path.read_text(encoding="utf-8")
            pilot_text = pilot_text.replace(
                "| cache-as-truth | bad | 8/12 | 11/12 | +3 | 66.7% | 91.7% | +25.0 pp | fail to pass | Treatment rejected Redis as source of truth. |",
                "| cache-as-truth | bad | 8/10 | 11/10 | +3 | 80.0% | 110.0% | +30.0 pp | fail to pass | Treatment rejected Redis as source of truth. |",
            )
            pilot_text = pilot_text.replace("- Mean normalized control: 68.0%", "- Mean normalized control: 70.7%")
            pilot_text = pilot_text.replace("- Mean normalized treatment: 91.3%", "- Mean normalized treatment: 95.0%")
            pilot_text = pilot_text.replace("- Mean normalized lift: +23.3 pp", "- Mean normalized lift: +24.3 pp")
            pilot_path.write_text(pilot_text, encoding="utf-8")

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: cache-as-truth expected denominator 12 for category bad",
            ab_errors,
        )

    def test_checker_rejects_pilot_unknown_score_category(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace(
                    "| order-consistency | good | 7/10 | 9/10 |",
                    "| order-consistency | typo | 7/10 | 9/10 |",
                ),
                encoding="utf-8",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertTrue(
            any(
                error
                in {
                    "evaluation/ab/pilot-results.md: order-consistency unknown category typo",
                    "evaluation/ab/pilot-results.md: order-consistency expected category good, found typo",
                }
                for error in ab_errors
            ),
            ab_errors,
        )

    def test_checker_ignores_score_like_tables_outside_case_scores(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_text = pilot_path.read_text(encoding="utf-8")
            pilot_text = pilot_text.replace(
                "Responses are preserved under each case section in this file.",
                """Responses are preserved under each case section in this file.

| Case | Category | Control score | Treatment score | Lift | Control normalized | Treatment normalized | Normalized lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| archive-only | bad | 1/1 | 1/1 | +0 | 100.0% | 100.0% | +0.0 pp | unchanged | This archived table is not part of scoring. |""",
            )
            pilot_path.write_text(pilot_text, encoding="utf-8")

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertEqual(ab_errors, [])

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

    def test_benchmark_checker_reports_ab_content_error(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace(
                    "- Single model: the pilot only covers GPT-5 Codex.\n",
                    "",
                ),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/ab/pilot-results.md: missing limitation Single model",
            report["ab_errors"],
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
