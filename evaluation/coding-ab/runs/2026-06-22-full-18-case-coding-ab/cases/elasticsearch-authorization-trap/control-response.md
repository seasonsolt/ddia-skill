You asked for a Java review-and-patch of the document access check, focused on correctness when permissions change, handling ambiguous permission lookups, and adding tests/metrics to catch stale access decisions.

### Findings (by severity)

1. **High – stale permission reads are possible**  
   The direct `search.get(...)` lookup can return an out-of-date replica view right after permission writes, causing transient incorrect denies/grants.

2. **High – ambiguous permission results are not handled**  
   Current code assumes a single hit and a non-null set. If the index contains duplicate permission docs for a document, stale or corrupted data can slip through and return an arbitrary decision.

3. **Medium – potential null-safety regressions**  
   `hit` or `hit.allowedUserIds()` may be null, leading to runtime exceptions and false positives/negatives.

4. **Medium – weak observability**  
   No metrics exist for misses, ambiguities, stale-read recovery, or exceptions, so this class cannot prove correctness across permission churn.

### Recommended Java patch

```java
import java.util.Set;
import java.util.UUID;

public final class DocumentAccessService {
    private static final String PERMISSIONS_INDEX = "document_permissions";

    private final SearchClient search;
    private final AccessMetrics metrics;

    public boolean canView(UUID userId, UUID documentId) {
        if (userId == null || documentId == null) {
            metrics.invalidRequest();
            return false;
        }

        final String uid = userId.toString();
        final String docId = documentId.toString();

        PermissionLookup first = lookupWithLimit(docId, ReadMode.EVENTUAL);
        if (first.hits.isEmpty()) {
            metrics.permissionLookupMiss();
            return false;
        }

        if (first.hits.size() != 1) {
            metrics.ambiguousPermissionLookup();
            return false; // fail-closed when data integrity is uncertain
        }

        if (isAllowed(first.hits.get(0), uid)) {
            metrics.permissionAllowed();
            return true;
        }

        // Retry once against authoritative/read-fresh path to guard near-term stale replica reads.
        PermissionLookup fresh = lookupWithLimit(docId, ReadMode.PRIMARY_FRESH);
        if (fresh.hits.size() != 1) {
            metrics.staleRetryFailure();
            return false;
        }

        boolean allowed = isAllowed(fresh.hits.get(0), uid);
        if (allowed) {
            metrics.staleRetryRecovered();
        } else {
            metrics.permissionDenied();
        }
        return allowed;
    }

    private PermissionLookup lookupWithLimit(String documentId, ReadMode readMode) {
        // Replace with your SearchClient query API shape.
        // The key part is: read with deterministic cardinality limit=2 and configurable
        // eventual-vs-primary/refresh semantics.
        // Example semantics:
        // - EVENTUAL: current fast path
        // - PRIMARY_FRESH: force read from primary or refresh point (read-after-write safety)
        return search.lookupPermissionIndex(PERMISSIONS_INDEX, documentId, 2, readMode);
    }

    private boolean isAllowed(SearchHit hit, String userIdAsString) {
        if (hit == null) {
            return false;
        }
        Set<String> allowedUserIds = hit.allowedUserIds();
        return allowedUserIds != null && allowedUserIds.contains(userIdAsString);
    }

    // Read mode to be implemented by your SearchClient layer
    enum ReadMode {
        EVENTUAL,
        PRIMARY_FRESH
    }

    interface AccessMetrics {
        void invalidRequest();

        void permissionLookupMiss();

        void ambiguousPermissionLookup();

        void permissionAllowed();

        void permissionDenied();

        void staleRetryRecovered();

        void staleRetryFailure();
    }

    static final class PermissionLookup {
        private final java.util.List<SearchHit> hits;

        PermissionLookup(java.util.List<SearchHit> hits) {
            this.hits = hits;
        }

        java.util.List<SearchHit> hits() {
            return hits;
        }
    }
}
```

If your `SearchClient` currently has only `get(index, id)`, add a small repository layer that exposes:
- `lookupPermissionIndex(index, documentId, limit, readMode)`
- `SearchHit` + cardinality checks
- `primary/refresh` read path

That keeps the service testable and keeps the inconsistency protections localized.

### Tests to add (high value for this issue)

1. `nullUserOrDocumentIdReturnsFalseAndIncrementsInvalidRequest`
2. `missingPermissionDocumentReturnsFalseAndIncrementsMiss`
3. `multiplePermissionRowsForSameDocumentReturnsFalseAndIncrementsAmbiguous`
4. `permissionAllowsUserAfterRetryWhenFirstReadWasStale`
   - Fake client returns stale replica hit without user first, then primary-fresh hit with user present.
   - Assert final `true` and `staleRetryRecovered` increments.
5. `permissionDeniesUserAfterRetryWhenBothReadsDeny`
   - Assert `staleRetryFailure`/`permissionDenied` counters.
6. `throwsExceptionInSearchClientReturnsFalseAndIncrementsError` (if you add error metric)

### Metrics that specifically catch stale decisions

1. `doc_access_lookup_miss_total`
2. `doc_access_lookup_ambiguous_total`
3. `doc_access_lookup_stale_retry_recovered_total`
4. `doc_access_lookup_stale_retry_failed_total`
5. `doc_access_allowed_total`
6. `doc_access_denied_total`
7. Optional: histogram for lookup latency split by read mode (`eventual` vs `primary_fresh`)

These changes make transient permission-change windows explicit, fail safely on index ambiguity, and give you evidence when stale reads are being exercised.