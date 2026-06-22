# DDIA A/B Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reusable A/B evaluation framework for `ddia-system-design` and record a first five-case pilot result comparing no-skill control responses against skill-enabled treatment responses.

**Architecture:** Extend the existing benchmark checker with a focused A/B validation layer for `evaluation/ab/`. Add A/B instructions, blind scoring docs, a result template, a pilot result file with preserved paired responses and scores, then update the root README to report the pilot honestly as evidence, not statistical proof.

**Tech Stack:** Markdown benchmark assets, Python standard library, `unittest`, existing Git workflow.

---

## Scope Check

This is one focused subsystem: an A/B layer on top of the existing DDIA benchmark. It does not add automated LLM judging, multi-model testing, statistical confidence intervals, repeated randomized runs, independent external scoring, or CI automation.

## File Structure

- Modify: `/Users/Thin/Documents/ddia/scripts/check_ddia_benchmark.py`
  - Add A/B file validation while preserving existing benchmark validation.
- Modify: `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`
  - Add temp-fixture tests for A/B asset validation, then add current-repo integration checks after the A/B files exist.
- Create: `/Users/Thin/Documents/ddia/evaluation/ab/README.md`
  - Explain the A/B method, limitations, and rerun steps.
- Create: `/Users/Thin/Documents/ddia/evaluation/ab/control-instructions.md`
  - Prompt wrapper for no-skill control responses.
- Create: `/Users/Thin/Documents/ddia/evaluation/ab/treatment-instructions.md`
  - Prompt wrapper for skill-enabled treatment responses.
- Create: `/Users/Thin/Documents/ddia/evaluation/ab/blind-scoring-guide.md`
  - Instructions for scoring Response A and Response B before revealing mapping.
- Create: `/Users/Thin/Documents/ddia/evaluation/ab/results-template.md`
  - Template for future A/B runs.
- Create: `/Users/Thin/Documents/ddia/evaluation/ab/pilot-results.md`
  - First five-case pilot A/B result with preserved responses, scores, lift, notes, and limitations.
- Modify: `/Users/Thin/Documents/ddia/README.md`
  - Replace "not A/B yet" wording with pilot A/B evidence and limitations.

---

### Task 1: Add A/B Asset Validator

**Files:**
- Modify: `/Users/Thin/Documents/ddia/scripts/check_ddia_benchmark.py`
- Modify: `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`

- [ ] **Step 1: Add failing A/B validator tests**

In `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`, add these helper constants and functions after `make_complete_benchmark`:

