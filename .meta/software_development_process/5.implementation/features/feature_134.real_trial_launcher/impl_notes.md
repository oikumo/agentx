# Implementation notes — feature_134.real_trial_launcher (fake-executor core)

> 2026-09-27 · RED `test_fake_plans_12_in_order` → GREEN (`launcher.py` new) → REFACTOR → SYNC → DONE. No launches, no tokens, fakes only.

## What changed

- `scripts/session_inspect/launcher.py` NEW (stdlib-only): `plan_trials` via `manifest.expand_matrix` (12 trials, seed 0 in-order); `dispatch_fake(trial, executor)` once + `/tmp` stub isolation; `enforce_timeout` 300s strict-once → `timeout_failed`; `collect_fake` usable/independent_n; `run_fake` via 132 `gate_run` (budgets/isolation/claims/explicit_p) — refusals map to `no_safe_launch`, allowed → `{allowed:True, n_trials:12, executed:False, fake_n:12}`.
- Failure vocabulary preserved (closed): executor exception → `trial_incomplete`; manifest problems propagate `manifest_invalid`; timeout is an outcome string, not a new Finding.
- Tests `tests/scripts/session_inspect/test_fake_launcher.py` (4): plan 12 in-order + unique; dispatch sequential once-each; timeout strict-once no-retry; run_fake refuses without gate.
- Bridge `tests/features/feature_134.real_trial_launcher/test_bridge_134.py` (2): plan 12 + gated run (refuse/allow, `executed:False` always).

## Discipline

- `uv` only; `service.py`/`run_gate.py`/`manifest.py` untouched; `feature_129/130/131/132/133` untouched; synthetic only; no subprocess/threads/sleeps.
