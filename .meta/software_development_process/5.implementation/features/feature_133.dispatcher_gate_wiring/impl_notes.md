# Implementation notes — feature_133.dispatcher_gate_wiring (dispatcher wires run_gate)

> 2026-09-27 · testlist 3 → RED → GREEN (service.py run wires run_gate) → REFACTOR → SYNC. No launches, no tokens. S5/S6 contracts preserved (run refusals stay `no_safe_launch`, detail keeps cause).

## What changed

- `scripts/session_inspect/service.py` `experiment run`: parses manifest JSON, reads `budgets|isolation|claims|explicit_p` from manifest body (OP_ARGS unchanged, no harness-surface edit), calls `run_gate.gate_run`; `allowed` → `{ok:True, result:{allowed, n_trials:12, executed:False}}`; any refusal → `{ok:False, reason:no_safe_launch, detail:<cause>, executed:False}`.
- `scripts/session_inspect/run_gate.py` reused unchanged (132).
- Tests `test_dispatcher_gate.py` (3): invalid manifest → `no_safe_launch`+detail `manifest_invalid`; no claims/p → `no_safe_launch`; full gate pass → allowed 12 `executed False`.
- S5 `test_run_gated` + S6 `test_s6_pilot_dry_run` still green (62 passed slice).

## Discipline

- `uv` only; OP_ARGS/`.ts` untouched (no pin churn); `feature_129/130/131/132` untouched; synthetic only; batch-N noted.
