# Case: Event Pipeline

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to design a clickstream ingestion pipeline. The product needs near-real-time dashboards, replayable raw events, late event handling, and daily batch reports. Recommend an architecture and explain trade-offs, failure modes, and correctness checks.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill handles stream and batch requirements together instead of optimizing for dashboards alone.

## Weak Answer Patterns

- Builds only a real-time dashboard path and omits replayable raw storage.
- Ignores event time, late events, duplicates, backfills, and consumer lag.
- Treats exactly-once processing as a magic platform feature.

## Strong Answer Signals

- Separates durable raw event storage, stream processing, serving views, and daily batch outputs.
- Defines event time, watermarks, late event policy, replay strategy, idempotent sinks, and reconciliation.
- Explains latency versus correctness trade-offs for dashboards and reports.

## Scoring Notes

- Score workload framing based on event volume, burstiness, retention, dashboard latency, and report accuracy requirements.
- Score verification value based on replay tests, duplicate-event tests, late-event tests, consumer lag metrics, and report reconciliation.
