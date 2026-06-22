Your request is: “Should we simplify profile reads by always querying the primary DB, and what Java patch plus operational checks would you recommend?”

You should **not** force all reads to primary. Keep the version-aware replica-first read; it is the right optimization for balancing freshness and load. But the current code needs a small hardening patch for production behavior.

### Review verdict
- Main risk: replica exceptions are not handled. A transient replica error now fails the request instead of safely falling back to primary.
- Current logic assumes `findById` always returns a profile object and that callers pass valid inputs.
- No observability: fallback events are invisible, so stale-read behavior can become a silent outage.

### Recommended Java patch
```java
public final class ProfileService {
    private final ProfilePrimaryRepository primary;
    private final ProfileReplicaRepository replica;

    public UpdatedProfile updateDisplayName(UUID userId, String displayName) {
        if (userId == null) {
            throw new IllegalArgumentException("userId must not be null");
        }
        if (displayName == null || displayName.isBlank()) {
            throw new IllegalArgumentException("displayName must not be null or blank");
        }

        Profile saved = primary.updateDisplayNameReturningRow(userId, displayName);
        if (saved == null) {
            throw new IllegalStateException("Profile update returned null for userId=" + userId);
        }
        return new UpdatedProfile(saved, saved.version());
    }

    public Profile readProfile(UUID userId, long minVersion) {
        if (userId == null) {
            throw new IllegalArgumentException("userId must not be null");
        }
        if (minVersion < 0) {
            throw new IllegalArgumentException("minVersion must be >= 0");
        }

        try {
            return replica.findByIdAtLeastVersion(userId, minVersion)
                    .orElseGet(() -> readFromPrimary(userId, minVersion));
        } catch (RuntimeException ex) {
            // TODO: increment replica_fallback counter here (and increment replica_error)
            return readFromPrimary(userId, minVersion);
        }
    }

    private Profile readFromPrimary(UUID userId, long minVersion) {
        // TODO: increment fallback_to_primary counter here
        Profile profile = primary.findById(userId);
        if (profile == null) {
            throw new NoSuchElementException("Profile not found for userId=" + userId);
        }
        if (profile.version() < minVersion) {
            // Defensive check for unexpected version regression / data corruption scenarios
            throw new IllegalStateException(
                "Primary returned profile version " + profile.version()
                + " below requested minVersion " + minVersion + " for userId=" + userId
            );
        }
        return profile;
    }
}
```

### Operational checks to protect this design
- Track `replica_read_attempts`, `replica_read_hits`, `replica_read_misses`, and `replica_read_errors`.
- Track `read_fallback_to_primary` and alert on rising fallback percentage (canary for replication lag or replica outage).
- Track replica replication lag and alert if it exceeds your freshness SLO.
- Track `minVersion` vs returned version delta and alert on any delta where replica returns below requested version.
- Add circuit-breaker/timeout for replica reads and route directly to primary when unhealthy.
- Add alerts on `primary` fallback load spikes (protect primary saturation risk).
- Chaos / integration checks:
  - forced replica delay,
  - replica connection failure,
  - slow replica,
  - version monotonicity under concurrent updates.