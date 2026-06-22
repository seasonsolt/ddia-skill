# DDIA Benchmark Case Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the DDIA skill benchmark from broad structural coverage to named behavior coverage for the eight deferred system-design gaps.

**Architecture:** Keep the benchmark Markdown-first. Add eight concrete case files, pin required case paths in `check_ddia_benchmark.py`, and extend the test fixture so missing coverage cases fail deterministically instead of only changing aggregate counts.

**Tech Stack:** Markdown benchmark cases, Python standard library, `unittest`, existing checker scripts.

---

## Scope Check

This plan expands benchmark case coverage only. It does not rerun A/B pilots, change the installed `ddia-system-design` skill behavior, add automated LLM judging, or score historical responses.

## File Structure

- Modify: `/Users/Thin/Documents/ddia/scripts/check_ddia_benchmark.py`
  - Replace count-only validation with count plus named required case validation.
- Modify: `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`
  - Update the complete benchmark fixture to include the expanded named cases.
  - Add a regression for a missing required expanded case.
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/06-quantitative-workload-capacity.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/07-batch-backfill-reconciliation.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/08-schema-evolution-rollout.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/09-correct-cache-use.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/10-observability-runbook.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/11-idempotency-outbox.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/bad/05-capacity-cost-handwave.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/adversarial/05-global-linearizable-writes.md`
- Modify: `/Users/Thin/Documents/ddia/evaluation/benchmark-guide.md`
  - Add a coverage matrix for the expanded benchmark.

---

### Task 1: Add Required Expanded Case Regression

**Files:**
- Modify: `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`

- [ ] **Step 1: Add helper case content for expanded fixture**

Add this helper below `case_text()`:

```python
EXPANDED_CASES = {
    "evaluation/cases/good/06-quantitative-workload-capacity.md": case_text(
        title="Quantitative Workload Capacity",
        category="good",
        scoring_profile="good",
    ),
    "evaluation/cases/good/07-batch-backfill-reconciliation.md": case_text(
        title="Batch Backfill Reconciliation",
        category="good",
        scoring_profile="good",
    ),
    "evaluation/cases/good/08-schema-evolution-rollout.md": case_text(
        title="Schema Evolution Rollout",
        category="good",
        scoring_profile="good",
    ),
    "evaluation/cases/good/09-correct-cache-use.md": case_text(
        title="Correct Cache Use",
        category="good",
        scoring_profile="good",
    ),
    "evaluation/cases/good/10-observability-runbook.md": case_text(
        title="Observability Runbook",
        category="good",
        scoring_profile="good",
    ),
    "evaluation/cases/good/11-idempotency-outbox.md": case_text(
        title="Idempotency Outbox",
        category="good",
        scoring_profile="good",
    ),
    "evaluation/cases/bad/05-capacity-cost-handwave.md": case_text(
        title="Capacity Cost Handwave",
        category="bad",
        scoring_profile="anti-pattern",
    ),
    "evaluation/cases/adversarial/05-global-linearizable-writes.md": case_text(
        title="Global Linearizable Writes",
        category="adversarial",
        scoring_profile="anti-pattern",
    ),
}
```

- [ ] **Step 2: Add a fixture writer for expanded cases**

Add this helper below `make_complete_benchmark()`:

```python
def make_expanded_benchmark(root: pathlib.Path) -> None:
    make_complete_benchmark(root)
    for relative, text in EXPANDED_CASES.items():
        write(root / relative, text)
```

- [ ] **Step 3: Add missing required case regression**

Add this test to `class DdiaBenchmarkTest(unittest.TestCase)` after `test_checker_accepts_complete_benchmark`:

```python
    def test_checker_reports_missing_required_expanded_case(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_expanded_benchmark(repo)
            missing_case = repo / "evaluation/cases/good/06-quantitative-workload-capacity.md"
            missing_case.unlink()

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/cases/good/06-quantitative-workload-capacity.md: missing required case",
            report["case_errors"],
        )
```

- [ ] **Step 4: Run the focused test and confirm it fails**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_checker_reports_missing_required_expanded_case -v
```

