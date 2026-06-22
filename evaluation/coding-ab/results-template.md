# DDIA Coding A/B Results Template

## Run Metadata

- Evaluator:
- Date:
- Model:
- Skill version:

## Hidden Mapping

- Response A:
- Response B:

## Case Scores

Use the blind judge rubric: base dimensions are worth up to 12 points. Adversarial coding cases add anti-pattern resistance for a maximum score of 14. Pass criteria are governed by evaluation/coding-ab/blind-llm-judge.md.

| Case | Category | Control score | Treatment score | Lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| checkout-cache-as-truth | bad |  |  |  |  |  |
| payment-exactly-once-trap | adversarial |  |  |  |  |  |
| order-outbox-missing | bad |  |  |  |  |  |
| profile-replica-lag | bad |  |  |  |  |  |
| redis-distributed-lock-money-transfer | adversarial |  |  |  |  |  |

## Dimension Differences

Record Java patch correctness, source-of-truth reasoning, failure-mode coverage, transaction and idempotency reasoning, verification value, and anti-pattern resistance differences.

## Response Archive

Preserve Response A and Response B for every coding case.

## Overall Decision

- Total control score:
- Total treatment score:
- Total lift:
- Limitations:
