# Feature 156: State Scope

> **Status:** [ ] Not started
> **Created:** 2026-10-12
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

StateScope ownership doc (invocation/session/feature/project/harness, skills own nothing) + `doctor` lint for stray state files, so resume never invents state. Closes Phase1 contracts (154+155+156).

## Scope (one sentence — what "done" looks like)

`state.scope.md` ownership table lands, `doctor` warns on `.skill-state.json`, pilots reference owners only.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_156.state_scope/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_156.state_scope/analysis_001_state_scope.md` | [x] |
| Design | Design doc | `4.design/features/feature_156.state_scope/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_156.state_scope/` | [ ] |
| Testing | Test report | `6.testing/features/feature_156.state_scope/test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
