# Checkout Cache As Truth Coding A/B Run

## Files

- `control-response.md`: raw Codex last-message output for the control arm.
- `treatment-response.md`: raw Codex last-message output for the DDIA treatment arm.
- `blind-judge-result.json`: raw blind judge JSON output.
- `mapping.txt`: response-to-arm mapping revealed after judging.

## Run Setup

- Date: 2026-06-22
- Case: `checkout-cache-as-truth`
- Category: bad
- Answer model: `gpt-5.3-codex-spark`
- Judge model: `gpt-5.3-codex-spark`
- CLI: `codex-cli 0.141.0`
- Answer mode: `codex exec --ephemeral --ignore-user-config --ignore-rules`
- Sandbox: read-only
- Reasoning effort: high

The answer model saw only the case metadata, scenario, flawed Java, and task.
The answer model did not see the judge-only sections:

- Expected DDIA Reasoning
- Strong Patch Signals
- Weak Patch Patterns
- Scoring Notes

## Mapping

- Response A: control
- Response B: treatment

## Result

| Arm | Score | Pass |
| --- | ---: | --- |
| Control | 7/12 | no |
| Treatment | 8/12 | no |

The blind judge picked the treatment answer because it handled idempotency and
concurrent replay more cleanly. Both answers failed because they kept Redis in
the write-time availability path instead of moving the inventory invariant into
a durable transaction or equivalent reservation workflow.

## Known Contamination

The control response contains an extra natural-language rewrite line from the
local language-learning instruction. The judge still scored the technical
content, but future pilot runners should isolate answer generation from all
personal or project response-style instructions.