```python
AB_REQUIRED_FILES = [
    "evaluation/ab/README.md",
    "evaluation/ab/control-instructions.md",
    "evaluation/ab/treatment-instructions.md",
    "evaluation/ab/blind-scoring-guide.md",
    "evaluation/ab/results-template.md",
    "evaluation/ab/pilot-results.md",
]


def make_complete_ab_assets(root: pathlib.Path) -> None:
    write(
        root / "evaluation/ab/README.md",
        """# DDIA Skill A/B Evaluation

## Purpose

Compare control responses without ddia-system-design against treatment responses with ddia-system-design.

## Method

Run the same cases with the same model, score Response A and Response B, then reveal the mapping.

## Pilot Case Set

- evaluation/cases/good/01-order-consistency.md
- evaluation/cases/good/04-replica-lag.md
- evaluation/cases/bad/01-cache-as-truth.md
- evaluation/cases/adversarial/02-exactly-once-trap.md
- evaluation/cases/bad/04-vague-startup-architecture.md

## Limitations

This is pilot A/B evidence, not statistical proof.
""",
    )
    write(
        root / "evaluation/ab/control-instructions.md",
        """# Control Instructions

Answer the benchmark case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill.
""",
    )
    write(
        root / "evaluation/ab/treatment-instructions.md",
        """# Treatment Instructions

Use ddia-system-design for the benchmark case.

Follow the ddia-system-design response shape: assumptions, recommendation, trade-offs, failure modes, correctness, operations, and tests.
""",
    )
    write(
        root / "evaluation/ab/blind-scoring-guide.md",
        """# Blind Scoring Guide

## Scoring Order

Score Response A and Response B before revealing which response is control or treatment.

## Mapping Reveal

Reveal the mapping only after all dimensions, notes, and pass decisions are recorded.
""",
    )
    write(
        root / "evaluation/ab/results-template.md",
        """# DDIA Skill A/B Results Template

## Run Metadata

- Evaluator:
- Date:
- Model:
- Skill version:

## Hidden Mapping

- Response A:
- Response B:

## Case Scores

| Case | Category | Control score | Treatment score | Lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- |

## Dimension Differences

Record workload framing, trade-off quality, failure-mode coverage, correctness reasoning, verification value, and anti-pattern resistance differences.

## Response Archive

Preserve Response A and Response B for every case.

## Overall Decision

- Total control score:
- Total treatment score:
- Total lift:
- Limitations:
""",
    )
    write(
        root / "evaluation/ab/pilot-results.md",
        """# DDIA Skill Pilot A/B Results

## Run Metadata

- Evaluator: Codex
- Date: 2026-06-22
- Model: GPT-5 Codex
- Skill version: local pilot

## Pilot Case Coverage

- evaluation/cases/good/01-order-consistency.md
- evaluation/cases/good/04-replica-lag.md
- evaluation/cases/bad/01-cache-as-truth.md
- evaluation/cases/adversarial/02-exactly-once-trap.md
- evaluation/cases/bad/04-vague-startup-architecture.md

## Hidden Mapping

- Response A: control
- Response B: treatment

## Case Scores

| Case | Category | Control score | Treatment score | Lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| order-consistency | good | 7 | 9 | +2 | fail to pass | Treatment added stronger verification and failure-mode reasoning. |
| replica-lag | good | 7 | 10 | +3 | fail to pass | Treatment named read-your-writes and monotonic reads. |
| cache-as-truth | bad | 8 | 11 | +3 | fail to pass | Treatment rejected Redis as source of truth. |
| exactly-once-trap | adversarial | 8 | 11 | +3 | fail to pass | Treatment challenged end-to-end exactly-once. |
| vague-startup-architecture | bad | 8 | 10 | +2 | diagnostic improvement | Treatment scoped the recommendation and named missing requirements. |

## Dimension Differences

Treatment improved correctness reasoning, verification value, and anti-pattern resistance across the pilot cases.

## Response Archive

Responses are preserved under each case section in this file.

## Overall Decision

- Total control score: 38
- Total treatment score: 51
- Total lift: +13
- Limitations: This is a five-case pilot scored from preserved paired responses. It is not statistical proof.
""",
    )
```

Then add these tests to `class DdiaBenchmarkTest(unittest.TestCase)`:

```python
    def test_checker_accepts_complete_ab_assets(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(ab_errors, [])
        self.assertEqual(missing_paths, [])

    def test_checker_reports_missing_ab_file(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            (repo / "evaluation/ab/pilot-results.md").unlink()

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(ab_errors, [])
        self.assertIn("evaluation/ab/pilot-results.md", missing_paths)

    def test_checker_rejects_control_instructions_that_allow_skill(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            write(
                repo / "evaluation/ab/control-instructions.md",
                "# Control Instructions\n\nUse ddia-system-design for the answer.\n",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/control-instructions.md: must forbid using ddia-system-design",
            ab_errors,
        )

    def test_checker_rejects_pilot_missing_selected_case(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace(
                    "- evaluation/cases/bad/01-cache-as-truth.md\n",
                    "",
                ),
                encoding="utf-8",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: missing pilot case evaluation/cases/bad/01-cache-as-truth.md",
            ab_errors,
        )
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_benchmark -v
```

Expected: FAIL because `validate_ab_assets()` does not exist yet.

- [ ] **Step 3: Add A/B validator helper to checker**

Modify `/Users/Thin/Documents/ddia/scripts/check_ddia_benchmark.py`.

Add these constants after `GUIDE_PATH`:

