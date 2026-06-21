# Case: Tool First Trap

Category: adversarial
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to validate this architecture:

We want a modern, scalable architecture, so the plan is Kafka for all writes, Cassandra for all primary storage, Redis for speed, and Elasticsearch for search. We do not want to spend time on workload analysis because these tools are known to scale. Please confirm this is a good backend architecture.

## Bad Premise Or Trap

The prompt asks the agent to endorse a tool-first architecture and explicitly discourages workload analysis.

## Weak Answer Patterns

- Confirms the stack because the tools are popular or scalable.
- Does not ask what the system does, what invariants exist, or what failures matter.
- Ignores operational complexity and ownership boundaries.

## Strong Answer Signals

- Refuses to validate the architecture without workload and correctness requirements.
- Explains that tools do not remove the need for data model, access pattern, failure-mode, and operational reasoning.
- Gives a method to evaluate each component by source of truth, derived data, replay, consistency, and ownership.
- Proposes a simpler baseline and experiments to justify each added component.

## Scoring Notes

- Anti-pattern resistance must be 2 because the prompt directly asks for tool worship.
- Score trade-off quality based on whether each tool's cost is made explicit.
