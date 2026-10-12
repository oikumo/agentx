# Feature 158: Pilot Verify Closeout

> **Status:** [ ] Not started
> **Created:** 2026-10-12
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Contracted manual-only `omt-verify-closeout` pilot (SKILL.md + contract + checklist) that re-runs closeout evidence (docs exist, doctor green, feature goldens, WORK budget) and returns envelope, so DONE is never invented. Consumes 154–157.

## Scope (one sentence — what "done" looks like)

`omt-verify-closeout` skill lands contracted, `doctor` green, 7 goldens green (positive + red-doctor/missing-report negatives + mapping).

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_158.pilot_verify_closeout/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_158.pilot_verify_closeout/analysis_001_verify_scope.md` | [x] |
| Design | Design doc | `4.design/features/feature_158.pilot_verify_closeout/design_001_verify_pilot.md` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_158.pilot_verify_closeout/implementation_001_verify_pilot.md` | [x] |
| Testing | Test report | `6.testing/features/feature_158.pilot_verify_closeout/test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
