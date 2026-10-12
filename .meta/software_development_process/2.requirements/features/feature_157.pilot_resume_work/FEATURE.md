# Feature 157: Pilot Resume Work

> **Status:** [ ] Not started
> **Created:** 2026-10-12
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Contracted manual-only `omt-resume-work` pilot (SKILL.md + contract + checklist) that reconciles session→feature→project→harness owners with fingerprints and returns envelope, so resume never invents state. Consumes 154+155+156.

## Scope (one sentence — what "done" looks like)

`omt-resume-work` skill lands contracted, `doctor` green, 7 goldens green (positive + stale-pause negative + envelope mapping).

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_157.pilot_resume_work/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_157.pilot_resume_work/analysis_001_resume_scope.md` | [x] |
| Design | Design doc | `4.design/features/feature_157.pilot_resume_work/design_001_resume_pilot.md` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_157.pilot_resume_work/implementation_001_resume_pilot.md` | [x] |
| Testing | Test report | `6.testing/features/feature_157.pilot_resume_work/test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
