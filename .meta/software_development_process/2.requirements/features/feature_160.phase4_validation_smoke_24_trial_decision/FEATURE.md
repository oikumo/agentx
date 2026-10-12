# Feature 160: Phase4 Validation Smoke 24-Trial Decision

> **Status:** [ ] Not started
> **Created:** 2026-10-12
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Phase4 validation for meta_harness_skills — smoke + 24-trial experiment (4 cases x baseline/treatment x 3 reps) + rollout decision retain/revise/drop/inconclusive, measuring whether manual-only pilots cut mistaken steps with envelope evidence.

## Scope (one sentence — what "done" looks like)

Phase4 validation ships smoke + 24-trial (4 cases x baseline/treatment x 3 reps) + rollout decision retain/revise/drop/inconclusive with envelope evidence.

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_160.phase4_validation_smoke_24_trial_decision/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_160.phase4_validation_smoke_24_trial_decision/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_160.phase4_validation_smoke_24_trial_decision/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_160.phase4_validation_smoke_24_trial_decision/` | [ ] |
| Testing | Test report | `6.testing/features/feature_160.phase4_validation_smoke_24_trial_decision/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
