# Coding Case: good-outbox-relay-idempotent-consumer

Case ID: good-outbox-relay-idempotent-consumer
Category: good
Language: Java
Primary DDIA topics: durable handoff, duplicate message handling, recovery

## Scenario

An order service writes an order row and also stores a durable follow-up work record for fulfillment. A separate fulfillment handler ignores messages it has already seen before creating shipments. The team asks whether this should be simplified by sending directly to Kafka from the request path because it seems more immediate.

## Flawed Java

```java
public final class OrderService {
    private final OrderRepository orders;
    private final OutboxRepository outbox;

    @Transactional
    public UUID createOrder(CreateOrder command) {
        UUID orderId = orders.insert(command);
        outbox.insert(new OutboxEvent("order-created", orderId.toString(), new OrderCreated(orderId)));
        return orderId;
    }
}

public final class FulfillmentConsumer {
    private final ProcessedMessageRepository processed;
    private final ShipmentRepository shipments;

    @Transactional
    public void onOrderCreated(String messageId, OrderCreated event) {
        if (!processed.tryInsert(messageId)) {
            return;
        }
        shipments.createIfAbsent(event.orderId());
    }
}
```

## Task

Review the code, assess whether a Java-oriented patch is needed, and justify the operational checks that would protect this design.

## Expected DDIA Reasoning

The answer should keep the outbox because the order row and durable event handoff are atomic in the database transaction. It should verify relay acknowledgement handling, duplicate publish after retry or crash, and consumer idempotency rather than replacing the design with synchronous Kafka send.

## Strong Patch Signals

- Preserves order/outbox atomicity in the same database transaction.
- Keeps the idempotent consumer and shipment `createIfAbsent` behavior.
- Adds relay lag, publish retry, duplicate publish, and duplicate-consume metrics.

## Weak Patch Patterns

- Removes the outbox and publishes only through Kafka in the request path.
- Assumes synchronous Kafka send in the request transaction is safer or atomic with the database.
- Ignores duplicate delivery and replay behavior.

## Scoring Notes

- Award high scores for recognizing this as a good durable handoff pattern with at-least-once relay semantics.
- Penalize answers that trade recoverability for lower apparent latency without addressing crash windows.
