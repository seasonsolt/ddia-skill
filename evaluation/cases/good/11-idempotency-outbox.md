# Case: Idempotency Outbox

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this API and eventing design:

A subscription service receives `CreateSubscription` requests from clients. It writes a subscription row, charges the customer through a payment provider, and publishes a `SubscriptionCreated` event for downstream systems. Clients retry on timeout, workers can crash, and the payment provider can return success after our request times out. Review the design for idempotency and failure windows.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill can design idempotent APIs and outbox/inbox boundaries.

## Weak Answer Patterns

- Relies on client retries being rare or provider calls being reliable.
- Publishes events outside the database transaction without discussing crash windows.
- Ignores idempotency keys, unique constraints, provider request IDs, and duplicate downstream consumption.

## Strong Answer Signals

- Requires client idempotency keys, unique constraints, and stable provider idempotency identifiers.
- Defines transactional state changes and an outbox for publishing subscription events.
- Discusses inbox/deduplication for downstream consumers and reconciliation with provider state.
- Proposes timeout, retry, crash-after-charge, duplicate-request, and duplicate-event tests.

## Scoring Notes

- Score correctness reasoning based on duplicate prevention across API, payment, database, and event boundaries.
- Score failure-mode coverage based on explicit crash windows and retry behavior.
