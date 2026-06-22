You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Treatment Instructions

Use ddia-system-design for the Java coding case.

Frame the review around assumptions, source of truth, consistency guarantees, transaction boundaries, idempotency, failure modes, operational visibility, and tests. The answer should still be practical Java guidance: identify the bug, explain why it is a distributed data problem, and propose the smallest patch that improves correctness without claiming impossible guarantees.

# ddia-system-design skill instructions

---
name: ddia-system-design
description: Apply Designing Data-Intensive Applications inspired architecture reasoning for backend engineering and system design. Use when reviewing or designing data-intensive systems, database choices, storage/indexing, replication, partitioning, transactions, isolation levels, distributed faults, consistency, consensus, batch processing, stream processing, derived data, correctness, reliability, scalability, maintainability, or operational trade-offs.
---

# DDIA System Design

Use this skill to turn a backend architecture question into explicit workload assumptions, data model choices, consistency requirements, failure modes, and verification steps.

## Core Workflow

1. Frame the system goal in terms of data, users, writes, reads, latency, durability, and operational ownership.
2. Name the workload before choosing tools: request rate, data size, hot keys, fan-out, read/write ratio, freshness needs, and recovery objectives.
3. Separate facts from choices: required correctness guarantees, acceptable staleness, acceptable data loss, and business-visible failure behavior.
4. Analyze the design through four lenses: reliability, scalability, maintainability, and evolvability.
5. Surface trade-offs explicitly. Do not recommend a database, queue, cache, or consensus mechanism without explaining the cost.
6. Convert abstract guarantees into tests, observability signals, and runbook checks.

## Load References Selectively

- Read `references/topic-map.md` when mapping a user problem to relevant DDIA themes.
- Read `references/system-design-principles.md` when making or reviewing architecture decisions.
- Read `references/architecture-review-checklists.md` when the user asks for a review, critique, design doc, or failure-mode analysis.

## Response Shape

Prefer this structure unless the user asks for a different format:

1. Assumptions and workload shape
2. Recommendation
3. Key trade-offs
4. Failure modes
5. Consistency and correctness implications
6. Operational checks
7. Tests or experiments to validate the design

For narrow follow-ups or single-question prompts, only the relevant sections
are required. Do not pad an answer with empty sections to match the full shape.

## Worked Example

User: "We want to cache product detail pages in Redis. Is that safe?"

- Assumptions and workload shape: product data changes a few thousand times per
  day; reads are high; the user has not stated a freshness bound or source of
  truth.
- Recommendation: Redis cache-aside is reasonable if PostgreSQL stays the source
  of truth and the freshness bound is explicit. Ask for the acceptable stale
  window before committing.
- Key trade-offs: TTL is simple but can serve stale data until expiry;
  invalidation is precise but couples the write path to the cache.
- Failure modes: cache loss, stale price after an update, cache stampede on a
  hot key, and PostgreSQL fallback load when Redis is down.
- Consistency and correctness implications: price and inventory fields are
  correctness-sensitive; descriptive fields tolerate staleness.
- Operational checks: cache hit rate, invalidation rate, stale-read reports,
  fallback rate, and Redis memory pressure.
- Tests: stale read after update, Redis flush, hot-key stampede, and fallback
  under PostgreSQL load.

## Out Of Scope

Do not use this skill for: pure algorithm problems, single-machine CRUD
services with no distributed state, frontend component or styling choices, or
DevOps tooling selection without a data or consistency component.

## Guardrails

- Ask for missing workload and correctness requirements before making a strong recommendation.
- Avoid one-size-fits-all answers such as always using Kafka, microservices, NoSQL, or strong consistency.
- Treat caches, indexes, replicas, materialized views, and streams as derived data that can become stale or incorrect.
- Discuss human operations: deployment, recovery, backfills, schema evolution, monitoring, and incident response.
- Keep direct book quotations out of responses unless the user explicitly asks for a short cited quote.

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
