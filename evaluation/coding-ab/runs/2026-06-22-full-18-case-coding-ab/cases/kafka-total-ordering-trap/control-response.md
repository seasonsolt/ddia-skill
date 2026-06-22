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