Expected: FAIL because the checker has not yet enforced named required expanded cases.

- [ ] **Step 5: Commit the failing test**

Do not commit if the test passes before implementation.

```bash
cd /Users/Thin/Documents/ddia
git add tests/test_ddia_benchmark.py
git commit -m "test: require expanded benchmark cases"
```

---

### Task 2: Pin Required Case Paths In Checker

**Files:**
- Modify: `/Users/Thin/Documents/ddia/scripts/check_ddia_benchmark.py`
- Modify: `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`

- [ ] **Step 1: Replace aggregate count constant with named case lists**

In `scripts/check_ddia_benchmark.py`, replace:

```python
EXPECTED_CASE_COUNTS = {"good": 5, "bad": 4, "adversarial": 4}
```

with:

```python
REQUIRED_CASE_FILES = {
    "good": [
        pathlib.Path("evaluation/cases/good/01-order-consistency.md"),
        pathlib.Path("evaluation/cases/good/02-event-pipeline.md"),
        pathlib.Path("evaluation/cases/good/03-database-choice.md"),
        pathlib.Path("evaluation/cases/good/04-replica-lag.md"),
        pathlib.Path("evaluation/cases/good/05-derived-data.md"),
        pathlib.Path("evaluation/cases/good/06-quantitative-workload-capacity.md"),
        pathlib.Path("evaluation/cases/good/07-batch-backfill-reconciliation.md"),
        pathlib.Path("evaluation/cases/good/08-schema-evolution-rollout.md"),
        pathlib.Path("evaluation/cases/good/09-correct-cache-use.md"),
        pathlib.Path("evaluation/cases/good/10-observability-runbook.md"),
        pathlib.Path("evaluation/cases/good/11-idempotency-outbox.md"),
    ],
    "bad": [
        pathlib.Path("evaluation/cases/bad/01-cache-as-truth.md"),
        pathlib.Path("evaluation/cases/bad/02-replica-lag-denial.md"),
        pathlib.Path("evaluation/cases/bad/03-hot-partition.md"),
        pathlib.Path("evaluation/cases/bad/04-vague-startup-architecture.md"),
        pathlib.Path("evaluation/cases/bad/05-capacity-cost-handwave.md"),
    ],
    "adversarial": [
        pathlib.Path("evaluation/cases/adversarial/01-tool-first-trap.md"),
        pathlib.Path("evaluation/cases/adversarial/02-exactly-once-trap.md"),
        pathlib.Path("evaluation/cases/adversarial/03-distributed-lock-trap.md"),
        pathlib.Path("evaluation/cases/adversarial/04-schema-evolution-trap.md"),
        pathlib.Path("evaluation/cases/adversarial/05-global-linearizable-writes.md"),
    ],
}
EXPECTED_CASE_COUNTS = {category: len(paths) for category, paths in REQUIRED_CASE_FILES.items()}
```

- [ ] **Step 2: Report missing required case files**

In `check_benchmark()`, immediately after `relative_dir = directory.as_posix()`, add:

```python
        for required_case in REQUIRED_CASE_FILES[category]:
            if not (repo / required_case).exists():
                case_errors.append(f"{required_case.as_posix()}: missing required case")
```

- [ ] **Step 3: Update the complete benchmark fixture**

In `tests/test_ddia_benchmark.py`, update `make_complete_benchmark()` to call the expanded fixture writer at the end:

```python
    for relative, text in EXPANDED_CASES.items():
        write(root / relative, text)
```

Remove `make_expanded_benchmark()` if it is now identical to `make_complete_benchmark()`, and update the missing-case regression to call `make_complete_benchmark(repo)`.

- [ ] **Step 4: Run benchmark tests**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_benchmark -v
```

Expected: PASS for the test fixture. The current repo checker may still fail until Task 3 creates the real case files.

- [ ] **Step 5: Commit checker and fixture changes**

```bash
cd /Users/Thin/Documents/ddia
git add scripts/check_ddia_benchmark.py tests/test_ddia_benchmark.py
git commit -m "test: pin expanded benchmark case files"
```

---

### Task 3: Add Expanded Good Cases

**Files:**
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/06-quantitative-workload-capacity.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/07-batch-backfill-reconciliation.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/08-schema-evolution-rollout.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/09-correct-cache-use.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/10-observability-runbook.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/11-idempotency-outbox.md`

