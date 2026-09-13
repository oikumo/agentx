# Test report — feature_083.verification_integration_lane (T5-5 3A)

> Date: 2026-09-13 · Type: minor_feature · Status: PASS

## Scope verified

- `verification_integration_lane` (mh8 T5-5, strict slice order after
  079/080/081/082, NEXT_STEP §13 + Slice 3A + §10.3/§10.5/§17.4/§18/§19.8/§19.9):
  coordinator-owned verification/integration lane — four `_transact` ops in
  `scripts/omt/net/state.py` (`submit_result` worker → `verify_result`
  coordinator → `integrate_start` coordinator → `integrate_finish`
  coordinator) plus `submit|verify|integrate_start|integrate_finish` CLI ops
  and an additive probe `verification`/`integration` occupancy view.
- Lane semantics: `verifying → integration_ready → integrating → done`
  binding lifecycle (fail paths return to pending with `block_reason`
  evidence); code-enforced `test_slots=1` + `integration_slot=1` (lane
  counts are the fence, place tokens honored when present via splice
  migration — the 082 worker_slots pattern); worker slot freed at submit;
  immutable result ref (`head_commit` + `patch_digest` + `evidence_digest`,
  checkpoint fenced out once submitted); coordinator-only verify/integrate
  (`not_coordinator` for workers, §19.8); stale generations refuse every
  publish path (`stale_generation`, §19.5); combined-acceptance failure is
  `integrate_finish verdict=fail` → pending with evidence, `work_done`
  untouched, no automatic Done (§19.9); completed tasks hold no capacity
  (§18 inv 7); integration occupancy never exceeds one (§18 inv 8).

## Goldens (`tests/scripts/omt/test_net_verification_integration_lane.py`, 10 green)

- Submit moves active→verifying with immutable ref (head/patch pinned,
  worker slot freed, test lane occupied).
- Second submit while one verifies refuses `verification_busy` (test_slots=1).
- Submit without head+patch refuses `missing_result`.
- Worker verify refuses `not_coordinator`; coordinator `verify pass` moves
  verifying→integration_ready and frees the test slot.
- Worker `integrate_start` refuses `not_coordinator` even for its own valid
  result (§19.8).
- Second `integrate_start` while one task integrates refuses
  `integration_busy` (serialized lane, inv 8).
- `integrate_finish verdict=fail` returns to pending with combined-failure
  `block_reason` evidence and `work_done == 0` (objective unsatisfied, §19.9).
- Stale generation submit after transfer refuses `stale_generation` (§19.5).
- CLI round-trip: `submit --mutation {head_commit, patch_digest}` envelope
  carries `task.place == work_verifying` (rc 0).

## Incidental discipline notes

- `skip-latest-wins` (canary, scope: tests): new hermetic goldens only.
- Genuine RED: `AttributeError: module 'net.state' has no attribute
  'submit_result'` before GREEN.
- Round discipline: `state.py` + `cli.py` patched once each via a `uv`-run
  script (ONE edit/file/round); `cli.py` probe-menu extension is additive
  keys only (`verification`/`integration` alongside `parallel`/`capacity` —
  the 082 exact-shape precedent).
- Topology choice: no splice migration required — `TASK_BINDING_PLACES`
  gains the 3 lane places, but `validate_task_bindings` treats an absent
  lane place as code-enforced (bindings == tokens, anonymous 0), so legacy
  hermetic pool bundles keep validating while migrated bundles get token
  fidelity; net stays ≤15 places by construction (no places added).
- CLI-only in this slice (no `omt_net` plugin exposure — tool budgets ~99%
  full, the T1-6 precedent: harnessc CLI subcommand over a new tool);
  `mutation` reuses the checkpoint JSON-evidence pattern; `command_id`
  stays on every new op (D14); budgets UNCHANGED (tool_args 2454/2464,
  tool_schemas 1812/1856).
- Deferred with rationale (strict slice order): transaction journal +
  crash recovery → T5-6 3B; evidence digests + dependency staleness +
  objective acceptance → T5-7 3C; plugin exposure of the lane ops (if ever —
  budgets are the constraint).

## Verification

- New goldens: 10/10 green.
- Neighbors: claim/capacity/worktree/plugin-args/cli — 49/49 green.
- Boundary e2e (`test_omt_harness_e2e.py`): 1/1 green.
- `harnessc check`: 0 errors (263 records) · `build`: OK (5 projections).
- Full suite: `tests/` 2130 passed, 0 failed.
