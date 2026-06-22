# Case: Observability Runbook

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this operational plan:

We operate a notification pipeline: API requests enqueue messages, workers send email and push notifications, and delivery receipts update a status table. The architecture is mostly built, but incidents are hard to diagnose. Ask what observability, alerts, dashboards, and runbooks are needed before launch.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill treats operations as first-class design output.

## Weak Answer Patterns

- Gives generic advice to add logs and metrics without naming signals.
- Ignores queue lag, duplicate sends, provider throttling, dead letters, retry storms, and status drift.
- Skips operator actions and incident thresholds.

## Strong Answer Signals

- Defines metrics for enqueue rate, worker throughput, queue age, retry count, provider error rate, dedupe hits, and status update lag.
- Adds traces or correlation IDs from API request through provider callback.
- Proposes alerts tied to user impact and runbooks with concrete mitigation actions.
- Includes dashboards, dead-letter inspection, replay safety, and reconciliation jobs.

## Scoring Notes

- Score verification value based on whether the answer produces actionable checks and incident drills.
- Score failure-mode coverage based on observable symptoms and operator response paths.
