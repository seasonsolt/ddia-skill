# Agent Lab Skill Comparison Evidence

- Generated at: `2026-06-22T15:02:50.222807+00:00`
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
| Error rate | 1.0 | 1.0 |  |
| Timeout rate | 1.0 | 1.0 |  |

## Run IDs

- Baseline: `eval-2fa51f18397c40f1a66a604cc44400d7, eval-006987e760074245b26e85518642b111, eval-9d4ee8ac80354de79ba28c0c135c9164`
- Treatment: `eval-26319c097c66486fb1bd07459da34f9a, eval-898c9c72f29341749f82135864a5fe1e, eval-30d3b31a12a543cb875c4c68e147babb`

## Reproduction

```bash
python3 -m skill_lab.cli compare --baseline ./skills/example-coding-skill --treatment-repo https://github.com/seasonsolt/ddia-skill --treatment-skill-path skills/ddia-system-design --task-pack ./task_packs/ddia-coding-real --api-url http://localhost:8000 --runs 3 --network --timeout-seconds 300 --output-dir /tmp/agent-lab-ddia-evidence
```

## Limitations

This is repeated Agent Lab comparison evidence, not statistical proof. Model output variance, model/provider configuration, task-pack coverage, and sandbox timeouts can affect the result.
