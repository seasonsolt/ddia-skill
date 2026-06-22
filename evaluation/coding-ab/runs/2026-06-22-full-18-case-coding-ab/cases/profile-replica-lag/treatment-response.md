A cleaner version of your scenario: users can save a new display name, but the service writes to the primary DB and immediately reads from a replica, so the same request can see a stale row because replica lag is expected.

**Bug (and why it’s a distributed data problem)**
- Your source of truth is the primary, but the read after write is served by an asynchronous replica.
- The two calls are a distributed read/write split boundary, not an atomic operation.  
- As soon as replication delay exists, `replica.findById` can return the old profile even though the write has committed.

**Assumptions and workload shape**
- Profile reads dominate, writes are user-driven and intermittent.
- Correctness requirement is at least read-your-writes for the actor making the update.
- Slightly higher write latency is acceptable; permanent sticky reads to primary are not.

**Smallest correctness-improving patch**
- Keep replica reads for normal traffic.
- For this write API only, read back from primary (or write-and-return in one primary call).

```java
public final class ProfileService {
    private final ProfilePrimaryRepository primary;
    private final ProfileReplicaRepository replica;

    public Profile updateDisplayName(UUID userId, String displayName) {
        primary.updateDisplayName(userId, displayName);
        return primary.findById(userId); // source of truth read
    }
}
```

If `updateDisplayName` can return the updated row, use that directly and skip the extra read.

**Transaction boundaries**
- `update` + `read` should stay in a single primary data path, ideally in the same DB transaction/connection scope for read-your-writes semantics.
- Do not mix write-primary and immediate read-replica in the same user request unless you add explicit replication-coordination logic.

**Consistency and correctness implications**
- This guarantees the response for this request is correct.
- It does **not** guarantee zero staleness for other concurrent readers, which is normal with async replicas.
- You should state this in SLAs (e.g., user-facing write responses are strong; cross-request replica freshness is eventual).

**Idempotency**
- Retry behavior should be explicit: repeated identical retries (`same userId + same displayName`) are effectively idempotent.
- Add idempotency handling at API boundary only if clients retry automatically and you need stronger safety against duplicate intent.

**Failure modes**
- Primary write succeeds but primary read fails: return retryable 5xx vs compensating read from replica (may return stale).
- Primary is unavailable while replica is up: don’t silently fall back to replica for this path, or you reintroduce stale visibility.
- Concurrent update races: last write wins unless you use version checks (`updated_at`/version column) if business rules require monotonic updates.

**Operational checks**
- Track primary write latency for this endpoint.
- Track replica lag metrics and read-replica staleness diff checks (primary vs replica profile checksums per sampled user).
- Track count of stale responses for user-facing write calls (must go to zero after this fix).

**Tests**
- Unit test: verify `updateDisplayName` returns updated value after update.
- Integration test with replication lag simulation: force stale replica, ensure write path returns fresh primary value.
- Retry/idempotency test: repeated same request should keep resulting value consistent.
- Chaos test: primary write succeeds, primary read fails, and service returns deterministic error path.