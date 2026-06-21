# Answer Quality Rubric

Score each response from 0 to 2 on each dimension.

## Dimensions

1. Workload framing
   - 0: Missing, materially wrong, or generic.
   - 1: Names some workload factors but misses important reads, writes, data volume, latency, growth, or skew.
   - 2: Frames the concrete workload shape and ties it to the recommendation.
2. Trade-off quality
   - 0: Recommends tools or patterns as automatically correct.
   - 1: Mentions trade-offs but leaves costs vague.
   - 2: Explains the cost of each major choice in latency, availability, correctness, complexity, or operations.
3. Failure-mode coverage
   - 0: Does not name relevant failure modes.
   - 1: Names generic failures without tying them to the design.
   - 2: Names concrete failures under concurrency, faults, lag, overload, replay, skew, or operations.
4. Correctness reasoning
   - 0: Ignores invariants, consistency, ordering, isolation, idempotency, or reconciliation where relevant.
   - 1: Mentions correctness concepts but does not connect them to user-visible behavior.
   - 2: Explains the required guarantees and how the design preserves or weakens them.
5. Verification value
   - 0: Gives no useful tests, metrics, experiments, or runbook checks.
   - 1: Gives partial verification guidance that is not directly falsifiable.
   - 2: Gives concrete tests, metrics, experiments, or operational checks that can disprove the recommendation.
6. Anti-pattern resistance
   - 0: Accepts a bad premise or optimizes around it without challenge.
   - 1: Partially challenges the premise but still leaves the unsafe design path open.
   - 2: Clearly identifies the bad premise and redirects to safer workload, correctness, or ownership reasoning.

## Passing Standards

- Good cases pass at 8 out of 10 with no dimension scored 0. Anti-pattern resistance is not scored for good cases.
- Bad and adversarial cases pass at 10 out of 12 with no dimension scored 0.
- Bad and adversarial cases require Anti-pattern resistance to be scored 2.
- The whole benchmark passes only when every must-pass case passes.
- Diagnostic-only cases do not block the whole benchmark, but their scores and failure notes must be recorded.
