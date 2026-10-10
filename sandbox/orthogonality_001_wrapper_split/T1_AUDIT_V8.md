# T1_AUDIT_V8 — legacy slug + test-file mapping (sandbox only, no moves)

> Status: **draft audit** (2026-10-10, sandbox only). No files moved, no renames,
> no ledger writes, no `tests/` canary consumed (nothing touched outside `sandbox/`).
> Grandfather rule: everything stays where it is until T2 goldens + T3 lanes land;
> this table is the mapping T1 requires before any move. Counts re-measured
> 2026-10-10T17:40Z (see `EXECUTE_V8.md` §1); re-count at signing.

## 0. Decisions carried (close what V7 left open where evidence now exists)

- D-tri (Q2 CLOSED per V7 §1): `tools/petri-net-studio/` = product;
  `shared/petri-net/` = product-owned contract (FORMAT.md LOCKED v1 + schema +
  `conformance/` + `examples/`); studio PROJECT.md carries a conforming `bridge:` tag
  **only** for harness-driven analysis slices. Four legs covered, no third home.
- File→tool map (V7 §3 admission CLOSED by this audit): `phase/skip/complete/tdd`
  are all provided by `.opencode/plugins/omt_enforcer.ts` (gate + tool provider):
  `omt_enforcer.ts:17,28-29` declares `omt_phase/omt_skip/omt_complete` as custom tools;
  `omt_enforcer.ts:18,47` imports `createTddTools` from `../lib/enforcer/tdd_hats`
  (feature_016 two-hats + TDD tools). The 11 plugin files = enforcer (gate + 4 tools)
  + 6 `omt_*` feature plugins (`kb_nav,nav,net,q,session,status,think`) + `reason_check/table`
  + `startup_table`. "14 tools in 11 files" now fully cited — drop the admission line at promotion.
- Language: "runtime-orthogonal, dev-coupled" everywhere; bare "orthogonal" rejected in review.

## 1. Legacy slug mapping (`.projects/meta/` 25 projects + `META.md` = 26 entries)

Rule going forward: new harness slugs end `_meta`; legacy `meta_*` grandfathered, no renames;
product homes under `.projects/agentx/`; bridge work under owner side + conforming `bridge:` tag
(standalone token in Decisions log — 0 conforming tags today, 1 prose hit `meta_harness_11:50`).

| Slug (under `.projects/meta/`) | Proposed home | Note |
|---|---|---|
| `agentx_1_0_0` (draft) | `.projects/agentx/` (product) | pending-moves row; move needs `link <feature> <project> --origin manual` + ledger record; deferred to UC8 |
| `agentx_concurrent_development` | `.projects/agentx/` (product) | same as above |
| `rag_v2` | `.projects/agentx/` (product) | same as above |
| `petri_net_studio` | `.projects/agentx/` (product) + `tools/`-as-product + `shared/`-as-contract | D-tri; conforming `bridge:` tag only for harness analysis slices |
| `petri_net_library` | REVIEW (likely product; not in pending-moves draft) | T1 close-out decides: product move or bridge tag; do not silently grandfather under `meta/` |
| `feature_kb_akb` | REVIEW (app KB; bridge candidate) | application knowledge base spans product docs + harness `kb_nav`; T1 close-out assigns with tag |
| `harness_reason`, `meta_harness_2/3/4/5/6/7/8/9/10/11/12/13/14/15`, `meta_harness_concurrent`, `net_enforced_harness`, `project_lifecycle`, `workflows` | `.projects/meta/` (harness, grandfathered) | legacy `meta_*` prefix accepted forever; no renames (WORK.md + ledger churn) |
| `.projects/agentx/META.md` | placeholder + populated 4-row pending-moves draft | unchanged; moves deferred with approval only |

## 2. Test-file mapping (grandfather list — no silent moves)

