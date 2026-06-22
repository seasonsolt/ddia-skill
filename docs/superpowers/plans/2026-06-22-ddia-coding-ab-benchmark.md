# DDIA Coding A/B Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Java code-review-patch A/B benchmark that tests whether `ddia-system-design` improves concrete backend implementation choices.

**Architecture:** Keep the coding benchmark separate from the existing prose A/B benchmark under `evaluation/coding-ab/`. Extend `scripts/check_ddia_benchmark.py` with focused coding A/B validators, and cover them through `tests/test_ddia_benchmark.py`. The benchmark stores flawed Java snippets, control/treatment instructions, a blinded LLM judge guide, a result template, and deterministic validation for case structure and judge JSON.

**Tech Stack:** Markdown benchmark files, Java snippets embedded in Markdown, Python standard library validation, `unittest`.

---

## File Structure

- Create `evaluation/coding-ab/README.md`: explains the coding A/B workflow.
- Create `evaluation/coding-ab/control-instructions.md`: control prompt for patching Java without `ddia-system-design`.
- Create `evaluation/coding-ab/treatment-instructions.md`: treatment prompt requiring `ddia-system-design`.
- Create `evaluation/coding-ab/blind-llm-judge.md`: LLM judge rubric and required JSON output.
- Create `evaluation/coding-ab/results-template.md`: result record template for coding A/B runs.
- Create `evaluation/coding-ab/cases/checkout-cache-as-truth.md`: flawed Redis checkout code.
- Create `evaluation/coding-ab/cases/payment-exactly-once-trap.md`: flawed payment event pipeline code.
- Create `evaluation/coding-ab/cases/order-outbox-missing.md`: flawed order/event transaction code.
- Create `evaluation/coding-ab/cases/profile-replica-lag.md`: flawed immediate replica read code.
- Create `evaluation/coding-ab/cases/redis-distributed-lock-money-transfer.md`: flawed Redis lock transfer code.
- Modify `scripts/check_ddia_benchmark.py`: add coding A/B asset, case, and judge JSON validators.
- Modify `tests/test_ddia_benchmark.py`: add tests for coding A/B success and failure paths.
- Modify `README.md`: mention the stronger coding A/B track and validation command.
- Modify `evaluation/benchmark-guide.md`: include the coding A/B benchmark in run guidance.

## Task 1: Coding A/B Assets And Baseline Validation

**Files:**
- Create: `evaluation/coding-ab/README.md`
- Create: `evaluation/coding-ab/control-instructions.md`
- Create: `evaluation/coding-ab/treatment-instructions.md`
- Create: `evaluation/coding-ab/blind-llm-judge.md`
- Create: `evaluation/coding-ab/results-template.md`
- Create: `evaluation/coding-ab/cases/checkout-cache-as-truth.md`
- Create: `evaluation/coding-ab/cases/payment-exactly-once-trap.md`
- Create: `evaluation/coding-ab/cases/order-outbox-missing.md`
- Create: `evaluation/coding-ab/cases/profile-replica-lag.md`
- Create: `evaluation/coding-ab/cases/redis-distributed-lock-money-transfer.md`
- Modify: `scripts/check_ddia_benchmark.py`
- Modify: `tests/test_ddia_benchmark.py`

- [ ] **Step 1: Write failing tests for coding A/B assets**

Add these constants and helpers near the existing A/B helper section in `tests/test_ddia_benchmark.py`:

~~~~python
CODING_AB_REQUIRED_FILES = [
    "evaluation/coding-ab/README.md",
    "evaluation/coding-ab/control-instructions.md",
    "evaluation/coding-ab/treatment-instructions.md",
    "evaluation/coding-ab/blind-llm-judge.md",
    "evaluation/coding-ab/results-template.md",
]


def coding_case_text(
    *,
    title: str = "Checkout Cache As Truth",
    case_id: str = "checkout-cache-as-truth",
    category: str = "bad",
    ddia_topics: str = "storage and retrieval, transactions, derived data and correctness",
) -> str:
    return f"""# Coding Case: {title}

Case ID: {case_id}
Category: {category}
Language: Java
Primary DDIA topics: {ddia_topics}

## Context

The service contains a backend correctness bug hidden in a Java snippet. Patch the code so the business invariant survives retries, stale data, and partial failures.

## Flawed Java

```java
final class CheckoutService {{
    private final RedisClient redis;
    private final PaymentGateway paymentGateway;

    CheckoutReceipt checkout(String cartId, String paymentMethodId) {{
        long amountCents = redis.getLong("cart:" + cartId + ":total");
        String chargeId = paymentGateway.charge(paymentMethodId, amountCents);
        return new CheckoutReceipt(cartId, chargeId, amountCents);
    }}
}}
```

## Patch Instructions

Return a patched Java snippet and a short explanation using the required response format.

## Unsafe Premise

The snippet treats fast derived cache data as authoritative for a payment decision.

## Strong Patch Signals

- Reads or recomputes the final payable amount from authoritative database state.
- Keeps Redis as derived preview state only.
- Adds an explicit mismatch, stale-data, or recomputation path.
- Names verification such as stale-cache tests and cache/database mismatch metrics.

## Weak Patch Patterns

- Leaves Redis as the source of truth for the charged amount.
- Adds retries without fixing the authoritative boundary.
- Gives prose advice without changing the Java boundary.

## Scoring Notes

- Score source-of-truth boundary based on whether payment decisions avoid Redis-derived values.
- Score Java patch quality based on whether the snippet shows concrete methods and transaction boundaries.
"""


