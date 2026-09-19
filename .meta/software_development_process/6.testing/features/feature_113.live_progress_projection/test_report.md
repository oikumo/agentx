# Test report — feature_113.live_progress_projection (O5, Programming → Testing)

> Date: 2026-09-19 · Phase: Programming → Testing (`minor_feature`, no TDD) · Live net untouched (rev 60 `drained_complete`; all state tests hermetic via `OMT_NET_DIR`/`OMT_LEDGER_PATH`/`OMT_COORDINATION_ROOT` tmp).

## Scope under test

Menu-time freshness (`probe` before present) + re-render push after each fire/claim + minimal live view reusing studio projection. Still serial (F7 not reversed); multi-fire still `multi_mutate_deferred_o4` (O4).

## Results

- **New goldens `tests/scripts/omt/test_net_fresh_o5.py`: 7/7 green** (canary-approved) — fresh pure ×3 (is_fresh, hint+push, projection_lines), probe push/freshness/projection, stale-refuse, state helpers, no-new-places.
- **Targeted: 62/62 green** — fresh_o5 (7) + menu_o1 + claim_o3 + apply_o2 + cli + state + e2e.
- **Full suite: 1847 passed, 2 deselected, 0 failed** (79s) — prior 1840 + 7 new; no regressions.
- **`harnessc check`: 265 records, 0 errors** — all budgets OK (work_md 9623/9728).
- **Live probe rev 60**: `push {net_revision:60}`, `freshness {fresh:true}`, `projection ["rev 60 | marking …", "lanes …"]` honest (no pending bindings).

## Receipt discipline (harness-surface rounds)

1. `freshness.py` (new pure module) → hermetic smoke + 26 green receipt.
2. `state.py` `freshness_for_state` + `push_for_state` (one bash-run transform, lazy import, fail-open) → 33 green.
3. `cli.py` `_probe/_fire/_apply_selection/_task_envelope` additive `push/freshness/projection` (one bash-run transform) → 47 green + live probe proof.
4. Goldens after tests/ canary (`omt_skip{scope:tests, purpose:canary}`) → 7/7 + 62 targeted + e2e refresh per round.
- Pre-existing only: lazy-import LSP noise in test files (repo-wide pattern).

## Design adherence (P10-clean)

Freshness/push are `probe`-time derived views (counts in net, text in render — D20/D16 split); overlay file stays derived via `derive_overlay` (no custom keys, Tier-3 clean). No new `net_*` kind (replay-safe); `src/agentx/` untouched (D1).

## Residual

- `push.tasks_block` empty in CLI envelopes (full `sync net_to_md` render stays caller-applied per D4 proposal-only) — full text push is O5-follow-up if measured need appears.
- Live view is text `projection_lines` (no slider interaction) — slider/join is O4 scope.
- `uv` only throughout.
