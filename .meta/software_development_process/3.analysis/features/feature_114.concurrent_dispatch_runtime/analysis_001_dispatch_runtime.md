# Analysis 001 — O4 concurrent dispatch runtime (scope for approval)

> Feature: `feature_114.concurrent_dispatch_runtime` (`major_feature`, project `meta_harness_11`) · Phase: Analysis · Date: 2026-09-19.
> Resumes: PROJECT.md §Plan O4 + gaps doc G12/G13 + F7 + features 080–083 + M0 complete (O1 110 + O2 111 + O3 112 Done, O5-slice 113 Done, rev 60 `drained_complete`, suite 1847, `check 265/0`).

---

## 1. Problem (reproducer)

M0 gives a selectable whole-project menu with atomic apply but execution stays serial:

- Live `probe rev 60`: `marking {agent_attention:1, src_edit_capacity:1, tests_capacity:1, worker_slots:2, work_done:7, pending:0, active:0}`, `enabled:[]`, `observation:drained_complete`, `parallel:[]`, `menu.next:none`, `coverage work_done anonymous 7/7` (pre-O3) → post-M0 `menu.claims:[]` honest, `fresh:true`, `push {net_revision:60}`.
- O2 `apply_selection` resolves `pick {id,…}` to a plan but enforces at-most-one-mutate (`multi_mutate_deferred_o4`): batch with 2 fires refuses — first fire bumps rev 60→61, second is stale or blocked by `agent_attention` (F7 cap 1). No bulk-claim, no dispatch plan, no fan-out.
- Features 080 (`task_claim_generation`), 081 (`worktree_execution_isolation`), 082 (`two_worker_capacity_scope_arbitration`), 083 (`verification_integration_lane`) exist per ledger (meta_harness_8 complete) but are not wired into a `menu → dispatch N workers → join` runtime: `parallel:[]` empty in every observed probe; `sync`/`splice` never emit a dispatch plan; no per-task worktrees, no progress `fire`s, no completion join that `fire(work_complete)` + re-render.
- F7 (meta_harness_concurrent PROJECT.md Feasibility): "`agent_attention` = 1 token means the metanet is a decision-support model for a single-threaded agent, not a scheduler… the agent still executes serially… deliverable is concurrency modeling, not concurrent execution." O4 explicitly requires reversing F7 for the dispatch lane with a new locked decision (PROJECT.md D2, gaps doc O4 sketch).

Reproduce: hermetic pool bundle with 2 pending O3 claims at rev R → `apply_selection` with 2 mutating picks → `multi_mutate_deferred_o4` refuse; `probe.parallel:[]`; no worktrees, no join.

## 2. What O4-full must prove (oracle)

- **Dispatch planner (pure, deterministic, stdlib-only):** `enabled[]/parallel[]` + O3 claim handles + verification/integration lane capacities + `worker_slots=2` → dispatch plan: ordered `[{claim, worktree, lane, capacity_lease}]` with WIP bound enforced (pending+active ≤ places cap 15; workers ≤ 2; verification 0/1, integration 0/1). Empty `enabled[]` → empty plan (no invented work, D19 kept). Stale-R plan refuses with fresh `probe` + menu re-render (G4 batch guard extended from O2).
- **N worktrees/sub-agents → join → `work_complete`:** per-claim isolated worktree (081 precedent: git worktree per claim, hermetic `OMT_NET_DIR`/`OMT_LEDGER_PATH`/`OMT_COORDINATION_ROOT` tmp in tests, real worktrees only with explicit lane approval), 2-worker arbitration (082: acquire `worker_slots` + `agent_attention` lane lease per task, release on join), verification/integration lane routing (083: lane-tagged tasks, lane capacity 0/1 each), per-task progress `fire`s (O5 `push`/`freshness`/`projection` envelopes reused), completion join = all-or-nothing `fire(work_complete --expected-revision R)` + `sync net_to_md` re-render + ledger `net_*` (`selection`/`batch_id`/dispatch plan, no new kind — replay-safe).
- **WIP/capacity/deadlock safety:** planner refuses over-WIP (3rd claim while 2 workers held → `blocked_by: [worker_slots]` with re-render); `deadlocks_complete` + `conflicts[]`/`holders[]` flow into Blocked text (G3 lane synthesis carried forward from O1 `lanes_line`); `place_invariants` hold (no new places/transitions — Tier-3 excludes net; dispatch is runtime wiring, not structure).
- **F7 lane-only reversal (new decision, locked here):** `agent_attention=1` serial holds for `src/` edits (two-hats + receipt discipline unchanged); dispatch lane may fan-out ≤2 worktrees/sub-agents under `worker_slots=2` arbitration with sidecar/worktree isolation; live harness pinned/green throughout (`check 0 + build OK + suite + KNOWN empty`); slice violation → slice reverts, never the harness. Full `src/agentx/` bridge stays out (D1 — O6 scope).
- **O2/O3/O5 consumption:** consumes O2 `apply_selection` batch shape (lifts `multi_mutate_deferred_o4` only inside dispatch lane with atomic join), O3 `claim_handles` + `menu.claims` reservation (gen-fenced `claim_task`), O5 `freshness_for_state`/`push_for_state`/`projection_lines` for progress envelopes. Still proposal-only for `proj:/drift:/unscoped:` without bindings (no invented tasks — O3 residual kept).
- Out of scope: agentx adaptive-net bridge + directive→fragment synthesis (O6, needs D1 revisit); slider/join UI beyond text `projection_lines` (O5-follow-up if measured need); distributed/remote/timed/colored nets.