def make_complete_coding_ab_assets(root: pathlib.Path) -> None:
    write(
        root / "evaluation/coding-ab/README.md",
        """# DDIA Coding A/B Evaluation

## Purpose

Compare Java patch responses from the same model with and without ddia-system-design.

## Method

Run the same flawed Java case through the control and treatment instructions, randomize Response A and Response B, and score both patches with the blinded LLM judge.

## Coding Case Set

- evaluation/coding-ab/cases/checkout-cache-as-truth.md
- evaluation/coding-ab/cases/payment-exactly-once-trap.md
- evaluation/coding-ab/cases/order-outbox-missing.md
- evaluation/coding-ab/cases/profile-replica-lag.md
- evaluation/coding-ab/cases/redis-distributed-lock-money-transfer.md

## LLM Judge

Use evaluation/coding-ab/blind-llm-judge.md and preserve the judge JSON.

## Limitations

The code snippets are judged for architectural correctness and do not need to compile.
""",
    )
    write(
        root / "evaluation/coding-ab/control-instructions.md",
        """# Coding A/B Control Instructions

Patch the Java code without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill.

Use the required response format:

## Patched Java

```java
// patched code
```

## Why this fixes the bug

- Give 5 to 8 concise bullets.
""",
    )
    write(
        root / "evaluation/coding-ab/treatment-instructions.md",
        """# Coding A/B Treatment Instructions

Use ddia-system-design to patch the Java code.

Apply the skill guardrails: frame the correctness boundary, challenge unsafe premises, treat derived data as derived, and convert failure modes into verification checks.

Use the required response format:

## Patched Java

```java
// patched code
```

## Why this fixes the bug

- Give 5 to 8 concise bullets.
""",
    )
    write(
        root / "evaluation/coding-ab/blind-llm-judge.md",
        """# Coding A/B Blind LLM Judge

## Scoring Order

Score Response A and Response B before revealing which response is control or treatment.

## Dimensions

1. Correctness invariant
2. Source-of-truth boundary
3. Failure-mode handling
4. Idempotency and retry safety
5. Operational verification
6. Java patch quality
7. Anti-pattern resistance

## JSON Output

Return valid JSON with case_id, response_a, response_b, scores, total, pass, and rationale.

## Mapping Reveal

Reveal the mapping only after scores and pass decisions are recorded.
""",
    )
    write(
        root / "evaluation/coding-ab/results-template.md",
        """# DDIA Coding A/B Results Template

## Run Metadata

- Evaluator:
- Date:
- Model:
- Skill version:
- Judge model:
- Randomization seed:

## Hidden Mapping

- Response A:
- Response B:

## Judge Input Record

Record the case path, anonymized response order, and judge prompt version.

## Case Scores

| Case | Category | Control score | Treatment score | Lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- |

## Judge JSON Archive

Preserve the raw judge JSON for every case.

## Overall Decision

- Total control score:
- Total treatment score:
- Total lift:
- Limitations:
""",
    )
    cases = [
        ("checkout-cache-as-truth", "Checkout Cache As Truth", "bad"),
        ("payment-exactly-once-trap", "Payment Exactly Once Trap", "adversarial"),
        ("order-outbox-missing", "Order Outbox Missing", "bad"),
        ("profile-replica-lag", "Profile Replica Lag", "bad"),
        ("redis-distributed-lock-money-transfer", "Redis Distributed Lock Money Transfer", "adversarial"),
    ]
    for case_id, title, category in cases:
        write(
            root / f"evaluation/coding-ab/cases/{case_id}.md",
            coding_case_text(title=title, case_id=case_id, category=category),
        )
~~~~

Add these tests inside `class DdiaBenchmarkTest(unittest.TestCase)`:

```python
    def test_current_repo_coding_ab_assets_are_complete(self):
        checker = load_checker()

        report = checker.check_benchmark(REPO)

        self.assertEqual(report["coding_ab_missing_paths"], [])
        self.assertEqual(report["coding_ab_errors"], [])

    def test_checker_accepts_complete_coding_ab_assets(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_coding_ab_assets(repo)

            missing_paths, errors = checker.validate_coding_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertEqual(errors, [])

    def test_checker_rejects_coding_case_without_java_block(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_coding_ab_assets(repo)
            case_path = repo / "evaluation/coding-ab/cases/checkout-cache-as-truth.md"
            case_path.write_text(
                case_path.read_text(encoding="utf-8").replace("```java", "```text", 1),
                encoding="utf-8",
            )

            missing_paths, errors = checker.validate_coding_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/coding-ab/cases/checkout-cache-as-truth.md: Flawed Java must include a java code block",
            errors,
        )
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_checker_accepts_complete_coding_ab_assets -v
```

Expected: FAIL with `AttributeError: module 'check_ddia_benchmark' has no attribute 'validate_coding_ab_assets'`.

- [ ] **Step 3: Add coding A/B checker support**

Add these constants after `AB_REQUIRED_PHRASES` in `scripts/check_ddia_benchmark.py`:

