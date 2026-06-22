# Blind Scoring Guide

## Scoring Order

Score Response A and Response B before revealing which response is control or treatment.

Use `evaluation/rubrics/answer-quality.md` for every response. For good cases, score five dimensions for a maximum of 10. For bad and adversarial cases, also score Anti-pattern resistance for a maximum of 12.

Score the substance of the answer, not the mere presence of headings. A response should earn points when it actually explains workload, trade-offs, failure modes, correctness, and verification.

## Mapping Reveal

Reveal the mapping only after all dimensions, notes, totals, and pass/fail decisions are recorded.

After revealing the mapping, compute treatment lift:

```text
treatment score - control score
```

Also record normalized score lift in percentage points so 10-point and 12-point cases can be compared:

```text
(treatment score / treatment max * 100) - (control score / control max * 100)
```

Record whether the treatment changed the pass/fail decision and which dimensions improved or regressed.
