# Feature 159: Session Compat Versioned Error

> **Status:** [ ] Not started
> **Created:** 2026-10-12
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

`omt_session` reads the live OpenCode SQLite DB read-only or returns a versioned machine-readable error mapped to `OmtResult` — no secret skill-side path, no prose heuristic.

## Scope (one sentence — what "done" looks like)

`omt_session` returns `version:1` on all paths with UPPER_SNAKE `code` + remediation + read-only proof, mapped via `skill_result.from_session` to envelope.

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_159.session_compat_versioned_error/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_159.session_compat_versioned_error/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_159.session_compat_versioned_error/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_159.session_compat_versioned_error/` | [ ] |
| Testing | Test report | `6.testing/features/feature_159.session_compat_versioned_error/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
