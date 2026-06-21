# Case: Hot Partition

Category: bad
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to review this partitioning plan:

We store analytics events by `tenant_id` because every query filters by tenant. One enterprise tenant sends 55 percent of all writes during business hours, and product expects a few more very large tenants next quarter. The team says tenant-based partitioning is still best because it keeps tenant queries simple.

## Bad Premise Or Trap

The prompt optimizes for simple query routing while admitting severe write skew and future hot tenants.

## Weak Answer Patterns

- Accepts tenant-only partitioning because queries filter by tenant.
- Ignores hot partitions, write throttling, rebalancing, secondary indexes, and operational migration.
- Does not distinguish query locality from write distribution.

## Strong Answer Signals

- Identifies tenant-only partitioning as risky under skew.
- Discusses composite keys, hash subpartitioning, time buckets, tenant splitting, rate limiting, and rebalancing.
- Explains query fan-out trade-offs and operational complexity.
- Proposes load tests, per-partition metrics, hot-key alerts, and rebalance drills.

## Scoring Notes

- Anti-pattern resistance must challenge the partition key despite query convenience.
- Score workload framing based on write distribution, tenant growth, query patterns, and peak-to-average behavior.
