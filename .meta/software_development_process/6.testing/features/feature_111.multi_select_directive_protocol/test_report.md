# Test report — feature_111.multi_select_directive_protocol (O2, Testing)

> Date: 2026-09-19 · Phase: Testing (`minor_feature`, no TDD) · Live net untouched (rev 60 `drained_complete`; all state tests hermetic via `OMT_NET_DIR`/`OMT_LEDGER_PATH` tmp).

## Scope under test

`pick {O1 IDs} + per-id directive` grammar → pure plan (M0 at-most-one-mutate bound) → `state.apply_selection` single-commit threading → CLI `apply-selection` (CLI-only, 084 precedent, no plugin exposure).

## Results

- **New goldens `tests/scripts/omt/test_net_apply_o2.py`: 12/12 green** (canary-approved) — grammar accept ×3 / refuse ×4 (`unknown_id`, `dup_id`, `directive_without_id`, `bad_syntax`), `multi_mutate_deferred_o4` bound, annotate-only shape, threading: no-write report, `stale_revision` refuse, single-fire commit (marking `p1:1→p2:1`, rev 0→1, `net_fire` carries `selection`/`directives`/`batch_id`, place set unchanged).
- **Targeted: 54/54 green** — apply_o2 (12) + menu_o1 + sync_md + sync + history + harness_e2e.
- **Full suite: 1830 passed, 0 failed** (154s) — prior 1817 + 12 new + 1 e2e-shape delta; no regressions.
- **`harnessc check`: 265 records, 0 errors** — all budgets OK (work_md 9552/9728).

## Receipt discipline (harness-surface rounds)

1. `apply_selection.py` (new pure module) → hermetic smoke + e2e receipt.
2. `state.py` `apply_selection` (+~100 lines after `fire()`) → e2e + state/cli receipt (17 green).
3. `cli.py` `apply-selection` via one bash-run transform (handler/parser/dispatch, guard-bug fixed pre-receipt) → 37 green.
4. Warning-cleanup edit (`re.split` maxsplit remnant) → 35 green.
- Pre-existing only: 3 downstream LSP notes in `state.py` (untouched region), lazy-import LSP noise in test files (repo-wide pattern).

## Design deviation (recorded in design_001 §5)

Directives ride in the ledger record's fields, not the overlay — `save()` re-derives the overlay from the net (P10), custom keys would drop. No new `net_*` kind (replay-safe), no overlay/place/transition change (Tier-3 clean).

## Residual

- Multi-mutate batches refuse (`multi_mutate_deferred_o4`) — true parallel apply is O4 (needs F7 reversal decision).
- `proj:`/`drift:`/`unscoped:` picks are annotate/propose-only — claim handles are O3.
- `uv` only throughout.
