# Case: Capacity Cost Handwave

Category: bad
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to review this proposal:

Our metrics ingestion service handles 200,000 events per second today and must support 10x growth next year. The proposal says we should store raw events, rollups, and query indexes in one PostgreSQL cluster because PostgreSQL is reliable. If load grows, we can move to bigger machines or add read replicas later. Is this acceptable?

## Bad Premise Or Trap

The prompt handwaves capacity, cost, write amplification, retention, and query workload while assuming vertical scaling and read replicas solve ingestion growth.

## Weak Answer Patterns

- Accepts one database cluster without calculating ingestion rate, storage growth, retention, or index cost.
- Suggests read replicas for a write-heavy ingestion bottleneck.
- Ignores partitioning, compaction, rollup strategy, hot indexes, backpressure, and cost controls.

## Strong Answer Signals

- Rejects the handwave and asks for event size, retention, query patterns, cardinality, and SLOs.
- Estimates write volume, storage growth, index overhead, and 10x operating cost.
- Separates raw event storage, rollups, query-serving indexes, and retention policies.
- Proposes load tests, backpressure, partitioning, compaction, cost dashboards, and degradation behavior.

## Scoring Notes

- Anti-pattern resistance must identify that read replicas do not solve write ingestion capacity.
- Score workload framing based on concrete volume, retention, and cost calculations.
