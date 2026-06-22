You want a backward-compatible migration: keep publishing a legacy field (`amountCents`) while introducing `totalCents`, and make the legacy consumer accept both field names so reads don’t break.

```java
public final class OrderEventPublisher {
    private static final String ORDER_TOPIC = "orders.v2";
    private final KafkaTemplate<String, String> kafka;

    public void publish(Order order) {
        long amountCents = order.totalCents();

        String payload = """
            {"orderId":"%s","totalCents":%d,"amountCents":%d,"currency":"%s"}
            """.formatted(order.id(), amountCents, amountCents, order.currency());

        kafka.send(ORDER_TOPIC, order.id().toString(), payload);
    }
}
```

```java
public final class LegacyOrderConsumer {
    public void handle(JsonNode event) {
        JsonNode amountNode = event.path("amountCents");
        if (!amountNode.isNumber()) {
            amountNode = event.path("totalCents");
        }

        if (!amountNode.isNumber()) {
            throw new IllegalArgumentException("Order event missing required amount field: amountCents or totalCents");
        }

        long amount = amountNode.asLong();
        reserveCredit(amount);
    }
}
```

This lets older consumers continue to work during rollout; once all downstream services move to `totalCents`, you can remove `amountCents` from the producer later.