```python
AB_REQUIRED_FILES = [
    "evaluation/ab/README.md",
    "evaluation/ab/control-instructions.md",
    "evaluation/ab/treatment-instructions.md",
    "evaluation/ab/blind-scoring-guide.md",
    "evaluation/ab/results-template.md",
    "evaluation/ab/pilot-results.md",
]

AB_README_SECTIONS = ["Purpose", "Method", "Pilot Case Set", "Limitations"]
AB_BLIND_SCORING_SECTIONS = ["Scoring Order", "Mapping Reveal"]
AB_RESULT_SECTIONS = [
    "Run Metadata",
    "Hidden Mapping",
    "Case Scores",
    "Dimension Differences",
    "Response Archive",
    "Overall Decision",
]
AB_PILOT_CASES = [
    "evaluation/cases/good/01-order-consistency.md",
    "evaluation/cases/good/04-replica-lag.md",
    "evaluation/cases/bad/01-cache-as-truth.md",
    "evaluation/cases/adversarial/02-exactly-once-trap.md",
    "evaluation/cases/bad/04-vague-startup-architecture.md",
]
AB_REQUIRED_PHRASES = {
    "evaluation/ab/README.md": ["control", "treatment", "pilot", "not statistical proof"],
    "evaluation/ab/control-instructions.md": [
        "without using or referencing ddia-system-design",
        "Do not load, invoke, mention, or rely on the DDIA system design skill",
    ],
    "evaluation/ab/treatment-instructions.md": [
        "Use ddia-system-design",
        "assumptions, recommendation, trade-offs, failure modes, correctness, operations, and tests",
    ],
    "evaluation/ab/blind-scoring-guide.md": [
        "Score Response A and Response B before revealing",
        "Reveal the mapping only after",
    ],
    "evaluation/ab/results-template.md": [
        "Control score",
        "Treatment score",
        "Lift",
        "Pass/fail change",
        "Response Archive",
    ],
    "evaluation/ab/pilot-results.md": [
        "Total control score:",
        "Total treatment score:",
        "Total lift:",
        "not statistical proof",
    ],
}
```

Add this helper after `validate_required_sections`:

```python
def validate_ab_assets(repo: pathlib.Path) -> tuple[list[str], list[str]]:
    missing_paths: list[str] = []
    errors: list[str] = []

    for relative in AB_REQUIRED_FILES:
        path = repo / relative
        text = read_text(path)
        if not path.exists():
            missing_paths.append(relative)
            continue
        if not text.strip():
            errors.append(f"{relative}: file is empty")
            continue
        for phrase in AB_REQUIRED_PHRASES.get(relative, []):
            if phrase not in text:
                errors.append(f"{relative}: missing phrase {phrase}")

    readme = repo / "evaluation/ab/README.md"
    if readme.exists():
        errors.extend(validate_required_sections(readme, "evaluation/ab/README.md", AB_README_SECTIONS))

    blind = repo / "evaluation/ab/blind-scoring-guide.md"
    if blind.exists():
        errors.extend(
            validate_required_sections(blind, "evaluation/ab/blind-scoring-guide.md", AB_BLIND_SCORING_SECTIONS)
        )

    template = repo / "evaluation/ab/results-template.md"
    if template.exists():
        errors.extend(validate_required_sections(template, "evaluation/ab/results-template.md", AB_RESULT_SECTIONS))

    pilot = repo / "evaluation/ab/pilot-results.md"
    if pilot.exists():
        pilot_text = read_text(pilot)
        errors.extend(validate_required_sections(pilot, "evaluation/ab/pilot-results.md", AB_RESULT_SECTIONS))
        for case in AB_PILOT_CASES:
            if case not in pilot_text:
                errors.append(f"evaluation/ab/pilot-results.md: missing pilot case {case}")
        for score_label in ["Control score", "Treatment score", "Lift", "Pass/fail change", "Notes"]:
            if score_label not in pilot_text:
                errors.append(f"evaluation/ab/pilot-results.md: missing score column {score_label}")

    control_text = read_text(repo / "evaluation/ab/control-instructions.md")
    if control_text and (
        "without using or referencing ddia-system-design" not in control_text
        or "Do not load, invoke, mention, or rely on the DDIA system design skill" not in control_text
    ):
        errors.append("evaluation/ab/control-instructions.md: must forbid using ddia-system-design")

    treatment_text = read_text(repo / "evaluation/ab/treatment-instructions.md")
    if treatment_text and "Use ddia-system-design" not in treatment_text:
        errors.append("evaluation/ab/treatment-instructions.md: must require using ddia-system-design")

    return missing_paths, errors
```

- [ ] **Step 4: Run tests to verify the isolated validator passes**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_benchmark -v
```

Expected: all tests pass. The validator is not wired into `check_benchmark()` yet, so the current repository benchmark remains green before the real `evaluation/ab/` files are added.

- [ ] **Step 5: Commit Task 1**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add scripts/check_ddia_benchmark.py tests/test_ddia_benchmark.py
git commit -m "test: add ddia ab benchmark validation"
```

---

### Task 2: Add A/B Framework Documentation

**Files:**
- Create: `/Users/Thin/Documents/ddia/evaluation/ab/README.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/ab/control-instructions.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/ab/treatment-instructions.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/ab/blind-scoring-guide.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/ab/results-template.md`

- [ ] **Step 1: Add A/B README**

Create `/Users/Thin/Documents/ddia/evaluation/ab/README.md`:

