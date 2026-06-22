#!/usr/bin/env python3
import argparse
import hashlib
import json
import pathlib
import random
import shutil
import subprocess
import sys
from datetime import datetime

from check_ddia_benchmark import CODING_AB_CASES, validate_coding_ab_judge_result_payload
from render_coding_ab_prompt import render_prompt


DEFAULT_MODEL = "gpt-5.3-codex-spark"
DEFAULT_REASONING_EFFORT = "high"
SCORE_KEYS = [
    "correctness_invariant",
    "source_of_truth_boundary",
    "failure_mode_handling",
    "idempotency_retry_safety",
    "operational_verification",
    "java_patch_quality",
    "anti_pattern_resistance",
]
BASE_SCORE_KEYS = [key for key in SCORE_KEYS if key != "anti_pattern_resistance"]
JUDGE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["case_id", "category", "response_a", "response_b", "winner", "rationale"],
    "properties": {
        "case_id": {"type": "string"},
        "category": {"type": "string", "enum": ["good", "bad", "adversarial"]},
        "response_a": {"$ref": "#/$defs/response"},
        "response_b": {"$ref": "#/$defs/response"},
        "winner": {"type": "string", "enum": ["A", "B", "tie"]},
        "rationale": {"type": "string"},
    },
    "$defs": {
        "scores": {
            "type": "object",
            "additionalProperties": False,
            "required": SCORE_KEYS,
            "properties": {
                "correctness_invariant": {"type": "integer", "enum": [0, 1, 2]},
                "source_of_truth_boundary": {"type": "integer", "enum": [0, 1, 2]},
                "failure_mode_handling": {"type": "integer", "enum": [0, 1, 2]},
                "idempotency_retry_safety": {"type": "integer", "enum": [0, 1, 2]},
                "operational_verification": {"type": "integer", "enum": [0, 1, 2]},
                "java_patch_quality": {"type": "integer", "enum": [0, 1, 2]},
                "anti_pattern_resistance": {
                    "anyOf": [{"type": "integer", "enum": [0, 1, 2]}, {"type": "null"}]
                },
            },
        },
        "response": {
            "type": "object",
            "additionalProperties": False,
            "required": ["scores", "rationale"],
            "properties": {
                "scores": {"$ref": "#/$defs/scores"},
                "rationale": {"type": "string"},
            },
        },
    },
}


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: pathlib.Path) -> object:
    return json.loads(read_text(path))


def write_json(path: pathlib.Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2, sort_keys=False) + "\n")


def case_id_for_path(case_path: pathlib.Path) -> str:
    return case_path.stem


def git_commit(repo: pathlib.Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def category_for_case(case_id: str) -> str:
    try:
        return CODING_AB_CASES[case_id]
    except KeyError as exc:
        raise ValueError(f"unknown coding A/B case: {case_id}") from exc


def denominator(category: str) -> int:
    return 14 if category == "adversarial" else 12


def computed_pass(category: str, scores: dict[str, int | None]) -> bool:
    base_scores = [scores[key] for key in BASE_SCORE_KEYS]
    if not all(isinstance(score, int) for score in base_scores):
        return False
    total = sum(score for score in base_scores if isinstance(score, int))
    anti_pattern = scores["anti_pattern_resistance"]
    if category == "adversarial":
        if not isinstance(anti_pattern, int):
            return False
        total += anti_pattern
        return total >= 12 and all(score > 0 for score in base_scores) and anti_pattern == 2
    return total >= 10 and all(score > 0 for score in base_scores)


def normalize_response(category: str, response: dict[str, object]) -> dict[str, object]:
    scores = response["scores"]
    if not isinstance(scores, dict):
        raise ValueError("judge response scores must be an object")
    total = sum(score for score in scores.values() if isinstance(score, int))
    return {
        "scores": scores,
        "total": total,
        "denominator": denominator(category),
        "pass": computed_pass(category, scores),
        "rationale": response["rationale"],
    }


def normalize_judge_payload(payload: dict[str, object], case_id: str, category: str) -> dict[str, object]:
    result = {
        "case_id": case_id,
        "category": category,
        "response_a": normalize_response(category, payload["response_a"]),
        "response_b": normalize_response(category, payload["response_b"]),
        "winner": payload["winner"],
        "rationale": payload["rationale"],
    }
    errors = validate_coding_ab_judge_result_payload(result)
    if errors:
        raise ValueError("invalid judge payload after normalization: " + "; ".join(errors))
    return result


def codex_command(
    *,
    repo: pathlib.Path,
    model: str,
    reasoning_effort: str,
    output_path: pathlib.Path,
    schema_path: pathlib.Path | None = None,
) -> list[str]:
    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--sandbox",
        "read-only",
        "-m",
        model,
        "-c",
        f'model_reasoning_effort="{reasoning_effort}"',
        "-C",
        str(repo),
        "-o",
        str(output_path),
    ]
    if schema_path is not None:
        command.extend(["--output-schema", str(schema_path)])
    command.append("-")
    return command


