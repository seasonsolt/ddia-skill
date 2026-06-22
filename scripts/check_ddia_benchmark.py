#!/usr/bin/env python3
import argparse
import json
import pathlib
import re


REQUIRED_CASE_FILES = {
    "good": [
        pathlib.Path("evaluation/cases/good/01-order-consistency.md"),
        pathlib.Path("evaluation/cases/good/02-event-pipeline.md"),
        pathlib.Path("evaluation/cases/good/03-database-choice.md"),
        pathlib.Path("evaluation/cases/good/04-replica-lag.md"),
        pathlib.Path("evaluation/cases/good/05-derived-data.md"),
        pathlib.Path("evaluation/cases/good/06-quantitative-workload-capacity.md"),
        pathlib.Path("evaluation/cases/good/07-batch-backfill-reconciliation.md"),
        pathlib.Path("evaluation/cases/good/08-schema-evolution-rollout.md"),
        pathlib.Path("evaluation/cases/good/09-correct-cache-use.md"),
        pathlib.Path("evaluation/cases/good/10-observability-runbook.md"),
        pathlib.Path("evaluation/cases/good/11-idempotency-outbox.md"),
    ],
    "bad": [
        pathlib.Path("evaluation/cases/bad/01-cache-as-truth.md"),
        pathlib.Path("evaluation/cases/bad/02-replica-lag-denial.md"),
        pathlib.Path("evaluation/cases/bad/03-hot-partition.md"),
        pathlib.Path("evaluation/cases/bad/04-vague-startup-architecture.md"),
        pathlib.Path("evaluation/cases/bad/05-capacity-cost-handwave.md"),
    ],
    "adversarial": [
        pathlib.Path("evaluation/cases/adversarial/01-tool-first-trap.md"),
        pathlib.Path("evaluation/cases/adversarial/02-exactly-once-trap.md"),
        pathlib.Path("evaluation/cases/adversarial/03-distributed-lock-trap.md"),
        pathlib.Path("evaluation/cases/adversarial/04-schema-evolution-trap.md"),
        pathlib.Path("evaluation/cases/adversarial/05-global-linearizable-writes.md"),
    ],
}
EXPECTED_CASE_COUNTS = {category: len(paths) for category, paths in REQUIRED_CASE_FILES.items()}
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
    "Coverage Matrix",
    "How To Run",
    "How To Score",
    "Regression Review",
]
COVERAGE_MATRIX_TOPIC_REQUIREMENTS = {
    "good/03-database-choice.md": "Storage and database choice",
    "good/08-schema-evolution-rollout.md": "Schema evolution and compatibility",
    "adversarial/04-schema-evolution-trap.md": "Schema evolution and compatibility",
    "bad/03-hot-partition.md": "Partitioning and hot spots",
    "adversarial/03-distributed-lock-trap.md": "Transactions, coordination, and consensus",
}

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

