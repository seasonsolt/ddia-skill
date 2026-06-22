# DDIA Skill Pilot A/B Results

## Run Metadata

- Evaluator: Codex
- Date: 2026-06-22
- Model: GPT-5 Codex
- Skill version: `708110e`

## Pilot Case Coverage

- `evaluation/cases/good/01-order-consistency.md`
- `evaluation/cases/good/04-replica-lag.md`
- `evaluation/cases/bad/01-cache-as-truth.md`
- `evaluation/cases/adversarial/02-exactly-once-trap.md`
- `evaluation/cases/bad/04-vague-startup-architecture.md`

## Hidden Mapping

- Response A: control
- Response B: treatment

## Case Scores

| Case | Category | Control score | Treatment score | Lift | Control normalized | Treatment normalized | Normalized lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| order-consistency | good | 7/10 | 9/10 | +2 | 70.0% | 90.0% | +20.0 pp | fail to pass | Treatment added clearer source-of-truth boundaries, idempotency, reconciliation, and falsifiable checks. |
| replica-lag | good | 7/10 | 10/10 | +3 | 70.0% | 100.0% | +30.0 pp | fail to pass | Treatment named read-your-writes and monotonic reads, then tied mitigations to session routing and lag metrics. |
| cache-as-truth | bad | 8/12 | 11/12 | +3 | 66.7% | 91.7% | +25.0 pp | fail to pass | Treatment rejected Redis as authoritative for payment decisions and kept financial invariants in transactional storage. |
| exactly-once-trap | adversarial | 8/12 | 11/12 | +3 | 66.7% | 91.7% | +25.0 pp | fail to pass | Treatment challenged end-to-end exactly-once and added idempotency boundaries for external side effects and ledger writes. |
| vague-startup-architecture | bad | 8/12 | 10/12 | +2 | 66.7% | 83.3% | +16.7 pp | diagnostic improvement | Treatment gave a scoped default, listed missing requirements, and avoided overconfident database selection. |

## Dimension Differences

- Workload framing: treatment improved by asking for load, latency, skew, or freshness assumptions in four of five cases.
- Trade-off quality: treatment improved by naming latency, availability, correctness, and operational costs instead of only recommending tools.
- Failure-mode coverage: treatment improved by naming cache staleness, replica lag, duplicate side effects, retries, and reconciliation paths.
- Correctness reasoning: treatment improved by tying design choices to source of truth, read guarantees, financial invariants, and idempotency.
- Verification value: treatment improved by adding concrete tests, metrics, and reconciliation checks across all five cases.
- Anti-pattern resistance: treatment improved on all three bad or adversarial cases by challenging the unsafe premise directly.

## Response Archive

### order-consistency

#### Response A

The design can work if the relational database remains the main store for orders and Redis is only a cache. The main risks are stale order status, inventory updates arriving late, and users seeing inconsistent history during cancellation. I would keep order writes in the relational database, publish inventory events after the order transaction, and make inventory consumers idempotent. Add monitoring for failed events, retry queues, and cache hit rates. Test order placement, cancellation, event retry, and Redis loss.

#### Response B

Assumptions and workload shape: orders need durable state transitions, users expect order history to reflect committed order writes, and inventory updates may lag because they cross a service boundary. The relational order database should own order state. Redis should be a derived cache, and inventory events should be an asynchronous integration path.

Recommendation: keep order creation and cancellation in one transactional order boundary. Publish inventory changes through a transactional outbox so the database commit and event publication cannot silently diverge. Make inventory consumers idempotent and reconcile order state against inventory reservations.

Key trade-offs: asynchronous inventory events reduce coupling and write latency, but they create temporary inconsistency. Redis improves read latency, but it can be stale or lost. Stronger coordination with inventory can reduce oversell risk, but it adds latency and availability coupling.

Failure modes: event publish after commit can fail, consumers can process duplicates, cancellation can race with reservation, Redis can show stale status, and inventory can lag behind user-visible order state.

Consistency and correctness implications: order state should be authoritative in the order database. Inventory reservation semantics need explicit idempotency keys, ordering rules, and reconciliation.

Operational checks: monitor outbox age, consumer lag, duplicate event rate, Redis freshness, failed reservation count, and reconciliation mismatches.

Tests: crash after order commit before event publish, duplicate inventory events, cancel while reservation is pending, Redis flush, delayed consumer, and reconciliation repair.

### replica-lag

#### Response A

The likely cause is replica lag. After a write, the read can go to a replica that has not applied the update yet. Options include reading from the primary after writes, reducing replica lag, or using sticky sessions. Monitor replication delay and error rates. Test by saving a profile and reading it immediately several times.

#### Response B

Assumptions and workload shape: profile writes are low enough that the system can treat immediate post-write reads differently from ordinary profile reads. The user-visible bug is not generic eventual consistency; it is missing read-your-writes and possibly monotonic-read behavior.

Recommendation: route reads after a profile write to a source that has applied that write. Use leader reads for a short window, session stickiness to a replica known to have the write, or LSN/version-aware routing. Keep stale-tolerant profile reads on replicas.

Key trade-offs: leader reads increase leader load and latency. Session stickiness reduces non-monotonic reads but complicates routing. LSN-aware reads are more precise but require plumbing write positions through the application.

Failure modes: replica apply lag, failover to a stale replica, user refresh routed to different replicas, cache mixed with replica reads, and missing version propagation.

Consistency and correctness implications: users need read-your-writes after saving settings. Fast refreshes should not move backward in observed profile version.

Operational checks: track replica apply lag by replica, post-write leader-read rate, stale-read reports, version mismatch counts, and failover freshness.

Tests: save then immediate read, repeated refresh across replicas, delayed replica apply, failover during profile update, and version-aware routing fallback.

