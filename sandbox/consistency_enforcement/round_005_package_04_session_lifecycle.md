# Round 005 — Package 4: session lifecycle (AXR-04, AXR-08, AXR-09 — one ownership contract, D5)

> Workflow: `.workflows/agentx/loops/consistency_enforcement.md` (override — no OMT gates for this run; `omt_think` + mocked tests + approval gate still apply).
> Project: `agentx_1_0_0` (draft) — repair-only, order 1→6, acceptance = per-finding Regression check.
> Scope source: `round_001_implementation_review.md` §AXR-04, §AXR-08, §AXR-09 + probes `test_axr04_new_session_undefined_helper`, `test_axr04_helper_only_patch_does_not_restore_restart`, `test_axr08_pid_change_loses_snapshot_selection` (×2 modes), `test_axr09_start_session_retains_database_and_goals`.
> Step: strategy 3 (propose) — STOP at step 4 approval gate. No `src/` edits applied in this round.

## 1. Confirmed gaps (summary)

- **AXR-04** `session.py`: `is_created()` uses unqualified `is_directory_exists` → `NameError` kills console `new`. Even with the name bound: `create_new_session` backs up `current` then creates `current_<timestamp>` — a fresh `Session()` opens the empty `current` and sees no history (replacement not at the startup contract's `current`). `NewSessionCommand` also swaps the session manager's session without invalidating `MainController`'s cached agent controllers (old config/persistence retained).
- **AXR-08** `main_controller.py:185,228` + `adapter.py`: agent IDs `agent_<pid>` / `fast_agent_<pid>` change per process → restart looks up snapshots for a new ID, finds none (probe: `agent_102` has zero goals despite saved snapshot).
- **AXR-09** `agent.py:147-161`: `start_session` swaps config + IDs but keeps the old `_db` + repositories + subsystem state → new `persistent_path` never becomes the storage; old goals ride along (probe: db still in A, `old-goal` alive, B has no db).
- Shared (D5): AXR-04/08/09 share **one session-ownership contract** — create/rebind/save/reconstruct/resume agree on storage + stable identity; legacy data recoverable.

## 2. Alternatives (pick one)

- **A* — one ownership contract (recommended, report recipe).**
  - **AXR-04:** import/qualify the helper; coherent transition = back up `current` → stop on backup failure → create replacement **at `current`** (startup contract preserved, no timestamped active dir) → rollback if creation fails. `NewSessionCommand` invalidates `MainController` cached agent controllers after a successful swap so reopened screens rebuild against the new session.
  - **AXR-08:** stable per-session per-mode agent ID (`agent` / `fast_agent` — no PID); PID only execution metadata. `load_latest_snapshot` selection per-mode (never cross-mode); legacy `agent_<pid>` snapshots: select latest per-mode legacy row and **retain its legacy ID as identity** when unambiguous (keeps rows/snapshot/identity association intact — report's own option).
  - **AXR-09:** `start_session` rebuilds persistence (fresh `_db` + repositories) + subsystems (policy/memory/goal/reflection) from the new config via the same construction path as `__init__`; define carry-over = AI service + view wiring only. B-init failure → raise before touching live agent (A stays usable).
- **B — minimal fixes (partial).** Fix `NameError` + keep timestamped replacement + pointer file; fix AXR-08 by DB-wide latest snapshot; AXR-09 by patching `_db` path only. Faster, leaves the three gaps' root causes (ambiguous active dir, cross-mode selection, retained subsystems) partially open — label partial.
- **C — pointer-based active-session indirection.** Persisted active-session pointer + timestamped dirs; every consumer honors it. Bigger surface (startup, session manager, all consumers), report lists it as alternative — heavier than A.

### Cross-cutting (any pick)
- Acceptance: `new` command end-to-end (old history in backup, replacement accepts history, reopen sees it, both agent modes rebuilt on new storage+sandbox); PID-change resume recovers goals/policies/memory/reflection for both modes incl. legacy-ID snapshot case; A→B switch = fresh state, writes to B, A reopenable, B-failure leaves A usable.
- Mocked tests (fake providers, temp dirs, real SQLite); no live terminal input.
- Probes retired, not gated (D4).

## 3. Approval gate (step 4 — awaiting user)

Reply with a single letter (A/B/C). No `src/` edits until go-ahead (step 5). Results go to `# Result` below after execution (step 6).

## 4. Execution notes (for step 5, after approval)

- Mocked unit tests first (rule 3); `omt_think` in touched source (rule 2); sub-agents for parallel analysis where useful (rule 4).
- Record: repaired revision, test nodes/commands, coverage, residuals (automatic-exit snapshot timing stays out of scope).

# Result (executed 2026-09-20 — user picked A)

- **Chosen:** A (one ownership contract). `session.py`: helper imported; `create_new_session` = backup → **replacement at `current`** (startup contract), raises on backup failure of a live session, rolls back backup if replacement creation fails. `commands.py` `NewSessionCommand.run` → `MainController.invalidate_session_scoped_controllers()` (drops cached Advanced/Fast Agent controllers; next open rebuilds on replacement storage+sandbox). `main_controller.py`: stable per-session per-mode ids `agent` / `fast_agent` (no PID). `agent.py`: `load_latest_snapshot` adopts the latest per-mode legacy `agent_<pid>` id as stable identity before resume (`_adopt_identity` propagates to config + subsystems); `agent_db.py`/`schema_db.py`: `SELECT_LATEST_AGENT_ID_BY_PREFIX` (ESCAPE'd `agent\_%` — mode families never overlap). `agent.py` `start_session`: builds fresh db/repositories/subsystems/tools from the new config and swaps atomically — construction failure raises pre-swap (old session fully usable); carry-over = AI service only. TA thoughts added in agent.py, session.py, main_controller.py.
- **Observation probes (must stop passing):** all 5 **fail as desired** — axr04-1 (no NameError), axr04-2 (replacement is `current`, not `current_<ts>`), axr08 ×2 (id stable + goals recovered), axr09 (db now in B, fresh goals, B db exists).
- **Regression proof (9 scenarios):** legacy adoption + goal resume PASS; unrelated-candidates deterministic (latest `agent_202` wins) PASS; per-mode isolation (`fast_agent` never adopts `agent_*`) PASS; restart recovers goals both modes PASS; A→B fresh switch + A reopenable PASS; failed-switch leaves agent intact PASS; `new` end-to-end (backup keeps old-history, replacement at `current` accepts+reopens history, cached controllers invalidated, rebuilt agent on replacement storage+sandbox) PASS; backup-failure refuses transition, old session usable PASS.
- **Existing suites:** `session|agent|goal|main_controller|commands|snapshot` → **473 passed, 0 failed**.
- **Probe census after pkg 1–4:** 13 failed (fixed findings) / 7 passing = axr05 ×5 (Package 5, next) + axr10 + axr11 (Package 6).
- **Residuals:** automatic snapshot-on-exit timing out of scope (report limitation); adoption picks latest legacy id per mode — multiple same-mode legacy ids resolve by newest snapshot (deterministic, recorded); `GoalTree.nodes` is a dict keyed by id (tests must iterate `.values()`).
- **Next:** Package 5 RAG file handoff (AXR-05). Do not close Package 4 until durable `tests/` regressions land (canary approval needed). CLOSED 2026-09-20: 9 durable tests landed in `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_axr04_axr08_axr09_session_lifecycle.py` (canary).
