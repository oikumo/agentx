# Test report — feature_082.two_worker_capacity_scope_arbitration (T5-4 2D)

> Date: 2026-09-13 · Type: minor_feature · Status: PASS

## Scope verified

- `two_worker_capacity_scope_arbitration` (mh8 T5-4, strict slice order after
  079/080/081, NEXT_STEP §10–§11 + Slice 2D, D8/D13 one-machine `worker_slots=2`):
  the first real two-worker execution demo — code-enforced capacity (active
  bindings < 2, `worker_slots` place tokens honored when present via splice
  migration) + component-aware scope arbitration (ancestor/descendant, not
  string prefix) inside the T5-1 `_transact` authority, plus a capacity-aware
  probe parallel menu (`parallel` + `capacity`, additive keys only).

## Goldens (`tests/scripts/omt/test_net_two_worker_capacity_scope.py`, 7 green)

- Two disjoint claims run concurrent (A+T1, B+T2; `work_active` 1→2).
- Third claim refused `worker_capacity_exhausted` (worker_slots=2 full).
- Release frees a slot (T3 claims after T1 releases, owner/carrier updated).
- Overlapping scope refused `scope_conflict` with the blocking task in the message
  (`src/agentx/agent/model` vs `src/agentx/agent/model/policy`).
- Component-aware: `src/foo` vs `src/foobar` is NOT a conflict (string prefix
  only) and both claim; `src/foo` vs `src/foo/bar` IS (pinned at the helper
  level too).
- Unscoped tasks never conflict (empty scope = no constraint).
- Probe menu: capacity `{used:0, total:2, free:2}` + `parallel:[T1,T2]` at rest;
  after one claim `used:1` and `T2` still offered; full → `parallel:[]`
  (capacity-aware fix caught by the boundary e2e, round-2 patch).

## Incidental discipline notes

- `skip-latest-wins` (canary, scope: tests): new hermetic goldens only.
- Genuine RED: third-claim capacity test DID NOT RAISE before GREEN.
- Round discipline: state.py + cli.py patched once each via `uv`-run scripts
  (ONE edit/file/round); round-2 state.py touch-up (parallel offer
  capacity-aware) after the boundary e2e caught `parallel:[T3]` at full
  capacity — re-verified goldens + e2e R2.
- Topology choice: no splice migration required — `worker_slots` tokens are
  consumed/restored when the place exists, the active-binding count is the
  fence otherwise; net stays ≤15 places by construction (no places added).
- `harnessc check` 0 errors; the `meta_harness_development_self_evaluation.md`
  drift warning is pre-existing (open repair flag, untouched).

## Verification

- New goldens: 7/7 green.
- Neighbors: claim/authority/worktree/cli/menu/pool/resources — 68/68 green.
- Boundary e2e: CLI T1+T2 concurrent, T3 refused `worker_capacity_exhausted`,
  probe ok — green (R2: parallel offer capacity-aware — green).
- `harnessc check`: 0 errors (263 records) · `build`: OK (5 projections).
- Full suite: `tests/` 2120 passed, 0 failed.
