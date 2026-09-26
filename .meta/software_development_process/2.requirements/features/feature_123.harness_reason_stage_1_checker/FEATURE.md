# Feature 123: Harness Reason Stage 1 Checker

> **Status:** [ ] Not started
> **Created:** 2026-09-26
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Stage-1 advisory checker for harness_reason: pure check+explain over Stage-0 contracts/IR with immutable context import and premise slices, agreeing with existing authority on all 12 §14.1 cases, sandbox-only.

## Scope (one sentence — what "done" looks like)

Done = check+explain replay the §3 three-row and §11.6 mismatch examples from digests plus 12/12 §14.1 agreement in `.sandbox/harness_reason/` with no src/net/toolbox change.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_123.harness_reason_stage_1_checker/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_123.harness_reason_stage_1_checker/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_123.harness_reason_stage_1_checker/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_123.harness_reason_stage_1_checker/` | [ ] |
| Testing | Test report | `6.testing/features/feature_123.harness_reason_stage_1_checker/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
