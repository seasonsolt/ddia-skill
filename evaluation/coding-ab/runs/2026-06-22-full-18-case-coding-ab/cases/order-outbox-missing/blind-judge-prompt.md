You are the blind LLM judge for a DDIA coding A/B benchmark.

Score Response A and Response B before any mapping is revealed. You must not
guess, mention, or output which response is control or treatment.

Return JSON that matches the provided schema. Do not include Markdown.

Case ID: order-outbox-missing
Category: bad

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


## Response A

More natural wording: You want a Java code review of the order creation flow and a minimal patch that prevents orders from being written without a fulfillment event, even if the service crashes or Kafka is unavailable.

## Assumptions and workload shape
- Order writes are the primary operation and must be durable in Postgres.
- Fulfillment requires every created order to eventually emit an `OrderCreated` event.
- Duplicates are acceptable only if the fulfillment path can safely deduplicate; losing an event is not acceptable.
- Service restarts and Kafka outages happen.

## Bug and why this is a distributed data problem
- The current code performs a **dual write** to two systems: Postgres (`orders.insert`) and Kafka (`kafka.send`) without atomicity.
- `send` is invoked inside a DB transaction but is not part of the same failure domain as Postgres.
- A crash can produce:
  - DB row committed, Kafka not sent (Kafka down at send time or async failure not observed).
  - Event sent, DB row rolled back (failure before commit).
- `kafka.send` is async and its result is not checked, so producer failures can be silently ignored.
- This is a classic cross-system consistency problem, not a single-DB transaction problem.

## Source of truth and transaction boundaries
- **Source of truth**: Postgres `orders` table.
- Kafka should be treated as a derived, async event stream.
- Keep a durable in-DB intent record (`outbox`) in the same transaction as order creation.
- Publish to Kafka from the outbox in a separate process/thread with retries.

## Minimal correctness patch (practical Java/Spring)
1. Write an outbox row in the same `@Transactional` method as the order insert.
2. Add a publisher worker that reads pending outbox rows and sends them to Kafka.
3. Mark rows as sent only after Kafka send ack.
4. Add consumer-side idempotency (or event-key uniqueness) to handle at-least-once delivery.

```java
// OrderService.java
@Service
@RequiredArgsConstructor
public class OrderService {
  private final OrderRepository orders;
  private final OutboxRepository outbox;
  private final ObjectMapper mapper;

  @Transactional
  public UUID createOrder(CreateOrder command) {
    UUID orderId = orders.insert(command);

    outbox.save(new OutboxEvent(
      UUID.randomUUID(),                 // outbox id
      orderId.toString(),                // aggregateId
      "OrderCreated",                    // eventType
      "orders",                          // topic
      mapper.valueToTree(new OrderCreated(orderId)),
      OutboxStatus.PENDING,
      Instant.now()
    ));

    return orderId;
  }
}
```

```java
// OutboxDispatcher.java
@Component
@RequiredArgsConstructor
public class OutboxDispatcher {
  private final OutboxRepository outbox;
  private final KafkaTemplate<String, OrderCreated> kafka;
  private final ObjectMapper mapper;

  @Scheduled(fixedDelayString = "PT1S")
  @Transactional
  public void dispatch() {
    List<OutboxEvent> batch = outbox.claimNextBatch(100); // PENDING + FOR UPDATE SKIP LOCKED
    for (OutboxEvent event : batch) {
      event.markInFlight();
      outbox.save(event);

      try {
        OrderCreated payload = mapper.treeToValue(event.payload(), OrderCreated.class);
        kafka.send(event.topic(), event.aggregateId(), payload).get(3, TimeUnit.SECONDS);
        event.markSent();
      } catch (Exception ex) {
        event.markFailed(ex.getMessage());
      }
    }
  }
}
```

Database-level idea:
- `outbox.status`: `PENDING`, `IN_FLIGHT`, `SENT`, `FAILED`
- Add indexes on `(status, next_retry_at)` and unique `(aggregate_id, event_type)` if one-time semantics per order event.
- `claimNextBatch` should lock rows (`FOR UPDATE SKIP LOCKED`) to avoid duplicate dispatch by multiple workers.

## Key trade-offs
- This gives **at-least-once** delivery end-to-end, not exactly-once.
- Throughput and reliability improve, with eventual consistency to Kafka.
- Extra writes to outbox increase write I/O and require cleanup/retention of sent rows.

## Failure modes (covered / remaining)
- Crash during `createOrder` before commit: neither order nor outbox row appears.
- Crash after commit before dispatch: row remains `PENDING` and will be retried later.
- Kafka unavailable: rows stay `PENDING/IN_FLIGHT`, no order-loss.
- Dispatcher crash after send ack but before marking `SENT`: duplicate possible; requires idempotent downstream.
- Poisoned message repeatedly failing: keep `FAILED` with capped retry count + dead-letter queue/manual inspection path.

## Idempotency
- Use event key = `orderId` in Kafka so downstream can de-duplicate by aggregate id.
- If fulfillment service is exactly-once-sensitive, add a persisted `processed_events(order_id,event_type)` check before side effects.

