# DDIA Skill Benchmark Results

Copy this file to `evaluation/results/YYYY-MM-DD-<commit>.md` for each benchmark run, then replace each instruction sentence with the recorded value for that run.

## Run Metadata

- Evaluator: write the evaluator name.
- Date: write the run date in YYYY-MM-DD format.
- Skill version: write the Git commit or skill version.
- Skill path: /Users/Thin/Documents/ddia/skills/ddia-system-design

## Answer Quality

| Case | Category | Pass mode | Workload | Trade-offs | Failure modes | Correctness | Verification | Anti-pattern | Total | Pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Add one row per benchmark case. | Use good, bad, or adversarial. | Use must-pass or diagnostic-only. | Score 0-2. | Score 0-2. | Score 0-2. | Score 0-2. | Score 0-2. | Score 0-2 or N/A. | Sum scored dimensions. | Use yes or no. |

## Process Compliance

| Case | Skill material usage | Assumption framing | Missing requirement questions | Response structure | Verification conversion | Total |
| --- | --- | --- | --- | --- | --- | --- |
| Add one row per benchmark case. | Score 0-2. | Score 0-2. | Score 0-2. | Score 0-2. | Score 0-2. | Sum scored dimensions. |

## Regression Notes

- Previous result compared: write the result file path.
- Regressed cases: write the case IDs and score changes.
- Improved cases: write the case IDs and score changes.
- New weaknesses found: write concrete weakness notes.
- Recommended skill changes: write concrete changes or `none`.

## Overall Decision

- All must-pass cases passed: write yes or no.
- Diagnostic-only failures recorded: write yes, no, or not applicable.
- Skill changes needed: write yes or no.