## 3. Resource budget

- Code: new pure helper (e.g. `scripts/omt/net/dispatch_runtime.py`: plan composer + worktree/lease/join orchestrator, stdlib-only, no net I/O) + thin threading in `state.py`/`cli.py` (reuse `fire --expected-revision` / `claim` / `sync net_to_md` / O5 push paths; no new places/transitions/transitions, no new `net_*` kind). `src/agentx/` untouched (D1).
- Tests (major_feature → TDD auto-on at Programming): new goldens `tests/scripts/omt/test_net_dispatch_o4.py` — plan deterministic ×N (empty/enabled, WIP refuse, lane route, stale refuse), worktree isolation (hermetic tmp), 2-worker acquire/release, lane capacities, progress envelope threading, join `work_complete` + re-render, no-new-places — needs tests/ canary approval; e2e receipt per harness-surface round (one edit per file per receipt); targeted + full suite green; `check 265/0` held.
- Runtime: one `probe` (plan at R) + N worktree spawns + progress fires + one join commit + one re-render; token cost bounded by worker cap 2; sidecars/worktrees only until slice approval; `uv` only.

## 4. Wiring table (080–083 + M0 → O4)

| Precedent | Provides | O4 consumption |
|---|---|---|
| 080 `task_claim_generation` | claim handle generation | dispatch plan input (claim → task lease) |
| 081 `worktree_execution_isolation` | per-task worktree isolation | per-claim worktree (hermetic tmp in tests) |
| 082 `two_worker_capacity_scope_arbitration` | 2-worker capacity arbitration | `worker_slots=2` acquire/release + scope guard |
| 083 `verification_integration_lane` | verification/integration lanes | lane routing + capacity 0/1 each |
| O2 `apply_selection` (111) | atomic batch shape, `multi_mutate_deferred_o4` bound | lifted only in dispatch lane with atomic join |
| O3 `claim_handles` (112) | `task_id→holder` map, `menu.claims`, gen-fenced claim | reservation per dispatched claim |
| O5 `freshness/push/projection` (113) | `probe`-time derived views, CLI envelopes | progress fires during execution |

## 5. F7 reversal decision draft (to lock at Design)

- **F7-revoked-lane (2026-09-19, O4 slice):** F7 (`agent_attention=1` serial modeling-only) is reversed for the dispatch lane only: ≤2 concurrent worktrees/sub-agents under `worker_slots=2` + lane leases, with worktree isolation + WIP/capacity/deadlock enforcement + atomic join. `src/` edit serialism (capacity 1, receipt round-robin, two-hats + auto-revert) is unchanged. Reversal is slice-scoped: violation → slice reverts. Requires this Analysis approval + Design approval before Programming fan-out.

## 6. Next (Design → code)

- `omt_phase{major_feature, Design}` → dispatch plan spec + worktree/lease/join shape + lane routing + golden list + F7 decision lock → Programming (TDD `testlist → red → green → refactor → done`, pytest) → `omt_complete{advance_to:Testing}` + test report.
