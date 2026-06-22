# DDIA Skill A/B Evaluation

## Purpose

Use this A/B workflow to compare backend architecture answers from the same model with and without `ddia-system-design`.

The control response answers the case without using or referencing the skill. The treatment response answers the same case with the skill. Both responses use the same case prompt and the same answer-quality rubric.

## Method

1. Pick benchmark cases from `evaluation/cases/`.
2. Generate a control response with `control-instructions.md`.
3. Generate a treatment response with `treatment-instructions.md`.
4. Label the responses as `Response A` and `Response B`.
5. Score both responses with `blind-scoring-guide.md` before revealing the mapping.
6. Record control score, treatment score, lift, pass/fail change, and notes.

## Pilot Case Set

- `evaluation/cases/good/01-order-consistency.md`
- `evaluation/cases/good/04-replica-lag.md`
- `evaluation/cases/bad/01-cache-as-truth.md`
- `evaluation/cases/adversarial/02-exactly-once-trap.md`
- `evaluation/cases/bad/04-vague-startup-architecture.md`

## Limitations

This is pilot A/B evidence, not statistical proof. A stronger study would use independent blinded scoring, repeated randomized runs, and more than one model.