```markdown
# DDIA Skill A/B Evaluation

## Purpose

Use this A/B workflow to compare backend architecture answers from the same model with and without `ddia-system-design`.

The control response answers the case without using or referencing the skill. The treatment response answers the same case with the skill. Both responses use the same case prompt and the same answer-quality rubric.

## Method

1. Pick benchmark cases from `evaluation/cases/`.
2. Generate a control response with `control-instructions.md`.
3. Generate a treatment response with `treatment-instructions.md`.
4. Label the responses as `Response A` and `Response B`.
5. Score both responses with `blind-scoring-guide.md` before revealing the mapping.
6. Record control score, treatment score, lift, pass/fail change, and notes.

## Pilot Case Set

- `evaluation/cases/good/01-order-consistency.md`
- `evaluation/cases/good/04-replica-lag.md`
- `evaluation/cases/bad/01-cache-as-truth.md`
- `evaluation/cases/adversarial/02-exactly-once-trap.md`
- `evaluation/cases/bad/04-vague-startup-architecture.md`

## Limitations

This is pilot A/B evidence, not statistical proof. A stronger study would use independent blinded scoring, repeated randomized runs, and more than one model.
```

- [ ] **Step 2: Add control instructions**

Create `/Users/Thin/Documents/ddia/evaluation/ab/control-instructions.md`:

```markdown
# Control Instructions

Answer the benchmark case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill.

Use your general backend architecture knowledge. Give a useful answer, but do not use the DDIA skill workflow, DDIA reference files, or DDIA skill response shape.
```

- [ ] **Step 3: Add treatment instructions**

Create `/Users/Thin/Documents/ddia/evaluation/ab/treatment-instructions.md`:

```markdown
# Treatment Instructions

Use ddia-system-design for the benchmark case.

Follow the ddia-system-design response shape: assumptions, recommendation, trade-offs, failure modes, correctness, operations, and tests.

Use the skill's guardrails: frame workload before recommending, challenge unsafe premises, treat derived data as derived, and convert design claims into verification steps.
```

- [ ] **Step 4: Add blind scoring guide**

Create `/Users/Thin/Documents/ddia/evaluation/ab/blind-scoring-guide.md`:

```markdown
# Blind Scoring Guide

## Scoring Order

Score Response A and Response B before revealing which response is control or treatment.

Use `evaluation/rubrics/answer-quality.md` for every response. For good cases, score five dimensions for a maximum of 10. For bad and adversarial cases, also score Anti-pattern resistance for a maximum of 12.

## Mapping Reveal

Reveal the mapping only after all dimensions, notes, totals, and pass/fail decisions are recorded.

After revealing the mapping, compute treatment lift:

```text
treatment score - control score
```

Record whether the treatment changed the pass/fail decision and which dimensions improved or regressed.
```

- [ ] **Step 5: Add A/B result template**

Create `/Users/Thin/Documents/ddia/evaluation/ab/results-template.md`:

```markdown
# DDIA Skill A/B Results Template

## Run Metadata

- Evaluator: write the evaluator name.
- Date: write the run date in YYYY-MM-DD format.
- Model: write the model name.
- Skill version: write the Git commit or skill version.

## Hidden Mapping

- Response A: write control or treatment after scoring.
- Response B: write control or treatment after scoring.

## Case Scores

| Case | Category | Control score | Treatment score | Lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Add one row per case. | Use good, bad, or adversarial. | Score after reveal. | Score after reveal. | Treatment minus control. | State no change, fail to pass, pass to fail, or diagnostic change. | Record scoring rationale. |

## Dimension Differences

Record workload framing, trade-off quality, failure-mode coverage, correctness reasoning, verification value, and anti-pattern resistance differences.

## Response Archive

For each case, preserve Response A and Response B exactly as evaluated.

## Overall Decision

- Total control score: write the total.
- Total treatment score: write the total.
- Total lift: write treatment minus control.
- Limitations: write the study limitations.
```

- [ ] **Step 6: Verify only the pilot result is still missing**

Run:

```bash
cd /Users/Thin/Documents/ddia
python3 - <<'PY'
import importlib.util
import pathlib

repo = pathlib.Path("/Users/Thin/Documents/ddia")
module_path = repo / "scripts" / "check_ddia_benchmark.py"
spec = importlib.util.spec_from_file_location("check_ddia_benchmark", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

missing_paths, ab_errors = module.validate_ab_assets(repo)
print({"missing_paths": missing_paths, "ab_errors": ab_errors})
expected_missing = ["evaluation/ab/pilot-results.md"]
raise SystemExit(0 if missing_paths == expected_missing and ab_errors == [] else 1)
PY
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_benchmark -v
```

