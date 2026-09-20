# Test report — feature_115.live_progress_full_push_join_view (O5a+b, Programming → Testing)

> Date: 2026-09-20 · Phase: Programming → Testing (`minor_feature`, no TDD) · Live net untouched (rev 60 `drained_complete`; all state tests hermetic via `OMT_NET_DIR`/`OMT_LEDGER_PATH`/`OMT_COORDINATION_ROOT` tmp; only read-only live `probe` evidence).

## Scope under test

O5a full-text push (`push.tasks_block` filled with the dry-run `sync net_to_md` Tasks text on probe/fire/claim/apply/dispatch-join, D4 proposal-only kept) + O5b join/batch progress view (deterministic text projection over `plan_to_dict`, read-only). Still serial `src/` discipline (no F7 change); dispatch commit subcommand still deferred (O4 residual kept).

## Results

- **New goldens `tests/scripts/omt/test_net_followup_o5.py`: 8/8 green** (canary-approved) — batch order ×1, fail-open ×1, tail ×1, push round-trip ×1, push-carries-text ×1, stale-refuses ×1, probe-compat ×1, join-empty ×1.
- **Targeted: 78/78 green** — e2e (1) + fresh_o5 (7) + dispatch_o4 (23) + cli + menu_o1 + claim_o3 + apply_o2.
- **Full suite: 1880 passed, 2 deselected, 0 failed** (83s) — prior 1872 + 8 new; no regressions (2 deselected = pre-existing live-smoke).
- **`harnessc check`: 265 records, 0 errors** — all budgets OK (work_md 9711/9728 — full-text push rides envelopes only, not WORK.md).
- **Live probe rev 60**: `push.tasks_block` == live Tasks text (`<!-- net_rev:60 -->` + D19 + Pool + 19 proj/9 drift/2 unscoped + Lanes); `projection[0]` unchanged (`rev 60 | marking …`); `fresh:true`; no batch lines (plan `[]` — correct fail-open).

## Receipt discipline (harness-surface rounds)

1. `freshness.py` export → smoke; helper → smoke + e2e + fresh_o5; type-narrow fixes → e2e each (gate-enforced).
2. `state.py` helpers → e2e; NetState annotations → e2e ×2; join threading → 40 targeted.
3. `cli.py` 4-site bash-transform (A1 B1 C1 DE2, counts asserted) → 78 targeted.
4. Goldens after tests/ canary (`omt_skip{scope:tests, purpose:canary}`) → 8/8 + full suite + check.
- Pre-existing only: 3 downstream LSP notes in `state.py` (untouched `_dep_status` area) + lazy-import LSP noise in the new test file (repo-wide pattern, same as `test_net_fresh_o5.py`).

## Design adherence (P10-clean)

Push text and join view are derived views (counts/text in envelopes, state in net — D20/D16 split); overlay untouched; no new `net_*` kind (replay-safe); `src/agentx/` untouched (D1); F7 lane-only lock unchanged (no new fan-out).

## Residual

- Non-pool nets render `feature_N` fallback rows in push text (no reality scan on the mutate path); live pool nets match `sync` exactly.
- `dispatch --expected-revision` commit subcommand still deferred (O4 residual); this slice only projects its plan/join.
- `uv` only throughout.
