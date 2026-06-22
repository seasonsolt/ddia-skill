# DDIA Coding A/B Benchmark Design

## Purpose

The current A/B pilot measures whether `ddia-system-design` improves architecture prose. The coding A/B benchmark should test a stricter claim: the skill helps an agent make better backend implementation decisions when patching unsafe Java code.

The benchmark will give the same flawed Java snippet to a control response and a treatment response. The control response uses general backend knowledge. The treatment response uses `ddia-system-design`. A blinded LLM judge scores the patched snippets with a DDIA-derived rubric.

## Target

The target user is a backend engineer or architect who wants evidence that the skill changes concrete engineering behavior, not only explanation quality.

The benchmark should show whether the treatment response is better at:

- keeping authoritative data in the right source of truth
- placing transaction boundaries around correctness-sensitive state
- adding idempotency and retry safety
- avoiding unsafe assumptions about caches, replicas, locks, and stream processors
- translating failure modes into code paths, checks, and operational signals

## Non-Goals

This benchmark does not need to compile or execute Java code. It should use code snippets as evidence of design choices. The LLM judge may penalize code that is too vague to show the intended boundary.

This benchmark is not a replacement for production tests. It is an evaluation harness for skill usefulness.

## Evaluation Shape

Each coding case contains:

- a short product context
- a flawed Java snippet
- the unsafe premise embedded in the code
- patch instructions
- expected strong answer signals
- weak answer patterns
- scoring notes

The model response format is:

```text
## Patched Java
<patched Java snippet>

## Why this fixes the bug
- 5 to 8 bullets
```

The patched Java may use small interfaces and fake repository classes. It should still show the critical boundary clearly. For example, a payment case should show where the idempotency key, ledger uniqueness, provider request ID, and reconciliation path live.

## A/B Protocol

1. Select the same coding case for both arms.
2. Generate the control response with instructions that forbid using or referencing `ddia-system-design`.
3. Generate the treatment response with instructions that require using `ddia-system-design`.
4. Randomize the order as `Response A` and `Response B`.
5. Give the judge the case, the flawed snippet, the two anonymized patches, and the scoring rubric.
6. The judge emits structured JSON scores and short rationale.
7. Reveal mapping only after scores are recorded.
8. Compute treatment lift, pass/fail changes, and regression notes.

## Initial Java Patch Cases

### checkout-cache-as-truth

The flawed snippet reads the final checkout amount from Redis because it is fast and highly available, then updates PostgreSQL later through an async worker.

Strong treatment behavior:

- payment amount comes from transactional database state or authoritative line items
- Redis remains a derived cache for previews
- checkout blocks, refreshes, or recomputes when cache and database disagree
- the patch adds mismatch metrics and stale-cache tests in the explanation

Primary DDIA topics: storage and retrieval, transactions, derived data and correctness.

### payment-exactly-once-trap

The flawed snippet assumes Kafka or stream-processor exactly-once mode prevents duplicate charges across an API, Kafka, a worker, an external payment provider, and a ledger table.

Strong treatment behavior:

- rejects end-to-end exactly-once as a blanket guarantee
- adds API idempotency keys, provider idempotency IDs, ledger unique constraints, and retry-safe state transitions
- handles provider timeout with unknown outcome
- explains reconciliation between provider state and ledger state

Primary DDIA topics: transactions, distributed faults, stream processing.

### order-outbox-missing

The flawed snippet inserts an order row and then publishes `OrderCreated` outside the transaction. A crash after commit can lose the event.

Strong treatment behavior:

- writes the order and outbox event in one transaction
- lets a retryable publisher drain the outbox
- makes consumers idempotent
- adds checks for outbox age, duplicate events, and reconciliation

Primary DDIA topics: transactions, stream processing, derived data and correctness.

### profile-replica-lag

The flawed snippet writes profile settings to the leader but immediately reads from a random replica for the response.

Strong treatment behavior:

- preserves read-your-writes for immediate post-write reads
- uses leader read, session stickiness, or LSN/version-aware routing
- keeps stale-tolerant reads on replicas when safe
- adds stale-read and monotonic-read checks

Primary DDIA topics: replication, consistency, distributed faults.

### redis-distributed-lock-money-transfer

The flawed snippet obtains Redis locks with a short TTL around two HTTP updates to account services and treats that as a correctness guarantee for money transfer.

Strong treatment behavior:

- rejects Redis locks alone as sufficient for financial correctness
- moves the invariant into an authoritative ledger, serializable transaction, or consensus-backed boundary
- uses idempotency keys and fencing where a lease remains relevant
- explains partial failure, lock expiry, process pause, and duplicate transfer tests

Primary DDIA topics: transactions, distributed faults, consistency and consensus.

## LLM Judge Rubric

Each response receives 0, 1, or 2 points per dimension.

- Correctness invariant: Does the patch protect the business invariant?
- Source-of-truth boundary: Does the patch keep authoritative decisions out of derived state?
- Failure-mode handling: Does the patch handle the specific crash, retry, timeout, lag, or partial failure?
- Idempotency and retry safety: Does the patch make repeated requests or messages safe?
- Operational verification: Does the explanation name metrics, tests, reconciliation, or runbook checks?
- Java patch quality: Does the snippet show concrete methods and boundaries rather than vague pseudocode?

Adversarial cases add:

- Anti-pattern resistance: Does the patch directly reject the unsafe premise embedded in the original code?

Good and bad coding cases pass at 10 out of 12 with no zero dimensions. Adversarial coding cases pass at 12 out of 14, require anti-pattern resistance of 2, and allow no zero dimensions.

## Judge Output

The judge should return JSON:

```json
{
  "case_id": "checkout-cache-as-truth",
  "response_a": {
    "scores": {
      "correctness_invariant": 0,
      "source_of_truth_boundary": 0,
      "failure_mode_handling": 0,
      "idempotency_retry_safety": 0,
      "operational_verification": 0,
      "java_patch_quality": 0,
      "anti_pattern_resistance": null
    },
    "total": 0,
    "pass": false,
    "rationale": "Short scoring rationale."
  },
  "response_b": {
    "scores": {
      "correctness_invariant": 0,
      "source_of_truth_boundary": 0,
      "failure_mode_handling": 0,
      "idempotency_retry_safety": 0,
      "operational_verification": 0,
      "java_patch_quality": 0,
      "anti_pattern_resistance": null
    },
    "total": 0,
    "pass": false,
    "rationale": "Short scoring rationale."
  }
}
```

The deterministic checker should validate the JSON shape, score bounds, totals, pass rules, and that the hidden mapping is absent from judge input.

## Credibility Controls

The benchmark should avoid making the treatment arm win through prompt formatting alone.

- Use the same flawed code and patch request for both arms.
- Give both arms the same response format.
- Hide control/treatment mapping from the judge.
- Randomize A/B order per case.
- Preserve raw responses and judge JSON.
- Run at least three repeated trials for the pilot cases before claiming more than directional evidence.
- Document the model, date, skill version, judge prompt, and randomization seed.

## Expected Result

If the skill is useful, treatment patches should more often move correctness into code boundaries rather than prose. The clearest lift should appear in cache-as-truth, exactly-once, missing-outbox, replica-lag, and distributed-lock cases because those prompts encode common DDIA anti-patterns.

The README can then present the coding A/B results as stronger evidence than prose-only scoring, while still labeling the first run as pilot evidence until repeated blinded runs exist.
