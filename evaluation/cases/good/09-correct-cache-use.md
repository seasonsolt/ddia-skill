# Case: Correct Cache Use

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this cache design:

Our product catalog service stores product data in PostgreSQL and serves product detail pages through an API. Product data changes a few thousand times per day, reads are 40,000 QPS at peak, and stale price reads must last less than 30 seconds. The proposal uses Redis cache-aside with TTL, background refresh for hot products, and fallback to PostgreSQL on miss. Review whether this is a correct cache design and what needs to be verified.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill can approve cache use when the cache remains derived state.

## Weak Answer Patterns

- Rejects all caching without considering read workload and freshness tolerance.
- Treats TTL as sufficient without discussing invalidation, rebuild, cache stampede, and stale price risk.
- Skips fallback behavior when Redis is unavailable or PostgreSQL is under pressure.

## Strong Answer Signals

- Keeps PostgreSQL as source of truth and Redis as derived, rebuildable state.
- Discusses cache-aside, TTL, targeted invalidation, hot-key protection, stampede prevention, and stale-read bounds.
- Separates price correctness from less critical catalog fields.
- Proposes freshness metrics, cache hit rate, invalidation tests, Redis-loss tests, and stale-price audits.

## Scoring Notes

- Score trade-off quality based on accepting cache use with explicit correctness boundaries.
- Score verification value based on freshness, rebuild, and degradation tests.