## Operational visibility
- Track:
  - `outbox_pending_count`
  - `outbox_inflight_count`
  - `outbox_retry_count` and mean/percentiles
  - max `age_of_oldest_pending`
  - Kafka send failure rate and producer error types
  - reconciliation metric: `orders_created - fulfilled_events_enqueued`
- Alert on stale `PENDING` > expected lag and repeated failures per order.

## Tests / experiments
- Unit/integration:
  1. Inject DB exception after order insert: no outbox row and no fulfilled event.
  2. Inject Kafka unavailability: order persists, outbox stays pending, then recovers and dispatches.
  3. Crash-simulation between send ack and status update: duplicate Kafka event occurs, consumer deduplicates safely.
  4. Multi-instance dispatcher with `FOR UPDATE SKIP LOCKED`: no duplicate dispatch attempts per row.
  5. Backfill/restart test: pending events drained correctly after restart.

## Response B

Your request, phrased more naturally:  
To prevent fulfillment misses after crashes or Kafka outages, make order persistence and event publication atomic by persisting an outbox record in the same DB transaction, then asynchronously publish from a retrying outbox worker.

```diff
// OrderService.java
@@
 public final class OrderService {
     private final OrderRepository orders;
-    private final KafkaTemplate<String, OrderCreated> kafka;
+    private final OutboxRepository outbox;
+    private final ObjectMapper objectMapper;
 
     @Transactional
-    public UUID createOrder(CreateOrder command) {
+    public UUID createOrder(CreateOrder command) throws JsonProcessingException {
         UUID orderId = orders.insert(command);
-        kafka.send("orders", orderId.toString(), new OrderCreated(orderId));
+        outbox.save(OutboxEvent.pending(
+                "orders",
+                orderId.toString(),           // key for idempotency
+                "order.created",
+                objectMapper.writeValueAsString(new OrderCreated(orderId))
+        ));
         return orderId;
     }
 }
```

```java
// OutboxEvent.java
@Entity
@Table(name = "order_outbox")
public class OutboxEvent {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String topic;
    private String eventKey;
    private String eventType;
    @Column(columnDefinition = "jsonb")
    private String payload;

    @Enumerated(EnumType.STRING)
    private OutboxStatus status = OutboxStatus.PENDING;

    private int attempts = 0;
    private Instant createdAt = Instant.now();
    private Instant nextAttemptAt = Instant.now();
    private Instant sentAt;

    private String lastError;

    protected OutboxEvent() {}

    private OutboxEvent(String topic, String eventKey, String eventType, String payload) {
        this.topic = topic;
        this.eventKey = eventKey;
        this.eventType = eventType;
        this.payload = payload;
    }

    public static OutboxEvent pending(String topic, String eventKey, String eventType, String payload) {
        return new OutboxEvent(topic, eventKey, eventType, payload);
    }

    public void markSent() { status = OutboxStatus.SENT; sentAt = Instant.now(); lastError = null; }
    public void markRetry(String error) {
        attempts++;
        status = OutboxStatus.PENDING;
        long delaySeconds = Math.min(60L, (long) Math.pow(2, Math.min(attempts, 10)));
        nextAttemptAt = Instant.now().plusSeconds(delaySeconds);
        lastError = error;
    }

    public boolean isGiveUp(int maxAttempts) { return attempts >= maxAttempts; }
}
```

```java
// OutboxStatus.java
public enum OutboxStatus {
    PENDING,
    SENT
}
```

```java
// OutboxRepository.java
public interface OutboxRepository extends JpaRepository<OutboxEvent, Long> {

    @Query(value = """
        SELECT * FROM order_outbox
         WHERE status = 'PENDING'
           AND next_attempt_at <= :now
         ORDER BY created_at
         LIMIT :limit
         FOR UPDATE SKIP LOCKED
        """, nativeQuery = true)
    List<OutboxEvent> fetchDueEvents(@Param("now") Instant now, @Param("limit") int limit);
}
```

```java
// OutboxPublisher.java
@Component
@RequiredArgsConstructor
public class OutboxPublisher {
    private final KafkaTemplate<String, String> kafka;
    private final OutboxRepository outbox;

    @Transactional
    @Scheduled(fixedDelay = 3000)
    public void publishPending() {
        List<OutboxEvent> events = outbox.fetchDueEvents(Instant.now(), 200);
        for (OutboxEvent e : events) {
            try {
                kafka.send(e.getTopic(), e.getEventKey(), e.getPayload())
                     .get(5, TimeUnit.SECONDS);
                e.markSent();
            } catch (Exception ex) {
                if (e.isGiveUp(10)) {
                    // add a dead-letter/review path here
                    throw new IllegalStateException("outbox message exceeded retry limit for key=" + e.getEventKey(), ex);
                }
                e.markRetry(ex.getMessage());
            }
        }
    }
}
```

Why this works:
- `OrderService#createOrder` now writes both the order and an outbox event in one DB transaction.
- If the service crashes after DB commit, the outbox row remains and will be retried.
- If Kafka is down, the background publisher keeps retrying with backoff instead of dropping the event.
- `eventKey` enables fulfillment-side idempotency, preventing duplicate shipment work if needed.