```python
CODING_AB_CASES_DIR = pathlib.Path("evaluation/coding-ab/cases")
CODING_AB_REQUIRED_CASES = {
    "checkout-cache-as-truth.md": "bad",
    "payment-exactly-once-trap.md": "adversarial",
    "order-outbox-missing.md": "bad",
    "profile-replica-lag.md": "bad",
    "redis-distributed-lock-money-transfer.md": "adversarial",
}
CODING_AB_REQUIRED_FILES = [
    "evaluation/coding-ab/README.md",
    "evaluation/coding-ab/control-instructions.md",
    "evaluation/coding-ab/treatment-instructions.md",
    "evaluation/coding-ab/blind-llm-judge.md",
    "evaluation/coding-ab/results-template.md",
]
CODING_AB_CASE_SECTIONS = [
    "Context",
    "Flawed Java",
    "Patch Instructions",
    "Unsafe Premise",
    "Strong Patch Signals",
    "Weak Patch Patterns",
    "Scoring Notes",
]
CODING_AB_BULLET_SECTIONS = [
    "Strong Patch Signals",
    "Weak Patch Patterns",
    "Scoring Notes",
]
CODING_AB_README_SECTIONS = ["Purpose", "Method", "Coding Case Set", "LLM Judge", "Limitations"]
CODING_AB_JUDGE_SECTIONS = ["Scoring Order", "Dimensions", "JSON Output", "Mapping Reveal"]
CODING_AB_RESULT_SECTIONS = [
    "Run Metadata",
    "Hidden Mapping",
    "Judge Input Record",
    "Case Scores",
    "Judge JSON Archive",
    "Overall Decision",
]
CODING_AB_SCORE_DIMENSIONS = [
    "Correctness invariant",
    "Source-of-truth boundary",
    "Failure-mode handling",
    "Idempotency and retry safety",
    "Operational verification",
    "Java patch quality",
    "Anti-pattern resistance",
]
```

Add these functions before `check_benchmark`:

```python
def validate_coding_ab_case(path: pathlib.Path, relative: str, expected_category: str) -> list[str]:
    text = read_text(path)
    errors: list[str] = []
    lines = text.splitlines()

    if not lines or not lines[0].startswith("# Coding Case: ") or not lines[0][len("# Coding Case: ") :].strip():
        errors.append(f"{relative}: missing # Coding Case: heading")

    if not metadata_value(text, "Case ID"):
        errors.append(f"{relative}: missing Case ID")

    if metadata_value(text, "Category") != expected_category:
        errors.append(f"{relative}: expected Category: {expected_category}")

    if metadata_value(text, "Language") != "Java":
        errors.append(f"{relative}: expected Language: Java")

    if not metadata_value(text, "Primary DDIA topics"):
        errors.append(f"{relative}: missing Primary DDIA topics")

    for section in CODING_AB_CASE_SECTIONS:
        body = section_body(text, section)
        if body is None:
            errors.append(f"{relative}: missing section {section}")
            continue
        if section == "Context" and len(body.strip()) < 80:
            errors.append(f"{relative}: Context must be at least 80 characters")
        if section == "Flawed Java" and "```java" not in body:
            errors.append(f"{relative}: Flawed Java must include a java code block")
        if section in CODING_AB_BULLET_SECTIONS and not has_bullet(body):
            errors.append(f"{relative}: section {section} must include at least one bullet")

    return errors


def validate_coding_ab_assets(repo: pathlib.Path) -> tuple[list[str], list[str]]:
    missing_paths: list[str] = []
    errors: list[str] = []

    for relative in CODING_AB_REQUIRED_FILES:
        path = repo / relative
        text = read_text(path)
        if not path.exists():
            missing_paths.append(relative)
            continue
        if not text.strip():
            errors.append(f"{relative}: file is empty")

    readme = repo / "evaluation/coding-ab/README.md"
    if readme.exists():
        errors.extend(validate_required_sections(readme, "evaluation/coding-ab/README.md", CODING_AB_README_SECTIONS))

    judge = repo / "evaluation/coding-ab/blind-llm-judge.md"
    if judge.exists():
        errors.extend(validate_required_sections(judge, "evaluation/coding-ab/blind-llm-judge.md", CODING_AB_JUDGE_SECTIONS))
        judge_body = section_body(read_text(judge), "Dimensions") or ""
        for dimension in CODING_AB_SCORE_DIMENSIONS:
            if dimension not in judge_body:
                errors.append(f"evaluation/coding-ab/blind-llm-judge.md: missing dimension {dimension}")

    template = repo / "evaluation/coding-ab/results-template.md"
    if template.exists():
        errors.extend(
            validate_required_sections(template, "evaluation/coding-ab/results-template.md", CODING_AB_RESULT_SECTIONS)
        )

    control_text = read_text(repo / "evaluation/coding-ab/control-instructions.md")
    if control_text and (
        "without using or referencing ddia-system-design" not in control_text
        or "Do not load, invoke, mention, or rely on the DDIA system design skill" not in control_text
        or "## Patched Java" not in control_text
        or "## Why this fixes the bug" not in control_text
    ):
        errors.append("evaluation/coding-ab/control-instructions.md: must forbid skill use and require response format")

    treatment_text = read_text(repo / "evaluation/coding-ab/treatment-instructions.md")
    if treatment_text and (
        "Use ddia-system-design" not in treatment_text
        or "## Patched Java" not in treatment_text
        or "## Why this fixes the bug" not in treatment_text
    ):
        errors.append("evaluation/coding-ab/treatment-instructions.md: must require skill use and response format")

    case_dir = repo / CODING_AB_CASES_DIR
    if not case_dir.exists():
        missing_paths.append(CODING_AB_CASES_DIR.as_posix())
    else:
        case_files = {path.name: path for path in sorted(case_dir.glob("*.md"))}
        for filename, category in CODING_AB_REQUIRED_CASES.items():
            path = case_files.get(filename)
            relative = (CODING_AB_CASES_DIR / filename).as_posix()
            if path is None:
                missing_paths.append(relative)
                continue
            errors.extend(validate_coding_ab_case(path, relative, category))
        for filename in case_files:
            if filename not in CODING_AB_REQUIRED_CASES:
                errors.append(f"evaluation/coding-ab/cases/{filename}: unexpected coding case")

    return missing_paths, errors
