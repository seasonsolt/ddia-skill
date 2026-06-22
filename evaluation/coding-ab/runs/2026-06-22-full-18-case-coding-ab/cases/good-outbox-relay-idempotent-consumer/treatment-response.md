You asked for a distributed-design review of this Java outbox + consumer pattern, with a minimal correctness patch and operational checks.

## Assumptions and workload shape
- Order creation is write-heavy in bursts and each successful order must eventually trigger one shipment.
- Duplicate shipments are business-critical correctness failures.
- The system tolerates at-least-once message delivery, but not double side effects.
- Outbox is used as the source-of-truth bridge between transactional DB state and async processing.

## Source of truth and consistency goals
- Source of truth for order state: `orders`.
- Outbox is durable intent/event log, not the source of business truth.
- Shipment table is derived state and must be idempotent.
- Moving Kafka send into the request path removes atomicity unless you use transactional messaging with careful coordinator design.

## Recommendation (smallest practical patch)
The biggest distributed-data bug is **not in the shown `createOrder` transaction itself**, but in the boundary between event publication and consumption if you “simplify” to synchronous Kafka send.

Smallest patch:
1. Keep outbox in the request path transaction.
2. Persist a stable event id once in outbox and use it as the message id for dedupe.
3. Make `tryInsert` and `createIfAbsent` atomic via unique constraints, not best-effort logic.

```java
public final class OrderService {
    public UUID createOrder(CreateOrder command) {
        UUID orderId = orders.insert(command);
        UUID eventId = UUID.randomUUID(); // stable dedupe key
        outbox.insert(new OutboxEvent(
            eventId,
            "order-created",
            orderId.toString(),
            new OrderCreated(orderId)
        ));
        return orderId;
    }
}

public final class FulfillmentConsumer {
    private final ProcessedMessageRepository processed;
    private final ShipmentRepository shipments;

    @Transactional
    public void onOrderCreated(UUID messageId, OrderCreated event) {
        if (!processed.tryInsert(messageId)) { // unique INSERT INTO processed(message_id) VALUES (?) ON CONFLICT DO NOTHING
            return;
        }
        shipments.createIfAbsent(event.orderId()); // INSERT ... ON CONFLICT DO NOTHING by order_id
    }
}
```

Also required schema guarantees:
- `processed(message_id)` must be `UNIQUE`.
- `shipments(order_id)` should be `UNIQUE`.
- Kafka message should carry the outbox `eventId`; the consumer should dedupe on that value.

## Key trade-offs
- You keep outbox latency (extra polling/relay step) but preserve correctness under partial failure.
- Direct request-path Kafka send is lower latency on happy path, but weakens durability and can produce missing/duplicate fulfillment work under failure.
- You get “at-least-once + idempotent handling,” not true end-to-end exactly-once.

## Failure modes
- DB commit succeeds, event not published.
- Event published, DB transaction rolled back.
- Consumer crashes after marking `processed` but before shipment write commit.
- Consumer reprocesses same message after restart/rebalance.
- Relay worker duplicates publishes or reorders same event.
- Dedupe store/shipments table outages causing delayed or partial processing.

## Consistency and correctness implications
- `@Transactional` on both sides gives local atomicity only.
- Without stable dedupe keys + uniqueness constraints, duplicates can still pass through as separate DB writes.
- A distributed transaction across DB + Kafka is unnecessary here if outbox + idempotent consumer are implemented correctly.
- You can only claim: “no shipment duplicates” and “order is persisted iff outbox intent exists,” not “exactly-once end-to-end delivery by default.”

## Operational checks
- Outbox lag: count and age of `PENDING` outbox rows; alert if queue age grows.
- Publish reliability: outbox publish failures and retry counts with exponential backoff/dead-letter thresholds.
- Dedup effectiveness: ratio of `processed` duplicate inserts rejected.
- Shipment correctness: mismatch count between `orders` with created time and expected shipments (lagging or missing).
- Relay-to-consumer traceability: correlation id from `orderId` + `eventId` across logs.
- Consumer lag and replay rate.

## Tests / experiments to validate
- Simulate crash after outbox insert, before publish.
- Simulate Kafka send failure with retry loops.
- Simulate duplicate deliveries; verify only one shipment row exists.
- Simulate redelivery order with consumer retries after partial failures.
- Load test hot order creation to confirm `shipments(order_id)` unique constraint prevents duplicates under concurrent events.