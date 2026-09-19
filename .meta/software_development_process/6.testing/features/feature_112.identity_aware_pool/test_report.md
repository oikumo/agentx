# Test report — feature_112.identity_aware_pool (O3, Testing)

> Date: 2026-09-19 · Phase: Programming → Testing (`minor_feature`, no TDD) · Live net untouched (rev 60 `drained_complete`; all state tests hermetic via `OMT_NET_DIR`/`OMT_LEDGER_PATH`/`OMT_COORDINATION_ROOT` tmp).

## Scope under test

O1 IDs → logical `task_id` derived map + `probe.menu.claims` holder view + `apply_selection` handles view + `claim_task` reservation (gen-fenced) de-anonymizing coverage. Still serial (F7 not reversed); multi-fire still `multi_mutate_deferred_o4` (O4).

## Results

- **New goldens `tests/scripts/omt/test_net_claim_o3.py`: 12/12 green** (canary-approved) — map stable ×3 (`proj/drift/unscoped/pool`), unknown refuse, handles left-join (missing=pending, existing=work_pending), claim holds `work_active/alice/gen-1`, second-session `task_not_pending`, coverage `bindings 1/1 anonymous 0`, apply annotate report carries `handles + handles_summary`, stale-rev refuse, no-new-places, probe `menu.claims` additive.
- **Targeted: 58/58 green** — claim_o3 (12) + e2e + apply_o2 + menu_o1 + cli + claim_generation.
- **Full suite: 1840 passed, 2 deselected, 0 failed** (73s) — prior 1830 + 12 new − 2 deselected; no regressions.
- **`harnessc check`: 265 records, 0 errors** — all budgets OK (work_md 9585/9728).

## Receipt discipline (harness-surface rounds)

1. `claim_handles.py` (new pure module) → hermetic smoke + e2e receipt (1/1).
2. `state.py` `apply_selection` handles view (one bash-run multi-site transform: lazy import + annotate + mutated reports) → 27 green.
3. `cli.py` `_task_menu` additive `claims[]` (one bash-run transform) → 36 green.
4. Goldens after tests/ canary (`omt_skip{scope:tests, purpose:canary}`) → 12/12 + 58 targeted.
- Pre-existing only: lazy-import LSP noise in test files (repo-wide pattern); 3 downstream LSP notes in `state.py` untouched region.

## Design adherence (P10-clean)

Handles are a `probe`-time derived view over sidecar `task_bindings[]` (counts in net, map in sidecar+ledger — D20/D16 split); overlay file stays derived via `derive_overlay` (no custom keys, Tier-3 clean). No new `net_*` kind (replay-safe); `src/agentx/` untouched (D1).

## Residual

- Live rev 60 has no pending bindings (`tasks:[]`, `menu.claims:[]` honest) — de-anonymization proves in hermetic pool bundles; live claims appear when pending work exists.
- `proj:/drift:/unscoped:` without a binding remain annotate/propose-only (no invented tasks) — binding creation is O4 dispatch scope.
- `uv` only throughout.
