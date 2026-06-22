# DDIA Coding Case Coverage Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the Java coding A/B benchmark from a five-case pilot into an 18-case coverage suite that tests whether `ddia-system-design` changes concrete backend implementation boundaries.

**Architecture:** Keep coding cases as Markdown fixtures under `evaluation/coding-ab/cases/`, but add a coverage matrix and deterministic checker rules so missing DDIA themes are caught. Add a prompt renderer that strips judge-only sections before answer generation, because the case files contain answer keys for scoring. The suite should include good, bad, and adversarial Java cases so it measures useful guidance, false positives, and anti-pattern resistance.

**Tech Stack:** Markdown benchmark fixtures, Java snippets embedded in Markdown, Python standard library validation, `unittest`, Codex CLI for optional real LLM pilot runs.

---

## File Structure

- Modify `scripts/check_ddia_benchmark.py`: expand `CODING_AB_CASES`, add expected category counts, add coverage-matrix validation, and validate result-template rows against every coding case.
- Modify `tests/test_ddia_benchmark.py`: add failing tests for the expanded case set, coverage matrix, redacted prompt generation, and result-template rows.
- Create `evaluation/coding-ab/coverage-matrix.md`: maps every coding case to the DDIA topics it covers.
- Modify `evaluation/coding-ab/README.md`: document the expanded case set and the redaction protocol.
- Modify `evaluation/coding-ab/results-template.md`: add one row for every expanded coding case.
- Create `scripts/render_coding_ab_prompt.py`: renders control or treatment prompts without judge-only sections.
- Create 13 new coding cases in `evaluation/coding-ab/cases/`.
- Keep the existing 5 cases:
  - `checkout-cache-as-truth`
  - `order-outbox-missing`
  - `payment-exactly-once-trap`
  - `profile-replica-lag`
  - `redis-distributed-lock-money-transfer`
- Modify `README.md`: update the coding A/B benchmark count and link to the coverage matrix.
- Modify `evaluation/benchmark-guide.md`: add the redacted prompt renderer to the coding A/B run instructions.

## Expanded Case Set

Use this exact case taxonomy.

| Case ID | Category | Main purpose |
| --- | --- | --- |
| good-cache-aside-product-preview | good | Correct cache use where Redis is a preview/read optimization, not the business invariant. |
| good-outbox-relay-idempotent-consumer | good | Correct transactional outbox plus idempotent consumer. |
| good-replica-session-token-routing | good | Correct read-your-writes routing with bounded primary reads. |
| good-expand-contract-schema-rollout | good | Correct schema evolution using expand/contract and backwards compatibility. |
| checkout-cache-as-truth | bad | Existing case: cache used as inventory source of truth. |
| order-outbox-missing | bad | Existing case: database write and Kafka publish are not durably coupled. |
| profile-replica-lag | bad | Existing case: immediate replica read violates read-your-writes. |
| seat-booking-write-skew | bad | Isolation-level bug where two concurrent bookings violate a capacity invariant. |
| schema-migration-breaking-reader | bad | Rolling deploy breaks old readers by removing or renaming a field too early. |
| stream-consumer-non-idempotent | bad | Consumer double-applies side effects during replay or duplicate delivery. |
| hot-partition-tenant-counter | bad | Single hot key or tenant partition collapses under skewed write traffic. |
| retry-storm-no-dlq | bad | Queue worker retries poison messages until it creates backpressure and duplicate side effects. |
| missing-reconciliation-observability | bad | Code has no reconciliation, lag, or invariant metrics for derived data drift. |
| payment-exactly-once-trap | adversarial | Existing case: impossible end-to-end exactly-once payment claim. |
| redis-distributed-lock-money-transfer | adversarial | Existing case: Redis lock used as money-transfer correctness boundary. |
| multi-region-last-write-wins-profile | adversarial | Last-write-wins conflict resolution loses user data across regions. |
| elasticsearch-authorization-trap | adversarial | Search index used as authorization or billing truth. |
| kafka-total-ordering-trap | adversarial | Kafka partition ordering treated as a global invariant or exactly-once substitute. |

## Task 1: Add Coverage Contract Tests

**Files:**
- Modify: `tests/test_ddia_benchmark.py`

- [ ] **Step 1: Add expected expanded coding case constants**

Add this constant near the existing coding A/B test helpers:

```python
EXPECTED_EXPANDED_CODING_AB_CASES = {
    "good-cache-aside-product-preview": "good",
    "good-outbox-relay-idempotent-consumer": "good",
    "good-replica-session-token-routing": "good",
    "good-expand-contract-schema-rollout": "good",
    "checkout-cache-as-truth": "bad",
    "order-outbox-missing": "bad",
    "profile-replica-lag": "bad",
    "seat-booking-write-skew": "bad",
    "schema-migration-breaking-reader": "bad",
    "stream-consumer-non-idempotent": "bad",
    "hot-partition-tenant-counter": "bad",
    "retry-storm-no-dlq": "bad",
    "missing-reconciliation-observability": "bad",
    "payment-exactly-once-trap": "adversarial",
    "redis-distributed-lock-money-transfer": "adversarial",
    "multi-region-last-write-wins-profile": "adversarial",
    "elasticsearch-authorization-trap": "adversarial",
    "kafka-total-ordering-trap": "adversarial",
}

EXPECTED_CODING_COVERAGE_TOPICS = {
    "Correct cache use",
    "Source-of-truth boundary",
    "Transactional outbox",
    "Idempotent consumer",
    "Read-your-writes",
    "Replica lag",
    "Isolation and write skew",
    "Schema evolution",
    "Stream replay and duplicate delivery",
    "Partitioning and hot keys",
    "Backpressure and poison messages",
    "Observability and reconciliation",
    "External side effects",
    "Distributed locks and fencing",
    "Multi-region conflict resolution",
    "Derived data authorization",
    "Ordering guarantees",
}
```

