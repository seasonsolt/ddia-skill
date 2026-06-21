# Case: Distributed Lock Trap

Category: adversarial
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to review this money-transfer design:

Account balances live in separate services. To prevent double spending, each transfer obtains a Redis distributed lock on both account IDs, updates both services over HTTP, and releases the locks. The lock TTL is 5 seconds. Is this enough to guarantee correctness?

## Bad Premise Or Trap

The prompt treats short-lived Redis locks as sufficient for cross-service financial correctness.

## Weak Answer Patterns

- Accepts Redis locks as a correctness guarantee.
- Ignores process pauses, expired leases, partial HTTP failures, fencing, retries, and split-brain behavior.
- Does not discuss transaction boundaries or authoritative ledger design.

## Strong Answer Signals

- Rejects locks alone as sufficient for financial correctness.
- Discusses authoritative ledger, database constraints, serializable transactions, consensus-backed coordination, fencing tokens, idempotency, and compensation.
- Explains availability and latency trade-offs of stronger coordination.
- Proposes concurrency tests, pause-after-lock tests, TTL-expiry tests, duplicate transfer tests, and invariant checks.

## Scoring Notes

- Anti-pattern resistance must explicitly say the proposed locks do not guarantee correctness.
- Score failure-mode coverage based on partial failure and lease-expiry scenarios.
