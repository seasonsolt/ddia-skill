# DDIA A/B Credibility Hardening Design

## Goal

Strengthen the credibility of the existing `ddia-system-design` A/B evaluation
without expanding the benchmark case set yet.

The current pilot is useful directional evidence, but it is too easy to
challenge because the treatment response shape aligns with the scoring rubric,
the control instructions are stricter than a normal no-skill baseline, and the
pilot uses one model, one run, and self-evaluation.

## Scope

This pass focuses on credibility and documentation, not new benchmark topics.
It should update the A/B assets, validation logic, and README so the evidence is
honest, reproducible, and harder to overread.

In scope:

- Reframe the README pilot claim as one paired pilot observation.
- Make control instructions fairer by forbidding skill loading but not forbidding
  normal structured system-design reasoning.
- Add explicit limitations for self-evaluation bias, response-shape/rubric
  alignment, single-model scope, single-run scope, no variance estimate, and
  non-random case selection.
- Add normalized score reporting so 10-point and 12-point cases can be compared.
- Add deterministic validation for A/B arithmetic and required limitation terms.
- Add a documented stronger next-run protocol using repeated runs and
  randomized labels.

Out of scope:

- Adding new benchmark cases.
- Running a new multi-run A/B study.
- Adding automated LLM judging.
- Changing the `ddia-system-design` skill behavior itself, except where docs may
  clarify future work.

## Current Problems To Fix

### Over-Strong Pilot Wording

The README currently says treatment moved four must-pass cases from fail to
pass. The statement is factually based on the pilot table, but the wording reads
stronger than the evidence. It should be reframed as:

> In one five-case paired pilot run, treatment scored higher than control and
> four must-pass cases crossed the pass threshold.

The README should still show the result, but it must make the evidence level
clear: directional pilot evidence, not statistical proof.

### Control Instruction Handicap

The current control instructions prohibit using the skill workflow, reference
files, and skill response shape. That makes the control arm weaker than a normal
baseline because it discourages structured system-design reasoning.

The fairer control should say:

- Do not load, invoke, mention, or rely on `ddia-system-design`.
- Use general backend architecture knowledge.
- Use whatever clear answer structure you normally would.

It should not prohibit a structured architecture answer.

### Response Shape Confound

Treatment instructions require a response shape that maps closely to the
answer-quality rubric dimensions. This is useful for skill behavior, but it
confounds the A/B result: treatment may score higher partly because it has
dedicated headings for rubric dimensions.

The limitations must name this directly. The next-run protocol should reduce
the confound by allowing the control arm to use normal structured answers.

### Mixed Raw Score Denominators

Good cases are scored out of 10. Bad and adversarial cases are scored out of 12.
Raw totals are still useful for auditability, but direct raw aggregation weights
12-point cases more heavily.

The pilot result should add normalized per-case percentages and mean normalized
scores:

- normalized control percent
- normalized treatment percent
- normalized lift in percentage points
- mean normalized control
- mean normalized treatment
- mean normalized lift

### Missing Arithmetic Validation

The checker validates A/B structure, but it does not validate score arithmetic.
Future edits could accidentally drift the pilot totals or lift values.

The checker should validate:

- every pilot score row has parseable `N/D` control and treatment scores
- every lift value matches treatment numerator minus control numerator when the
  denominators match
- total control score equals the sum of control numerators
- total treatment score equals the sum of treatment numerators
- total lift equals treatment total minus control total
- normalized score fields are present
- required limitation phrases are present

For mixed denominators, raw lift validation should be limited to rows where the
case uses a single denominator for both arms, which is true in the pilot.

## Target Files

- `evaluation/ab/control-instructions.md`
  - Relax the control baseline so it forbids skill use but allows ordinary
    structured architecture reasoning.
- `evaluation/ab/treatment-instructions.md`
  - Keep the skill-enabled response shape, but make the comparison limitation
    explicit in the A/B docs rather than hiding it.
- `evaluation/ab/README.md`
  - Explain the fairer control/treatment setup and the stronger future protocol.
- `evaluation/ab/blind-scoring-guide.md`
  - Tell evaluators to score by content, not by heading presence alone.
- `evaluation/ab/results-template.md`
  - Add normalized scoring fields and explicit limitation fields.
- `evaluation/ab/pilot-results.md`
  - Add normalized score table or columns.
  - Add detailed limitations.
  - State that this pilot scores answer quality only and does not score the
    process-compliance rubric.
  - Reframe the overall decision as a single paired pilot observation.
