# Analysis 001 — P2 slice A: one-template transition map + conformance harness

> Feature: `feature_103.mh10_p2_global_gate` (`minor_feature`, project `meta_harness_10`) · Phase: Analysis · Date: 2026-09-18.
> Profile: **read-only evidence, no authority change** — earns P2 re-entry row (b) partial; rows (a,c,d,e) parked.

---

## 1. Managed-op inventory (all paths that move global state today)

| # | Managed op | Code path | Net effect today | Transition fired? |
|---|---|---|---|---|
| 1 | `fire(transition)` | `state.py:746-789` via `_transact` | `fire_marking` + `rev+1` + `net_fire` ledger | **yes** |
| 2 | `claim_task` | `state.py:837+` + `_move_pool_token :819-834` | binding `pending→active` + pool token move + `rev+1` inside `_transact` | **no** (direct counter) |
| 3 | `release/complete` (recovery/lane/integration) | `_move_pool_token` callers | pool counter `+=1/-=1` + binding place update | **no** |
| 4 | absent-lane occupancy | `validate_task_bindings :296-300` | `tokens = bindings`, never error | **no** (binding-only) |
| 5 | `project.py sync` (WORK.md/META.md derived rows) | `scripts/omt/project.py` | file mutation, no rev bump, no ledger | **no** |
| 6 | session-start menu render | `AGENTS.md STARTUP` parsing `WORK.md` text | presentation only, reads files | **no** (read path) |
| 7 | crash-window outcome | `_transact :730-742` clear-before-record | marker cleared before `record_command` | **n/a** (C1 residual) |

## 2. One-template map (slice A target)

Each row 1–6 gets a named template transition with enablement = today's guard, effect = today's mutation, ledger = today's record **plus** a `conformance` row (`op, B, M, transition, fired?`):

* `work_start(task_id)` ≡ today's `claim_task` guards (`task_not_pending`, capacity, scope_conflict) + pool move — slice A records the equivalence, slice B rewires the call.
* `work_finish/work_fail/work_cancel` ≡ recovery/lane/integration moves.
* `sync_render` ≡ `project.py sync` + menu render as **derived reads** (`B` recomputed from `M + ledger tail`, never a second source).
* Absent-lane + crash-window stay labeled `OMISSION / carried residual` until slices C/D close them.

Invariant per op: `projection(B) == marking(M)` after the op lands, across pass/fail/cancel/recovery; stale `rev/generation/owner` refuses with `stale_revision/stale_generation/not_owner` (already stable codes from feature_080).

## 3. Conformance harness (what Programming builds)

New read-only module `scripts/omt/net/conformance.py` (no live-surface mutation, net-zero safe):

* `managed_ops()` — the 7-row table above as data (op → file:line + transition name + fired-today bool).
* `check_live(base)` — loads live `NetState`, recomputes `B` (pool counts from bindings + `WORK.md` pool parse) vs `M` (live_marking), returns per-row `agree + fired?` (today: agree with `fired=false` = OMISSION class, matching P1 `divergence.md`).
* `check_fixture(scenario)` — seeded omission fixtures (claim without fire, absent-lane occupancy, sync-without-rev) must be **detected** (reported, never silently passed).

## 4. Exit criteria

* Analysis: this doc + FEATURE.md/PLAN.md filled (this step).
* Programming: `conformance.py` + unit fixtures, no `state.py`/`.opencode/` edits.
* Testing: `test_report.md` — live `B-vs-M` agree + all seeded omissions detected + `check 0 + build OK + suite` green.
* Done: `omt_complete` feature_103 → PROJECT.md slice-A row checked; P2 gate itself stays parked (needs slices B: rewiring, C: crash reorder + injection, D: allow/deny matrix + payback + retirement).
