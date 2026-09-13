# Feature 088: G.Kb Per-File Read Recency

> **Status:** [x] Done (2026-09-13)
> **Created:** 2026-09-13
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

meta_harness_8 T2-5 (source: mh3 P3-9). g.kb previously required a session-wide `omt_kb_nav` consult (or sticky/fast-path unlock) before ANY `src/` edit — even when the agent had just Read the exact file it was about to edit. This feature adds a NEW per-file Read-recency substrate: an enforcer after-hook records each completed Read ({session → rel → ms}), and the g.kb predicate consults it per-file — a read-then-edit of the SAME file passes without a redundant KB consult, while a blind edit to a never-read file still blocks. It is deliberately NOT a mirror of think-consult `recent_consults` (mh3 R2).

## Scope (one sentence — what "done" looks like)

Read-then-edit of the same file in the same session satisfies g.kb for that file only; never-read files still block; consult/unlock paths unchanged.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_088.g_kb_per_file_read_recency/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_088.g_kb_per_file_read_recency/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_088.g_kb_per_file_read_recency/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_088.g_kb_per_file_read_recency/` | [ ] |
| Testing | Test report | `6.testing/features/feature_088.g_kb_per_file_read_recency/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
