# DDIA Coding A/B Pilot Results

## Run Metadata

- Date: 2026-06-22
- Evaluator: Codex CLI
- CLI version: codex-cli 0.141.0
- Model: gpt-5.3-codex-spark
- Provider: OpenAI
- Reasoning effort: high
- Sandbox: read-only
- Session mode: ephemeral
- Case: checkout-cache-as-truth
- Category: bad

## Run Hygiene

The answer-generation prompt used only the case metadata, scenario, flawed Java,
and task. It deliberately removed these judge-only sections from the case file:

- Expected DDIA Reasoning
- Strong Patch Signals
- Weak Patch Patterns
- Scoring Notes

An earlier unredacted attempt was discarded because those sections leak the
answer key to both arms.

Both arms used the same model, reasoning effort, output shape, and case text.
The control prompt used `evaluation/coding-ab/control-instructions.md`. The
treatment prompt used `evaluation/coding-ab/treatment-instructions.md` plus the
installed `ddia-system-design` skill text.

The blind judge saw the full case, the rubric, Response A, and Response B. It
did not see the control/treatment mapping.

This pilot used one case from the original five-case pilot suite. The expanded
18-case suite should be used for the next run. Future runs should use the
prompt renderer instead of hand-built prompts.

## Hidden Mapping

- Response A: control
- Response B: treatment

## Score

| Case | Category | Control score | Treatment score | Lift | Pass/fail change | Winner |
| --- | --- | ---: | ---: | ---: | --- | --- |
| checkout-cache-as-truth | bad | 7/12 | 8/12 | +1 | both failed | treatment |

## Dimension Scores

| Dimension | Control | Treatment | Difference |
| --- | ---: | ---: | ---: |
| Correctness invariant | 1 | 1 | 0 |
| Source-of-truth boundary | 1 | 1 | 0 |
| Failure-mode handling | 1 | 1 | 0 |
| Idempotency and retry safety | 1 | 2 | +1 |
| Operational verification | 2 | 2 | 0 |
| Java patch quality | 1 | 1 | 0 |

Anti-pattern resistance is not scored for bad cases, so the denominator is 12.

## Blind Judge Output

The full generated control answer, treatment answer, mapping, and raw judge JSON
are archived in
[`runs/2026-06-22-checkout-cache-as-truth`](runs/2026-06-22-checkout-cache-as-truth).

```json
{
  "case_id": "checkout-cache-as-truth",
  "category": "bad",
  "response_a": {
    "correctness_invariant": 1,
    "source_of_truth_boundary": 1,
    "failure_mode_handling": 1,
    "idempotency_retry_safety": 1,
    "operational_verification": 2,
    "java_patch_quality": 1,
    "anti_pattern_resistance": null,
    "total": 7,
    "denominator": 12,
    "pass": false,
    "notes": "Adds an idempotency key and duplicate handling, and proposes tests for retry/crash/reconciliation, but still keeps Redis as the active availability source. Concurrent same-request retries can still mis-handle hold lifecycle, and stale hold-index cleanup is weak."
  },
  "response_b": {
    "correctness_invariant": 1,
    "source_of_truth_boundary": 1,
    "failure_mode_handling": 1,
    "idempotency_retry_safety": 2,
    "operational_verification": 2,
    "java_patch_quality": 1,
    "anti_pattern_resistance": null,
    "total": 8,
    "denominator": 12,
    "pass": false,
    "notes": "Clearer idempotent/replay flow with explicit in-flight control and duplicate-path handling, and stronger failure tests. Still relies on Redis-decremented stock as the write-time availability gate without a durable inventory boundary; crash-after-reserve leak remains a correctness risk unless external reconciliation is fully defined/implemented."
  },
  "winner": "B",
  "rationale": "Response B is stronger overall due to cleaner idempotency and concurrent replay handling (in-flight reservation + pre-check by checkoutId). Response A has a meaningful attempt but includes a higher-risk race around hold release under duplicate-inflight attempts and weaker hold-index hygiene. Neither fully satisfies the strongest DDIA fix (durable source-of-truth inventory transaction), so both fail. B is improved relative to A."
}
```

## Interpretation

The treatment improved the answer, but only slightly. The useful gain was in
idempotency and retry handling. The treatment also made the failure and
observability framing clearer.

The important negative result is that the treatment still kept Redis as the
write-time availability gate. For this case, the desired patch should move the
inventory invariant into a durable transactional boundary, such as a conditional
Postgres update, row lock, reservation row, or equivalent durable workflow.

This means the coding A/B benchmark is already useful: it found that the skill
can improve explanation quality without reliably changing the implementation
boundary. That is exactly the distinction this coding track was meant to test.

## Next Iteration

- Strengthen `ddia-system-design` for coding tasks with an explicit rule:
  "If a cache, replica, lock, or stream currently protects a business invariant,
  first ask whether the invariant belongs in a durable transactional boundary."
- Add a worked Java example that moves a cache-protected invariant into a
  database transaction.
- Add an answer-generation helper that automatically strips judge-only sections
  before running future A/B pilots.
- Rerun the expanded 18-case coding suite with at least three response samples
  per arm.

## Limitations

- One case only.
- One model only.
- One sample per arm.
- The same model family generated and judged the answers.
- The judge was blind to mapping, but not independent of the answer model.
- The response shape was fixed for both arms, which may reduce natural control
  variance.
