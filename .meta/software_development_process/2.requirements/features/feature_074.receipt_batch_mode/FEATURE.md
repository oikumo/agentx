# Feature 074: Receipt Batch Mode

> **Status:** [~] In progress (Programming done, Testing done, pending omt_complete)
> **Created:** 2026-09-12
> **WORK.md task:** meta_harness_8 T4-2 (no pool task; project-linked minor_feature)
> **Project:** meta_harness_8 (origin: scaffold, D5 overlap-clear vs mh7 P2-3 + Improvement002 D)

---

## Summary

T4-2 replaces the per-file receipt round-robin (ONE edit/file/round + e2e refresh) with a bounded staged batch: `harnessc.py stage --feature <slug> <files...>` snapshots mtimes + sha256 digests + policy version into ignored runtime state (`.meta/.omt/omt_harness_stage.json`); staged files bypass the per-file second-edit guard (`isStagedHarnessFile` in `omt_shared.ts`) so temporary inconsistency inside the batch is OK; a single boundary e2e validates the whole patch (same patch, same treatment any edit count). D-bar content binding: the e2e receipt now carries `policy_ver` + `toolchain` alongside digests, and the guard re-checks digest + policy even when the timestamp looks fresh (input change invalidates). Fail-closed outside the stage; stage/clear never touch tracked content (user edits preserved); only explicit `--clear` drops a stage (a failing boundary e2e still blocks).

## Scope (one sentence — what "done" looks like)

T4-2 done = stage CLI + staged bypass + content-bound receipt shipped with 5 golden tests green, boundary e2e green, `harnessc check` 0 errors, omt-suite 458 green (1 pre-existing budget-pin failure unrelated).

## Task type

minor_feature (decl-only per §12; no design doc)

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_074.receipt_batch_mode/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_074.receipt_batch_mode/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_074.receipt_batch_mode/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_074.receipt_batch_mode/` | [ ] |
| Testing | Test report | `6.testing/features/feature_074.receipt_batch_mode/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
