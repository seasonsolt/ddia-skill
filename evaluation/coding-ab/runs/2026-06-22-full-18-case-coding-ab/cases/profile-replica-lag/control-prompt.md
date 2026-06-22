You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

A profile service writes to the primary database and immediately reads from a read replica to return the updated profile. Users intermittently see their old display name after saving.

## Java Code

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
