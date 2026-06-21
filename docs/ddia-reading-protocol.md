# DDIA Reading Protocol

This repository may read the local DDIA PDF to create an original Codex skill. The final committed skill must not contain long copied passages from the book.

## Source

- Local PDF: `/Users/Thin/Library/Mobile Documents/com~apple~CloudDocs/学习/分布式/designing-data-intensive-applications.pdf`
- Private extracted text: `/Users/Thin/Documents/ddia/tmp/ddia-extract/pages/`
- Committed original notes: `/Users/Thin/Documents/ddia/analysis/ddia-reading-ledger.md`

## Reading Method

Read pages in order inside each chapter. For every chapter, write original notes in the ledger using these fields:

- `Target engineering decisions`: real decisions a backend engineer or architect makes.
- `Failure modes`: ways a design can break under load, faults, concurrency, or operations.
- `Trade-offs`: explicit cost, correctness, latency, complexity, and operability choices.
- `Review questions`: questions a future Codex agent should ask before recommending a design.
- `Skill guidance`: concise instructions that can be moved into the skill references.

## Copyright Discipline

- Use original wording in committed files.
- Keep copied source text only in `tmp/ddia-extract/`, which is ignored by Git.
- Keep direct quotations out of the skill unless a short phrase is necessary and clearly attributed.
- Prefer concepts, checklists, and decision frameworks over book summaries.

## Coverage Standard

The ledger is complete when all 12 chapters are marked `Reviewed: yes`, each chapter has at least three bullets in every field, and each bullet gives practical guidance rather than a paraphrased sentence.
