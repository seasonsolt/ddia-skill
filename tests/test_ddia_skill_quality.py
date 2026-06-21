import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest


REPO = pathlib.Path(__file__).resolve().parents[1]


def load_checker():
    module_path = REPO / "scripts" / "check_ddia_skill_quality.py"
    spec = importlib.util.spec_from_file_location("check_ddia_skill_quality", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_complete_repo(root: pathlib.Path) -> None:
    write(root / "skills/ddia-system-design/SKILL.md", "# DDIA Skill\n\nreliability scalability maintainability\n")
    write(root / "skills/ddia-system-design/agents/openai.yaml", "name: ddia-system-design\n")
    write(
        root / "skills/ddia-system-design/references/topic-map.md",
        """# DDIA Topic Map For Backend Architecture

## Reliability, Scalability, Maintainability

reliability scalability maintainability replication partitioning transactions isolation linearizability consensus batch processing stream processing derived data

## Replication

Use this section to validate meaningful structure and content.

## Partitioning

Use this section to validate meaningful structure and content.
""",
    )
    write(
        root / "skills/ddia-system-design/references/system-design-principles.md",
        """# System Design Principles

## Start With Workload Shape

reliability scalability maintainability replication partitioning transactions isolation linearizability consensus batch processing stream processing derived data

## Treat Guarantees As Product Behavior

Use this section to validate meaningful structure and content.

## Model Derived Data Explicitly

Use this section to validate meaningful structure and content.
""",
    )
    write(
        root / "skills/ddia-system-design/references/architecture-review-checklists.md",
        """# Architecture Review Checklists

## Workload Checklist

reliability scalability maintainability replication partitioning transactions isolation linearizability consensus batch processing stream processing derived data

## Replication And Consistency Checklist

Use this section to validate meaningful structure and content.

## Derived Data Checklist

Use this section to validate meaningful structure and content.
""",
    )
    write(
        root / "evaluation/rubric.md",
        """# DDIA Skill Usefulness Rubric

Score each response from 0 to 2 on each dimension.

## Dimensions

1. Workload framing: identifies reads, writes, load, latency, data volume, and growth assumptions.
2. Trade-off quality: explains costs rather than naming a tool as automatically correct.
3. Failure-mode coverage: names concrete ways the design can fail under concurrency, faults, lag, overload, or operations.
4. Correctness reasoning: discusses isolation, consistency, idempotency, ordering, or reconciliation where relevant.
5. Verification value: gives tests, metrics, experiments, or runbook checks that can validate the design.

## Score Anchors

- 0: Missing or materially incorrect.
- 1: Partially addresses the dimension but leaves important gaps.
- 2: Clearly addresses the dimension with concrete, relevant detail.

## Passing Standard

A prompt passes when the response scores at least 8 out of 10 and has no dimension scored 0.
""",
    )
    prompt_titles = [
        "Order Consistency",
        "Event Pipeline",
        "Database Choice",
        "Replica Lag",
        "Derived Data",
    ]
    for index, title in enumerate(prompt_titles, start=1):
        write(
            root / f"evaluation/prompts/{index:02d}-{title.lower().replace(' ', '-')}.md",
            f"""# Prompt {index}: {title}

Use the DDIA system design skill to review a backend architecture scenario. Include enough body text to validate that this is a meaningful evaluation prompt with trade-offs, failure modes, and correctness checks.
""",
        )
    write(
        root / "evaluation/results-template.md",
        """# DDIA Skill Evaluation Results

Evaluator:
Date:
Skill version:

## Prompt 1: Order Consistency

- Workload framing:
- Trade-off quality:
- Failure-mode coverage:
- Correctness reasoning:
- Verification value:
- Total score:
- Pass:
- Notes:

## Prompt 2: Event Pipeline

- Workload framing:
- Trade-off quality:
- Failure-mode coverage:
- Correctness reasoning:
- Verification value:
- Total score:
- Pass:
- Notes:

## Prompt 3: Database Choice

- Workload framing:
- Trade-off quality:
- Failure-mode coverage:
- Correctness reasoning:
- Verification value:
- Total score:
- Pass:
- Notes:

## Prompt 4: Replica Lag

- Workload framing:
- Trade-off quality:
- Failure-mode coverage:
- Correctness reasoning:
- Verification value:
- Total score:
- Pass:
- Notes:

## Prompt 5: Derived Data

- Workload framing:
- Trade-off quality:
- Failure-mode coverage:
- Correctness reasoning:
- Verification value:
- Total score:
- Pass:
- Notes:

## Overall Decision

- All prompts passed:
- Skill changes needed:
""",
    )


class DdiaSkillQualityTest(unittest.TestCase):
    def test_quality_checker_accepts_complete_assets(self):
        checker = load_checker()
        report = checker.check_repo(REPO)
        self.assertEqual(report["missing_files"], [])
        self.assertEqual(report["missing_terms"], [])
        self.assertEqual(report["prompt_count"], 5)
        self.assertEqual(report["invalid_files"], [])
        self.assertEqual(report["structure_errors"], [])

    def test_quality_checker_reports_missing_required_file(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_repo(repo)
            (repo / "evaluation/rubric.md").unlink()

            report = checker.check_repo(repo)

        self.assertIn("evaluation/rubric.md", report["missing_files"])

    def test_quality_checker_rejects_empty_rubric_or_prompt(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_repo(repo)
            write(repo / "evaluation/rubric.md", "")
            write(repo / "evaluation/prompts/01-order-consistency.md", "")

            report = checker.check_repo(repo)

        self.assertTrue(any("evaluation/rubric.md" in item for item in report["invalid_files"]))
        self.assertTrue(any("evaluation/prompts/01-order-consistency.md" in item for item in report["invalid_files"]))

    def test_quality_checker_reports_wrong_prompt_count_for_extra_prompt(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_repo(repo)
            write(repo / "evaluation/prompts/99-extra.md", "# Prompt 99: Extra\n\nUse the DDIA system design skill.\n")

            report = checker.check_repo(repo)

        self.assertEqual(report["prompt_count"], 6)
        self.assertTrue(any("expected 5 prompt files" in item for item in report["structure_errors"]))

    def test_quality_checker_reports_missing_term_and_reference_structure(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_repo(repo)
            for path in (repo / "skills/ddia-system-design").glob("**/*.md"):
                path.write_text(path.read_text(encoding="utf-8").replace("consensus", ""), encoding="utf-8")
            write(repo / "skills/ddia-system-design/references/topic-map.md", "# Wrong Heading\n\nToo short.\n")

            report = checker.check_repo(repo)

        self.assertIn("consensus", report["missing_terms"])
        self.assertTrue(any("topic-map.md" in item for item in report["structure_errors"]))

    def test_cli_returns_failure_for_incomplete_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(REPO / "scripts" / "check_ddia_skill_quality.py"),
                    "--repo",
                    str(repo),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 1)
        self.assertIn("missing_files", completed.stdout)


if __name__ == "__main__":
    unittest.main()