- [ ] **Step 1: Create quantitative workload case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/good/06-quantitative-workload-capacity.md`:

```markdown
# Case: Quantitative Workload Capacity

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this design:

We are building an activity feed service. Today it has 2 million daily active users, 35 million read requests per day, 4 million writes per day, p95 feed-read latency target of 150 ms, and a 12-month growth expectation of 10x. The proposal stores posts in PostgreSQL, precomputes fanout into Redis sorted sets, and rebuilds feeds overnight. Review whether the architecture can meet workload, correctness, and cost goals.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill turns vague scalability discussion into quantitative capacity reasoning.

## Weak Answer Patterns

- Says the system can scale by adding cache or replicas without calculating reads, writes, fanout, storage, or rebuild time.
- Ignores hot users, celebrity fanout, cache memory pressure, queue backlog, and read latency targets.
- Skips cost and operational limits for Redis memory, rebuild jobs, and database write amplification.

## Strong Answer Signals

- Converts daily reads and writes into peak QPS assumptions and asks for fanout distribution.
- Compares fanout-on-write, fanout-on-read, and hybrid approaches with storage and latency trade-offs.
- Discusses hot keys, queue backpressure, rebuild duration, cache eviction, and consistency between PostgreSQL and derived feeds.
- Proposes load tests, queue lag alerts, feed freshness SLOs, and cost estimates for 10x growth.

## Scoring Notes

- Score workload framing based on concrete rate, storage, latency, and growth calculations.
- Score trade-off quality based on whether the answer chooses a feed strategy from workload shape rather than tool preference.
```

- [ ] **Step 2: Create batch backfill case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/good/07-batch-backfill-reconciliation.md`:

```markdown
# Case: Batch Backfill Reconciliation

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this migration plan:

We have three years of order events in Kafka and S3. A new fraud model needs a derived customer-risk table built from historical events and then kept current from the live stream. The team plans to run a Spark backfill once, write directly into PostgreSQL, then start the streaming consumer. Review the plan for correctness, replay safety, and verification.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill handles batch plus streaming derived data and reconciliation.

## Weak Answer Patterns

- Treats the backfill as a one-time script without idempotent output or checkpointing.
- Ignores duplicate events, late events, schema drift, replay windows, and cutover ordering.
- Skips reconciliation between batch output, stream output, and source events.

## Strong Answer Signals

- Defines a deterministic derived table keyed by customer and model version.
- Uses idempotent writes, checkpoints, replayable jobs, and explicit cutover watermarks.
- Handles late data, schema versions, joins, and backfill reruns without double counting.
- Proposes row-count checks, aggregate reconciliation, sample audits, and shadow reads before cutover.

## Scoring Notes

- Score correctness reasoning based on whether replay and rerun behavior are safe.
- Score verification value based on reconciliation between source events, batch output, and stream-maintained state.
```

- [ ] **Step 3: Create schema evolution case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/good/08-schema-evolution-rollout.md`:

```markdown
# Case: Schema Evolution Rollout

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this database migration:

The user profile service stores `full_name` in one column. We need separate `given_name` and `family_name` columns for search and compliance exports. Multiple services read the table, mobile clients can lag by weeks, and the table has 600 million rows. The proposal is to add the two columns, deploy code that writes only the new columns, run an online backfill, then drop `full_name`. Review the rollout.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill covers expand-contract migration and compatibility.

## Weak Answer Patterns

- Drops or stops writing the old column before all readers are compatible.
- Ignores mobile/client version lag, long-running backfill load, rollback, and data quality checks.
- Treats backfill as purely mechanical without ambiguity in name parsing.

## Strong Answer Signals

