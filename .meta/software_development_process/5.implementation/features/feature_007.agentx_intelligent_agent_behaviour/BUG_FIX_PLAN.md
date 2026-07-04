# Bug Fix Plan — feature_007.agentx_intelligent_agent_behaviour

**Created:** 2026-07-04  
**Source:** Comprehensive bug review of `src/agentx/agent/` (38 files)  
**Test Baseline:** 137 feature_007 tests pass; MVC++ 0 errors on agent module

---

## Priority Matrix

| Priority | Count | Description |
|----------|-------|-------------|
| **P0 — Blocker** | 7 | Core lifecycle broken (session resume, reflection, goal completion) |
| **P1 — High** | 6 | Silent failures, safety gaps, MVC++ violations |
| **P2 — Medium** | 5 | Data loss, integration friction, API mismatches |
| **P3 — Low** | 10 | Code quality, performance, encapsulation |

---

## P0 — Blockers (Must Fix First)

### C1: `resume_session()` doesn't re-register built-in tools
**File:** `src/agentx/agent/model/agent.py` (lines 131–145)  
**Fix:** Call `self._register_builtin_tools(config)` at end of `resume_session()`  
**Test:** Add integration test: create agent → persist → resume → verify `list_sensors()` includes filesystem, rag_query, session  
**Effort:** 15 min

### C2: `reflect()` returns engine instead of result
**File:** `src/agentx/agent/model/agent.py` (lines 274–276)  
**Fix:** Change signature to `def reflect(self, trace: DecisionTrace, ctx: PolicyContext) -> ReflectionEntry` and delegate to engine  
**Note:** Internal `run_cycle()` already calls engine directly — this fixes external API only  
**Effort:** 10 min

### C3: `resume_session()` doesn't restore `_ai_service`
**File:** `src/agentx/agent/model/agent.py` (line 143)  
**Fix Option A:** Store AI service reference in snapshot (not serializable)  
**Fix Option B:** Document that `set_ai_service()` must be called after resume (current impl_notes.md §3 says "injected later")  
**Recommendation:** Option B — add explicit comment + auto-call in `AgentAdapter.create()`  
**Effort:** 10 min

### C4: Controller accesses private `_db` (MVC++ violation)
**File:** `src/agentx/agent/controller/session_controller.py` (line 24)  
**Fix:** Add `load_snapshot(snapshot_id) -> SessionSnapshot | None` to `IAgentModelPartner` / `Agent` facade; controller calls partner method  
**Effort:** 20 min

### C5: `MainController.show_agent()` creates new agent every time
**File:** `src/agentx/ui/screens/main/main_controller.py` (lines 90–120)  
**Fix:** 
- Check for existing `_agent_controller` and reuse
- Or: load latest snapshot via `SessionDatabase.load_latest_snapshot()`
- Wire `AgentAdapter.create()` to use existing agent if available
**Effort:** 30 min

### C6: Goal completion logic over-eager in `act()`
**File:** `src/agentx/agent/model/agent.py` (lines 268–271)  
**Fix:** Only mark goal complete if `command.correlation_id` matches goal's expected action, OR if `success_criteria.kind == "tool_success"` AND `action_result` corresponds to that goal's tool  
**Effort:** 20 min

### C7: DB path fragile — no explicit default in model
**File:** `src/agentx/agent/model/agent.py` (line 76)  
**Fix:** Add default `persistent_path` to `MemoryConfig` (e.g., `".agentx/memory"`) and ensure directory creation in `SessionDatabase._ensure_schema()` (already does `mkdir(parents=True)`)  
**Effort:** 10 min

---

## P1 — High Priority

### M1: `perceive()` swallows sensor exceptions silently
**File:** `src/agentx/agent/model/agent.py` (lines 219–241)  
**Fix:** Return `SensorReading(confidence=0.0, data={"error": str(exc)})` instead of just logging; policy can check `confidence == 0.0`  
**Effort:** 15 min