| Area | Count (2026-10-10) | Proposed lane | Disposition |
|---|---|---|---|
| `tests/controllers,views,model,unit` | product dirs (present) | `tests/agentx/` | grandfathered; migrate under Oracle exemption manifest in T1–T3, no silent moves |
| `tests/scripts/` (`omt/` 71 + `toolbox/` 6 + `reason/` + `session_inspect/` = 104) | 104 files | `tests/harness_meta/` | all-harness (omt gate + toolbox + reason Tier-1 + session Tier-2); grandfathered |
| `tests/features/` 52 dirs | 100 files | MIXED (bucket below) | grandfathered; per-dir buckets below, per-file look at T1 close-out |
| `tests_automated/` | 1 (`__init__.py`, no tests) | EXCLUDE | empty package marker; no lane |
| `tests/test_sandbox/` | 1 (`test_program/memory.json`, fixture) | EXCLUDE | data only; no lane |
| root `toolbox/` | 0 co-located `test_*.py` | EXCLUDE (covered via `tests/scripts/toolbox/`) | no moves |
| `tools/*/tests` (petri-net-studio) | 15 (engine 6 + state 1 + ui 4 + dashboard 3 + independence 1) | product lane | D-tri exemplar; T2 template (`check-independence + conformance`) |
| `.sandbox/` | 0 files | EXCLUDE | empty; no lane |
| `.workflows/` (`agentx/`, `app_knowledge_base/`, `meta_harness/`, `META.md`) | catalog | NEITHER (above harness) | `# Rules` line 1 follow-vs-override; scope line only, never owned by either lane |
| build roots (`pyproject.toml/uv.lock/.venv/.python-version`) | shared | SHARED prerequisite | neither lane claims; rename-away proofs depend on them staying put |

`tests/features/` 52-dir buckets (proposed, per-file look at close-out):
- Product bucket (tests/agentx): `feature_007,010,013,018,019,024,025,027,029,031,034,035,036`
  (agent/intelligent-agent, demo screen, model selector, react, coding ×2, no-tui, context-window,
  rag_v2 ×2, petri_net_library, studio editor/analysis/graph).
- Harness bucket (tests/harness_meta): `feature_016,026,039,040,041,050,051,052,053,054,055,056,057,
  058,059,060,061,062,063,064,066,103,104,105,106,107,108,109,114,118,131,132,133,134,135`
  (tdd, omt_q ×3, net engine/composition/concurrency ×3, net-as-gate + ledger isolation + version
  canary + predicates + fast-path + preflight + skip/phase hygiene + budget meter + thought review +
  tiered template + dangling + nav cache + preflight-on-declare + kb sticky + work-truth + think batch +
  mh10 p2 ×7 + concurrent dispatch + mh11 worktree + session-inspect ×5).
- Review bucket (bridge or per-file split): `feature_015` (security/quality spans both),
  `feature_030` (project_lifecycle = homes system), `feature_043` (meta_net_dashboard = net + UI),
  `feature_kb_akb` (app KB = product docs + harness kb_nav).

## 3. T1 row #1 + bridge backlog + projection re-pin

- Row #1: `src/agentx/ui/test_omt_mvc_gate.py` (2 lines: real
  `from agentx.model.session import Session` + `print('ok')`, 0 test fns, dead code under `src/`
  with misleading `test_` prefix). Disposition: DELETE (no coverage depends on it; collected by no
  suite) — execution needs your go (touches `src/`, phase already declared this session).
  Alternative: move to `tests/harness_meta/` with a real assertion + tests canary. Until closed,
  UC1 Post stays self-falsified — declared, not hidden.
- Conforming-`bridge:`-tag backlog: 0 exist; 1 prose non-hit (`meta_harness_11:50`).
  T1 close-out greps the pinned format (standalone token in Decisions log), never substring.
- Projection re-pin (Q4, `.meta/.omt/` now 12 entries): pin as read-only projections of
  `ledger.jsonl`: `WORK.compiled.md`, `nav.index.jsonl`, `harness.ir.json`,
  `net_state.sidecar.json`, `WORK.md ## Projects` + "read-only = no writes outside append" test in T2.
  New files (`harness.report`, `kb.index.jsonl`, `kb.ir.json`, `ledger-202610.jsonl`,
  `omt_harness_e2e_last_run.json`) get a scope-or-exclude line at T2 pin time — never silently
  added to the contract.

## 4. What T1 close-out needs (not done in this sandbox pass)

Per-dir `tests/features/` review-bucket resolution + full per-file table sign-off, `bridge:` backlog
groomed, D-tri + file→tool map carried into `SECTION:split_proof` doc, newcomer-cost check per move
("student still `uv run agentx` → `c` with zero harness knowledge?"), `omt_session` evidence cite.
Moves/migrations run under Oracle exemption manifest with `omt_skip{scope:tests}` canary each —
on your explicit go only.
