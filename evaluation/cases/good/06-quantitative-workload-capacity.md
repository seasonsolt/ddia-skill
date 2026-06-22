# Case: Quantitative Workload Capacity

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this design:

We are building an activity feed service. Today it has 2 million daily active users, 35 million read requests per day, 4 million writes per day, p95 feed-read latency target of 150 ms, and a 12-month growth expectation of 10x. The proposal stores posts in PostgreSQL, precomputes fanout into Redis sorted sets, and rebuilds feeds overnight. Review whether the architecture can meet workload, correctness, and cost goals.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill turns vague scalability discussion into quantitative capacity reasoning.

## Weak Answer Patterns

- Says the system can scale by adding cache or replicas without calculating reads, writes, fanout, storage, or rebuild time.
- Ignores hot users, celebrity fanout, cache memory pressure, queue backlog, and read latency targets.
- Skips cost and operational limits for Redis memory, rebuild jobs, and database write amplification.

## Strong Answer Signals

- Converts daily reads and writes into peak QPS assumptions and asks for fanout distribution.
- Compares fanout-on-write, fanout-on-read, and hybrid approaches with storage and latency trade-offs.
- Discusses hot keys, queue backpressure, rebuild duration, cache eviction, and consistency between PostgreSQL and derived feeds.
- Proposes load tests, queue lag alerts, feed freshness SLOs, and cost estimates for 10x growth.

## Scoring Notes

- Score workload framing based on concrete rate, storage, latency, and growth calculations.
- Score trade-off quality based on whether the answer chooses a feed strategy from workload shape rather than tool preference.
