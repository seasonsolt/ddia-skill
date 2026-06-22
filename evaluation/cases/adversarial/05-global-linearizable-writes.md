# Case: Global Linearizable Writes

Category: adversarial
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to design our account settings service:

Users are global. We want every region to accept writes locally, every read in every region to immediately reflect the latest write, and p99 latency under 50 ms worldwide. The team proposes active-active multi-region writes with conflict-free replication and says users should never see stale data. Describe the architecture assuming all three requirements are mandatory.

## Bad Premise Or Trap

The prompt asks for local writes, global immediate consistency, and low worldwide latency at the same time without acknowledging consensus and latency trade-offs.

## Weak Answer Patterns

- Accepts all requirements without discussing quorum, leader placement, clock/replication limits, or conflict resolution.
- Claims active-active replication gives immediate global consistency.
- Ignores stale reads, write conflicts, failover behavior, and regional partitions.

## Strong Answer Signals

- Challenges the premise and explains the trade-off between local latency, availability, and linearizable global state.
- Offers explicit choices such as single-region leader, regional ownership, quorum writes, or relaxed consistency for selected fields.
- Separates fields that require strict consistency from fields that can tolerate convergence.
- Proposes Jepsen-style partition tests, conflict injection, stale-read checks, failover drills, and latency SLO validation.

## Scoring Notes

- Anti-pattern resistance must reject the idea that conflict-free active-active writes provide immediate global linearizability.
- Score trade-off quality based on explicit consistency and latency choices.
