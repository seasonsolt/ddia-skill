# Case: Replica Lag

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to diagnose this production issue:

After moving read traffic to replicas, users sometimes update profile settings and then immediately see old values. Support also reports non-monotonic behavior when users refresh quickly. Explain likely causes, design options, trade-offs, and observability checks.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill connects replica lag to read-your-writes and monotonic-read behavior.

## Weak Answer Patterns

- Says replica lag is expected and stops there.
- Recommends reading from the leader for everything without discussing cost.
- Omits session routing, LSN or version tracking, failover behavior, and lag observability.

## Strong Answer Signals

- Names read-your-writes and monotonic-read violations.
- Discusses leader reads, session stickiness, version or LSN-aware routing, synchronous replication costs, and fallback behavior.
- Proposes replica lag metrics, stale-read tests, and user-session checks.

## Scoring Notes

- Score correctness reasoning based on whether the answer translates consistency terms into user-visible behavior.
- Score verification value based on reproducible stale-read tests and monitoring for replica apply lag.
