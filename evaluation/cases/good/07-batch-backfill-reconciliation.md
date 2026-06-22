# Case: Batch Backfill Reconciliation

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this migration plan:

We have three years of order events in Kafka and S3. A new fraud model needs a derived customer-risk table built from historical events and then kept current from the live stream. The team plans to run a Spark backfill once, write directly into PostgreSQL, then start the streaming consumer. Review the plan for correctness, replay safety, and verification.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill handles batch plus streaming derived data and reconciliation.

## Weak Answer Patterns

- Treats the backfill as a one-time script without idempotent output or checkpointing.
- Ignores duplicate events, late events, schema drift, replay windows, and cutover ordering.
- Skips reconciliation between batch output, stream output, and source events.

## Strong Answer Signals

- Defines a deterministic derived table keyed by customer and model version.
- Uses idempotent writes, checkpoints, replayable jobs, and explicit cutover watermarks.
- Handles late data, schema versions, joins, and backfill reruns without double counting.
- Proposes row-count checks, aggregate reconciliation, sample audits, and shadow reads before cutover.

## Scoring Notes

- Score correctness reasoning based on whether replay and rerun behavior are safe.
- Score verification value based on reconciliation between source events, batch output, and stream-maintained state.
