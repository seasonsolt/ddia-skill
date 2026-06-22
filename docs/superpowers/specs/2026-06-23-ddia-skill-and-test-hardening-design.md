# DDIA Skill And Test Hardening Design

## Goal

Close the twelve open deferred gaps from the credibility-hardening plan and fix
the four review-flagged issues, so the repository has no known open gaps from
the first deep review.

## Scope

In scope:

- Fix README case-count drift and declare the Python version requirement.
- Document why the A/B pilot is frozen at five cases.
- Add a worked example, a narrow-follow-up exemption, and explicit off-topic
  boundaries to `SKILL.md`.
- Reduce repeated concept duplication across the three reference files.
- Document the role of `agents/openai.yaml` and cover it with a test.
- Document the relation between `evaluation/rubric.md` and
  `evaluation/rubrics/answer-quality.md`.
- Document the split between skill behavior tests and reading/PDF tests.
- Remove the hardcoded PDF path fallback from the extraction test.
- Loosen `prompt_count == 5` to a minimum and document the heading-coupling
  intent.
- Add a behavior-contract regression test for the skill instructions.

Out of scope:

- Running a new repeated A/B study.
- Adding new benchmark cases.
- Automated LLM judging.

## Items

### Review-flagged fixes

1. README case count says `13 cases: 5/4/4` but the benchmark now has
   `21 cases: 11/5/5`. Two places in `README.md` need updating.
2. `README.md` does not declare the Python version requirement even though the
   checker uses `str | None` union syntax that requires Python 3.10 or newer.
3. `evaluation/ab/README.md` does not explain why the pilot is frozen at five
   cases or when new cases enter.
4. The twelve open deferred gaps need a tracking plan; this spec and its plan
   are that tracking.

### Deferred skill gaps

5. `agents/openai.yaml` has no documented role and no test coverage.
6. `SKILL.md` has no worked example to calibrate output granularity.
7. `SKILL.md` has no narrow-follow-up exemption, so the seven-section shape can
   pad small answers.
8. `SKILL.md` has no explicit off-topic boundaries.
9. The three reference files repeat concepts (`derived data` handling,
   `workload` framing) in prose across principles and checklists.

### Deferred test infrastructure gaps

10. No behavior-oriented regression evidence; all tests are structural.
11. `check_ddia_skill_quality.py` hard-locks `prompt_count == 5`, blocking
    prompt growth.
12. Heading-coupling in regression guards is not documented as intentional.
13. `agents/openai.yaml` is not covered by any test.
14. Reading/PDF extraction tests are not documented as separate from skill
    behavior tests.
15. `evaluation/rubric.md` and `evaluation/rubrics/answer-quality.md` coexist
    with no documented relationship.
16. `tests/test_extract_ddia_structure.py` hardcodes a developer-local PDF path
    fallback.

## Success Criteria

This pass is successful when:

- README case counts and validation status match the actual benchmark.
- README declares the Python 3.10+ requirement.
- `evaluation/ab/README.md` explains the frozen pilot set.
- `SKILL.md` has a worked example, a narrow-follow-up exemption, and off-topic
  boundaries.
- Reference files keep their required sections and role terms but reduce prose
  overlap.
- `agents/openai.yaml` has a documented role and a test.
- `evaluation/rubrics/README.md` documents the two rubrics.
- `tests/README.md` documents the two test groups.
- `tests/test_extract_ddia_structure.py` skips PDF-dependent tests when
  `DDIA_PDF_PATH` is unset instead of falling back to a developer path.
- `check_ddia_skill_quality.py` accepts `prompt_count >= 5` and documents why
  heading lists are intentional regression guards.
- A behavior-contract test verifies the skill instructions are internally
  consistent and complete.
- The full unit suite and both checkers pass.
