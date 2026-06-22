# DDIA Skill Benchmark Guide

## Purpose

Use this benchmark to verify whether the `ddia-system-design` skill improves backend architecture reasoning. Good cases prove usefulness. Bad and adversarial cases expose weak behavior and become regression tests for future skill iterations.

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

## How To Score

Good cases use five answer-quality dimensions for a maximum score of 10. A good case passes at 8 or higher with no zero dimensions.

Bad and adversarial cases use the same five dimensions plus Anti-pattern resistance for a maximum score of 12. A bad or adversarial case passes at 10 or higher only if Anti-pattern resistance is 2 and no dimension is 0.

Process compliance is scored separately. It should not rescue a weak final answer, but it helps diagnose whether the skill workflow itself needs improvement.

## Regression Review

For each new run, compare totals, per-dimension scores, and failure notes against the previous run. If an old must-pass case fails, treat it as a benchmark regression until the skill, prompt, or rubric is corrected.

When a new bad or adversarial case reveals a real weakness, keep that case in the benchmark permanently unless it is redundant with another case.
