# Case: Derived Data

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review a search indexing design:

PostgreSQL is the source of truth. A background worker sends changes to Elasticsearch. Product wants search results to affect billing workflow decisions. Review the correctness risks and propose a safer architecture.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill treats Elasticsearch as derived state and keeps billing decisions anchored in authoritative data.

## Weak Answer Patterns

- Lets Elasticsearch directly control billing decisions.
- Ignores index lag, missed updates, partial failures, rebuilds, and divergence.
- Does not define source-of-truth boundaries or reconciliation.

## Strong Answer Signals

- Keeps billing decisions in PostgreSQL or another authoritative transactional path.
- Treats Elasticsearch as derived search state with lag metrics, rebuilds, and divergence detection.
- Proposes reconciliation and clear unsafe states when search is stale.

## Scoring Notes

- Score correctness reasoning based on whether business-critical decisions avoid stale derived data.
- Score failure-mode coverage based on index lag, dropped updates, duplicate updates, rebuilds, and stale reads.
