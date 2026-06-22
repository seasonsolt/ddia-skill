You are the blind LLM judge for a DDIA coding A/B benchmark.

Score Response A and Response B before any mapping is revealed. You must not
guess, mention, or output which response is control or treatment.

Return JSON that matches the provided schema. Do not include Markdown.

Case ID: kafka-total-ordering-trap
Category: adversarial

Important scoring rules:
- For good and bad coding cases, set anti_pattern_resistance to null.
- For adversarial coding cases, score anti_pattern_resistance as 0, 1, or 2.
- Score only observable reasoning and Java patch quality.
- Do not reward a response for naming ddia-system-design.
- Prefer practical correctness over broad conceptual prose.

## Rubric

# Blind LLM Judge

## Scoring Order

Score Response A and Response B before revealing which response is control or treatment. Use only the case text and the submitted answer. Do not reward mention of ddia-system-design by name; reward the observable reasoning and patch quality.

## Dimensions

1. Correctness invariant
2. Source-of-truth boundary
3. Failure-mode handling
4. Idempotency and retry safety
5. Operational verification
6. Java patch quality
7. Anti-pattern resistance

Base dimensions receive 0, 1, or 2 points.
For good and bad coding cases, anti-pattern resistance is null and the total is out of 12.
For adversarial coding cases, anti-pattern resistance receives 0, 1, or 2 points and the total is out of 14.

- 0 points: missing, incorrect, or actively harmful.
- 1 point: partially addresses the issue but leaves important ambiguity or failure modes.
- 2 points: concrete, correct, and tied to the case's Java patch and DDIA concern.

Good coding cases pass at 10 out of 12 with every base dimension above 0. They should preserve the correct system boundary and avoid unnecessary distributed coordination or durability machinery.
Bad coding cases pass at 10 out of 12 with every base dimension above 0. Adversarial coding cases pass at 12 out of 14 with every dimension above 0 and 2 points in anti-pattern resistance.

## Mapping Reveal

Reveal the mapping only after all dimensions, notes, and pass decisions are recorded. Then record whether the treatment improved, regressed, or tied the control answer and why.


## Full Case, Including Judge-Only Notes

# Coding Case: kafka-total-ordering-trap

Case ID: kafka-total-ordering-trap
Category: adversarial
Language: Java
Primary DDIA topics: stream processing, ordering, idempotency, partitioning

## Scenario

An account service consumes balance-related events from Kafka and stores the last applied sequence on each account. The team asks for a Java patch after seeing occasional skipped or out-of-order account updates during a topic migration.

## Flawed Java

```java
public final class AccountEventConsumer {
    private final AccountRepository accounts;

    public void onEvent(AccountEvent event) {
        Account account = accounts.find(event.accountId());
        if (event.sequence() <= account.lastSequence()) {
            return;
        }
        accounts.save(account.apply(event));
    }
}
```

## Task

Review the consumer and propose a Java-oriented patch. Keep the answer focused on the ordering guarantee the code relies on, how that guarantee should be enforced, and tests for replay, duplicates, and deployment changes.

## Expected DDIA Reasoning

The answer should state that Kafka only orders records within a partition, not globally across a topic. A strong patch must ensure all events for one account use the account ID as the partition key, or move the invariant into a durable conditional sequence check that rejects stale updates and handles gaps without corrupting account state.

## Strong Patch Signals

- Partitions events by account ID or another stable key that maps all account events to the same partition.
- Uses a durable conditional update on account ID and sequence instead of a check-then-save race.
- Handles duplicate delivery, replay from earlier offsets, and sequence gaps explicitly.
- Mentions repartitioning, producer changes, or topic migration as deployment risks that need validation.

## Weak Patch Patterns

- Assumes Kafka provides global ordering across partitions.
- Uses timestamps as the ordering authority for account mutations.
- Ignores repartitioning or producer-key changes during deployment.
- Keeps a non-transactional `find` then `save` sequence check as the only correctness guard.

## Scoring Notes

- This adversarial case tests ordering guarantees and idempotent stream processing.
- Award high scores for patches that combine partition-key discipline with durable idempotency checks.
- Penalize answers that rely on consumer-thread ordering without proving per-account partitioning or storage-level guards.


## Response A

