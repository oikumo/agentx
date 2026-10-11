# Feature 151: T5 Per-Mechanic Receipts

> **Status:** [x] Done 2026-10-11
> **Created:** 2026-10-11
> **WORK.md task:** harness_wrapper_split T5 (PROPOSAL_V7 §6 T5 + §3 "Per-mechanic receipts are T5 design, not current fact")

## Summary

The `g.receipt` second-edit guard is GLOBAL today: any harness-surface edit requires a fresh run of the single global e2e, so touching one mechanic (e.g. `omt_q.ts`) forces re-receipting the whole harness surface before ANY other harness file can be edited again. T5 replaces it slice by slice: files map to mechanic slices; a slice-fresh receipt block (per-slice `passed_at` + content digests + results) lets a bumped mechanic be re-receipted by running ONLY that slice's tests (`uv run scripts/omt/receipt.py mint --slice <name>`), leaving other slices' receipts untouched. Unmapped files keep the legacy global check (v1 compat); policy changes (`META_HARNESS.omt`) still invalidate everything (policy_ver global by design).

## Scope (one sentence — what "done" looks like

Done = editing a mapped harness file is allowed when ITS slice's receipt block is fresh (mtime + digest + results), even if other slices are stale, and `receipt.py mint --slice` re-validated only that slice's test set; legacy paths behave byte-identically; goldens pin slice resolution, per-slice freshness, stale-block blocking, digest content-binding, and unmapped fallback.

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_151.t5_per_mechanic_receipts/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_151.t5_per_mechanic_receipts/analysis_001_t5_receipts.md` | [x] |
| Design | Design doc | `4.design/features/feature_151.t5_per_mechanic_receipts/design_001_t5_receipts.md` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_151.t5_per_mechanic_receipts/implementation_001_t5_receipts.md` | [x] |
| Testing | Test report | `6.testing/features/feature_151.t5_per_mechanic_receipts/test_report.md` | [x] |
