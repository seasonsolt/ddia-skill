# DDIA Skill Benchmark Guide

## Purpose

Use this benchmark to verify whether the `ddia-system-design` skill improves backend architecture reasoning. Good cases provide evidence of usefulness. Bad and adversarial cases expose weak behavior and become regression tests for future skill iterations.

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

1. Pick a Java patch case from `evaluation/coding-ab/cases/`.
2. Generate a control patch with `evaluation/coding-ab/control-instructions.md`.
3. Generate a treatment patch with `evaluation/coding-ab/treatment-instructions.md`.
4. Randomize both patches as Response A and Response B.
5. Score both patches with `evaluation/coding-ab/blind-llm-judge.md`.
6. Preserve the raw patches and judge JSON in a copy of `evaluation/coding-ab/results-template.md`.

The coding A/B track does not require compiling Java. The judge scores whether
the patch moves correctness into the right source-of-truth, transaction,
idempotency, retry, and verification boundaries.

## How To Score

Good cases use five answer-quality dimensions for a maximum score of 10. A good case passes at 8 or higher with no zero dimensions.

Bad and adversarial cases use the same five dimensions plus Anti-pattern resistance for a maximum score of 12. A bad or adversarial case passes at 10 or higher only if Anti-pattern resistance is 2 and no dimension is 0.

Process compliance is scored separately. It should not rescue a weak final answer, but it helps diagnose whether the skill workflow itself needs improvement.

## Regression Review

For each new run, compare totals, per-dimension scores, and failure notes against the previous run. If an old must-pass case fails, treat it as a benchmark regression until the skill, prompt, or rubric is corrected.

When a new bad or adversarial case reveals a real weakness, keep that case in the benchmark permanently unless it is redundant with another case.
