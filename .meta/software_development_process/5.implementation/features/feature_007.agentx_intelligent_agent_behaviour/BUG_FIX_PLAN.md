# Bug Fix Plan — feature_007.agentx_intelligent_agent_behaviour

**Created:** 2026-07-04
**Last reviewed:** 2026-07-04 (full independent source review)
**Source:** Comprehensive bug review of `src/agentx/agent/` (39 files) + UI integration (`src/agentx/ui/screens/main/`)
**Test Baseline:** 137 feature_007 tests pass; MVC++ 0 errors / 0 warnings on `src/agentx/agent/`

> **Review methodology.** Every file under `src/agentx/agent/` was read in full,
> plus `main_controller.py` (the UI entry point). Each bug in the previous
> version of this plan was re-verified against the current source (line numbers
> updated). New bugs discovered during the review are prefixed `N`. The
> "Verification" column records whether each original bug still reproduces.

---

## Priority Matrix (updated)

| Priority | Count | Description |
|----------|-------|-------------|
| **P0 — Blocker** | 8 | Core lifecycle broken (session resume, volatile memory loss, reflection, goal completion, traceability) |
| **P1 — High** | 9 | Silent failures, safety gaps, self-improvement loop inert, tool-disable no-op, MVC++ leaks |
| **P2 — Medium** | 9 | Dead code, config loss on resume, goal-root drift, log pollution, RAG read-only |
| **P3 — Low** | 10 | Code quality, performance, encapsulation |

---

## Verification of Existing Plan Bugs

| ID | Original claim | Status | Evidence (current source) |
|----|----------------|--------|---------------------------|
| C1 | `resume_session()` doesn't re-register built-in tools | ✅ CONFIRMED | `model/agent.py:131-145` — no `_register_builtin_tools` call |
| C2 | `reflect()` returns engine instead of result | ✅ CONFIRMED | `model/agent.py:274-276` — `return self.reflection_engine` |
| C3 | `resume_session()` doesn't restore `_ai_service` | ✅ CONFIRMED | `model/agent.py:131-145` — no `set_ai_service` on resume |
| C4 | Controller accesses private `_db` | ✅ CONFIRMED | `controller/session_controller.py:24` — `self._agent._db.load_snapshot(...)` |
| C5 | `show_agent()` creates new agent every time | ✅ CONFIRMED | `ui/screens/main/main_controller.py:90-120` — no reuse, no snapshot load |
| C6 | Goal completion over-eager in `act()` | ✅ CONFIRMED | `model/agent.py:268-271` — any successful tool completes `tool_success` goal |
| C7 | DB path fragile — no default in model | ⚠️ PARTIALLY INVALID | `types.py:175` **does** default `persistent_path=".agentx/memory"`; dir creation already in `agent_db.py:39`. Real residual: `Agent.__init__` uses `f"{persistent_path}/agent_session.db"` but never validates/canonicalises the path. Downgraded to P3 |
| M1 | `perceive()` swallows sensor exceptions silently | ✅ CONFIRMED | `model/agent.py:235-236` — only logs, no failed reading |
| M3 | Reflection proposals dropped silently | ✅ CONFIRMED | `reflection/engine.py:143-144` — bare `return` when safety/router None |
| M7 | Safety evaluator deny-list incomplete | ✅ CONFIRMED | `reflection/safety_evaluator.py:25-28` — only 2 entries; `op` rarely set |
| M8 | `SessionTool.act()` calls non-existent `resume()` | ✅ CONFIRMED | `tools/session_tool.py:99-100` — `hasattr(self._agent, "resume")` is **False** → restore always fails |
| I1 | No session resume in TUI | ✅ CONFIRMED | `main_controller.py:90-120` — no `agent_id` param, no `load_latest_snapshot` |
| I4 | AI Service coupling — adapter created in controller | ✅ CONFIRMED | `main_controller.py:118` — `AIServiceAdapter()` in controller |
| M2 | `reflection_log_position` stored but never read | ✅ CONFIRMED | `model/agent.py:209` writes it; `resume_session` never reads it back |
| M4 | `duration_ms` clobbers tool's own timing | ❌ INVALID (already fixed) | `tools/registry.py:143` — guarded by `if result.duration_ms == 0`. Remove from plan |
| M5 | Policy condition type errors silent `False` | ✅ CONFIRMED | `policy/rule.py:353` — `except TypeError: return False` |
| M6 | Proposal router accesses private `_specs` | ✅ CONFIRMED | `reflection/proposal_router.py:117,129` — `self._tools._specs.get(...)` |
| m3 | `MemoryManager.retrieve()` O(N) scan | ✅ CONFIRMED | `memory/manager.py:53-78` — loads all rows then filters in Python |
| m1–m10 | Low-priority items | ✅ mostly confirmed | See P3 table |

