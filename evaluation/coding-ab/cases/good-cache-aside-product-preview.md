# Coding Case: good-cache-aside-product-preview

Case ID: good-cache-aside-product-preview
Category: good
Language: Java
Primary DDIA topics: read paths, cached previews, derived data safety

## Scenario

A product page service uses Redis to speed up product previews, but checkout and pricing still read from Postgres. The team asks whether this cache usage should be rejected or patched.

## Flawed Java

```java
public final class ProductPreviewService {
    private final RedisClient redis;
    private final ProductRepository products;

    public ProductPreview preview(String sku) {
        String cached = redis.get("product-preview:" + sku);
        if (cached != null) {
            return ProductPreview.fromJson(cached);
        }

        Product product = products.findForPreview(sku);
        ProductPreview preview = ProductPreview.from(product.id(), product.name(), product.thumbnailUrl());
        redis.setex("product-preview:" + sku, 300, preview.toJson());
        return preview;
    }
}
```

## Task

Review the code, assess whether a Java-oriented patch is needed, and justify the operational checks that would protect this design.

## Expected DDIA Reasoning

The answer should not reject all caching. It should identify Redis as derived preview data, keep business decisions such as checkout price and availability outside this cache, and recommend bounded TTL, invalidation, and metrics for stale previews.

## Strong Patch Signals

- States that this is acceptable if preview data is non-authoritative.
- Keeps checkout, payment, authorization, and inventory decisions on durable sources.
- Adds stale-cache tests, invalidation tests, and cache-hit/stale-age metrics.

## Weak Patch Patterns

- Removes Redis because "caches are unsafe" without distinguishing preview data from business invariants.
- Moves checkout price or inventory decisions into the preview cache.
- Adds distributed locks around preview reads.

## Scoring Notes

- Award high scores for avoiding false positives and preserving the derived-data boundary.
- Penalize answers that over-engineer a read-only preview path.