- [ ] **Step 2: Add a failing test for the expanded case registry**

Add this test method to `DdiaBenchmarkTest`:

```python
def test_coding_ab_case_registry_covers_expanded_suite(self):
    checker = load_checker()

    self.assertEqual(checker.CODING_AB_CASES, EXPECTED_EXPANDED_CODING_AB_CASES)
    self.assertEqual(checker.CODING_AB_EXPECTED_CATEGORY_COUNTS, {"good": 4, "bad": 9, "adversarial": 5})
```

- [ ] **Step 3: Add a failing test for the coverage matrix contract**

Add this test method to `DdiaBenchmarkTest`:

```python
def test_coding_ab_coverage_matrix_covers_required_topics(self):
    checker = load_checker()
    matrix_path = REPO / "evaluation" / "coding-ab" / "coverage-matrix.md"
    matrix_text = matrix_path.read_text(encoding="utf-8")

    for case_id in EXPECTED_EXPANDED_CODING_AB_CASES:
        self.assertIn(f"`{case_id}`", matrix_text)

    for topic in EXPECTED_CODING_COVERAGE_TOPICS:
        self.assertIn(topic, matrix_text)

    missing_paths, coding_ab_errors = checker.validate_coding_ab_assets(REPO)
    self.assertEqual(missing_paths, [])
    self.assertEqual(coding_ab_errors, [])
```

- [ ] **Step 4: Add a failing test for result-template rows**

Add this test method to `DdiaBenchmarkTest`:

```python
def test_coding_ab_results_template_has_every_case_row(self):
    template = (REPO / "evaluation" / "coding-ab" / "results-template.md").read_text(encoding="utf-8")

    for case_id in EXPECTED_EXPANDED_CODING_AB_CASES:
        self.assertIn(f"| {case_id} |", template)
```

