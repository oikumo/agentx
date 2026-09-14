# Feature 099: Mh9 S2 Truthful Boundary Residual

> **Status:** [~] In progress (S2 4-file round green)
> **Created:** 2026-09-14
> **WORK.md task:** mh9 S2 — project meta_harness_9 (paired with S1)
> **Project:** `meta_harness_9` (origin: scaffold)

---

## Summary

S2 correctness: invalid cannot claim success — F09 authority writes report failure, F05-caller empty→fail-closed, F02 advice vs authority split, F03 obligations compose on live path. Smallest diffs, positive controls, one edit per file per e2e receipt.

## Scope (one sentence — what "done" looks like)

Done = allow/deny matrix green on real edits (4 seeded invalid rejected + valid accepted) per `analysis_001_residual_order.md` + `test_report.md`.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_099.mh9_s2_truthful_boundary_residual/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_099.mh9_s2_truthful_boundary_residual/analysis_001_residual_order.md` | [x] |
| Design | Design doc | `4.design/features/feature_099.mh9_s2_truthful_boundary_residual/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_099.mh9_s2_truthful_boundary_residual/` | [ ] |
| Testing | Test report | `6.testing/features/feature_099.mh9_s2_truthful_boundary_residual/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
