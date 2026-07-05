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

- [x] Implement feature_012.tui_framework <!-- id:T-012-prio-high agent:true -->
  - [x] Major feature: reusable TUI base-class library (ui/tui/framework/: base screen, modal, app, adapter, navigation mixin, widgets, register_partner) + refactor 9 existing screens/adapters to inherit from it; 62 framework tests; full suite 578/579 (1 pre-existing); MVC++ 0/6; fast-agent freeze-fix preserved

- [x] Implement feature_010.agent_demo_screen <!-- id:T-010-prio-med agent:true -->
  - [x] Design, model (scenarios A+B), controller, view (AgentDemoScreen), 34 tests; full suite 468/469; MVC++ 0/6

- [x] Implement feature_011.fast_agent <!-- id:T-011-prio-high agent:true -->
  - [x] Design (design_001 + operation_spec_001), Implementation (3 new View files + 4 edited files), Testing (44 tests, 0 regressions); MVC++ 0/6; full suite 512/513 (1 pre-existing)

- [x] Implement feature_013.ai_model_provider_selector <!-- id:T-013-prio-med agent:true -->
  - [x] New_screen: Models module on Main screen (m key / 🎛️ Models button) to select the current AI model provider; ModelRegistry (catalog + JSON-persisted selection + factory) unifies OpenRouter/OpenAI/Gemini/Ollama/LlamaCpp under LLMProvider; AIService.get_current_llm() delegates to registry; 4 hardcoded openrouter call sites refactored (chat, rag-chat, rag, agent ai_adapter w/ legacy fallback preserved); ModelsController + IModelsViewPartner(ABC) + ModelsTUIScreen(BaseAgentXScreen, OptionList); 56 feature tests + 5 refactor-driven test updates + 1 new binding test; full suite 635/636 (1 pre-existing); MVC++ 0/6 (baseline)