- [ ] **Step 5: Run tests to verify failure**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_coding_ab_case_registry_covers_expanded_suite
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_coding_ab_coverage_matrix_covers_required_topics
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_coding_ab_results_template_has_every_case_row
```

Expected: FAIL. The checker still has 5 coding cases, the coverage matrix does not exist, and the result template only has 5 coding rows.

- [ ] **Step 6: Commit failing contract tests**

```bash
git add tests/test_ddia_benchmark.py
git commit -m "test: require expanded coding ab coverage"
```

## Task 2: Expand Checker Constants And Coverage Validation

**Files:**
- Modify: `scripts/check_ddia_benchmark.py`
- Modify: `tests/test_ddia_benchmark.py`

- [ ] **Step 1: Replace the coding case registry**

Replace the existing `CODING_AB_CASES` block in `scripts/check_ddia_benchmark.py` with:

```python
CODING_AB_CASES = {
    "good-cache-aside-product-preview": "good",
    "good-outbox-relay-idempotent-consumer": "good",
    "good-replica-session-token-routing": "good",
    "good-expand-contract-schema-rollout": "good",
    "checkout-cache-as-truth": "bad",
    "order-outbox-missing": "bad",
    "profile-replica-lag": "bad",
    "seat-booking-write-skew": "bad",
    "schema-migration-breaking-reader": "bad",
    "stream-consumer-non-idempotent": "bad",
    "hot-partition-tenant-counter": "bad",
    "retry-storm-no-dlq": "bad",
    "missing-reconciliation-observability": "bad",
    "payment-exactly-once-trap": "adversarial",
    "redis-distributed-lock-money-transfer": "adversarial",
    "multi-region-last-write-wins-profile": "adversarial",
    "elasticsearch-authorization-trap": "adversarial",
    "kafka-total-ordering-trap": "adversarial",
}
CODING_AB_EXPECTED_CATEGORY_COUNTS = {"good": 4, "bad": 9, "adversarial": 5}
CODING_AB_COVERAGE_MATRIX_PATH = "evaluation/coding-ab/coverage-matrix.md"
CODING_AB_REQUIRED_TOPICS = {
    "Correct cache use",
    "Source-of-truth boundary",
    "Transactional outbox",
    "Idempotent consumer",
    "Read-your-writes",
    "Replica lag",
    "Isolation and write skew",
    "Schema evolution",
    "Stream replay and duplicate delivery",
    "Partitioning and hot keys",
    "Backpressure and poison messages",
    "Observability and reconciliation",
    "External side effects",
    "Distributed locks and fencing",
    "Multi-region conflict resolution",
    "Derived data authorization",
    "Ordering guarantees",
}
```

- [ ] **Step 2: Include the coverage matrix in required files**

Change `CODING_AB_REQUIRED_FILES` to include the matrix:

```python
CODING_AB_REQUIRED_FILES = [
    "evaluation/coding-ab/README.md",
    "evaluation/coding-ab/control-instructions.md",
    "evaluation/coding-ab/treatment-instructions.md",
    "evaluation/coding-ab/blind-llm-judge.md",
    "evaluation/coding-ab/results-template.md",
    CODING_AB_COVERAGE_MATRIX_PATH,
] + [f"evaluation/coding-ab/cases/{case_id}.md" for case_id in CODING_AB_CASES]
```

- [ ] **Step 3: Add coverage-matrix parser and validator**

Add this function after `markdown_table_first_column_values`:

```python
def markdown_table_rows(body: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in body.splitlines():
        cells = markdown_table_cells(line)
        if cells is not None:
            rows.append(cells)
    return rows
```

Add this validator near the other coding A/B validators:

```python
def validate_coding_ab_coverage_matrix(path: pathlib.Path, relative: str) -> list[str]:
    text = read_text(path)
    errors: list[str] = []
    covered_cases: set[str] = set()
    covered_topics: set[str] = set()

    matrix_body = section_body(text, "Coverage Matrix")
    if matrix_body is None:
        return [f"{relative}: missing section Coverage Matrix"]

    for row in markdown_table_rows(matrix_body):
        if len(row) < 3:
            errors.append(f"{relative}: malformed coverage row for {row[0] if row else '<unknown>'}")
            continue
        case_id = row[0]
        topics = {topic.strip() for topic in row[2].split(",") if topic.strip()}
        if case_id not in CODING_AB_CASES:
            errors.append(f"{relative}: unknown coding case {case_id}")
            continue
        covered_cases.add(case_id)
        covered_topics.update(topics)

    for case_id in CODING_AB_CASES:
        if case_id not in covered_cases:
            errors.append(f"{relative}: missing coverage row for {case_id}")

    for topic in CODING_AB_REQUIRED_TOPICS:
        if topic not in covered_topics:
            errors.append(f"{relative}: missing coverage topic {topic}")

    for topic in sorted(covered_topics - CODING_AB_REQUIRED_TOPICS):
        errors.append(f"{relative}: unknown coverage topic {topic}")

    return errors
```

- [ ] **Step 4: Validate category counts**

Add this helper near the coding validators:

```python
def validate_coding_ab_category_counts(relative: str = "coding_ab_registry") -> list[str]:
    counts = {"good": 0, "bad": 0, "adversarial": 0}
    errors: list[str] = []
    for category in CODING_AB_CASES.values():
        if category not in counts:
            errors.append(f"{relative}: unknown coding category {category}")
            continue
        counts[category] += 1

    if counts != CODING_AB_EXPECTED_CATEGORY_COUNTS:
        errors.append(f"{relative}: expected category counts {CODING_AB_EXPECTED_CATEGORY_COUNTS}, found {counts}")
    return errors
```

- [ ] **Step 5: Call the new validators**

Inside `validate_coding_ab_assets`, after the file loop, add:

```python
    errors.extend(validate_coding_ab_category_counts())
```

Inside `validate_coding_ab_assets`, after the result-template validation block, add:

```python
    coverage_matrix = repo / CODING_AB_COVERAGE_MATRIX_PATH
    if coverage_matrix.exists():
        errors.extend(validate_coding_ab_coverage_matrix(coverage_matrix, CODING_AB_COVERAGE_MATRIX_PATH))
```

- [ ] **Step 6: Update the test helper registry**

In `tests/test_ddia_benchmark.py`, update `make_complete_coding_ab_assets` so its `cases` dict matches `EXPECTED_EXPANDED_CODING_AB_CASES`.

Use:

```python
    cases = EXPECTED_EXPANDED_CODING_AB_CASES
```

- [ ] **Step 7: Run tests to verify failure is now only missing files/docs**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_coding_ab_case_registry_covers_expanded_suite
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_current_repo_coding_ab_assets_are_complete
```

Expected: registry test PASS. Current repo completeness test FAIL with missing new case files and coverage matrix.

- [ ] **Step 8: Commit checker expansion**

```bash
git add scripts/check_ddia_benchmark.py tests/test_ddia_benchmark.py
git commit -m "test: expand coding ab coverage contract"
```

## Task 3: Add Good Coding Cases

**Files:**
- Create: `evaluation/coding-ab/cases/good-cache-aside-product-preview.md`
- Create: `evaluation/coding-ab/cases/good-outbox-relay-idempotent-consumer.md`
- Create: `evaluation/coding-ab/cases/good-replica-session-token-routing.md`
- Create: `evaluation/coding-ab/cases/good-expand-contract-schema-rollout.md`

- [ ] **Step 1: Add `good-cache-aside-product-preview.md`**

Create `evaluation/coding-ab/cases/good-cache-aside-product-preview.md` with this structure:

```markdown
# Coding Case: good-cache-aside-product-preview

Case ID: good-cache-aside-product-preview
Category: good
Language: Java
Primary DDIA topics: Correct cache use, source-of-truth boundary, derived data

## Scenario

A product page service uses Redis to speed up product previews, but checkout and pricing still read from Postgres. The team asks whether this cache usage should be rejected or patched.

## Flawed Java

```java
public final class ProductPreviewService {
    private final RedisClient redis;
    private final ProductRepository products;

    public ProductPreview preview(String sku) {
        String cached = redis.get("product-preview:" + sku);
        if (cached != null) {
            return ProductPreview.fromJson(cached);
        }

        Product product = products.findForPreview(sku);
        ProductPreview preview = ProductPreview.from(product.id(), product.name(), product.thumbnailUrl());
        redis.setex("product-preview:" + sku, 300, preview.toJson());
        return preview;
    }
}
```

## Task

Review the code and propose a Java-oriented patch only if needed. Keep the answer focused on whether Redis is being used safely and what tests or operational checks would protect this design.

## Expected DDIA Reasoning

The answer should not reject all caching. It should identify Redis as derived preview data, keep business decisions such as checkout price and availability outside this cache, and recommend bounded TTL, invalidation, and metrics for stale previews.

## Strong Patch Signals

- States that this is acceptable if preview data is non-authoritative.
- Keeps checkout, payment, authorization, and inventory decisions on durable sources.
- Adds stale-cache tests, invalidation tests, and cache-hit/stale-age metrics.

## Weak Patch Patterns

- Removes Redis because "caches are unsafe" without distinguishing preview data from business invariants.
- Moves checkout price or inventory decisions into the preview cache.
- Adds distributed locks around preview reads.

## Scoring Notes

- Award high scores for avoiding false positives and preserving the derived-data boundary.
- Penalize answers that over-engineer a read-only preview path.
```

- [ ] **Step 2: Add `good-outbox-relay-idempotent-consumer.md`**

Use this Java snippet in the `Flawed Java` section:

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

Use these required sections:

- Scenario: an engineer already uses a transactional outbox and idempotent consumer and asks whether to replace it with synchronous Kafka send.
- Expected DDIA Reasoning: keep the outbox; verify relay acknowledgement, duplicate publish, and consumer idempotency.
- Strong Patch Signals: preserves order/outbox atomicity, keeps idempotent consumer, adds relay lag and duplicate metrics.
- Weak Patch Patterns: removes outbox, assumes Kafka send in the request transaction is safer, ignores duplicate delivery.

- [ ] **Step 3: Add `good-replica-session-token-routing.md`**

Use this Java snippet:

```java
public final class ProfileService {
    private final ProfilePrimaryRepository primary;
    private final ProfileReplicaRepository replica;

    public UpdatedProfile updateDisplayName(UUID userId, String displayName) {
        Profile saved = primary.updateDisplayNameReturningRow(userId, displayName);
        return new UpdatedProfile(saved, saved.version());
    }

    public Profile readProfile(UUID userId, long minVersion) {
        Optional<Profile> fromReplica = replica.findByIdAtLeastVersion(userId, minVersion);
        return fromReplica.orElseGet(() -> primary.findById(userId));
    }
}
```

Use these required sections:

- Scenario: the service returns the primary write result and later uses a version token to avoid stale replica reads.
- Expected DDIA Reasoning: this protects read-your-writes without routing every read to primary.
- Strong Patch Signals: keeps bounded primary fallback, version/LSN routing, replica-lag metrics.
- Weak Patch Patterns: removes all replicas, adds sleep, or claims eventual consistency is always fine.

- [ ] **Step 4: Add `good-expand-contract-schema-rollout.md`**

Use this Java snippet:

```java
public final class UserWriter {
    private final JdbcTemplate jdbc;

    public void updateName(UUID userId, String fullName) {
        NameParts parts = NameParts.parse(fullName);
        jdbc.update(
            "UPDATE users SET full_name = ?, given_name = ?, family_name = ? WHERE id = ?",
            fullName,
            parts.givenName(),
            parts.familyName(),
            userId
        );
    }
}

public final class UserReader {
    public UserDto map(ResultSet rs) throws SQLException {
        String fullName = rs.getString("full_name");
        String givenName = rs.getString("given_name");
        String familyName = rs.getString("family_name");
        return new UserDto(fullName, givenName, familyName);
    }
}
```

Use these required sections:

- Scenario: the team is halfway through an expand/contract migration from `full_name` to split name columns.
- Expected DDIA Reasoning: dual-write is acceptable during the compatibility window if backfill, validation, and reader compatibility are explicit.
- Strong Patch Signals: preserves old and new columns, adds backfill reconciliation, names contract preconditions.
- Weak Patch Patterns: deletes `full_name` immediately, ignores old readers, or treats JSON/nullable fields as enough.

- [ ] **Step 5: Run the focused checker**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON scripts/check_ddia_benchmark.py --repo .
```

Expected: still FAIL because bad/adversarial expansion cases and coverage matrix are not complete.

- [ ] **Step 6: Commit good cases**

```bash
git add evaluation/coding-ab/cases/good-cache-aside-product-preview.md \
  evaluation/coding-ab/cases/good-outbox-relay-idempotent-consumer.md \
  evaluation/coding-ab/cases/good-replica-session-token-routing.md \
  evaluation/coding-ab/cases/good-expand-contract-schema-rollout.md
git commit -m "testdata: add good coding ab cases"
```

## Task 4: Add Bad Coding Cases

**Files:**
- Create: `evaluation/coding-ab/cases/seat-booking-write-skew.md`
- Create: `evaluation/coding-ab/cases/schema-migration-breaking-reader.md`
- Create: `evaluation/coding-ab/cases/stream-consumer-non-idempotent.md`
- Create: `evaluation/coding-ab/cases/hot-partition-tenant-counter.md`
- Create: `evaluation/coding-ab/cases/retry-storm-no-dlq.md`
- Create: `evaluation/coding-ab/cases/missing-reconciliation-observability.md`

- [ ] **Step 1: Add `seat-booking-write-skew.md`**

Use this Java snippet:

```java
public final class SeatBookingService {
    private final BookingRepository bookings;

    @Transactional
    public Booking book(UUID eventId, UUID userId) {
        int booked = bookings.countConfirmed(eventId);
        Event event = bookings.findEvent(eventId);
        if (booked >= event.capacity()) {
            throw new SoldOutException(eventId);
        }
        return bookings.insert(new Booking(eventId, userId, "CONFIRMED"));
    }
}
```

Required reasoning:

- Expected DDIA Reasoning: count-then-insert can write-skew under concurrent transactions unless a durable invariant is enforced by row lock, conditional update, exclusion constraint, serializable isolation, or reservation table.
- Strong Patch Signals: uses conditional capacity decrement or locked event row, adds idempotency key, tests concurrent overbooking.
- Weak Patch Patterns: adds Java `synchronized`, Redis lock, or retry without invariant.

- [ ] **Step 2: Add `schema-migration-breaking-reader.md`**

Use this Java snippet:

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

Required reasoning:

- Expected DDIA Reasoning: producer changed schema before all readers were compatible; patch should use additive fields, versioned topics or compatibility checks, dual-publish/dual-read during rollout, and consumer contract tests.
- Strong Patch Signals: keeps `amountCents` during migration, adds schema registry compatibility gate, backfills or transforms safely.
- Weak Patch Patterns: says JSON is flexible, catches null and defaults to zero, or upgrades all consumers manually without rollout proof.

- [ ] **Step 3: Add `stream-consumer-non-idempotent.md`**

Use this Java snippet:

```java
public final class LoyaltyConsumer {
    private final LoyaltyRepository loyalty;

    public void onPaymentCaptured(PaymentCaptured event) {
        int points = event.amountCents() / 100;
        loyalty.addPoints(event.userId(), points);
    }
}
```

Required reasoning:

- Expected DDIA Reasoning: event delivery and replay can duplicate side effects; patch should record processed event IDs or make the sink idempotent.
- Strong Patch Signals: unique processed-message table, transactional points update, replay tests, duplicate-message tests.
- Weak Patch Patterns: relies on Kafka exactly-once alone, uses in-memory set, or swallows duplicate exceptions after side effect.

- [ ] **Step 4: Add `hot-partition-tenant-counter.md`**

Use this Java snippet:

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

Required reasoning:

- Expected DDIA Reasoning: a single hot tenant creates a hot partition; patch should shard counters, aggregate asynchronously, and define read freshness.
- Strong Patch Signals: write sharding by bucket, periodic compaction, bounded-staleness reads, hot-key metrics.
- Weak Patch Patterns: increases provisioned capacity only, retries throttled writes, or switches databases without workload math.

- [ ] **Step 5: Add `retry-storm-no-dlq.md`**

Use this Java snippet:

```java
public final class EmailWorker {
    private final QueueClient queue;
    private final EmailSender sender;

    public void handle(Message message) {
        EmailJob job = EmailJob.fromJson(message.body());
        sender.send(job.to(), job.subject(), job.body());
        queue.ack(message.id());
    }
}
```

Required reasoning:

- Expected DDIA Reasoning: failures after send and before ack can duplicate email; poison messages can retry forever. Patch should add idempotency keys, bounded retries, DLQ, and retry metrics.
- Strong Patch Signals: idempotent send key, attempt count, dead-letter path, visibility timeout handling, duplicate-send tests.
- Weak Patch Patterns: catches all exceptions and acks, retries forever, or adds sleep without backpressure.

- [ ] **Step 6: Add `missing-reconciliation-observability.md`**

Use this Java snippet:

```java
public final class SearchIndexUpdater {
    private final ProductRepository products;
    private final SearchClient search;

    public void updateProduct(UUID productId, ProductPatch patch) {
        Product product = products.update(productId, patch);
        search.index("products", productId.toString(), ProductDocument.from(product));
    }
}
```

Required reasoning:

- Expected DDIA Reasoning: search is derived data and can drift from Postgres; patch should use outbox or durable change log, reconciliation, lag metrics, and runbook checks.
- Strong Patch Signals: durable indexing event, idempotent indexer, reindex job, drift metric, failure injection.
- Weak Patch Patterns: retries `search.index` inline only, treats search as authoritative, or ignores index lag.

- [ ] **Step 7: Run the focused checker**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON scripts/check_ddia_benchmark.py --repo .
```

Expected: still FAIL because adversarial expansion cases and coverage matrix are incomplete.

- [ ] **Step 8: Commit bad cases**

```bash
git add evaluation/coding-ab/cases/seat-booking-write-skew.md \
  evaluation/coding-ab/cases/schema-migration-breaking-reader.md \
  evaluation/coding-ab/cases/stream-consumer-non-idempotent.md \
  evaluation/coding-ab/cases/hot-partition-tenant-counter.md \
  evaluation/coding-ab/cases/retry-storm-no-dlq.md \
  evaluation/coding-ab/cases/missing-reconciliation-observability.md
git commit -m "testdata: add bad coding ab cases"
```

## Task 5: Add Adversarial Coding Cases

**Files:**
- Create: `evaluation/coding-ab/cases/multi-region-last-write-wins-profile.md`
- Create: `evaluation/coding-ab/cases/elasticsearch-authorization-trap.md`
- Create: `evaluation/coding-ab/cases/kafka-total-ordering-trap.md`

- [ ] **Step 1: Add `multi-region-last-write-wins-profile.md`**

Use this Java snippet:

```java
public final class ProfileConflictResolver {
    public Profile resolve(Profile local, Profile remote) {
        return local.updatedAt().isAfter(remote.updatedAt()) ? local : remote;
    }
}
```

Required reasoning:

- Expected DDIA Reasoning: last-write-wins can lose independent updates across regions. Patch should merge per-field where valid, use versions/vector clocks or conflict records, and define product-visible conflict behavior.
- Strong Patch Signals: rejects blanket LWW for user data, preserves both conflicting values, adds conflict queue or CRDT-style merge only where valid.
- Weak Patch Patterns: trusts wall-clock timestamps, increases NTP precision, or silently overwrites.
- Scoring Notes: this adversarial case requires anti-pattern resistance score 2 to pass.

- [ ] **Step 2: Add `elasticsearch-authorization-trap.md`**

Use this Java snippet:

```java
public final class DocumentAccessService {
    private final SearchClient search;

    public boolean canView(UUID userId, UUID documentId) {
        SearchHit hit = search.get("document_permissions", documentId.toString());
        return hit.allowedUserIds().contains(userId.toString());
    }
}
```

Required reasoning:

- Expected DDIA Reasoning: Elasticsearch is a derived index and should not be the authorization source of truth. Patch should check durable permission data and use the index only for candidate retrieval.
- Strong Patch Signals: durable authorization repository, post-filtering search results, index lag metrics, deny-by-default on ambiguity.
- Weak Patch Patterns: refreshes the index synchronously, adds cache TTL, or treats search hits as permission proof.
- Scoring Notes: this adversarial case tests derived-data anti-pattern resistance.

- [ ] **Step 3: Add `kafka-total-ordering-trap.md`**

Use this Java snippet:

```java
public final class AccountEventConsumer {
    private final AccountRepository accounts;

    public void onEvent(AccountEvent event) {
        Account account = accounts.find(event.accountId());
        if (event.sequence() <= account.lastSequence()) {
            return;
        }
        accounts.save(account.apply(event));
    }
}
```

Required reasoning:

- Expected DDIA Reasoning: Kafka only orders within a partition; the patch must ensure all events for an account share a partition key or move the invariant into a durable sequence check.
- Strong Patch Signals: partitions by account ID, uses conditional update on sequence, handles gaps, replay, and duplicate delivery.
- Weak Patch Patterns: assumes Kafka gives global order, uses timestamps, or ignores repartitioning during deployment.
- Scoring Notes: this adversarial case tests ordering guarantees and idempotent stream processing.

- [ ] **Step 4: Run the focused checker**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON scripts/check_ddia_benchmark.py --repo .
```

Expected: still FAIL until coverage matrix and templates include all 18 case rows.

- [ ] **Step 5: Commit adversarial cases**

```bash
git add evaluation/coding-ab/cases/multi-region-last-write-wins-profile.md \
  evaluation/coding-ab/cases/elasticsearch-authorization-trap.md \
  evaluation/coding-ab/cases/kafka-total-ordering-trap.md
git commit -m "testdata: add adversarial coding ab cases"
```

## Task 6: Add Coverage Matrix And Template Rows

**Files:**
- Create: `evaluation/coding-ab/coverage-matrix.md`
- Modify: `evaluation/coding-ab/results-template.md`
- Modify: `evaluation/coding-ab/README.md`

- [ ] **Step 1: Create the coverage matrix**

Create `evaluation/coding-ab/coverage-matrix.md` with this table:

```markdown
# DDIA Coding A/B Coverage Matrix

## Coverage Matrix

| Case | Category | Topics |
| --- | --- | --- |
| good-cache-aside-product-preview | good | Correct cache use, Source-of-truth boundary |
| good-outbox-relay-idempotent-consumer | good | Transactional outbox, Idempotent consumer |
| good-replica-session-token-routing | good | Read-your-writes, Replica lag |
| good-expand-contract-schema-rollout | good | Schema evolution |
| checkout-cache-as-truth | bad | Source-of-truth boundary, Correct cache use |
| order-outbox-missing | bad | Transactional outbox, Observability and reconciliation |
| profile-replica-lag | bad | Read-your-writes, Replica lag |
| seat-booking-write-skew | bad | Isolation and write skew |
| schema-migration-breaking-reader | bad | Schema evolution |
| stream-consumer-non-idempotent | bad | Stream replay and duplicate delivery, Idempotent consumer |
| hot-partition-tenant-counter | bad | Partitioning and hot keys |
| retry-storm-no-dlq | bad | Backpressure and poison messages, External side effects |
| missing-reconciliation-observability | bad | Observability and reconciliation |
| payment-exactly-once-trap | adversarial | External side effects |
| redis-distributed-lock-money-transfer | adversarial | Distributed locks and fencing |
| multi-region-last-write-wins-profile | adversarial | Multi-region conflict resolution |
| elasticsearch-authorization-trap | adversarial | Derived data authorization, Source-of-truth boundary |
| kafka-total-ordering-trap | adversarial | Ordering guarantees, Stream replay and duplicate delivery |
```

- [ ] **Step 2: Update result-template case rows**

Replace the `## Case Scores` table in `evaluation/coding-ab/results-template.md` with:

```markdown
| Case | Category | Control score | Treatment score | Lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| good-cache-aside-product-preview | good |  |  |  |  |  |
| good-outbox-relay-idempotent-consumer | good |  |  |  |  |  |
| good-replica-session-token-routing | good |  |  |  |  |  |
| good-expand-contract-schema-rollout | good |  |  |  |  |  |
| checkout-cache-as-truth | bad |  |  |  |  |  |
| order-outbox-missing | bad |  |  |  |  |  |
| profile-replica-lag | bad |  |  |  |  |  |
| seat-booking-write-skew | bad |  |  |  |  |  |
| schema-migration-breaking-reader | bad |  |  |  |  |  |
| stream-consumer-non-idempotent | bad |  |  |  |  |  |
| hot-partition-tenant-counter | bad |  |  |  |  |  |
| retry-storm-no-dlq | bad |  |  |  |  |  |
| missing-reconciliation-observability | bad |  |  |  |  |  |
| payment-exactly-once-trap | adversarial |  |  |  |  |  |
| redis-distributed-lock-money-transfer | adversarial |  |  |  |  |  |
| multi-region-last-write-wins-profile | adversarial |  |  |  |  |  |
| elasticsearch-authorization-trap | adversarial |  |  |  |  |  |
| kafka-total-ordering-trap | adversarial |  |  |  |  |  |
```

- [ ] **Step 3: Update README case-set wording**

In `evaluation/coding-ab/README.md`, update `## Case Set` to mention:

```markdown
The expanded coding suite has 18 cases:

- 4 good cases that check whether the skill avoids false positives and over-design.
- 9 bad cases that check ordinary implementation bug detection.
- 5 adversarial cases that check unsafe-premise resistance.

The full topic mapping is in `evaluation/coding-ab/coverage-matrix.md`.
```

- [ ] **Step 4: Run template and coverage tests**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_coding_ab_coverage_matrix_covers_required_topics
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_coding_ab_results_template_has_every_case_row
$PYTHON scripts/check_ddia_benchmark.py --repo .
```

Expected: PASS for the focused tests and checker.

- [ ] **Step 5: Commit coverage docs**

```bash
git add evaluation/coding-ab/coverage-matrix.md evaluation/coding-ab/results-template.md evaluation/coding-ab/README.md
git commit -m "docs: add coding ab coverage matrix"
```

## Task 7: Add Redacted Prompt Renderer

**Files:**
- Create: `scripts/render_coding_ab_prompt.py`
- Modify: `tests/test_ddia_benchmark.py`
- Modify: `evaluation/coding-ab/README.md`
- Modify: `evaluation/benchmark-guide.md`

- [ ] **Step 1: Write failing renderer tests**

Add this helper to `tests/test_ddia_benchmark.py`:

```python
def load_prompt_renderer():
    module_path = REPO / "scripts" / "render_coding_ab_prompt.py"
    spec = importlib.util.spec_from_file_location("render_coding_ab_prompt", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
```

Add this test:

```python
def test_coding_ab_prompt_renderer_strips_judge_only_sections(self):
    renderer = load_prompt_renderer()
    case_path = REPO / "evaluation" / "coding-ab" / "cases" / "checkout-cache-as-truth.md"

    prompt = renderer.render_prompt(
        repo=REPO,
        case_path=case_path,
        arm="control",
        skill_path=REPO / "skills" / "ddia-system-design" / "SKILL.md",
    )

    self.assertIn("## Scenario", prompt)
    self.assertIn("## Flawed Java", prompt)
    self.assertIn("## Task", prompt)
    self.assertIn("Coding Control Instructions", prompt)
    self.assertNotIn("Primary DDIA topics", prompt)
    self.assertNotIn("Expected DDIA Reasoning", prompt)
    self.assertNotIn("Strong Patch Signals", prompt)
    self.assertNotIn("Weak Patch Patterns", prompt)
    self.assertNotIn("Scoring Notes", prompt)
```

Add this test:

```python
def test_coding_ab_treatment_prompt_includes_skill_text_but_no_judge_key(self):
    renderer = load_prompt_renderer()
    case_path = REPO / "evaluation" / "coding-ab" / "cases" / "checkout-cache-as-truth.md"

    prompt = renderer.render_prompt(
        repo=REPO,
        case_path=case_path,
        arm="treatment",
        skill_path=REPO / "skills" / "ddia-system-design" / "SKILL.md",
    )

    self.assertIn("Coding Treatment Instructions", prompt)
    self.assertIn("# DDIA System Design", prompt)
    self.assertIn("## Scenario", prompt)
    self.assertNotIn("Expected DDIA Reasoning", prompt)
    self.assertNotIn("Strong Patch Signals", prompt)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_coding_ab_prompt_renderer_strips_judge_only_sections
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_coding_ab_treatment_prompt_includes_skill_text_but_no_judge_key
```

Expected: FAIL because `scripts/render_coding_ab_prompt.py` does not exist.

- [ ] **Step 3: Create the renderer**

Create `scripts/render_coding_ab_prompt.py`:

```python
#!/usr/bin/env python3
import argparse
import pathlib
import sys


ANSWER_VISIBLE_SECTIONS = ["Scenario", "Flawed Java", "Task"]
ARM_INSTRUCTIONS = {
    "control": "evaluation/coding-ab/control-instructions.md",
    "treatment": "evaluation/coding-ab/treatment-instructions.md",
}


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def section_body(text: str, heading: str) -> str:
    marker = f"## {heading}"
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            body = []
            for body_line in lines[index + 1 :]:
                if body_line.startswith("## "):
                    break
                body.append(body_line)
            return "\n".join(body).strip()
    raise ValueError(f"missing section {heading}")


def render_case_for_answer_model(case_text: str) -> str:
    rendered = ["# Coding Case"]
    for heading in ANSWER_VISIBLE_SECTIONS:
        rendered.append(f"## {heading}")
        rendered.append(section_body(case_text, heading))
    return "\n\n".join(rendered).strip() + "\n"


def render_prompt(
    *,
    repo: pathlib.Path,
    case_path: pathlib.Path,
    arm: str,
    skill_path: pathlib.Path,
) -> str:
    if arm not in ARM_INSTRUCTIONS:
        raise ValueError(f"arm must be one of {sorted(ARM_INSTRUCTIONS)}")

    parts = [
        "You are participating in a coding A/B benchmark.",
        "Do not edit files, do not run commands, and do not mention this benchmark setup.",
        "Produce the answer only.",
        read_text(repo / ARM_INSTRUCTIONS[arm]).strip(),
    ]
    if arm == "treatment":
        parts.append("# ddia-system-design skill instructions\n\n" + read_text(skill_path).strip())

    parts.append(render_case_for_answer_model(read_text(case_path)).strip())
    return "\n\n".join(parts).strip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--case", type=pathlib.Path, required=True)
    parser.add_argument("--arm", choices=sorted(ARM_INSTRUCTIONS), required=True)
    parser.add_argument(
        "--skill-path",
        type=pathlib.Path,
        default=pathlib.Path("skills/ddia-system-design/SKILL.md"),
    )
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    case_path = args.case if args.case.is_absolute() else repo / args.case
    skill_path = args.skill_path if args.skill_path.is_absolute() else repo / args.skill_path

    sys.stdout.write(render_prompt(repo=repo, case_path=case_path, arm=args.arm, skill_path=skill_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Update docs to require the renderer**

Add this paragraph to `evaluation/coding-ab/README.md` under `## Method`:

```markdown
Use `scripts/render_coding_ab_prompt.py` to generate answer prompts. Do not feed
the raw case file to the answer model, because raw case files include judge-only
sections such as expected reasoning, strong patch signals, weak patch patterns,
and scoring notes.
```

Add this command to `evaluation/benchmark-guide.md`:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON scripts/render_coding_ab_prompt.py --repo . --arm control --case evaluation/coding-ab/cases/checkout-cache-as-truth.md > /tmp/ddia-control-prompt.md
$PYTHON scripts/render_coding_ab_prompt.py --repo . --arm treatment --case evaluation/coding-ab/cases/checkout-cache-as-truth.md > /tmp/ddia-treatment-prompt.md
```

- [ ] **Step 5: Run renderer tests**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_coding_ab_prompt_renderer_strips_judge_only_sections
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_coding_ab_treatment_prompt_includes_skill_text_but_no_judge_key
```

Expected: PASS.

- [ ] **Step 6: Commit renderer**

```bash
git add scripts/render_coding_ab_prompt.py tests/test_ddia_benchmark.py evaluation/coding-ab/README.md evaluation/benchmark-guide.md
git commit -m "feat: render redacted coding ab prompts"
```

## Task 8: Update Top-Level Docs And Validation Status

**Files:**
- Modify: `README.md`
- Modify: `evaluation/benchmark-guide.md`
- Modify: `evaluation/coding-ab/pilot-results.md`

- [ ] **Step 1: Update README coding benchmark section**

Replace the coding benchmark paragraph in `README.md` with:

```markdown
The coding A/B benchmark now has 18 Java cases: 4 good cases, 9 bad cases, and
5 adversarial cases. The coverage matrix is in
[`evaluation/coding-ab/coverage-matrix.md`](evaluation/coding-ab/coverage-matrix.md).
Use `scripts/render_coding_ab_prompt.py` for answer generation so judge-only
sections are not leaked to the model.
```

- [ ] **Step 2: Update benchmark guide**

In `evaluation/benchmark-guide.md`, add a short coding A/B run checklist:

```markdown
For coding A/B runs:

1. Render prompts with `scripts/render_coding_ab_prompt.py`.
2. Run control and treatment with the same model and settings.
3. Randomize Response A and Response B before judging.
4. Score with `evaluation/coding-ab/blind-llm-judge.md`.
5. Archive the generated responses, mapping, and judge JSON under `evaluation/coding-ab/runs/<date>-<case-id>/`.
6. Record scores in `evaluation/coding-ab/results-template.md` or a dated result file.
```

- [ ] **Step 3: Update pilot-results caveat**

In `evaluation/coding-ab/pilot-results.md`, add:

```markdown
This pilot used the original five-case pilot suite. The expanded 18-case suite
should be used for the next run. Future runs should use the prompt renderer
instead of hand-built prompts.
```

- [ ] **Step 4: Run docs validation**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON scripts/check_ddia_skill_quality.py --repo .
$PYTHON scripts/check_ddia_benchmark.py --repo .
```

Expected: both commands PASS.

- [ ] **Step 5: Commit docs**

```bash
git add README.md evaluation/benchmark-guide.md evaluation/coding-ab/pilot-results.md
git commit -m "docs: document expanded coding ab suite"
```

## Task 9: Full Verification And Push

**Files:**
- No new files.

- [ ] **Step 1: Run full unit suite**

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON -m unittest discover -s tests
```

Expected: all tests PASS, with the existing expected skip still allowed.

- [ ] **Step 2: Run deterministic validators**

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON scripts/check_ddia_skill_quality.py --repo .
$PYTHON scripts/check_ddia_benchmark.py --repo .
```

Expected: both validators PASS. `check_ddia_benchmark.py` should report no `coding_ab_missing_paths` and no `coding_ab_errors`.

- [ ] **Step 3: Run whitespace check**

```bash
git diff --check
```

Expected: no output and exit code 0.

- [ ] **Step 4: Inspect final status**

```bash
git status --short --branch
git log --oneline --decorate -5
```

Expected: branch is ahead of `origin/codex/ddia-system-design-skill` by the new commits and has no uncommitted files.

- [ ] **Step 5: Push**

```bash
git push origin codex/ddia-system-design-skill
```

Expected: push succeeds and the branch matches remote.

## Self-Review

- Spec coverage: The plan covers good cases, bad cases, adversarial cases, isolation/write-skew, schema migration, stream replay, hot partitions, derived-data authorization, multi-region conflict, observability, retries, DLQ behavior, and redacted prompt generation.
- Placeholder scan: The plan contains exact case IDs, exact target files, exact commands, exact checker constants, and exact renderer code.
- Type consistency: The case IDs in `EXPECTED_EXPANDED_CODING_AB_CASES`, `CODING_AB_CASES`, `coverage-matrix.md`, and `results-template.md` match.

## Execution Options

Plan complete and saved to `docs/superpowers/plans/2026-06-22-ddia-coding-case-coverage-expansion.md`.

1. Subagent-Driven (recommended): dispatch a fresh subagent per task, review between tasks, fast iteration.
2. Inline Execution: execute tasks in this session with checkpoints.
