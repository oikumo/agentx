# Feature 094: Selective Verifiable Knowledge Pilot

> **Status:** [x] Done (SHIPPED 2026-09-14, mh8 T3-6)
> **Created:** 2026-09-13
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Selective verifiable knowledge pilot (mh8 T3-6, Improvement002 E): sidecar
lesson-metadata JSON (3 top repeated-discovery lessons) + read-only
change-surface advisory lookup. Relevant changes surface the lesson, unrelated
edits stay silent, promotion/retirement carry reason + replacement check.

## Scope (one sentence — what "done" looks like)

Option A ships: `scripts/omt/kb_pilot/` sidecar + advisory lookup with 10
goldens green, e2e green, full suite 2241/2241, no policy change.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_094.selective_verifiable_knowledge_pilot/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_094.selective_verifiable_knowledge_pilot/analysis_001_*.md` | [x] |
| Design | Design doc | `4.design/features/feature_094.selective_verifiable_knowledge_pilot/design_001_*.md` | [x] (boundary in analysis_001, decl-only per §12) |
| Implementation | Impl notes | `5.implementation/features/feature_094.selective_verifiable_knowledge_pilot/` | [x] |
| Testing | Test report | `6.testing/features/feature_094.selective_verifiable_knowledge_pilot/` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
