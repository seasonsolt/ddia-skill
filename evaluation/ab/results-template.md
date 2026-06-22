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

| Case | Category | Control score | Treatment score | Lift | Control normalized | Treatment normalized | Normalized lift | Pass/fail change | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Add one row per case. | Use good, bad, or adversarial. | Score after reveal. | Score after reveal. | Treatment minus control. | Control percentage. | Treatment percentage. | Treatment percentage minus control percentage. | State no change, fail to pass, pass to fail, or diagnostic change. | Record scoring rationale. |

## Dimension Differences

Record workload framing, trade-off quality, failure-mode coverage, correctness reasoning, verification value, and anti-pattern resistance differences.

## Response Archive

For each case, preserve Response A and Response B exactly as evaluated.

## Limitations

- Self-evaluation bias: state whether the generator and evaluator are independent.
- Response-shape/rubric alignment: state whether one arm was prompted into a structure that matches the rubric.
- Single model: state which model was used and whether other models were excluded.
- Single run: state how many runs were generated per arm.
- No variance estimate: state whether mean, minimum, maximum, and range were measured.
- Non-random case selection: state how cases were selected.
- Process-compliance rubric not scored: state whether process compliance was scored separately.

## Overall Decision

- Total control score: write the total.
- Total treatment score: write the total.
- Total lift: write treatment minus control.
- Mean normalized control: write the mean control percentage.
- Mean normalized treatment: write the mean treatment percentage.
- Mean normalized lift: write treatment percentage minus control percentage.
- Limitations: summarize the evidence strength.