```

Update `check_benchmark`:

```python
    coding_ab_missing_paths, coding_ab_errors = validate_coding_ab_assets(repo)
    missing_paths.extend(coding_ab_missing_paths)

    return {
        "case_counts": case_counts,
        "missing_paths": missing_paths,
        "case_errors": case_errors,
        "rubric_errors": rubric_errors,
        "template_errors": template_errors,
        "guide_errors": guide_errors,
        "ab_errors": ab_errors,
        "coding_ab_missing_paths": coding_ab_missing_paths,
        "coding_ab_errors": coding_ab_errors,
    }
```

Update `main` error keys:

```python
    error_keys = [
        "missing_paths",
        "case_errors",
        "rubric_errors",
        "template_errors",
        "guide_errors",
        "ab_errors",
        "coding_ab_errors",
    ]
```

- [ ] **Step 4: Add the coding A/B files**

Create `evaluation/coding-ab/README.md`:

~~~~markdown
# DDIA Coding A/B Evaluation

## Purpose

Use this workflow to compare Java patch responses from the same model with and without `ddia-system-design`.

The control response patches the flawed Java snippet without using the skill. The treatment response patches the same snippet with the skill. A blinded LLM judge scores both patches before the mapping is revealed.

## Method

1. Pick a coding case from `evaluation/coding-ab/cases/`.
2. Generate the control response with `control-instructions.md`.
3. Generate the treatment response with `treatment-instructions.md`.
4. Randomize the responses as `Response A` and `Response B`.
5. Score both responses with `blind-llm-judge.md`.
6. Preserve the raw responses, judge JSON, hidden mapping, lift, and limitations.

## Coding Case Set

- `evaluation/coding-ab/cases/checkout-cache-as-truth.md`
- `evaluation/coding-ab/cases/payment-exactly-once-trap.md`
- `evaluation/coding-ab/cases/order-outbox-missing.md`
- `evaluation/coding-ab/cases/profile-replica-lag.md`
- `evaluation/coding-ab/cases/redis-distributed-lock-money-transfer.md`

## LLM Judge

The judge scores correctness invariant, source-of-truth boundary, failure-mode handling, idempotency and retry safety, operational verification, Java patch quality, and anti-pattern resistance.

The judge must not know which response used the skill until after scores are recorded.

## Limitations

The snippets are judged for backend correctness boundaries and do not need to compile. A stronger study should run repeated randomized trials, use more than one judge, and add human spot checks.
~~~~

Create `evaluation/coding-ab/control-instructions.md`:

~~~~markdown
# Coding A/B Control Instructions

Patch the Java code without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill.

Use your general backend engineering knowledge. Give a concrete Java patch, not only prose.

Use this response format:

## Patched Java

```java
// patched code
```

## Why this fixes the bug

- Give 5 to 8 concise bullets.
~~~~

Create `evaluation/coding-ab/treatment-instructions.md`:

~~~~markdown
# Coding A/B Treatment Instructions

Use ddia-system-design to patch the Java code.

Apply the skill guardrails: frame the correctness boundary, challenge unsafe premises, treat derived data as derived, and convert failure modes into verification checks.

Give a concrete Java patch, not only prose.

Use this response format:

## Patched Java

```java
// patched code
```

## Why this fixes the bug

- Give 5 to 8 concise bullets.
~~~~

Create `evaluation/coding-ab/blind-llm-judge.md`:

~~~~markdown
# Coding A/B Blind LLM Judge

## Scoring Order

Score Response A and Response B before revealing which response is control or treatment.

Use only the coding case, flawed Java snippet, anonymized patched responses, and this rubric. Do not reward a response for mentioning DDIA, and do not infer which response used the skill.

## Dimensions

1. Correctness invariant: 0 means the invariant is still unsafe, 1 means partly protected, 2 means the patch clearly protects the business invariant.
2. Source-of-truth boundary: 0 means the patch still trusts derived state, 1 means it names the boundary but leaves gaps, 2 means authoritative decisions use authoritative state.
3. Failure-mode handling: 0 means the specific failure window remains, 1 means some failure paths are handled, 2 means the patch addresses the relevant crash, timeout, lag, retry, or partial failure.
4. Idempotency and retry safety: 0 means retries can duplicate effects, 1 means partial dedupe exists, 2 means repeated requests or messages are safe at the right boundary.
5. Operational verification: 0 means no concrete checks, 1 means generic checks, 2 means specific tests, metrics, reconciliation, or runbook checks.
6. Java patch quality: 0 means vague pseudocode, 1 means plausible but underspecified code, 2 means concrete Java boundaries and method responsibilities are visible.
7. Anti-pattern resistance: 0 means the unsafe premise is accepted, 1 means it is softened, 2 means it is directly rejected. Use `null` for cases that do not require this dimension.

## JSON Output

Return valid JSON with this shape:

```json
{
  "case_id": "checkout-cache-as-truth",
  "response_a": {
    "scores": {
      "correctness_invariant": 2,
      "source_of_truth_boundary": 2,
      "failure_mode_handling": 2,
      "idempotency_retry_safety": 1,
      "operational_verification": 2,
      "java_patch_quality": 2,
      "anti_pattern_resistance": 2
    },
    "total": 13,
    "pass": true,
    "rationale": "The patch moves checkout amount authority to database state and treats Redis as derived state."
  },
  "response_b": {
    "scores": {
      "correctness_invariant": 1,
      "source_of_truth_boundary": 0,
      "failure_mode_handling": 1,
      "idempotency_retry_safety": 1,
      "operational_verification": 1,
      "java_patch_quality": 1,
      "anti_pattern_resistance": 0
    },
    "total": 5,
    "pass": false,
    "rationale": "The patch keeps Redis on the payment path."
  }
}
```

## Mapping Reveal

Reveal the mapping only after all scores, totals, pass decisions, and rationales are recorded.
~~~~

Create `evaluation/coding-ab/results-template.md`:

```markdown
# DDIA Coding A/B Results Template

