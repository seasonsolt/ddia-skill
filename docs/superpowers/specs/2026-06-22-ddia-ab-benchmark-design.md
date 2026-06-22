# DDIA Skill A/B Benchmark Design

## Goal

Add a reusable A/B evaluation layer for `ddia-system-design` and record a first
pilot result. The A/B layer should answer a stricter question than the current
benchmark:

Does the same model produce better backend architecture answers when it uses
`ddia-system-design` than when it answers without the skill?

## Current Context

The repository already has:

- A first criterion-based evaluation in `evaluation/results.md`.
- Thirteen benchmark cases under `evaluation/cases/`.
- Answer-quality and process-compliance rubrics under `evaluation/rubrics/`.
- A benchmark guide and result template.
- A benchmark checker that validates the case library and rubric files.

Those assets show that skill-enabled responses can pass useful DDIA-style
cases. They do not yet prove lift against a no-skill baseline.

## A/B Benchmark Shape

The A/B benchmark will live under `evaluation/ab/`:

```text
evaluation/ab/
  README.md
  control-instructions.md
  treatment-instructions.md
  blind-scoring-guide.md
  results-template.md
  pilot-results.md
```

The A/B layer will reuse the existing case files:

```text
evaluation/cases/good/
evaluation/cases/bad/
evaluation/cases/adversarial/
```

Control responses must answer without loading, invoking, or referencing
`ddia-system-design`. Treatment responses must use `ddia-system-design` and
follow its response shape.

## Pilot Case Set

The first pilot will use five cases:

1. `evaluation/cases/good/01-order-consistency.md`
2. `evaluation/cases/good/04-replica-lag.md`
3. `evaluation/cases/bad/01-cache-as-truth.md`
4. `evaluation/cases/adversarial/02-exactly-once-trap.md`
5. `evaluation/cases/bad/04-vague-startup-architecture.md`

This mix covers normal design review, consistency behavior, derived-state
correctness, anti-pattern resistance, and underspecified architecture advice.

## Scoring

Both control and treatment responses use the same answer-quality rubric in
`evaluation/rubrics/answer-quality.md`.

Good cases:

- Maximum score: 10.
- Passing standard: at least 8 out of 10 with no zero-scored dimension.
- Anti-pattern resistance is not scored.

Bad and adversarial cases:

- Maximum score: 12.
- Passing standard: at least 10 out of 12 with no zero-scored dimension.
- Anti-pattern resistance must score 2.

Each pilot case result must record:

- Case ID and category.
- Control score.
- Treatment score.
- Absolute score lift.
- Pass/fail change.
- Dimension-level score differences.
- Notes explaining where the skill helped or failed to help.

## Execution Method

The first pilot will use a practical paired-run method:

1. Generate one control response for each pilot case using
   `evaluation/ab/control-instructions.md`.
2. Generate one treatment response for each pilot case using
   `evaluation/ab/treatment-instructions.md`.
3. Store both responses as `Response A` and `Response B` in the result file.
4. Score `Response A` and `Response B` using the answer-quality rubric.
5. Reveal the mapping after scores are recorded: control versus treatment.
6. Compute per-case lift and total lift.

The pilot is not a fully independent blinded study because the same agent may
run and score it. The result file must preserve response text, scoring notes,
and mapping so another evaluator can rescore it later.

## Evidence Standard

The README may describe the result as pilot A/B evidence only. It must not
claim statistical proof.

If treatment beats control, the README can report:

```text
Pilot A/B: treatment beat control by +N total points across 5 cases.
```

If treatment does not beat control, the README must report that result and use
the failure notes to drive skill improvement.

## Validation Requirements

Validation should check that:

- All required `evaluation/ab/` files exist.
- The A/B README explains control, treatment, blind scoring, and limitations.
- Control instructions forbid using or referencing `ddia-system-design`.
- Treatment instructions require using `ddia-system-design`.
- The blind scoring guide tells the evaluator to score before revealing mapping.
- The results template has fields for response labels, hidden mapping,
  dimensions, score lift, notes, and overall decision.
- The pilot result covers the five selected cases and records control score,
  treatment score, lift, pass/fail change, notes, and limitations.

The validator should only check structure and required fields. It should not
decide whether the A/B score itself is persuasive.

## Out Of Scope

The first A/B version will not include:

- Automated LLM judging.
- Statistical confidence intervals.
- Multi-model comparisons.
- Repeated randomized runs.
- Independent external human scoring.
- CI automation.

Those can be added after the pilot proves the workflow is useful.

## README Update

The README should replace the current "not A/B yet" wording with a short pilot
A/B section that links to `evaluation/ab/pilot-results.md`.

The README should still state the limitation: the pilot is paired and scored
from preserved responses, but it is not a statistical proof.

## Success Criteria

This work is successful when:

- A future evaluator can rerun the A/B process from the docs.
- The first pilot compares control and treatment on the same five cases.
- The pilot result reports lift honestly, including failures or weak gains.
- Deterministic validation catches missing A/B files or incomplete pilot
  fields.
- The README shows A/B evidence without overstating it.
