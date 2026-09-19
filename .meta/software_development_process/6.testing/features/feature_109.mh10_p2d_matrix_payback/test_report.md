# Test report — feature_109.mh10_p2d_matrix_payback (Slice D: matrix/payback)

> Date: 2026-09-19 · Phase: Testing · Type: `minor_feature` · Project: `meta_harness_10`.

## Scope

Allow/deny matrix on real gate paths (V1–V5 allow, I1–I8 deny fail-closed) + payback measurement protocol + net-zero/diet math. Tests-only: no `state.py` behavior change, no template/bundle change, no live-gate registration (rev stays 60).

## Goldens (13/13 green)

`tests/features/feature_109.mh10_p2d_matrix_payback/test_d_matrix.py`:

- V1 `test_v1_fire_receipt_allows_concurrent_edit` — concurrent + receipt → OK.
- V2 `test_v2_derived_reads_stay_non_firing` — sync/menu rows `no` + derived-read + OMISSION (never FIRED).
- V3 `test_v3_solo_path_unchanged` — `command_id=None` fires, no marker (D8 frozen).
- V4 `test_v4_reconciled_retry_replays` — same `command_id` retry replays, no second bump.
- V5 `test_v5_ledger_evidence_reader_accepts_shaped_rows` — shaped rows ok, fired/fallback counted.
- I1 `test_i1_no_receipt_denies_concurrent_edit` — `ERR_NET_NOT_ENABLED`.
- I2 `test_i2_stale_rev_denies` — `ERR_NET_STALE_REV`.
- I3 `test_i3_drift_denies` — drift + conflicts → `ERR_NET_DRIFT_CONFLICT`.
- I4 `test_i4_net_down_denies_without_breakglass` — `ERR_NET_DOWN`.
- I5 `test_i5_absent_breakglass_never_allows` — absent grants nothing; present grants OK even when down.
- I6 `test_i6_task_fence_fail_closed` — unreadable bundle → `ERR_NET_DOWN`; `stale_generation`/`not_owner`/`workspace_mismatch` pins present (full fences in feature_080/081 suites).
- I7 `test_i7_lane_over_cap_never_silent` — lane rows `yes-B3b-template`; keyless row is offender.
- I8 `test_i8_resultless_commit_diagnoses` — old-shape marker + live==to + no index → `txn_unindexed_commit`, marker left.

GREEN on first run (13/13, 0.07s) — current `gate.py`/`state.py` already implement the deny contract; the matrix proves it rather than fixing it.

## Regression

- `test_net_transaction_authority` + `test_net_recovery_journal`: 17/17 green.
- `tests/scripts/omt/` (excl. e2e): 637 green.
- `test_omt_harness_e2e`: 1 passed (receipt refreshed after the tests-only round).
- Full suite: **1801 passed** (1788 + 13 new), 0 failures — first full run showed 1 flake (`test_nav_reminder_deferred_after_nav_first`, passes in isolation + in file + on rerun full green); rerun 1801/1801.
- `harnessc check`: 265 records, 0 errors. `harnessc build`: OK (265 → 5 projections).

## Residuals

- Payback (a) needs wild sessions (N≥10): setup vs avoided-rework ledger not yet accumulated — verdict stays keep-advisory until payback > 0 surviving support.
- No live bundle migration (no template change; rev stays 60). No new gates/tools (net-zero 10/12 holds; diet headrooms unchanged).