- Proposes expand-contract rollout with dual writes or derived reads during compatibility window.
- Separates schema change, code rollout, backfill, validation, read switch, and cleanup.
- Addresses online migration throttling, rollback, idempotent backfill, and ambiguous names.
- Proposes metrics for null rate, parse failures, reader compatibility, and export correctness.

## Scoring Notes

- Score failure-mode coverage based on compatibility, rollback, and online migration risks.
- Score maintainability based on whether cleanup happens only after measured reader migration.
```

- [ ] **Step 4: Create correct cache-use case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/good/09-correct-cache-use.md`:

```markdown
# Case: Correct Cache Use

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this cache design:

Our product catalog service stores product data in PostgreSQL and serves product detail pages through an API. Product data changes a few thousand times per day, reads are 40,000 QPS at peak, and stale price reads must last less than 30 seconds. The proposal uses Redis cache-aside with TTL, background refresh for hot products, and fallback to PostgreSQL on miss. Review whether this is a correct cache design and what needs to be verified.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill can approve cache use when the cache remains derived state.

## Weak Answer Patterns

- Rejects all caching without considering read workload and freshness tolerance.
- Treats TTL as sufficient without discussing invalidation, rebuild, cache stampede, and stale price risk.
- Skips fallback behavior when Redis is unavailable or PostgreSQL is under pressure.

## Strong Answer Signals

- Keeps PostgreSQL as source of truth and Redis as derived, rebuildable state.
- Discusses cache-aside, TTL, targeted invalidation, hot-key protection, stampede prevention, and stale-read bounds.
- Separates price correctness from less critical catalog fields.
- Proposes freshness metrics, cache hit rate, invalidation tests, Redis-loss tests, and stale-price audits.

## Scoring Notes

- Score trade-off quality based on accepting cache use with explicit correctness boundaries.
- Score verification value based on freshness, rebuild, and degradation tests.
```

- [ ] **Step 5: Create observability runbook case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/good/10-observability-runbook.md`:

```markdown
# Case: Observability Runbook

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this operational plan:

We operate a notification pipeline: API requests enqueue messages, workers send email and push notifications, and delivery receipts update a status table. The architecture is mostly built, but incidents are hard to diagnose. Ask what observability, alerts, dashboards, and runbooks are needed before launch.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill treats operations as first-class design output.

## Weak Answer Patterns

- Gives generic advice to add logs and metrics without naming signals.
- Ignores queue lag, duplicate sends, provider throttling, dead letters, retry storms, and status drift.
- Skips operator actions and incident thresholds.

## Strong Answer Signals

- Defines metrics for enqueue rate, worker throughput, queue age, retry count, provider error rate, dedupe hits, and status update lag.
- Adds traces or correlation IDs from API request through provider callback.
- Proposes alerts tied to user impact and runbooks with concrete mitigation actions.
- Includes dashboards, dead-letter inspection, replay safety, and reconciliation jobs.

## Scoring Notes

- Score verification value based on whether the answer produces actionable checks and incident drills.
- Score failure-mode coverage based on observable symptoms and operator response paths.
```

- [ ] **Step 6: Create idempotency outbox case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/good/11-idempotency-outbox.md`:

```markdown
# Case: Idempotency Outbox

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this API and eventing design:

A subscription service receives `CreateSubscription` requests from clients. It writes a subscription row, charges the customer through a payment provider, and publishes a `SubscriptionCreated` event for downstream systems. Clients retry on timeout, workers can crash, and the payment provider can return success after our request times out. Review the design for idempotency and failure windows.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill can design idempotent APIs and outbox/inbox boundaries.

## Weak Answer Patterns

- Relies on client retries being rare or provider calls being reliable.
- Publishes events outside the database transaction without discussing crash windows.
- Ignores idempotency keys, unique constraints, provider request IDs, and duplicate downstream consumption.

## Strong Answer Signals

- Requires client idempotency keys, unique constraints, and stable provider idempotency identifiers.
- Defines transactional state changes and an outbox for publishing subscription events.
- Discusses inbox/deduplication for downstream consumers and reconciliation with provider state.
- Proposes timeout, retry, crash-after-charge, duplicate-request, and duplicate-event tests.

## Scoring Notes

- Score correctness reasoning based on duplicate prevention across API, payment, database, and event boundaries.
- Score failure-mode coverage based on explicit crash windows and retry behavior.
```