Naturalized version of your request: *Please review this `AccountEventConsumer` for ordering, idempotency, and correctness issues in a distributed Kafka-to-DB pipeline, and give a minimal Java patch with practical tests and operational safeguards.*

## 1) Assumptions and workload shape
- Input stream is **at-least-once** (Kafka can redeliver messages during migration/rebalance/retries).
- Events are per-account and must be applied in strict `sequence` order to produce correct balances.
- You have multiple consumers/threads and topic migration increases duplicate/out-of-order exposure.
- The account row is the immediate consistency surface used by downstream services.

## 2) Core bug and why this is a distributed data problem
The consumer currently has a classic **read-check-write race**:

```java
Account account = accounts.find(...)
if (event.sequence() <= account.lastSequence()) return;
accounts.save(account.apply(event));
```

Even if `lastSequence` is monotonic, this code assumes:
1. events always arrive in order per account (not guaranteed during migration),
2. only one updater touches the same account at once (not guaranteed with consumer scaling/rehash/retries),
3. applying directly after a read is safe (not true under concurrent consumers).

That makes it a distributed correctness issue, not just a Java bug.

## 3) Smallest patch that improves correctness
Enforce ordering with an **atomic conditional update** at the write boundary, keyed on expected previous sequence. Keep replay/duplicates from corrupting state.

```java
public final class AccountEventConsumer {
    private final AccountRepository accounts;
    private final PendingAccountEventRepository pending;

    @Transactional
    public void onEvent(AccountEvent event) {
        long expectedPrevSeq = event.sequence() - 1;

        int updated = accounts.applyIfNextSequence(
            event.accountId(),
            event.sequence(),
            expectedPrevSeq,
            event.deltaAmount()
        );

        if (updated == 1) {
            return; // exactly-on-onece applied (idempotent for replay + ordered)
        }

        long lastSeq = accounts.lastSequence(event.accountId()); // 0 if missing
        if (event.sequence() <= lastSeq) {
            metrics.duplicates.increment();
            return; // duplicate/replayed event
        }

        // out-of-order or gap; do not apply early
        pending.save(event);
        metrics.outOfOrderGap.increment();
    }
}
```

Repository side (one SQL/CAS-style update):

```java
@Modifying
@Query("""
    UPDATE accounts
    SET balance = balance + :delta, last_sequence = :seq
    WHERE account_id = :accountId
      AND last_sequence = :expectedPrevSeq
""")
int applyIfNextSequence(@Param("accountId") long accountId,
                        @Param("seq") long sequence,
                        @Param("expectedPrevSeq") long expectedPrevSeq,
                        @Param("delta") BigDecimal delta);
```

## 4) Consistency and transaction boundaries
- This turns update into a **single atomic conditional write** inside one transaction.
- It enforces per-account ordering as: “event N applies only if N-1 has already been applied.”
- It is idempotent for duplicates when `sequence <= lastSequence` (no state change).
- It prevents bad state from out-of-order events during migration.
- It does **not** solve permanent sequence gaps by itself (that is a retention/replay/deployment issue); gap events must be retried or dead-lettered.

## 5) Deployment / source-of-truth guidance
- Source of truth should remain DB state + immutable event stream, not Kafka offset.
- Ensure partitioning by `accountId` in both source and destination topics to reduce in-order violations.
- Keep migration to one ordered writer per account key for a bounded period (or run a replay worker draining `pending`).
- Add a bounded retry policy for `pending` with DLQ for poison/gap events.

## 6) Failure modes
- Missing intermediate sequence: event waits in `pending` and stalls progression (expected).
- Permanent data loss in source topic before migration replay: pending never resolves; alert required.
- Hot account contention: retry churn and pending queue growth on a single account.
- Multiple application instances: CAS update handles concurrency safely; no partial writes.
- Consumer crash between read/decide/save: no harm due idempotent conditional CAS pattern.

## 7) Operational visibility
Track:
- `account_event_applied_total`
- `account_event_duplicate_total` (sequence <= lastSequence)
- `account_event_pending_total`
- `account_event_pending_age_ms` (oldest pending)
- `pending_dlq_total`
- processing lag per partition + migration lag window

Also monitor DB rows updated=0 by repository method to catch ordering anomalies early.

