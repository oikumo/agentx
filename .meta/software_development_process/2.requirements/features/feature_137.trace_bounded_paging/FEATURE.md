# Feature 137: Trace Bounded Paging

> **Status:** [x] Shipped 2026-09-28 (minor_feature: declaration + code + 6 tests + e2e receipt; see mh15 CURRENT_STATE 2026-09-28 entry)
> **Created:** 2026-09-27
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Bounded paging for `omt_session trace` (mh15 slice 1): the bare-trace default no longer dumps ~100KB/350-entry skeletons — it returns a ~≤2KB first page with totals, `truncated`, stable snapshot-order paging (`page`/`per_page`, mirroring `inspect`), and a digest-bound `detail_ref`, so every entry stays retrievable and replays stay stable.

## Scope (one sentence — what "done" looks like)

`trace` defaults to page 0 × 20 with full totals + truncated flag + digest ref, explicit pages reconstruct the full timeline losslessly, plugin/service arg parity holds, and the boundary e2e + pin suite stays green.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_137.trace_bounded_paging/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_137.trace_bounded_paging/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_137.trace_bounded_paging/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_137.trace_bounded_paging/` | [ ] |
| Testing | Test report | `6.testing/features/feature_137.trace_bounded_paging/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
