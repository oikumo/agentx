# WORK

> Single‑developer + coding‑agent roadmap.  
> Machine‑parseable, minimal friction, git‑friendly.

---

## Convention

| Symbol | Meaning |
|--------|---------|
| `[ ]`  | Pending |
| `[~]`  | In progress (agent working on it) |
| `[x]`  | Done |
| `[!]`  | Blocked / needs decision |

**Hierarchy** – top‑level task → optional subtasks (indented 4 spaces).  
**Metadata** – optional inline comment: `<!-- id:T‑123 prio:medium agent:true -->`  
**Thoughts** – separate `---` line then bullet list; tools can strip it.

---

## Tasks

- [x] Implement feature_007.agentx_intelligent_agent_behaviour
  - [x] Full OMT++ cycle: Analysis (8 artifacts) → Design (framework, tools, policy DSL, reflection) → Implementation (model, controllers, views, persistence, integrations) → Testing (132 tests, 0 regressions); user validated

- [x] Fix feature_007 bugs per BUG_FIX_PLAN.md <!-- id:T-007-bugfix prio:high agent:true -->
  - [x] Independent review (39 files); all P0–P3 bugs fixed across 9 groups; 32 regression tests; 169/169 feature_007 pass; full suite 434/435; MVC++ 0/0

- [x] Implement feature_004.modern_ui <!-- id:T-004 prio:high agent:true -->
  - [x] TUI infrastructure, MainTUIScreen, main.py integration, e2e tests; 4 rounds of TUI fixes (navigation, chat conversation, RAG freeze); user accepted; FEATURE.md written

- [x] Update README.md with feature_006 and agentic workflow <!-- id:T-006-readme prio:med agent:true -->
- [x] Update application design overview in `.meta/.../4.design/` <!-- id:T-006-design prio:med agent:true -->

- [ ] Implement feature_001.session_user_objectives_driven_by_Petri_Net <!-- id:T-001-prio-high agent:false -->
  - [ ] Define scope & success criteria

- [x] Implement feature_006.opencode_process_enforcement <!-- id:T-006-prio-high agent:true -->
  - [x] MVC++ linter, feature scaffolder, live permissions, process gate plugin, AGENTS.md; phase exit validation, omt_status/omt_complete tools, e2e harness guard; user accepted

- [ ] Implement feature_002.rag_retrieval_augmented_generation <!-- id:T-002-prio-med agent:false -->
  - [ ] Scaffold design doc

- [x] Implement feature_010.agent_demo_screen <!-- id:T-010-prio-med agent:true -->
  - [x] Design, model (scenarios A+B), controller, view (AgentDemoScreen), 34 tests; full suite 468/469; MVC++ 0/6

- [x] Implement feature_011.fast_agent <!-- id:T-011-prio-high agent:true -->
  - [x] Design (design_001 + operation_spec_001), Implementation (3 new View files + 4 edited files), Testing (44 tests, 0 regressions); MVC++ 0/6; full suite 512/513 (1 pre-existing)

---

## Agent Scratchpad (auto‑managed, do not edit manually)

