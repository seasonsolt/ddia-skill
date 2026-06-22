#!/usr/bin/env python3
import argparse
import pathlib
import sys


ANSWER_VISIBLE_SECTIONS = ["Scenario", "Flawed Java", "Task"]
ANSWER_VISIBLE_HEADINGS = {"Flawed Java": "Java Code"}
ARM_INSTRUCTIONS = {
    "control": "evaluation/coding-ab/control-instructions.md",
    "treatment": "evaluation/coding-ab/treatment-instructions.md",
}


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def section_body(text: str, heading: str) -> str:
    marker = f"## {heading}"
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            body = []
            for body_line in lines[index + 1 :]:
                if body_line.startswith("## "):
                    break
                body.append(body_line)
            return "\n".join(body).strip()
    raise ValueError(f"missing section {heading}")


def render_case_for_answer_model(case_text: str) -> str:
    rendered = []
    for source_heading in ANSWER_VISIBLE_SECTIONS:
        visible_heading = ANSWER_VISIBLE_HEADINGS.get(source_heading, source_heading)
        rendered.append(f"## {visible_heading}")
        rendered.append(section_body(case_text, source_heading))
    return "\n\n".join(rendered).strip() + "\n"


def render_prompt(
    *,
    repo: pathlib.Path,
    case_path: pathlib.Path,
    arm: str,
    skill_path: pathlib.Path,
) -> str:
    if arm not in ARM_INSTRUCTIONS:
        raise ValueError(f"arm must be one of {sorted(ARM_INSTRUCTIONS)}")

    parts = [
        "You are participating in a coding A/B benchmark.",
        "Do not edit files, do not run commands, and do not mention this benchmark setup.",
        "Produce the answer only.",
        read_text(repo / ARM_INSTRUCTIONS[arm]).strip(),
    ]
    if arm == "treatment":
        parts.append("# ddia-system-design skill instructions\n\n" + read_text(skill_path).strip())

    parts.append(render_case_for_answer_model(read_text(case_path)).strip())
    return "\n\n".join(parts).strip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--case", type=pathlib.Path, required=True)
    parser.add_argument("--arm", choices=sorted(ARM_INSTRUCTIONS), required=True)
    parser.add_argument(
        "--skill-path",
        type=pathlib.Path,
        default=pathlib.Path("skills/ddia-system-design/SKILL.md"),
    )
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    case_path = args.case if args.case.is_absolute() else repo / args.case
    skill_path = args.skill_path if args.skill_path.is_absolute() else repo / args.skill_path

    sys.stdout.write(render_prompt(repo=repo, case_path=case_path, arm=args.arm, skill_path=skill_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
