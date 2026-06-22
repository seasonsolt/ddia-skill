# Coding Case: missing-reconciliation-observability

Case ID: missing-reconciliation-observability
Category: bad
Language: Java
Primary DDIA topics: derived data, change data capture, recovery, observability

## Scenario

A product service updates Postgres and then immediately updates a search index. Support reports products whose details are correct in the admin database but stale or missing in search results.

## Flawed Java

```java
public final class SearchIndexUpdater {
    private final ProductRepository products;
    private final SearchClient search;

    public void updateProduct(UUID productId, ProductPatch patch) {
        Product product = products.update(productId, patch);
        search.index("products", productId.toString(), ProductDocument.from(product));
    }
}
```

## Task

Review the update path and propose a patch that keeps the search index recoverable and observable when indexing fails or falls behind.

## Expected DDIA Reasoning

The answer should identify search as derived data that can drift from Postgres. A good patch should use an outbox, durable change log, or CDC stream for indexing work, make the indexer idempotent, add reconciliation or reindexing, and expose lag and drift metrics with runbook checks.

## Strong Patch Signals

- Writes a durable indexing event or consumes a durable database change log.
- Makes the indexer idempotent and includes a reindex or reconciliation job.
- Adds drift metrics, indexing lag metrics, and failure-injection tests.

## Weak Patch Patterns

- Retries `search.index` inline only, keeping the request path as the recovery mechanism.
- Treats search as authoritative when it conflicts with Postgres.
- Ignores index lag, failed updates, or operator runbook checks.

## Scoring Notes

- Award high scores for explaining search as derived state and designing repair paths.
- Penalize answers that only improve immediate retry behavior without durable catch-up.