Expected: the inline validator exits 0 after printing `{"missing_paths": ["evaluation/ab/pilot-results.md"], "ab_errors": []}`. The benchmark unit tests pass because full A/B integration is deferred until Task 4.

- [ ] **Step 7: Commit Task 2**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add evaluation/ab/README.md evaluation/ab/control-instructions.md evaluation/ab/treatment-instructions.md evaluation/ab/blind-scoring-guide.md evaluation/ab/results-template.md
git commit -m "docs: add ddia ab benchmark framework"
```

---

### Task 3: Add Pilot A/B Results

**Files:**
- Create: `/Users/Thin/Documents/ddia/evaluation/ab/pilot-results.md`

- [ ] **Step 1: Add pilot result file**

Create `/Users/Thin/Documents/ddia/evaluation/ab/pilot-results.md`:

```markdown
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

| Case | Category | Control score | Treatment score | Lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| order-consistency | good | 7/10 | 9/10 | +2 | fail to pass | Treatment added clearer source-of-truth boundaries, idempotency, reconciliation, and falsifiable checks. |
| replica-lag | good | 7/10 | 10/10 | +3 | fail to pass | Treatment named read-your-writes and monotonic reads, then tied mitigations to session routing and lag metrics. |
| cache-as-truth | bad | 8/12 | 11/12 | +3 | fail to pass | Treatment rejected Redis as authoritative for payment decisions and kept financial invariants in transactional storage. |
| exactly-once-trap | adversarial | 8/12 | 11/12 | +3 | fail to pass | Treatment challenged end-to-end exactly-once and added idempotency boundaries for external side effects and ledger writes. |
| vague-startup-architecture | bad | 8/12 | 10/12 | +2 | diagnostic improvement | Treatment gave a scoped default, listed missing requirements, and avoided overconfident database selection. |

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

## Overall Decision

- Total control score: 38
- Total treatment score: 51
- Total lift: +13
- Limitations: This is a five-case pilot scored from preserved paired responses. It is not statistical proof.
```

- [ ] **Step 2: Run validator and existing benchmark checker**

Run:

```bash
cd /Users/Thin/Documents/ddia
python3 - <<'PY'
import importlib.util
import pathlib

