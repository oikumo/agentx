# Impl notes - feature_118.mh11_worktree_lifecycle (B worktree lifecycle)

## New module: scripts/omt/net/worktree_lifecycle.py (new file, 6.6KB)
Pure composer plus one subprocess boundary, stdlib-only, no state import:
- resolve_lane(task_id, generation, lane): general lane gives root
  .sandbox/bench plus branch feat/T-gN (session plane, improvement003 vars);
  managed lane gives .worktrees plus omt/T/gN (081 preserved).
  Refusals: unknown_task, bad_generation.
- status_checks(path, branch, base_commit): closed git reading
  (status --porcelain, rev-parse --verify, rev-list base..HEAD --count);
  every failure reads clean False. No side effects.
- compose_join(tasks, base main): grouped order - all merges --no-ff
  ordered by task_id, then worktree remove --force plus branch -D.
  Refusals: empty_join, unknown_workspace.
- gate_complete(status, verify_ok, expected_revision, live_revision):
  unknown_workspace / unclean_sidecar / no_commit_since_claim /
  verify_red / stale_revision (returns None on pass).

## Threading: scripts/omt/net/state.py (4 regions, additive only)
- plan_dispatch_view preview: tasks gain sidecar via pure derive
  (predicted generation = binding gen + 1), fail-open, no FS writes.
- dispatch_claims per-task claim: workspace gains nested sidecar
  dict (root/branch/path/lane); 081 id/path/branch/base_commit/worktree
  keys byte-identical.
- claimed_info report tasks gain sidecar; ledger net_claim gains
  sidecar branch/path. No new ledger kind, no new places/transitions.
- CLI join --dry-run deferred (O4 precedent: probe plan preview only);
  join executes through dispatch_claims + compose_join by the caller.

## Receipt discipline
Round 1: worktree_lifecycle.py create + B goldens create (parallel OK),
e2e refresh, grouped-order fix. Round 2: state.py single-write threading,
e2e refresh. TDD two cycles (composer 9 goldens, threading 2 goldens),
same-node red/green, sync clean, done with 2 pre-existing baseline
failures only (improvement003 budget pins, unrelated to 118).
