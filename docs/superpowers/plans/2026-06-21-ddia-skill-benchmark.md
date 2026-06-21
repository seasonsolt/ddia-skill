# DDIA Skill Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a repeatable benchmark that proves and improves the `ddia-system-design` skill with good, bad, and adversarial architecture cases.

**Architecture:** Add a canonical benchmark structure under `evaluation/cases/`, `evaluation/rubrics/`, and `evaluation/results/` while leaving the existing first-pass `evaluation/prompts/` files intact as historical compatibility. Add a dedicated deterministic validator for benchmark structure; the validator checks completeness and consistency, not architecture quality.

**Tech Stack:** Markdown benchmark assets, Python standard library, `unittest`, existing Git workflow.

---

## Scope Check

This is one focused subsystem: a benchmark for the existing DDIA skill. It does not add automated LLM grading, CI, dashboards, or multi-model comparison. It creates structured test cases, rubrics, a benchmark guide, a results template, and deterministic validation.

## File Structure

- Create: `/Users/Thin/Documents/ddia/scripts/check_ddia_benchmark.py`
  - Validates benchmark directories, case files, rubrics, guide, and results template.
- Create: `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`
  - Unit tests for the benchmark validator.
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/01-order-consistency.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/02-event-pipeline.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/03-database-choice.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/04-replica-lag.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/good/05-derived-data.md`
  - Canonical good-case benchmark prompts derived from the existing five evaluation prompts.
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/bad/01-cache-as-truth.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/bad/02-replica-lag-denial.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/bad/03-hot-partition.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/bad/04-vague-startup-architecture.md`
  - Bad cases that reveal weak architecture reasoning.
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/adversarial/01-tool-first-trap.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/adversarial/02-exactly-once-trap.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/adversarial/03-distributed-lock-trap.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/cases/adversarial/04-schema-evolution-trap.md`
  - Adversarial cases that test resistance to misleading premises.
- Create: `/Users/Thin/Documents/ddia/evaluation/rubrics/answer-quality.md`
  - Answer-quality scoring for good, bad, and adversarial cases.
- Create: `/Users/Thin/Documents/ddia/evaluation/rubrics/process-compliance.md`
  - Observable skill-process scoring.
- Create: `/Users/Thin/Documents/ddia/evaluation/results/template.md`
  - Copyable benchmark result format.
- Create: `/Users/Thin/Documents/ddia/evaluation/benchmark-guide.md`
  - How to run, score, and compare benchmark runs.

Existing files under `/Users/Thin/Documents/ddia/evaluation/prompts/`, `/Users/Thin/Documents/ddia/evaluation/rubric.md`, `/Users/Thin/Documents/ddia/evaluation/results-template.md`, and `/Users/Thin/Documents/ddia/evaluation/results.md` remain as historical first-pass evaluation artifacts for this implementation.

---

### Task 1: Add Benchmark Validator Unit Tests And Script

**Files:**
- Create: `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`
- Create: `/Users/Thin/Documents/ddia/scripts/check_ddia_benchmark.py`

- [ ] **Step 1: Write the failing validator tests**

Create `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`:

```python
import importlib.util
import pathlib
import tempfile
import unittest


REPO = pathlib.Path(__file__).resolve().parents[1]


