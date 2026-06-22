# Coding Case: multi-region-last-write-wins-profile

Case ID: multi-region-last-write-wins-profile
Category: adversarial
Language: Java
Primary DDIA topics: replication, conflict resolution, distributed consistency, user data correctness

## Scenario

A profile service accepts updates in multiple regions and resolves conflicts when asynchronous replication delivers another region's copy. The team asks for a small Java patch because a few users have reported missing profile edits after travel or failover.

## Flawed Java

```java
public final class ProfileConflictResolver {
    public Profile resolve(Profile local, Profile remote) {
        return local.updatedAt().isAfter(remote.updatedAt()) ? local : remote;
    }
}
```

## Task

Review the resolver and propose a safer Java-oriented conflict-resolution patch. Keep the answer focused on product-visible behavior for conflicts and tests for concurrent profile edits across regions.

## Expected DDIA Reasoning

The answer should reject blanket last-write-wins for user profile data because it can lose independent updates across regions. A strong patch should merge per field where that merge is valid, attach versions, vector clocks, or equivalent causal metadata, preserve unresolved conflicts as explicit records, and define how the product surfaces or resolves conflicts instead of silently choosing one whole object.

## Strong Patch Signals

- Rejects blanket LWW as the conflict policy for user data.
- Preserves both conflicting values when the system cannot merge them safely.
- Adds a conflict queue, review state, or CRDT-style merge only for fields where the merge semantics are valid.
- Uses versions, vector clocks, or causal metadata to distinguish concurrent writes from superseding writes.

## Weak Patch Patterns

- Trusts wall-clock timestamps as proof of the winning update.
- Increases NTP precision while keeping the same whole-record overwrite policy.
- Silently overwrites one region's value without recording the conflict.
- Adds retries or region preference rules without addressing independent concurrent edits.

## Scoring Notes

- This adversarial case requires anti-pattern resistance score 2 to pass.
- Award high scores for patches that distinguish field-level mergeable data from non-mergeable conflicts.
- Penalize answers that make LWW appear safer through clock tuning or tie-breakers.
