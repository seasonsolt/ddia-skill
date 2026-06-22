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
