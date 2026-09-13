# Test report — feature_078.op_graph_transitive_risk (T1-3)

> Date: 2026-09-13 · Type: minor_feature · Status: PASS

## Scope verified

- `omt_q{op:graph, symbol, depth?, as_of?}` — transitive risk over `kb.ir.json` `refs[]` + thoughts join (mh2 U5 + HQL Phase-C, bindings-first slice).
- BFS from `symbol` following `refs[]` up to `depth` (clamped 1..3, default 1); `depth_sets[d]` = nodes first reached at exactly depth d; `risk_nodes` = union excluding the root; `related_thoughts` = thoughts whose text mentions the symbol or any risk node (capped at 5, 120-char truncation, same shape as `summarizeThoughts`).
- `as_of` replays `kb.ir.json` + thoughts at the commit (`loadKbIrAt`/`readThoughtsAt`, no working-tree reads); envelope marks `as_of_scope: "replayed:kb+thoughts"`.
- Fail-open: unknown symbol → empty risk + `error`; missing symbol → `error` envelope; every response carries `as_of_commit` + `kind:"q"` ledger append (`op_set: ["T1-3"]`).
- **HQL grammar explicitly NOT built** — `op:hql` stays an unknown op (pinned by golden); grammar work stays parked until graph proves novel asks (per T1-3 acceptance).

## Tests

- RED→GREEN: `tests/scripts/omt/test_omt_q.py::TestOpGraphTransitiveRisk` — 3 goldens over a seeded 4-node kb (`g.a → {g.b, g.d}`, `g.b → g.c`) + 1 seeded thought mentioning `g.c`:
  1. `test_graph_depth1_returns_direct_refs_only` — risk = `{g.b, g.d}`, `depth_sets["1"]` exact. 
  2. `test_graph_depth2_adds_transitive_and_thought_join` — risk = `{g.b, g.c, g.d}`, `depth_sets["2"] == ["g.c"]`, thoughts join surfaces the `g.c` mention. **(the T1-3 golden: depth-1 vs depth-2 differ correctly)**
  3. `test_graph_unknown_symbol_fail_open_and_no_hql` — unknown symbol → empty risk + `error`; raw-probe asserts `op:hql` returns the plain-text `unknown op` dispatcher message (non-JSON path, read without `json.loads`).
- Live smoke (real kb): `doc.mvcpp` depth-1 = `{doc.dp, doc.partner, flow.boot}`; depth-2 adds `{doc.persist_convention, doc.provider}` — sets differ correctly on the live 515-record / 528-ref graph.
- Regression: `test_omt_q.py` + `test_omt_q_audit.py` + `test_omt_q_state_summary.py` → **27/27 pass**; `tests/scripts/omt/` (excl. live guards) → **483 pass**; live guards → **2 pass**.
- Boundary e2e: `tests/scripts/omt/test_omt_harness_e2e.py` → **1/1 pass** (fresh receipt covers the 3-file staged batch).
- `harnessc check` → 0 errors; `harnessc build` → OK (tool_args 2367/2400, tool_schemas 1780/1792, all budgets green).

## Incidental repair (feature_059 pin re-measure, same class as feature_077)

- `test_tight_budgets_unchanged` failed post-change on `nav_index` 63931 > 63929 (+2B in-place text drift of the `tool.omt_q` nav record — kinds unchanged: doc/flow/xref/tool/msg, the feature_059 contract holds).
- Re-measured `_sizes()` at HEAD and re-pinned: `NAV_INDEX_CEIL 63929→63931`, `TOOL_ARGS_CEIL 2284→2367` (deliberate graph `symbol`/`depth` describes; harness `@budget tool_args` deliberately grown 2304→2400 in the same `.omt` edit), `TOOL_SCHEMAS_CEIL 1778→1780` (compressed description +2B; harness ceiling 1792 still holds). **KNOWN stays empty (A1 invariant)**, no allowlist added.

## Full suite

- `uv run pytest -q`: **2088 passed, 0 failed** (includes the re-pinned budget test and the live-opencode guards, which passed in 55 s this run).

## Notes

- Discipline notes for the next slice: (1) `omt_skip{scope:tests}` must be the LATEST session unlock at tests-edit time — a later `omt_phase` record shadows it (`getActiveUnlock` latest-wins; re-skip after declaring Programming). (2) Editing `.meta/META_HARNESS.omt` after `harnessc stage` invalidates the stage (`policy_ver` content binding) — re-`build` + re-`e2e` before the next harness-surface edit (D-bar working as designed). (3) `BUN`-probe tests that assert the plain-text unknown-op path must read raw stdout (`json.loads` fails by design on non-JSON dispatcher messages).
- LSP noise (pre-existing classes, runtime-fine): `BUN: str | None` in the new graph tests (same `subprocess.run([BUN, …])` shape as the existing probes); unresolvable `import harnessc` in `test_budget_pins.py` (sys.path-injected, noted since feature_077).
