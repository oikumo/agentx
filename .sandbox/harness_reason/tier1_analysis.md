# Tier-1 Analysis — reason_check.ts advisory pilot

> Feature: feature_128.harness_reason_tier_1_advisory_pilot (minor_feature, Analysis) · Project: harness_reason · Date: 2026-09-26
> Spec: proposal §7 Tier-1 row + §11.6 ops (check/explain/compare/concretize, plan withheld) + §5 cert envelope + §§14-15 gates · Pattern: `.opencode/plugins/reason_table.ts` + `startup_table.ts` (stdlib only, no `omt_` prefix)

## Objective
Ship `reason_check.ts` — thin advisory proxy, small non-harness cost (one `reason_check: allow` line outside harnessc blocks, no @tool row/build/receipt) — that carries S0 7/7 + S1 12/12 replays through Python SSOT `scripts/reason/check.py` with per-op argv whitelist + pinned tests, TS advisory guard, §5 envelope (≤2KB + detail_ref).

## Inputs (authoritative)
- `stage0_contracts.json` (8 generators v1) + `stage0_ir.json` (Obs/D/A, HarnessObs d1/d2/d3, DetailedD, F preserves, aligned query, refresh compute, probe7 round-trip)
- `run_probes.py` 7/7 digest `6e355d71` + `run_checker.py` 12/12 + `run_composer.py` 7/7 + `run_experiment.py` 7/7 (sandbox, stdlib only)
- `reason_table.ts` Tier-0 (plain-line renderer, digest/detail_ref parse, budgets IR≤40/cert≤30/slice≤15) — reuse envelope shape
- §11.6 op table (check/explain/compare first pilot, plan only after value) + §5 cert example + UC8 slice shape
- `opencode.jsonc` perm layout (harnessc begin/end blocks for read/bash/perm; Tier-1 allow line must sit outside)

## Gaps vs current
- No `scripts/reason/` SSOT exists (no cli/check, elaborate, kernel, router, certs). No `reason_check.ts` proxy. No argv whitelist pins.
- Tier-0 formats IR/certs but executes no checks; Tier-1 must execute check/explain/compare/concretize via SSOT without widening enum, importing src/, or writing net/ledger.

## Exit criteria (Analysis → Design)
- Closed enum fixed (check|explain|compare|concretize, plan withheld) + per-op argv shape fixed
- SSOT file map fixed (check.py + minimal elaborate/kernel/router/certs for S0/S1 replay)
- §5 envelope shape fixed (verdicts + digests + issues/unknowns/derivation + detail_ref, ≤2KB)
- Design will list ops + I/O + whitelist + guard + tests (whitelist pins, probe fixtures, cert replay)

## Boundary (D2/D3/D5 holds)
- Sandbox + `scripts/reason/` + `tests/scripts/reason/` + `.opencode/plugins/reason_check.ts` (+ `lib/reason/` only if outgrows one file) + one opencode.jsonc allow line outside harnessc blocks. No `src/` imports, no net/ledger writes, no token moves, no grants, no `omt_` prefix, no @tool row/build/receipt, no `uv.lock` change, stdlib only.
- If pilot cannot carry probes 1–7 without widening enum, adding src/ imports, or touching net/ledger → shrink to Tier-0 (kill line).