### cache-as-truth

#### Response A

Redis is fast, but using it for final payment amount is risky. If Redis loses data or has stale data, the payment amount may be wrong. A safer design is to keep PostgreSQL as the source of truth and use Redis only for performance. Add cache invalidation and compare Redis values with PostgreSQL. Test Redis failures and concurrent cart updates.

#### Response B

Assumptions and workload shape: the final payable amount is a financial invariant. Users and the business expect the charged amount to match the committed cart state. Redis availability does not make Redis authoritative.

Recommendation: reject Redis as the source of truth for payment decisions. Store cart totals, checkout state, and payment amount in PostgreSQL inside the transaction or workflow boundary that creates the payment intent. Redis may cache cart previews, but checkout should read from authoritative storage or recompute from authoritative line items.

Key trade-offs: Redis can reduce read latency for browsing, but using it for payment correctness creates stale-read and lost-update risk. PostgreSQL may add latency, but it gives transaction boundaries, constraints, and auditability.

Failure modes: cache eviction, stale cache after cart update, asynchronous PostgreSQL update failure, concurrent cart mutation during checkout, duplicated worker updates, and payment amount mismatch.

Consistency and correctness implications: payment amount must be derived from authoritative cart state. If cached state disagrees, checkout should block, refresh, or recompute rather than charge.

Operational checks: track cache/database mismatches, checkout recomputations, async worker lag, payment amount corrections, and cart update races.

Tests: Redis flush before checkout, delayed async worker, concurrent cart update and payment, stale cache read, duplicate worker update, and reconciliation of charged amount against PostgreSQL.

### exactly-once-trap

#### Response A

Exactly-once mode in the stream processor helps reduce duplicates, but you still need retries and idempotency. Use unique event IDs, store processed IDs, and make ledger writes idempotent. For the payment provider, use idempotency keys. Test retries and crashes.

#### Response B

Assumptions and workload shape: this pipeline moves money and writes a ledger. The requirement cannot be satisfied by assuming duplicates cannot happen. Stream processor exactly-once settings do not create an end-to-end exactly-once guarantee across an API, Kafka, a worker, an external payment provider, and a ledger database.

Recommendation: define where duplicate effects are prevented. Use API idempotency keys, a transactional outbox for accepted payment requests, idempotent Kafka consumers, payment-provider idempotency keys, and ledger unique constraints. Treat the ledger as authoritative and reconcile provider state against it.

Key trade-offs: stronger idempotency and reconciliation add storage and operational work, but they protect money movement. A transactional boundary around the ledger improves correctness but does not cover external side effects by itself.

Failure modes: API retry after timeout, crash after provider charge before ledger write, duplicate Kafka delivery, worker retry, provider timeout with unknown charge status, and ledger write conflict.

Consistency and correctness implications: the invariant is not exactly-once message processing; it is exactly-once financial effect per business idempotency key.

Operational checks: track duplicate request keys, provider idempotency reuse, ledger uniqueness conflicts, unreconciled provider charges, and retry outcomes.

Tests: duplicate API request, Kafka redelivery, crash after provider side effect, provider timeout, ledger conflict, and reconciliation repair.

### vague-startup-architecture

#### Response A

For a new B2B SaaS product, PostgreSQL is the safest default. It supports users, teams, permissions, audit logs, and transactions. MongoDB or DynamoDB may help at scale, and Neo4j may help for graph relationships, but PostgreSQL is simpler to start with. You can add search or analytics later.

#### Response B

Assumptions and workload shape: the prompt does not provide request volume, data size, tenant model, permission complexity, audit retention, latency goals, or operational constraints. A definitive database choice would be premature.

Recommendation: use PostgreSQL as a scoped default for an early B2B SaaS source of truth if the first version needs users, teams, permissions, audit logs, and transactional workflows. Do not treat that as a final architecture decision for analytics, notifications, search, or AI features.

Key trade-offs: PostgreSQL gives constraints, joins, transactions, migrations, and operational familiarity. MongoDB may help if the product centers on document-local access with limited cross-document invariants. DynamoDB may fit high-scale key-value access but requires careful access-pattern design. Neo4j may fit traversal-heavy graph queries but is unlikely to be the first source of truth for permissions and audit history.

Failure modes: picking a database based on future scale myths, splitting invariants too early, under-designing permissions, mixing analytics with OLTP, and ignoring migration paths.

Consistency and correctness implications: permissions and audit history are correctness-sensitive. Put those invariants near the authoritative storage boundary.

Operational checks: validate core queries, permission checks, audit write rate, migration workflow, backup/restore, and tenant growth.

Tests: prototype permission queries, audit-log retention, tenant isolation, migration rollback, and expected high-volume workflows before adding specialized stores.

## Limitations

- Self-evaluation bias: the same agent family generated and scored the pilot, so scores may favor the skill-enabled response style.
- Response-shape/rubric alignment: treatment instructions ask for sections that map closely to the answer-quality rubric.
- Single model: the pilot only covers GPT-5 Codex.
- Single run: each case has one control response and one treatment response.
- No variance estimate: the pilot does not report repeated-run mean, minimum, maximum, or range.
- Non-random case selection: the five cases were selected for coverage, not sampled randomly.
- Process-compliance rubric not scored: this pilot scores answer quality only.

## Overall Decision

- Total control score: 38
- Total treatment score: 51
- Total lift: +13
- Mean normalized control: 68.0%
- Mean normalized treatment: 91.3%
- Mean normalized lift: +23.3 pp
- Limitations: In one five-case paired pilot run, treatment scored higher than control and four must-pass cases crossed the pass threshold. This is directional pilot evidence, not statistical proof.
