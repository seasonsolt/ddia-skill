Diagnosis
You’re asking for a Java-focused DDIA-style fix for a cache-first checkout path, with emphasis on source-of-truth, consistency boundaries, idempotency, and failure behavior under flash-sale pressure.

1. **Source of truth is broken**: Redis is being treated as the system of record for availability, so any failure between `decr` and DB insert creates permanent mismatch until nightly reconciliation, violating correctness during checkout.
2. **Missing transaction boundary across systems**: `redis.decr` and `orders.insert` are not atomic together. Postgres success and Redis success can diverge on crashes/retries, so `confirmed_orders` can drift from stock.
3. **No idempotency**: retries can consume multiple units for the same intent, and concurrent duplicate requests can amplify pressure and cause apparent oversell or wrong sold-out responses.
4. **Failure modes are silent**: on DB exception, stock is not consistently restored (currently only when immediate `< 0` branch runs). Crashes during or after the method can leak reservations.
5. **Observability gap**: there is no visibility into cache-vs-DB drift, stale in-flight reservations, or reconciliation lag.

Patch
1. Keep Postgres as the **authoritative source** for confirmed orders; keep Redis as a fast reservation cache.
2. Add a caller-provided idempotency key (`checkoutId`) and a unique constraint/index on `orders.checkout_id`.
3. Reserve stock with a Lua script that also marks request in-flight; release stock with another script in a single failure path; return same receipt on duplicate checkoutId.
4. Add operational metrics around: in-flight collisions, retry replays, cache reserve/release failures, and reconciliation lag.

```java
public final class CheckoutService {
    private final RedisClient redis;
    private final OrderRepository orders;
    private static final long INFLIGHT_TTL_MS = 30_000L;

    // KEYS: [stockKey, inflightKey]
    // ARGV: [checkoutId, ttlMs]
    private static final String RESERVE_LUA =
        "if redis.call('SETNX', KEYS[2], ARGV[1]) == 0 then return -2 end\n" +
        "redis.call('PEXPIRE', KEYS[2], ARGV[2])\n" +
        "local stock = tonumber(redis.call('GET', KEYS[1]) or '0')\n" +
        "if stock <= 0 then redis.call('DEL', KEYS[2]); return -1 end\n" +
        "redis.call('DECR', KEYS[1])\n" +
        "return stock - 1";

    // KEYS: [stockKey, inflightKey]
    // ARGV: [checkoutId]
    private static final String RELEASE_LUA =
        "if redis.call('GET', KEYS[2]) == ARGV[1] then\n" +
        "  redis.call('INCR', KEYS[1])\n" +
        "  redis.call('DEL', KEYS[2])\n" +
        "end\n" +
        "return 1";

    public Receipt checkout(String sku, String userId, String checkoutId) {
        if (checkoutId == null || checkoutId.isBlank()) {
            throw new IllegalArgumentException("checkoutId required for idempotency");
        }

        // Idempotent replay path: source-of-truth check before cache touch
        var existing = orders.findByCheckoutId(checkoutId);
        if (existing.isPresent()) {
            return toReceipt(existing.get());
        }

        String stockKey = "stock:" + sku;
        String inflightKey = "checkout:inflight:" + checkoutId;

        Long remaining = redis.evalLong(RESERVE_LUA, List.of(stockKey, inflightKey),
                                       List.of(checkoutId, String.valueOf(INFLIGHT_TTL_MS));
        if (remaining == null || remaining == -1) {
            throw new SoldOutException(sku);
        }
        if (remaining == -2) {
            // concurrent duplicate is in-flight: retry or return conflict
            throw new RetryableCheckoutConflictException(checkoutId);
        }

        boolean dbCommitted = false;
        try {
            // unique (sku,userId,checkoutId) or (checkoutId) enforced in DB
            Order order = orders.insert(new Order(sku, userId, checkoutId, "CONFIRMED"));
            dbCommitted = true;
            return new Receipt(order.id(), "confirmed");
        } catch (DuplicateKeyException dup) {
            // idempotent retry after previous successful write
            Order replay = orders.findByCheckoutId(checkoutId)
                                .orElseThrow(() -> new IllegalStateException("inconsistent state"));
            return toReceipt(replay);
        } finally {
            if (!dbCommitted) {
                redis.evalLong(RELEASE_LUA, List.of(stockKey, inflightKey), List.of(checkoutId));
            } else {
                redis.delete(inflightKey);
            }
        }
    }

    private Receipt toReceipt(Order order) {
        return new Receipt(order.id(), order.status().toLowerCase());
    }
}
```

This improves correctness to:
- **Consistency guarantee**: for a fixed `checkoutId`, at most one confirmed order is returned.
- **Bounded failure behavior**: most DB failures revert Redis reservation immediately.
- **No strong XA claim**: atomicity across Redis and Postgres is best-effort; use a periodic reconciler for stale in-flight/leaked reservations.

Tests
1. `test_retry_with_same_checkoutId_is_idempotent_and_does_not_double_decrement`  
   Call `checkout(sku, user, sameCheckoutId)` twice with forced duplicate request timing. Assert one order row and stock decremented once.

2. `test_concurrent_unique_retries_do_not_oversell`  
   Initialize stock=100 in Redis/Postgres, fire 1000 distinct checkoutIds with 1 thread per request. Assert confirmed orders ≤ 100 and final Redis stock + confirmed count never exceeds initial stock.

3. `test_db_failure_after_reserve_rolls_back_cache`  
   Stub repository to throw on insert. Assert Redis stock returns to original and inflight key is removed.

4. `test_inflight_collision_returns_retryable`  
   Create one thread that passes reserve and blocks before DB insert; another thread with same `checkoutId` should receive retryable conflict (`-2` path) or replay after commit, never create a second confirmed order.

5. `test_crash_during_processing_leak_recovery`  
   Simulate process kill right after reservation (or throw before insert) and run reconciliation backfill job/observer. Verify stale in-flight reservations are detected and stock is restored within bounded time.

6. `test_visibility_and_sla`  
   Assert metrics for `reserve_fail_soldout`, `reserve_conflict`, `rollback_compensations`, and `inflight_ttl_expired` emit, and alert when `cache_db_divergence` or stale in-flight count exceeds threshold.