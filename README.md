# DDIA System Design Skill

`ddia-system-design` is a Codex skill for backend engineers and architects who
need sharper reviews of data-intensive systems.

The skill turns an architecture question into explicit workload assumptions,
data model choices, consistency requirements, failure modes, and verification
steps. It is inspired by *Designing Data-Intensive Applications*, but the
committed skill content is original engineering guidance and review material.
This repository does not contain the DDIA PDF or extracted book text.

## What The Skill Helps With

Use it when you are designing or reviewing systems that involve:

- database choice and data modeling
- replication, replica lag, failover, and read consistency
- partitioning, hot keys, and rebalancing
- transactions, isolation levels, idempotency, and invariants
- distributed locks, leases, timeouts, retries, and partial failure
- batch processing, stream processing, replay, and late events
- caches, indexes, search documents, materialized views, and other derived data
- operational checks, backfills, schema evolution, and incident response

The skill pushes the agent to ask for missing workload and correctness
requirements before making a strong recommendation. It also pushes every
recommendation toward tests, metrics, experiments, or runbook checks.

## Skill Workflow

The skill uses this response shape by default:

1. Assumptions and workload shape
2. Recommendation
3. Key trade-offs
4. Failure modes
5. Consistency and correctness implications
6. Operational checks
7. Tests or experiments to validate the design

It includes three reference files:

- [`topic-map.md`](skills/ddia-system-design/references/topic-map.md) maps
  architecture problems to DDIA-style review lenses.
- [`system-design-principles.md`](skills/ddia-system-design/references/system-design-principles.md)
  gives decision rules for workload, guarantees, derived data, failure, and
  evolution.
- [`architecture-review-checklists.md`](skills/ddia-system-design/references/architecture-review-checklists.md)
  gives concrete review questions for design docs and production systems.

## Evaluation Results

The first evaluation suite scored the skill on five dimensions:

- workload framing
- trade-off quality
- failure-mode coverage
- correctness reasoning
- verification value

Each dimension is scored from 0 to 2. A case passes at 8 out of 10 or higher
with no zero-scored dimension.

| Evaluation case | Score | Pass | What the response showed |
| --- | ---: | --- | --- |
| Order consistency | 8/10 | yes | Treated Redis and inventory events as derived/asynchronous paths. Recommended source-of-truth boundaries, transactional outbox, idempotency, reconciliation, and failure injection. |
| Event pipeline | 10/10 | yes | Covered durable logs, raw event storage, event time, watermarks, replay, idempotent sinks, late events, consumer lag, and reconciliation. |
| Database choice | 9/10 | yes | Recommended relational storage as the source of truth and explained document and graph database trade-offs. |
| Replica lag | 10/10 | yes | Identified read-your-writes and monotonic-read gaps, then tied fixes to leader reads, session stickiness, LSN/version routing, synchronous replication costs, and observability. |
| Derived data | 9/10 | yes | Treated Elasticsearch as derived state and kept billing decisions anchored in PostgreSQL. |

Result: all five prompts passed. The full record is in
[`evaluation/results.md`](evaluation/results.md).

## A/B Status

These results are not an A/B test yet. They are criterion-based evaluations of
skill-enabled responses. They show that the skill can produce useful DDIA-style
answers on the selected cases, but they do not measure lift against a no-skill
baseline.

An A/B run should compare:

- A: the same model answering each case without `ddia-system-design`
- B: the same model answering each case with `ddia-system-design`

Both runs should use the same prompts, model, temperature, and scoring rubric.
The evaluator should score responses without knowing which run produced them.
Useful metrics include total score lift, per-dimension lift, pass-rate change,
and anti-pattern resistance improvement on bad and adversarial cases.

## Benchmark Suite

The repository also includes a repeatable benchmark for future skill changes.
It has 13 cases:

- 5 good cases in [`evaluation/cases/good`](evaluation/cases/good)
- 4 bad cases in [`evaluation/cases/bad`](evaluation/cases/bad)
- 4 adversarial cases in [`evaluation/cases/adversarial`](evaluation/cases/adversarial)

Good cases check whether the skill can answer normal architecture questions.
Bad and adversarial cases test whether it resists unsafe premises such as:

- using a cache as the source of truth for payment decisions
- accepting replica-lag bugs as "eventual consistency"
- choosing a partition key despite clear write skew
- confirming a Kafka/Cassandra/Redis/Elasticsearch stack before workload analysis
- treating exactly-once stream processing as an end-to-end guarantee
- using Redis locks for cross-service financial correctness
- deploying breaking event schema changes because JSON is flexible

The benchmark has two scoring layers:

- [`answer-quality.md`](evaluation/rubrics/answer-quality.md) scores the final
  architecture answer.
- [`process-compliance.md`](evaluation/rubrics/process-compliance.md) scores
  whether the agent followed the skill workflow.

Use [`evaluation/benchmark-guide.md`](evaluation/benchmark-guide.md) to run a
benchmark pass and record results in
[`evaluation/results/template.md`](evaluation/results/template.md).

## Validation

Run the deterministic checks from the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_ddia_skill_quality.py --repo .
python3 scripts/check_ddia_benchmark.py --repo .
```

Current validation status:

- 36 unit tests pass.
- `check_ddia_skill_quality.py` reports no missing files, terms, invalid files, or structure errors.
- `check_ddia_benchmark.py` reports `good: 5`, `bad: 4`, `adversarial: 4`, with no benchmark errors.

## Install Locally

Copy the skill directory into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R skills/ddia-system-design ~/.codex/skills/ddia-system-design
```

Then start a Codex task that involves backend architecture, databases,
replication, partitioning, transactions, distributed systems, streams, or
derived data. The skill description is designed to trigger on those topics.

## Repository Layout

```text
skills/ddia-system-design/      Codex skill package
evaluation/prompts/             First-pass evaluation prompts
evaluation/results.md           First evaluation result record
evaluation/cases/               Good, bad, and adversarial benchmark cases
evaluation/rubrics/             Answer-quality and process-compliance rubrics
scripts/                        Extraction and validation helpers
tests/                          Deterministic unit tests
analysis/                       Original reading ledger
docs/                           Reading protocol, specs, and implementation plans
```

## Copyright Boundary

This project uses a local copy of the DDIA PDF only for private reading and
note extraction. Generated private text goes under `tmp/`, which Git ignores.
Committed files contain original notes, checklists, prompts, rubrics, and skill
instructions.
