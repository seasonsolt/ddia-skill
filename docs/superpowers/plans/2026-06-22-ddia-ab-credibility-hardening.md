# DDIA A/B Credibility Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the current `ddia-system-design` A/B evaluation more credible by reducing control-arm bias, documenting threats to validity, adding normalized scores, and validating A/B result arithmetic.

**Architecture:** Keep the current Markdown-first evaluation structure. Extend `check_ddia_benchmark.py` with small parsing helpers for A/B pilot score rows and limitation terms, update A/B docs to be more honest about evidence strength, and update README wording to report a single paired pilot observation rather than implying broad causal proof.

**Tech Stack:** Markdown evaluation assets, Python standard library, `unittest`, existing Git workflow.

---

## Scope Check

This plan implements one focused subsystem: A/B credibility hardening. It does not add new benchmark cases, run a new repeated A/B study, change the installed skill behavior, add automated LLM judging, or refactor private PDF/reading tools.

## File Structure

- Modify: `/Users/Thin/Documents/ddia/evaluation/ab/control-instructions.md`
  - Make the control arm fairer by forbidding skill use while allowing normal structured architecture reasoning.
- Modify: `/Users/Thin/Documents/ddia/evaluation/ab/blind-scoring-guide.md`
  - Tell evaluators to score content, not heading presence.
- Modify: `/Users/Thin/Documents/ddia/evaluation/ab/results-template.md`
  - Add normalized scoring and explicit limitation fields for future runs.
- Modify: `/Users/Thin/Documents/ddia/evaluation/ab/README.md`
  - Explain the fairer control setup, threats to validity, and stronger repeated-run protocol.
- Modify: `/Users/Thin/Documents/ddia/evaluation/ab/pilot-results.md`
  - Add normalized scoring, detailed limitations, process-compliance non-coverage, and more cautious overall decision wording.
- Modify: `/Users/Thin/Documents/ddia/scripts/check_ddia_benchmark.py`
  - Add deterministic A/B score arithmetic, normalized-field, and limitation validation.
- Modify: `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`
  - Add tests for valid hardening assets, arithmetic drift, missing normalized fields, and missing limitations.
- Modify: `/Users/Thin/Documents/ddia/README.md`
  - Reword the A/B section to report one paired pilot observation.

---

### Task 1: Add A/B Credibility Validation Tests

**Files:**
- Modify: `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`

- [ ] **Step 1: Update the A/B fixture to the hardened format**

In `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`, update `make_complete_ab_assets()` so the A/B fixture matches the hardened target state.

Replace the `control-instructions.md` fixture text with:

```python
        """# Control Instructions

Answer the benchmark case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill.

Use your general backend architecture knowledge. Use whatever clear answer structure you normally would for a backend architecture review.
""",
```

Replace the `blind-scoring-guide.md` fixture text with:

```python
        """# Blind Scoring Guide

## Scoring Order

Score Response A and Response B before revealing which response is control or treatment.

Score the substance of the answer, not the mere presence of headings. A response should earn points when it actually explains workload, trade-offs, failure modes, correctness, and verification.

## Mapping Reveal

Reveal the mapping only after all dimensions, notes, and pass decisions are recorded.
""",
```

Replace the `results-template.md` fixture text with:

```python
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

| Case | Category | Control score | Treatment score | Lift | Control normalized | Treatment normalized | Normalized lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Dimension Differences

Record workload framing, trade-off quality, failure-mode coverage, correctness reasoning, verification value, and anti-pattern resistance differences.

## Response Archive

Preserve Response A and Response B for every case.

## Limitations

- Self-evaluation bias:
- Response-shape/rubric alignment:
- Single model:
- Single run:
- No variance estimate:
- Non-random case selection:
- Process-compliance rubric not scored:

## Overall Decision

- Total control score:
- Total treatment score:
- Total lift:
- Mean normalized control:
- Mean normalized treatment:
- Mean normalized lift:
""",
```

Replace the `pilot-results.md` fixture text with:

```python
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

| Case | Category | Control score | Treatment score | Lift | Control normalized | Treatment normalized | Normalized lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| order-consistency | good | 7/10 | 9/10 | +2 | 70.0% | 90.0% | +20.0 pp | fail to pass | Treatment added stronger verification and failure-mode reasoning. |
| replica-lag | good | 7/10 | 10/10 | +3 | 70.0% | 100.0% | +30.0 pp | fail to pass | Treatment named read-your-writes and monotonic reads. |
| cache-as-truth | bad | 8/12 | 11/12 | +3 | 66.7% | 91.7% | +25.0 pp | fail to pass | Treatment rejected Redis as source of truth. |
| exactly-once-trap | adversarial | 8/12 | 11/12 | +3 | 66.7% | 91.7% | +25.0 pp | fail to pass | Treatment challenged end-to-end exactly-once. |
| vague-startup-architecture | bad | 8/12 | 10/12 | +2 | 66.7% | 83.3% | +16.7 pp | diagnostic improvement | Treatment scoped the recommendation and named missing requirements. |

## Dimension Differences

Treatment improved correctness reasoning, verification value, and anti-pattern resistance across the pilot cases.

## Response Archive

Responses are preserved under each case section in this file.

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
""",
```

- [ ] **Step 2: Add tests for new validation rules**

Add these methods to `class DdiaBenchmarkTest(unittest.TestCase)` after the existing A/B tests:

```python
    def test_checker_rejects_pilot_score_total_drift(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace(
                    "- Total treatment score: 51",
                    "- Total treatment score: 50",
                ),
                encoding="utf-8",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: total treatment score 50 does not equal case sum 51",
            ab_errors,
        )

    def test_checker_rejects_pilot_missing_normalized_scores(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace("Control normalized", "Control percent"),
                encoding="utf-8",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: missing score column Control normalized",
            ab_errors,
        )

    def test_checker_rejects_pilot_missing_required_limitation(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace(
                    "- No variance estimate: the pilot does not report repeated-run mean, minimum, maximum, or range.\n",
                    "",
                ),
                encoding="utf-8",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/pilot-results.md: missing limitation No variance estimate",
            ab_errors,
        )

    def test_checker_rejects_control_instructions_that_ban_structured_answers(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            write(
                repo / "evaluation/ab/control-instructions.md",
                """# Control Instructions

Answer the benchmark case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill.

Do not use the DDIA skill workflow, DDIA reference files, or DDIA skill response shape.
""",
            )

            missing_paths, ab_errors = checker.validate_ab_assets(repo)

        self.assertEqual(missing_paths, [])
        self.assertIn(
            "evaluation/ab/control-instructions.md: must allow ordinary structured architecture reasoning",
            ab_errors,
        )
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_benchmark -v
```

Expected: FAIL. The new tests should fail because `validate_ab_assets()` does not yet validate normalized columns, arithmetic totals, detailed limitations, or structured-answer bans.

- [ ] **Step 4: Commit Task 1**

Do not commit Task 1 yet because it intentionally creates failing tests. Continue directly to Task 2.

---

### Task 2: Implement A/B Credibility Validation

**Files:**
- Modify: `/Users/Thin/Documents/ddia/scripts/check_ddia_benchmark.py`
- Modify: `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`

- [ ] **Step 1: Add constants for hardened validation**

In `/Users/Thin/Documents/ddia/scripts/check_ddia_benchmark.py`, update `AB_REQUIRED_PHRASES` and add these constants after it:

```python
AB_REQUIRED_PHRASES = {
    "evaluation/ab/README.md": [
        "control",
        "treatment",
        "pilot",
        "not statistical proof",
        "response-shape/rubric alignment",
        "repeated runs",
    ],
    "evaluation/ab/control-instructions.md": [
        "without using or referencing ddia-system-design",
        "Do not load, invoke, mention, or rely on the DDIA system design skill",
        "Use whatever clear answer structure you normally would",
    ],
    "evaluation/ab/treatment-instructions.md": [
        "Use ddia-system-design",
        "assumptions, recommendation, trade-offs, failure modes, correctness, operations, and tests",
    ],
    "evaluation/ab/blind-scoring-guide.md": [
        "Score Response A and Response B before revealing",
        "Reveal the mapping only after",
        "Score the substance of the answer",
    ],
    "evaluation/ab/results-template.md": [
        "Control score",
        "Treatment score",
        "Lift",
        "Control normalized",
        "Treatment normalized",
        "Normalized lift",
        "Pass/fail change",
        "Response Archive",
        "Limitations",
    ],
    "evaluation/ab/pilot-results.md": [
        "Total control score:",
        "Total treatment score:",
        "Total lift:",
        "Mean normalized control:",
        "Mean normalized treatment:",
        "Mean normalized lift:",
        "not statistical proof",
    ],
}

AB_SCORE_COLUMNS = [
    "Control score",
    "Treatment score",
    "Lift",
    "Control normalized",
    "Treatment normalized",
    "Normalized lift",
    "Pass/fail change",
    "Notes",
]
AB_LIMITATION_LABELS = [
    "Self-evaluation bias",
    "Response-shape/rubric alignment",
    "Single model",
    "Single run",
    "No variance estimate",
    "Non-random case selection",
    "Process-compliance rubric not scored",
]
AB_CONTROL_BANNED_PHRASES = [
    "do not use the ddia skill workflow",
    "do not use the ddia skill response shape",
    "do not use any similar structure",
]
AB_SCORE_ROW_PATTERN = re.compile(
    r"^\| (?P<case>[^|]+) \| (?P<category>[^|]+) \| "
    r"(?P<control>\d+)/(?P<control_den>\d+) \| "
    r"(?P<treatment>\d+)/(?P<treatment_den>\d+) \| "
    r"(?P<lift>[+-]\d+) \| "
    r"(?P<control_norm>\d+(?:\.\d+)?)% \| "
    r"(?P<treatment_norm>\d+(?:\.\d+)?)% \| "
    r"(?P<normalized_lift>[+-]\d+(?:\.\d+)?) pp \| "
)
```

- [ ] **Step 2: Add parsing helpers**

Add these helpers before `validate_ab_assets()`:

```python
def numeric_metadata_value(text: str, label: str) -> int | None:
    value = metadata_value(text, label)
    if value is None:
        return None
    match = re.search(r"[+-]?\d+", value)
    return int(match.group(0)) if match else None


def percentage_metadata_value(text: str, label: str) -> float | None:
    value = metadata_value(text, label)
    if value is None:
        return None
    match = re.search(r"[+-]?\d+(?:\.\d+)?", value)
    return float(match.group(0)) if match else None


def close_percent(actual: float, expected: float) -> bool:
    return abs(actual - expected) <= 0.15


def validate_ab_score_math(text: str, relative: str) -> list[str]:
    errors: list[str] = []
    control_total = 0
    treatment_total = 0
    normalized_control_values: list[float] = []
    normalized_treatment_values: list[float] = []

    for line in text.splitlines():
        match = AB_SCORE_ROW_PATTERN.match(line)
        if not match:
            continue
        case = match.group("case").strip()
        control = int(match.group("control"))
        control_den = int(match.group("control_den"))
        treatment = int(match.group("treatment"))
        treatment_den = int(match.group("treatment_den"))
        lift = int(match.group("lift"))
        control_norm = float(match.group("control_norm"))
        treatment_norm = float(match.group("treatment_norm"))
        normalized_lift = float(match.group("normalized_lift"))

        control_total += control
        treatment_total += treatment
        expected_control_norm = control / control_den * 100
        expected_treatment_norm = treatment / treatment_den * 100
        expected_normalized_lift = expected_treatment_norm - expected_control_norm
        normalized_control_values.append(expected_control_norm)
        normalized_treatment_values.append(expected_treatment_norm)

        if control_den == treatment_den and lift != treatment - control:
            errors.append(f"{relative}: {case} lift {lift:+d} does not equal treatment minus control {treatment - control:+d}")
        if not close_percent(control_norm, expected_control_norm):
            errors.append(f"{relative}: {case} control normalized {control_norm:.1f}% does not match {expected_control_norm:.1f}%")
        if not close_percent(treatment_norm, expected_treatment_norm):
            errors.append(f"{relative}: {case} treatment normalized {treatment_norm:.1f}% does not match {expected_treatment_norm:.1f}%")
        if not close_percent(normalized_lift, expected_normalized_lift):
            errors.append(f"{relative}: {case} normalized lift {normalized_lift:+.1f} pp does not match {expected_normalized_lift:+.1f} pp")

    if not normalized_control_values:
        errors.append(f"{relative}: no parseable case score rows")
        return errors

    total_control = numeric_metadata_value(text, "- Total control score")
    total_treatment = numeric_metadata_value(text, "- Total treatment score")
    total_lift = numeric_metadata_value(text, "- Total lift")
    if total_control != control_total:
        errors.append(f"{relative}: total control score {total_control} does not equal case sum {control_total}")
    if total_treatment != treatment_total:
        errors.append(f"{relative}: total treatment score {total_treatment} does not equal case sum {treatment_total}")
    if total_lift != treatment_total - control_total:
        errors.append(f"{relative}: total lift {total_lift} does not equal treatment minus control {treatment_total - control_total:+d}")

    mean_control = sum(normalized_control_values) / len(normalized_control_values)
    mean_treatment = sum(normalized_treatment_values) / len(normalized_treatment_values)
    mean_lift = mean_treatment - mean_control
    recorded_mean_control = percentage_metadata_value(text, "- Mean normalized control")
    recorded_mean_treatment = percentage_metadata_value(text, "- Mean normalized treatment")
    recorded_mean_lift = percentage_metadata_value(text, "- Mean normalized lift")
    if recorded_mean_control is None or not close_percent(recorded_mean_control, mean_control):
        errors.append(f"{relative}: mean normalized control does not match {mean_control:.1f}%")
    if recorded_mean_treatment is None or not close_percent(recorded_mean_treatment, mean_treatment):
        errors.append(f"{relative}: mean normalized treatment does not match {mean_treatment:.1f}%")
    if recorded_mean_lift is None or not close_percent(recorded_mean_lift, mean_lift):
        errors.append(f"{relative}: mean normalized lift does not match {mean_lift:+.1f} pp")

    return errors
```

- [ ] **Step 3: Wire the new validation into `validate_ab_assets()`**

Inside the pilot validation block in `validate_ab_assets()`, replace the existing score-column loop:

```python
        for score_label in ["Control score", "Treatment score", "Lift", "Pass/fail change", "Notes"]:
            if score_label not in pilot_text:
                errors.append(f"evaluation/ab/pilot-results.md: missing score column {score_label}")
```

with:

```python
        for score_label in AB_SCORE_COLUMNS:
            if score_label not in pilot_text:
                errors.append(f"evaluation/ab/pilot-results.md: missing score column {score_label}")
        for limitation in AB_LIMITATION_LABELS:
            if limitation not in pilot_text:
                errors.append(f"evaluation/ab/pilot-results.md: missing limitation {limitation}")
        errors.extend(validate_ab_score_math(pilot_text, "evaluation/ab/pilot-results.md"))
```

Update the control-instruction check to allow structured answers and reject only real control-arm handcapping:

```python
    control_text = read_text(repo / "evaluation/ab/control-instructions.md")
    if control_text and (
        "without using or referencing ddia-system-design" not in control_text
        or "Do not load, invoke, mention, or rely on the DDIA system design skill" not in control_text
    ):
        errors.append("evaluation/ab/control-instructions.md: must forbid using ddia-system-design")
    if control_text and "Use whatever clear answer structure you normally would" not in control_text:
        errors.append("evaluation/ab/control-instructions.md: must allow ordinary structured architecture reasoning")
    if control_text and any(phrase in control_text.lower() for phrase in AB_CONTROL_BANNED_PHRASES):
        errors.append("evaluation/ab/control-instructions.md: must allow ordinary structured architecture reasoning")
```