```
[2026-06-27T18:26] Agent: Completed feature_004 navigation fixes, all tests pass.
[2026-06-27T18:30] Agent: Next action - write FEATURE.md for feature_004.
[2026-06-27T19:15] Agent: Fixed TUI RAG screen freeze on Select button - replaced blocking console input with TUI screens.
[2026-06-28] Agent: Moved feature_003 content to feature_007 (scaffolded via new_feature.py); Analysis phase started
[2026-06-29] Agent: Completed all 8 Analysis artifacts for feature_007 (use cases, class diagrams, sequence diagrams, state diagrams, data dictionary, NFRs, traceability, architecture summary); Usability validated with User; Ready for Design phase
[2026-06-29] Agent: Updated WORK.md with detailed sub-tasks per PLAN.md; Creating Design phase scaffold and design_001_agent_framework.md
[2026-06-29] Agent: Architecture decision — persistence uses stdlib sqlite3 only (no SQLAlchemy, no Alembic); updated PLAN.md, design_001 (§5.1/5.2/5.3/9/10/11.2/13/15), analysis_001, analysis_007, and WORK.md to match existing SessionDatabase/RagDatabase convention.
[2026-06-29] Agent: Completed Design D6/D7/D8 — expanded design_001 §6 (ToolSpec, ToolRegistry, discovery, built-in tools), §7 (priority resolution, conflict detection, adaptation hooks), §8 (critique parser, safety evaluator, proposal routing); aligned interfaces with class diagram & data dictionary; corrected TOOL_CONFIG→TOOL_CONFIGURATION.
[2026-06-29] Agent: Fixed META HARNESS bug — omt_enforcer.ts checkPhaseExitArtifacts + omt_status.ts getArtifactStatus resolved feature dirs as short "feature_NNN" but new_feature.py scaffolds full-slug dirs (feature_007.agentx_intelligent_agent_behaviour), causing false-negative artifact detection. Added resolveFeatureDir() (exact + prefix match) to both. Harness e2e test passes (receipt refreshed); both plugins load OK via node --experimental-strip-types. Also created operation_spec_001_agent_operations.md (Design deliverable, guide §10). NOTE: advancing Design→Programming via omt_complete is blocked until opencode restarts so the plugin fix reloads.
[2026-06-29] Agent: Verified OMT harness after restart — omt_status works (no p.split error), plugin fix loaded. Advanced feature_007 Design→Programming via omt_complete. Implemented full agent framework (I1-I13): types.py (38 enums+dataclasses), interfaces.py (8 Abstract Partners), persistence (schema_db/agent_db/repositories_db — stdlib sqlite3), tool registry (ToolRegistry + ISensor/IActuator + 3 built-in tools), policy engine (condition DSL parser+AST+evaluator+conflict resolver), reflection engine (critique parser+safety evaluator+proposal router), Agent facade (perceive/decide/act/reflect/persist), 3 controllers, console+TUI views, AgentAdapter (feature_004 integration). MVC check: 0 errors, 0 warnings on src/agentx/agent/. Full cycle test passed (goal+policy→decide→act→reflect→persist). impl_notes.md written. Ready for Testing phase.
[2026-06-29] Agent: Testing phase complete (T1-T6). Wrote 132 tests across 11 test files: unit tests (types, tool registry, memory, goals, policy DSL, reflection, persistence), integration tests (agent facade cycle, controllers, multi-cycle), MVC++ compliance tests (mvc_check.py, ABC check, loc check, view/model isolation), TUI e2e tests (Textual pilot). All 132 pass. Zero regressions on existing 262 tests (1 pre-existing failure in test_chat_rag_screens.py unrelated to feature_007). Moved agent_adapter.py from view/tui/ to top-level agent/ to fix view-imports-model MVC++ violation. test_report.md written.
[2026-06-29] Agent: Fixed AI service wiring — created AIServiceAdapter implementing IAIServicePartner, wired into MainController.show_agent(), improved ReflectionEngine to show clear "AI service unavailable" message when API keys missing. All 137 feature_007 tests pass, full suite 372/373 pass (1 pre-existing failure), MVC++ 0 errors / 6 warnings. Feature complete and validated.
[2026-07-04] Agent: Independent review of feature_007 (39 files). Verified 17/18 original bugs (M4 false-positive, C7 downgraded). Found 9 NEW bugs (N1 volatile-memory loss on resume, N2 double correlation_id, N3 dead _pol_repo, N4 inert self-improvement loop, N5 tool-disable no-op, N6 View→Model leaks, N7 config not restored, N8 goal-root drift, N9 no state-clear on resume). Updated BUG_FIX_PLAN.md.
[2026-07-04] Agent: Implemented all P0/P1 bug fixes (Groups 1-9). resume_session() now restores tools+volatile memory+config+goal root+reflection log and clears stale state (N1/N7/N8/N9/M2/C1/C3). run_cycle uses a single command (N2); goal completion scoped via SuccessCriteria.tool_id (C6). reflect() returns ReflectionEntry (C2); load_snapshot on facade (C4); SessionTool calls resume_session (M8). perceive() surfaces failed readings (M1); reflection skipped w/o AI (N11); safety deny-list expanded (M7); un-routed proposals visible (M3). Tool enablement enforced in perceive+execute (N5/M6). PolicyEngine now repo-based like GoalManager (N3). AgentAdapter owns AI wiring + resume (C5/I1/I4). Approval flow closes the reflection loop: pending_proposals/approve_proposal + TUI proposals/approve commands (N4). Controller partner methods replace get_agent() reach-through (N6). Added 21 regression tests. 158/158 feature_007 pass, full suite 423/424 (1 pre-existing), MVC++ 0/0.
[2026-07-04] Agent: Completed ALL remaining P2/P3 fixes. M5 (compare TypeError logged), N12 (RagSensorTool now a hybrid actuator — EXECUTE_TOOL rag_query retrieves knowledge), m1 (empty tool_id dropped), m2 (context_memory_limit config), m4 (dead limit clause removed), m5 (greedy regex for nested JSON), m7 (IPersistencePartner.load_snapshot return type), m9 (adapter runtime isinstance check), m10 (filesystem MAX_FILES=2000 cap), C7* (persistent_path canonicalized), N13 (ReflectionEngine.set_ai_service public API), N14 (list_tools/register_tool/etc. on facade; ToolController no longer reaches into tool_registry), N15 (conflict overlap on identifiers only), N16 (perception keys joined cleanly in prompt). 32 regression tests total. 169/169 feature_007 pass, full suite 434/435 (1 pre-existing), MVC++ 0/0. ALL bugs in BUG_FIX_PLAN.md resolved (only M4 dropped as false positive).
[2026-07-04] Agent: Implemented feature_011.fast_agent — a new "⚡ Fast Agent" main-menu option (f key) that drives the existing feature_007 Agent via a stack of Textual ModalScreen dialogs (Goal → Running → Reflection → Result). First ModalScreen use in codebase. 3 new View files (fast_agent_screen.py, fast_agent_modals.py, fast_agent_view.py), 4 edited files (agent_controller.py +get_cycle_summary, adapter.py +create_fast, main_controller.py +show_fast_agent, main_screen.py +f binding +5th button +grid 3x2 +relabel Advanced Agent). No Model-layer changes. 44 new tests + 5 updated existing tests. 512/513 full suite (1 pre-existing), MVC++ 0/6.
```
