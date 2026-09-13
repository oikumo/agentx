# Feature 078: Op Graph Transitive Risk

> **Status:** [x] Done 2026-09-13 (mh8 T1-3)
> **Created:** 2026-09-12
> **Project:** meta_harness_8 (T1-3 `op:graph` transitive risk → HQL gate)

---

## Summary

`omt_q{op:graph, symbol, depth?, as_of?}` — transitive risk over `kb.ir.json` `refs[]` plus thoughts join. BFS depth 1..3 from the symbol; depth-1 vs depth-2 risk sets differ correctly (live: `doc.mvcpp` depth-2 adds `doc.persist_convention` + `doc.provider`). HQL grammar explicitly NOT built (parked until graph proves novel asks).

## Scope (one sentence — what "done" looks like)

T1-3 ships `op:graph` with depth-1 vs depth-2 golden + thoughts join + unknown-symbol fail-open + no-HQL pin, suite 2088 green, budgets green.

## Task type

minor_feature (declaration only per §12; no design doc)

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_078.op_graph_transitive_risk/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_078.op_graph_transitive_risk/analysis_001_*.md` | [x] decl-only (scope in FEATURE.md + PROJECT.md T1-3 row) |
| Design | Design doc | `4.design/features/feature_078.op_graph_transitive_risk/design_001_*.md` | [x] decl-only (minor_feature, mechanism in scope) |
| Implementation | Impl notes | `5.implementation/features/feature_078.op_graph_transitive_risk/` | [x] `.opencode/plugins/omt_q.ts` foldGraph + omt_graph + dispatcher; `.meta/META_HARNESS.omt` tool desc + tool_args budget 2304→2400 |
| Testing | Test report | `6.testing/features/feature_078.op_graph_transitive_risk/` | [x] test_report.md — 3 goldens + 2088 suite green |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