def run_codex(
    *,
    repo: pathlib.Path,
    prompt: str,
    output_path: pathlib.Path,
    log_path: pathlib.Path,
    model: str,
    reasoning_effort: str,
    schema_path: pathlib.Path | None = None,
    force: bool = False,
    timeout_seconds: int = 900,
) -> None:
    if output_path.exists() and read_text(output_path).strip() and not force:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    command = codex_command(
        repo=repo,
        model=model,
        reasoning_effort=reasoning_effort,
        output_path=output_path,
        schema_path=schema_path,
    )
    completed = subprocess.run(
        command,
        input=prompt,
        cwd=repo,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
    )
    log = [
        "$ " + " ".join(command[:-1]) + " -",
        "",
        "## stdout",
        completed.stdout,
        "",
        "## stderr",
        completed.stderr,
        "",
        f"exit_code: {completed.returncode}",
    ]
    write_text(log_path, "\n".join(log))
    if completed.returncode != 0:
        raise RuntimeError(f"codex exec failed for {output_path}; see {log_path}")
    if not output_path.exists() or not read_text(output_path).strip():
        raise RuntimeError(f"codex exec did not write {output_path}; see {log_path}")


def judge_prompt(
    *,
    case_text: str,
    rubric_text: str,
    response_a: str,
    response_b: str,
    case_id: str,
    category: str,
) -> str:
    return f"""You are the blind LLM judge for a DDIA coding A/B benchmark.

Score Response A and Response B before any mapping is revealed. You must not
guess, mention, or output which response is control or treatment.

Return JSON that matches the provided schema. Do not include Markdown.

Case ID: {case_id}
Category: {category}

Important scoring rules:
- For good and bad coding cases, set anti_pattern_resistance to null.
- For adversarial coding cases, score anti_pattern_resistance as 0, 1, or 2.
- Score only observable reasoning and Java patch quality.
- Do not reward a response for naming ddia-system-design.
- Prefer practical correctness over broad conceptual prose.

## Rubric

{rubric_text}

## Full Case, Including Judge-Only Notes

{case_text}

## Response A

{response_a}

## Response B

{response_b}
"""


def mapping_for_case(seed: str, case_id: str) -> dict[str, str]:
    rng_seed = int(hashlib.sha256(f"{seed}:{case_id}".encode("utf-8")).hexdigest(), 16)
    arms = ["control", "treatment"]
    random.Random(rng_seed).shuffle(arms)
    return {"A": arms[0], "B": arms[1]}


def response_for_letter(mapping: dict[str, str], letter: str, control: str, treatment: str) -> str:
    return control if mapping[letter] == "control" else treatment