repo = pathlib.Path("/Users/Thin/Documents/ddia")
module_path = repo / "scripts" / "check_ddia_benchmark.py"
spec = importlib.util.spec_from_file_location("check_ddia_benchmark", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

missing_paths, ab_errors = module.validate_ab_assets(repo)
print({"missing_paths": missing_paths, "ab_errors": ab_errors})
raise SystemExit(1 if missing_paths or ab_errors else 0)
PY
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_benchmark.py --repo /Users/Thin/Documents/ddia
```

Expected: the inline validator exits 0 and prints `{"missing_paths": [], "ab_errors": []}`. The benchmark checker also exits 0 under the existing non-A/B checks. Full benchmark-checker integration happens in Task 4 after all A/B assets are present.

- [ ] **Step 3: Commit Task 3**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add evaluation/ab/pilot-results.md
git commit -m "test: record ddia ab pilot results"
```

---

### Task 4: Integrate A/B Validation And Update README

**Files:**
- Modify: `/Users/Thin/Documents/ddia/scripts/check_ddia_benchmark.py`
- Modify: `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`
- Modify: `/Users/Thin/Documents/ddia/README.md`

- [ ] **Step 1: Wire A/B validation into the benchmark checker**

In `/Users/Thin/Documents/ddia/scripts/check_ddia_benchmark.py`, add this before the return dictionary in `check_benchmark()`:

```python
    ab_missing_paths, ab_errors = validate_ab_assets(repo)
    missing_paths.extend(ab_missing_paths)
```

Add `"ab_errors": ab_errors,` to the returned dictionary:

```python
    return {
        "case_counts": case_counts,
        "missing_paths": missing_paths,
        "case_errors": case_errors,
        "rubric_errors": rubric_errors,
        "template_errors": template_errors,
        "guide_errors": guide_errors,
        "ab_errors": ab_errors,
    }
```

Update the `error_keys` list in `main()`:

```python
    error_keys = [
        "missing_paths",
        "case_errors",
        "rubric_errors",
        "template_errors",
        "guide_errors",
        "ab_errors",
    ]
```

- [ ] **Step 2: Add benchmark integration tests for A/B validation**

In `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`, update `test_current_repo_benchmark_is_complete` to include:

```python
        self.assertEqual(report["ab_errors"], [])
```

Update `test_checker_accepts_complete_benchmark` so the temp repository includes A/B assets:

```python
    def test_checker_accepts_complete_benchmark(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)

            report = checker.check_benchmark(repo)

        self.assertEqual(report["case_counts"], {"good": 5, "bad": 4, "adversarial": 4})
        self.assertEqual(report["missing_paths"], [])
        self.assertEqual(report["case_errors"], [])
        self.assertEqual(report["rubric_errors"], [])
        self.assertEqual(report["template_errors"], [])
        self.assertEqual(report["guide_errors"], [])
        self.assertEqual(report["ab_errors"], [])
```

Add this integration test to `class DdiaBenchmarkTest(unittest.TestCase)`:

```python
    def test_benchmark_checker_reports_missing_ab_file(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            (repo / "evaluation/ab/pilot-results.md").unlink()

            report = checker.check_benchmark(repo)

        self.assertIn("evaluation/ab/pilot-results.md", report["missing_paths"])
```

- [ ] **Step 3: Replace A/B status section**

In `/Users/Thin/Documents/ddia/README.md`, replace the current `## A/B Status` section with:

```markdown
## Pilot A/B Result

The repository now includes a five-case pilot A/B evaluation. It compares the
same model answering selected benchmark cases without the skill against the
same model answering with `ddia-system-design`.

Pilot result:

- Control total: 38
- Treatment total: 51
- Lift: +13 points across 5 cases
- Pass-rate change: treatment moved four must-pass cases from fail to pass

The strongest gains came from correctness reasoning, verification value, and
anti-pattern resistance. The treatment responses challenged unsafe premises
more directly, including Redis-as-payment-truth and end-to-end exactly-once
claims.

This is pilot A/B evidence, not statistical proof. The response text, scoring
notes, and mapping are preserved in
[`evaluation/ab/pilot-results.md`](evaluation/ab/pilot-results.md) so another
evaluator can rescore the run.
```

- [ ] **Step 4: Add A/B files to repository layout**

In the repository layout block, add:

```text
evaluation/ab/                  A/B instructions, template, and pilot result
```

- [ ] **Step 5: Run README, tests, and checker validation**

Run:

```bash
cd /Users/Thin/Documents/ddia
LC_ALL=C rg -n "[^\\x00-\\x7F]" README.md
git diff --check
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_benchmark -v
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_benchmark.py --repo /Users/Thin/Documents/ddia
```

Expected:

- `rg` exits 1 with no output.
- `git diff --check` exits 0.
- the benchmark unit tests pass.
- benchmark checker exits 0.

- [ ] **Step 6: Commit Task 4**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add scripts/check_ddia_benchmark.py tests/test_ddia_benchmark.py README.md
git commit -m "docs: add ddia ab pilot summary"
```

---

### Task 5: Final Verification And Publish

**Files:**
- No source changes expected.

- [ ] **Step 1: Run full tests**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Run existing skill quality checker**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_skill_quality.py --repo /Users/Thin/Documents/ddia
```

Expected output includes:

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

Expected output includes empty:

```json
{
  "ab_errors": [],
  "case_errors": [],
  "guide_errors": [],
  "missing_paths": [],
  "rubric_errors": [],
  "template_errors": []
}
```

- [ ] **Step 4: Check git state**

Run:

```bash
cd /Users/Thin/Documents/ddia
git status --short --branch
```

Expected output starts with:

```text
## codex/ddia-system-design-skill...origin/codex/ddia-system-design-skill
```

No modified or untracked files should remain.

- [ ] **Step 5: Push branch**

Run:

```bash
cd /Users/Thin/Documents/ddia
git push origin codex/ddia-system-design-skill
```

Expected: push succeeds to `git@github.com:seasonsolt/ddia-skill.git`.

---

## Self-Review Checklist

- The plan implements every section of `/Users/Thin/Documents/ddia/docs/superpowers/specs/2026-06-22-ddia-ab-benchmark-design.md`.
- The A/B framework has control instructions, treatment instructions, blind scoring, a template, and a pilot result.
- The pilot uses the five approved cases.
- The pilot result preserves both responses and reports control score, treatment score, lift, pass/fail change, notes, and limitations.
- The validator checks required A/B files and fails on missing or incomplete A/B assets.
- The README reports pilot A/B evidence without claiming statistical proof.
