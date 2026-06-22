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

CODING_AB_CASES = {
    "checkout-cache-as-truth": "bad",
    "payment-exactly-once-trap": "adversarial",
    "order-outbox-missing": "bad",
    "profile-replica-lag": "bad",
    "redis-distributed-lock-money-transfer": "adversarial",
}
CODING_AB_REQUIRED_FILES = [
    "evaluation/coding-ab/README.md",
    "evaluation/coding-ab/control-instructions.md",
    "evaluation/coding-ab/treatment-instructions.md",
    "evaluation/coding-ab/blind-llm-judge.md",
    "evaluation/coding-ab/results-template.md",
] + [f"evaluation/coding-ab/cases/{case_id}.md" for case_id in CODING_AB_CASES]
CODING_AB_README_SECTIONS = ["Purpose", "Method", "Case Set", "Limitations"]
CODING_AB_JUDGE_SECTIONS = ["Scoring Order", "Dimensions", "Mapping Reveal"]
CODING_AB_JUDGE_DIMENSIONS = [
    "Correctness invariant",
    "Source-of-truth boundary",
    "Failure-mode handling",
    "Idempotency and retry safety",
    "Operational verification",
    "Java patch quality",
    "Anti-pattern resistance",
]
CODING_AB_RESULT_SECTIONS = [
    "Run Metadata",
    "Hidden Mapping",
    "Case Scores",
    "Dimension Differences",
    "Response Archive",
    "Overall Decision",
]
CODING_AB_CASE_SECTIONS = [
    "Scenario",
    "Flawed Java",
    "Task",
    "Expected DDIA Reasoning",
    "Strong Patch Signals",
    "Weak Patch Patterns",
    "Scoring Notes",
]
CODING_AB_BULLET_CASE_SECTIONS = [
    "Strong Patch Signals",
    "Weak Patch Patterns",
    "Scoring Notes",
]
CODING_AB_REQUIRED_PHRASES = {
    "evaluation/coding-ab/README.md": ["control", "treatment", "Java", "not statistical"],
    "evaluation/coding-ab/control-instructions.md": [
        "without using or referencing ddia-system-design",
        "Do not load, invoke, mention, or rely on the DDIA system design skill",
    ],
    "evaluation/coding-ab/treatment-instructions.md": [
        "Use ddia-system-design",
        "source of truth",
        "failure modes",
        "idempotency",
    ],
    "evaluation/coding-ab/blind-llm-judge.md": [
        "Score Response A and Response B before revealing",
        "Reveal the mapping only after",
        "0, 1, or 2 points",
        "Bad coding cases pass",
        "Adversarial coding cases pass",
    ],
    "evaluation/coding-ab/results-template.md": [
        "Control score",
        "Treatment score",
        "Lift",
        "Pass/fail change",
        "Response Archive",
    ],
}
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
CODING_AB_ANTI_PATTERN_SCORE_KEY = "anti_pattern_resistance"
CODING_AB_BASE_SCORE_KEYS = [
    score_key for score_key in CODING_AB_SCORE_KEYS if score_key != CODING_AB_ANTI_PATTERN_SCORE_KEY
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


def first_fenced_code_block(text: str, language: str) -> str | None:
    pattern = rf"```{re.escape(language)}\s*\n(.*?)```"
    match = re.search(pattern, text, flags=re.DOTALL)
    return match.group(1) if match else None


def markdown_table_first_column_values(body: str) -> set[str]:
    values = set()
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or cells[0] == "Case" or set(cells[0]) <= {"-", " "}:
            continue
        values.add(cells[0])
    return values


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


def validate_coding_ab_case(path: pathlib.Path, relative: str, expected_category: str) -> list[str]:
    text = read_text(path)
    errors = []
    lines = text.splitlines()
    case_id = pathlib.Path(relative).stem

    if not lines or lines[0].strip() != f"# Coding Case: {case_id}":
        errors.append(f"{relative}: missing # Coding Case: heading")

    if metadata_value(text, "Case ID") != case_id:
        errors.append(f"{relative}: expected Case ID: {case_id}")

    if metadata_value(text, "Category") != expected_category:
        errors.append(f"{relative}: expected Category: {expected_category}")

    if metadata_value(text, "Language") != "Java":
        errors.append(f"{relative}: expected Language: Java")

    topics = metadata_value(text, "Primary DDIA topics")
    if not topics:
        errors.append(f"{relative}: missing Primary DDIA topics")

    for section in CODING_AB_CASE_SECTIONS:
        body = section_body(text, section)
        if body is None:
            errors.append(f"{relative}: missing section {section}")
            continue
        if section in CODING_AB_BULLET_CASE_SECTIONS and not has_bullet(body):
            errors.append(f"{relative}: section {section} must include at least one bullet")
        if section == "Flawed Java":
            java_code = first_fenced_code_block(body, "java")
            if java_code is None:
                errors.append(f"{relative}: section Flawed Java must include a java code block")
            elif not java_code.strip():
                errors.append(f"{relative}: section Flawed Java must include non-empty java code")

    return errors


def validate_coding_ab_judge_result_payload(payload: object) -> list[str]:
    if not isinstance(payload, dict):
        return ["payload: must be a JSON object"]

    errors = []
    if any(leak_key in payload for leak_key in ["mapping", "arm", "variant"]):
        errors.append("payload: must not reveal control or treatment mapping")

    case_id = payload.get("case_id")
    if not isinstance(case_id, str) or not case_id.strip():
        errors.append("case_id: must be a non-empty string")
        case_category = None
    else:
        case_category = CODING_AB_CASES.get(case_id)
        if case_category is None:
            errors.append(f"case_id: unknown coding A/B case {case_id}")

    for response_key in CODING_AB_RESPONSE_KEYS:
        response = payload.get(response_key)
        if not isinstance(response, dict):
            errors.append(f"{response_key}: must be an object")
            continue

        if any(leak_key in response for leak_key in ["mapping", "arm", "variant"]):
            errors.append(f"{response_key}: must not reveal control or treatment mapping")

        scores = response.get("scores")
        score_sum = 0
        score_errors = False
        base_scores: list[int] = []
        anti_pattern_score: int | None = None
        if not isinstance(scores, dict):
            errors.append(f"{response_key}: scores must be an object")
            score_errors = True
        else:
            for score_key in CODING_AB_BASE_SCORE_KEYS:
                if score_key not in scores:
                    errors.append(f"{response_key}: missing score {score_key}")
                    score_errors = True
                    continue

                score = scores[score_key]
                if isinstance(score, bool) or score not in {0, 1, 2}:
                    errors.append(f"{response_key}: {score_key} must be 0, 1, or 2")
                    score_errors = True
                    continue
                score_sum += score
                base_scores.append(score)

            if CODING_AB_ANTI_PATTERN_SCORE_KEY not in scores:
                errors.append(f"{response_key}: missing score {CODING_AB_ANTI_PATTERN_SCORE_KEY}")
                score_errors = True
            else:
                anti_pattern_score = scores[CODING_AB_ANTI_PATTERN_SCORE_KEY]
                if case_category == "adversarial":
                    if isinstance(anti_pattern_score, bool) or anti_pattern_score not in {0, 1, 2}:
                        errors.append(
                            f"{response_key}: anti_pattern_resistance must be 0, 1, or 2 "
                            "for adversarial coding cases"
                        )
                        score_errors = True
                    else:
                        score_sum += anti_pattern_score
                elif case_category is not None:
                    if anti_pattern_score is not None:
                        errors.append(
                            f"{response_key}: anti_pattern_resistance must be null "
                            "for non-adversarial coding cases"
                        )
                        score_errors = True

        total = response.get("total")
        if isinstance(total, bool) or not isinstance(total, int):
            errors.append(f"{response_key}: total must be an integer")
            total_valid = False
        else:
            total_valid = True
            max_total = 14 if case_category == "adversarial" else 12
            if case_category is not None and total > max_total:
                errors.append(f"{response_key}: total must not exceed {max_total}")
            if isinstance(scores, dict) and not score_errors and total != score_sum:
                errors.append(f"{response_key}: total {total} does not match score sum {score_sum}")

        passed = response.get("pass")
        if not isinstance(passed, bool):
            errors.append(f"{response_key}: pass must be a boolean")
        elif case_category is not None and total_valid and isinstance(scores, dict) and not score_errors:
            if case_category == "adversarial":
                computed_pass = (
                    total >= 12
                    and all(score > 0 for score in base_scores)
                    and anti_pattern_score is not None
                    and anti_pattern_score > 0
                    and anti_pattern_score == 2
                )
            else:
                computed_pass = total >= 10 and all(score > 0 for score in base_scores)
            if passed != computed_pass:
                errors.append(f"{response_key}: pass {passed} does not match computed pass {computed_pass}")

        rationale = response.get("rationale")
        if not isinstance(rationale, str) or len(rationale.strip()) < 20:
            errors.append(f"{response_key}: rationale must be at least 20 characters")

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
            continue
        for phrase in CODING_AB_REQUIRED_PHRASES.get(relative, []):
            if phrase not in text:
                errors.append(f"{relative}: missing phrase {phrase}")

    readme = repo / "evaluation/coding-ab/README.md"
    if readme.exists():
        errors.extend(validate_required_sections(readme, "evaluation/coding-ab/README.md", CODING_AB_README_SECTIONS))
        readme_text = read_text(readme)
        for case_id in CODING_AB_CASES:
            relative = f"evaluation/coding-ab/cases/{case_id}.md"
            if relative not in readme_text:
                errors.append(f"evaluation/coding-ab/README.md: missing case {relative}")

    judge = repo / "evaluation/coding-ab/blind-llm-judge.md"
    if judge.exists():
        errors.extend(
            validate_required_sections(
                judge,
                "evaluation/coding-ab/blind-llm-judge.md",
                CODING_AB_JUDGE_SECTIONS,
            )
        )
        dimensions_body = section_body(read_text(judge), "Dimensions") or ""
        for dimension in CODING_AB_JUDGE_DIMENSIONS:
            if not has_dimension(dimensions_body, dimension):
                errors.append(f"evaluation/coding-ab/blind-llm-judge.md: missing dimension {dimension}")

    template = repo / "evaluation/coding-ab/results-template.md"
    if template.exists():
        template_text = read_text(template)
        errors.extend(
            validate_required_sections(
                template,
                "evaluation/coding-ab/results-template.md",
                CODING_AB_RESULT_SECTIONS,
            )
        )
        case_scores = section_body(template_text, "Case Scores") or ""
        template_case_ids = markdown_table_first_column_values(case_scores)
        for case_id in CODING_AB_CASES:
            if case_id not in template_case_ids:
                errors.append(f"evaluation/coding-ab/results-template.md: missing case {case_id}")
        normalized_template = template_text.lower()
        has_adversarial_max_14 = (
            "adversarial" in normalized_template
            and (
                "maximum score of 14" in normalized_template
                or "max 14" in normalized_template
                or "out of 14" in normalized_template
            )
        )
        if not has_adversarial_max_14:
            errors.append(
                "evaluation/coding-ab/results-template.md: must explain adversarial coding cases have max 14"
            )

    control_text = read_text(repo / "evaluation/coding-ab/control-instructions.md")
    if control_text and (
        "without using or referencing ddia-system-design" not in control_text
        or "Do not load, invoke, mention, or rely on the DDIA system design skill" not in control_text
    ):
        errors.append("evaluation/coding-ab/control-instructions.md: must forbid using ddia-system-design")

    treatment_text = read_text(repo / "evaluation/coding-ab/treatment-instructions.md")
    if treatment_text and (
        "Use ddia-system-design" not in treatment_text
        or "source of truth" not in treatment_text
        or "failure modes" not in treatment_text
        or "idempotency" not in treatment_text
    ):
        errors.append("evaluation/coding-ab/treatment-instructions.md: must require DDIA coding review constraints")

    for case_id, expected_category in CODING_AB_CASES.items():
        relative = f"evaluation/coding-ab/cases/{case_id}.md"
        path = repo / relative
        if path.exists():
            errors.extend(validate_coding_ab_case(path, relative, expected_category))

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
    coding_ab_missing_paths, coding_ab_errors = validate_coding_ab_assets(repo)

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
        "coding_ab_missing_paths",
        "coding_ab_errors",
    ]
    return 1 if any(report[key] for key in error_keys) else 0


if __name__ == "__main__":
    raise SystemExit(main())
