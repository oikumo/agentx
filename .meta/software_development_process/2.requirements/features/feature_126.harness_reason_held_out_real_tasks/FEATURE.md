# Feature 126: Harness Reason Held Out Real Tasks

> **Status:** [ ] Not started
> **Created:** 2026-09-26
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Paired-experiment follow-on: replace synthetic cost ledgers with held-out real tasks on real sandbox files under identical three-arm shared-inputs/snapshot/order/oracle discipline; sandbox-only, advisory boundary holds.

## Scope (one sentence — what "done" looks like)

R1-R4 held-out probe passes on real files plus rerun of S0 7/7 + S1 12/12 + S2 7/7 + S3 7/7 with byte-stable digests, sandbox only.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_126.harness_reason_held_out_real_tasks/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_126.harness_reason_held_out_real_tasks/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_126.harness_reason_held_out_real_tasks/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_126.harness_reason_held_out_real_tasks/` | [ ] |
| Testing | Test report | `6.testing/features/feature_126.harness_reason_held_out_real_tasks/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
