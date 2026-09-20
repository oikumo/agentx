# Design 001 — O4 concurrent dispatch runtime (full: planner + N-worktrees + join)

> Feature: `feature_114.concurrent_dispatch_runtime` (`major_feature`) · Phase: Design · Date: 2026-09-19.
> Consumes: Analysis 001 + O2 `apply_selection` batch shape + O3 `claim_handles` + O5 `freshness/push/projection` + 080–083 precedents + F7 lane-only reversal draft (to lock here).

---

## 1. Locked decision — F7 lane-only reversal

- **F7-revoked-lane (2026-09-19, O4 slice, locked):** F7 serial modeling-only is reversed for the dispatch lane only: ≤2 concurrent worktrees/sub-agents under `worker_slots=2` + per-task lane leases, with worktree isolation + WIP/capacity/deadlock enforcement + atomic join. `src/` edit serialism holds: `src_edit_capacity=1`, `tests_capacity=1`, receipt round-robin (one edit per file per e2e receipt), two-hats + genuine-RED + auto-revert, `uv` only. Live harness pinned/green throughout; slice violation → slice reverts, never the harness. `src/agentx/` bridge stays out (D1 — O6).
- Non-interference: no places/transitions added (Tier-3 excludes net); dispatch is runtime wiring over existing pool + resources + lanes; helpers fail-open; experiments in sidecars/worktrees.

## 2. Dispatch plan (pure, deterministic)

New `scripts/omt/net/dispatch_runtime.py` (stdlib-only, no net/ledger I/O):

- `plan_dispatch(*, claims, enabled, parallel, worker_slots, verification, integration, work_pending, work_active, revision) -> Plan | PlanRefused`
  - Inputs come from caller `state.py` at rev R: O3 `claim_handles` resolved claims, `probe.enabled[]/parallel[]`, `resources {workers 0/2, verification 0/1, integration 0/1}`, pool counts.
  - Output ordered `tasks:[{claim, task_id, lane: verification|integration|general, worktree, lease}]`, `WIP {pending, active, cap:15}`, `revision:R`, `batch_id`.
  - Refuse codes (stable strings, pre-write): `stale_revision (expected R, live R') | worker_capacity_exhausted | verification_lane_busy | integration_lane_busy | wip_cap_exceeded | unknown_claim:{id} | empty_plan`.
  - Empty `enabled[]` + no claims → `empty_plan` (no invented work, D19 kept); over-WIP (3rd claim while 2 held) → `worker_capacity_exhausted` + fresh-menu hint.
- `describe_plan(plan) -> str` — one-line summary for approval gate + ledger `reasoning`.

## 3. Worktree / lease / join shape (thin caller threading)

- Caller threading (harness-surface, receipt-disciplined, one edit per file per e2e receipt):
  1. `state.py`: `plan_dispatch` (pure) → `dispatch_claims(base, *, plan, reasoning, session, expected_revision, command_id)` — validate all at R via `probe` snapshot → acquire `worker_slots` + lane leases under existing `_transact` (reuse, no new lock) → spawn per-claim worktrees (hermetic `OMT_NET_DIR`/`OMT_LEDGER_PATH`/`OMT_COORDINATION_ROOT` tmp in tests; real `git worktree` only in dispatch lane with explicit approval) → per-task progress `fire`s carrying O5 `push/freshness/projection` envelopes → join = single `fire(work_complete --expected-revision R)` + `sync net_to_md` re-render; any task blocked/stale → refuse + release leases + re-render, zero partial marks.
  2. `cli.py`: `dispatch` subcommand (`--expected-revision` required, session whitelist per 046) printing plan JSON + join report + re-render hint; `probe` gains dispatch `plan` preview (additive `plan[]`, fail-open).
  3. `sync_md.py`: untouched except `lanes_line`/`render_tasks_block` already carry lanes; Blocked text gains `blocked_by: [worker_slots|verification|integration]` reasons from plan refuses.
- Lifts O2 `multi_mutate_deferred_o4` only inside dispatch lane: multi-claim batches allowed iff planner approves WIP/capacity at R and join stays single-commit atomic. Outside dispatch lane the O2 bound stands.
- Ledger: reuse existing kinds only (`net_claim` per reservation with `batch_id`, `net_fire` per progress/join with `selection`/`dispatch_plan`/`batch_id`, closing `net_sync`); no new `net_*` kind (replay-safe); no overlay custom keys (P10 — `derive_overlay` re-derives; annotations ride ledger fields per O2 §5 deviation).

## 4. Lane routing + WIP/deadlock enforcement

| Lane | Capacity | Route rule |
|---|---|---|
| `verification` | 0/1 | lane-tagged claims first; busy → `verification_lane_busy` refuse + re-render |
| `integration` | 0/1 | same; busy → `integration_lane_busy` refuse |
| `general` (workers) | 0/2 | `worker_slots` acquire/release per task; exhausted → `worker_capacity_exhausted` |
| WIP pool | places ≤15 | `pending+active` bound; exceed → `wip_cap_exceeded` |

- `deadlocks_complete` + `conflicts[]`/`holders[]` flow into Blocked text (G3 carried forward); `place_invariants` asserted unchanged in goldens (Tier-3).

## 5. Goldens (new file, canary-gated, TDD at Programming)

`tests/scripts/omt/test_net_dispatch_o4.py` (~14, `major_feature` TDD `testlist → red → green → refactor → done`, pytest):

- plan deterministic: empty → `empty_plan`; 2-claim hermetic bundle → 2-task ordered plan; 3rd while 2 held → `worker_capacity_exhausted`; lane busy → lane refuse; stale R → `stale_revision` + fresh hint.
- worktree isolation: hermetic tmp per task, no live net touch (rev 60 untouched in tests).
- acquire/release: 2-worker leases held during run, released on join; double-acquire refuses.
- progress envelopes: O5 `push/freshness/projection` present on progress fires.
- join: single `work_complete` commit (marking `active:N→0`, `done:+N`, rev R→R+1), `net_fire` carries `dispatch_plan`/`batch_id`, place set unchanged.
- D19 + rev-stamp preserved in describe; `uv` only.

## 6. Receipt + budget plan

- Rounds: (1) `dispatch_runtime.py` pure plan → e2e; (2) `state.py` plan/dispatch/join threading (bash-run transform, lazy import, fail-open) → e2e; (3) `cli.py` `dispatch` + probe preview → e2e; goldens after tests/ canary (`omt_skip{scope:tests, purpose:canary}`); targeted + full suite green; `check 265/0` held.
- Token/runtime: one `probe` (plan at R) + N spawns + progress fires + one join + one re-render; cap 2 bounds cost; sidecars/worktrees only; `src/agentx/` untouched.
