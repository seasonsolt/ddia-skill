#!/usr/bin/env python3
import argparse
import json
import pathlib
import re


EXPECTED_CASE_COUNTS = {"good": 5, "bad": 4, "adversarial": 4}
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
BULLET_CASE_SECTIONS = [
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
RESULT_TEMPLATE_SECTIONS = [
    "Run Metadata",
    "Answer Quality",
    "Process Compliance",
    "Regression Notes",
    "Overall Decision",
]
GUIDE_SECTIONS = [
    "Purpose",
    "How To Run",
    "How To Score",
    "Regression Review",
]

RUBRIC_FILES = {
    "evaluation/rubrics/answer-quality.md": ANSWER_QUALITY_DIMENSIONS,
    "evaluation/rubrics/process-compliance.md": PROCESS_COMPLIANCE_DIMENSIONS,
}
RESULT_TEMPLATE_PATH = "evaluation/results/template.md"
GUIDE_PATH = "evaluation/benchmark-guide.md"


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def section_body(text: str, heading: str) -> str | None:
    marker = f"## {heading}"
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            body = []
            for body_line in lines[index + 1 :]:
                if body_line.startswith("## "):
                    break
                body.append(body_line)
            return "\n".join(body)
    return None


def has_bullet(body: str) -> bool:
    return any(line.strip().startswith("- ") and len(line.strip()) > 2 for line in body.splitlines())


def metadata_value(text: str, label: str) -> str | None:
    prefix = f"{label}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def has_markdown_section(text: str, heading: str) -> bool:
    return section_body(text, heading) is not None


def has_dimension(dimensions_body: str, dimension: str) -> bool:
    pattern = rf"^\s*\d+\.\s+{re.escape(dimension)}(?:\b|:|$)"
    return re.search(pattern, dimensions_body, flags=re.MULTILINE) is not None


def validate_case(path: pathlib.Path, relative: str, expected_category: str) -> list[str]:
    text = read_text(path)
    errors = []
    lines = text.splitlines()

    if not lines or not lines[0].startswith("# Case: ") or not lines[0][len("# Case: ") :].strip():
        errors.append(f"{relative}: missing # Case: heading")

    if metadata_value(text, "Category") != expected_category:
        errors.append(f"{relative}: expected Category: {expected_category}")

    pass_mode = metadata_value(text, "Pass mode")
    if pass_mode not in {"must-pass", "diagnostic-only"}:
        errors.append(f"{relative}: expected Pass mode: must-pass or diagnostic-only")

    expected_profile = "good" if expected_category == "good" else "anti-pattern"
    if metadata_value(text, "Scoring profile") != expected_profile:
        errors.append(f"{relative}: expected Scoring profile: {expected_profile}")

    for section in REQUIRED_CASE_SECTIONS:
        body = section_body(text, section)
        if body is None:
            errors.append(f"{relative}: missing section {section}")
            continue
        if section == "Prompt" and len(body.strip()) < 80:
            errors.append(f"{relative}: Prompt must be at least 80 characters")
        if section in BULLET_CASE_SECTIONS and not has_bullet(body):
            errors.append(f"{relative}: section {section} must include at least one bullet")

    return errors


def validate_rubric(path: pathlib.Path, relative: str, dimensions: list[str]) -> list[str]:
    text = read_text(path)
    if not text.strip():
        return [f"{relative}: file is empty"]

    errors = []
    dimensions_body = section_body(text, "Dimensions")
    if dimensions_body is None:
        errors.append(f"{relative}: missing section Dimensions")
        dimensions_body = ""

    for dimension in dimensions:
        if not has_dimension(dimensions_body, dimension):
            errors.append(f"{relative}: missing dimension {dimension}")

    return errors


def validate_required_sections(path: pathlib.Path, relative: str, sections: list[str]) -> list[str]:
    text = read_text(path)
    if not text.strip():
        return [f"{relative}: file is empty"]

    errors = []
    for section in sections:
        if not has_markdown_section(text, section):
            errors.append(f"{relative}: missing section {section}")
    return errors


def check_benchmark(repo: pathlib.Path) -> dict[str, object]:
    repo = pathlib.Path(repo)
    case_counts = {}
    missing_paths = []
    case_errors = []

    for category, relative_dir in CASE_DIRS.items():
        case_dir = repo / relative_dir
        case_files = sorted(case_dir.glob("*.md")) if case_dir.exists() else []
        case_counts[category] = len(case_files)

        if not case_dir.exists():
            missing_paths.append(relative_dir.as_posix())
        expected_count = EXPECTED_CASE_COUNTS[category]
        if len(case_files) != expected_count:
            case_errors.append(f"{relative_dir.as_posix()}: expected {expected_count} cases, found {len(case_files)}")

        for case_path in case_files:
            relative = case_path.relative_to(repo).as_posix()
            case_errors.extend(validate_case(case_path, relative, category))

    rubric_errors = []
    for relative, dimensions in RUBRIC_FILES.items():
        path = repo / relative
        if not path.exists():
            missing_paths.append(relative)
            continue
        rubric_errors.extend(validate_rubric(path, relative, dimensions))

    template_errors = []
    template_path = repo / RESULT_TEMPLATE_PATH
    if not template_path.exists():
        missing_paths.append(RESULT_TEMPLATE_PATH)
    else:
        template_errors.extend(validate_required_sections(template_path, RESULT_TEMPLATE_PATH, RESULT_TEMPLATE_SECTIONS))

    guide_errors = []
    guide_path = repo / GUIDE_PATH
    if not guide_path.exists():
        missing_paths.append(GUIDE_PATH)
    else:
        guide_errors.extend(validate_required_sections(guide_path, GUIDE_PATH, GUIDE_SECTIONS))

    return {
        "case_counts": case_counts,
        "missing_paths": missing_paths,
        "case_errors": case_errors,
        "rubric_errors": rubric_errors,
        "template_errors": template_errors,
        "guide_errors": guide_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check DDIA skill benchmark structure.")
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path.cwd())
    args = parser.parse_args()

    report = check_benchmark(args.repo)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))

    error_keys = ["missing_paths", "case_errors", "rubric_errors", "template_errors", "guide_errors"]
    return 1 if any(report[key] for key in error_keys) else 0


if __name__ == "__main__":
    raise SystemExit(main())
