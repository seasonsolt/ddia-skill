# Case: Replica Lag Denial

Category: bad
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to review this incident:

The product team says eventual consistency is fine for profile data. After moving all profile reads to replicas, users report that saving settings sometimes appears to fail because a refresh shows the old value. The team proposes adding a banner that says changes may take a few seconds. Is that enough?

## Bad Premise Or Trap

The prompt claims eventual consistency is acceptable while describing a read-your-writes product bug.

## Weak Answer Patterns

- Accepts the banner as sufficient without challenging the product behavior.
- Treats all profile reads as equally stale-tolerant.
- Ignores monotonic reads, session behavior, and replica lag observability.

## Strong Answer Signals

- Challenges the premise by separating stale-tolerant reads from read-your-writes paths.
- Discusses leader reads, session stickiness, version-aware routing, or LSN-aware reads after writes.
- Explains latency, availability, and operational costs of each option.
- Proposes metrics and tests for stale reads, monotonic reads, and replica apply lag.

## Scoring Notes

- Anti-pattern resistance must identify that a UX banner does not fix correctness for immediate post-write reads.
- Score verification value based on specific stale-read reproduction tests and lag monitoring.
