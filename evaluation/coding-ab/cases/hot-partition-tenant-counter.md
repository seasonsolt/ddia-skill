# Coding Case: hot-partition-tenant-counter

Case ID: hot-partition-tenant-counter
Category: bad
Language: Java
Primary DDIA topics: partitioning, scalability, counters, operational metrics

## Scenario

A multi-tenant API records each request by incrementing a per-tenant usage counter in DynamoDB. Most tenants are small, but one large tenant regularly hits throttling during traffic spikes.

## Flawed Java

```java
public final class UsageCounterService {
    private final DynamoDbClient dynamo;

    public void recordRequest(String tenantId) {
        dynamo.updateItem(UpdateItemRequest.builder()
            .tableName("tenant_usage")
            .key(Map.of("tenant_id", AttributeValue.fromS(tenantId)))
            .updateExpression("ADD request_count :one")
            .expressionAttributeValues(Map.of(":one", AttributeValue.fromN("1")))
            .build());
    }
}
```

## Task

Review the counter design and propose a patch that handles very high request rates for a single tenant while preserving useful usage reads.

## Expected DDIA Reasoning

The answer should identify that a single hot tenant creates a hot partition because all writes hit the same key. A good patch should shard counters across buckets, aggregate them asynchronously, and define the freshness and accuracy guarantees for reads.

## Strong Patch Signals

- Uses write sharding by bucket, time slice, or random suffix for high-volume tenant counters.
- Adds periodic compaction or asynchronous aggregation into a read-optimized total.
- Defines bounded-staleness reads and adds hot-key or throttling metrics.

## Weak Patch Patterns

- Only increases provisioned capacity without addressing the single-key bottleneck.
- Retries throttled writes aggressively, making the hot partition worse.
- Switches databases without workload math or a clear partitioning model.

## Scoring Notes

- Award high scores for describing write distribution, read aggregation, and freshness trade-offs together.
- Penalize answers that hide throttling with retries while losing or delaying usage updates unpredictably.
