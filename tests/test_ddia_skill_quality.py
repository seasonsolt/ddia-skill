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


TOPIC_MAP_SECTIONS = [
    "Reliability, Scalability, Maintainability",
    "Data Models And Query Languages",
    "Storage And Retrieval",
    "Encoding And Evolution",
    "Replication",
    "Partitioning",
    "Transactions And Isolation",
    "Distributed Faults",
    "Consistency And Consensus",
    "Batch Processing",
    "Stream Processing",
    "Derived Data And Correctness",
]

PRINCIPLE_SECTIONS = [
    "Start With Workload Shape",
    "Treat Guarantees As Product Behavior",
    "Model Derived Data Explicitly",
    "Design For Partial Failure",
    "Make Evolution A First-Class Requirement",
    "Prefer Simple Ownership Boundaries",
    "Review Storage Choices By Access Pattern",
    "Review Replication Choices By Failure Behavior",
    "Review Partitioning Choices By Skew And Query Routing",
    "Review Transactions By Anomaly",
    "Review Streams By Replay And Time",
]

CHECKLIST_SECTIONS = [
    "Workload Checklist",
    "Data Model Checklist",
    "Replication And Consistency Checklist",
    "Partitioning Checklist",
    "Transaction And Correctness Checklist",
    "Distributed Failure Checklist",
    "Batch And Stream Checklist",
    "Derived Data Checklist",
    "Recommendation Checklist",
]


def reference_with_bullets(heading: str, sections: list[str], terms: str) -> str:
    body = [heading, ""]
    for section in sections:
        body.extend(
            [
                f"## {section}",
                "",
                f"- {section} coverage includes {terms}.",
                "",
            ]
        )
    return "\n".join(body)


