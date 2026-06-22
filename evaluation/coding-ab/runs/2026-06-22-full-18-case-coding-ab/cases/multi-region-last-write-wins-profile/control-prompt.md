You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

A profile service accepts updates in multiple regions and resolves conflicts when asynchronous replication delivers another region's copy. The team asks for a small Java patch because a few users have reported missing profile edits after travel or failover.

## Java Code

```java
public final class ProfileConflictResolver {
    public Profile resolve(Profile local, Profile remote) {
        return local.updatedAt().isAfter(remote.updatedAt()) ? local : remote;
    }
}
```

## Task

Review the resolver and propose a safer Java-oriented conflict-resolution patch. Keep the answer focused on product-visible behavior for conflicts and tests for concurrent profile edits across regions.
