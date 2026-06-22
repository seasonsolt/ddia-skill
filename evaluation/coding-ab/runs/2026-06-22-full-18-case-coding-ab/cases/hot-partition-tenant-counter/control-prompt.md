You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

A multi-tenant API records each request by incrementing a per-tenant usage counter in DynamoDB. Most tenants are small, but one large tenant regularly hits throttling during traffic spikes.

## Java Code

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