- [x] Fix feature_011.fast_agent UI freeze <!-- id:T-011-freeze prio:high agent:true -->
  - [x] **Root cause**: Two bugs — (1) `RunningModal.__init__` set `self._running = True`, shadowing Textual's `DOMNode._running` attribute; this made `push_screen` skip `_register` → screen's message pump never started → `on_mount` never fired → worker never started → screen dead. (2) The original `_tick()` ran `run_cycle()` synchronously on the UI thread, blocking on `llm.invoke()`.
  - [x] **Fix**: Renamed `_running` → `_auto_running` (avoids Textual attribute collision); rewrote `RunningModal` to run `run_cycle()` on a daemon worker thread, communicating via `queue.Queue` + `threading.Event` (stop/pause); UI thread polls the queue via `set_timer(0.05, _poll)` — never blocks on LLM calls. `_dismissed` flag guards double-dismiss. Reflection proposals pause the worker via `_pause_evt` and resume on `_on_reflection`.
  - [x] **Regression tests**: 4 new tests in `TestRunningModalFreezeFix` — `test_run_cycle_runs_off_ui_thread`, `test_event_loop_responsive_during_blocking_cycle`, `test_stop_works_while_cycle_blocks`, `test_pause_resumes_after_blocking_cycle`. All use `_pump_until` (asyncio.sleep yields) instead of `pilot.pause()` (which times out on the recurring poll timer).
  - [x] **Results**: 48/48 feature_011 pass; full suite 516/517 (1 pre-existing); MVC++ 0/0

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
[2026-07-05] Agent: Fixed feature_011.fast_agent UI freeze. Found TWO root causes: (1) RunningModal.__init__ set self._running=True, shadowing Textual's DOMNode._running — push_screen's _get_screen saw is_running=True, skipped _register, the screen's message pump never started, on_mount never fired, worker never started. Renamed to _auto_running. (2) The original _tick() ran run_cycle() synchronously on the UI thread, blocking on llm.invoke(). Rewrote RunningModal to use a daemon worker thread + queue.Queue + threading.Event for stop/pause; UI thread polls via set_timer(0.05, _poll). 4 regression tests (TestRunningModalFreezeFix): off-thread execution, event-loop responsiveness during block, Stop-during-block, pause/resume. 48/48 feature_011 pass; 516/517 full suite (1 pre-existing); MVC++ 0/0.
[2026-07-05] Agent: Implemented feature_012.tui_framework — a reusable TUI base-class library at src/agentx/ui/tui/framework/ (partner.py register_partner; base_screen.py BaseAgentXScreen + NavigationMixin; base_modal.py BaseAgentXModalScreen; base_app.py BaseAgentXApp; base_adapter.py BaseScreenAdapter; widgets.py 5 extracted widgets; __init__.py). Refactored 9 existing TUI screens/adapters + app to inherit: MainTUIScreen/ChatTUIScreen/RagTUIScreen/AgentTUIScreen/AgentDemoScreen/FastAgentTUIScreen → BaseAgentXScreen; 4 fast-agent modals → BaseAgentXModalScreen; TUIApplication → BaseAgentXApp; 3 adapters → BaseScreenAdapter; MainTUIScreen 4 navigation methods → navigate_to_child (≈240→40 LOC); _log → safe_log; IAgentViewPartner.register → register_partner. Key design correction: BaseAgentXModalScreen(BaseAgentXScreen, ModalScreen[T]) ordering so super().__init__(controller) chains (design doc's ModalScreen-first ordering was wrong). _controller typed Any (duck-typed convention). Main adapter is app-delegating (overrides __init__+show). RunningModal worker/queue/poll loop UNCHANGED (freeze-fix preserved). 2 refactor-driven test updates (logged omt_skip{scope:tests}): feature_011 mvc test repointed main_screen.py→framework/widgets.py for MenuGrid source; bug-repro test RAG/Chat assertion made case-insensitive for navigate_to_child's screen_cls.__name__ error message. 62 new framework tests (base/nav/mvc+regression). Full suite 578/579 (1 pre-existing test_llm_initialization_attempted); MVC++ 0 errors/6 warnings (baseline, all pre-existing); framework 0/0.
[2026-07-05] Agent: Implemented feature_013.ai_model_provider_selector — a "Models" module on the Main screen (m key / 🎛️ Models button) that lets the user select the current AI model provider. Model layer: new model/ai/model_registry.py (ProviderInfo dataclass + ModelRegistry: 5-provider catalog, current selection, JSON persistence at ~/.agentx/model_selection.json best-effort, create_current_llm factory; default_registry singleton; config_path injectable for tests). Unified the ad-hoc Ollama class and get_remote_llm_google_gemini() fn under the LLMProvider ABC as OllamaProvider + GeminiProvider (lazy imports). AIService gains get_current_llm()/get_current_provider_info()/get_registry() delegating to the registry; legacy openrouter/cloud/local factories kept for backward-compat. Refactored the 4 hardcoded AIService().openrouter_llm_provider().create_llm() call sites → get_current_llm(): chat_controller, rag_chat_controller, rag.py. agent/ai_adapter._ensure_llm now tries the user-selected provider FIRST, then the legacy OpenRouter→OpenAI fallback chain (preserves graceful degradation the reflection engine relied on). Controller: new ui/screens/models/models_controller.py (IModelsViewPartner ABC + ModelsController). View: new ui/tui/screens/models_screen.py (ModelsTUIScreen extends BaseAgentXScreen; OptionList of providers, ● marks current, Enter selects, Esc/b back; pure View — no agentx.model import). Main wiring: MainController.show_models() (idempotent C5 pattern) + get_models_controller(); MainTUIScreen m binding + action_open_models (navigate_to_child) + button handler + help text; MenuGrid 6th button 🎛️ Models (btn-models). Persistence = JSON not sqlite (selection is one scalar, not entity CRUD — proportionate per guide §1). 56 new feature tests (25 unit model_registry + 18 integration controller/callsites/pilot + 13 mvc compliance) + 5 refactor-driven test updates (menu grid 5→6 buttons, bindings 7→8, button ids/variants) + 1 new test_binding_m_models; tests unlocked via logged omt_skip{scope:tests}. Full suite 635/636 (1 pre-existing test_llm_initialization_attempted — chat_screen.py NOT touched, unrelated); MVC++ 0 errors/6 warnings (baseline, all pre-existing); feature_013 0/0. Full OMT++ cycle: Analysis (use_case_001 + analysis_001) → Design (design_001 + operation_spec_001, mermaid class/flow/sequence diagrams) → Programming → Testing → Done.
```
