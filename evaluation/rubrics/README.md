# DDIA Rubrics

This directory holds the benchmark scoring rubrics. Two rubric files coexist
for historical and operational reasons.

## `evaluation/rubric.md`

The first-pass usefulness rubric. It scores five dimensions (Workload framing,
Trade-off quality, Failure-mode coverage, Correctness reasoning, Verification
value) on a 0-2 scale for a maximum of 10. It was used to score the original
five-prompt evaluation recorded in `evaluation/results.md`.

Use it when reproducing or extending the first-pass evaluation under
`evaluation/prompts/`. It does not score Anti-pattern resistance because the
first-pass prompts contain no deliberate traps.

## `evaluation/rubrics/answer-quality.md`

The benchmark answer-quality rubric. It scores the same five dimensions plus
Anti-pattern resistance for a maximum of 10 (good cases) or 12 (bad and
adversarial cases). It is the rubric used by the benchmark suite and the A/B
evaluation.

Use it for all scoring under `evaluation/cases/` and `evaluation/ab/`. Bad and
adversarial cases require Anti-pattern resistance to score 2 to pass.

## `evaluation/rubrics/process-compliance.md`

A separate process rubric scored alongside answer quality when the agent
workflow is observable. It does not rescue a weak answer; it diagnoses whether
the skill workflow itself needs improvement.

## Relationship

`rubric.md` is the frozen first-pass rubric. `rubrics/answer-quality.md` is the
current benchmark rubric. The repository checkers validate these rubric files:
`check_ddia_skill_quality.py` validates `evaluation/rubric.md`, while
`check_ddia_benchmark.py` validates the benchmark rubrics under
`evaluation/rubrics/`. Do not delete `rubric.md`; the first-pass evaluation
results depend on it.
