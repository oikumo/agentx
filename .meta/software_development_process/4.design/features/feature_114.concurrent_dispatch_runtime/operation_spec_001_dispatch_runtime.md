# Operation Spec 001 — feature_114.concurrent_dispatch_runtime: public operation contracts

> Phase: Design companion to design_001. Each operation: signature · pre · post/effects · errors. Python engine (`scripts/omt/net/model.py`/`analysis.py`) UNCHANGED — dispatch reuses `probe` snapshot / `_transact` / `fire_marking` / `resource_report` exactly; no new places/transitions; no new `net_*` kind.

## scripts/omt/net/dispatch_runtime.py — pure planner (design §2)

| Op | Pre | Post / returns | Errors |
|---|---|---|---|
| `plan_dispatch(*, claims: list[dict], enabled: list[str], parallel: list[str], worker_slots: dict, verification: dict, integration: dict, work_pending: int, work_active: int, revision: int) -> Plan` | `claims` = O3 resolved claim dicts `{claim, task_id}`; capacities are `probe.resources` shapes; `revision` = live R | Deterministic ordered `Plan {tasks:[{claim, task_id, lane, worktree, lease}], wip:{pending, active, cap:15}, revision:R, batch_id}`. Ordering: verification-lane claims, integration-lane claims, then general by `task_id` code-point. Pure, stdlib-only, no I/O. | `PlanRefused(stale_revision)` when caller passes expected R ≠ live R (checked by caller; planner takes R as given) — planner itself raises `PlanRefused(empty_plan)` if no claims and `enabled==[]`; `PlanRefused(worker_capacity_exhausted)` if `len(claims) > free workers`; `PlanRefused(verification_lane_busy | integration_lane_busy)` if lane-tagged claim exceeds lane free; `PlanRefused(wip_cap_exceeded)` if `pending+active+len(claims) > 15`; `PlanRefused(unknown_claim:{id})` if claim id not in O3 handles |
| `describe_plan(plan: Plan) -> str` | `plan` from `plan_dispatch` | One-line human summary `dispatch {n} tasks rev R batch {id} lanes {v/i/g}` for approval gate + ledger `reasoning`. Pure. | none (total over `Plan`) |

## scripts/omt/net/state.py — dispatch threading (design §3)

| Op | Pre | Post / effects | Errors |
|---|---|---|---|
| `plan_dispatch_view(base, *, expected_revision: int) -> dict` | `base` = loaded `NetState` at live rev R'; `expected_revision` = R from menu | Read-only preview: resolves O3 handles + probe snapshot at R' → `plan_dispatch(...)` pure → returns `plan` dict. No writes, no leases. Fail-open: any helper import failure → `{"plan": [], "reason": "unavailable"}`. | `PlanRefused(stale_revision)` if R ≠ R' (refuse pre-write with fresh-menu hint) |
| `dispatch_claims(base, *, plan: dict, reasoning: str, session: str, expected_revision: int, command_id: str) -> (NetState, report)` | `plan` from preview at R; `session` whitelisted per 046; `command_id` idempotency key | Atomic join under existing `_transact`: acquire `worker_slots` + lane leases → per-claim `net_claim` (gen-fenced, `batch_id`) → per-task progress `net_fire` with O5 `push/freshness/projection` fields → single `fire(work_complete --expected-revision R)` → `sync net_to_md` re-render hint. Returns `(state, report {tasks, batch_id, revision:R→R+1, lanes, wip})`. Any task blocked/stale → release leases + refuse, zero partial marks. | Reuses `_transact` errors verbatim + planner refuse codes (`worker_capacity_exhausted`, lane busy, `wip_cap_exceeded`, `stale_revision`); every refuse prints fresh-menu re-render hint |

## scripts/omt/net/cli.py — dispatch CLI (design §3)

| Op | Contract |
|---|---|
| `dispatch --expected-revision R [--dry-run]` | Session-whitelisted subcommand: dry-run prints plan JSON only; commit path calls `dispatch_claims` and prints join report JSON + re-render hint (`sync net_to_md` next). Errors → `{"ok": false, "error": <code>, "revision": R'}` envelope, exit 2 (CLI convention). |
| `probe` dispatch preview | Additive `plan[]` field in probe JSON (fail-open `[]` when no claims); existing probe fields byte-identical. |

## tests/scripts/omt/test_net_dispatch_o4.py — pytest suite (design §5)

| Op | Contract |
|---|---|
| plan vectors | empty → `empty_plan`; 2-claim hermetic → 2-task ordered; 3rd while 2 held → `worker_capacity_exhausted`; lane busy → lane refuse; stale R → `stale_revision` |
| isolation vectors | hermetic `OMT_NET_DIR`/`OMT_LEDGER_PATH`/`OMT_COORDINATION_ROOT` tmp per task; live rev 60 untouched; place set unchanged (Tier-3) |
| join vectors | single `work_complete` commit (`active:N→0`, `done:+N`, R→R+1); `net_fire` carries `dispatch_plan`/`batch_id`; D19 + rev-stamp in describe |

## Global invariants

- **Net structure untouched** — no `splice` add/remove in dispatch; `place_invariants` hold; overlay derivation unchanged (P10).
- **Ledger kinds reused only** — `net_claim` / `net_fire` / `net_sync`; no new kind (replay-safe).
- **Serial `src/` discipline holds** — `src_edit_capacity=1`, receipt round-robin, two-hats + auto-revert; `src/agentx/` untouched (D1).
- **All sorts code-point**; `uv` only.
