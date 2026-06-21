# Case: Database Choice

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to compare relational, document, and graph databases for a team collaboration product with users, organizations, projects, tasks, comments, mentions, permissions, and audit history. Give a recommendation and explain which assumptions would change it.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill chooses storage by data model, access pattern, and invariants rather than by popularity.

## Weak Answer Patterns

- Recommends one database category as universally best.
- Ignores permissions, audit history, many-to-many relationships, and schema evolution.
- Does not explain what assumptions would change the recommendation.

## Strong Answer Signals

- Compares relational joins and constraints, document locality, and graph traversal needs.
- Explains why relational storage is likely a strong source-of-truth default for permissions and auditability.
- Names conditions that would favor document or graph models.
- Gives concrete migration, query, and integrity tests.

## Scoring Notes

- Score trade-off quality based on whether the answer explains costs of joins, denormalization, traversal, schema changes, and operational complexity.
- Score correctness reasoning based on permission and audit-history invariants.
