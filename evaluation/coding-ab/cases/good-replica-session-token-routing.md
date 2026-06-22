# Coding Case: good-replica-session-token-routing

Case ID: good-replica-session-token-routing
Category: good
Language: Java
Primary DDIA topics: replicated reads, user-visible freshness, routing

## Scenario

A profile service returns the saved profile after an update and includes a version marker for the client to pass on later profile reads. The team asks whether this should be simplified by sending every profile read to the main database.

## Flawed Java

```java
public final class ProfileService {
    private final ProfilePrimaryRepository primary;
    private final ProfileReplicaRepository replica;

    public UpdatedProfile updateDisplayName(UUID userId, String displayName) {
        Profile saved = primary.updateDisplayNameReturningRow(userId, displayName);
        return new UpdatedProfile(saved, saved.version());
    }

    public Profile readProfile(UUID userId, long minVersion) {
        Optional<Profile> fromReplica = replica.findByIdAtLeastVersion(userId, minVersion);
        return fromReplica.orElseGet(() -> primary.findById(userId));
    }
}
```

## Task

Review the code, assess whether a Java-oriented patch is needed, and justify the operational checks that would protect this design.

## Expected DDIA Reasoning

The answer should recognize that returning the primary write result plus using a version or LSN token on later reads protects read-your-writes without routing every read to the primary. The replica can still serve reads that have caught up, while the primary fallback handles sessions that require a newer version.

## Strong Patch Signals

- Keeps bounded primary fallback instead of removing replicas globally.
- Uses version/LSN routing or session tokens to avoid stale reads.
- Adds replica-lag metrics, fallback-rate metrics, and tests that simulate lag.

## Weak Patch Patterns

- Removes all replica reads even when only session freshness needs primary fallback.
- Adds fixed sleeps before reading from the replica.
- Claims eventual consistency is always fine for the post-update user session.

## Scoring Notes

- Award high scores for preserving scale-out reads while making the freshness guarantee explicit.
- Penalize answers that ignore the version token or treat primary routing as an all-or-nothing choice.
