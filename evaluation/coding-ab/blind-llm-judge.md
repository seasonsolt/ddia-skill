# Blind LLM Judge

## Scoring Order

Score Response A and Response B before revealing which response is control or treatment. Use only the case text and the submitted answer. Do not reward mention of ddia-system-design by name; reward the observable reasoning and patch quality.

## Dimensions

1. Java patch correctness
2. Source-of-truth reasoning
3. Failure-mode coverage
4. Transaction and idempotency reasoning
5. Verification value
6. Anti-pattern resistance

Each dimension receives 0, 1, or 2 points.

- 0 points: missing, incorrect, or actively harmful.
- 1 point: partially addresses the issue but leaves important ambiguity or failure modes.
- 2 points: concrete, correct, and tied to the case's Java patch and DDIA concern.

Bad coding cases pass at 9 out of 12 with no zero in anti-pattern resistance. Adversarial coding cases pass at 10 out of 12 with 2 points in anti-pattern resistance.

## Mapping Reveal

Reveal the mapping only after all dimensions, notes, and pass decisions are recorded. Then record whether the treatment improved, regressed, or tied the control answer and why.