- [ ] **Step 7: Run checker against current repo**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_benchmark.py --repo /Users/Thin/Documents/ddia
```

Expected: no `case_errors` for the new good cases.

- [ ] **Step 8: Commit good cases**

```bash
cd /Users/Thin/Documents/ddia
git add evaluation/cases/good/06-quantitative-workload-capacity.md evaluation/cases/good/07-batch-backfill-reconciliation.md evaluation/cases/good/08-schema-evolution-rollout.md evaluation/cases/good/09-correct-cache-use.md evaluation/cases/good/10-observability-runbook.md evaluation/cases/good/11-idempotency-outbox.md
git commit -m "test: add expanded good benchmark cases"
```

---

### Task 4: Add Expanded Bad And Adversarial Cases

**Files:**
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/bad/05-capacity-cost-handwave.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/adversarial/05-global-linearizable-writes.md`

- [ ] **Step 1: Create capacity and cost anti-pattern case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/bad/05-capacity-cost-handwave.md`:

```markdown
# Case: Capacity Cost Handwave

Category: bad
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to review this proposal:

Our metrics ingestion service handles 200,000 events per second today and must support 10x growth next year. The proposal says we should store raw events, rollups, and query indexes in one PostgreSQL cluster because PostgreSQL is reliable. If load grows, we can move to bigger machines or add read replicas later. Is this acceptable?

## Bad Premise Or Trap

The prompt handwaves capacity, cost, write amplification, retention, and query workload while assuming vertical scaling and read replicas solve ingestion growth.

## Weak Answer Patterns

- Accepts one database cluster without calculating ingestion rate, storage growth, retention, or index cost.
- Suggests read replicas for a write-heavy ingestion bottleneck.
- Ignores partitioning, compaction, rollup strategy, hot indexes, backpressure, and cost controls.

## Strong Answer Signals

- Rejects the handwave and asks for event size, retention, query patterns, cardinality, and SLOs.
- Estimates write volume, storage growth, index overhead, and 10x operating cost.
- Separates raw event storage, rollups, query-serving indexes, and retention policies.
- Proposes load tests, backpressure, partitioning, compaction, cost dashboards, and degradation behavior.

## Scoring Notes

- Anti-pattern resistance must identify that read replicas do not solve write ingestion capacity.
- Score workload framing based on concrete volume, retention, and cost calculations.
```

- [ ] **Step 2: Create global linearizable writes adversarial case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/adversarial/05-global-linearizable-writes.md`:

```markdown
# Case: Global Linearizable Writes

Category: adversarial
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to design our account settings service:

Users are global. We want every region to accept writes locally, every read in every region to immediately reflect the latest write, and p99 latency under 50 ms worldwide. The team proposes active-active multi-region writes with conflict-free replication and says users should never see stale data. Describe the architecture assuming all three requirements are mandatory.

## Bad Premise Or Trap

The prompt asks for local writes, global immediate consistency, and low worldwide latency at the same time without acknowledging consensus and latency trade-offs.

## Weak Answer Patterns

- Accepts all requirements without discussing quorum, leader placement, clock/replication limits, or conflict resolution.
- Claims active-active replication gives immediate global consistency.
- Ignores stale reads, write conflicts, failover behavior, and regional partitions.

## Strong Answer Signals

- Challenges the premise and explains the trade-off between local latency, availability, and linearizable global state.
- Offers explicit choices such as single-region leader, regional ownership, quorum writes, or relaxed consistency for selected fields.
- Separates fields that require strict consistency from fields that can tolerate convergence.
- Proposes Jepsen-style partition tests, conflict injection, stale-read checks, failover drills, and latency SLO validation.

## Scoring Notes

- Anti-pattern resistance must reject the idea that conflict-free active-active writes provide immediate global linearizability.
- Score trade-off quality based on explicit consistency and latency choices.
```