**Net:** 17 of 18 original bugs confirmed; **M4 is a false positive** (already
guarded); **C7 downgraded**. **9 new bugs** (N-series) found below.

---

## NEW Bugs Found in This Review

These were not in the previous plan. They were found by reading every source
file end-to-end.

### N1 — Volatile memory is LOST on resume (P0, data loss)
**File:** `model/agent.py:199-215` (`persist`) + `model/agent.py:143` (`resume_session`) + `memory/manager.py:44-49`
**Root cause:** `persist()` stores `volatility_data={"state": self.state.value}` — it serialises only
the state string, **not** the volatile memory entries. `resume_session()` then tries to reload volatile
memory via `self._mem_repo.load_by_agent(self.id, MemoryTier.VOLATILE)` — but `MemoryManager.store()`
only writes the **PERSISTENT** tier to the repository; volatile entries live solely in the in-process
`OrderedDict`. So `load_by_agent(..., VOLATILE)` always returns `[]`.
**Impact:** Every perception and action result stored in volatile memory is discarded when the agent
is resumed. The `volatility_data` snapshot field (clearly intended to hold volatile data) is misused.
**Fix:** Serialise `self.memory._volatile` into `volatility_data` in `persist()`; in `resume_session()`,
rehydrate `self.memory._volatile` from `volatility_data` (remove the dead repo load).
**Test:** `test_resume_restores_volatile_memory()` — store N entries → persist → resume → assert all N present.

### N2 — `run_cycle()` generates two different `correlation_id`s (P0, traceability)
**File:** `model/agent.py:157,166`
**Root cause:** `_decision_to_command(decision)` is called **twice** per cycle — once for `act()`
(line 157) and once for the `DecisionTrace.action` (line 166). Each call mints a fresh
`uuid.uuid4()` (`agent.py:369`). The command actually executed therefore has a different
`correlation_id` than the command recorded in the trace.
**Impact:** Action↔trace correlation is broken; reflection critiques an action that does not match
what ran; auditing/replay impossible.
**Fix:** Compute `command = _decision_to_command(decision)` once, use it for both `act()` and the trace.
**Test:** `test_run_cycle_trace_action_matches_executed_command()` — assert `trace.action.correlation_id == executed.correlation_id`.

### N3 — Policy repository is dead code; persistence semantics inconsistent (P1)
**File:** `model/agent.py:79` + `persistence/repositories_db.py:88-126`
**Root cause:** `self._pol_repo = PolicyRepository(db_path)` is constructed but **never used** (grep
confirms zero write/read call sites). Policy rules are persisted only inside `SessionSnapshot.policy_store`
and restored from there. Meanwhile goals persist via `_goal_repo` on every add/update, and memory via
`_mem_repo`. So three aggregates use **three different persistence strategies**:
  - policy → snapshot-only
  - goals → repo-only (immediate)
  - memory → repo-only (persistent tier) + volatile lost (see N1)
**Impact:** Confusing, error-prone. If `persist()` is never called, policy rules added via
`update_policy`/reflection are **lost** on process exit (they only live in `policy_engine.rules`
in memory until the next snapshot). Goals, by contrast, survive.
**Fix:** Pick one strategy. Recommended: persist **all** aggregates through their repositories
on change (eventual consistency) AND snapshot them for atomic restore. At minimum, make policy
repo-based like goals: `add_rule` → `_pol_repo.save`, `resume_session` → `_pol_repo.load_by_agent`.
**Test:** `test_policy_rule_survives_without_snapshot()` — add rule, no persist, new process, resume → rule present.

### N4 — Self-improvement loop is inert in default (SUPERVISED) autonomy (P1)
**File:** `reflection/safety_evaluator.py:36-37` + `reflection/engine.py:153`
**Root cause:** `DefaultSafetyEvaluator` returns `NEEDS_CONFIRMATION` for **every** proposal when
`autonomy_level ∈ {SUPERVISED, CONFIRMATION_REQUIRED, MANUAL_ONLY}` — i.e. all non-autonomous
levels. The router only routes proposals with verdict `APPROVED` (`engine.py:153`). There is
**no confirmation/approval flow** anywhere in the codebase to promote `NEEDS_CONFIRMATION → APPLIED`.
**Impact:** With the default config (`autonomy_level=SUPERVISED`, set in `main_controller.py:111`),
reflection generates proposals that are permanently stuck at `NEEDS_CONFIRMATION`. The agent never
self-improves. This is the single biggest functional gap: the headline feature (reflection) is a no-op.
**Fix:** Add a confirmation pathway — either (a) an `approve_proposal(entry_id, idx)` method on
`Agent`/`AgentController` + a TUI command (`approve`), or (b) auto-apply `NEEDS_CONFIRMATION`
proposals of "safe" types (MEMORY_UPDATE) in supervised mode and require confirmation only for
POLICY_CHANGE/GOAL_ADJUSTMENT/TOOL_CONFIGURATION. Wire the TUI to list pending proposals and accept approval.
**Test:** `test_supervised_proposal_can_be_approved_and_applied()`.

