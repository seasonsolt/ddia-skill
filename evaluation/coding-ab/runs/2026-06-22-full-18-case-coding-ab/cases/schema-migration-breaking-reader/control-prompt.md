You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

An order service publishes JSON events that several downstream services consume. A newer producer was deployed first, and a legacy credit-reservation consumer started failing on events from the new topic.

## Java Code

```java
public final class OrderEventPublisher {
    private final KafkaTemplate<String, String> kafka;

    public void publish(Order order) {
        String payload = """
            {"orderId":"%s","totalCents":%d,"currency":"%s"}
            """.formatted(order.id(), order.totalCents(), order.currency());
        kafka.send("orders.v2", order.id().toString(), payload);
    }
}

public final class LegacyOrderConsumer {
    public void handle(JsonNode event) {
        long amount = event.get("amountCents").asLong();
        reserveCredit(amount);
    }
}
```

## Task

Review the producer and consumer change and propose a patch that lets the migration roll out without breaking existing readers.