- [ ] **Step 4: Run tests to verify Task 1 failures now pass against fixtures**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_benchmark -v
```

Expected: the fixture-focused tests pass, but `test_current_repo_benchmark_is_complete` may fail until real A/B docs are updated in Task 3. If it fails only because the current repo lacks hardened A/B docs, continue to Task 3 before committing.

---

### Task 3: Harden A/B Documentation And Pilot Result

**Files:**
- Modify: `/Users/Thin/Documents/ddia/evaluation/ab/control-instructions.md`
- Modify: `/Users/Thin/Documents/ddia/evaluation/ab/blind-scoring-guide.md`
- Modify: `/Users/Thin/Documents/ddia/evaluation/ab/results-template.md`
- Modify: `/Users/Thin/Documents/ddia/evaluation/ab/README.md`
- Modify: `/Users/Thin/Documents/ddia/evaluation/ab/pilot-results.md`
- Modify: `/Users/Thin/Documents/ddia/README.md`

- [ ] **Step 1: Update control instructions**

Replace `/Users/Thin/Documents/ddia/evaluation/ab/control-instructions.md` with:

```markdown
# Control Instructions

Answer the benchmark case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill.

Use your general backend architecture knowledge. Use whatever clear answer structure you normally would for a backend architecture review.

Do not intentionally avoid structured reasoning. The control arm is a no-skill baseline, not an unstructured-answer baseline.
```

- [ ] **Step 2: Update blind scoring guide**

Replace `/Users/Thin/Documents/ddia/evaluation/ab/blind-scoring-guide.md` with:

```markdown
# Blind Scoring Guide

## Scoring Order

Score Response A and Response B before revealing which response is control or treatment.

Use `evaluation/rubrics/answer-quality.md` for every response. For good cases, score five dimensions for a maximum of 10. For bad and adversarial cases, also score Anti-pattern resistance for a maximum of 12.

Score the substance of the answer, not the mere presence of headings. A response should earn points when it actually explains workload, trade-offs, failure modes, correctness, and verification.

## Mapping Reveal

Reveal the mapping only after all dimensions, notes, totals, and pass/fail decisions are recorded.

After revealing the mapping, compute treatment lift:

```text
treatment score - control score
```

Also record normalized score lift in percentage points so 10-point and 12-point cases can be compared:

```text
(treatment score / treatment max * 100) - (control score / control max * 100)
```

Record whether the treatment changed the pass/fail decision and which dimensions improved or regressed.
```

- [ ] **Step 3: Update results template**

Replace `/Users/Thin/Documents/ddia/evaluation/ab/results-template.md` with:

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

| Case | Category | Control score | Treatment score | Lift | Control normalized | Treatment normalized | Normalized lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Add one row per case. | Use good, bad, or adversarial. | Score after reveal. | Score after reveal. | Treatment minus control. | Control percentage. | Treatment percentage. | Treatment percentage minus control percentage. | State no change, fail to pass, pass to fail, or diagnostic change. | Record scoring rationale. |

## Dimension Differences

Record workload framing, trade-off quality, failure-mode coverage, correctness reasoning, verification value, and anti-pattern resistance differences.

## Response Archive

For each case, preserve Response A and Response B exactly as evaluated.

## Limitations

- Self-evaluation bias: state whether the generator and evaluator are independent.
- Response-shape/rubric alignment: state whether one arm was prompted into a structure that matches the rubric.
- Single model: state which model was used and whether other models were excluded.
- Single run: state how many runs were generated per arm.
- No variance estimate: state whether mean, minimum, maximum, and range were measured.
- Non-random case selection: state how cases were selected.
- Process-compliance rubric not scored: state whether process compliance was scored separately.

## Overall Decision

- Total control score: write the total.
- Total treatment score: write the total.
- Total lift: write treatment minus control.
- Mean normalized control: write the mean control percentage.
- Mean normalized treatment: write the mean treatment percentage.
- Mean normalized lift: write treatment percentage minus control percentage.
- Limitations: summarize the evidence strength.
```

- [ ] **Step 4: Update A/B README**

In `/Users/Thin/Documents/ddia/evaluation/ab/README.md`, keep the existing sections and add these paragraphs to the relevant sections.

Under `## Method`, after the current numbered list, add:

