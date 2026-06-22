# Full DDIA Coding A/B Run

## Run Metadata

- Date: 2026-06-22
- Commit: 30911d6
- Model: gpt-5.3-codex-spark
- Reasoning effort: high
- Cases: 18
- Shuffle seed: `ddia-coding-ab-2026-06-22`
- Answer runner: `codex exec --ephemeral --ignore-user-config --ignore-rules --sandbox read-only`
- Judge runner: same model and settings, blind to control/treatment mapping

## Aggregate Result

- Control total: 151/226 (66.8%)
- Treatment total: 202/226 (89.4%)
- Absolute lift: +51/226 (22.6% points)
- Control passes: 4/18
- Treatment passes: 15/18
- Score winners: treatment 15, control 2, tie 1
- Blind judge winner labels after reveal: treatment 15, control 2, tie 1

## Category Breakdown

| Category | Cases | Control | Treatment | Lift | Control passes | Treatment passes | Treatment wins | Control wins | Ties |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| good | 4 | 43/48 | 43/48 | +0 | 3 | 4 | 2 | 1 | 1 |
| bad | 9 | 64/108 | 102/108 | +38 | 0 | 9 | 9 | 0 | 0 |
| adversarial | 5 | 44/70 | 57/70 | +13 | 1 | 2 | 4 | 1 | 0 |

## Case Scores

| Case | Category | Control | Treatment | Lift | Pass/fail change | Score winner | Judge winner |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| checkout-cache-as-truth | bad | 5/12 | 10/12 | +5 | control fail -> treatment pass | treatment | treatment |
| elasticsearch-authorization-trap | adversarial | 7/14 | 11/14 | +4 | both fail | treatment | treatment |
| good-cache-aside-product-preview | good | 11/12 | 12/12 | +1 | both pass | treatment | treatment |
| good-expand-contract-schema-rollout | good | 9/12 | 10/12 | +1 | control fail -> treatment pass | treatment | treatment |
| good-outbox-relay-idempotent-consumer | good | 12/12 | 10/12 | -2 | both pass | control | control |
| good-replica-session-token-routing | good | 11/12 | 11/12 | +0 | both pass | tie | tie |
| hot-partition-tenant-counter | bad | 8/12 | 11/12 | +3 | control fail -> treatment pass | treatment | treatment |
| kafka-total-ordering-trap | adversarial | 10/14 | 13/14 | +3 | control fail -> treatment pass | treatment | treatment |
| missing-reconciliation-observability | bad | 8/12 | 11/12 | +3 | control fail -> treatment pass | treatment | treatment |
| multi-region-last-write-wins-profile | adversarial | 6/14 | 9/14 | +3 | both fail | treatment | treatment |
| order-outbox-missing | bad | 8/12 | 12/12 | +4 | control fail -> treatment pass | treatment | treatment |
| payment-exactly-once-trap | adversarial | 8/14 | 13/14 | +5 | control fail -> treatment pass | treatment | treatment |
| profile-replica-lag | bad | 8/12 | 10/12 | +2 | control fail -> treatment pass | treatment | treatment |
| redis-distributed-lock-money-transfer | adversarial | 13/14 | 11/14 | -2 | control pass -> treatment fail | control | control |
| retry-storm-no-dlq | bad | 7/12 | 12/12 | +5 | control fail -> treatment pass | treatment | treatment |
| schema-migration-breaking-reader | bad | 7/12 | 12/12 | +5 | control fail -> treatment pass | treatment | treatment |
| seat-booking-write-skew | bad | 4/12 | 12/12 | +8 | control fail -> treatment pass | treatment | treatment |
| stream-consumer-non-idempotent | bad | 9/12 | 12/12 | +3 | control fail -> treatment pass | treatment | treatment |

## Artifacts

Each case directory under `cases/` contains:

- `control-response.md`
- `treatment-response.md`
- `blind-judge-raw.json`
- `blind-judge-result.json`
- `mapping.txt`
- `case-summary.json`
- rendered answer prompts and the blind judge prompt
- Codex command logs

## Limitations

- One model only.
- One sample per arm per case.
- The same model family generated and judged the answers.
- The judge was blind to control/treatment mapping, but not independent of the answer model.
- No Java compilation was required; the judge scored patch quality from code snippets and explanation.
