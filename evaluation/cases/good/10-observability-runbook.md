# Case: Observability Runbook

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this operational plan:

We operate a notification pipeline: API requests enqueue messages, workers send email and push notifications, and delivery receipts update a status table. The architecture is mostly built, but incidents are hard to diagnose. The pipeline handles 5,000 notification requests per second at peak, must avoid duplicate sends for billing and compliance messages, and has a user-visible delivery-status SLO of 99% within five minutes. Ask what observability, alerts, dashboards, runbooks, and correctness checks are needed before launch.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill treats operations as first-class design output.

## Weak Answer Patterns

- Gives generic advice to add logs and metrics without naming signals.
- Ignores queue lag, duplicate sends, provider throttling, dead letters, retry storms, and status drift.
- Does not separate user-visible delivery correctness from provider latency, retry backlog, and status-table drift.
- Skips operator actions and incident thresholds.

## Strong Answer Signals

- Defines metrics for enqueue rate, worker throughput, queue age, retry count, provider error rate, dedupe hits, and status update lag.
- Frames workload by request rate, queue depth, provider quota, retry volume, and five-minute delivery-status SLO.
- Separates delivery attempts, provider acknowledgements, receipts, and user-visible status correctness.
- Discusses trade-offs between aggressive retries, provider throttling, duplicate sends, and delayed delivery.
- Adds traces or correlation IDs from API request through provider callback.
- Proposes alerts tied to user impact and runbooks with concrete mitigation actions.
- Includes dashboards, dead-letter inspection, replay safety, and reconciliation jobs.

## Scoring Notes

- Score workload framing based on whether the answer quantifies queue load, provider limits, retry volume, and delivery-status SLOs.
- Score correctness reasoning based on whether duplicate-send prevention and status-table reconciliation are observable and testable.
- Score verification value based on whether the answer produces actionable checks and incident drills.
- Score failure-mode coverage based on observable symptoms and operator response paths.
