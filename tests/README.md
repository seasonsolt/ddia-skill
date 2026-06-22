# DDIA Test Suite

The test suite has two groups that serve different purposes and can be run
separately.

## Skill Behavior And Benchmark Tests

These tests validate the `ddia-system-design` skill package and the benchmark
assets. They do not require the DDIA PDF and run in any environment with Python
3.10+.

- `test_ddia_skill_content.py` - skill frontmatter, reference coverage, and
  `agents/openai.yaml` interface.
- `test_ddia_skill_quality.py` - structural quality checker for skill files,
  rubric, prompts, and results template.
- `test_ddia_skill_behavior.py` - behavior-contract checks for response shape,
  narrow follow-ups, guardrails, scope boundaries, and worked examples.
- `test_ddia_benchmark.py` - benchmark case library, rubrics, A/B assets, and
  score arithmetic validation.

Run alone:

```bash
python3 -m unittest tests.test_ddia_skill_content tests.test_ddia_skill_quality tests.test_ddia_skill_behavior tests.test_ddia_benchmark
```

## Reading And PDF Extraction Tests

These tests validate the private reading tools used to build the skill from the
local DDIA PDF. They are not related to skill behavior at runtime.

- `test_ddia_reading_ledger.py` - reading ledger renderer and completeness
  checker.
- `test_extract_ddia_structure.py` - PDF outline extraction. Tests that need the
  actual PDF skip when the `DDIA_PDF_PATH` environment variable is unset.
- `test_extract_ddia_text_for_private_notes.py` - private page-text extraction
  and output guards.

Run alone:

```bash
python3 -m unittest tests.test_ddia_reading_ledger tests.test_extract_ddia_structure tests.test_extract_ddia_text_for_private_notes
```

## Running Everything

```bash
python3 -m unittest discover -s tests
```

The bundled codex runtime provides Python 3.12.13, which satisfies the
`str | None` union syntax used by the checkers.
