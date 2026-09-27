# Design 001 — Real trial launcher (12-trial execution engine)

> Feature: `feature_134.real_trial_launcher` · Status: DECIDED 2026-09-27 (user answers) · No launches, no tokens, no src edits by writing this file.
> Builds on: 132 `run_gate` (pre-checks) + 133 dispatcher wiring (`allowed`, `executed:false`). This feature would make `executed:true` real.

## 1. Goal

Launch 12 independent OpenCode trials for `context_strategy/run_001` with manifest-bound `[mh13.experiment]` markers, then collect/validate/compare per PROJECT.md without inventing N, smearing usage, or bypassing gates.

## 2. Non-goals (hard)

- No second scheduler; reuse `omt_net` dispatch/claim + resource places.
- No silent launches; every trial needs explicit `p` + held claims + budgets.
- No raw transcript bodies in repo; content-is-data; protected paths enforced.
- No promotion claims from N=3/rep pilot; feasibility only.

## 3. Proposed components (to be designed, not built here)

- `launcher.py`: manifest → per-trial worktree/selector (`/tmp`), order-seed shuffle, per-trial OpenCode invocation via supported execution path, marker injection, checkpoint/resume, cancel, timeout/kill, exit-code capture.
- `collector hook`: after each trial, snapshot + bind labels + per-trial usage (session-cumulative basis), store snapshot digest + source refs.
- `budget enforcer`: tokens/time/concurrency pre-check (132 gate) + live kill on overrun → named `run_budget_exceeded` + cursor, never silent truncation.
- `isolation`: per-trial worktree, env scrub, no repo writes outside allowlist, emitter identity recorded.
- `service run` (future): `allowed` + claims held + explicit_p → delegate to launcher (effectful); all else → `no_safe_launch`. Tier-2 effect classification separate from read-only ops.

## 4. Decisions (user, 2026-09-27)

1. Execution: existing META HARNESS dispatch/claim controls only (no separate subprocess credential path).
2. Budgets: small pilot — low tokens, 5min/trial, concurrency 1, instrumentation overhead tracked separately.
3. Timeout/retry: strict once — single attempt, timeout fails trial, no retry (attempt-selection rule: first-only).
4. Snapshot dest: `/tmp` per-run dir, atomic write, outside repo.
5. Claims: runner session holds 12 claims for run duration.

## 5. Exit (future)

- 12 independent captures, manifest-bound labels, quality + metrics, negatives green, replay stable, overhead disclosed, regression + e2e green, auditable bundle.
- Then `omt_complete` Design→Programming (TDD launcher with fakes, never live in unit tests)→Testing→Done.

## 6. Next

Approve open questions → finalize Design → Programming (fake-executor TDD) → guarded live run on explicit `p`.