```markdown
The control arm is a no-skill baseline. It forbids loading or relying on `ddia-system-design`, but it does not forbid normal structured architecture reasoning.

The treatment arm uses `ddia-system-design` and may follow its response shape. This creates a known response-shape/rubric alignment risk, so evaluators should score answer substance rather than heading presence.
```

Under `## Limitations`, replace the current paragraph with:

```markdown
This is pilot A/B evidence, not statistical proof. The current pilot has self-evaluation bias, response-shape/rubric alignment risk, a single model, a single run per arm, no variance estimate, and non-random case selection. It also scores answer quality only; it does not score the process-compliance rubric.

A stronger study would use independent blinded scoring, repeated randomized runs, and more than one model.
```

Add this new section after `## Limitations`:

```markdown
## Repeated-Run Protocol

1. Select cases before generating responses.
2. Run at least three control responses and three treatment responses per case.
3. Randomize whether control or treatment is labeled Response A for each pair.
4. Score all responses before revealing mapping.
5. Report mean, minimum, maximum, and range for each arm.
6. Report pass-threshold crossings separately from average score lift.
7. Preserve all response texts so another evaluator can rescore.
```

- [ ] **Step 5: Update pilot results with normalized scores and detailed limitations**

In `/Users/Thin/Documents/ddia/evaluation/ab/pilot-results.md`, replace the `## Case Scores` table with:

```markdown
## Case Scores

| Case | Category | Control score | Treatment score | Lift | Control normalized | Treatment normalized | Normalized lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| order-consistency | good | 7/10 | 9/10 | +2 | 70.0% | 90.0% | +20.0 pp | fail to pass | Treatment added clearer source-of-truth boundaries, idempotency, reconciliation, and falsifiable checks. |
| replica-lag | good | 7/10 | 10/10 | +3 | 70.0% | 100.0% | +30.0 pp | fail to pass | Treatment named read-your-writes and monotonic reads, then tied mitigations to session routing and lag metrics. |
| cache-as-truth | bad | 8/12 | 11/12 | +3 | 66.7% | 91.7% | +25.0 pp | fail to pass | Treatment rejected Redis as authoritative for payment decisions and kept financial invariants in transactional storage. |
| exactly-once-trap | adversarial | 8/12 | 11/12 | +3 | 66.7% | 91.7% | +25.0 pp | fail to pass | Treatment challenged end-to-end exactly-once and added idempotency boundaries for external side effects and ledger writes. |
| vague-startup-architecture | bad | 8/12 | 10/12 | +2 | 66.7% | 83.3% | +16.7 pp | diagnostic improvement | Treatment gave a scoped default, listed missing requirements, and avoided overconfident database selection. |
```

Add this section immediately before `## Overall Decision`:

```markdown
## Limitations

- Self-evaluation bias: the same agent family generated and scored the pilot, so scores may favor the skill-enabled response style.
- Response-shape/rubric alignment: treatment instructions ask for sections that map closely to the answer-quality rubric.
- Single model: the pilot only covers GPT-5 Codex.
- Single run: each case has one control response and one treatment response.
- No variance estimate: the pilot does not report repeated-run mean, minimum, maximum, or range.
- Non-random case selection: the five cases were selected for coverage, not sampled randomly.
- Process-compliance rubric not scored: this pilot scores answer quality only.
```

Replace the `## Overall Decision` bullet list with:

```markdown
## Overall Decision

- Total control score: 38
- Total treatment score: 51
- Total lift: +13
- Mean normalized control: 68.0%
- Mean normalized treatment: 91.3%
- Mean normalized lift: +23.3 pp
- Limitations: In one five-case paired pilot run, treatment scored higher than control and four must-pass cases crossed the pass threshold. This is directional pilot evidence, not statistical proof.
```

- [ ] **Step 6: Update README pilot wording**

In `/Users/Thin/Documents/ddia/README.md`, replace the current `Pilot result:` block and following paragraphs with:

