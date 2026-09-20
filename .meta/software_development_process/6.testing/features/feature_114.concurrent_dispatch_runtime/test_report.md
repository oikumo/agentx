# Test report — feature_114.concurrent_dispatch_runtime (O4, Programming → Testing)

> Date: 2026-09-20 · Phase: Programming → Testing (`major_feature`, TDD GREEN) · Live net untouched (rev 60 `drained_complete`; all dispatch/state tests hermetic via `OMT_NET_DIR`/`OMT_LEDGER_PATH`/`OMT_COORDINATION_ROOT` tmp).

## Scope under test

O4 concurrent dispatch runtime per Analysis 001 + Design 001 + Operation Spec 001: pure deterministic planner (`scripts/omt/net/dispatch_runtime.py::plan_dispatch`) over O3 resolved claims + probe-time capacities (worker_slots=2, verification/integration 0/1, WIP pool cap 15), read-only preview (`state.plan_dispatch_view`, fail-open), atomic join (`state.dispatch_claims`: validate-all → per-claim `net_claim` gen-fenced → single `fire(work_complete)` join + O5 progress envelopes → ONE revision bump R→R+1), probe `plan[]` preview threading (`cli._probe`). F7 lane-only reversal locked at Design §1 (fan-out ≤2 under worker_slots + lane leases; `src/` edit serialism unchanged; `src/agentx/` untouched per D1).

## Results

- **New goldens `tests/scripts/omt/test_net_dispatch_o4.py`: 23/23 green** (tests/ canary `omt_skip{scope:tests}`; hermetic, live ledger never read):
  - PlanEmpty ×1 (empty claims + empty enabled → `empty_plan`, D19 no invented work).
  - PlanCompose ×3 (verification→integration→general ordering; general by task_id code-point; unknown lane falls back general).
  - PlanRefusals ×6 (`unknown_claim`, `dup_claim`, `worker_capacity_exhausted` 3-claims/2-free, `verification_lane_busy`, `integration_lane_busy`, `wip_cap_exceeded` 14+0+2>15).
  - PlanDeterminism ×2 (batch_id sha1(rev|sorted task_ids)[:12] stable per rev, distinct across rev; worktree `wt-{batch6}-{task}` + lease `lease-{batch}-{nn}` derivation; `describe_plan` + `plan_to_dict` shape).
  - PreviewView ×4 (pending bindings resolve; caller claims lane plan; over-capacity stays fail-open `plan:[] + refused`; stale expected_revision raises `stale_revision` with re-render hint).
  - DispatchJoin ×7 (one-revision commit active:N→0 done:+N R→R+1 + workspace worktree stamp + slots restored; ledger `net_claim`/`net_fire` carry `batch_id`, join `dispatch_plan` + `progress[]` with O5 `push/freshness/projection`; stale/unknown/not-pending/scope-conflict/slots-token refuses all atomic with zero partial marks).
- **Targeted: 56/56 green** — dispatch_o4 (23) + menu_o1 (14) + claim_o3 (12) + fresh_o5 (7).
- **§12 pointer `tests/features/feature_114.concurrent_dispatch_runtime/test_dispatch_o4.py`: 2/2 green** (canary-approved smoke: empty-refuses + single-claim composes; canonical 23 remain at `tests/scripts/omt/`; combined 25/25 with canonical).
- **Full suite: 1872 passed, 2 deselected, 0 failed** (72s) — prior 1847 + 23 canonical + 2 pointer; no regressions.
- **`harnessc check`: 265 records, 0 errors** — all budgets OK (work_md 9664/9728).
- **E2E receipt `test_omt_harness_e2e`: 1/1 green** per harness-surface round.
- **TDD: `omt_tdd sync` clean** (no stranded REDs); cycle 1 `TestPlanEmpty::test_empty_refuses` closed RED→GREEN (implementation predated tests per prior-session user-directed override skip; remaining goldens pin implementation directly per directed scope).
- **Contract fix (src, code-hat):** `dispatch_claims` accepts preview shape (`plan.get("tasks") or plan.get("plan")`) per operation_spec_001 §dispatch_claims ("plan from preview"); probe `plan[]` contract untouched.
- **Hermetic hardening (tests-only, no golden behavior change):** 6 pre-existing failures (5× feature_109 P2D deny-matrix i1–i5 + 1× feature_073 task_prep blocker) shared one root cause — prior session's live `scope=all` override skip made the gate allow/break_glass on the live ledger path (test-isolation violation); fixed with `OMT_LEDGER_PATH` seeding (d_matrix autouse fixture + task_prep subprocess env). Live `scope=all` skip expired by design; ledger untouched.

## Receipt discipline (harness-surface rounds)

1. `dispatch_runtime.py` (new pure module, stdlib-only, no net/ledger I/O) → hermetic smoke + goldens.
2. `state.py` `plan_dispatch_view` + `dispatch_claims` threading (lazy import, fail-open preview; single `_transact` join; O4 preview-compat + progress-envelope collapse documented inline) → e2e refresh per round; contract fix ×1 single edit.
3. `cli.py` probe `plan[]` preview only (additive, fail-open `[]`) → e2e refresh.
4. Goldens after tests/ canary in 3 rounds with e2e refresh per round; `uv` only throughout.
- Pre-existing only: lazy-import LSP noise in test files (repo-wide pattern).

## Design adherence (P10-clean, Tier-3)

Planner is pure (no I/O; capacities passed as `{used,cap,free}` views, malformed fail-closed to 0); no places/transitions added (structure untouched — dispatch is runtime wiring over existing pool + resources + lanes); ledger reuses `net_claim`/`net_fire` only (no new `net_*` kind, replay-safe; N progress envelopes collapse into the single join `net_fire.progress[]` — N fire records would misrepresent one marking commit); overlay derivation unchanged; SpliceError carrier (not PlanRefused) keeps CLI envelope uniform — stable CODE is the contract; all sorts code-point; `src/agentx/` untouched (D1); `uv` only.

## Residual

- O4 in Programming pending `omt_complete{advance_to:Testing}` + user close/ship call.
- CLI `dispatch --expected-revision` commit subcommand deferred (design §3.2): probe carries additive `plan[]` preview; dispatch commits via `state.dispatch_claims` API. Full CLI dispatch + slider/join live view are O5-follow-up if measured need appears.
- Real `git worktree` fan-out only in dispatch lane with explicit approval; tests use hermetic tmp per task (no live net touch).
- O2 `multi_mutate_deferred_o4` lifted only inside dispatch lane with atomic join; outside the lane the O2 bound stands.
