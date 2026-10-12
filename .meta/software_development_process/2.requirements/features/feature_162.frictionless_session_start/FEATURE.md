# Feature 162: Frictionless Session Start

> **Status:** [ ] Not started
> **Created:** 2026-10-12
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Live-first, fail-closed session start: `hi` with empty pool renders lean (no stale A-J from rev60 file when live is rev0/none).

## Scope (one sentence — what "done" looks like)

Done when session start builds picks live-first with zero stale letters and lean empty-pool reply.

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_162.frictionless_session_start/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_162.frictionless_session_start/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_162.frictionless_session_start/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_162.frictionless_session_start/` | [ ] |
| Testing | Test report | `6.testing/features/feature_162.frictionless_session_start/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
