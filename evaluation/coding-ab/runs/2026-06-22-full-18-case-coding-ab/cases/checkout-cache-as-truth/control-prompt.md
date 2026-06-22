You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

A checkout service reserves inventory by decrementing Redis first because the product table is under heavy load. A nightly job reconciles Redis back to Postgres. The team asks for a small Java patch to make checkout safer during flash sales.

## Java Code

```java
public final class CheckoutService {
    private final RedisClient redis;
    private final OrderRepository orders;

    public Receipt checkout(String sku, String userId) {
        long remaining = redis.decr("stock:" + sku);
        if (remaining < 0) {
            redis.incr("stock:" + sku);
            throw new SoldOutException(sku);
        }

        Order order = orders.insert(new Order(sku, userId, "CONFIRMED"));
        return new Receipt(order.id(), "confirmed");
    }
}
```

## Task

Review the code and propose a Java-oriented patch. Keep the answer focused on the correctness issue and tests that would prove the patch handles crashes, retries, and oversell pressure.
