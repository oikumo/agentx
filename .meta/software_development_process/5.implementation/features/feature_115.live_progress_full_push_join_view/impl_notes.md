# Implementation notes — feature_115.live_progress_full_push_join_view

> Date: 2026-09-20 · minor_feature (no TDD) · project `meta_harness_11`.

## What changed

- `scripts/omt/net/freshness.py` (+~85): new pure `batch_projection_lines(plan, lanes?, conflicts?)` (stdlib-only, no I/O) over the `plan_to_dict` shape — `batch {id} rev {R} lanes {v/i/g} wip {p/a/cap}` + per-task lines in planner order + `deadlocks_complete/blocked:*` tail; malformed → `[]`. `projection_lines` untouched (backward compat).
- `scripts/omt/net/state.py` (+~110): `_render_push_text(st)` (dry-run `sync_md.render_tasks_block` compose with O1 menu inputs, never writes/applies — D4; fail-open `""`; pool nets match `sync` exactly, non-pool rows fall back to `feature_N` slugs) + `join_projection_for_state(st, plan?)` (fail-open `[]`); dispatch-join block now threads full-text push (`{"claims": N}` counts) and appends batch lines to `projection`.
- `scripts/omt/net/cli.py` (+~30, one bash-transform round): `_probe` captures the full plan view, fills `push.tasks_block`, appends join lines after the existing projection lines; `_fire` / `_apply_selection` / `_task_envelope` fill `push.tasks_block`. All additive, fail-open, no format break.
- `tests/scripts/omt/test_net_followup_o5.py` (new, 8 goldens, canary-approved): batch order/fail-open/tail + push round-trip/stale/probe-compat/join-empty vectors; hermetic via `OMT_NET_DIR`/`OMT_LEDGER_PATH`/`OMT_COORDINATION_ROOT` tmp.

## Discipline notes

- Receipt round-robin respected (ONE edit per file per e2e receipt; gate-blocked second edits cleared with `test_omt_harness_e2e.py` receipts; cli.py 4-site change as ONE bash-transform round).
- Think-gate consulted (`state.py`, `cli.py`, `sync_md.py`, `dispatch_runtime.py`, `freshness.py`); KB consults recorded (no hits); `omt_skip{scope:tests, purpose:canary}` logged for the new goldens file.
- Live net untouched (rev 60; only read-only `probe` evidence); `src/agentx/` untouched (D1); `uv` only.
- Residual LSP: 3 pre-existing downstream notes in `state.py` (`_dep_status` area, untouched) + repo-pattern lazy-import noise in the new test file (same as `test_net_fresh_o5.py`).
