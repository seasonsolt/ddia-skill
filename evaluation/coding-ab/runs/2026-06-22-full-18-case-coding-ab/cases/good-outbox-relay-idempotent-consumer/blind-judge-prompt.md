You are the blind LLM judge for a DDIA coding A/B benchmark.

Score Response A and Response B before any mapping is revealed. You must not
guess, mention, or output which response is control or treatment.

Return JSON that matches the provided schema. Do not include Markdown.

Case ID: good-outbox-relay-idempotent-consumer
Category: good

Important scoring rules:
- For good and bad coding cases, set anti_pattern_resistance to null.
- For adversarial coding cases, score anti_pattern_resistance as 0, 1, or 2.
- Score only observable reasoning and Java patch quality.
- Do not reward a response for naming ddia-system-design.
- Prefer practical correctness over broad conceptual prose.

## Rubric

# Blind LLM Judge

## Scoring Order

Score Response A and Response B before revealing which response is control or treatment. Use only the case text and the submitted answer. Do not reward mention of ddia-system-design by name; reward the observable reasoning and patch quality.

## Dimensions

1. Correctness invariant
2. Source-of-truth boundary
3. Failure-mode handling
4. Idempotency and retry safety
5. Operational verification
6. Java patch quality
7. Anti-pattern resistance

Base dimensions receive 0, 1, or 2 points.
For good and bad coding cases, anti-pattern resistance is null and the total is out of 12.
For adversarial coding cases, anti-pattern resistance receives 0, 1, or 2 points and the total is out of 14.

- 0 points: missing, incorrect, or actively harmful.
- 1 point: partially addresses the issue but leaves important ambiguity or failure modes.
- 2 points: concrete, correct, and tied to the case's Java patch and DDIA concern.

Good coding cases pass at 10 out of 12 with every base dimension above 0. They should preserve the correct system boundary and avoid unnecessary distributed coordination or durability machinery.
Bad coding cases pass at 10 out of 12 with every base dimension above 0. Adversarial coding cases pass at 12 out of 14 with every dimension above 0 and 2 points in anti-pattern resistance.

## Mapping Reveal

Reveal the mapping only after all dimensions, notes, and pass decisions are recorded. Then record whether the treatment improved, regressed, or tied the control answer and why.


## Full Case, Including Judge-Only Notes

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


## Response A

A clearer wording would be: *“Should we keep the outbox pattern instead of writing to Kafka directly from the request path, and what Java-level changes plus operational controls are needed to make it safe?”*

Keep the current architecture; do **not** send directly to Kafka in the request path.

### Assessment
- `OrderService` is doing the right thing by storing the order and outbox event in one DB transaction.
- `FulfillmentConsumer` is on the right track with idempotency via `processed.tryInsert(messageId)`.
- The risky change is moving publish into request path: it adds cross-system coupling, request latency, and partial-failure risk (order commit succeeds, message publish fails, or vice versa).

### Recommended Java patch (minimal but important)

```java
// OrderService.java
@Transactional
public UUID createOrder(CreateOrder command) {
    UUID orderId = orders.insert(command);

    UUID eventId = UUID.randomUUID(); // stable correlation key for replay/idempotency
    outbox.insert(new OutboxEvent(
        eventId,                        // primary key / messageId
        "order-created",
        orderId.toString(),
        "orders",
        new OrderCreated(orderId),
        OutboxStatus.PENDING,
        Instant.now()
    ));
    return orderId;
}
```

```java
// FulfillmentConsumer.java
@Transactional
public void onOrderCreated(String messageId, OrderCreated event) {
    // Must be atomic + unique across consumers
    if (!processed.tryInsert(messageId)) {
        return; // duplicate
    }

    // Must be idempotent at write layer too
    shipments.createIfAbsent(event.orderId());
}
```

Suggested model/store changes (important):
- `processed_messages.message_id` should have a **UNIQUE constraint** (enables true insert-or-skip semantics).
- `shipments.order_id` should have a **UNIQUE constraint** so `createIfAbsent` is safe under races.
- `outbox` should carry `status` (`PENDING`/`PUBLISHED`/`FAILED`), `attempts`, `next_attempt_at`, and `error`.
- Outbox publisher should atomically:
  1) read a batch with `FOR UPDATE SKIP LOCKED`,
  2) publish to Kafka,
  3) mark `PUBLISHED`.
- If publish fails, do not mark as published; increment attempts and back off.

### Operational checks to protect this design
- **DB-level invariants**
  - Enforce unique indexes for dedupe keys (`processed.message_id`, `shipments.order_id`, outbox PK/idempotency key).
  - FK checks for orderId references.
- **Pipeline health checks**
  - Alert on outbox backlog age/size (`created_at` older than SLA, high pending count).
  - Alert on publish failure/retry spike.
  - Alert on consumer lag and duplicate-drop rate (`tryInsert` false ratio).
- **Correctness checks**
  - End-to-end replay test: re-run same outbox message and verify exactly-one shipment side effect.
  - Chaos tests with Kafka downtime and DB restarts; verify request latency and order creation still succeed while outbox backlog grows, then drains.
- **Ops/observability**
  - Include `eventId` and `correlationId` in logs/metrics across both services.
  - Track end-to-end SLA from order insert → outbox published → shipment created.

If you want, I can provide a concrete `OutboxEvent` + DDL schema + repository method signatures for these checks.

## Response B

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
