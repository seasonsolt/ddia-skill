# Agent Lab Skill Comparison Evidence

- Generated at: `2026-06-23T03:49:06.480578+00:00`
- Evaluator: `seasonsolt/agent-lab`
- Treatment repo: `https://github.com/seasonsolt/ddia-skill`
- Treatment commit: `a2a8695436d01b53a91cb794200c81d7e9532eaf`
- Treatment skill path: `skills/ddia-system-design`
- Baseline skill path: `/Users/Thin/Source/git/seasonsolt/agent-lab/skills/example-coding-skill`
- Task pack path: `/Users/Thin/Source/git/seasonsolt/agent-lab/task_packs/ddia-coding-real`
- Verdict: `inconclusive`

## Summary

| Metric | Baseline | Treatment | Delta |
| --- | ---: | ---: | ---: |
| Mean auto score | 33.33 | 33.33 | 0.0 |
| Mean final score | 23.33 | 23.33 | 0.0 |
| Mean pass rate | 0.0 | 0.0 | 0.0 |
| Error rate | 0.33 | 0.0 |  |
| Timeout rate | 0.0 | 0.0 |  |

## Run IDs

- Baseline: `eval-feba7f6c73a74c72b8643d0e6807a524, eval-71a04edce70948d6939cbe49678fa2d4, eval-68d20bf85f1640dcbab7a27878815792`
- Treatment: `eval-5c1cba64f01843db97372fbc05a73048, eval-522b03a1fc4341dcbccec071c27ffb93, eval-9dcd3aa903534ad5acd5fc416dec0bdd`

## Reproduction

```bash
python3 -m skill_lab.cli compare --baseline ./skills/example-coding-skill --treatment-repo https://github.com/seasonsolt/ddia-skill --treatment-skill-path skills/ddia-system-design --task-pack ./task_packs/ddia-coding-real --api-url http://localhost:8000 --runs 3 --network --timeout-seconds 300 --output-dir /tmp/agent-lab-ddia-evidence
```

## Limitations

This is repeated Agent Lab comparison evidence, not statistical proof. Model output variance, model/provider configuration, task-pack coverage, and sandbox timeouts can affect the result.
