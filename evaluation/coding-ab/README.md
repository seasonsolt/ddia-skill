# DDIA Coding A/B Evaluation

## Purpose

Compare Java coding-review answers from a control prompt against treatment answers that use ddia-system-design reasoning. The benchmark focuses on whether the answer finds data-system correctness risks in ordinary Java service code and proposes patches that respect source-of-truth, transaction, idempotency, replication, and failure-mode constraints.

## Method

Run each case twice with the same model and context window. One run uses the control instructions and one run uses the treatment instructions. Hide the mapping as Response A and Response B, collect both answers, then score with the blind LLM judge before revealing which answer used the skill.

## Case Set

- evaluation/coding-ab/cases/checkout-cache-as-truth.md
- evaluation/coding-ab/cases/payment-exactly-once-trap.md
- evaluation/coding-ab/cases/order-outbox-missing.md
- evaluation/coding-ab/cases/profile-replica-lag.md
- evaluation/coding-ab/cases/redis-distributed-lock-money-transfer.md

## Limitations

This benchmark checks a small Java coding-review slice. It is useful for regression and directional A/B evidence, but it is not statistical proof.
