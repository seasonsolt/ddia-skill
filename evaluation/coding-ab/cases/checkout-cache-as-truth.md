# Coding Case: checkout-cache-as-truth

Case ID: checkout-cache-as-truth
Category: bad
Language: Java
Primary DDIA topics: source of truth, cache invalidation, transactions, recovery

## Scenario

A checkout service reserves inventory by decrementing Redis first because the product table is under heavy load. A nightly job reconciles Redis back to Postgres. The team asks for a small Java patch to make checkout safer during flash sales.

## Flawed Java

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

## Expected DDIA Reasoning

The answer should reject Redis as the authoritative inventory record, identify the crash window between `decr` and `orders.insert`, and move the invariant into a durable transactional boundary or explicit reservation workflow. It should discuss idempotency for repeated checkout attempts and reconciliation for ambiguous outcomes.

## Strong Patch Signals

- Makes Postgres or another durable transactional store the source of truth for inventory and orders.
- Uses a conditional update, row lock, reservation row, or equivalent invariant-preserving transaction.
- Adds idempotency keys and tests for duplicate requests, process crash after reservation, and concurrent checkout attempts.

## Weak Patch Patterns

- Adds a Redis lock while leaving Redis as the only proof of inventory.
- Retries `orders.insert` without defining how duplicate orders or lost decrements are handled.
- Treats the nightly reconciliation job as sufficient for user-facing correctness.

## Scoring Notes

- Award high scores for a patch that names the invariant and tests concurrent oversell behavior.
- Penalize answers that only add null checks, exception handling, or cache TTL changes.