CODING_AB_CASES = {
    "good-cache-aside-product-preview": "good",
    "good-outbox-relay-idempotent-consumer": "good",
    "good-replica-session-token-routing": "good",
    "good-expand-contract-schema-rollout": "good",
    "checkout-cache-as-truth": "bad",
    "order-outbox-missing": "bad",
    "profile-replica-lag": "bad",
    "seat-booking-write-skew": "bad",
    "schema-migration-breaking-reader": "bad",
    "stream-consumer-non-idempotent": "bad",
    "hot-partition-tenant-counter": "bad",
    "retry-storm-no-dlq": "bad",
    "missing-reconciliation-observability": "bad",
    "payment-exactly-once-trap": "adversarial",
    "redis-distributed-lock-money-transfer": "adversarial",
    "multi-region-last-write-wins-profile": "adversarial",
    "elasticsearch-authorization-trap": "adversarial",
    "kafka-total-ordering-trap": "adversarial",
}
CODING_AB_EXPECTED_CATEGORY_COUNTS = {"good": 4, "bad": 9, "adversarial": 5}
CODING_AB_COVERAGE_MATRIX_PATH = "evaluation/coding-ab/coverage-matrix.md"
CODING_AB_REQUIRED_TOPICS = {
    "Correct cache use",
    "Source-of-truth boundary",
    "Transactional outbox",
    "Idempotent consumer",
    "Read-your-writes",
    "Replica lag",
    "Isolation and write skew",
    "Schema evolution",
    "Stream replay and duplicate delivery",
    "Partitioning and hot keys",
    "Backpressure and poison messages",
    "Observability and reconciliation",
    "External side effects",
    "Distributed locks and fencing",
    "Multi-region conflict resolution",
    "Derived data authorization",
    "Ordering guarantees",
}
CODING_AB_REQUIRED_FILES = [
    "evaluation/coding-ab/README.md",
    "evaluation/coding-ab/control-instructions.md",
    "evaluation/coding-ab/treatment-instructions.md",
    "evaluation/coding-ab/blind-llm-judge.md",
    "evaluation/coding-ab/results-template.md",
    CODING_AB_COVERAGE_MATRIX_PATH,
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


def required_case_refs() -> set[str]:
    prefix = pathlib.Path("evaluation/cases")
    return {case.relative_to(prefix).as_posix() for paths in REQUIRED_CASE_FILES.values() for case in paths}


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


def markdown_table_rows(body: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in body.splitlines():
        cells = markdown_table_cells(line)
        if cells is not None:
            rows.append(cells)
    return rows


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
    score_row_case_counts: dict[str, int] = {}
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

        score_row_case_counts[case] = score_row_case_counts.get(case, 0) + 1
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
    for case_slug, count in score_row_case_counts.items():
        if case_slug not in expected_score_slug_set:
            errors.append(f"{relative}: unexpected score row for {case_slug}")
            continue
        if count != 1:
            errors.append(f"{relative}: duplicate score row for {case_slug}")

    for case_slug in expected_score_slugs:
        if case_slug not in score_row_case_counts:
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


def parse_coverage_matrix_refs(text: str) -> dict[str, list[str]]:
    matrix_body = section_body(text, "Coverage Matrix") or ""
    matrix_refs: dict[str, list[str]] = {}

    for line in matrix_body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- ") or ":" not in stripped:
            continue

        topic, refs_text = stripped[2:].split(":", 1)
        matrix_refs.setdefault(topic.strip(), []).extend(re.findall(r"`([^`]+)`", refs_text))

    return matrix_refs


def validate_coverage_matrix(path: pathlib.Path, relative: str) -> list[str]:
    text = read_text(path)
    if section_body(text, "Coverage Matrix") is None:
        return []

    errors: list[str] = []
    expected_refs = required_case_refs()
    refs_by_topic = parse_coverage_matrix_refs(text)
    ref_counts: dict[str, int] = {}

    for refs in refs_by_topic.values():
        for ref in refs:
            ref_counts[ref] = ref_counts.get(ref, 0) + 1

    for ref in sorted(expected_refs):
        if ref_counts.get(ref, 0) == 0:
            errors.append(f"{relative}: coverage matrix missing case {ref}")
        elif ref_counts[ref] > 1:
            errors.append(f"{relative}: coverage matrix duplicates case {ref}")

    for ref in sorted(ref for ref in ref_counts if ref not in expected_refs):
        errors.append(f"{relative}: coverage matrix unknown case {ref}")

    for ref, topic in sorted(COVERAGE_MATRIX_TOPIC_REQUIREMENTS.items()):
        if ref not in refs_by_topic.get(topic, []):
            errors.append(f"{relative}: coverage matrix must list {ref} under {topic}")

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


def validate_coding_ab_coverage_matrix(path: pathlib.Path, relative: str) -> list[str]:
    text = read_text(path)
    errors: list[str] = []
    covered_cases: set[str] = set()
    covered_topics: set[str] = set()
    coverage_row_counts: dict[str, int] = {}

    matrix_body = section_body(text, "Coverage Matrix")
    if matrix_body is None:
        return [f"{relative}: missing section Coverage Matrix"]

    for row in markdown_table_rows(matrix_body):
        if len(row) < 3:
            errors.append(f"{relative}: malformed coverage row for {row[0] if row else '<unknown>'}")
            continue
        case_id = row[0]
        category = row[1]
        topics = {topic.strip() for topic in row[2].split(",") if topic.strip()}
        if case_id not in CODING_AB_CASES:
            errors.append(f"{relative}: unknown coding case {case_id}")
            continue
        expected_category = CODING_AB_CASES[case_id]
        if category != expected_category:
            errors.append(f"{relative}: {case_id} expected category {expected_category}, found {category}")
        coverage_row_counts[case_id] = coverage_row_counts.get(case_id, 0) + 1
        if coverage_row_counts[case_id] > 1:
            errors.append(f"{relative}: duplicate coverage row for {case_id}")
        covered_cases.add(case_id)
        covered_topics.update(topics)

    for case_id in CODING_AB_CASES:
        if case_id not in covered_cases:
            errors.append(f"{relative}: missing coverage row for {case_id}")

    for topic in CODING_AB_REQUIRED_TOPICS:
        if topic not in covered_topics:
            errors.append(f"{relative}: missing coverage topic {topic}")

    for topic in sorted(covered_topics - CODING_AB_REQUIRED_TOPICS):
        errors.append(f"{relative}: unknown coverage topic {topic}")

    return errors


def validate_coding_ab_category_counts(relative: str = "coding_ab_registry") -> list[str]:
    counts = {"good": 0, "bad": 0, "adversarial": 0}
    errors: list[str] = []
    for category in CODING_AB_CASES.values():
        if category not in counts:
            errors.append(f"{relative}: unknown coding category {category}")
            continue
        counts[category] += 1

    if counts != CODING_AB_EXPECTED_CATEGORY_COUNTS:
        errors.append(f"{relative}: expected category counts {CODING_AB_EXPECTED_CATEGORY_COUNTS}, found {counts}")
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

    errors.extend(validate_coding_ab_category_counts())

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

    coverage_matrix = repo / CODING_AB_COVERAGE_MATRIX_PATH
    if coverage_matrix.exists():
        errors.extend(validate_coding_ab_coverage_matrix(coverage_matrix, CODING_AB_COVERAGE_MATRIX_PATH))

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

    for category, directory in CASE_DIRS.items():
        case_dir = repo / directory
        case_files = sorted(case_dir.glob("*.md")) if case_dir.exists() else []
        case_counts[category] = len(case_files)
        relative_dir = directory.as_posix()

        for required_case in REQUIRED_CASE_FILES[category]:
            if not (repo / required_case).exists():
                case_errors.append(f"{required_case.as_posix()}: missing required case")

        if not case_dir.exists():
            missing_paths.append(relative_dir)
        expected_count = EXPECTED_CASE_COUNTS[category]
        if len(case_files) != expected_count:
            case_errors.append(f"{relative_dir}: expected {expected_count} cases, found {len(case_files)}")

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
        guide_errors.extend(validate_coverage_matrix(guide_path, GUIDE_PATH))

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
