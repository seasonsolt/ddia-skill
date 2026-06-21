#!/usr/bin/env python3
import argparse
import json
import pathlib
from typing import Any


REQUIRED_FILES = [
    "skills/ddia-system-design/SKILL.md",
    "skills/ddia-system-design/references/topic-map.md",
    "skills/ddia-system-design/references/system-design-principles.md",
    "skills/ddia-system-design/references/architecture-review-checklists.md",
    "skills/ddia-system-design/agents/openai.yaml",
    "evaluation/rubric.md",
    "evaluation/prompts/01-order-consistency.md",
    "evaluation/prompts/02-event-pipeline.md",
    "evaluation/prompts/03-database-choice.md",
    "evaluation/prompts/04-replica-lag.md",
    "evaluation/prompts/05-derived-data.md",
    "evaluation/results-template.md",
]

REFERENCE_FILES = {
    "skills/ddia-system-design/references/topic-map.md": "# DDIA Topic Map For Backend Architecture",
    "skills/ddia-system-design/references/system-design-principles.md": "# System Design Principles",
    "skills/ddia-system-design/references/architecture-review-checklists.md": "# Architecture Review Checklists",
}

PROMPT_FILES = {
    "evaluation/prompts/01-order-consistency.md": "# Prompt 1:",
    "evaluation/prompts/02-event-pipeline.md": "# Prompt 2:",
    "evaluation/prompts/03-database-choice.md": "# Prompt 3:",
    "evaluation/prompts/04-replica-lag.md": "# Prompt 4:",
    "evaluation/prompts/05-derived-data.md": "# Prompt 5:",
}

DIMENSION_LABELS = [
    "Workload framing",
    "Trade-off quality",
    "Failure-mode coverage",
    "Correctness reasoning",
    "Verification value",
]

PROMPT_TITLES = [
    "Prompt 1: Order Consistency",
    "Prompt 2: Event Pipeline",
    "Prompt 3: Database Choice",
    "Prompt 4: Replica Lag",
    "Prompt 5: Derived Data",
]

REQUIRED_TERMS = [
    "reliability",
    "scalability",
    "maintainability",
    "replication",
    "partitioning",
    "transactions",
    "isolation",
    "linearizability",
    "consensus",
    "batch processing",
    "stream processing",
    "derived data",
]


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_existing_text(repo: pathlib.Path, relative_paths: list[str]) -> str:
    chunks = []
    for relative in relative_paths:
        path = repo / relative
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks).lower()


def validate_rubric(repo: pathlib.Path) -> list[str]:
    relative = "evaluation/rubric.md"
    text = read_text(repo / relative)
    lower = text.lower()
    errors = []
    if not text.strip():
        return [f"{relative}: file is empty"]
    for label in DIMENSION_LABELS:
        if label.lower() not in lower:
            errors.append(f"{relative}: missing dimension {label}")
    if "passing standard" not in lower:
        errors.append(f"{relative}: missing Passing Standard")
    for anchor in ["0:", "1:", "2:"]:
        if anchor not in text:
            errors.append(f"{relative}: missing score anchor {anchor}")
    return errors


def validate_prompts(repo: pathlib.Path) -> tuple[int, list[str], list[str]]:
    prompt_dir = repo / "evaluation" / "prompts"
    prompt_count = len(list(prompt_dir.glob("*.md"))) if prompt_dir.exists() else 0
    invalid_files = []
    structure_errors = []
    if prompt_count != 5:
        structure_errors.append(f"evaluation/prompts: expected 5 prompt files, found {prompt_count}")

    for relative, heading in PROMPT_FILES.items():
        text = read_text(repo / relative)
        if not text.strip():
            invalid_files.append(f"{relative}: file is empty")
            continue
        if heading not in text.splitlines()[0]:
            invalid_files.append(f"{relative}: missing heading {heading}")
        if "Use the DDIA system design skill" not in text:
            invalid_files.append(f"{relative}: missing skill usage instruction")
        if len(text.strip()) < 120:
            invalid_files.append(f"{relative}: content is too short")
    return prompt_count, invalid_files, structure_errors


def validate_results_template(repo: pathlib.Path) -> list[str]:
    relative = "evaluation/results-template.md"
    text = read_text(repo / relative)
    lower = text.lower()
    errors = []
    if not text.strip():
        return [f"{relative}: file is empty"]
    for title in PROMPT_TITLES:
        if title.lower() not in lower:
            errors.append(f"{relative}: missing {title}")
    for label in DIMENSION_LABELS:
        if f"- {label.lower()}:" not in lower:
            errors.append(f"{relative}: missing {label} label")
    for label in ["- total score:", "- pass:", "overall decision"]:
        if label not in lower:
            errors.append(f"{relative}: missing {label}")
    return errors


def validate_references(repo: pathlib.Path) -> list[str]:
    errors = []
    for relative, heading in REFERENCE_FILES.items():
        text = read_text(repo / relative)
        if not text.strip():
            errors.append(f"{relative}: file is empty")
            continue
        first_line = text.splitlines()[0] if text.splitlines() else ""
        if first_line != heading:
            errors.append(f"{relative}: expected heading {heading}")
        section_count = sum(1 for line in text.splitlines() if line.startswith("## "))
        if len(text.strip()) < 300:
            errors.append(f"{relative}: content is too short")
        if section_count < 2:
            errors.append(f"{relative}: expected at least 2 sections")
    return errors


def check_repo(repo: pathlib.Path) -> dict[str, Any]:
    missing_files = [relative for relative in REQUIRED_FILES if not (repo / relative).exists()]
    prompt_count, invalid_prompt_files, prompt_structure_errors = validate_prompts(repo)
    invalid_files = []
    invalid_files.extend(validate_rubric(repo))
    invalid_files.extend(invalid_prompt_files)
    invalid_files.extend(validate_results_template(repo))
    structure_errors = []
    structure_errors.extend(prompt_structure_errors)
    structure_errors.extend(validate_references(repo))
    skill_text = read_existing_text(
        repo,
        [
            "skills/ddia-system-design/SKILL.md",
            "skills/ddia-system-design/references/topic-map.md",
            "skills/ddia-system-design/references/system-design-principles.md",
            "skills/ddia-system-design/references/architecture-review-checklists.md",
        ],
    )
    missing_terms = [term for term in REQUIRED_TERMS if term not in skill_text]
    return {
        "missing_files": missing_files,
        "missing_terms": missing_terms,
        "prompt_count": prompt_count,
        "invalid_files": invalid_files,
        "structure_errors": structure_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check DDIA skill quality assets.")
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path("."))
    args = parser.parse_args()

    report = check_repo(args.repo.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if (
        report["missing_files"]
        or report["missing_terms"]
        or report["invalid_files"]
        or report["structure_errors"]
        or report["prompt_count"] != 5
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
