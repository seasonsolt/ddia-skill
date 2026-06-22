You are the blind LLM judge for a DDIA coding A/B benchmark.

Score Response A and Response B before any mapping is revealed. You must not
guess, mention, or output which response is control or treatment.

Return JSON that matches the provided schema. Do not include Markdown.

Case ID: profile-replica-lag
Category: bad

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

# Coding Case: profile-replica-lag

Case ID: profile-replica-lag
Category: bad
Language: Java
Primary DDIA topics: replication lag, read-your-writes, session guarantees, routing

## Scenario

A profile service writes to the primary database and immediately reads from a read replica to return the updated profile. Users intermittently see their old display name after saving.

## Flawed Java

```java
public final class ProfileService {
    private final ProfilePrimaryRepository primary;
    private final ProfileReplicaRepository replica;

    public Profile updateDisplayName(UUID userId, String displayName) {
        primary.updateDisplayName(userId, displayName);
        return replica.findById(userId);
    }
}
```

## Task

Review the code and propose a patch that makes the user-facing response correct without routing every future profile read to the primary forever.

## Expected DDIA Reasoning

The answer should identify a read-your-writes violation caused by replica lag. It should discuss primary reads after writes, session tokens, version checks, bounded staleness, or fallback routing until the replica catches up.

## Strong Patch Signals

- Returns the updated row from the primary write path or reads from primary immediately after the write.
- Tracks a version, timestamp, or session marker so later reads can avoid stale replicas.
- Adds tests that simulate replica lag and verify read-your-writes behavior.

## Weak Patch Patterns

- Adds a fixed sleep before reading the replica.
- Treats eventual consistency as acceptable for the immediate save response without product agreement.
- Invalidates a cache while ignoring the replica read path.

## Scoring Notes

- Award credit for scoped primary routing that protects the session without removing replicas from all traffic.
- Penalize answers that do not name replica lag or read-your-writes.


## Response A

A clearer way to phrase it: The write goes to the primary and then you read immediately from a replica, but replicas can lag, so the response can be stale. The fix is to make the write response read-your-writes-safe with a short, bounded replica recheck (using a version/timestamp), and only fall back to primary if needed.

```java
public final class ProfileService {
    private final ProfilePrimaryRepository primary;
    private final ProfileReplicaRepository replica;
    private static final int MAX_REPLICA_RETRIES = 5;
    private static final long RETRY_DELAY_MS = 40L;

    public ProfileService(ProfilePrimaryRepository primary, ProfileReplicaRepository replica) {
        this.primary = primary;
        this.replica = replica;
    }

    public Profile updateDisplayName(UUID userId, String displayName) {
        // Primary returns the new row (or at least updated metadata like updatedAt/version).
        Profile updated = primary.updateDisplayNameAndReturn(userId, displayName);
        Profile replicaProfile = waitForReplicaToCatchUp(userId, updated.getUpdatedAt());

        // Usually read from replica; primary only for bounded fallback.
        return replicaProfile != null ? replicaProfile : primary.findById(userId);
    }

    private Profile waitForReplicaToCatchUp(UUID userId, Instant expectedUpdatedAt) {
        for (int i = 0; i < MAX_REPLICA_RETRIES; i++) {
            Profile replicaProfile = replica.findById(userId);
            if (replicaProfile != null && !replicaProfile.getUpdatedAt().isBefore(expectedUpdatedAt)) {
                return replicaProfile;
            }

            try {
                Thread.sleep(RETRY_DELAY_MS);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        return null;
    }
}
```

Also update the primary repository contract so it returns the updated profile (or at least row version/timestamp), because without a read marker you can’t tell whether the replica is fresh:

```java
public interface ProfilePrimaryRepository {
    Profile updateDisplayNameAndReturn(UUID userId, String displayName);
    Profile findById(UUID userId);
}
```

This gives correct immediate-response behavior for the save flow without sending all profile reads to primary permanently.

## Response B

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
