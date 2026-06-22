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