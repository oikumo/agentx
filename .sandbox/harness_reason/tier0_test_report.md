# Test report — feature_127.harness_reason_tier_0_renderer

> Date: 2026-09-26 · Phase: Testing · Scope: Verify tier0_demo 22/22 + S0 7/7 + checker 12/12, sandbox only, zero harness cost

## Results
- `uv run --no-sync python .sandbox/harness_reason/tier0_demo.py` → **22/22 PASS** (ir-loads, ir-verdicts d1=aligned/d2=mismatched/d3=unresolved, detailed-3rows, F-preserves, aligned-expected, refresh-compute, render-ir-plain/budget ≤40, cert-verdicts/issues/unknowns/digest/budget ≤2KB/≤30, envelope-detail_ref, digest parses, slice-first-unsupported/unresolved/unknown-node/budget ≤15)
- `uv run --no-sync python .sandbox/harness_reason/run_probes.py` → **7/7 PASS** digest `6e355d7189e13fb5` byte-stable
- `uv run --no-sync python .sandbox/harness_reason/run_checker.py` → **12/12 PASS**
- `uv run pytest -q` → **1992 passed, 2 deselected** (101.89s, pre-existing tree mods untouched)
- TS: `reason_table.ts` mirrors `startup_table.ts` (no `omt_` prefix, stdlib-only imports `@opencode-ai/plugin` + `node:fs`/`node:path`, no shared init, no registry/perm/receipt change); `npx tsc` unavailable offline (uv-only), syntax mirrors proven pattern

## Boundary held
- New: `.opencode/plugins/reason_table.ts` + `.sandbox/harness_reason/tier0_{analysis,design,demo}.md/py` + feature_127 scaffolding only
- No `src/`, no `tests/`, no `scripts/reason/`, no net/ledger writes, no `opencode.jsonc` perm change, no `uv.lock` change
- Pre-existing dirty (`toolbox/*`, `scripts/omt/net/cli.py`, `.opencode/plugins/omt_net.ts`) untouched by this feature

## Acceptance
Tier-0 carries IR+cert+UC8 as plain lines with digest/detail_ref parsing, budgets enforced (IR ≤40, cert ≤30/≤2KB, slice ≤15), truncation never passes (detail_ref envelope). Ready Done.