## Run Metadata

- Evaluator:
- Date:
- Model:
- Skill version:
- Judge model:
- Randomization seed:

## Hidden Mapping

- Response A:
- Response B:

## Judge Input Record

Record the case path, anonymized response order, and judge prompt version.

## Case Scores

| Case | Category | Control score | Treatment score | Lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- |

## Judge JSON Archive

Preserve the raw judge JSON for every case.

## Overall Decision

- Total control score:
- Total treatment score:
- Total lift:
- Limitations:
```

- [ ] **Step 5: Add full coding case files**

Create `evaluation/coding-ab/cases/checkout-cache-as-truth.md`:

````markdown
# Coding Case: Checkout Cache As Truth

Case ID: checkout-cache-as-truth
Category: bad
Language: Java
Primary DDIA topics: storage and retrieval, transactions, derived data and correctness

## Context

The checkout service charges the final payable amount for a cart. Redis stores a fast cart-total preview that is updated after cart changes. PostgreSQL stores cart line items and checkout records. A stale or lost Redis value can charge the wrong amount.

## Flawed Java

```java
final class CheckoutService {
    private final RedisClient redis;
    private final CartRepository cartRepository;
    private final PaymentGateway paymentGateway;
    private final AsyncCartTotalWriter asyncCartTotalWriter;

    CheckoutReceipt checkout(String cartId, String paymentMethodId) {
        long amountCents = redis.getLong("cart:" + cartId + ":total");
        String chargeId = paymentGateway.charge(paymentMethodId, amountCents);
        asyncCartTotalWriter.persistLater(cartId, amountCents);
        return new CheckoutReceipt(cartId, chargeId, amountCents);
    }
}
```

## Patch Instructions

Patch the Java so the charged amount comes from authoritative state. Redis may remain on the preview path, but it must not decide the final payment amount.

## Unsafe Premise

The code treats Redis as authoritative for a financial decision because it is fast and available.

## Strong Patch Signals

- Reads or recomputes the final payable amount from PostgreSQL line items inside the checkout boundary.
- Keeps Redis as derived preview state only.
- Adds an explicit stale-cache, mismatch, or recomputation path.
- Mentions stale-cache tests, cache/database mismatch metrics, and concurrent cart-change tests.

## Weak Patch Patterns

- Leaves `redis.getLong` as the amount charged by the payment gateway.
- Adds retries around Redis or payment without fixing the authoritative boundary.
- Updates PostgreSQL after the charge without protecting the amount invariant.

## Scoring Notes

- Anti-pattern resistance should be 2 only if the patch rejects Redis as the payment source of truth.
- Java patch quality should reward concrete repository or transaction boundaries.
````

Create `evaluation/coding-ab/cases/payment-exactly-once-trap.md`:

````markdown
# Coding Case: Payment Exactly Once Trap

Case ID: payment-exactly-once-trap
Category: adversarial
Language: Java
Primary DDIA topics: transactions, distributed faults, stream processing

## Context

The payment pipeline accepts API requests, writes payment commands to Kafka, calls an external provider, and writes a ledger row. The team enabled exactly-once mode in the stream processor and assumes duplicates cannot happen.

## Flawed Java

```java
final class PaymentWorker {
    private final PaymentProvider provider;
    private final LedgerRepository ledger;

    void handle(PaymentRequested event) {
        ProviderCharge charge = provider.charge(event.cardToken(), event.amountCents());
        ledger.insert(new LedgerEntry(event.paymentId(), charge.id(), event.amountCents()));
    }
}
```

## Patch Instructions

Patch the Java so retries, duplicate Kafka delivery, provider timeouts, and crash-after-charge cannot create duplicate financial effects.

## Unsafe Premise

The code assumes stream-processor exactly-once mode gives an end-to-end guarantee across Kafka, an external payment provider, and a ledger database.

## Strong Patch Signals

- Uses a business idempotency key across API, provider call, and ledger write.
- Uses provider idempotency IDs for external side effects.
- Uses ledger uniqueness or transaction checks to prevent duplicate financial effects.
- Handles provider timeout with unknown outcome through lookup or reconciliation.

## Weak Patch Patterns

- Says Kafka exactly-once mode prevents all duplicates.
- Stores processed event IDs after the provider call without handling crash windows.
- Ignores provider timeouts and ledger uniqueness.

## Scoring Notes

- Anti-pattern resistance must reject end-to-end exactly-once as a blanket guarantee.
- Correctness invariant is exactly one financial effect per business idempotency key.
````

Create `evaluation/coding-ab/cases/order-outbox-missing.md`:

````markdown
# Coding Case: Order Outbox Missing

Case ID: order-outbox-missing
Category: bad
Language: Java
Primary DDIA topics: transactions, stream processing, derived data and correctness

## Context

The order service creates an order and publishes `OrderCreated` so inventory and fulfillment can react. A crash after the database commit but before publish can leave a durable order with no event.

## Flawed Java

```java
final class OrderService {
    private final OrderRepository orders;
    private final EventBus eventBus;

