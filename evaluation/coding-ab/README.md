# DDIA Coding A/B Evaluation

## Purpose

Compare Java coding-review answers from a control prompt against treatment answers that use ddia-system-design reasoning. The benchmark focuses on whether the answer finds data-system correctness risks in ordinary Java service code and proposes patches that respect source-of-truth, transaction, idempotency, replication, and failure-mode constraints.

## Method

Run each case twice with the same model and context window. One run uses the control instructions and one run uses the treatment instructions. Hide the mapping as Response A and Response B, collect both answers, then score with the blind LLM judge before revealing which answer used the skill.

## Case Set

The expanded coding suite has 18 cases:

- 4 good cases that check whether the skill avoids false positives and over-design.
- 9 bad cases that check ordinary implementation bug detection.
- 5 adversarial cases that check unsafe-premise resistance.

The full topic mapping is in [evaluation/coding-ab/coverage-matrix.md](coverage-matrix.md).

- evaluation/coding-ab/cases/good-cache-aside-product-preview.md
- evaluation/coding-ab/cases/good-outbox-relay-idempotent-consumer.md
- evaluation/coding-ab/cases/good-replica-session-token-routing.md
- evaluation/coding-ab/cases/good-expand-contract-schema-rollout.md
- evaluation/coding-ab/cases/checkout-cache-as-truth.md
- evaluation/coding-ab/cases/order-outbox-missing.md
- evaluation/coding-ab/cases/profile-replica-lag.md
- evaluation/coding-ab/cases/seat-booking-write-skew.md
- evaluation/coding-ab/cases/schema-migration-breaking-reader.md
- evaluation/coding-ab/cases/stream-consumer-non-idempotent.md
- evaluation/coding-ab/cases/hot-partition-tenant-counter.md
- evaluation/coding-ab/cases/retry-storm-no-dlq.md
- evaluation/coding-ab/cases/missing-reconciliation-observability.md
- evaluation/coding-ab/cases/payment-exactly-once-trap.md
- evaluation/coding-ab/cases/redis-distributed-lock-money-transfer.md
- evaluation/coding-ab/cases/multi-region-last-write-wins-profile.md
- evaluation/coding-ab/cases/elasticsearch-authorization-trap.md
- evaluation/coding-ab/cases/kafka-total-ordering-trap.md

## Limitations

This benchmark checks a small Java coding-review slice. It is useful for regression and directional A/B evidence, but it is not statistical proof.