def run_case(
    *,
    repo: pathlib.Path,
    run_dir: pathlib.Path,
    case_path: pathlib.Path,
    skill_path: pathlib.Path,
    rubric_text: str,
    schema_path: pathlib.Path,
    seed: str,
    model: str,
    reasoning_effort: str,
    force: bool,
) -> dict[str, object]:
    case_id = case_id_for_path(case_path)
    category = category_for_case(case_id)
    case_dir = run_dir / "cases" / case_id
    case_text = read_text(case_path)
    control_prompt = render_prompt(repo=repo, case_path=case_path, arm="control", skill_path=skill_path)
    treatment_prompt = render_prompt(repo=repo, case_path=case_path, arm="treatment", skill_path=skill_path)

    write_text(case_dir / "control-prompt.md", control_prompt)
    write_text(case_dir / "treatment-prompt.md", treatment_prompt)
    run_codex(
        repo=repo,
        prompt=control_prompt,
        output_path=case_dir / "control-response.md",
        log_path=case_dir / "control-codex.log",
        model=model,
        reasoning_effort=reasoning_effort,
        force=force,
    )
    run_codex(
        repo=repo,
        prompt=treatment_prompt,
        output_path=case_dir / "treatment-response.md",
        log_path=case_dir / "treatment-codex.log",
        model=model,
        reasoning_effort=reasoning_effort,
        force=force,
    )

    mapping = mapping_for_case(seed, case_id)
    write_text(case_dir / "mapping.txt", f"Response A: {mapping['A']}\nResponse B: {mapping['B']}\n")
    control_response = read_text(case_dir / "control-response.md")
    treatment_response = read_text(case_dir / "treatment-response.md")
    prompt = judge_prompt(
        case_text=case_text,
        rubric_text=rubric_text,
        response_a=response_for_letter(mapping, "A", control_response, treatment_response),
        response_b=response_for_letter(mapping, "B", control_response, treatment_response),
        case_id=case_id,
        category=category,
    )
    write_text(case_dir / "blind-judge-prompt.md", prompt)
    run_codex(
        repo=repo,
        prompt=prompt,
        output_path=case_dir / "blind-judge-raw.json",
        log_path=case_dir / "blind-judge-codex.log",
        model=model,
        reasoning_effort=reasoning_effort,
        schema_path=schema_path,
        force=force,
    )

    raw_payload = load_json(case_dir / "blind-judge-raw.json")
    if not isinstance(raw_payload, dict):
        raise ValueError(f"{case_id}: judge raw output is not a JSON object")
    normalized = normalize_judge_payload(raw_payload, case_id, category)
    write_json(case_dir / "blind-judge-result.json", normalized)

    response_by_arm = {
        "control": normalized["response_a"] if mapping["A"] == "control" else normalized["response_b"],
        "treatment": normalized["response_a"] if mapping["A"] == "treatment" else normalized["response_b"],
    }
    control_result = response_by_arm["control"]
    treatment_result = response_by_arm["treatment"]
    if not isinstance(control_result, dict) or not isinstance(treatment_result, dict):
        raise ValueError(f"{case_id}: invalid normalized response shape")

    control_total = int(control_result["total"])
    treatment_total = int(treatment_result["total"])
    max_score = denominator(category)
    lift = treatment_total - control_total
    normalized_lift = (treatment_total / max_score) - (control_total / max_score)
    if lift > 0:
        score_winner = "treatment"
    elif lift < 0:
        score_winner = "control"
    else:
        score_winner = "tie"

    judge_winner = normalized["winner"]
    if judge_winner == "A":
        judge_winner_arm = mapping["A"]
    elif judge_winner == "B":
        judge_winner_arm = mapping["B"]
    else:
        judge_winner_arm = "tie"

    case_summary = {
        "case_id": case_id,
        "category": category,
        "mapping": mapping,
        "control_total": control_total,
        "treatment_total": treatment_total,
        "denominator": max_score,
        "control_pass": bool(control_result["pass"]),
        "treatment_pass": bool(treatment_result["pass"]),
        "lift": lift,
        "normalized_lift": normalized_lift,
        "score_winner": score_winner,
        "judge_winner": judge_winner_arm,
        "control_rationale": control_result["rationale"],
        "treatment_rationale": treatment_result["rationale"],
        "judge_rationale": normalized["rationale"],
    }
    write_json(case_dir / "case-summary.json", case_summary)
    return case_summary


