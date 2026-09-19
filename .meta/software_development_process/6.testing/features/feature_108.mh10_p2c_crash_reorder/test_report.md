# Test report — feature_108.mh10_p2c_crash_reorder (Slice C: crash reorder)

> Date: 2026-09-18 · Phase: Testing · Type: `minor_feature` · Project: `meta_harness_10`.

## Scope

Record-before-clear reorder in `scripts/omt/net/state.py::_transact` + `reconcile_transactions` backfill, closing the C1 crash window so every crash point between save/clear/record reconciles deterministically with idempotent replay.

## Goldens (6/6 green)

`tests/features/feature_108.mh10_p2c_crash_reorder/test_c_crash_reorder.py`:

- `TestHappyPath::test_record_then_clear_replay_no_bump` — happy path records + clears; retry replays with no rev bump.
- `TestHappyPath::test_solo_path_unchanged` — `command_id=None` takes no index, leaves no marker (D8 frozen).
- `TestCrashWindows::test_w1_crash_before_record_backfills_and_replays` — fault-injected crash before `record_command`: marker carries result → reconcile `recovered_committed_backfilled` → retry replays (exactly 1 bump). RED on old code (marker gone).
- `TestCrashWindows::test_w2_crash_between_record_and_clear_replays` — clear skipped during fire: marker (with result) + index present → reconcile committed → retry replays. RED on old code (no result in marker).
- `TestCrashWindows::test_resultless_marker_diagnoses_not_silent` — old-shape marker (no result) + live==to + no index → `diagnosis` (`txn_unindexed_commit`), marker left, nothing synthesized. RED on old code (returned committed).
- `TestCrashWindows::test_exception_after_save_leaves_marker` — `append_ledger` fails after save: marker left → `diagnosis`, never clean. RED on old code (returned committed).

RED verified before the fix (4 failed / 2 passed); GREEN after (6/6).

## Regression

- `test_net_transaction_authority` + `test_net_recovery_journal`: 17/17 green.
- `tests/scripts/omt/` (excl. e2e): 637 green.
- `test_omt_harness_e2e`: 1 passed (receipt refreshed after the one `state.py` round).
- Full suite: **1788 passed** (1782 + 6 new), 0 failures.
- `harnessc check`: 265 records, 0 errors. `harnessc build`: OK (265 → 5 projections).

## Residuals

- Crash between save and marker-result-write (single in-memory statement span, no I/O) still diagnoses fail-closed — by design, never synthesized.
- Matrix/payback (D) stays parked. No live bundle migration (no template change; rev stays 60).