def make_complete_repo(root: pathlib.Path) -> None:
    write(root / "skills/ddia-system-design/SKILL.md", "# DDIA Skill\n\nreliability scalability maintainability\n")
    write(root / "skills/ddia-system-design/agents/openai.yaml", "name: ddia-system-design\n")
    all_terms = "reliability scalability maintainability replication partitioning transactions isolation linearizability consensus batch processing stream processing derived data"
    write(
        root / "skills/ddia-system-design/references/topic-map.md",
        reference_with_bullets("# DDIA Topic Map For Backend Architecture", TOPIC_MAP_SECTIONS, all_terms),
    )
    write(
        root / "skills/ddia-system-design/references/system-design-principles.md",
        reference_with_bullets(
            "# System Design Principles",
            PRINCIPLE_SECTIONS,
            "workload guarantees derived data partial failure evolution ownership storage replication partitioning transactions streams",
        ),
    )
    write(
        root / "skills/ddia-system-design/references/architecture-review-checklists.md",
        reference_with_bullets(
            "# Architecture Review Checklists",
            CHECKLIST_SECTIONS,
            "workload data model replication partitioning transaction distributed failure batch stream derived data recommendation",
        ),
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

    def test_quality_checker_accepts_extra_prompt_above_minimum(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_repo(repo)
            write(
                repo / "evaluation/prompts/99-extra.md",
                """# Prompt 99: Extra

Use the DDIA system design skill to review another backend architecture scenario with enough context to evaluate workload, trade-offs, failure modes, correctness, and verification value.
""",
            )
            template_path = repo / "evaluation/results-template.md"
            template_path.write_text(
                template_path.read_text(encoding="utf-8").replace(
                    "## Overall Decision",
                    """## Prompt 99: Extra

- Workload framing:
- Trade-off quality:
- Failure-mode coverage:
- Correctness reasoning:
- Verification value:
- Total score:
- Pass:
- Notes:

## Overall Decision""",
                ),
                encoding="utf-8",
            )

            report = checker.check_repo(repo)

        self.assertEqual(report["prompt_count"], 6)
        self.assertEqual(report["invalid_files"], [])
        self.assertEqual(report["structure_errors"], [])

    def test_quality_checker_rejects_extra_prompt_without_result_section(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_repo(repo)
            write(
                repo / "evaluation/prompts/99-extra.md",
                """# Prompt 99: Extra

Use the DDIA system design skill to review another backend architecture scenario with enough context to evaluate workload, trade-offs, failure modes, correctness, and verification value.
""",
            )

            report = checker.check_repo(repo)

        self.assertEqual(report["prompt_count"], 6)
        self.assertTrue(any("evaluation/results-template.md: missing Prompt 99: Extra" in item for item in report["invalid_files"]))

    def test_quality_checker_rejects_malformed_extra_prompt(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_repo(repo)
            write(repo / "evaluation/prompts/99-extra.md", "# Extra\n\nUse the DDIA system design skill.\n")

            report = checker.check_repo(repo)

        self.assertEqual(report["prompt_count"], 6)
        self.assertTrue(any("evaluation/prompts/99-extra.md: missing heading # Prompt N:" in item for item in report["invalid_files"]))
        self.assertTrue(any("evaluation/prompts/99-extra.md: content is too short" in item for item in report["invalid_files"]))

    def test_quality_checker_rejects_fewer_than_five_prompts(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_repo(repo)
            (repo / "evaluation/prompts/05-derived-data.md").unlink()

            report = checker.check_repo(repo)

        self.assertEqual(report["prompt_count"], 4)
        self.assertTrue(any("expected at least 5 prompt files" in item for item in report["structure_errors"]))

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

    def test_results_template_requires_scoring_fields_in_each_prompt_section(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_repo(repo)
            write(
                repo / "evaluation/results-template.md",
                """# DDIA Skill Evaluation Results

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

## Prompt 3: Database Choice

## Prompt 4: Replica Lag

## Prompt 5: Derived Data

## Overall Decision

- All prompts passed:
- Skill changes needed:
""",
            )

            report = checker.check_repo(repo)

        self.assertTrue(any("Prompt 2: Event Pipeline" in item for item in report["invalid_files"]))
        self.assertTrue(any("Total score" in item for item in report["invalid_files"]))

    def test_reference_sections_require_non_empty_bullets(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_repo(repo)
            body = ["# DDIA Topic Map For Backend Architecture", ""]
            for section in TOPIC_MAP_SECTIONS:
                body.extend([f"## {section}", "", "Filler paragraph without a bullet.", ""])
            write(repo / "skills/ddia-system-design/references/topic-map.md", "\n".join(body))

            report = checker.check_repo(repo)

        self.assertTrue(any("topic-map.md" in item and "non-empty bullet" in item for item in report["structure_errors"]))

    def test_reference_role_terms_must_be_in_their_own_reference_files(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            make_complete_repo(repo)
            concentrated_terms = " ".join(
                [
                    "reliability",
                    "scalability",
                    "maintainability",
                    "linearizability",
                    "consensus",
                    "batch processing",
                    "stream processing",
                    "workload",
                    "guarantees",
                    "derived data",
                    "partial failure",
                    "evolution",
                    "ownership",
                    "storage",
                    "replication",
                    "partitioning",
                    "transactions",
                    "streams",
                ]
            )
            write(
                repo / "skills/ddia-system-design/references/topic-map.md",
                reference_with_bullets(
                    "# DDIA Topic Map For Backend Architecture",
                    TOPIC_MAP_SECTIONS,
                    concentrated_terms,
                ),
            )
            write(
                repo / "skills/ddia-system-design/references/system-design-principles.md",
                reference_with_bullets(
                    "# System Design Principles",
                    [f"Generic Section {index}" for index in range(1, len(PRINCIPLE_SECTIONS) + 1)],
                    "generic architecture text",
                ),
            )

            report = checker.check_repo(repo)

        self.assertEqual(report["missing_terms"], [])
        self.assertTrue(any("system-design-principles.md" in item and "workload" in item for item in report["structure_errors"]))

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