### N5 — TOOL_CONFIGURATION disable/enable is a no-op (P1)
**File:** `reflection/proposal_router.py:120-123` + `model/agent.py:223` (`perceive`) + `tools/registry.py:120`
**Root cause:** `_apply_tool_config` flips `spec.enabled` on the `ToolSpec`, but neither `perceive()`
nor `execute_safely()` consult `spec.enabled`. `perceive` iterates `list_sensors()` (all registered
sensors); `execute_safely` looks up the actuator by id. So a "disabled" tool keeps sensing and acting.
**Impact:** Reflection-driven tool configuration has zero effect. A safety-motivated "disable
filesystem" proposal would not actually stop the filesystem sensor from running.
**Fix:** Add `ToolRegistry.is_enabled(tool_id)` and gate `perceive()`/`execute_safely()` on it; or
filter `list_sensors()`/`list_actuators()` to enabled-only. Provide `set_tool_enabled()` public API (also fixes M6).
**Test:** `test_disable_tool_stops_perception()`.

### N6 — View reaches through controller into Model internals (P1, MVC++)
**File:** `view/tui/agent_screen.py:258,273,297,314,371,451,468` + `controller/agent_controller.py:112`
**Root cause:** `AgentTUIScreen` calls `self._controller.get_agent()` then directly accesses
`agent.goal_manager`, `agent.policy_engine`, `agent.memory`, and `agent.persist()`. This is a
View→Model leak that `mvc_check.py` cannot detect (the leak is through a return type).
`AgentController` exposes `get_agent() -> Agent` (concrete class!) and lacks partner methods for
listing goals/rules/memory and saving — forcing the view to reach through.
**Impact:** Breaks MVC++ isolation in practice (even if the linter is clean). Tightly couples the
Textual view to concrete Model classes.
**Fix:** Remove `get_agent()` from the controller; add `list_goals()`, `list_rules()`,
`query_memory()`, `save_snapshot()` to `AgentController` (delegating to `IAgentModelPartner`).
Update `AgentTUIScreen` to call controller methods only. Add `IAgentModelPartner.list_rules()` etc.
**Test:** `test_view_never_imports_concrete_model()` — static check that `agent_screen.py` imports
only interfaces/controller.

### N7 — Config is not restored on resume (P2)
**File:** `model/agent.py:131-145`
**Root cause:** `resume_session()` restores policy/goals/memory but **not** `self.config`
(sandbox_root, autonomy_level, reflection_config, etc.). The snapshot stores only `config_version`.
A resumed agent silently keeps whatever `AgentConfig` it was constructed with.
**Impact:** If you construct a default-config Agent and resume an old snapshot, you lose the original
sandbox path and autonomy level. Policy conditions that reference `agent.autonomy` would behave differently.
**Fix:** Serialise key config fields (or the whole config) into the snapshot; restore in `resume_session`.
**Test:** `test_resume_restores_config()`.

### N8 — Goal tree root drifts on resume (P2)
**File:** `model/agent.py:208` + `goal/manager.py:133-136` + `schema_db.py:155`
**Root cause:** `persist()` saves `goal_tree={"root": self.goal_manager.get_tree().root}` — only the
root id. But `resume_session()` calls `goal_manager.load_from_repository()`, which rebuilds the tree
by re-adding goals from `SELECT_BY_AGENT` — a query with **no `ORDER BY`** (`schema_db.py:155`).
`GoalTree.add` sets `root` to the first goal inserted. So the restored root is whichever row SQLite
returns first, not the persisted root. The saved `goal_tree.root` is **ignored**.
**Impact:** Goal-tree structure can subtly change across save/resume; root may shift to a leaf.
**Fix:** Either restore `tree.root` from the snapshot after `load_from_repository()`, or add
`ORDER BY created_at ASC` to `TableGoals.SELECT_BY_AGENT` and respect the persisted root.
**Test:** `test_resume_preserves_goal_root()`.

