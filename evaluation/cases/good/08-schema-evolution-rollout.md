# Case: Schema Evolution Rollout

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this database migration:

The user profile service stores `full_name` in one column. We need separate `given_name` and `family_name` columns for search and compliance exports. Multiple services read the table, mobile clients can lag by weeks, and the table has 600 million rows. The proposal is to add the two columns, deploy code that writes only the new columns, run an online backfill, then drop `full_name`. Review the rollout.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill covers expand-contract migration and compatibility.

## Weak Answer Patterns

- Drops or stops writing the old column before all readers are compatible.
- Ignores mobile/client version lag, long-running backfill load, rollback, and data quality checks.
- Treats backfill as purely mechanical without ambiguity in name parsing.

## Strong Answer Signals

- Proposes expand-contract rollout with dual writes or derived reads during compatibility window.
- Separates schema change, code rollout, backfill, validation, read switch, and cleanup.
- Addresses online migration throttling, rollback, idempotent backfill, and ambiguous names.
- Proposes metrics for null rate, parse failures, reader compatibility, and export correctness.

## Scoring Notes

- Score failure-mode coverage based on compatibility, rollback, and online migration risks.
- Score maintainability based on whether cleanup happens only after measured reader migration.
