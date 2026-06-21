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


def read_existing_text(repo: pathlib.Path, relative_paths: list[str]) -> str:
    chunks = []
    for relative in relative_paths:
        path = repo / relative
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks).lower()


def check_repo(repo: pathlib.Path) -> dict[str, Any]:
    missing_files = [relative for relative in REQUIRED_FILES if not (repo / relative).exists()]
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
    prompt_count = len(list((repo / "evaluation" / "prompts").glob("*.md"))) if (repo / "evaluation" / "prompts").exists() else 0
    return {
        "missing_files": missing_files,
        "missing_terms": missing_terms,
        "prompt_count": prompt_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check DDIA skill quality assets.")
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path("."))
    args = parser.parse_args()

    report = check_repo(args.repo.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["missing_files"] or report["missing_terms"] or report["prompt_count"] != 5:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
