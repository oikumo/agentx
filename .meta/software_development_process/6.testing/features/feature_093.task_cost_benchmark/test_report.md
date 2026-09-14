# Test Report: Task Cost Benchmark

> **Phase:** Testing — `omt_agent_guide.md §11` | **Feature:** feature_093.task_cost_benchmark
> Run everything with `uv run pytest ...` (AGENTS.md MANDATORY).

## Stage 1 — Unit / component
| Component | Normal path | Exception paths | Result |
|-----------|-------------|-----------------|--------|
| task-def validation (registry, gate annotations, think consults) | 4 tests | invalid registry shapes | [x] 4/4 |
| metrics math (TP/FP/missed/intervention/byte math, success semantics) | 3 tests | verify-fail flips success; missed never flips success (TA:120) | [x] 3/3 |
| removal accounting (saved calls/bytes, violations slipped) | 2 tests | — | [x] 2/2 |
| report render (markdown + `bench_first_numbers.v1` JSON schema) | 1 test | — | [x] 1/1 |
| deny-rule parsing (bash/read denies, $schema-URL `//` case TA:126) | 2 tests | — | [x] 2/2 |
| CLI list (8 tasks) | 1 test | — | [x] 1/1 |

## Stage 2 — Integration
- bun-gated hermetic fixture trials (`fixture_nophase` all-caught, `fixture_bugfix` green): missed=0, fp=0, success=true — [x] 2/2
- bun-gated removal variants (remove g.phase → no-phase slips; remove g.tests → canary slips; declare/canary counted saved) — [x] 2/2
- Staged receipt batch (T4-2): 3-file batch (probe.ts + cli.py + tasks.py) → boundary e2e green → `stage --clear` → `check` 0 errors → `build` OK.

## Stage 3 — System (use-case driven)
- First-numbers `--mode real` run at pinned rev `3478bb2` → `bench_first_numbers.{json,md}` (schema `bench_first_numbers.v1`): 6/6 tasks green, TP=13/FP=0/missed=0, regressions=0, success=true.
- Resume task: orientation 288–289B vs full re-read counterfactual (T3-3 win quantified in per-task `orientation_bytes`).

## Evidence

```
$ uv run pytest tests/scripts/omt/test_task_cost_benchmark.py -q
17 passed in 4.37s

$ uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q
1 passed in 0.80s

$ uv run scripts/omt/harnessc.py check
harnessc: check OK — 265 records, 0 errors
$ uv run scripts/omt/harnessc.py build
harnessc: build OK — 265 records → 5 projections

$ uv run pytest -q
2231 passed, 10 warnings in 149.90s (0:02:29)   # 2214 baseline + 17 new, 0 failures
```

## Findings fixed this session (were red in the 81b3aa1 first run)
1. `concurrent_conflict` missed=2 + assert fail — probe `execOmt` blind-`JSON.stringify` double-encoded the already-serialized `omt_net` CLI string (escaped quotes hid `'"ok": false'` refusals and the `'"ok": true'` receipt). Fix: string-or-object guard on all five plugin-tool branches (same shape as the `omt_q` branch). Plus `b_stale_claim.expected_revision: 0` resolved to the genuine setup revision in `cli.run_trial` (TA:119). Now TP=3/missed=0/success=true.
2. `harness_repair` regressions=1 — golden ran the whole `test_budget_diet.py` file; its live-check test fails in a fresh worktree on sandbox hygiene (`bench.spec.json` root_allowlist + empty-ledger project records), not on the seeded fault. Fix: golden narrowed to `::test_boundary_headroom_64_fires_65_silent` (the seeded-fault signal, TA:126). Now success=true/regressions=0.