def markdown_table(rows: list[dict[str, object]]) -> str:
    lines = [
        "| Case | Category | Control | Treatment | Lift | Pass/fail change | Score winner | Judge winner |",
        "| --- | --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in rows:
        control_score = f"{row['control_total']}/{row['denominator']}"
        treatment_score = f"{row['treatment_total']}/{row['denominator']}"
        if row["control_pass"] == row["treatment_pass"]:
            pass_change = "both pass" if row["control_pass"] else "both fail"
        elif row["treatment_pass"]:
            pass_change = "control fail -> treatment pass"
        else:
            pass_change = "control pass -> treatment fail"
        lines.append(
            "| {case_id} | {category} | {control_score} | {treatment_score} | {lift:+d} | "
            "{pass_change} | {score_winner} | {judge_winner} |".format(
                case_id=row["case_id"],
                category=row["category"],
                control_score=control_score,
                treatment_score=treatment_score,
                lift=row["lift"],
                pass_change=pass_change,
                score_winner=row["score_winner"],
                judge_winner=row["judge_winner"],
            )
        )
    return "\n".join(lines)


def aggregate(rows: list[dict[str, object]]) -> dict[str, object]:
    control_total = sum(int(row["control_total"]) for row in rows)
    treatment_total = sum(int(row["treatment_total"]) for row in rows)
    max_total = sum(int(row["denominator"]) for row in rows)
    category_counts: dict[str, dict[str, int]] = {}
    for row in rows:
        category = str(row["category"])
        category_counts.setdefault(
            category,
            {
                "cases": 0,
                "control_total": 0,
                "treatment_total": 0,
                "max_total": 0,
                "control_passes": 0,
                "treatment_passes": 0,
                "treatment_wins": 0,
                "control_wins": 0,
                "ties": 0,
            },
        )
        bucket = category_counts[category]
        bucket["cases"] += 1
        bucket["control_total"] += int(row["control_total"])
        bucket["treatment_total"] += int(row["treatment_total"])
        bucket["max_total"] += int(row["denominator"])
        bucket["control_passes"] += int(bool(row["control_pass"]))
        bucket["treatment_passes"] += int(bool(row["treatment_pass"]))
        bucket["treatment_wins"] += int(row["score_winner"] == "treatment")
        bucket["control_wins"] += int(row["score_winner"] == "control")
        bucket["ties"] += int(row["score_winner"] == "tie")

    return {
        "cases": len(rows),
        "control_total": control_total,
        "treatment_total": treatment_total,
        "max_total": max_total,
        "lift": treatment_total - control_total,
        "control_normalized": control_total / max_total if max_total else 0,
        "treatment_normalized": treatment_total / max_total if max_total else 0,
        "normalized_lift": (treatment_total - control_total) / max_total if max_total else 0,
        "control_passes": sum(int(bool(row["control_pass"])) for row in rows),
        "treatment_passes": sum(int(bool(row["treatment_pass"])) for row in rows),
        "treatment_wins": sum(int(row["score_winner"] == "treatment") for row in rows),
        "control_wins": sum(int(row["score_winner"] == "control") for row in rows),
        "ties": sum(int(row["score_winner"] == "tie") for row in rows),
        "judge_treatment_wins": sum(int(row["judge_winner"] == "treatment") for row in rows),
        "judge_control_wins": sum(int(row["judge_winner"] == "control") for row in rows),
        "judge_ties": sum(int(row["judge_winner"] == "tie") for row in rows),
        "by_category": category_counts,
    }


def format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def write_summary(
    *,
    run_dir: pathlib.Path,
    rows: list[dict[str, object]],
    model: str,
    reasoning_effort: str,
    commit: str,
    seed: str,
) -> None:
    totals = aggregate(rows)
    write_json(run_dir / "results.json", {"metadata": {"model": model, "reasoning_effort": reasoning_effort, "commit": commit, "seed": seed}, "aggregate": totals, "cases": rows})

    category_lines = [
        "| Category | Cases | Control | Treatment | Lift | Control passes | Treatment passes | Treatment wins | Control wins | Ties |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for category in ["good", "bad", "adversarial"]:
        bucket = totals["by_category"].get(category)
        if not bucket:
            continue
        category_lines.append(
            "| {category} | {cases} | {control}/{max_total} | {treatment}/{max_total} | {lift:+d} | "
            "{control_passes} | {treatment_passes} | {treatment_wins} | {control_wins} | {ties} |".format(
                category=category,
                cases=bucket["cases"],
                control=bucket["control_total"],
                treatment=bucket["treatment_total"],
                max_total=bucket["max_total"],
                lift=bucket["treatment_total"] - bucket["control_total"],
                control_passes=bucket["control_passes"],
                treatment_passes=bucket["treatment_passes"],
                treatment_wins=bucket["treatment_wins"],
                control_wins=bucket["control_wins"],
                ties=bucket["ties"],
            )
        )

    summary = f"""# Full DDIA Coding A/B Run

## Run Metadata

- Date: {datetime.now().strftime("%Y-%m-%d")}
- Commit: {commit}
- Model: {model}
- Reasoning effort: {reasoning_effort}
- Cases: {totals["cases"]}
- Shuffle seed: `{seed}`
- Answer runner: `codex exec --ephemeral --ignore-user-config --ignore-rules --sandbox read-only`
- Judge runner: same model and settings, blind to control/treatment mapping

## Aggregate Result

- Control total: {totals["control_total"]}/{totals["max_total"]} ({format_percent(totals["control_normalized"])})
- Treatment total: {totals["treatment_total"]}/{totals["max_total"]} ({format_percent(totals["treatment_normalized"])})
- Absolute lift: {totals["lift"]:+d}/{totals["max_total"]} ({format_percent(totals["normalized_lift"])} points)
- Control passes: {totals["control_passes"]}/{totals["cases"]}
- Treatment passes: {totals["treatment_passes"]}/{totals["cases"]}
- Score winners: treatment {totals["treatment_wins"]}, control {totals["control_wins"]}, tie {totals["ties"]}
- Blind judge winner labels after reveal: treatment {totals["judge_treatment_wins"]}, control {totals["judge_control_wins"]}, tie {totals["judge_ties"]}

## Category Breakdown

{chr(10).join(category_lines)}

## Case Scores

{markdown_table(rows)}

## Artifacts

Each case directory under `cases/` contains:

- `control-response.md`
- `treatment-response.md`
- `blind-judge-raw.json`
- `blind-judge-result.json`
- `mapping.txt`
- `case-summary.json`
- rendered answer prompts and the blind judge prompt
- Codex command logs

## Limitations

- One model only.
- One sample per arm per case.
- The same model family generated and judged the answers.
- The judge was blind to control/treatment mapping, but not independent of the answer model.
- No Java compilation was required; the judge scored patch quality from code snippets and explanation.
"""
    write_text(run_dir / "README.md", summary)


def selected_cases(repo: pathlib.Path, names: list[str]) -> list[pathlib.Path]:
    case_dir = repo / "evaluation/coding-ab/cases"
    all_cases = sorted(case_dir.glob("*.md"))
    if not names:
        return all_cases
    by_id = {path.stem: path for path in all_cases}
    cases = []
    for name in names:
        case_id = pathlib.Path(name).stem
        if case_id not in by_id:
            raise ValueError(f"unknown case: {name}")
        cases.append(by_id[case_id])
    return cases


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--reasoning-effort", default=DEFAULT_REASONING_EFFORT)
    parser.add_argument("--seed", default="ddia-coding-ab-2026-06-22")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    if shutil.which("codex") is None:
        raise SystemExit("codex executable not found")

    run_id = args.run_id or f"{datetime.now().strftime('%Y-%m-%d')}-full-18-case-coding-ab"
    run_dir = repo / "evaluation/coding-ab/runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    schema_path = run_dir / "judge-output-schema.json"
    write_json(schema_path, JUDGE_SCHEMA)

    commit = git_commit(repo)
    rubric_text = read_text(repo / "evaluation/coding-ab/blind-llm-judge.md")
    skill_path = repo / "skills/ddia-system-design/SKILL.md"
    cases = selected_cases(repo, args.case)
    rows = []
    for index, case_path in enumerate(cases, start=1):
        case_id = case_id_for_path(case_path)
        print(f"[{index}/{len(cases)}] {case_id}", flush=True)
        rows.append(
            run_case(
                repo=repo,
                run_dir=run_dir,
                case_path=case_path,
                skill_path=skill_path,
                rubric_text=rubric_text,
                schema_path=schema_path,
                seed=args.seed,
                model=args.model,
                reasoning_effort=args.reasoning_effort,
                force=args.force,
            )
        )
        write_summary(
            run_dir=run_dir,
            rows=rows,
            model=args.model,
            reasoning_effort=args.reasoning_effort,
            commit=commit,
            seed=args.seed,
        )

    write_summary(
        run_dir=run_dir,
        rows=rows,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        commit=commit,
        seed=args.seed,
    )
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