- `scripts/check_ddia_benchmark.py`
  - Add A/B score and limitation validation.
- `tests/test_ddia_benchmark.py`
  - Add tests for arithmetic validation, missing normalized fields, and missing
    limitation terms.
- `README.md`
  - Reword the pilot A/B section to reduce causal overclaiming.

## Validation Rules

The deterministic checker should reject incomplete A/B results when:

- required A/B files are missing
- required sections are missing
- control instructions still forbid normal structured system-design reasoning
- pilot results omit normalized scoring
- pilot results omit explicit limitations for:
  - self-evaluation bias
  - response-shape/rubric alignment
  - single model
  - single run
  - no variance estimate
  - non-random case selection
  - process-compliance rubric not scored
- score totals do not reconcile
- total lift does not equal treatment total minus control total

The checker should not decide whether the pilot proves the skill works. It only
checks whether the result is structurally honest and arithmetically consistent.

## Deferred Gaps

This pass intentionally hardens the credibility of the current A/B evidence
before expanding scope. The following review findings remain valid and should
be handled by later passes.

### Benchmark Coverage Gaps

Defer these to a benchmark case-expansion pass:

- Quantitative workload and capacity planning case with concrete rates, data
  sizes, latency targets, and growth assumptions.
- Consensus or multi-region write case covering leader election, quorum,
  conflict handling, or linearizability trade-offs.
- Batch processing and backfill case covering idempotent outputs, replay,
  late data, joins, and reconciliation.
- Database schema evolution case covering expand-contract rollout, online
  migration, backfill, and rollback.
- Correct cache-use good case covering cache-aside, write-through, TTL,
  invalidation, and rebuild trade-offs.
- Observability and runbook case where metrics, alerts, dashboards, and
  operator actions are the main design output.
- Idempotency and outbox/inbox case where duplicate requests, retries, and
  crash windows are the primary concern.
- Capacity and cost case that asks whether the design can handle 10x growth and
  what it costs to operate.

### Skill Tuning Gaps

Defer these to a skill-tuning pass:

- Clarify whether `skills/ddia-system-design/agents/openai.yaml` is required
  packaging metadata, and test or remove it accordingly.
- Add a short worked example to `SKILL.md` to calibrate answer granularity.
- Add a narrow-follow-up exemption so the seven-section response shape does not
  force verbose answers for small questions.
- Add explicit "do not use for" boundaries for pure algorithms, frontend
  component choices, and simple single-node CRUD questions.
- Reduce repeated concepts across reference files so topic maps map, principles
  decide, and checklists ask.

### Test Infrastructure Gaps

Defer these to a test-infrastructure pass:

- Add behavior-oriented regression evidence beyond structural file checks.
- Revisit the `prompt_count == 5` constraint so first-pass evaluation prompts
  can evolve without excessive checker churn.
- Decide whether heading-coupled tests should remain strict regression guards
  or become easier to evolve.
- Add coverage for `skills/ddia-system-design/agents/openai.yaml` if the file
  remains part of the package.
- Separate private reading/PDF extraction tests from skill-package tests in
  reporting so test counts do not overstate skill regression coverage.
- Document the relationship between historical `evaluation/rubric.md` and
  benchmark `evaluation/rubrics/answer-quality.md`.
- Replace hardcoded local PDF fallback paths with explicit environment-variable
  configuration or skip behavior.

## Stronger Next-Run Protocol

Add a documented next-run protocol under `evaluation/ab/README.md` or a new
`evaluation/ab/repeated-run-protocol.md`.

The protocol should specify:

1. Select cases before generating responses.
2. Run at least three control responses and three treatment responses per case.
3. Randomize whether control or treatment is labeled Response A for each pair.
4. Score all responses before revealing mapping.
5. Report mean, minimum, maximum, and range for each arm.
6. Report pass-threshold crossings separately from average score lift.
7. Preserve all response texts so another evaluator can rescore.

This protocol is documentation only for this pass. Actually running the repeated
study is a later project.

## Success Criteria

This improvement pass is successful when:

- README no longer implies that the five-case pilot is a strong causal proof.
- The A/B docs explicitly discuss the main threats to validity.
- The control arm is fairer and no longer banned from normal structured answers.
- The pilot result includes normalized scores and detailed limitations.
- The benchmark checker catches score arithmetic drift and missing limitations.
- The full unit suite and benchmark checker pass.
