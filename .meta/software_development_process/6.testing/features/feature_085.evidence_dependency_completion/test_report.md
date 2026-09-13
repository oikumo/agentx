# Test report — feature_085.evidence_dependency_completion (T5-7 3C)

> Date: 2026-09-13 · Type: minor_feature · Status: PASS

## Scope verified

- `evidence_dependency_completion` (mh8 T5-7, strict slice order after
  079/080/081/082/083/084, NEXT_STEP §12 + Slice 3C): dependency satisfied
  = an accepted artifact version — the downstream pins
  `{need, task_id, head_commit, evidence_digest}` and the upstream must be
  `work_done` with a matching 083-lane submission; staleness (§12.2):
  upstream re-integrates after downstream verified → the next
  verify/integrate pass refuses `dependency_stale`; upstream not yet done
  (or unknown) → `dependency_unsatisfied`. Fail verdicts bypass both gates
  (failure evidence is always recordable). Objective acceptance is
  observation only (`objective_status` accepted iff every listed task is
  `work_done` with satisfied deps — no worker self-report can mint Done;
  the only Done path stays the dep-gated `integrate_finish` pass, §12.3).
- New `_transact` op `declare_dependencies` stamps `deps` on
  work_active/verifying bindings (gen-fenced `stale_generation` D9,
  malformed → `invalid_deps`, no token moves; deps ride the binding dict
  through the lane so verify + integrate see the same pins).
- `verify_result` + `integrate_finish` verdict=pass both call
  `_check_deps_satisfied` inside the held lock (the §12.2 race is closed:
  verify-time satisfaction is re-checked at integrate time).
- Read paths (no lock, no write): `dependency_status` (per-dep
  satisfied|stale|unsatisfied with pinned vs current head/evidence) +
  `objective_status` (per-task place/evidence_digest/deps_satisfied +
  accepted bool). `integrate_finish` pass also stamps `accepted_deps` +
  `accepted_evidence` for audit.
- CLI-only in this slice (no `omt_net` plugin exposure — tool budgets ~99%
  full, the T1-6/083/084 precedent); `declare-deps --mutation` carries the
  JSON deps list (list or `{deps:[...]}`); `deps --task-id X` or
  `deps --objective T1,T2`; `command_id` on the mutating op (D14);
  budgets UNCHANGED (tool_args 2454/2464, tool_schemas 1812/1856).

## Goldens (`tests/scripts/omt/test_net_evidence_dependency.py`, 14 green)

- Declare stamps pinned versions; wrong generation → `stale_generation`;
  malformed (missing task_id) → `invalid_deps`.
- Verify pass with satisfied deps → integration_ready (happy path).
- Verify pass with upstream pending → `dependency_unsatisfied`, stays verifying.
- Verify pass with head mismatch → `dependency_stale` (names expected vs current).
- Verify pass with digest mismatch (head matches) → `dependency_stale`
  (digest is the fence).
- Verify fail bypasses dep checks → pending (failure evidence always allowed).
- Integrate race (§12.2): T9 verified vs T4 v1, T4 repairs to v2 before T9
  enters the lane, T9 integrate_start succeeds (slot was free), then
  integrate_finish → `dependency_stale`, stays integrating.
- Integrate fail bypasses dep checks → pending.
- `dependency_status`: pending upstream → unsatisfied; re-pinned to current
  versions after T4 integrates → satisfied.
- `objective_status`: T9 not done → accepted False; both done + satisfied →
  accepted True with places work_done.
- Declare after transfer → `stale_generation` (D9 fence preserved).
- CLI round-trip: `declare-deps` → `submit` → `verify` (rc 0) → `deps`
  reports satisfied (rc 0).

## Incidental discipline notes

- `skip-latest-wins` (canary, scope: tests): new hermetic goldens only.
- Genuine RED: 14 failed before GREEN (`declare_dependencies`/`dependency_status`/
  `objective_status` missing + `declare-deps` invalid choice + dep gates absent).
- Test-incidentals: `SpliceError` lives in `net.state` (not `net.lock` —
  fixed 7 imports to the 083 `state.SpliceError` pattern); CLI `_run` needs
  `--reasoning` (required flag, added); race test first drafted T9
  integrate_start before T4 repair → `integration_busy` (slot held) —
  reordered to repair-while-ready then start (slot-free), which is the true
  §12.2 shape.
- Round discipline: `state.py` + `cli.py` patched via a `uv`-run script
  under `harnessc stage --feature feature_085...` (T4-2 staged bypass:
  2 files, single e2e at the boundary); test file fixed in the same batch
  (manual round discipline — check + e2e green before each bash patch).
- LSP notes: test file's `net` lazy-import resolution errors are the
  pre-existing 083-era pattern (runnable RED) — no newly introduced
  violations; gates are the green suites.
- Deferred with rationale (strict slice order): T5-8 fresh-review loop when
  backlog empties; T3-4 benchmark anytime (no policy change); remaining
  T1-1/T2-4..7/T3-3/6/7 backlog audit before any reprioritization.

## Verification

- New goldens: 14/14 green.
- Neighbors: authority/claim-gen/worktree/capacity/lane/recovery/cli — 74/74 green.
- OMT subset (`tests/scripts/omt/`, e2e excluded): 549/549 green.
- Boundary e2e (`test_omt_harness_e2e.py`): 1/1 green.
- `harnessc check`: 0 errors (263 records) · `build`: OK (5 projections).
- Full suite: `tests/` 2153 passed, 0 failed.
