# DDIA Skill Usefulness Rubric

Score each response from 0 to 2 on each dimension.

## Dimensions

1. Workload framing: identifies reads, writes, load, latency, data volume, and growth assumptions.
2. Trade-off quality: explains costs rather than naming a tool as automatically correct.
3. Failure-mode coverage: names concrete ways the design can fail under concurrency, faults, lag, overload, or operations.
4. Correctness reasoning: discusses isolation, consistency, idempotency, ordering, or reconciliation where relevant.
5. Verification value: gives tests, metrics, experiments, or runbook checks that can validate the design.

## Score Anchors

- 0: Missing, materially incorrect, or too generic to help evaluate the design.
- 1: Partially addresses the dimension but leaves important assumptions, risks, or evidence gaps.
- 2: Clearly addresses the dimension with concrete, relevant details tied to the proposed design.

## Passing Standard

A prompt passes when the response scores at least 8 out of 10 and has no dimension scored 0.

The skill passes the evaluation suite when all five prompts pass.