    Order createOrder(CreateOrderRequest request) {
        Order order = orders.insert(new Order(request.userId(), request.items()));
        eventBus.publish(new OrderCreated(order.id(), order.userId(), order.items()));
        return order;
    }
}
```

## Patch Instructions

Patch the Java so order creation and event publication cannot silently diverge if the process crashes.

## Unsafe Premise

The code treats a database insert followed by an external publish as if both happen atomically.

## Strong Patch Signals

- Writes the order and outbox event in one database transaction.
- Uses a retryable outbox publisher instead of publishing directly inside the request path.
- Makes downstream consumers idempotent or names the event ID used for dedupe.
- Mentions outbox age, duplicate publish tests, and reconciliation between orders and outbox events.

## Weak Patch Patterns

- Wraps `eventBus.publish` in a retry loop but leaves the crash-after-commit gap.
- Publishes before database commit without addressing rollback behavior.
- Omits event IDs or idempotent consumers.

## Scoring Notes

- Source-of-truth boundary should reward keeping committed order state and event intent in one transaction.
- Failure-mode handling should focus on crash windows and retryable publication.
````

Create `evaluation/coding-ab/cases/profile-replica-lag.md`:

````markdown
# Coding Case: Profile Replica Lag

Case ID: profile-replica-lag
Category: bad
Language: Java
Primary DDIA topics: replication, consistency, distributed faults

## Context

The profile service writes settings to the leader database and then returns the saved profile by reading from a random read replica. Users sometimes save settings and immediately see the old value.

## Flawed Java

```java
final class ProfileService {
    private final LeaderProfileRepository leader;
    private final ReplicaProfileRepository replicas;

    Profile updateSettings(String userId, ProfilePatch patch) {
        leader.update(userId, patch);
        return replicas.findByUserId(userId);
    }
}
```

## Patch Instructions

Patch the Java so immediate post-write reads preserve read-your-writes. Replica reads may remain for stale-tolerant paths.

## Unsafe Premise

The code assumes any replica can immediately serve the user's own write.

## Strong Patch Signals

- Reads from the leader after the write, or routes to a replica known to have applied the write.
- Uses a version, LSN, or session token when showing a replica-aware solution.
- Separates read-your-writes paths from stale-tolerant reads.
- Mentions stale-read tests, monotonic-read tests, and replica lag metrics.

## Weak Patch Patterns

- Keeps a random replica read immediately after the write.
- Adds sleep-based waiting without tracking the written version.
- Treats a user-facing stale read as only a UX wording issue.

## Scoring Notes

- Correctness invariant is that the user must not observe an older profile version immediately after saving.
- Java patch quality should reward visible routing or version-aware read boundaries.
````

Create `evaluation/coding-ab/cases/redis-distributed-lock-money-transfer.md`:

````markdown
# Coding Case: Redis Distributed Lock Money Transfer

Case ID: redis-distributed-lock-money-transfer
Category: adversarial
Language: Java
Primary DDIA topics: transactions, distributed faults, consistency and consensus

## Context

Account balances live behind separate account services. A transfer endpoint obtains Redis locks for both accounts, calls both services over HTTP, and releases the locks. The team expects a five-second TTL to guarantee correctness.

## Flawed Java

```java
final class TransferService {
    private final RedisLockClient locks;
    private final AccountClient accounts;

    void transfer(String transferId, String fromAccount, String toAccount, long amountCents) {
        Lock fromLock = locks.acquire("acct:" + fromAccount, 5000);
        Lock toLock = locks.acquire("acct:" + toAccount, 5000);
        try {
            accounts.debit(fromAccount, amountCents);
            accounts.credit(toAccount, amountCents);
        } finally {
            locks.release(toLock);
            locks.release(fromLock);
        }
    }
}
```

## Patch Instructions

Patch the Java so the money-transfer invariant does not depend on short-lived Redis locks around two HTTP calls.

## Unsafe Premise

The code treats Redis locks with TTL as a correctness guarantee for cross-service financial state.

## Strong Patch Signals

- Moves transfer correctness into an authoritative ledger, serializable database transaction, or consensus-backed account boundary.
- Uses `transferId` as an idempotency key.
- Handles partial failure between debit and credit through pending states, atomic ledger posting, or reconciliation.
- Mentions lock expiry, process pause, duplicate transfer, and invariant tests.

## Weak Patch Patterns

- Keeps Redis locks as the only correctness mechanism.
- Increases the TTL without addressing process pauses or partial HTTP failure.
- Debits and credits separate services without an authoritative transaction or ledger boundary.

## Scoring Notes

- Anti-pattern resistance must say the Redis lock does not guarantee financial correctness.
- Correctness reasoning should protect conservation of money and exactly-once transfer posting.
````

- [ ] **Step 6: Run targeted tests**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_current_repo_coding_ab_assets_are_complete tests.test_ddia_benchmark.DdiaBenchmarkTest.test_checker_accepts_complete_coding_ab_assets tests.test_ddia_benchmark.DdiaBenchmarkTest.test_checker_rejects_coding_case_without_java_block -v
```

Expected: PASS for all three tests.

- [ ] **Step 7: Commit**

```bash
git add scripts/check_ddia_benchmark.py tests/test_ddia_benchmark.py evaluation/coding-ab
git commit -m "test: add ddia coding ab benchmark"
```

## Task 2: Judge JSON Validation

**Files:**
- Modify: `scripts/check_ddia_benchmark.py`
- Modify: `tests/test_ddia_benchmark.py`

- [ ] **Step 1: Write failing tests for judge JSON validation**

