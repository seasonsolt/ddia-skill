# DDIA Skill Benchmark Guide

## Purpose

Use this benchmark to verify whether the `ddia-system-design` skill improves backend architecture reasoning. Good cases provide evidence of usefulness. Bad and adversarial cases expose weak behavior and become regression tests for future skill iterations.

## Coverage Matrix

The benchmark intentionally covers these DDIA-style backend design behaviors:

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
- Ambiguous requirements and requirement discovery: `bad/04-vague-startup-architecture.md`, `adversarial/01-tool-first-trap.md`

## How To Run

1. Record the current skill version with `git rev-parse --short HEAD`.
2. Run every case in `evaluation/cases/good/`, `evaluation/cases/bad/`, and `evaluation/cases/adversarial/`.
3. Capture each model response.
4. Score answer quality with `evaluation/rubrics/answer-quality.md`.
5. Score process compliance with `evaluation/rubrics/process-compliance.md` when the process is observable.
6. Copy `evaluation/results/template.md` to `evaluation/results/YYYY-MM-DD-<commit>.md`.
7. Fill in every score, pass decision, regression note, and recommended skill change.
8. Compare the new result with the previous result file.

## How To Run Coding A/B

For coding A/B runs:

1. Render prompts with `scripts/render_coding_ab_prompt.py`.
2. Run control and treatment with the same model and settings.
3. Randomize Response A and Response B before judging.
4. Score with `evaluation/coding-ab/blind-llm-judge.md`.
5. Archive the generated responses, mapping, and judge JSON under `evaluation/coding-ab/runs/<date>-<case-id>/`.
6. Record scores in `evaluation/coding-ab/results-template.md` or a dated result file.

Generate answer prompts with the redacted renderer instead of sending raw case
files to the answer model:

```bash
PYTHON=python3
$PYTHON scripts/render_coding_ab_prompt.py --repo . --arm control --case evaluation/coding-ab/cases/checkout-cache-as-truth.md > /tmp/ddia-control-prompt.md
$PYTHON scripts/render_coding_ab_prompt.py --repo . --arm treatment --case evaluation/coding-ab/cases/checkout-cache-as-truth.md > /tmp/ddia-treatment-prompt.md
```

The coding A/B track does not require compiling Java. The judge scores whether
the Java patch moves correctness into the right source-of-truth, transaction,
idempotency, retry, and verification boundaries.

## How To Score

For prose benchmark cases under `evaluation/cases/`, good cases use five answer-quality dimensions for a maximum score of 10. A good case passes at 8 or higher with no zero dimensions.

For prose bad and adversarial cases, use the same five dimensions plus Anti-pattern resistance for a maximum score of 12. A bad or adversarial case passes at 10 or higher only if Anti-pattern resistance is 2 and no dimension is 0.

For coding A/B cases under `evaluation/coding-ab/cases/`, use `evaluation/coding-ab/blind-llm-judge.md`. Good and bad coding cases score six base dimensions for a maximum score of 12 with `anti_pattern_resistance: null`. Adversarial coding cases add anti-pattern resistance for a maximum score of 14.

Process compliance is scored separately. It should not rescue a weak final answer, but it helps diagnose whether the skill workflow itself needs improvement.

## Regression Review

For each new run, compare totals, per-dimension scores, and failure notes against the previous run. If an old must-pass case fails, treat it as a benchmark regression until the skill, prompt, or rubric is corrected.

When a new bad or adversarial case reveals a real weakness, keep that case in the benchmark permanently unless it is redundant with another case.
