# Test report — feature_079.net_transaction_authority (T5-1 2A)

> Date: 2026-09-13 · Type: minor_feature · Status: PASS

## Scope verified

- `net_transaction_authority` (mh8 T5-1, strict slice order, D10 lock-first):
  every authoritative net/binding mutation path runs inside one shared local
  transaction authority — revision check moved INSIDE the critical section +
  `command_id` idempotency + stable refusal codes. Solo behavior frozen (no
  `expected_revision`/`command_id` → today's commit path, D8).

## Short design note (lock primitive — PROJECT.md §Scope requirement)

- New `scripts/omt/net/lock.py` (imports `.errors` only — no `state` cycle):
  `CoordinationLock(root).exclusive()` = `fcntl.flock(LOCK_EX)` on
  `<coordination-root>/net.lock` (NB+retry, 30 s deadline → `lock_unavailable`
  fail-closed); `OMT_COORDINATION_ROOT` overrides the root (forward-compat
  for 2C shared root, default = bundle dir). Non-Unix / unreadable index /
  contested-hold all fail CLOSED, never silently unprotected.
- `command_id` index (`net_commands.json`, 500-entry prune, tmp+replace under
  the held lock): same ID + same canonical payload → replay original result
  (no bump, no double-fire); same ID + different payload → `SpliceError`
  `command_id_conflict`. Ledger shapes untouched (no pin churn); the index is
  a bounded lookup cache, the ledger stays the audit trail.
- `state._transact(op, payload, expected_revision, command_id, apply)`: lock →
  idempotency → authoritative `_require_revision(load)` → apply → record.
  Routed: `fire`, `splice` (all modes incl. non-bumping `repair`), `sync`
  bootstrap (double-checked creation), `init_empty`. `synthesize`/`mine`
  need no lock (ledger-audit writes only, no bundle mutation). No binding-edit
  or migration function exists yet — any future one must use `_transact`
  (rule documented, not code). CLI `main`'s pre-lock rev check stays a fast
  rejection only. CLI gains `--command-id` on fire/splice (threaded to
  state); `LockError` maps to a stable envelope code.
- Deferred (documented, not dropped): opencode-plugin `command_id`
  pass-through (whitelist subset test stays green without it; rides with 2B
  claim txn which needs session binding anyway); crash-between-save-and-ledger
  journaling (3B slice); worktree/claim/generation layers (2B–3C build on this).

## Tests

- New `tests/scripts/omt/test_net_transaction_authority.py` — 8 goldens:
  1. `test_plain_fire_commits_without_index` — solo path frozen (rev bump, no index file).
  2. `test_stale_revision_still_refuses` — D19 message/code preserved.
  3. `test_two_procs_from_rev0_exactly_one_commits` — **the T5-1 golden**:
     2 forked procs behind a barrier, both `fire(expected_revision=0)` on a
     still-enabled-twice transition → exactly 1 commit (rev 1) + 1
     `stale_revision`; final marking `{p:1,q:1}`. Deterministic by construction
     (loser's in-lock load postdates the winner's save).
  4. `test_retry_same_command_replays_without_bump` — retry with the ORIGINAL
     expected rev replays (idempotency precedes the rev check), rev stays 1.
  5. `test_same_id_different_command_conflicts` — `command_id_conflict`, rev held.
  6. `test_splice_replay_and_conflict` — splice replay carries `replayed:True`
     (additive key, normal path shape unchanged); conflict + stale cases.
  7. `test_splice_stale_revision_refuses_inside_lock` — splice rev gate now real.
  8. `test_fire_command_id_round_trip` — CLI `--command-id` end to end.
- Regression: net suite (`test_net_state/splice/cli/sync/engine` + plugin-args
  whitelist) green; boundary e2e `test_omt_harness_e2e` 1/1 (covers the staged
  3-file batch: lock.py + state.py + cli.py, single e2e per T4-2 stage).
- `harnessc check` → 0 errors; `harnessc build` → OK (all budgets green, no
  ceiling moves — no tool-description growth this slice).

## Full suite

- `uv run pytest -q`: **2096 passed, 0 failed** (2088 baseline + 8 new).

## Notes

- `DeprecationWarning: multi-threaded fork()` from the race test under pytest
  (workers only do file I/O + flock; harmless here — `spawn` would need a
  picklable barrier rig for no gain; revisit if the suite ever goes green-threads).
- Discipline: `harnessc stage --feature feature_079…` batch (lock/state/cli)
  + one boundary e2e (D-bar working as designed); tests/ edit under canary
  `omt_skip{scope:tests}` (hermetic tmp dirs); `.meta/META_HARNESS.omt`
  untouched (no budget impact).
- LSP noise (pre-existing, runtime-fine): `cli.py:224/227` probe-typing +
  lazy `net` imports in the new test file (same shape as existing net tests).
