# Feature 115: Live Progress Full Push Join View

> **Status:** [ ] Not started
> **Created:** 2026-09-19
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

O5-follow-up (O5a+b): fill `push.tasks_block` with the dry-run `sync net_to_md` Tasks text on every mutating envelope and add a batch/join progress projection over the O4 dispatch plan — closing the two feature_113 residuals (empty `tasks_block`, text-only view) while keeping D4 proposal-only, Tier-3, and F7/D1 locks.

## Scope (one sentence — what "done" looks like)

Fire/claim/apply/dispatch envelopes return `push {net_revision, menu, tasks_block}` with D19 round-tripping text plus a deterministic batch/join projection, all additive fail-open with no new places or kinds.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_115.live_progress_full_push_join_view/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_115.live_progress_full_push_join_view/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_115.live_progress_full_push_join_view/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_115.live_progress_full_push_join_view/` | [ ] |
| Testing | Test report | `6.testing/features/feature_115.live_progress_full_push_join_view/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
