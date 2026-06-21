# Case: Order Consistency

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this design:

We are building an order service. Users can place orders, cancel orders, and view order history. Inventory is stored in another service. The proposal uses a relational database for orders, Redis for order status caching, and asynchronous events to update inventory. Review the design for consistency risks, failure modes, and verification steps.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill treats Redis and asynchronous inventory events as derived paths rather than authoritative state.

## Weak Answer Patterns

- Treats Redis order status as authoritative without discussing cache invalidation or rebuilds.
- Ignores outbox, idempotency, retries, duplicate events, and reconciliation.
- Skips user-visible order and inventory invariants.

## Strong Answer Signals

- Names the order database as the source of truth for order state.
- Discusses transactional outbox, idempotent consumers, event ordering, retries, and reconciliation.
- Separates user-visible correctness from cache freshness.
- Proposes concrete failure injection, lag metrics, and consistency checks.

## Scoring Notes

- Score workload framing based on whether the answer asks for order volume, cancellation frequency, inventory coupling, latency goals, and acceptable stale reads.
- Score correctness reasoning based on whether the answer protects order state transitions and inventory reservation semantics.
