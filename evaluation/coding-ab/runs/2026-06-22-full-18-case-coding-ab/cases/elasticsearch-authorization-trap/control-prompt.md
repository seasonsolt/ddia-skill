You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

A document access service uses a fast permission lookup before returning documents. Operators have seen occasional incorrect access decisions shortly after permission changes, and the team asks for a Java patch before a larger rollout.

## Java Code

```java
public final class DocumentAccessService {
    private final SearchClient search;

    public boolean canView(UUID userId, UUID documentId) {
        SearchHit hit = search.get("document_permissions", documentId.toString());
        return hit.allowedUserIds().contains(userId.toString());
    }
}
```

## Task

Review the access check and propose a Java-oriented patch. Keep the answer focused on correctness during permission changes, ambiguous lookup results, and tests or metrics that would catch stale access decisions.
