# Feature 109: Mh10_P2D_Matrix_Payback

> **Status:** [x] Analysis signed
> **Created:** 2026-09-19
> **WORK.md task:** MH10 P2 slice D

---

## Summary

Slice D closes P2 re-entry rows (d) allow/deny matrix + (e) net-zero retirement + (a) payback protocol: V1–V5 valid controls allow, I1–I8 seeded invalids deny fail-closed, payback measured on natural wins only, zero live gates.

## Scope (one sentence — what "done" looks like)

Matrix spec approved then tests-only goldens green + regressions + receipt + suite + check/build green with no template change.

## Task type

minor_feature (project meta_harness_10)

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_109.mh10_p2d_matrix_payback/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_109.mh10_p2d_matrix_payback/analysis_001_matrix_payback.md` | [x] |
| Design | Design doc | `4.design/features/feature_109.mh10_p2d_matrix_payback/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_109.mh10_p2d_matrix_payback/` | [ ] |
| Testing | Test report | `6.testing/features/feature_109.mh10_p2d_matrix_payback/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
