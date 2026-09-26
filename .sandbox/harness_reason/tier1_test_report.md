# Test report — feature_128.harness_reason_tier_1_advisory_pilot

> Date: 2026-09-26 · Phase: Testing · Scope: Verify tier1 demo 13/13 plus reason tests 14/14 plus S0 7/7 plus S1 12/12, advisory boundary no net ledger src writes

## Results
- `uv run --no-sync python .sandbox/harness_reason/tier1_demo.py` → **13/13 PASS** (ir-loads, verdicts d1=aligned/d2=mismatched/d3=unresolved, mismatch, d3-unknown, envelope, budget, concretize-4, over-bound, cli-check/explain/compare/concretize, plan-withheld)
- `uv run --no-sync pytest tests/scripts/reason/ -q` → **14 passed** (whitelist 4 + probes 5 + replay 5)
- `uv run --no-sync python .sandbox/harness_reason/run_probes.py` → **7/7 PASS** digest `6e355d7189e13fb5` byte-stable
- `uv run --no-sync python .sandbox/harness_reason/run_checker.py` → **12/12 PASS**
- `uv run pytest -q` → **2006 passed, 2 deselected** (107s, pre-existing tree mods untouched)
- TS: `reason_check.ts` closed enum + whitelist + advisory guard + `uv run scripts/reason/check.py` proxy + §5 plain lines; `opencode.jsonc` one `reason_check: allow` line outside harnessc blocks

## Boundary held
- New: `scripts/reason/check.py` + `elaborate/kernel/router/certs.py` + `.opencode/plugins/reason_check.ts` + `tests/scripts/reason/test_*` + `.sandbox/harness_reason/tier1_{analysis,design,demo}.md/py` + feature_128 scaffolding + one opencode.jsonc allow line
- No `src/`, no net/ledger writes, no token moves, no grants, no `omt_` prefix, no @tool row/build/receipt, no `uv.lock` change, `plan` withheld
- Pre-existing dirty (`toolbox/*`, `scripts/omt/net/cli.py`, `.opencode/plugins/omt_net.ts`) untouched by this feature

## Acceptance
Tier-1 carries S0/S1 replays via SSOT with whitelist pins and §5 envelopes, guard rejects writes/mints/plan, truncation never passes (detail_ref envelope). Ready Done.
