# Implementation notes — feature_132.pilot_launch_path (run-gate slice)

> 2026-09-27 · design_001 + operation_spec_001_run_gate · testlist 5 → RED (1 node, batch-N grouped per S3/S4 precedent) → GREEN (run_gate.py) → REFACTOR → SYNC → DONE. No launches, no tokens.

## What changed (NEW, stdlib-only, no launches)

- `scripts/session_inspect/run_gate.py` — `check_manifest` (strict validate), `check_isolation` (protected `.env|opencode.db|.git/` → `isolation_unavailable`), `check_budgets` (tokens/time_s/concurrency required → `budget_missing`), `gate_run` (manifest→isolation→budgets→claims+explicit_p; refusals `manifest_invalid|isolation_unavailable|budget_missing|no_safe_launch`; `{allowed, n_trials:12, executed:False}` only when all pass).
- `tests/scripts/session_inspect/test_run_gate.py` (5) — invalid manifest, protected dest, missing budgets, no-claims/no-p → `no_safe_launch`, all-pass → allowed 12 trials `executed False`.
- Bridge `tests/features/feature_132.../test_bridge.py` (2) — gate refusal + allow paths from canonical location.

## Discipline

- `uv` only; `feature_129/130/131` untouched (contracts reused); fixtures synthetic; batch-N warning noted (5 tests/file grouped, S3/S4 precedent).
- TDD two-hats respected; `service.py experiment run` still `no_safe_launch` (gate_run not wired to dispatcher in this slice).
