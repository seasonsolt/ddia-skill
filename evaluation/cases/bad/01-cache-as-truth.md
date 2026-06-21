# Case: Cache As Truth

Category: bad
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to review this proposal:

Our checkout service stores cart totals in PostgreSQL, but Redis is much faster. We want the payment workflow to read the final payable amount from Redis because the cache is updated on every cart change. PostgreSQL can be updated later by an asynchronous worker. Is this design acceptable if Redis has high availability?

## Bad Premise Or Trap

The prompt treats a cache as authoritative for a financial decision because it is fast and highly available.

## Weak Answer Patterns

- Accepts Redis as the source of truth for payment amount because it is fast.
- Equates high availability with correctness.
- Ignores cache loss, stale values, missed updates, race conditions, and reconciliation.

## Strong Answer Signals

- Rejects Redis as the authoritative source for payment decisions.
- Keeps payment amount and checkout invariants in a transactional source of truth.
- Allows Redis only as derived state with invalidation, rebuild, lag metrics, and reconciliation.
- Proposes tests for stale cache reads, lost cache updates, concurrent cart changes, and payment amount mismatches.

## Scoring Notes

- Anti-pattern resistance must be 2 for this case to pass.
- Score correctness reasoning based on whether payment invariants remain protected by authoritative storage.
