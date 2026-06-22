# Blind LLM Judge

## Scoring Order

Score Response A and Response B before revealing which response is control or treatment. Use only the case text and the submitted answer. Do not reward mention of ddia-system-design by name; reward the observable reasoning and patch quality.

## Dimensions

1. Correctness invariant
2. Source-of-truth boundary
3. Failure-mode handling
4. Idempotency and retry safety
5. Operational verification
6. Java patch quality
7. Anti-pattern resistance

Base dimensions receive 0, 1, or 2 points.
For good and bad coding cases, anti-pattern resistance is null and the total is out of 12.
For adversarial coding cases, anti-pattern resistance receives 0, 1, or 2 points and the total is out of 14.

- 0 points: missing, incorrect, or actively harmful.
- 1 point: partially addresses the issue but leaves important ambiguity or failure modes.
- 2 points: concrete, correct, and tied to the case's Java patch and DDIA concern.

Good coding cases pass at 10 out of 12 with every base dimension above 0. They should preserve the correct system boundary and avoid unnecessary distributed coordination or durability machinery.
Bad coding cases pass at 10 out of 12 with every base dimension above 0. Adversarial coding cases pass at 12 out of 14 with every dimension above 0 and 2 points in anti-pattern resistance.

## Mapping Reveal

Reveal the mapping only after all dimensions, notes, and pass decisions are recorded. Then record whether the treatment improved, regressed, or tied the control answer and why.