## 8) Tests
- Unit/integration tests:
  - Duplicate replay: same event twice → one apply only, balance unchanged second time.
  - Out-of-order: send `2` then `1` for same account → `2` rejected to pending, `1` applies, then `2` applies later.
  - Concurrent writers: same account events from parallel threads `1..N` with retries → final balance and `lastSequence = N`.
  - Gap never resolving: pending grows and alert/DLQ path triggers.
  - Migration replay test: mixed streams from old/new topic with duplicates/out-of-order for same account; no skipped balances, no out-of-order corruption.

## Response B

You are asking for a Java patch review of the consumer, focusing on the ordering assumptions it makes, how to enforce them, and what tests to add for replay, duplicates, and topic migration.

### Ordering guarantee (what the code currently relies on)
- It assumes events for an account are consumed in strictly increasing sequence order (`sequence` must be next for that account).
- It also assumes the read (`find`) and write (`save`) sequence is effectively atomic.
- With Kafka topic migration, both assumptions can break (reordering across partitions, duplicates, concurrent consumers), so updates can be skipped incorrectly.

### Recommended Java patch
```java
public final class AccountEventConsumer {
    private final AccountRepository accounts;
    private final OutOfOrderSink outOfOrderSink;
    private static final int CAS_RETRIES = 3;

    public void onEvent(AccountEvent event) {
        for (int attempt = 0; attempt < CAS_RETRIES; attempt++) {
            Account account = accounts.findOrCreate(event.accountId());
            long lastSeq = account.lastSequence();

            if (event.sequence() <= lastSeq) {
                // replay/duplicate: already applied
                return;
            }

            if (event.sequence() != lastSeq + 1) {
                // hard ordering violation (gap or reordering)
                outOfOrderSink.publish(event, account.accountId(), lastSeq);
                return;
            }

            Account updated = account.apply(event);

            // atomic CAS-style update: only writes if last_sequence is still what we read
            int rows = accounts.saveIfUnchanged(updated, lastSeq);
            if (rows == 1) {
                return; // applied exactly once
            }
            // concurrent updater raced; retry read + check once more
        }

        outOfOrderSink.publishRetryExhausted(event);
    }
}
```

```java
public interface AccountRepository {
    Account findOrCreate(String accountId);

    /**
     * @return 1 if row updated, 0 if optimistic write failed (last_sequence changed)
     */
    int saveIfUnchanged(Account account, long expectedLastSequence);
}
```

Example SQL for `saveIfUnchanged` (JPA/native/DSL equivalent is fine):
```sql
UPDATE account
SET balance = ?, last_sequence = ?
WHERE account_id = ? AND last_sequence = ?;
```

### Why this helps
- Prevents silent corruption from out-of-order events by routing them to a dead-letter/retry path instead of silently dropping.
- Ensures idempotence for duplicates/replays (`<= lastSequence`).
- Makes apply atomic under concurrency (`last_sequence = expectedLastSequence` CAS), preventing race losses.

### Deployment/migration controls to enforce ordering
- Keep Kafka partitioning strictly by `accountId` on both old and new topics.
- During migration, do not allow both old/new sources to produce interleaved updates for the same account without dedupe support.
- Keep one consuming code path until backlog catch-up is complete; only then switch source fully.
- Persist metrics:
  - `account.consumer.out_of_order`
  - `account.consumer.replay_duplicate`
  - `account.consumer.cas_retry_exhausted`

### Tests to add

1. Replay + duplicate
- Given `lastSequence=10`, send event `sequence=10` then `sequence=9`; consumer must not call write.
- State unchanged, call count 0 for `saveIfUnchanged`.

2. In-order and duplicate safety
- Given `lastSequence=10`, send event `sequence=11` twice.
- First call updates row once, second call ignored (`<= lastSequence`).

3. Out-of-order/gap during migration
- Given `lastSequence=10`, send event `sequence=12`.
- Consumer publishes to `OutOfOrderSink`, does not call write.

4. Concurrent replay safety (CAS path)
- Two threads deliver competing updates (`11` and `12`) under same account context; only one consistent CAS path succeeds per event.
- Verify eventual correctness (no duplicate apply, no stale overwrite).

5. Migration replay contract test
- Reproduce topic failover/replay with duplicate and reordered batches.
- Assert no balance divergence and final `lastSequence` equals highest contiguous applied sequence.
- Assert any gap/out-of-order events are captured by the ordered-error sink and do not mutate state.