```markdown
Pilot observation from one paired run:

- Control total: 38
- Treatment total: 51
- Raw lift: +13 points across 5 cases
- Mean normalized lift: +23.3 percentage points
- Pass-threshold observation: four must-pass cases crossed the pass threshold in this run

The strongest observed gains came from correctness reasoning, verification value, and anti-pattern resistance. The treatment responses challenged unsafe premises more directly, including Redis-as-payment-truth and end-to-end exactly-once claims.

This is directional pilot A/B evidence, not statistical proof. The run has self-evaluation bias, response-shape/rubric alignment risk, a single model, a single response per arm, no variance estimate, and non-random case selection. The response text, scoring notes, and mapping are preserved in [`evaluation/ab/pilot-results.md`](evaluation/ab/pilot-results.md) so another evaluator can rescore the run.
```

- [ ] **Step 7: Run tests and checker**

Run:

```bash
cd /Users/Thin/Documents/ddia
LC_ALL=C rg -n "[^\\x00-\\x7F]" README.md evaluation/ab
git diff --check
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_benchmark -v
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_benchmark.py --repo /Users/Thin/Documents/ddia
```

Expected:

- `rg` exits 1 with no output.
- `git diff --check` exits 0.
- `tests.test_ddia_benchmark` passes.
- benchmark checker exits 0 with `ab_errors: []`.

- [ ] **Step 8: Commit Tasks 1-3 together**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add scripts/check_ddia_benchmark.py tests/test_ddia_benchmark.py evaluation/ab/control-instructions.md evaluation/ab/blind-scoring-guide.md evaluation/ab/results-template.md evaluation/ab/README.md evaluation/ab/pilot-results.md README.md
git commit -m "test: harden ddia ab credibility checks"
```

---

### Task 4: Add Focused Integration Regression For Real A/B Errors

**Files:**
- Modify: `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`

- [ ] **Step 1: Add a `check_benchmark()` integration test for `ab_errors`**

Add this test to `class DdiaBenchmarkTest(unittest.TestCase)`:

```python
    def test_benchmark_checker_reports_ab_content_error(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            make_complete_ab_assets(repo)
            pilot_path = repo / "evaluation/ab/pilot-results.md"
            pilot_path.write_text(
                pilot_path.read_text(encoding="utf-8").replace(
                    "- Single model: the pilot only covers GPT-5 Codex.\n",
                    "",
                ),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/ab/pilot-results.md: missing limitation Single model",
            report["ab_errors"],
        )
```

- [ ] **Step 2: Run benchmark tests**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_benchmark -v
```

Expected: all benchmark tests pass.

- [ ] **Step 3: Commit Task 4**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add tests/test_ddia_benchmark.py
git commit -m "test: cover ab content errors in benchmark report"
```

---

### Task 5: Final Verification And Publish

**Files:**
- No source changes expected.

- [ ] **Step 1: Run full unit suite**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Run skill quality checker**

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

Expected output includes:

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

- [ ] **Step 4: Check README/A-B ASCII and diff hygiene**

Run:

```bash
cd /Users/Thin/Documents/ddia
LC_ALL=C rg -n "[^\\x00-\\x7F]" README.md evaluation/ab
git diff --check
```

Expected:

- `rg` exits 1 with no output.
- `git diff --check` exits 0.

- [ ] **Step 5: Check git state**

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

- [ ] **Step 6: Push branch**

Run:

```bash
cd /Users/Thin/Documents/ddia
git push origin codex/ddia-system-design-skill
```

Expected: push succeeds to `git@github.com:seasonsolt/ddia-skill.git`.

---

## Self-Review Checklist

- The plan implements every in-scope requirement in `/Users/Thin/Documents/ddia/docs/superpowers/specs/2026-06-22-ddia-ab-credibility-hardening-design.md`.
- The plan does not add new benchmark cases or run a new repeated A/B study.
- Control instructions become fairer without allowing the DDIA skill itself.
- Pilot results include normalized score columns and mean normalized totals.
- Pilot limitations include self-evaluation bias, response-shape/rubric alignment, single model, single run, no variance estimate, non-random case selection, and process-compliance rubric not scored.
- The checker validates arithmetic drift and required limitation terms.
- README wording reports a single paired pilot observation, not statistical proof.
- Every task has concrete commands and expected outcomes.

