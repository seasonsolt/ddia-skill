# Case: Vague Startup Architecture

Category: bad
Pass mode: diagnostic-only
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to choose our database:

We are building a new B2B SaaS product. We might need users, teams, permissions, notifications, audit logs, analytics, and maybe AI features later. Should we use PostgreSQL, MongoDB, Cassandra, Neo4j, or DynamoDB? Please give one definitive choice so we can start quickly.

## Bad Premise Or Trap

The prompt asks for a definitive database choice while omitting workload, data model, correctness, query, and operational requirements.

## Weak Answer Patterns

- Gives a confident single database choice without scoping assumptions.
- Chooses based on trend, scale mythology, or future AI features.
- Ignores permissions, auditability, transactions, query shape, and operational maturity.

## Strong Answer Signals

- Refuses an overconfident recommendation and states missing requirements.
- Gives a scoped default such as PostgreSQL for early relational SaaS needs while explaining assumptions.
- Names the requirements that would change the choice.
- Proposes lightweight experiments and schema/query spikes before committing.

## Scoring Notes

- Diagnostic-only because early product prompts may be intentionally vague.
- Anti-pattern resistance should reward scoped recommendations, not refusal to help.