### M3: Reflection proposals dropped silently if safety/router missing
**File:** `src/agentx/agent/model/reflection/engine.py` (lines 142–154)  
**Fix:** Log warning when `_safety` or `_router` is None; return proposals with `status=NEEDS_CONFIRMATION` so they're visible  
**Effort:** 10 min

### M7: Safety evaluator deny-list incomplete
**File:** `src/agentx/agent/model/reflection/safety_evaluator.py` (lines 24–40)  
**Fix:** Define standard `op` values for each `ProposalType` (e.g., `GOAL_ADJUSTMENT` → `abandon_root`, `delete`, `demote`); validate content schema  
**Effort:** 20 min

### M8: `SessionTool.act()` calls non-existent `resume()` method
**File:** `src/agentx/agent/model/tools/session_tool.py` (line 100)  
**Fix:** Change `self._agent.resume(snapshot_id)` → `self._agent.resume_session(snapshot_id)`  
**Effort:** 5 min

### I1: UI integration — no session resume in TUI
**Files:** `src/agentx/ui/screens/main/main_controller.py`, `src/agentx/agent/adapter.py`  
**Fix:** `AgentAdapter.create()` should accept optional `agent_id` to resume; `MainController.show_agent()` should load latest snapshot if exists  
**Effort:** 30 min

### I4: AI Service coupling — `AIServiceAdapter` created in controller
**File:** `src/agentx/ui/screens/main/main_controller.py` (line 118)  
**Fix:** Move AI service wiring to `AgentAdapter.create()`; inject via config or provider  
**Effort:** 15 min

---

## P2 — Medium Priority

### M2: `persist()` stores `reflection_log_position` but never reads it
**File:** `src/agentx/agent/model/agent.py` (lines 199–215, 131–145)  
**Fix:** In `resume_session()`, set `self.reflection_engine._entries = self._refl_repo.load_recent(agent_id, limit=reflection_log_position)` (adjust repo method)  
**Effort:** 20 min

### M4: `ActuatorResult.duration_ms` clobbers tool's own timing
**File:** `src/agentx/agent/model/tools/registry.py` (lines 142–144)  
**Fix:** Only set `duration_ms` if result has `duration_ms == 0`  
**Effort:** 5 min

### M5: Policy condition type errors silently return `False`
**File:** `src/agentx/agent/model/policy/rule.py` (line 339)  
**Fix:** Log warning on `TypeError` in `_compare()`; consider raising in strict mode  
**Effort:** 10 min

### M6: Proposal router accesses private `_specs`
**File:** `src/agentx/agent/model/reflection/proposal_router.py` (lines 117, 129)  
**Fix:** Add `ToolRegistry.set_tool_enabled(tool_id: str, enabled: bool) -> bool` public method  
**Effort:** 10 min

### m3: `MemoryManager.retrieve()` O(N) scan of persistent entries
**File:** `src/agentx/agent/model/memory/manager.py` (lines 53–78)  
**Fix:** Push filters to SQL in `MemoryRepository.load_by_agent()` — add optional `source`, `tags`, `min_importance`, `time_range` params  
**Effort:** 30 min

---

## P3 — Low Priority (Code Quality)

| ID | File | Line | Fix |
|----|------|------|-----|
| m1 | `model/agent.py` | 357–370 | Validate `tool_id` in `_decision_to_command()` |
| m2 | `model/agent.py` | 328–337 | Make `MemoryQuery.limit` configurable via `AgentConfig` |
| m4 | `model/goal/manager.py` | 45–46 | Fix off-by-one in `add_goal()` active count |
| m5 | `model/reflection/critique_parser.py` | 57 | Improve JSON extraction for multiple blocks |
| m7 | `interfaces.py` | 193–196 | Align `IPersistencePartner.load_snapshot()` return type with impl |
| m8 | `view/tui/agent_screen.py` | 258 | Use view-partner method instead of reaching to model |
| m9 | `adapter.py` | 32 | Add runtime `isinstance` check before cast |
| m10 | `model/tools/filesystem_tool.py` | 36–50 | Cache filesystem scan or add sampling rate |

