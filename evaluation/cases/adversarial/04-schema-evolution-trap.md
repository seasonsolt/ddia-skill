# Case: Schema Evolution Trap

Category: adversarial
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to review this event schema change:

We have twelve services consuming `OrderCreated` events. Product needs to rename `user_id` to `buyer_id`, remove `shipping_address`, and change `total_cents` to a decimal string this week. The platform team says JSON is flexible, so producers can deploy first and consumers can catch up later.

## Bad Premise Or Trap

The prompt treats JSON flexibility as compatibility and ignores old consumers, replayed events, and rolling deploys.

## Weak Answer Patterns

- Accepts producer-first deployment because JSON is flexible.
- Ignores old consumers, stored events, replay, optional fields, versioning, and compatibility tests.
- Does not define a rollout sequence.

## Strong Answer Signals

- Challenges the idea that JSON alone provides schema evolution safety.
- Proposes backward-compatible additive changes, dual-write or dual-read periods, schema contracts, consumer readiness, and replay compatibility.
- Discusses stored old events and rolling deployments.
- Proposes contract tests, replay tests, canaries, and consumer lag monitoring.

## Scoring Notes

- Anti-pattern resistance must identify producer-first breaking changes as unsafe.
- Score verification value based on concrete compatibility and replay tests.
