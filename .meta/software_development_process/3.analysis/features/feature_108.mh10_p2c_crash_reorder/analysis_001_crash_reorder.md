# Analysis 001 — Slice C: crash reorder (record-before-clear + reconcile backfill)

> Feature: `feature_108.mh10_p2c_crash_reorder` (`minor_feature`, project `meta_harness_10`) · Phase: Analysis · Date: 2026-09-18.
> Resumes: PROJECT.md D3/C1-residual + CURRENT_STATE iter14 Next (Slice C) + feature_079/084 locks.

---

## 1. Crash window (head-verified 2026-09-18)

`scripts/omt/net/state.py::_transact` success path (lines 746-758):

1. `write_pending_txn` (729) — marker `{txid, op, command_id, from_revision, to_revision, canonical}`.
2. `apply()` (731) — `save` bumps rev `from→to`, then `append_ledger`.
3. `clear_pending_txn` (746-750) — marker removed.
4. `record_command` (751-758) — idempotency index `{canonical, revision, result}`.

Windows:

- **W1 (save landed, crash before clear):** marker present, `live==to`, index missing. `reconcile_transactions` (3532-3615) reports `recovered_committed`, clears marker, appends `net_reconcile` — but does NOT backfill the index. Retry with the same `command_id` finds no prior → re-applies → **double-fire** (new rev, new generation).
- **W2 (crash between clear and record):** marker gone, index missing. Looks `clean`. Retry → **double-fire** silently.
- Exception path (732-745): `apply` raised after `save` landed (e.g. `append_ledger` failed) → marker left (`live==to`), no `info` result to record. Same duplicate risk on retry; reconcile reports committed but index stays missing.

`command_id=None` callers (solo behavior frozen, D8) skip the index — unaffected; the fix must keep their path byte-identical.

## 2. Design (record-before-clear + backfill, adopted)

- **Reorder:** `record_command` BEFORE `clear_pending_txn` in the success path. W2 disappears by construction (crash between record and clear leaves marker + index → reconcile sees committed + index present → retry replays).
- **Carry result in the marker:** after `apply()` returns `(st, info)`, overwrite the pending marker with the same `txid` + `result=info` (still under the held lock, before `record_command`). Cost: one extra `write_pending_txn` (tmp+fsync+replace, same durability as the first). This gives reconcile everything needed to backfill exactly.
- **Reconcile backfill (`live==to` leg):** when `pending.command_id` is present and `lookup_command` misses, `record_command(pending.command_id, pending.canonical, live_revision, pending.result or {})` before clearing + auditing. New audit outcome `recovered_committed_backfilled` (keeps `recovered_committed` for the already-indexed case — existing tests stay green). When `pending` has no `command_id` (solo path) → current behavior unchanged. When `pending` has `command_id` but no `result` (crash between save and marker-result-write, in-memory-only window, no I/O) → fail-closed `diagnosis` (leave marker, do NOT synthesize a result — generation/task_id must never be invented). That window is a single Python-statement span; the suite plants it explicitly and asserts diagnosis.
- **Exception-after-save leg:** unchanged semantics (leave marker) + same backfill rule applied at reconcile time: with `result` absent there is nothing to backfill → diagnosis (honest, instead of today's silent duplicate on next retry). No new auto-retry inside `_transact` (recovery stays explicit via `reconcile_transactions`, §15.2).

Refused: auto-retry inside `_transact` on marker-present (would mistake a live holder for a crash — the feature_084 lock reasoning, `state.py:688-691`); synthesizing `result` from live state (generation ownership must come from the commit, never re-derived).

## 3. Blast radius (explicit)

- `state.py` ONE round: `_transact` (pending-result write + record-before-clear) + `reconcile_transactions` (`live==to` backfill leg + new outcome). Docstring updates ride in the same round.
- `lock.py`: no format break — `pending.result` is an additive optional key; old markers without it take the diagnosis leg. Readers (`read_pending_txn`) unchanged.
- Fixtures asserting exact `_transact` source lines / marker keys update: `test_net_transaction_authority` (solo-path + replay untouched), `test_net_recovery_journal` (planted-marker reconcile: `recovered_committed` stays for indexed markers; new backfill/diagnosis cases are new tests, not edits to old asserts).
- Parked: matrix/payback (D), attention-vs-workers reconciliation, cap-raise amendment.

## 4. Exit

- Programming: ONE `state.py` round (reorder + marker-result + reconcile backfill) under the e2e receipt discipline (one edit per file per receipt).
- Testing: new `test_c_crash_reorder` goldens — (a) happy path records + clears (marker absent, index present, replay no-bump); (b) W1 injection (save landed, kill before record with result-carrying marker → reconcile backfills → retry replays, exactly 1 rev bump); (c) W2 injection (record landed, kill before clear → reconcile committed → retry replays); (d) result-less marker → diagnosis, marker left, retry refuses/duplicates never; (e) solo-path (`command_id=None`) unchanged (no index, marker absent); (f) exception-after-save → marker left for reconcile. Full receipt + `check` 265/0 + `build` OK + suite green + `test_report.md` → `omt_complete`.
