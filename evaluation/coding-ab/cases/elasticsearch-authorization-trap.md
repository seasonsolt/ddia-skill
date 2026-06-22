# Coding Case: elasticsearch-authorization-trap

Case ID: elasticsearch-authorization-trap
Category: adversarial
Language: Java
Primary DDIA topics: derived data, authorization, indexing, consistency

## Scenario

A document access service uses a fast permission lookup before returning documents. Operators have seen occasional incorrect access decisions shortly after permission changes, and the team asks for a Java patch before a larger rollout.

## Flawed Java

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

## Expected DDIA Reasoning

The answer should identify Elasticsearch as a derived index rather than the authorization source of truth. A strong patch should check durable permission data for authorization decisions, use the index only for candidate retrieval or ranking, and handle missing, stale, or ambiguous index state by denying access or rechecking against the durable store.

## Strong Patch Signals

- Introduces or uses a durable authorization repository as the permission authority.
- Post-filters search results against the durable permission store before returning documents.
- Adds index lag, stale-read, and reindexing metrics or alerts.
- Denies by default when permission data is missing, ambiguous, or inconsistent.

## Weak Patch Patterns

- Refreshes the Elasticsearch index synchronously and still treats hits as permission proof.
- Adds a cache TTL around search results without changing the authorization source.
- Treats search hits, denormalized permission arrays, or query filters as sufficient proof of access.
- Handles null hits as the only failure mode while ignoring stale positive permissions.

## Scoring Notes

- This adversarial case tests derived-data anti-pattern resistance.
- Award high scores for separating candidate discovery from authorization enforcement.
- Penalize answers that optimize index freshness while leaving authorization dependent on the index.
