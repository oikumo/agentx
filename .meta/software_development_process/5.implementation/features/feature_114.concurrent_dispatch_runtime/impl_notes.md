# Implementation notes — feature_114.concurrent_dispatch_runtime

> Date: 2026-09-19 · Scaffolded by `new_feature.py implementation` (feature_090).

## What changed

- `scripts/omt/net/dispatch_runtime.py` (new, 226 lines, stdlib-only): pure `plan_dispatch` (verification→integration→general ordering, `unknown/dup/empty/worker/lane/wip` stable refuses, sha1 batch_id, worktree/lease derivation) + `describe_plan` + `plan_to_dict`; no net/ledger I/O.
- `scripts/omt/net/state.py` (+367): `plan_dispatch_view` (read-only preview, fail-open, stale-refuse with O5 fresh hint) + `dispatch_claims` (ONE `_transact` atomic join: validate-all → per-claim `net_claim` gen-fenced with worktree stamp → single `fire(work_complete)` with O5 `progress[]` → R→R+1; accepts `tasks`/`plan` preview shapes).
- `scripts/omt/net/cli.py` (+6): probe additive `plan[]` preview (fail-open `[]`); full `dispatch --expected-revision` commit subcommand deferred to O5-follow-up.
- `tests/scripts/omt/test_net_dispatch_o4.py` (new, 23 goldens, canary-approved): planner/preview/join vectors per Design §5; hermetic via `OMT_NET_DIR`/`OMT_LEDGER_PATH`/`OMT_COORDINATION_ROOT` tmp.
- `tests/features/feature_109.../test_d_matrix.py` + `tests/scripts/omt/test_task_prep_slice.py` (tests-only hermetic `OMT_LEDGER_PATH` seeding; no golden behavior change — isolates prior live `scope=all` skip).

## Discipline notes

- Receipt round-robin respected for harness-surface files (ONE edit per file
  per e2e receipt; `uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q`).
- `uv` only (no bare python/pip/pytest).
