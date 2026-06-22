# Coding Case: schema-migration-breaking-reader

Case ID: schema-migration-breaking-reader
Category: bad
Language: Java
Primary DDIA topics: schema evolution, compatibility, event streams, deployment

## Scenario

An order service publishes JSON events that several downstream services consume. A newer producer was deployed first, and a legacy credit-reservation consumer started failing on events from the new topic.

## Flawed Java

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

## Expected DDIA Reasoning

The answer should identify that the producer changed the event schema before all readers were compatible. A good patch should use an additive or versioned migration path, compatibility checks, dual-publish or dual-read behavior during rollout, and consumer contract tests so old and new readers have proof of compatibility before the old field or topic is removed.

## Strong Patch Signals

- Keeps `amountCents` during the migration or publishes a compatible event shape until readers move.
- Adds a schema registry or compatibility gate that rejects breaking changes.
- Backfills, transforms, or dual-reads events safely during the rollout window.

## Weak Patch Patterns

- Says JSON is flexible enough and ignores missing-field behavior.
- Catches null and defaults the amount to zero, silently changing money movement.
- Assumes all consumers can be upgraded manually without rollout proof or contract tests.

## Scoring Notes

- Award high scores for explaining forward and backward compatibility across independently deployed services.
- Penalize answers that treat producer deployment order as the only required fix.