- [ ] **Step 3: Run checker against current repo**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_benchmark.py --repo /Users/Thin/Documents/ddia
```

Expected: no `case_errors` for the new bad and adversarial cases.

- [ ] **Step 4: Commit bad and adversarial cases**

```bash
cd /Users/Thin/Documents/ddia
git add evaluation/cases/bad/05-capacity-cost-handwave.md evaluation/cases/adversarial/05-global-linearizable-writes.md
git commit -m "test: add expanded anti-pattern benchmark cases"
```

---

### Task 5: Document Expanded Coverage Matrix

**Files:**
- Modify: `/Users/Thin/Documents/ddia/evaluation/benchmark-guide.md`

- [ ] **Step 1: Add coverage matrix section**

Append this section after `## Purpose`:

```markdown
## Coverage Matrix

The benchmark intentionally covers these DDIA-style backend design behaviors:

- Source-of-truth and derived-data boundaries: `good/01-order-consistency.md`, `bad/01-cache-as-truth.md`, `good/05-derived-data.md`
- Event pipeline correctness: `good/02-event-pipeline.md`, `good/11-idempotency-outbox.md`, `adversarial/02-exactly-once-trap.md`
- Storage and database choice: `good/03-database-choice.md`, `good/08-schema-evolution-rollout.md`, `adversarial/04-schema-evolution-trap.md`
- Replication and consistency: `good/04-replica-lag.md`, `bad/02-replica-lag-denial.md`, `adversarial/05-global-linearizable-writes.md`
- Partitioning and hot spots: `bad/03-hot-partition.md`, `adversarial/03-distributed-lock-trap.md`
- Quantitative workload and cost reasoning: `good/06-quantitative-workload-capacity.md`, `bad/05-capacity-cost-handwave.md`
- Batch/backfill and reconciliation: `good/07-batch-backfill-reconciliation.md`
- Correct cache use: `good/09-correct-cache-use.md`
- Observability and operations: `good/10-observability-runbook.md`
- Ambiguous requirements and requirement discovery: `bad/04-vague-startup-architecture.md`, `adversarial/01-tool-first-trap.md`
```

- [ ] **Step 2: Run benchmark tests**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_benchmark -v
```

Expected: PASS.

- [ ] **Step 3: Commit guide update**

```bash
cd /Users/Thin/Documents/ddia
git add evaluation/benchmark-guide.md
git commit -m "docs: document benchmark coverage matrix"
```

---

### Task 6: Final Verification And Publish

**Files:**
- No source changes expected.

- [ ] **Step 1: Run full tests**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Run quality checker**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_skill_quality.py --repo /Users/Thin/Documents/ddia
```

Expected:

```json
{
  "missing_files": [],
  "missing_terms": [],
  "prompt_count": 5,
  "invalid_files": [],
  "structure_errors": []
}
```

- [ ] **Step 3: Run benchmark checker**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_benchmark.py --repo /Users/Thin/Documents/ddia
```

Expected: `missing_paths`, `case_errors`, `rubric_errors`, `guide_errors`, `template_errors`, and `ab_errors` are empty. Expected `case_counts` are `{"good": 11, "bad": 5, "adversarial": 5}`.

- [ ] **Step 4: Run ASCII and diff checks**

Run:

```bash
cd /Users/Thin/Documents/ddia
LC_ALL=C rg -n "[^\x00-\x7F]" evaluation/cases evaluation/benchmark-guide.md
git diff --check
```

Expected: ASCII scan prints no matches; `git diff --check` exits 0.

- [ ] **Step 5: Push branch**

Run:

```bash
cd /Users/Thin/Documents/ddia
git status --short --branch
git push origin codex/ddia-system-design-skill
```

Expected: working tree is clean and branch pushes successfully.

---

## Self-Review Notes

- Spec coverage: this plan covers all eight deferred benchmark coverage gaps from the A/B credibility hardening design.
- Placeholder scan: no unresolved placeholder language remains.
- Type consistency: checker constants, expected counts, and fixture paths use the same relative filenames.
