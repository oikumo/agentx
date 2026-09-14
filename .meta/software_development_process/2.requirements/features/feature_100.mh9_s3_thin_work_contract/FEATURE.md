# Feature 100: Mh9_S3_Thin_Work_Contract

> **Status:** [~] In progress (S3 Analysis signed)
> **Created:** 2026-09-14
> **WORK.md task:** mh9 S3 thin work contract — project meta_harness_9 (active)
> **Project:** `meta_harness_9` (origin: scaffold)

---

## Summary

mh9 S3: one bounded read-only task view (request/acceptance/scope/obligations/next-action+evidence/stale-or-unknown/detail-refs, ≤2KB) projected over 072 typed policy + 073 task-prep + 092 resume digest + 055/062 preflight — no store, no writer, no authority change; 2-task demo + dry/live parity note.

## Scope (one sentence — what "done" looks like)

Done = sidecar renderer + schema in `.sandbox/work_contract/` with 2048B cap + 2 demo contracts that orient from projection alone + parity note, per `analysis_001_thin_contract.md`, with check/build/suite green.

---

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_100.mh9_s3_thin_work_contract/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_100.mh9_s3_thin_work_contract/analysis_001_thin_contract.md` | [x] |
| Design | Design doc | n/a (`minor_feature` decl-only; schema lives in analysis §3) | [x] |
| Implementation | Sidecar | `.sandbox/work_contract/` (contract.py + 2 demos + parity_note.md) | [x] |
| Testing | Test report | `6.testing/features/feature_100.mh9_s3_thin_work_contract/test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