def load_checker():
    module_path = REPO / "scripts" / "check_ddia_benchmark.py"
    spec = importlib.util.spec_from_file_location("check_ddia_benchmark", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def case_text(
    *,
    title: str,
    category: str,
    pass_mode: str = "must-pass",
    scoring_profile: str = "good",
) -> str:
    return f"""# Case: {title}

Category: {category}
Pass mode: {pass_mode}
Scoring profile: {scoring_profile}

## Prompt

Use the DDIA system design skill to review a backend architecture scenario with enough detail to evaluate workload framing, trade-offs, failure modes, correctness, and verification.

## Bad Premise Or Trap

No deliberate trap; this case checks normal DDIA-style system design reasoning.

## Weak Answer Patterns

- Recommends a tool before describing workload and correctness requirements.
- Skips concrete failure modes and verification steps.

## Strong Answer Signals

- Frames reads, writes, data volume, latency, and growth assumptions.
- Names trade-offs, failure modes, correctness implications, and validation checks.

## Scoring Notes

- Score answer quality with the rubric in evaluation/rubrics/answer-quality.md.
- Score process compliance only when the process is observable.
"""


def make_complete_benchmark(root: pathlib.Path) -> None:
    for index in range(1, 6):
        write(
            root / f"evaluation/cases/good/{index:02d}-good-case.md",
            case_text(title=f"Good Case {index}", category="good", scoring_profile="good"),
        )
    for index in range(1, 5):
        write(
            root / f"evaluation/cases/bad/{index:02d}-bad-case.md",
            case_text(title=f"Bad Case {index}", category="bad", scoring_profile="anti-pattern"),
        )
        write(
            root / f"evaluation/cases/adversarial/{index:02d}-adversarial-case.md",
            case_text(
                title=f"Adversarial Case {index}",
                category="adversarial",
                scoring_profile="anti-pattern",
            ),
        )

    write(
        root / "evaluation/rubrics/answer-quality.md",
        """# Answer Quality Rubric

## Dimensions

1. Workload framing
2. Trade-off quality
3. Failure-mode coverage
4. Correctness reasoning
5. Verification value
6. Anti-pattern resistance

## Passing Standards

- Good cases pass at 8 out of 10 with no zero dimensions.
- Bad and adversarial cases pass at 10 out of 12 with anti-pattern resistance scored 2.
""",
    )
    write(
        root / "evaluation/rubrics/process-compliance.md",
        """# Process Compliance Rubric

## Dimensions

1. Skill material usage
2. Assumption framing
3. Missing requirement questions
4. Response structure
5. Verification conversion
""",
    )
    write(
        root / "evaluation/results/template.md",
        """# DDIA Skill Benchmark Results

## Run Metadata

- Evaluator:
- Date:
- Skill version:

## Answer Quality

## Process Compliance

## Regression Notes

## Overall Decision
""",
    )
    write(
        root / "evaluation/benchmark-guide.md",
        """# DDIA Skill Benchmark Guide

## Purpose

Use this benchmark to prove usefulness and drive iteration.

## How To Run

Run every case in evaluation/cases and score the response.

## How To Score

Use answer quality and process compliance separately.

## Regression Review

Compare the new results against the previous benchmark result.
""",
    )


class DdiaBenchmarkTest(unittest.TestCase):
    def test_checker_accepts_complete_benchmark(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)

            report = checker.check_benchmark(repo)

        self.assertEqual(report["case_counts"], {"good": 5, "bad": 4, "adversarial": 4})
        self.assertEqual(report["missing_paths"], [])
        self.assertEqual(report["case_errors"], [])
        self.assertEqual(report["rubric_errors"], [])
        self.assertEqual(report["template_errors"], [])
        self.assertEqual(report["guide_errors"], [])

    def test_checker_rejects_missing_required_case_section(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            case_path = repo / "evaluation/cases/bad/01-bad-case.md"
            case_path.write_text(
                case_path.read_text(encoding="utf-8").replace("## Strong Answer Signals", "## Strong Signals"),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/cases/bad/01-bad-case.md: missing section Strong Answer Signals",
            report["case_errors"],
        )

    def test_checker_rejects_wrong_case_category(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            case_path = repo / "evaluation/cases/adversarial/01-adversarial-case.md"
            case_path.write_text(
                case_path.read_text(encoding="utf-8").replace("Category: adversarial", "Category: good"),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/cases/adversarial/01-adversarial-case.md: expected Category: adversarial",
            report["case_errors"],
        )

    def test_checker_requires_anti_pattern_profile_for_bad_cases(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            case_path = repo / "evaluation/cases/bad/02-bad-case.md"
            case_path.write_text(
                case_path.read_text(encoding="utf-8").replace(
                    "Scoring profile: anti-pattern",
                    "Scoring profile: good",
                ),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/cases/bad/02-bad-case.md: expected Scoring profile: anti-pattern",
            report["case_errors"],
        )

    def test_checker_rejects_missing_answer_quality_dimension(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_benchmark(repo)
            rubric_path = repo / "evaluation/rubrics/answer-quality.md"
            rubric_path.write_text(
                rubric_path.read_text(encoding="utf-8").replace("6. Anti-pattern resistance\n", ""),
                encoding="utf-8",
            )

            report = checker.check_benchmark(repo)

        self.assertIn(
            "evaluation/rubrics/answer-quality.md: missing dimension Anti-pattern resistance",
            report["rubric_errors"],
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify they fail**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_benchmark -v
```

Expected: FAIL with `FileNotFoundError` or import failure for `scripts/check_ddia_benchmark.py`.

- [ ] **Step 3: Add the benchmark checker**

Create `/Users/Thin/Documents/ddia/scripts/check_ddia_benchmark.py`:

```python
#!/usr/bin/env python3
import argparse
import json
import pathlib


EXPECTED_CASE_COUNTS = {
    "good": 5,
    "bad": 4,
    "adversarial": 4,
}

CASE_DIRS = {
    "good": pathlib.Path("evaluation/cases/good"),
    "bad": pathlib.Path("evaluation/cases/bad"),
    "adversarial": pathlib.Path("evaluation/cases/adversarial"),
}

REQUIRED_CASE_SECTIONS = [
    "Prompt",
    "Bad Premise Or Trap",
    "Weak Answer Patterns",
    "Strong Answer Signals",
    "Scoring Notes",
]

ANSWER_QUALITY_DIMENSIONS = [
    "Workload framing",
    "Trade-off quality",
    "Failure-mode coverage",
    "Correctness reasoning",
    "Verification value",
    "Anti-pattern resistance",
]

PROCESS_COMPLIANCE_DIMENSIONS = [
    "Skill material usage",
    "Assumption framing",
    "Missing requirement questions",
    "Response structure",
    "Verification conversion",
]

REQUIRED_RESULT_TEMPLATE_SECTIONS = [
    "Run Metadata",
    "Answer Quality",
    "Process Compliance",
    "Regression Notes",
    "Overall Decision",
]

REQUIRED_GUIDE_SECTIONS = [
    "Purpose",
    "How To Run",
    "How To Score",
    "Regression Review",
]


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def section_body(text: str, heading: str) -> str:
    lines = text.splitlines()
    marker = f"## {heading}"
    for index, line in enumerate(lines):
        if line.strip() == marker:
            body = []
            for body_line in lines[index + 1 :]:
                if body_line.startswith("## "):
                    break
                body.append(body_line)
            return "\n".join(body).strip()
    return ""


def has_bullet(body: str) -> bool:
    return any(line.strip().startswith("- ") and len(line.strip()) > 2 for line in body.splitlines())


def check_case(path: pathlib.Path, repo: pathlib.Path, expected_category: str) -> list[str]:
    relative = path.relative_to(repo).as_posix()
    text = read_text(path)
    errors: list[str] = []

    if not text.strip():
        return [f"{relative}: file is empty"]

    first_line = text.splitlines()[0].strip()
    if not first_line.startswith("# Case: "):
        errors.append(f"{relative}: missing # Case heading")

    if f"Category: {expected_category}" not in text:
        errors.append(f"{relative}: expected Category: {expected_category}")

    if "Pass mode: must-pass" not in text and "Pass mode: diagnostic-only" not in text:
        errors.append(f"{relative}: expected Pass mode: must-pass or diagnostic-only")

    expected_profile = "good" if expected_category == "good" else "anti-pattern"
    if f"Scoring profile: {expected_profile}" not in text:
        errors.append(f"{relative}: expected Scoring profile: {expected_profile}")

    for section in REQUIRED_CASE_SECTIONS:
        body = section_body(text, section)
        if not body:
            errors.append(f"{relative}: missing section {section}")
            continue
        if section == "Prompt" and len(body) < 80:
            errors.append(f"{relative}: Prompt section is too short")
        if section in {"Weak Answer Patterns", "Strong Answer Signals", "Scoring Notes"} and not has_bullet(body):
            errors.append(f"{relative}: section {section} needs at least one bullet")

    return errors


def check_rubrics(repo: pathlib.Path) -> list[str]:
    errors: list[str] = []
    answer_path = repo / "evaluation/rubrics/answer-quality.md"
    process_path = repo / "evaluation/rubrics/process-compliance.md"
    answer_text = read_text(answer_path)
    process_text = read_text(process_path)

    if not answer_text.strip():
        errors.append("evaluation/rubrics/answer-quality.md: file is empty or missing")
    for dimension in ANSWER_QUALITY_DIMENSIONS:
        if dimension not in answer_text:
            errors.append(f"evaluation/rubrics/answer-quality.md: missing dimension {dimension}")
    for phrase in ["Good cases pass", "Bad and adversarial cases pass"]:
        if phrase not in answer_text:
            errors.append(f"evaluation/rubrics/answer-quality.md: missing passing standard phrase {phrase}")

    if not process_text.strip():
        errors.append("evaluation/rubrics/process-compliance.md: file is empty or missing")
    for dimension in PROCESS_COMPLIANCE_DIMENSIONS:
        if dimension not in process_text:
            errors.append(f"evaluation/rubrics/process-compliance.md: missing dimension {dimension}")

    return errors


def check_results_template(repo: pathlib.Path) -> list[str]:
    relative = "evaluation/results/template.md"
    text = read_text(repo / relative)
    errors: list[str] = []
    if not text.strip():
        return [f"{relative}: file is empty or missing"]
    for section in REQUIRED_RESULT_TEMPLATE_SECTIONS:
        if f"## {section}" not in text:
            errors.append(f"{relative}: missing section {section}")
    return errors


def check_guide(repo: pathlib.Path) -> list[str]:
    relative = "evaluation/benchmark-guide.md"
    text = read_text(repo / relative)
    errors: list[str] = []
    if not text.strip():
        return [f"{relative}: file is empty or missing"]
    for section in REQUIRED_GUIDE_SECTIONS:
        if f"## {section}" not in text:
            errors.append(f"{relative}: missing section {section}")
    return errors


def check_benchmark(repo: pathlib.Path) -> dict[str, object]:
    missing_paths: list[str] = []
    case_errors: list[str] = []
    case_counts: dict[str, int] = {}

    for category, directory in CASE_DIRS.items():
        absolute_dir = repo / directory
        if not absolute_dir.exists():
            missing_paths.append(directory.as_posix())
            case_counts[category] = 0
            continue

        case_files = sorted(absolute_dir.glob("*.md"))
        case_counts[category] = len(case_files)
        expected_count = EXPECTED_CASE_COUNTS[category]
        if len(case_files) != expected_count:
            case_errors.append(
                f"{directory.as_posix()}: expected {expected_count} case files, found {len(case_files)}"
            )
        for case_file in case_files:
            case_errors.extend(check_case(case_file, repo, category))

    for required_path in [
        "evaluation/rubrics/answer-quality.md",
        "evaluation/rubrics/process-compliance.md",
        "evaluation/results/template.md",
        "evaluation/benchmark-guide.md",
    ]:
        if not (repo / required_path).exists():
            missing_paths.append(required_path)

    return {
        "case_counts": case_counts,
        "missing_paths": missing_paths,
        "case_errors": case_errors,
        "rubric_errors": check_rubrics(repo),
        "template_errors": check_results_template(repo),
        "guide_errors": check_guide(repo),
    }


def has_errors(report: dict[str, object]) -> bool:
    return any(
        report[key]
        for key in [
            "missing_paths",
            "case_errors",
            "rubric_errors",
            "template_errors",
            "guide_errors",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DDIA benchmark structure.")
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path.cwd())
    args = parser.parse_args()

    report = check_benchmark(args.repo)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if has_errors(report) else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run validator tests and verify they pass**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_benchmark -v
```

Expected: PASS for 5 tests.

- [ ] **Step 5: Commit Task 1**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add scripts/check_ddia_benchmark.py tests/test_ddia_benchmark.py
git commit -m "test: add ddia benchmark validator"
```

---

### Task 2: Add Benchmark Rubrics, Guide, And Results Template

**Files:**
- Create: `/Users/Thin/Documents/ddia/evaluation/rubrics/answer-quality.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/rubrics/process-compliance.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/results/template.md`
- Create: `/Users/Thin/Documents/ddia/evaluation/benchmark-guide.md`

- [ ] **Step 1: Add the answer-quality rubric**

Create `/Users/Thin/Documents/ddia/evaluation/rubrics/answer-quality.md`:

```markdown
# Answer Quality Rubric

Score each response from 0 to 2 on each dimension.

## Dimensions

1. Workload framing
   - 0: Missing, materially wrong, or generic.
   - 1: Names some workload factors but misses important reads, writes, data volume, latency, growth, or skew.
   - 2: Frames the concrete workload shape and ties it to the recommendation.
2. Trade-off quality
   - 0: Recommends tools or patterns as automatically correct.
   - 1: Mentions trade-offs but leaves costs vague.
   - 2: Explains the cost of each major choice in latency, availability, correctness, complexity, or operations.
3. Failure-mode coverage
   - 0: Does not name relevant failure modes.
   - 1: Names generic failures without tying them to the design.
   - 2: Names concrete failures under concurrency, faults, lag, overload, replay, skew, or operations.
4. Correctness reasoning
   - 0: Ignores invariants, consistency, ordering, isolation, idempotency, or reconciliation where relevant.
   - 1: Mentions correctness concepts but does not connect them to user-visible behavior.
   - 2: Explains the required guarantees and how the design preserves or weakens them.
5. Verification value
   - 0: Gives no useful tests, metrics, experiments, or runbook checks.
   - 1: Gives partial verification guidance that is not directly falsifiable.
   - 2: Gives concrete tests, metrics, experiments, or operational checks that can disprove the recommendation.
6. Anti-pattern resistance
   - 0: Accepts a bad premise or optimizes around it without challenge.
   - 1: Partially challenges the premise but still leaves the unsafe design path open.
   - 2: Clearly identifies the bad premise and redirects to safer workload, correctness, or ownership reasoning.

## Passing Standards

- Good cases pass at 8 out of 10 with no dimension scored 0. Anti-pattern resistance is not scored for good cases.
- Bad and adversarial cases pass at 10 out of 12 with no dimension scored 0.
- Bad and adversarial cases require Anti-pattern resistance to be scored 2.
- The whole benchmark passes only when every must-pass case passes.
- Diagnostic-only cases do not block the whole benchmark, but their scores and failure notes must be recorded.
```

- [ ] **Step 2: Add the process-compliance rubric**

Create `/Users/Thin/Documents/ddia/evaluation/rubrics/process-compliance.md`:

```markdown
# Process Compliance Rubric

Score only observable behavior. If hidden tool or skill usage is not visible, score based on the response and available transcript evidence.

## Dimensions

1. Skill material usage
   - 0: No sign that the DDIA skill workflow or references shaped the answer.
   - 1: Uses some DDIA language but does not clearly follow the skill workflow.
   - 2: Clearly follows the skill workflow or explicitly uses relevant DDIA reference lenses.
2. Assumption framing
   - 0: Recommends a design before stating assumptions.
   - 1: States assumptions after the recommendation or only partially.
   - 2: Frames workload, correctness, and ownership assumptions before or alongside the recommendation.
3. Missing requirement questions
   - 0: Makes a strong recommendation despite missing critical workload or correctness data.
   - 1: Mentions missing data but still overcommits.
   - 2: Asks or lists the missing requirements and scopes the recommendation accordingly.
4. Response structure
   - 0: Response is unstructured or hard to audit.
   - 1: Some structure exists, but key DDIA sections are missing.
   - 2: Uses the DDIA response shape or an equivalent structure covering assumptions, recommendation, trade-offs, failure modes, correctness, operations, and tests.
5. Verification conversion
   - 0: Does not convert claims into validation.
   - 1: Gives generic validation suggestions.
   - 2: Converts design claims into concrete tests, metrics, experiments, or runbook checks.

## Use

Process compliance is scored separately from answer quality. A response can be useful but still reveal weak process discipline.
```

- [ ] **Step 3: Add the results template**

Create `/Users/Thin/Documents/ddia/evaluation/results/template.md`:

```markdown
# DDIA Skill Benchmark Results

Copy this file to `evaluation/results/YYYY-MM-DD-<commit>.md` for each benchmark run, then replace each instruction sentence with the recorded value for that run.

## Run Metadata

- Evaluator: write the evaluator name.
- Date: write the run date in YYYY-MM-DD format.
- Skill version: write the Git commit or skill version.
- Skill path: /Users/Thin/Documents/ddia/skills/ddia-system-design

## Answer Quality

| Case | Category | Pass mode | Workload | Trade-offs | Failure modes | Correctness | Verification | Anti-pattern | Total | Pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Add one row per benchmark case. | Use good, bad, or adversarial. | Use must-pass or diagnostic-only. | Score 0-2. | Score 0-2. | Score 0-2. | Score 0-2. | Score 0-2. | Score 0-2 or N/A. | Sum scored dimensions. | Use yes or no. |

## Process Compliance

| Case | Skill material usage | Assumption framing | Missing requirement questions | Response structure | Verification conversion | Total |
| --- | --- | --- | --- | --- | --- | --- |
| Add one row per benchmark case. | Score 0-2. | Score 0-2. | Score 0-2. | Score 0-2. | Score 0-2. | Sum scored dimensions. |

## Regression Notes

- Previous result compared: write the result file path.
- Regressed cases: write the case IDs and score changes.
- Improved cases: write the case IDs and score changes.
- New weaknesses found: write concrete weakness notes.
- Recommended skill changes: write concrete changes or `none`.

## Overall Decision

- All must-pass cases passed: write yes or no.
- Diagnostic-only failures recorded: write yes, no, or not applicable.
- Skill changes needed: write yes or no.
```

- [ ] **Step 4: Add the benchmark guide**

Create `/Users/Thin/Documents/ddia/evaluation/benchmark-guide.md`:

```markdown
# DDIA Skill Benchmark Guide

## Purpose

Use this benchmark to verify whether the `ddia-system-design` skill improves backend architecture reasoning. Good cases prove usefulness. Bad and adversarial cases expose weak behavior and become regression tests for future skill iterations.

## How To Run

1. Record the current skill version with `git rev-parse --short HEAD`.
2. Run every case in `evaluation/cases/good/`, `evaluation/cases/bad/`, and `evaluation/cases/adversarial/`.
3. Capture each model response.
4. Score answer quality with `evaluation/rubrics/answer-quality.md`.
5. Score process compliance with `evaluation/rubrics/process-compliance.md` when the process is observable.
6. Copy `evaluation/results/template.md` to `evaluation/results/YYYY-MM-DD-<commit>.md`.
7. Fill in every score, pass decision, regression note, and recommended skill change.
8. Compare the new result with the previous result file.

## How To Score

Good cases use five answer-quality dimensions for a maximum score of 10. A good case passes at 8 or higher with no zero dimensions.

Bad and adversarial cases use the same five dimensions plus Anti-pattern resistance for a maximum score of 12. A bad or adversarial case passes at 10 or higher only if Anti-pattern resistance is 2 and no dimension is 0.

Process compliance is scored separately. It should not rescue a weak final answer, but it helps diagnose whether the skill workflow itself needs improvement.

## Regression Review

For each new run, compare totals, per-dimension scores, and failure notes against the previous run. If an old must-pass case fails, treat it as a benchmark regression until the skill, prompt, or rubric is corrected.

When a new bad or adversarial case reveals a real weakness, keep that case in the benchmark permanently unless it is redundant with another case.
```

- [ ] **Step 5: Run the benchmark checker and verify it still fails only because case files are missing**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_benchmark.py --repo /Users/Thin/Documents/ddia
```

Expected: exit code 1. The JSON report should show empty `rubric_errors`, `template_errors`, and `guide_errors`, with missing case directories or wrong case counts.

- [ ] **Step 6: Commit Task 2**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add evaluation/rubrics/answer-quality.md evaluation/rubrics/process-compliance.md evaluation/results/template.md evaluation/benchmark-guide.md
git commit -m "docs: add ddia benchmark rubrics"
```

---

### Task 3: Add Canonical Good Cases

**Files:**
- Create five files under `/Users/Thin/Documents/ddia/evaluation/cases/good/`

- [ ] **Step 1: Add the order consistency good case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/good/01-order-consistency.md`:

```markdown
# Case: Order Consistency

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review this design:

We are building an order service. Users can place orders, cancel orders, and view order history. Inventory is stored in another service. The proposal uses a relational database for orders, Redis for order status caching, and asynchronous events to update inventory. Review the design for consistency risks, failure modes, and verification steps.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill treats Redis and asynchronous inventory events as derived paths rather than authoritative state.

## Weak Answer Patterns

- Treats Redis order status as authoritative without discussing cache invalidation or rebuilds.
- Ignores outbox, idempotency, retries, duplicate events, and reconciliation.
- Skips user-visible order and inventory invariants.

## Strong Answer Signals

- Names the order database as the source of truth for order state.
- Discusses transactional outbox, idempotent consumers, event ordering, retries, and reconciliation.
- Separates user-visible correctness from cache freshness.
- Proposes concrete failure injection, lag metrics, and consistency checks.

## Scoring Notes

- Score workload framing based on whether the answer asks for order volume, cancellation frequency, inventory coupling, latency goals, and acceptable stale reads.
- Score correctness reasoning based on whether the answer protects order state transitions and inventory reservation semantics.
```

- [ ] **Step 2: Add the event pipeline good case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/good/02-event-pipeline.md`:

```markdown
# Case: Event Pipeline

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to design a clickstream ingestion pipeline. The product needs near-real-time dashboards, replayable raw events, late event handling, and daily batch reports. Recommend an architecture and explain trade-offs, failure modes, and correctness checks.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill handles stream and batch requirements together instead of optimizing for dashboards alone.

## Weak Answer Patterns

- Builds only a real-time dashboard path and omits replayable raw storage.
- Ignores event time, late events, duplicates, backfills, and consumer lag.
- Treats exactly-once processing as a magic platform feature.

## Strong Answer Signals

- Separates durable raw event storage, stream processing, serving views, and daily batch outputs.
- Defines event time, watermarks, late event policy, replay strategy, idempotent sinks, and reconciliation.
- Explains latency versus correctness trade-offs for dashboards and reports.

## Scoring Notes

- Score workload framing based on event volume, burstiness, retention, dashboard latency, and report accuracy requirements.
- Score verification value based on replay tests, duplicate-event tests, late-event tests, consumer lag metrics, and report reconciliation.
```

- [ ] **Step 3: Add the database choice good case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/good/03-database-choice.md`:

```markdown
# Case: Database Choice

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to compare relational, document, and graph databases for a team collaboration product with users, organizations, projects, tasks, comments, mentions, permissions, and audit history. Give a recommendation and explain which assumptions would change it.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill chooses storage by data model, access pattern, and invariants rather than by popularity.

## Weak Answer Patterns

- Recommends one database category as universally best.
- Ignores permissions, audit history, many-to-many relationships, and schema evolution.
- Does not explain what assumptions would change the recommendation.

## Strong Answer Signals

- Compares relational joins and constraints, document locality, and graph traversal needs.
- Explains why relational storage is likely a strong source-of-truth default for permissions and auditability.
- Names conditions that would favor document or graph models.
- Gives concrete migration, query, and integrity tests.

## Scoring Notes

- Score trade-off quality based on whether the answer explains costs of joins, denormalization, traversal, schema changes, and operational complexity.
- Score correctness reasoning based on permission and audit-history invariants.
```

- [ ] **Step 4: Add the replica lag good case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/good/04-replica-lag.md`:

```markdown
# Case: Replica Lag

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to diagnose this production issue:

After moving read traffic to replicas, users sometimes update profile settings and then immediately see old values. Support also reports non-monotonic behavior when users refresh quickly. Explain likely causes, design options, trade-offs, and observability checks.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill connects replica lag to read-your-writes and monotonic-read behavior.

## Weak Answer Patterns

- Says replica lag is expected and stops there.
- Recommends reading from the leader for everything without discussing cost.
- Omits session routing, LSN or version tracking, failover behavior, and lag observability.

## Strong Answer Signals

- Names read-your-writes and monotonic-read violations.
- Discusses leader reads, session stickiness, version or LSN-aware routing, synchronous replication costs, and fallback behavior.
- Proposes replica lag metrics, stale-read tests, and user-session checks.

## Scoring Notes

- Score correctness reasoning based on whether the answer translates consistency terms into user-visible behavior.
- Score verification value based on reproducible stale-read tests and monitoring for replica apply lag.
```

- [ ] **Step 5: Add the derived data good case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/good/05-derived-data.md`:

```markdown
# Case: Derived Data

Category: good
Pass mode: must-pass
Scoring profile: good

## Prompt

Use the DDIA system design skill to review a search indexing design:

PostgreSQL is the source of truth. A background worker sends changes to Elasticsearch. Product wants search results to affect billing workflow decisions. Review the correctness risks and propose a safer architecture.

## Bad Premise Or Trap

No deliberate trap. This case checks whether the skill treats Elasticsearch as derived state and keeps billing decisions anchored in authoritative data.

## Weak Answer Patterns

- Lets Elasticsearch directly control billing decisions.
- Ignores index lag, missed updates, partial failures, rebuilds, and divergence.
- Does not define source-of-truth boundaries or reconciliation.

## Strong Answer Signals

- Keeps billing decisions in PostgreSQL or another authoritative transactional path.
- Treats Elasticsearch as derived search state with lag metrics, rebuilds, and divergence detection.
- Proposes reconciliation and clear unsafe states when search is stale.

## Scoring Notes

- Score correctness reasoning based on whether business-critical decisions avoid stale derived data.
- Score failure-mode coverage based on index lag, dropped updates, duplicate updates, rebuilds, and stale reads.
```

- [ ] **Step 6: Run the checker and verify good cases are counted**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_benchmark.py --repo /Users/Thin/Documents/ddia
```

Expected: exit code 1. The JSON report should include `"good": 5` in `case_counts` and should still report missing or under-counted bad and adversarial cases.

- [ ] **Step 7: Commit Task 3**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add evaluation/cases/good
git commit -m "test: add ddia benchmark good cases"
```

---

### Task 4: Add Bad And Adversarial Cases

**Files:**
- Create four files under `/Users/Thin/Documents/ddia/evaluation/cases/bad/`
- Create four files under `/Users/Thin/Documents/ddia/evaluation/cases/adversarial/`

- [ ] **Step 1: Add the cache-as-truth bad case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/bad/01-cache-as-truth.md`:

```markdown
# Case: Cache As Truth

Category: bad
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to review this proposal:

Our checkout service stores cart totals in PostgreSQL, but Redis is much faster. We want the payment workflow to read the final payable amount from Redis because the cache is updated on every cart change. PostgreSQL can be updated later by an asynchronous worker. Is this design acceptable if Redis has high availability?

## Bad Premise Or Trap

The prompt treats a cache as authoritative for a financial decision because it is fast and highly available.

## Weak Answer Patterns

- Accepts Redis as the source of truth for payment amount because it is fast.
- Equates high availability with correctness.
- Ignores cache loss, stale values, missed updates, race conditions, and reconciliation.

## Strong Answer Signals

- Rejects Redis as the authoritative source for payment decisions.
- Keeps payment amount and checkout invariants in a transactional source of truth.
- Allows Redis only as derived state with invalidation, rebuild, lag metrics, and reconciliation.
- Proposes tests for stale cache reads, lost cache updates, concurrent cart changes, and payment amount mismatches.

## Scoring Notes

- Anti-pattern resistance must be 2 for this case to pass.
- Score correctness reasoning based on whether payment invariants remain protected by authoritative storage.
```

- [ ] **Step 2: Add the replica-lag denial bad case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/bad/02-replica-lag-denial.md`:

```markdown
# Case: Replica Lag Denial

Category: bad
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to review this incident:

The product team says eventual consistency is fine for profile data. After moving all profile reads to replicas, users report that saving settings sometimes appears to fail because a refresh shows the old value. The team proposes adding a banner that says changes may take a few seconds. Is that enough?

## Bad Premise Or Trap

The prompt claims eventual consistency is acceptable while describing a read-your-writes product bug.

## Weak Answer Patterns

- Accepts the banner as sufficient without challenging the product behavior.
- Treats all profile reads as equally stale-tolerant.
- Ignores monotonic reads, session behavior, and replica lag observability.

## Strong Answer Signals

- Challenges the premise by separating stale-tolerant reads from read-your-writes paths.
- Discusses leader reads, session stickiness, version-aware routing, or LSN-aware reads after writes.
- Explains latency, availability, and operational costs of each option.
- Proposes metrics and tests for stale reads, monotonic reads, and replica apply lag.

## Scoring Notes

- Anti-pattern resistance must identify that a UX banner does not fix correctness for immediate post-write reads.
- Score verification value based on specific stale-read reproduction tests and lag monitoring.
```

- [ ] **Step 3: Add the hot-partition bad case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/bad/03-hot-partition.md`:

```markdown
# Case: Hot Partition

Category: bad
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to review this partitioning plan:

We store analytics events by `tenant_id` because every query filters by tenant. One enterprise tenant sends 55 percent of all writes during business hours, and product expects a few more very large tenants next quarter. The team says tenant-based partitioning is still best because it keeps tenant queries simple.

## Bad Premise Or Trap

The prompt optimizes for simple query routing while admitting severe write skew and future hot tenants.

## Weak Answer Patterns

- Accepts tenant-only partitioning because queries filter by tenant.
- Ignores hot partitions, write throttling, rebalancing, secondary indexes, and operational migration.
- Does not distinguish query locality from write distribution.

## Strong Answer Signals

- Identifies tenant-only partitioning as risky under skew.
- Discusses composite keys, hash subpartitioning, time buckets, tenant splitting, rate limiting, and rebalancing.
- Explains query fan-out trade-offs and operational complexity.
- Proposes load tests, per-partition metrics, hot-key alerts, and rebalance drills.

## Scoring Notes

- Anti-pattern resistance must challenge the partition key despite query convenience.
- Score workload framing based on write distribution, tenant growth, query patterns, and peak-to-average behavior.
```

- [ ] **Step 4: Add the vague-startup-architecture bad case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/bad/04-vague-startup-architecture.md`:

```markdown
# Case: Vague Startup Architecture

Category: bad
Pass mode: diagnostic-only
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to choose our database:

We are building a new B2B SaaS product. We might need users, teams, permissions, notifications, audit logs, analytics, and maybe AI features later. Should we use PostgreSQL, MongoDB, Cassandra, Neo4j, or DynamoDB? Please give one definitive choice so we can start quickly.

## Bad Premise Or Trap

The prompt asks for a definitive database choice while omitting workload, data model, correctness, query, and operational requirements.

## Weak Answer Patterns

- Gives a confident single database choice without scoping assumptions.
- Chooses based on trend, scale mythology, or future AI features.
- Ignores permissions, auditability, transactions, query shape, and operational maturity.

## Strong Answer Signals

- Refuses an overconfident recommendation and states missing requirements.
- Gives a scoped default such as PostgreSQL for early relational SaaS needs while explaining assumptions.
- Names the requirements that would change the choice.
- Proposes lightweight experiments and schema/query spikes before committing.

## Scoring Notes

- Diagnostic-only because early product prompts may be intentionally vague.
- Anti-pattern resistance should reward scoped recommendations, not refusal to help.
```

- [ ] **Step 5: Add the tool-first adversarial case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/adversarial/01-tool-first-trap.md`:

```markdown
# Case: Tool First Trap

Category: adversarial
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to validate this architecture:

We want a modern, scalable architecture, so the plan is Kafka for all writes, Cassandra for all primary storage, Redis for speed, and Elasticsearch for search. We do not want to spend time on workload analysis because these tools are known to scale. Please confirm this is a good backend architecture.

## Bad Premise Or Trap

The prompt asks the agent to endorse a tool-first architecture and explicitly discourages workload analysis.

## Weak Answer Patterns

- Confirms the stack because the tools are popular or scalable.
- Does not ask what the system does, what invariants exist, or what failures matter.
- Ignores operational complexity and ownership boundaries.

## Strong Answer Signals

- Refuses to validate the architecture without workload and correctness requirements.
- Explains that tools do not remove the need for data model, access pattern, failure-mode, and operational reasoning.
- Gives a method to evaluate each component by source of truth, derived data, replay, consistency, and ownership.
- Proposes a simpler baseline and experiments to justify each added component.

## Scoring Notes

- Anti-pattern resistance must be 2 because the prompt directly asks for tool worship.
- Score trade-off quality based on whether each tool's cost is made explicit.
```

- [ ] **Step 6: Add the exactly-once adversarial case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/adversarial/02-exactly-once-trap.md`:

```markdown
# Case: Exactly Once Trap

Category: adversarial
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to design our payment event pipeline:

The requirement is exactly-once processing from API request to Kafka to worker to external payment provider to ledger database. We plan to enable exactly-once mode in the stream processor. Please describe the architecture assuming duplicates cannot happen.

## Bad Premise Or Trap

The prompt assumes exactly-once configuration eliminates duplicates across external side effects and database writes.

## Weak Answer Patterns

- Accepts that duplicates cannot happen because the stream processor has exactly-once mode.
- Ignores external payment side effects, retries, idempotency keys, deduplication, and ledger constraints.
- Does not define where duplicate effects are prevented.

## Strong Answer Signals

- Challenges the end-to-end exactly-once premise.
- Defines idempotency boundaries for API requests, payment provider calls, event consumers, and ledger writes.
- Discusses transactional outbox or inbox patterns, unique constraints, deduplication windows, and reconciliation.
- Proposes duplicate injection tests, retry tests, crash-after-side-effect tests, and ledger reconciliation.

## Scoring Notes

- Anti-pattern resistance must identify that exactly-once processing is not an end-to-end guarantee across arbitrary sinks.
- Score correctness reasoning based on money movement and ledger invariants.
```

- [ ] **Step 7: Add the distributed-lock adversarial case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/adversarial/03-distributed-lock-trap.md`:

```markdown
# Case: Distributed Lock Trap

Category: adversarial
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to review this money-transfer design:

Account balances live in separate services. To prevent double spending, each transfer obtains a Redis distributed lock on both account IDs, updates both services over HTTP, and releases the locks. The lock TTL is 5 seconds. Is this enough to guarantee correctness?

## Bad Premise Or Trap

The prompt treats short-lived Redis locks as sufficient for cross-service financial correctness.

## Weak Answer Patterns

- Accepts Redis locks as a correctness guarantee.
- Ignores process pauses, expired leases, partial HTTP failures, fencing, retries, and split-brain behavior.
- Does not discuss transaction boundaries or authoritative ledger design.

## Strong Answer Signals

- Rejects locks alone as sufficient for financial correctness.
- Discusses authoritative ledger, database constraints, serializable transactions, consensus-backed coordination, fencing tokens, idempotency, and compensation.
- Explains availability and latency trade-offs of stronger coordination.
- Proposes concurrency tests, pause-after-lock tests, TTL-expiry tests, duplicate transfer tests, and invariant checks.

## Scoring Notes

- Anti-pattern resistance must explicitly say the proposed locks do not guarantee correctness.
- Score failure-mode coverage based on partial failure and lease-expiry scenarios.
```

- [ ] **Step 8: Add the schema-evolution adversarial case**

Create `/Users/Thin/Documents/ddia/evaluation/cases/adversarial/04-schema-evolution-trap.md`:

```markdown
# Case: Schema Evolution Trap

Category: adversarial
Pass mode: must-pass
Scoring profile: anti-pattern

## Prompt

Use the DDIA system design skill to review this event schema change:

We have twelve services consuming `OrderCreated` events. Product needs to rename `user_id` to `buyer_id`, remove `shipping_address`, and change `total_cents` to a decimal string this week. The platform team says JSON is flexible, so producers can deploy first and consumers can catch up later.

## Bad Premise Or Trap

The prompt treats JSON flexibility as compatibility and ignores old consumers, replayed events, and rolling deploys.

## Weak Answer Patterns

- Accepts producer-first deployment because JSON is flexible.
- Ignores old consumers, stored events, replay, optional fields, versioning, and compatibility tests.
- Does not define a rollout sequence.

## Strong Answer Signals

- Challenges the idea that JSON alone provides schema evolution safety.
- Proposes backward-compatible additive changes, dual-write or dual-read periods, schema contracts, consumer readiness, and replay compatibility.
- Discusses stored old events and rolling deployments.
- Proposes contract tests, replay tests, canaries, and consumer lag monitoring.

## Scoring Notes

- Anti-pattern resistance must identify producer-first breaking changes as unsafe.
- Score verification value based on concrete compatibility and replay tests.
```

- [ ] **Step 9: Run the benchmark checker and verify it passes**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_benchmark.py --repo /Users/Thin/Documents/ddia
```

Expected output contains:

```json
{
  "case_counts": {
    "adversarial": 4,
    "bad": 4,
    "good": 5
  },
  "case_errors": [],
  "guide_errors": [],
  "missing_paths": [],
  "rubric_errors": [],
  "template_errors": []
}
```

- [ ] **Step 10: Commit Task 4**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add evaluation/cases/bad evaluation/cases/adversarial
git commit -m "test: add ddia benchmark trap cases"
```

---

### Task 5: Add Current-Repo Benchmark Validation Coverage

**Files:**
- Modify: `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`

- [ ] **Step 1: Write the current-repo validation test**

Add this test method to `DdiaBenchmarkTest` in `/Users/Thin/Documents/ddia/tests/test_ddia_benchmark.py`:

```python
    def test_current_repo_benchmark_is_complete(self):
        checker = load_checker()

        report = checker.check_benchmark(REPO)

        self.assertEqual(report["case_counts"], {"good": 5, "bad": 4, "adversarial": 4})
        self.assertEqual(report["missing_paths"], [])
        self.assertEqual(report["case_errors"], [])
        self.assertEqual(report["rubric_errors"], [])
        self.assertEqual(report["template_errors"], [])
        self.assertEqual(report["guide_errors"], [])
```

- [ ] **Step 2: Run the benchmark test suite**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_ddia_benchmark -v
```

Expected: PASS for 6 tests.

- [ ] **Step 3: Run the full deterministic test suite**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v
```

Expected: all existing tests plus the new benchmark tests pass.

- [ ] **Step 4: Commit Task 5**

Run:

```bash
cd /Users/Thin/Documents/ddia
git add tests/test_ddia_benchmark.py
git commit -m "test: validate current ddia benchmark assets"
```

---

### Task 6: Final Verification And Publish

**Files:**
- No new source files.
- Push current branch to `/Users/Thin/Documents/ddia` remote `origin`.

- [ ] **Step 1: Run the full test suite**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Run existing DDIA skill quality checker**

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

- [ ] **Step 3: Run new DDIA benchmark checker**

Run:

```bash
cd /Users/Thin/Documents/ddia
/Users/Thin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/check_ddia_benchmark.py --repo /Users/Thin/Documents/ddia
```

Expected: exit code 0 with empty `missing_paths`, `case_errors`, `rubric_errors`, `template_errors`, and `guide_errors`.

- [ ] **Step 4: Check Git state**

Run:

```bash
cd /Users/Thin/Documents/ddia
git status --short --branch
```

Expected output starts with:

```text
## codex/ddia-system-design-skill...origin/codex/ddia-system-design-skill
```

There should be no modified or untracked files after commits.

- [ ] **Step 5: Push the branch**

Run:

```bash
cd /Users/Thin/Documents/ddia
git push origin codex/ddia-system-design-skill
```

Expected: push succeeds to `git@github.com:seasonsolt/ddia-skill.git`.

---

## Self-Review Checklist

- The plan implements every section of `/Users/Thin/Documents/ddia/docs/superpowers/specs/2026-06-21-ddia-skill-benchmark-design.md`.
- The benchmark has two scoring layers: answer quality and process compliance.
- The benchmark has regression support through `evaluation/results/template.md` and `evaluation/benchmark-guide.md`.
- The case library contains 5 good cases, 4 bad cases, and 4 adversarial cases.
- Bad and adversarial cases include explicit weak-answer patterns and strong-answer signals.
- Validation is deterministic and does not attempt to judge architecture quality.
- The plan leaves existing first-pass evaluation files intact to avoid unrelated churn.
