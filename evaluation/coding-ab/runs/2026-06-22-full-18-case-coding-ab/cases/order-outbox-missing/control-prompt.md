You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

An order service writes an order row and immediately publishes an event to Kafka so fulfillment can ship the item. Operators report orders that exist in Postgres but never reach fulfillment after deploy restarts.

## Java Code

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
