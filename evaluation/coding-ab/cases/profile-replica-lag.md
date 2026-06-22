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
