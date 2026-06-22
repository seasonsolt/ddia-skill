A more natural version of your request: please review this Java checkout snippet and give a practical Java patch focused on correctness (especially cache/DB consistency, retries, and flash-sale oversell), then list tests that validate crash handling, retry behavior, and high-concurrency pressure.

## Diagnosis
- `decr` in Redis happens before the database write, so a crash between reservation and DB insert can permanently leak stock.
- There is no request-level idempotency, so retries can create duplicate orders and consume extra stock.
- Redis and Postgres are not reconciled for failures in the request path; Redis can briefly become the de facto state while DB is authoritative.
- The path is not safe under concurrent retries because duplicate attempts are not uniquely bounded.

## Patch
```java
public final class CheckoutService {
    private static final Duration HOLD_TTL = Duration.ofSeconds(30);
    private static final String HOLD_INDEX_KEY = "stock:hold:index";

    private final StringRedisTemplate redis;
    private final OrderRepository orders;

    private static final String RESERVE_STOCK_LUA = """
        local stockKey = KEYS[1]
        local holdKey = KEYS[2]
        local holdSet = KEYS[3]
        local requestId = ARGV[1]
        local ttlMs = tonumber(ARGV[2])

        if redis.call('GET', holdKey) then
          return tonumber(redis.call('GET', stockKey) or '0')
        end

        local stock = tonumber(redis.call('GET', stockKey) or '0')
        if stock <= 0 then
          return -1
        end

        redis.call('DECR', stockKey)
        redis.call('SET', holdKey, requestId, 'PX', ttlMs)
        redis.call('SADD', holdSet, holdKey)
        return stock - 1
        """;

    private static final String RELEASE_STOCK_LUA = """
        local stockKey = KEYS[1]
        local holdKey = KEYS[2]
        local holdSet = KEYS[3]
        local requestId = ARGV[1]

        if redis.call('GET', holdKey) == requestId then
          redis.call('INCR', stockKey)
          redis.call('DEL', holdKey)
          redis.call('SREM', holdSet, holdKey)
          return 1
        end
        return 0
        """;

    @Transactional
    public Receipt checkout(String sku, String userId, String requestId) {
        if (requestId == null || requestId.isBlank()) {
            throw new IllegalArgumentException("requestId is required for idempotent checkout");
        }

        String stockKey = "stock:" + sku;
        String holdKey = "stock:hold:" + sku + ":" + requestId;

        Long remaining = redis.execute(
            RedisScript.of(RESERVE_STOCK_LUA, Long.class),
            List.of(stockKey, holdKey, HOLD_INDEX_KEY),
            requestId,
            String.valueOf(HOLD_TTL.toMillis())
        );

        if (remaining == null || remaining < 0) {
            throw new SoldOutException(sku);
        }

        try {
            return orders.findByRequestId(requestId)
                .map(o -> new Receipt(o.id(), o.status()))
                .orElseGet(() -> {
                    Order order = orders.insert(new Order(sku, userId, requestId, "CONFIRMED"));
                    redis.delete(holdKey); // consume hold only after durable write
                    redis.opsForSet().remove(HOLD_INDEX_KEY, holdKey);
                    return new Receipt(order.id(), "confirmed");
                });

        } catch (DataIntegrityViolationException duplicate) {
            rollback(stockKey, holdKey, requestId);
            Order existing = orders.findByRequestId(requestId)
                .orElseThrow(() -> duplicate);
            return new Receipt(existing.id(), existing.status());

        } catch (RuntimeException ex) {
            rollback(stockKey, holdKey, requestId);
            throw ex;
        }
    }

    // periodic safety net for process crashes between Redis reserve and DB commit
    @Scheduled(fixedDelay = 5000)
    public void reclaimOrphanHolds() {
        for (String holdKey : redis.opsForSet().members(HOLD_INDEX_KEY)) {
            String[] parts = holdKey.split(":", 4); // stock:hold:{sku}:{requestId}
            String requestId = parts[3];
            if (orders.findByRequestId(requestId).isEmpty()) {
                String sku = parts[2];
                rollback("stock:" + sku, holdKey, requestId);
            }
        }
    }

    private void rollback(String stockKey, String holdKey, String requestId) {
        redis.execute(
            RedisScript.of(RELEASE_STOCK_LUA, Long.class),
            List.of(stockKey, holdKey, HOLD_INDEX_KEY),
            requestId
        );
    }
}
```

Also add these persistence constraints:
- `orders.request_id` must be `UNIQUE` to enforce dedupe on retries.
- `Order` should persist `requestId`, status, and optional user/sku.

## Tests
1. `rejectsOversellUnderConcurrentLoad`
   - Setup stock = 5 in Redis, 50 parallel checkout calls with distinct request IDs.
   - Assert 5 confirmations, 45 `SoldOutException`, no negative stock in Redis, confirmed row count == 5.

2. `retryWithSameRequestIdIsIdempotent`
   - Call `checkout(sku, user, req1)` twice.
   - Assert both return same `order.id()`, repository insert called once, stock decremented once.

3. `releasesStockOnDbFailure`
   - Force `orders.insert` to throw after reserve.
   - Assert Redis stock returns to original, hold key removed, order not inserted.

4. `recoversOrphanHoldAfterCrash`
   - Simulate crash by directly invoking reserve path and skipping DB insert (or mocking service failure before DB call), then run `reclaimOrphanHolds()`.
   - Assert hold marker removed and stock restored.

5. `duplicateRequestIdDuringRaceDoesNotDuplicate`
   - Two threads race with same requestId.
   - Assert one order row, at most one stock decrement, and second path returns existing receipt.