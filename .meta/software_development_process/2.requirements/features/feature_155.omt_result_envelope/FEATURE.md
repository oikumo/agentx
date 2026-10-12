# Feature 155: Omt Result Envelope

> **Status:** [ ] Not started
> **Created:** 2026-10-12
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Machine-readable `OmtResult` envelope `omt-skill-result/v1` (ok/outcome/code/blocker/evidence/retryable/stateRevision) + Python constructor/validator + TS shape + adapters, so blocked vs succeeded needs no textual heuristic. Builds on feature_154 contract shape-only.

## Scope (one sentence — what "done" looks like)

`skill.result.schema.json` + `skill_result.py` make/validate + adapters land, 7 goldens green, `doctor` checks result_schema, pilots can return envelope with no prose verdict.

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_155.omt_result_envelope/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_155.omt_result_envelope/analysis_001_envelope_scope.md` | [x] |
| Design | Design doc | `4.design/features/feature_155.omt_result_envelope/design_001_envelope.md` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_155.omt_result_envelope/implementation_001_envelope.md` | [x] |
| Testing | Test report | `6.testing/features/feature_155.omt_result_envelope/test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
