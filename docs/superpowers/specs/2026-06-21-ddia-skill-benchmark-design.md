# DDIA Skill Benchmark Design

## Goal

Design a repeatable benchmark that verifies whether the `ddia-system-design`
skill helps backend engineers and architects produce better data-intensive
system designs.

The benchmark has two jobs:

- Prove usefulness: good cases should show that the skill improves practical
  architecture reasoning.
- Drive iteration: bad and adversarial cases should expose weak behavior so
  future skill changes can be measured against stable regression cases.

## Current Context

The repository already contains a first evaluation suite:

- Five good-case prompts under `evaluation/prompts/`.
- A 0-2 scoring rubric in `evaluation/rubric.md`.
- A results template and one completed result file.
- Structural validation in `scripts/check_ddia_skill_quality.py`.

The current suite proves baseline usefulness, but it does not fully test
anti-pattern resistance, vague prompts, adversarial premises, or process
compliance.

## Benchmark Architecture

The benchmark will use three layers.

### Layer A: Answer Quality

This layer evaluates the final architecture answer. It works even when hidden
model behavior is not observable.

It asks whether the response is concrete, DDIA-style, operationally useful, and
correct for the scenario.

### Layer B: Process Compliance

This layer evaluates whether the agent followed the `ddia-system-design` skill
workflow.

It checks for observable behaviors such as framing assumptions before
recommendations, asking for missing workload and correctness requirements,
using the standard response shape, and converting claims into tests or
operational checks.

### Layer C: Regression History

This layer records benchmark scores per skill version. When the skill changes,
old cases should not regress. New bad cases become permanent regression tests
after they expose a real weakness.

## Proposed File Structure

```text
evaluation/
  cases/
    good/
    bad/
    adversarial/
  rubrics/
    answer-quality.md
    process-compliance.md
  results/
    YYYY-MM-DD-<commit>.md
  benchmark-guide.md
```

The existing five prompts can be migrated into `evaluation/cases/good/`.

## Test Case Set

### Good Cases

Keep the current five scenarios as baseline good cases:

1. Order consistency
2. Event pipeline
3. Database choice
4. Replica lag
5. Derived data correctness

These cases verify that the skill can produce useful architecture guidance for
common backend design problems.

### Bad And Adversarial Cases

Add eight cases designed to catch weak or overly agreeable answers:

1. Tool-first trap: the prompt asks whether to use Kafka and Cassandra before
   stating workload or correctness needs.
2. Cache-as-truth trap: the design uses Redis or a search index as the source
   of truth for business decisions.
3. Replica-lag denial: the prompt claims eventual consistency is acceptable
   while describing read-your-writes or monotonic-read bugs.
4. Exactly-once trap: the prompt asks for exactly-once event processing without
   defining sinks, idempotency, or deduplication boundaries.
5. Distributed-lock trap: the prompt proposes Redis locks for cross-service
   financial correctness.
6. Schema-evolution trap: the prompt asks to change event schemas quickly
   across services without compatibility planning.
7. Hot-partition trap: the prompt uses tenant ID or timestamp partitioning
   despite celebrity tenants or high write skew.
8. Vague-startup-architecture trap: the prompt asks for a definitive database
   choice while omitting workload and correctness requirements.

Each bad or adversarial case should include:

- Prompt text.
- The bad premise or trap.
- Weak-answer patterns.
- Strong-answer signals.
- Scoring notes.
- Whether the case is must-pass or diagnostic-only.

## Answer Quality Rubric

Good cases use the existing five 0-2 dimensions:

1. Workload framing
2. Trade-off quality
3. Failure-mode coverage
4. Correctness reasoning
5. Verification value

Bad and adversarial cases add a sixth dimension:

6. Anti-pattern resistance

Anti-pattern resistance measures whether the answer challenges the bad premise
instead of optimizing around it.

## Passing Standards

Good case:

- At least 8 out of 10.
- No dimension scored 0.

Bad or adversarial case:

- At least 10 out of 12.
- No dimension scored 0.
- Anti-pattern resistance must be 2.

Whole benchmark:

- All must-pass cases must pass.
- Diagnostic-only cases may fail, but their scores and failure notes must be
  recorded.

## Process Compliance Rubric

Score each response from 0 to 2 on these dimensions:

1. Loads or references relevant DDIA skill materials when needed.
2. Frames assumptions before recommending.
3. Asks for missing workload or correctness requirements when underspecified.
4. Uses the standard response shape or an equivalent explicit structure.
5. Converts design claims into tests, metrics, experiments, or runbook checks.

Process compliance is scored separately from answer quality because an answer
can be useful while still revealing that the skill workflow was not followed
consistently.

## Benchmark Execution Workflow

Each run should follow the same process:

1. Record the skill version, usually the current Git commit.
2. Run every case in `evaluation/cases/good/`,
   `evaluation/cases/bad/`, and `evaluation/cases/adversarial/`.
3. Capture the model response for each case.
4. Score the response with the answer-quality rubric.
5. Score process behavior separately when observable.
6. Write results to `evaluation/results/YYYY-MM-DD-<commit>.md`.
7. Compare the run against the previous benchmark result.
8. Record regressions and recommended skill changes.

For bad cases, results must explicitly record:

- The bad premise in the prompt.
- What a weak answer did or would do.
- What a strong DDIA-style answer should do.
- Whether the response challenged the premise.

## Validation Requirements

Deterministic validation should check that:

- Required directories exist.
- Required rubric files exist and contain the expected dimensions.
- Every case file declares its category, title, prompt, expected weak patterns,
  expected strong signals, scoring notes, and pass mode.
- The results template supports good, bad, adversarial, answer-quality,
  process-compliance, and regression sections.

The validation should not judge architecture quality itself. It should only
verify that the benchmark files are complete and consistently structured.

## Out Of Scope

The first benchmark version will not include:

- Fully automated LLM judging.
- Multi-vendor model comparisons.
- Statistical scoring across repeated runs.
- A web dashboard.
- CI automation.

These can be added later if the benchmark proves valuable.

## Success Criteria

The benchmark is successful when:

- A future agent can run it from the documentation without asking for missing
  process details.
- Good cases demonstrate practical architecture reasoning.
- Bad and adversarial cases expose anti-pattern resistance.
- Results are comparable across skill versions.
- New weaknesses can be added as permanent regression cases.
