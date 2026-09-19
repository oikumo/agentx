# Feature 108: Mh10_P2C_Crash_Reorder

> **Status:** [x] Analysis signed
> **Created:** 2026-09-18
> **WORK.md task:** meta_harness_10 P2 slice C

---

## Summary

MH10 P2 slice C closes the C1 crash window in `scripts/omt/net/state.py::_transact`: the success path currently does `clear_pending` (state.py:746-750) BEFORE `record_command` (state.py:751-758), so a crash between save/clear/record leaves a committed revision with no idempotency index — a retry with the same `command_id` double-fires. The slice reorders to record-before-clear and teaches `reconcile_transactions` to backfill the index from the WAL marker, with a crash-injection suite proving every crash point.

## Scope (one sentence — what "done" looks like)

Every crash point between save/clear/record reconciles deterministically with idempotent replay (no double-fire), proven by crash-injection goldens + receipt + `check`/`build`/suite green.

## Task type

minor_feature (declaration only per §12; Analysis signed in `analysis_001_crash_reorder.md`)

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_108.mh10_p2c_crash_reorder/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_108.mh10_p2c_crash_reorder/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_108.mh10_p2c_crash_reorder/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_108.mh10_p2c_crash_reorder/` | [ ] |
| Testing | Test report | `6.testing/features/feature_108.mh10_p2c_crash_reorder/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
