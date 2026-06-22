You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

A product service updates Postgres and then immediately updates a search index. Support reports products whose details are correct in the admin database but stale or missing in search results.

## Java Code

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