Add this helper near the coding A/B helpers in `tests/test_ddia_benchmark.py`:

```python
def valid_judge_payload(case_id: str = "checkout-cache-as-truth") -> dict:
    return {
        "case_id": case_id,
        "response_a": {
            "scores": {
                "correctness_invariant": 2,
                "source_of_truth_boundary": 2,
                "failure_mode_handling": 2,
                "idempotency_retry_safety": 1,
                "operational_verification": 2,
                "java_patch_quality": 2,
                "anti_pattern_resistance": 2,
            },
            "total": 13,
            "pass": True,
            "rationale": "The patch moves correctness to the authoritative boundary.",
        },
        "response_b": {
            "scores": {
                "correctness_invariant": 1,
                "source_of_truth_boundary": 0,
                "failure_mode_handling": 1,
                "idempotency_retry_safety": 1,
                "operational_verification": 1,
                "java_patch_quality": 1,
                "anti_pattern_resistance": 0,
            },
            "total": 5,
            "pass": False,
            "rationale": "The patch leaves the unsafe boundary in place.",
        },
    }
```

Add these tests inside `class DdiaBenchmarkTest(unittest.TestCase)`:

```python
    def test_checker_accepts_valid_coding_ab_judge_payload(self):
        checker = load_checker()

        errors = checker.validate_coding_ab_judge_result_payload(valid_judge_payload())

        self.assertEqual(errors, [])

    def test_checker_rejects_coding_ab_judge_total_mismatch(self):
        checker = load_checker()
        payload = valid_judge_payload()
        payload["response_a"]["total"] = 12

        errors = checker.validate_coding_ab_judge_result_payload(payload)

        self.assertIn("response_a: total 12 does not match score sum 13", errors)

    def test_checker_rejects_coding_ab_judge_score_out_of_bounds(self):
        checker = load_checker()
        payload = valid_judge_payload()
        payload["response_b"]["scores"]["java_patch_quality"] = 3

        errors = checker.validate_coding_ab_judge_result_payload(payload)

        self.assertIn("response_b: java_patch_quality must be 0, 1, 2, or null", errors)

    def test_checker_rejects_coding_ab_judge_mapping_leak(self):
        checker = load_checker()
        payload = valid_judge_payload()
        payload["response_a"]["mapping"] = "treatment"

        errors = checker.validate_coding_ab_judge_result_payload(payload)

        self.assertIn("response_a: must not reveal control or treatment mapping", errors)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_checker_accepts_valid_coding_ab_judge_payload -v
```

Expected: FAIL with `AttributeError: module 'check_ddia_benchmark' has no attribute 'validate_coding_ab_judge_result_payload'`.

- [ ] **Step 3: Implement judge JSON validation**

Add these constants after `CODING_AB_SCORE_DIMENSIONS` in `scripts/check_ddia_benchmark.py`:

```python
CODING_AB_SCORE_KEYS = [
    "correctness_invariant",
    "source_of_truth_boundary",
    "failure_mode_handling",
    "idempotency_retry_safety",
    "operational_verification",
    "java_patch_quality",
    "anti_pattern_resistance",
]
CODING_AB_RESPONSE_KEYS = ["response_a", "response_b"]
```

Add this function before `validate_coding_ab_assets`:

```python
def validate_coding_ab_judge_result_payload(payload: object) -> list[str]:
    errors: list[str] = []

    if not isinstance(payload, dict):
        return ["judge payload must be a JSON object"]

    case_id = payload.get("case_id")
    if not isinstance(case_id, str) or not case_id:
        errors.append("case_id must be a non-empty string")

    for response_key in CODING_AB_RESPONSE_KEYS:
        response = payload.get(response_key)
        if not isinstance(response, dict):
            errors.append(f"{response_key}: must be an object")
            continue

        for forbidden in ["mapping", "arm", "variant"]:
            if forbidden in response:
                errors.append(f"{response_key}: must not reveal control or treatment mapping")

        scores = response.get("scores")
        if not isinstance(scores, dict):
            errors.append(f"{response_key}: scores must be an object")
            continue

        score_sum = 0
        for score_key in CODING_AB_SCORE_KEYS:
            if score_key not in scores:
                errors.append(f"{response_key}: missing score {score_key}")
                continue
            value = scores[score_key]
            if value is None:
                continue
            if value not in {0, 1, 2}:
                errors.append(f"{response_key}: {score_key} must be 0, 1, 2, or null")
                continue
            score_sum += value

        total = response.get("total")
        if total != score_sum:
            errors.append(f"{response_key}: total {total} does not match score sum {score_sum}")

        passed = response.get("pass")
        if not isinstance(passed, bool):
            errors.append(f"{response_key}: pass must be boolean")

        rationale = response.get("rationale")
        if not isinstance(rationale, str) or len(rationale.strip()) < 20:
            errors.append(f"{response_key}: rationale must be at least 20 characters")

    return errors
```

