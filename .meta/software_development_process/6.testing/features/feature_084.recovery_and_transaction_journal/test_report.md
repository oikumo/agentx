# Test report — feature_084.recovery_and_transaction_journal (T5-6 3B)

> Date: 2026-09-13 · Type: minor_feature · Status: PASS

## Scope verified

- `recovery_and_transaction_journal` (mh8 T5-6, strict slice order after
  079/080/081/082/083, NEXT_STEP §14–§15 + Slice 3B): heartbeat liveness
  (evidence, never authority — §14.1), recovery-candidate observation +
  gen-incrementing checkpoint-preserving recovery transfer (§14.2/§14.3),
  and the `_transact` WAL marker (`net_txn.pending.json` — §15.1, recovery
  mechanism not SSOT §15.2) with deterministic startup reconcile.
- Heartbeat: `heartbeat_task` stamps `binding.liveness = {last_seen,
  session, owner}` under the transaction lock; active + matching
  generation required, else `stale_generation` (a superseded worker cannot
  fake freshness). Missed heartbeats never auto-revoke — the coordinator
  still runs `recover_task` explicitly after confirming the old execution
  is stopped or isolated.
- Recovery: `recovery_candidates(stale_after_s)` lists active tasks with
  `no_heartbeat` / `stale_heartbeat` / `unparsable_heartbeat` (read-only);
  `recover_task` preserves checkpoint/results, bumps gen+1, rebuilds the
  per-generation workspace (081), clears liveness, appends a `net_recover`
  audit event linking old → new generations; old-generation publishes
  refuse `stale_generation` (D9).
- Journal: `_transact` writes the pending marker (txid, op, command_id,
  from/to revision, task_id, canonical) inside the held lock after the
  idempotency/revision gates, clears it on clean commit and on clean
  refusal (revision unchanged), LEAVES it when the bundle advanced despite
  the error; `reconcile_transactions` resolves under lock — live == from
  → `recovered_aborted`, live == to → `recovered_committed` (both clear +
  `net_reconcile` audit), else fail-closed `diagnosis` (`txn_diverged`,
  marker kept).

## Goldens (`tests/scripts/omt/test_net_recovery_journal.py`, 9 green)

- Heartbeat stamps liveness (owner/session/last_seen), bumps rev, leaves
  no marker.
- Heartbeat with a superseded generation refuses `stale_generation`.
- Candidates: never-heartbeated → `no_heartbeat`; fresh heartbeat → none;
  aged heartbeat → `stale_heartbeat`.
- Kill-worker handoff: claim → checkpoint → heartbeat → recover preserves
  `checkpoint == step1-done`, gen 1→2, fresh `T1-g2` workspace, liveness
  cleared; old-gen checkpoint refuses `stale_generation`; `net_recover`
  in the ledger.
- Recover on a pending task refuses `task_not_active`.
- Clean commit and clean refusal (`stale_revision`) leave no marker;
  `reconcile` on clean → `clean`.
- Planted markers: from == live → `recovered_aborted`; to == live →
  `recovered_committed`; unrelated revs → `diagnosis`/`txn_diverged`
  with the marker kept.
- CLI round-trip: `claim` → `heartbeat` → `recover` (gen 2) →
  `reconcile` (`clean`), all rc 0.

## Incidental discipline notes

- `skip-latest-wins` (canary, scope: tests): new hermetic goldens only.
- Genuine RED: `AttributeError: module 'net.state' has no attribute
  'heartbeat_task'` before GREEN.
- Round discipline: `lock.py` (journal helpers) + `state.py` (import /
  `liveness` type / `_transact` WAL / heartbeat-recover-reconcile section)
  + `cli.py` (helpers / parsers / dispatch) each patched ONE edit per e2e
  receipt round; `e2e` refreshed between rounds.
- CLI-only in this slice (no `omt_net` plugin exposure — tool budgets ~99%
  full, the T1-6/083 precedent); `command_id` on heartbeat/recover (D14);
  budgets UNCHANGED (tool_args 2454/2464, tool_schemas 1812/1856).
- LSP notes: `cli.py` diagnostics (288/291/450/complexity) and the test
  file's `net` import resolution are pre-existing patterns (083-era
  `_emit(*_error(...))` envelope shape + lazy `sys.path` test import) —
  no newly introduced violations; gates are the green suites.
- Deferred with rationale (strict slice order): evidence digests +
  dependency staleness + objective acceptance → T5-7 3C; generation
  directories + atomic pointer (the §15.3 stronger design) stays a future
  migration — the journal is the incremental step.

## Verification

- New goldens: 9/9 green.
- Neighbors: authority/claim/worktree/capacity/lane/cli — 51/51 green.
- OMT subset (`tests/scripts/omt/`, e2e excluded): 535/535 green.
- Boundary e2e (`test_omt_harness_e2e.py`): 1/1 green.
- `harnessc check`: 0 errors (263 records) · `build`: OK (5 projections).
- Full suite: `tests/` 2139 passed, 0 failed.
