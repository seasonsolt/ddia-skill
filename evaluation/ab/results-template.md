# DDIA Skill A/B Results Template

## Run Metadata

- Evaluator: write the evaluator name.
- Date: write the run date in YYYY-MM-DD format.
- Model: write the model name.
- Skill version: write the Git commit or skill version.

## Hidden Mapping

- Response A: write control or treatment after scoring.
- Response B: write control or treatment after scoring.

## Case Scores

| Case | Category | Control score | Treatment score | Lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Add one row per case. | Use good, bad, or adversarial. | Score after reveal. | Score after reveal. | Treatment minus control. | State no change, fail to pass, pass to fail, or diagnostic change. | Record scoring rationale. |

## Dimension Differences

Record workload framing, trade-off quality, failure-mode coverage, correctness reasoning, verification value, and anti-pattern resistance differences.

## Response Archive

For each case, preserve Response A and Response B exactly as evaluated.

## Overall Decision

- Total control score: write the total.
- Total treatment score: write the total.
- Total lift: write treatment minus control.
- Limitations: write the study limitations.