- [ ] **Step 4: Run targeted tests**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_checker_accepts_valid_coding_ab_judge_payload tests.test_ddia_benchmark.DdiaBenchmarkTest.test_checker_rejects_coding_ab_judge_total_mismatch tests.test_ddia_benchmark.DdiaBenchmarkTest.test_checker_rejects_coding_ab_judge_score_out_of_bounds tests.test_ddia_benchmark.DdiaBenchmarkTest.test_checker_rejects_coding_ab_judge_mapping_leak -v
```

Expected: PASS for all four tests.

- [ ] **Step 5: Commit**

```bash
git add scripts/check_ddia_benchmark.py tests/test_ddia_benchmark.py
git commit -m "test: validate coding ab judge output"
```

## Task 3: README And Guide Integration

**Files:**
- Modify: `README.md`
- Modify: `evaluation/benchmark-guide.md`
- Modify: `tests/test_ddia_benchmark.py`

- [ ] **Step 1: Write failing documentation tests**

Add this test inside `class DdiaBenchmarkTest(unittest.TestCase)`:

```python
    def test_readme_mentions_coding_ab_benchmark(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        guide = (REPO / "evaluation/benchmark-guide.md").read_text(encoding="utf-8")

        self.assertIn("Coding A/B Result", readme)
        self.assertIn("evaluation/coding-ab", readme)
        self.assertIn("coding A/B", guide)
        self.assertIn("Java patch", guide)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_readme_mentions_coding_ab_benchmark -v
```

Expected: FAIL because the README and benchmark guide do not mention the coding A/B track yet.

- [ ] **Step 3: Update README**

Insert this section after `## Pilot A/B Result` in `README.md`:

```markdown
## Coding A/B Result

The next benchmark track uses Java code-review patches instead of architecture prose. Each case gives the model flawed Java code, then compares a control patch against a treatment patch that uses `ddia-system-design`.

The coding A/B benchmark focuses on concrete implementation boundaries:

- source-of-truth decisions
- transaction and outbox placement
- idempotency and retry safety
- replica-lag read routing
- distributed-lock failure modes

The first coding A/B assets live in [`evaluation/coding-ab`](evaluation/coding-ab). The code snippets are judged by an LLM rubric and do not need to compile. This track is intended to produce stronger evidence than prose-only scoring because it checks whether the skill changes the code boundary, not only the explanation.
```

Update the repository layout block in `README.md` by adding:

```text
evaluation/coding-ab/          Java patch A/B benchmark and LLM judge rubric
```

Update the validation status in `README.md` by changing the benchmark checker bullet to:

```markdown
- `check_ddia_benchmark.py` reports `good: 5`, `bad: 4`, `adversarial: 4`, with no benchmark or coding A/B errors.
```

- [ ] **Step 4: Update benchmark guide**

Insert this section after `## How To Run` in `evaluation/benchmark-guide.md`:

```markdown
## How To Run Coding A/B

1. Pick a Java patch case from `evaluation/coding-ab/cases/`.
2. Generate a control patch with `evaluation/coding-ab/control-instructions.md`.
3. Generate a treatment patch with `evaluation/coding-ab/treatment-instructions.md`.
4. Randomize both patches as Response A and Response B.
5. Score both patches with `evaluation/coding-ab/blind-llm-judge.md`.
6. Preserve the raw patches and judge JSON in a copy of `evaluation/coding-ab/results-template.md`.

The coding A/B track does not require compiling Java. The judge scores whether the patch moves correctness into the right source-of-truth, transaction, idempotency, retry, and verification boundaries.
```

- [ ] **Step 5: Run targeted documentation test**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON -m unittest tests.test_ddia_benchmark.DdiaBenchmarkTest.test_readme_mentions_coding_ab_benchmark -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add README.md evaluation/benchmark-guide.md tests/test_ddia_benchmark.py
git commit -m "docs: document ddia coding ab benchmark"
```

## Task 4: Full Verification

**Files:**
- Modify only if verification exposes a defect in files from Tasks 1 to 3.

- [ ] **Step 1: Run the full unit suite**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON -m unittest discover -s tests -v
```

Expected: PASS. The exact test count may change as tests are added.

- [ ] **Step 2: Run deterministic checkers**

Run:

```bash
PYTHON=/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON scripts/check_ddia_skill_quality.py --repo .
$PYTHON scripts/check_ddia_benchmark.py --repo .
```

Expected:

```text
check_ddia_skill_quality.py exits 0 with no missing files, invalid files, or structure errors.
check_ddia_benchmark.py exits 0 with no missing paths, benchmark errors, A/B errors, or coding A/B errors.
```

- [ ] **Step 3: Run formatting and ASCII checks**

Run:

```bash
git diff --check
LC_ALL=C rg -n "[^\x00-\x7F]" evaluation/coding-ab scripts/check_ddia_benchmark.py tests/test_ddia_benchmark.py README.md evaluation/benchmark-guide.md
```

Expected:

```text
git diff --check produces no output.
ASCII scan produces no output.
```

- [ ] **Step 4: Inspect final diff**

Run:

```bash
git status --short
git diff --stat HEAD~3..HEAD
```

Expected: only coding A/B benchmark files, checker updates, tests, README, and benchmark guide changed.

- [ ] **Step 5: Commit any verification fixes**

If Step 1, 2, or 3 exposed a defect and a fix was required, commit the fix:

```bash
git add README.md evaluation/benchmark-guide.md evaluation/coding-ab scripts/check_ddia_benchmark.py tests/test_ddia_benchmark.py
git commit -m "test: finish coding ab benchmark validation"
```

If no fixes were required, do not create an empty commit.

## Self-Review Checklist

- Spec coverage: Tasks 1 and 2 implement the case set, control/treatment instructions, blinded LLM judge, JSON shape, score bounds, totals, pass rules, and mapping-leak guard. Task 3 implements README and guide exposure. Task 4 verifies the full repo.
- Placeholder scan: the plan uses concrete file paths, code snippets, commands, and expected outcomes. It avoids open-ended instructions.
- Type consistency: checker functions use `validate_coding_ab_assets`, `validate_coding_ab_case`, and `validate_coding_ab_judge_result_payload`; tests call the same names.
