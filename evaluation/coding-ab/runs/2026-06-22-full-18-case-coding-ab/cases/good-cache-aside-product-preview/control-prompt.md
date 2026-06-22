You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

A product page service uses Redis to speed up product previews, but checkout and pricing still read from Postgres. The team asks whether this cache usage should be rejected or patched.

## Java Code

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
