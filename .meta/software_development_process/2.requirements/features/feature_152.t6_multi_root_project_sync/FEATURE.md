# Feature 152: T6 Multi-Root Project Sync

> **Status:** [x] Done 2026-10-11
> **Created:** 2026-10-11
> **WORK.md task:** harness_wrapper_split T6 (PROPOSAL_V7 §6 T6 + 2026-10-10 relocations-gap note)

## Summary

The project lifecycle is SINGLE-ROOT today: `homes()` walks one `projects_root()`, so `project.py sync` against `.projects/agentx` rewrites `WORK.md ## Projects` with only that root's rows (the UC8 `OMT_WORK_PATH=tmp` clobber-dodge exists solely because of this) — which is why the 4 product project homes could never leave `.projects/meta/`. T6 makes the lifecycle multi-root: `projects_roots()` discovers `.projects/*` (except `archive`), each root gets its own `META.md`, `WORK.md ## Projects` is the cross-root union (3-col shape locked), a `move` op (ledger kind extend, state-transparent) relocates homes, `new --root` births projects in the named root, and all lookups plus harnessc's project checks resolve across roots. Env single-root mode is preserved byte-compatibly (030 idiom).

## Scope (one sentence — what "done" looks like

Done = `project.py sync` covers both homes without clobbering `WORK.md`, the 4 product projects live under `.projects/agentx/` with states preserved, per-root manifests + union WORK.md byte-verify via `harnessc check`, and goldens pin union no-clobber, per-root manifests, move + guards, WORK-row-invisibility, `--root`, cross-root lookups, env compat, and FSM transparency.

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_152.t6_multi_root_project_sync/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_152.t6_multi_root_project_sync/analysis_001_t6_multi_root.md` | [x] |
| Design | Design doc | `4.design/features/feature_152.t6_multi_root_project_sync/design_001_t6_multi_root.md` | [x] |
| Design | Operation spec | `4.design/features/feature_152.t6_multi_root_project_sync/operation_spec_t6_multi_root.md` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_152.t6_multi_root_project_sync/implementation_001_t6_multi_root.md` | [x] |
| Testing | Test report | `6.testing/features/feature_152.t6_multi_root_project_sync/test_report.md` | [x] |
