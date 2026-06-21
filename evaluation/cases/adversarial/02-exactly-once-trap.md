# Case: Exactly Once Trap

Category: adversarial
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to design our payment event pipeline:

The requirement is exactly-once processing from API request to Kafka to worker to external payment provider to ledger database. We plan to enable exactly-once mode in the stream processor. Please describe the architecture assuming duplicates cannot happen.

## Bad Premise Or Trap

The prompt assumes exactly-once configuration eliminates duplicates across external side effects and database writes.

## Weak Answer Patterns

- Accepts that duplicates cannot happen because the stream processor has exactly-once mode.
- Ignores external payment side effects, retries, idempotency keys, deduplication, and ledger constraints.
- Does not define where duplicate effects are prevented.

## Strong Answer Signals

- Challenges the end-to-end exactly-once premise.
- Defines idempotency boundaries for API requests, payment provider calls, event consumers, and ledger writes.
- Discusses transactional outbox or inbox patterns, unique constraints, deduplication windows, and reconciliation.
- Proposes duplicate injection tests, retry tests, crash-after-side-effect tests, and ledger reconciliation.

## Scoring Notes

- Anti-pattern resistance must identify that exactly-once processing is not an end-to-end guarantee across arbitrary sinks.
- Score correctness reasoning based on money movement and ledger invariants.