---

## Implementation Order (Dependency-Aware)

```mermaid
graph TD
    C1[C1: Resume tools] --> C5[C5: UI reuse agent]
    C2[C2: Fix reflect()] --> C3[C3: AI service on resume]
    C4[C4: MVC++ fix] --> I1[I1: UI session resume]
    C7[C7: DB path default] --> C1
    M8[M8: SessionTool resume] --> C5
    M1[M1: Perceive errors] --> C1
    M3[M3: Reflection silent drop] --> C3
    M7[M7: Safety deny-list] --> M3
    I4[I4: AI service wiring] --> C5
    M2[M2: Reflection log pos] --> C1
    M4[M4: Duration ms] --> M1
    M5[M5: Policy type errors] --> M1
    M6[M6: Tool enabled API] --> M7
    m3[m3: Memory SQL filters] --> M1
```

**Critical Path:** C7 → C1 → C5 + I1 (session resume end-to-end)  
**Parallelizable:** C2, C3, C4, C6, M8, M1, M3, M7

---

## Test Strategy

| Bug | Test to Add |
|-----|-------------|
| C1 | `test_resume_session_restores_tools()` — assert `list_sensors()` after resume |
| C2 | `test_reflect_returns_reflection_entry()` — type check return value |
| C3 | `test_resume_preserves_ai_service()` — or doc test for re-injection |
| C4 | `test_controller_uses_partner_for_load_snapshot()` — no `_db` access |
| C5 | `test_show_agent_reuses_existing_agent()` — same agent_id on reopen |
| C6 | `test_goal_complete_only_on_relevant_tool()` — unrelated tool doesn't complete goal |
| M1 | `test_perceive_returns_failed_reading_on_sensor_error()` — confidence=0 |
| M8 | `test_session_tool_restore_calls_resume_session()` — method name fix |

---

## Acceptance Criteria

- [ ] All 7 P0 bugs fixed and verified by new tests
- [ ] All 137 existing tests still pass
- [ ] `uv run scripts/omt/mvc_check.py src/agentx/agent/` → 0 errors, 0 warnings
- [ ] End-to-end: User opens Agent TUI → submits goal → adds rule → runs cycle → saves → closes → reopens → state restored (goals, rules, memory, tools)
- [ ] Reflection produces proposals after resume (with AI service re-injected)

---

## Tracking

| Bug | Status | PR/Commit | Verified |
|-----|--------|-----------|----------|
| C1 | 📋 Planned | | |
| C2 | 📋 Planned | | |
| C3 | 📋 Planned | | |
| C4 | 📋 Planned | | |
| C5 | 📋 Planned | | |
| C6 | 📋 Planned | | |
| C7 | 📋 Planned | | |
| M1 | 📋 Planned | | |
| M3 | 📋 Planned | | |
| M7 | 📋 Planned | | |
| M8 | 📋 Planned | | |
| I1 | 📋 Planned | | |
| I4 | 📋 Planned | | |
| M2 | 📋 Planned | | |
| M4 | 📋 Planned | | |
| M5 | 📋 Planned | | |
| M6 | 📋 Planned | | |
| m3 | 📋 Planned | | |

---

## Notes for Implementer

1. **Start with C7 → C1** — fixes the foundation (DB path, tool registration on resume)
2. **Then C5 + I1 + I4** — fixes the UI integration (agent reuse, session resume, AI wiring)
3. **Then C2, C3, C6, M8** — core model fixes
4. **Then M1, M3, M7** — robustness
5. **Run full test suite after each group** — `uv run pytest tests/features/feature_007... -v`
6. **Run MVC check after any controller/interface changes** — `uv run scripts/omt/mvc_check.py src/agentx/agent/`

---

**Next Step:** Declare OMT++ phase for bug_fix task type and begin implementation.