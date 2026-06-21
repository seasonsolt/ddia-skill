# Process Compliance Rubric

Score only observable behavior. If hidden tool or skill usage is not visible, score based on the response and available transcript evidence.

## Dimensions

1. Skill material usage
   - 0: No sign that the DDIA skill workflow or references shaped the answer.
   - 1: Uses some DDIA language but does not clearly follow the skill workflow.
   - 2: Clearly follows the skill workflow or explicitly uses relevant DDIA reference lenses.
2. Assumption framing
   - 0: Recommends a design before stating assumptions.
   - 1: States assumptions after the recommendation or only partially.
   - 2: Frames workload, correctness, and ownership assumptions before or alongside the recommendation.
3. Missing requirement questions
   - 0: Makes a strong recommendation despite missing critical workload or correctness data.
   - 1: Mentions missing data but still overcommits.
   - 2: Asks or lists the missing requirements and scopes the recommendation accordingly.
4. Response structure
   - 0: Response is unstructured or hard to audit.
   - 1: Some structure exists, but key DDIA sections are missing.
   - 2: Uses the DDIA response shape or an equivalent structure covering assumptions, recommendation, trade-offs, failure modes, correctness, operations, and tests.
5. Verification conversion
   - 0: Does not convert claims into validation.
   - 1: Gives generic validation suggestions.
   - 2: Converts design claims into concrete tests, metrics, experiments, or runbook checks.

## Use

Process compliance is scored separately from answer quality. A response can be useful but still reveal weak process discipline.