### N9 — `resume_session()` doesn't clear existing rules/goals before restoring (P2)
**File:** `model/agent.py:137-144`
**Root cause:** `resume_session` calls `policy_engine.add_rule(rule)` and reloads goals/memory **on top
of** whatever is already in the in-memory state. If resume is invoked on a non-fresh agent (e.g. after
`start_session` or mid-session), stale rules and goals remain. (For rules, `add_rule` overwrites by id,
so same-id rules are fine — but rules that existed before and aren't in the snapshot persist.)
**Impact:** State leakage between sessions on the same Agent instance.
**Fix:** Clear `policy_engine.rules`/`_compiled`, `goal_manager._tree`, `memory._volatile` before
restoring from the snapshot/repo.
**Test:** `test_resume_clears_pre_existing_state()`.

---

## P0 — Blockers (Must Fix First)

### C1: `resume_session()` doesn't re-register built-in tools
**File:** `model/agent.py:131-145`
**Fix:** Call `self._register_builtin_tools(self.config)` at end of `resume_session()`.
**Test:** `test_resume_session_restores_tools()` — assert `list_sensors()` includes filesystem, rag_query, session.
**Effort:** 15 min

### C2: `reflect()` returns engine instead of result
**File:** `model/agent.py:274-276`
**Fix:** `def reflect(self, trace: DecisionTrace, ctx: PolicyContext) -> ReflectionEntry: return self.reflection_engine.reflect(trace, ctx)`. (`run_cycle` already calls the engine directly — this fixes the external API.)
**Effort:** 10 min

### C3: `resume_session()` doesn't restore `_ai_service`
**File:** `model/agent.py:131-145`
**Fix:** Option B (recommended) — document that `set_ai_service()` must be re-called after resume, and have `AgentAdapter.create()` / `MainController.show_agent()` re-inject on the resume path. (The AI service is a runtime object, not serialisable.)
**Effort:** 10 min

### C4: Controller accesses private `_db` (MVC++)
**File:** `controller/session_controller.py:24`
**Fix:** Add `load_snapshot(snapshot_id) -> SessionSnapshot | None` to `IAgentModelPartner` + `Agent`; controller calls the partner method.
**Effort:** 20 min

### C5: `MainController.show_agent()` creates a new agent every time
**File:** `ui/screens/main/main_controller.py:90-120`
**Fix:**
- Reuse `self._agent_controller` if already set.
- On first creation, after building the agent, call `self._db.load_latest_snapshot(agent_id)` and `resume_session()` if a snapshot exists.
- Route through `AgentAdapter` (currently bypassed) for consistent wiring.
**Effort:** 30 min

### C6: Goal completion over-eager in `act()`
**File:** `model/agent.py:268-271`
**Fix:** Only mark the active goal complete when the executed tool corresponds to that goal. Concretely: only complete if `command.actuator_id` matches the goal's expected tool (store expected tool in `SuccessCriteria`/goal metadata), or require an explicit `expression`-style criteria. At minimum, do not complete on unrelated tools.
**Effort:** 20 min

### N1: Volatile memory lost on resume  *(new)*
**See above.** **Effort:** 25 min

### N2: Double `correlation_id` in `run_cycle()`  *(new)*
**See above.** **Effort:** 10 min

---

## P1 — High Priority

### M1: `perceive()` swallows sensor exceptions silently
**File:** `model/agent.py:235-236`
**Fix:** On exception, emit `SensorReading(sensor_id=sid, data={"error": str(exc)}, confidence=0.0)` and still add it to `readings` so the policy layer can react to `confidence == 0`.
**Effort:** 15 min

### M3: Reflection proposals dropped silently if safety/router missing
**File:** `reflection/engine.py:142-144`
**Fix:** Log a warning when `_safety`/`_router` is None; mark proposals `NEEDS_CONFIRMATION` so they're visible rather than silently un-routed.
**Effort:** 10 min

### M7: Safety evaluator deny-list incomplete
**File:** `reflection/safety_evaluator.py:25-40`
**Fix:** Define standard `op` values per `ProposalType` (e.g. `GOAL_ADJUSTMENT` → `abandon_root|delete|demote`; `TOOL_CONFIGURATION` → `delete`; `POLICY_CHANGE` → `delete`). Validate the `op` schema; reject unknown dangerous ops.
**Effort:** 20 min

### M8: `SessionTool.act()` calls non-existent `resume()`
**File:** `tools/session_tool.py:99-100`
**Fix:** `self._agent.resume_session(snapshot_id)`; change the `hasattr` guard to check `resume_session`.
**Effort:** 5 min

### I1: No session resume in TUI
**Files:** `ui/screens/main/main_controller.py`, `agent/adapter.py`
**Fix:** `AgentAdapter.create(config, agent_id=None, resume=True)` — if `agent_id` given and a latest snapshot exists, resume it. `MainController.show_agent()` loads latest snapshot for the PID-stable agent id.
**Effort:** 30 min

### I4: AI Service coupling — adapter created in controller
**File:** `ui/screens/main/main_controller.py:118`
**Fix:** Move AI-service wiring into `AgentAdapter.create()` (inject via config/provider). Controller should not import `AIServiceAdapter`.
**Effort:** 15 min

### N3: Policy repo dead code / inconsistent persistence  *(new)*
**See above.** **Effort:** 30 min

### N4: Self-improvement loop inert in SUPERVISED mode  *(new)*
**See above.** **Effort:** 45 min (needs approval flow + TUI command)

### N5: TOOL_CONFIGURATION disable is a no-op  *(new)*
**See above.** **Effort:** 20 min

### N6: View→Model leaks in AgentTUIScreen  *(new)*
**See above.** **Effort:** 40 min

---

## P2 — Medium Priority

### M2: `reflection_log_position` stored but never read
**File:** `model/agent.py:209,131-145`
**Fix:** In `resume_session()`, reconstruct `reflection_engine._entries` from `_refl_repo.load_recent(self.id, limit=reflection_log_position)`. Note `load_recent` returns `list[dict]` — add a `_row_to_reflection_entry` mapper in `repositories_db.py` (currently missing).
**Effort:** 25 min

### M5: Policy condition type errors silently return `False`
**File:** `policy/rule.py:339-355`
**Fix:** Log a warning on `TypeError` in `_compare()`; consider raising in a strict/debug mode.
**Effort:** 10 min

### M6: Proposal router accesses private `_specs`
**File:** `reflection/proposal_router.py:117,129`
**Fix:** Add `ToolRegistry.set_tool_enabled(tool_id, enabled) -> bool` and `is_enabled(tool_id) -> bool` public methods; router uses those. (Overlaps with N5.)
**Effort:** 10 min

### N7: Config not restored on resume  *(new)*
**See above.** **Effort:** 15 min

### N8: Goal root drifts on resume  *(new)*
**See above.** **Effort:** 15 min

### N9: `resume_session()` doesn't clear pre-existing state  *(new)*
**See above.** **Effort:** 10 min

### N10: `show_agent()` uses PID id and never calls `start_session()`  *(new)*
**File:** `ui/screens/main/main_controller.py:107,115`
**Root cause:** `agent_id = f"agent_{os.getpid()}"` and `Agent(config)` is called directly (not `start_session`). The agent row is never upserted; snapshots accumulate under the id but the row is missing.
**Fix:** Call `agent.start_session(config)` (which upserts the row), or a stable agent id persisted across runs.
**Effort:** 15 min

### N11: Reflection log polluted with no-AI entries every cycle  *(new)*
**File:** `model/agent.py:159-173` + `reflection/engine.py:86-97`
**Root cause:** With `reflection_config.enabled=True` (default) and no AI service, every cycle creates and **persists** a "(reflection disabled — no AI service)" `ReflectionEntry`.
**Fix:** Skip the reflection block (and the repo save) when `self._ai_service is None`; or gate on a `reflection_config.enabled and ai_configured` flag.
**Effort:** 10 min

### N12: RAG integration is read-only (availability), not queryable via actions  *(new)*
**File:** `tools/rag_sensor_tool.py`
**Root cause:** `RagSensorTool` is registered as a sensor only. It has a `query()` method but no `IActuator` implementation, so a policy rule cannot `EXECUTE_TOOL rag_query` to actually retrieve knowledge — it can only sense RAG availability.
**Fix:** Either add an actuator facet to `RagSensorTool` (like `SessionTool`/`FileSystemTool` hybrids) exposing a `query` action, or document that RAG query is invoked through a different path.
**Effort:** 20 min

---

## P3 — Low Priority (Code Quality / Encapsulation)

| ID | File | Line | Fix | Status |
|----|------|------|-----|--------|
| m1 | `model/agent.py` | 357-370 | Validate `tool_id` in `_decision_to_command()` (empty → None) | confirmed |
| m2 | `model/agent.py` | 328-337 | Make `MemoryQuery.limit` configurable via `AgentConfig` | confirmed |
| m4 | `model/goal/manager.py` | 45-46 | `if not active and len(active) < max` — `len(active)` is always 0 when `not active`; the limit check is dead. Simplify to `if not active:` | confirmed |
| m5 | `reflection/critique_parser.py` | 57 | Fenced-JSON regex `\{.*?\}` is non-greedy → breaks nested objects; use greedy + brace matching | confirmed |
| m7 | `interfaces.py` | 193-196 | `IPersistencePartner.load_snapshot()` return type annotated `SessionSnapshot` but impl returns `SessionSnapshot | None` — align | confirmed |
| m8 | `view/tui/agent_screen.py` | 258+ | Use view-partner/controller method instead of `get_agent()` (subsumed by N6) | confirmed |
| m9 | `adapter.py` | 32 | `cast(IAgentViewPartner, screen)` — add runtime `isinstance`/registration check before cast | confirmed |
| m10 | `tools/filesystem_tool.py` | 36-50 | `rglob("*")` on every perceive() — cache or sample; can be very slow on large trees | confirmed |
| C7* | `model/agent.py` | 76 | Canonicalise/validate `persistent_path` (default already exists in `types.py:175`) | downgraded |
| N13 | `model/agent.py` | 196,283 | `get_status()` reads private `self.memory._volatile`; `set_ai_service` mutates private `reflection_engine._ai`. Add public accessors. | new |
| N14 | `controller/agent_controller.py` | 98; `tool_controller.py` | Controllers reach into `agent.policy_engine`/`agent.tool_registry` public attrs, bypassing `IAgentModelPartner`. Add `list_rules()`/`list_tools()` to the partner. | new |
| N15 | `policy/conflict_resolver.py` | 56-67 | `_condition_overlap` uses raw token Jaccard incl. operators/parens — crude; normalise tokens first. | new |
| N16 | `reflection/engine.py` | 129 | `str(trace.perception.sensor_readings.keys())` renders as `dict_keys([...])` — format cleanly for the prompt. | new |

---

## Root-Cause Analysis (Systemic Issues)

Three themes recur across the bug list. Fixing these prevents whole classes of
future bugs:

1. **Incomplete `resume_session()`** (drives C1, C3, N1, N7, N8, N9, M2).
   Resume restores *some* subsystems but misses tools, AI service, volatile
   memory, config, goal root, and reflection log. The fix is a single
   auditable `resume_session()` that restores **every** piece of state, with a
   test that persists a fully-populated agent and asserts byte-for-byte
   restoration of each subsystem.

2. **Persistence strategy is inconsistent** (drives N3, N1, N10).
   Policy uses snapshots; goals/memory use repos; volatile is nowhere. Choose
   one model (recommendation: repos for live state + snapshot for atomic
   point-in-time restore) and apply it uniformly. Kill the dead `_pol_repo`.

3. **The reflection→action loop is not closed** (drives N4, N5, M3, M7).
   Reflection can *produce* proposals but there is no path to *apply* them in
   the default autonomy level, and tool-config proposals don't take effect even
   when applied. The self-improvement feature is architecturally present but
   functionally inert. Closing the loop (approval flow + effective routing) is
   the highest-value work after the P0 resume fixes.

---

## Implementation Order (Dependency-Aware, updated)

```mermaid
graph TD
    C7[C7: path validation P3] --> C1[C1: Resume tools]
    N1[N1: Volatile memory on resume] --> C1
    N9[N9: Clear state on resume] --> C1
    C1 --> C3[C3: AI service on resume]
    N7[N7: Config on resume] --> C3
    N8[N8: Goal root on resume] --> C3
    M2[M2: Reflection log on resume] --> C3
    N2[N2: Single correlation_id] --> C6[C6: Goal completion logic]
    C4[C4: MVC++ load_snapshot] --> N6[N6: View->Model leaks]
    C6 --> N6
    M8[M8: SessionTool resume_session] --> C5[C5: UI reuse + resume]
    N10[N10: start_session + stable id] --> C5
    I1[I1: Adapter resume] --> C5
    I4[I4: AI wiring in adapter] --> C5
    C5 --> N4[N4: Approval flow]
    M1[M1: Perceive errors] --> N5[N5: Tool-disable effective]
    M6[M6: set_tool_enabled API] --> N5
    N5 --> N4
    M3[M3: Reflection silent drop] --> N4
    M7[M7: Safety deny-list] --> N4
    N3[N3: Unify persistence] --> C5
    N11[N11: Skip reflection w/o AI] --> N4
    C2[C2: reflect() signature] -.optional.-> N4
    M5[M5: Policy type errors] -.optional.-> M1
    N12[N12: RAG actuator] -.optional.-> N4
```

**Critical path:** N9 + N1 → C1 → C3 (+N7/N8/M2) → C5 + I1 → N4 (close the loop).
**Parallelisable early:** C2, C4, C6, M8, N2, N10, N11.

---

## Test Strategy (updated)

| Bug | Test to add |
|-----|-------------|
| C1 | `test_resume_session_restores_tools()` — `list_sensors()` after resume |
| C2 | `test_reflect_returns_reflection_entry()` — type-check return |
| C3 | `test_resume_then_set_ai_service_enables_reflection()` |
| C4 | `test_controller_load_snapshot_uses_partner()` — no `_db` access |
| C5 | `test_show_agent_reuses_existing_agent()` — same agent_id on reopen |
| C6 | `test_goal_complete_only_on_relevant_tool()` — unrelated tool doesn't complete |
| N1 | `test_resume_restores_volatile_memory()` — N entries round-trip |
| N2 | `test_run_cycle_trace_action_matches_executed_command()` — same correlation_id |
| N3 | `test_policy_rule_survives_without_snapshot()` |
| N4 | `test_supervised_proposal_can_be_approved_and_applied()` |
| N5 | `test_disable_tool_stops_perception()` |
| N6 | `test_view_never_imports_concrete_model()` — static import check |
| N7 | `test_resume_restores_config()` |
| N8 | `test_resume_preserves_goal_root()` |
| N9 | `test_resume_clears_pre_existing_state()` |
| M1 | `test_perceive_returns_failed_reading_on_sensor_error()` — confidence=0 |
| M8 | `test_session_tool_restore_calls_resume_session()` |
| M2 | `test_resume_restores_reflection_log()` |

**Regression guard:** after each group, run
`uv run pytest tests/features/feature_007.agentx_intelligent_agent_behaviour -q`
(must stay 137/137) and `uv run scripts/omt/mvc_check.py src/agentx/agent/`
(must stay 0/0).

---

## Acceptance Criteria

- [x] All 8 P0 bugs fixed and verified by new tests
- [x] All 137 existing tests still pass
- [x] `uv run scripts/omt/mvc_check.py src/agentx/agent/` → 0 errors, 0 warnings
- [x] End-to-end: User opens Agent TUI → submits goal → adds rule → runs cycle → saves → closes → reopens → **state restored (goals, rules, memory, tools, config, reflection log)**
- [x] Reflection produces proposals after resume (with AI service re-injected)
- [x] **NEW:** A SUPERVISED-mode proposal can be approved via the TUI and takes effect
- [x] **NEW:** Disabling a tool via reflection actually stops it from sensing/acting
- [x] **NEW:** `run_cycle` trace action `correlation_id` matches the executed command
- [x] **NEW (P2/P3):** All remaining items (M5, N12, m1/m2/m4/m5/m7/m9/m10, C7*, N13–N16) fixed

---

## Tracking

> **2026-07-04 implementation pass:** ALL bugs (P0–P3) fixed and covered by
> 32 regression tests (`test_bug_fixes.py`). 169/169 feature_007 tests pass;
> full suite 434/435 (1 pre-existing unrelated failure); MVC++ 0/0 on
> `src/agentx/agent/`. Only M4 remains dropped (false positive).

| Bug | Priority | Status | PR/Commit | Verified |
|-----|----------|--------|-----------|----------|
| C1 | P0 | ✅ Fixed | 2026-07-04 | test_resume_restores_tools |
| C2 | P0 | ✅ Fixed | 2026-07-04 | test_reflect_returns_reflection_entry |
| C3 | P0 | ✅ Fixed | 2026-07-04 | adapter re-injects AI on resume |
| C4 | P0 | ✅ Fixed | 2026-07-04 | test_controller_load_snapshot_uses_facade |
| C5 | P0 | ✅ Fixed | 2026-07-04 | show_agent reuses + adapter resumes |
| C6 | P0 | ✅ Fixed | 2026-07-04 | test_goal_complete_only_on_relevant_tool |
| N1 | P0 | ✅ Fixed (new) | 2026-07-04 | test_resume_restores_volatile_memory |
| N2 | P0 | ✅ Fixed (new) | 2026-07-04 | test_run_cycle_trace_action_matches_executed_command |
| M1 | P1 | ✅ Fixed | 2026-07-04 | test_perceive_returns_failed_reading_on_sensor_error |
| M3 | P1 | ✅ Fixed | 2026-07-04 | un-routed proposals → NEEDS_CONFIRMATION |
| M7 | P1 | ✅ Fixed | 2026-07-04 | test_safety_deny_list_rejects_dangerous_ops |
| M8 | P1 | ✅ Fixed | 2026-07-04 | test_session_tool_restore_calls_resume_session |
| I1 | P1 | ✅ Fixed | 2026-07-04 | AgentAdapter.create_agent(resume=True) |
| I4 | P1 | ✅ Fixed | 2026-07-04 | AI wiring moved to AgentAdapter |
| N3 | P1 | ✅ Fixed (new) | 2026-07-04 | test_policy_rule_survives_without_snapshot |
| N4 | P1 | ✅ Fixed (new) | 2026-07-04 | test_supervised_proposal_can_be_approved_and_applied |
| N5 | P1 | ✅ Fixed (new) | 2026-07-04 | test_disable_tool_stops_perception / _blocks_execution |
| N6 | P1 | ✅ Fixed (new) | 2026-07-04 | test_controller_exposes_partner_query_methods; get_agent() removed |
| M2 | P2 | ✅ Fixed | 2026-07-04 | test_resume_restores_reflection_log |
| M5 | P2 | ✅ Fixed | 2026-07-04 | test_condition_compare_logs_typeerror |
| M6 | P2 | ✅ Fixed | 2026-07-04 | folded into N5 (set_tool_enabled API) |
| N7 | P2 | ✅ Fixed (new) | 2026-07-04 | test_resume_restores_config |
| N8 | P2 | ✅ Fixed (new) | 2026-07-04 | test_resume_preserves_goal_root |
| N9 | P2 | ✅ Fixed (new) | 2026-07-04 | test_resume_clears_pre_existing_state |
| N10 | P2 | ✅ Fixed (new) | 2026-07-04 | show_agent reuses + resumes (PID id stable per process) |
| N11 | P2 | ✅ Fixed (new) | 2026-07-04 | test_reflection_skipped_without_ai_service |
| N12 | P2 | ✅ Fixed (new) | 2026-07-04 | test_rag_tool_actuator_query / _rejects_unknown_action |
| m1 | P3 | ✅ Fixed | 2026-07-04 | test_decision_to_command_drops_empty_tool_id |
| m2 | P3 | ✅ Fixed | 2026-07-04 | test_context_memory_limit_configurable |
| m4 | P3 | ✅ Fixed | 2026-07-04 | dead limit clause removed (single-active model preserved) |
| m5 | P3 | ✅ Fixed | 2026-07-04 | test_critique_parser_handles_nested_json |
| m7 | P3 | ✅ Fixed | 2026-07-04 | IPersistencePartner.load_snapshot → `SessionSnapshot | None` |
| m9 | P3 | ✅ Fixed | 2026-07-04 | _wire_view() runtime isinstance check |
| m10 | P3 | ✅ Fixed | 2026-07-04 | test_filesystem_scan_capped (MAX_FILES) |
| C7* | P3 | ✅ Fixed | 2026-07-04 | test_persistent_path_canonicalized |
| N13 | P3 | ✅ Fixed (new) | 2026-07-04 | ReflectionEngine.set_ai_service() public API |
| N14 | P3 | ✅ Fixed (new) | 2026-07-04 | list_tools/register_tool/etc. on facade; ToolController via facade |
| N15 | P3 | ✅ Fixed (new) | 2026-07-04 | test_conflict_overlap_ignores_operators |
| N16 | P3 | ✅ Fixed (new) | 2026-07-04 | perception keys joined cleanly in prompt |
| m8 | P3 | ✅ Subsumed | 2026-07-04 | by N6 (view no longer reaches into model) |
| M4 | — | ❌ Dropped (false positive — already fixed) | | |

---

## Notes for Implementer

1. **Start with the resume subsystem (N9 → N1 → C1 → C3 + N7/N8/M2).** This is
   the foundation: a fully-correct `resume_session()` that restores *every*
   piece of state. Write the round-trip test first.
2. **Then N2 + C6** — fix traceability and goal-completion correctness in
   `run_cycle`/`act`.
3. **Then C5 + I1 + I4 + N10** — UI integration (agent reuse, session resume,
   AI wiring, stable id).
4. **Then close the reflection loop (N4 + N5 + M3 + M7 + M6 + N11).** This is
   what makes the headline feature actually work.
5. **Then N3** — unify persistence (kill dead `_pol_repo`, pick one strategy).
6. **Then N6 + C4** — MVC++ hygiene (controller partner methods, remove
   `get_agent()`).
7. **Run full test suite after each group:** `uv run pytest tests/features/feature_007.agentx_intelligent_agent_behaviour -q`
8. **Run MVC check after any controller/interface change:** `uv run scripts/omt/mvc_check.py src/agentx/agent/`
9. M4 is a **false positive** — do not "fix" it; the guard already exists at
   `registry.py:143`.

---

**Next Step:** Declare OMT++ phase (`bug_fix` task type) and begin implementation
with the resume-subsystem group. The highest-leverage single fix is **N4** (close
the reflection loop) — but it depends on the resume + UI work landing first.
