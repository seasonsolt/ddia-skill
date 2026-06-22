# Coding Case: order-outbox-missing

Case ID: order-outbox-missing
Category: bad
Language: Java
Primary DDIA topics: outbox pattern, atomicity, message delivery, recovery

## Scenario

An order service writes an order row and immediately publishes an event to Kafka so fulfillment can ship the item. Operators report orders that exist in Postgres but never reach fulfillment after deploy restarts.

## Flawed Java

```java
public final class OrderService {
    private final OrderRepository orders;
    private final KafkaTemplate<String, OrderCreated> kafka;

    @Transactional
    public UUID createOrder(CreateOrder command) {
        UUID orderId = orders.insert(command);
        kafka.send("orders", orderId.toString(), new OrderCreated(orderId));
        return orderId;
    }
}
```

## Task

Review the code and propose a patch that prevents lost fulfillment work when the service crashes or Kafka is unavailable.

## Expected DDIA Reasoning

The answer should identify that the database transaction does not atomically include Kafka. It should propose a transactional outbox or equivalent durable handoff, with a relay that publishes events and marks them sent only after broker acknowledgement.

## Strong Patch Signals

- Writes the order and outbox event in the same database transaction.
- Uses a relay with retry, deduplication keys, and consumer idempotency.
- Adds tests for crash after commit before publish and duplicate publish after retry.

## Weak Patch Patterns

- Moves `kafka.send` before `orders.insert` or assumes the annotation covers Kafka.
- Adds a sleep, flush, or synchronous send without durable recovery.
- Ignores duplicate events on the fulfillment consumer side.

## Scoring Notes

- Award high scores for explaining both lost event and duplicate event failure modes.
- Penalize answers that only catch Kafka exceptions inside the transaction.
