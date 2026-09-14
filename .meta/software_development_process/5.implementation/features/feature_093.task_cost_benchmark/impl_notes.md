# Implementation notes — feature_093.task_cost_benchmark

> Date: 2026-09-14 · Scaffolded by `new_feature.py implementation` (feature_090).
> Resume close-out of the 2026-09-14 paused session (`.sandbox/pause_2026-09-14.md`).

## What changed

- `scripts/omt/bench/probe.ts` — `execOmt` string-or-object guard on the `omt_status`/`omt_think`/`omt_nav`/`omt_kb_nav`/`omt_net` branches (was blind `JSON.stringify`, which double-encoded the already-serialized `omt_net` CLI string and hid engine refusals/receipts from metrics + asserts).
- `scripts/omt/bench/cli.py` — `run_trial` resolves the `b_stale_claim.expected_revision` TA:119 placeholder to the genuine `setup_revision` after `setup_real` (was literal `0`, a real mismatch check but not the genuine stale flow).
- `scripts/omt/bench/tasks.py` — `harness_repair` golden narrowed to `test_budget_diet.py::test_boundary_headroom_64_fires_65_silent` (full-file run carries a live-check test that fails on sandbox hygiene, not on the seeded `BUDGET_DIET_PROXIMITY` fault).
- `.meta/.../feature_093.task_cost_benchmark/bench_first_numbers.{json,md}` — refreshed first-numbers at rev `3478bb2`: 6/6 green, TP=13/FP=0/missed=0, 66 steps / 21 harness calls / 140218 io_bytes / 35053 tokens_est.
- Unrelated live change (user, kept): `opencode.jsonc` gains `"git worktree *": "allow"` (was a stray `""` mid-edit that briefly broke deny parsing; user repaired before the final run).

## Discipline notes

- Receipt round-robin respected for harness-surface files: `harnessc stage --feature feature_093.task_cost_benchmark` over the 3 bench files → ONE edit per file → goldens → `run-all` → boundary e2e green → `stage --clear` → `check` 0 errors + `build` OK.
- Phase re-declared minor_feature/Programming + tests canary re-recorded on resume (D6).
- Think-gate consults recorded (analysis_001 16 thoughts, goldens file, all three edited bench files — 0 thoughts each, expected).
- KB consult: no bench records (expected, feature_091 precedent).
- `uv` only (no bare python/pip/pytest).
- Housekeeping: removed the kept debug worktree + `git worktree prune` (a kept worktree once blocked `setup_real` with "already registered" — same trap as the prior session).
