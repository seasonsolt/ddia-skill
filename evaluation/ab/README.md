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

The control arm is a no-skill baseline. It forbids loading or relying on `ddia-system-design`, but it does not forbid normal structured architecture reasoning.

The treatment arm uses `ddia-system-design` and may follow its response shape. This creates a known response-shape/rubric alignment risk, so evaluators should score answer substance rather than heading presence.

## Pilot Case Set

- `evaluation/cases/good/01-order-consistency.md`
- `evaluation/cases/good/04-replica-lag.md`
- `evaluation/cases/bad/01-cache-as-truth.md`
- `evaluation/cases/adversarial/02-exactly-once-trap.md`
- `evaluation/cases/bad/04-vague-startup-architecture.md`

## Limitations

This is pilot A/B evidence, not statistical proof. The current pilot has self-evaluation bias, response-shape/rubric alignment risk, a single model, a single run per arm, no variance estimate, and non-random case selection. It also scores answer quality only; it does not score the process-compliance rubric.

A stronger study would use independent blinded scoring, repeated randomized runs, and more than one model.

## Repeated-Run Protocol

Use repeated runs when moving beyond pilot evidence:

1. Select cases before generating responses.
2. Run at least three control responses and three treatment responses per case.
3. Randomize whether control or treatment is labeled Response A for each pair.
4. Score all responses before revealing mapping.
5. Report mean, minimum, maximum, and range for each arm.
6. Report pass-threshold crossings separately from average score lift.
7. Preserve all response texts so another evaluator can rescore.
