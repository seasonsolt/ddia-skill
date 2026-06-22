#!/usr/bin/env python3
import argparse
import json
import pathlib
import re


EXPECTED_CASE_COUNTS = {"good": 5, "bad": 4, "adversarial": 4}
AB_EXPECTED_SCORE_DENOMINATORS = {"good": 10, "bad": 12, "adversarial": 12}
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
    "Limitations",
    "Overall Decision",
]
AB_PILOT_CASES = [
    "evaluation/cases/good/01-order-consistency.md",
    "evaluation/cases/good/04-replica-lag.md",
    "evaluation/cases/bad/01-cache-as-truth.md",
    "evaluation/cases/adversarial/02-exactly-once-trap.md",
    "evaluation/cases/bad/04-vague-startup-architecture.md",
]
AB_PILOT_CASE_SCORE_SLUGS = {
    "evaluation/cases/good/01-order-consistency.md": "order-consistency",
    "evaluation/cases/good/04-replica-lag.md": "replica-lag",
    "evaluation/cases/bad/01-cache-as-truth.md": "cache-as-truth",
    "evaluation/cases/adversarial/02-exactly-once-trap.md": "exactly-once-trap",
    "evaluation/cases/bad/04-vague-startup-architecture.md": "vague-startup-architecture",
}
AB_ALLOWED_SCORE_CATEGORIES = {"good", "bad", "adversarial"}
AB_PILOT_CASE_SCORE_CATEGORIES = {
    "order-consistency": "good",
    "replica-lag": "good",
    "cache-as-truth": "bad",
    "exactly-once-trap": "adversarial",
    "vague-startup-architecture": "bad",
}
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
AB_SCORE_ROW_COLUMN_COUNT = 2 + len(AB_SCORE_COLUMNS)
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


def parse_score_fraction(value: str) -> tuple[int, int] | None:
    match = re.fullmatch(r"(\d+)/(\d+)", value.strip())
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def parse_percent(value: str) -> float | None:
    match = re.fullmatch(r"(\d+(?:\.\d+)?)%", value.strip())
    return float(match.group(1)) if match else None


def parse_normalized_lift(value: str) -> float | None:
    match = re.fullmatch(r"([+-]\d+(?:\.\d+)?) pp", value.strip())
    return float(match.group(1)) if match else None


def parse_lift(value: str) -> int | None:
    match = re.fullmatch(r"([+-]\d+)", value.strip())
    return int(match.group(1)) if match else None


def markdown_table_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    if not cells or cells[0] == "Case" or all(set(cell) <= {"-", ":"} for cell in cells):
        return None
    return cells


def validate_ab_score_math(text: str, relative: str) -> list[str]:
    errors: list[str] = []
    control_total = 0
    treatment_total = 0
    normalized_control_values: list[float] = []
    normalized_treatment_values: list[float] = []
    score_row_cases: set[str] = set()
    score_text = section_body(text, "Case Scores") or ""

    for line in score_text.splitlines():
        cells = markdown_table_cells(line)
        if cells is None:
            continue
        if len(cells) != AB_SCORE_ROW_COLUMN_COUNT:
            case = cells[0] if cells else "<unknown>"
            errors.append(f"{relative}: malformed score row for {case}")
            continue

        case = cells[0]
        category = cells[1]
        control_score = parse_score_fraction(cells[2])
        treatment_score = parse_score_fraction(cells[3])
        lift = parse_lift(cells[4])
        control_norm = parse_percent(cells[5])
        treatment_norm = parse_percent(cells[6])
        normalized_lift = parse_normalized_lift(cells[7])
        if (
            control_score is None
            or treatment_score is None
            or lift is None
            or control_norm is None
            or treatment_norm is None
            or normalized_lift is None
        ):
            errors.append(f"{relative}: unparseable score row for {case}")
            continue

        score_row_cases.add(case)
        control, control_den = control_score
        treatment, treatment_den = treatment_score

        control_total += control
        treatment_total += treatment
        if category not in AB_ALLOWED_SCORE_CATEGORIES:
            errors.append(f"{relative}: {case} unknown category {category}")
        expected_category = AB_PILOT_CASE_SCORE_CATEGORIES.get(case)
        if expected_category is not None and category != expected_category:
            errors.append(f"{relative}: {case} expected category {expected_category}, found {category}")
        if control_den != treatment_den:
            errors.append(f"{relative}: {case} control and treatment denominators must match")

        expected_denominator = AB_EXPECTED_SCORE_DENOMINATORS.get(category)
        if expected_denominator is not None and (
            control_den != expected_denominator or treatment_den != expected_denominator
        ):
            errors.append(f"{relative}: {case} expected denominator {expected_denominator} for category {category}")

        if control_den <= 0 or treatment_den <= 0:
            errors.append(f"{relative}: {case} score denominator must be greater than 0")
            continue
        if not 0 <= control <= control_den:
            errors.append(f"{relative}: {case} control score must be between 0 and {control_den}")
        if not 0 <= treatment <= treatment_den:
            errors.append(f"{relative}: {case} treatment score must be between 0 and {treatment_den}")

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

    expected_score_slugs = tuple(AB_PILOT_CASE_SCORE_SLUGS.values())
    expected_score_slug_set = set(expected_score_slugs)
    for case_slug in sorted(score_row_cases - expected_score_slug_set):
        errors.append(f"{relative}: unexpected score row for {case_slug}")

    for case_slug in expected_score_slugs:
        if case_slug not in score_row_cases:
            errors.append(f"{relative}: missing score row for {case_slug}")

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
        for score_label in AB_SCORE_COLUMNS:
            if score_label not in pilot_text:
                errors.append(f"evaluation/ab/pilot-results.md: missing score column {score_label}")
        for limitation in AB_LIMITATION_LABELS:
            if limitation not in pilot_text:
                errors.append(f"evaluation/ab/pilot-results.md: missing limitation {limitation}")
        errors.extend(validate_ab_score_math(pilot_text, "evaluation/ab/pilot-results.md"))

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

    treatment_text = read_text(repo / "evaluation/ab/treatment-instructions.md")
    if treatment_text and "Use ddia-system-design" not in treatment_text:
        errors.append("evaluation/ab/treatment-instructions.md: must require using ddia-system-design")

    return missing_paths, errors


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

    ab_missing_paths, ab_errors = validate_ab_assets(repo)
    missing_paths.extend(ab_missing_paths)

    return {
        "case_counts": case_counts,
        "missing_paths": missing_paths,
        "case_errors": case_errors,
        "rubric_errors": rubric_errors,
        "template_errors": template_errors,
        "guide_errors": guide_errors,
        "ab_errors": ab_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check DDIA skill benchmark structure.")
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path.cwd())
    args = parser.parse_args()

    report = check_benchmark(args.repo)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))

    error_keys = [
        "missing_paths",
        "case_errors",
        "rubric_errors",
        "template_errors",
        "guide_errors",
        "ab_errors",
    ]
    return 1 if any(report[key] for key in error_keys) else 0


if __name__ == "__main__":
    raise SystemExit(main())
