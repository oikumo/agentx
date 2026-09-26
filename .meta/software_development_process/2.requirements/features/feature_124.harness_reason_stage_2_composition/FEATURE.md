# Feature 124: Harness Reason Stage 2 Composition

> **Status:** [ ] Not started
> **Created:** 2026-09-26
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Stage-2 composition/replacement for harness_reason: parameterized fragments over S0 contracts/IR with replayable rewrite certs for a small law set, reuse across two task contexts with fresh obligations per instantiation, unsafe substitution rejected with witness, sandbox-only.

## Scope (one sentence — what "done" looks like)

Done = verify_candidate expands across two artifacts with fresh obligations (refuses h2-with-h1 evidence) + test;edit rejected under completion-relevant contract with (h1,h0) witness while permitted under files-only contract in `.sandbox/harness_reason/` with no src/net/toolbox change.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_124.harness_reason_stage_2_composition/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_124.harness_reason_stage_2_composition/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_124.harness_reason_stage_2_composition/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_124.harness_reason_stage_2_composition/` | [ ] |
| Testing | Test report | `6.testing/features/feature_124.harness_reason_stage_2_composition/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
