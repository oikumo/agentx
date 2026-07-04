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
  - [x] Complete the feature description with the User revision
  - [x] Create the feature implementation plan
  - [x] Validate the feature technical feasibility, fix the feature and it is plan if needed
  - [x] Validate the feature end User usability, fix the feature and it is plan if needed
  - [x] Analysis phase complete (8 artifacts)
    - [x] A1: Use case diagram + specifications (analysis_002_use_cases.md)
    - [x] A2: Class diagram (analysis_003_class_diagram.md)
    - [x] A3: Sequence diagrams (analysis_004_sequence_diagrams.md)
    - [x] A4: State diagrams (analysis_005_state_diagram.md)
    - [x] A5: Data dictionary (analysis_006_data_dictionary.md)
    - [x] A6: Non-functional requirements (analysis_007_nfrs.md)
    - [x] A7: Traceability matrix (analysis_008_traceability.md)
    - [x] A8: Analysis summary (analysis_001_agent_architecture.md)
  - [x] Design phase (major_feature requires design doc)
    - [x] D1: Scaffold design_001_agent_framework.md via new_feature.py
    - [x] D2: MVC++ component diagram for agent subsystem
    - [x] D3: Abstract Partner interfaces (IAgentViewPartner, IAgentModelPartner, IToolRegistryPartner, IMemoryStorePartner, IPolicyStorePartner, IGoalManager)
    - [x] D4: Data models (Pydantic/dataclasses) from Data Dictionary
    - [x] D5: Persistence schema
      - [x] In-memory data models defined (Pydantic/dataclasses)
      - [x] sqlite3 DDL schema defined (Table* classes, idempotent CREATE TABLE IF NOT EXISTS)
      - [x] SessionDatabase design (stdlib sqlite3, no ORM/migrations) — code in I7
      - [x] Schema validation approach defined — tests in T-phase
    - [x] D6: Tool registry protocol
      - [x] ISensor/IActuator interfaces defined
      - [x] ToolSpec schema formalized
      - [x] Registry implementation
      - [x] Discovery mechanism
      - [x] Built-in tool implementations
    - [x] D7: Policy engine DSL
      - [x] Rule syntax specification
      - [x] Condition DSL design
      - [x] Evaluator implementation
      - [x] Priority resolution
      - [x] Conflict detection
    - [x] D8: Reflection engine
      - [x] Prompt templates designed
      - [x] Proposal types defined
      - [x] Critique parser implementation
      - [x] Safety evaluation hook
      - [x] Proposal routing
      - [x] D9: MVC++ compliance checklist for agent module
      - [x] D10: Design summary document
      - [x] Declare omt_phase Design with design doc path
      - [x] Declare omt_phase Design with design doc path
    - [~] Implementation phase
        - [x] I1: Scaffold feature_007 implementation directory
        - [x] I2: Model layer (src/agentx/agent/model/) — Agent, MemoryManager, PolicyEngine, GoalManager, ReflectionEngine
        - [x] I3: Abstract Partners (src/agentx/agent/interfaces.py) — IAgentViewPartner, IMemoryStorePartner, IPolicyStorePartner, IToolRegistryPartner, IGoalManager, ISafetyEvaluator, IAIServicePartner, IPersistencePartner
        - [x] I4: Controller layer (src/agentx/agent/controller/) — AgentController, SessionController, ToolController
        - [x] I5: View layer (src/agentx/agent/view/) — AgentView (console), AgentTUIScreen (Textual), AgentAdapter
        - [x] I6: Tool Registry (src/agentx/agent/model/tools/) — ToolRegistry, ISensor/IActuator, ToolSpec, discovery, built-in tools (FileSystemTool, RagSensorTool, SessionTool)
        - [x] I7: Persistence (src/agentx/agent/persistence/) — stdlib sqlite3 backend (schema_db.py DDL + agent_db.py + repositories_db.py), MemoryRepository, PolicyRepository, GoalRepository, ReflectionRepository — no ORM, no Alembic
        - [x] I8: Policy Engine implementation — condition DSL parser (tokenizer+AST+visitor), evaluation loop, priority resolution, conflict detection, adaptation hooks
        - [x] I9: Reflection Engine implementation — critique parser, safety evaluator, proposal router, reflection engine
        - [x] I10: Integrate with feature_004 (Modern UI) — AgentAdapter, AgentTUIScreen
        - [x] I11: Integrate with feature_001 (Session Objectives) — IGoalManager stub, swap when 001 ready
        - [x] I12: Integrate with feature_002 (RAG) — RagSensorTool wrapping Rag.query()
        - [x] I13: Implementation notes (impl_notes.md)
        - [x] Run mvc_check.py after each component — 0 errors, 0 warnings on src/agentx/agent/
    - [x] Testing phase
        - [x] T1: Unit tests (132 tests — types, tool registry, memory, goals, policy DSL, reflection, persistence)
        - [x] T2: Integration tests (agent facade cycle, controllers, session persistence, multi-cycle)
        - [x] T3: MVC++ compliance tests (mvc_check.py 0 errors/0 warnings, ABC check, loc check, view/model isolation)
        - [x] T4: E2E tests (Textual pilot — mount, run cycle, save, show message)
        - [x] T5: Performance tests (qualitative — cycle <100ms, policy eval instant, persistence <50ms)
        - [x] T6: Test report (test_report.md — 132/132 pass, 0 regressions)
    - [x] User validate the feature implementation

- [x] Fix feature_007 bugs per BUG_FIX_PLAN.md (review + implementation) <!-- id:T-007-bugfix prio:high agent:true -->
    - [x] Independent source review of src/agentx/agent/ (39 files) + UI integration
    - [x] Update BUG_FIX_PLAN.md with verification table + 9 new bugs (N1-N16)
    - [x] Group 1: Complete resume_session() — N9 clear state, N1 volatile memory, C1 tools, C3 AI service, N7 config, N8 goal root, M2 reflection log
    - [x] Group 2: Cycle correctness — N2 single correlation_id, C6 scoped goal completion (SuccessCriteria.tool_id)
    - [x] Group 3: Model API — C2 reflect()→ReflectionEntry, C4 load_snapshot on facade, M8 SessionTool.resume_session
    - [x] Group 4: Robustness — M1 failed-reading, M3 un-routed proposals visible, M7 expanded deny-list, N11 skip reflection w/o AI
    - [x] Group 5: Tool enablement — N5 disable effective (perceive+execute), M6 public set_tool_enabled/is_enabled
    - [x] Group 6: Persistence unification — N3 PolicyEngine repo-based (mirrors GoalManager)
    - [x] Group 7: UI integration — C5 reuse+resume, I1 adapter resume, I4 AI wiring in adapter
    - [x] Group 8: Reflection loop closure — N4 approval flow (pending_proposals/approve_proposal + TUI proposals/approve commands)
    - [x] Group 9: MVC++ hygiene — N6 controller partner methods, removed get_agent() reach-through
    - [x] 21 regression tests (test_bug_fixes.py) — all pass
    - [x] 158/158 feature_007 tests pass; full suite 423/424 (1 pre-existing failure); MVC++ 0/0
    - [x] P2/P3 completion: M5 (compare TypeError log), N12 (RAG actuator query), m1 (tool_id validate), m2 (context_memory_limit), m4 (dead limit clause), m5 (nested JSON regex), m7 (load_snapshot return type), m9 (adapter isinstance), m10 (filesystem MAX_FILES cap), C7* (path canonicalize), N13 (set_ai_service public), N14 (list_tools facade + ToolController hygiene), N15 (conflict overlap identifier-only), N16 (prompt formatting)
    - [x] 32 regression tests total; 169/169 feature_007 pass; full suite 434/435 (1 pre-existing); MVC++ 0/0 — ALL bugs fixed

- [x] Implement feature_004.modern_ui <!-- id:T-004 prio:high agent:true -->
    - [x] Infrastructure complete (TUI module, providers, adapters)
    - [x] MainTUIScreen implemented with all widgets
    - [x] Integration with main.py complete
    - [x] Create tui automated end to end tests using pilot in `test_automated/tui/`
    - [x] TUI Bug Fixes – Architecture Rewiring (2025-06-27)
        - [x] Fixed MainTUIScreen to delegate navigation to controller
        - [x] Updated IMainViewPartner interface with `show_chat()` and `show_rag()` abstract methods
        - [x] Updated ChatController to accept view in constructor (for TUI/Console swapping)
        - [x] Updated RagController to accept view in constructor (for TUI/Console swapping)
        - [x] Updated RagView to implement `IRagView` interface
        - [x] Updated `IChatViewPartner` and `IRagViewPartner` with full abstract method signatures
        - [x] Implemented `TUIChatAdapter.show()` to run Textual chat screen
        - [x] Implemented `TUIRagAdapter.show()` to run Textual RAG screen
        - [x] Updated `ChatTUIScreen` to work with `IChatViewPartner` controller
        - [x] Updated `RagTUIScreen` to work with `IRagViewPartner` controller
    - [x] Remaining TUI Navigation Fix (2026-06-27)
        - [x] Fix automated e2e tests – MainTUIScreen now pushes screens directly AND calls controller
        - [x] Solution: Option 2 – MainTUIScreen pushes screens directly for navigation while also calling controller.show_chat()/show_rag() for side effects (recording, logging)
        - [x] All navigation tests pass: `test_key_c_opens_chat`, `test_key_r_opens_rag`, `test_escape_returns_from_chat`, `test_chat_button_opens_chat`
    - [x] Verify end-to-end TUI navigation (Main → Chat → RAG)
    - [x] **TUI Chat Conversation Fix (2026-06-27)**
        - [x] Root cause: MainController.show_chat() created console ChatView blocking TUI event loop
        - [x] Fix: MainController now uses provider to create TUIChatAdapter; ChatTUIScreen implements IChatView
        - [x] ChatTUIScreen now has show_partial_message(), show_message(), show_stream_message() for streaming
        - [x] TUIChatAdapter delegates to ChatTUIScreen via set_screen() connection
        - [x] All navigation + chat conversation e2e tests pass
    - [x] **TUI RAG Screen Freeze Fix (2026-06-27)**
        - [x] Root cause: RagController.select_repository() used blocking console input loop (RagRepositorySelectionView.show())
        - [x] Fix: RagTUIScreen._select_repository() now always uses TUI RepositorySelectionScreen (non-blocking)
        - [x] Also fixed _create_repository() and _ingest_documents() to use TUI screens
        - [x] Updated legacy unit tests in tests/tui/ to match new TUI screen delegation behavior
        - [x] All 23 automated TUI e2e tests pass including rag_screen_repository_selection_and_chat
    - [x] Verify User acceptance test
    - [x] Write `FEATURE.md` summary in `.meta/.../feature_004.modern_ui/`
- [x] Update README.md with feature_006 and agentic workflow description <!-- id:T-006-readme prio:med agent:true -->
- [x] Update application design overview in `.meta/software_development_process/4.design/` <!-- id:T-006-design prio:med agent:true -->
    - [x] Update application design structure documentation
    - [x] Update application design behavior documentation
- [ ] Implement feature_001.session_user_objectives_driven_by_Petri_Net <!-- id:T-001-prio-high agent:false -->
    - [ ] Define scope & success criteria
- [x] Implement feature_006.opencode_process_enforcement <!-- id:T-006-prio-high agent:true -->
    - [x] Plan → `.meta/.../feature_006.opencode_process_enforcement/plan/PLAN.md`
    - [x] MVC++ linter → `scripts/omt/mvc_check.py`
    - [x] Feature scaffolder + templates → `scripts/omt/new_feature.py`, `.meta/templates/`
    - [x] Live permissions → `opencode.jsonc`
    - [x] Process gate plugin → `.opencode/plugin/omt_enforcer.ts`
    - [x] AGENTS.md rewritten to match real enforcement
    - [x] Step 0 spike: opencode plugin API confirmed
    - [x] Tuning: agent self‑skip (logged); hard‑errors block / soft warn
    - [x] Harden: auto‑detect feature design artifact from slug
    - [x] Dogfood one bug_fix + one feature through the gate
    - [x] Fix 2 legacy MVC++ errors so the gate guards a clean baseline
    - [x] Phase exit validation (P0) — enforce artifacts on phase transition <!-- id:T-006-phase-exit prio:high agent:true -->
        - [x] PHASE_EXIT_REQUIREMENTS mapping per guide §12
        - [x] checkPhaseExitArtifacts() function with feature-scoped paths
        - [x] Integration in omt_phase.execute() — blocks invalid transitions
        - [x] Fixed: Unit tests scoped to tests/features/<feature>/
        - [x] Fixed: Operation specs detection (operation_spec_*.md pattern)
        - [x] Added: omt_complete tool for phase completion verification
        - [x] Added: WORK.md auto-sync hook on phase completion
      - [x] Verify User acceptance test
        - [x] Source fix: make `omt_status.ts` a standalone plugin and remove dynamic status import from `omt_enforcer.ts`
        - [x] Source fix: repair `omt_complete` feature-phase lookup and phase transition constants
        - [x] Source fix: repair phase-exit artifact validation (`REPO_ROOT` → plugin `directory`)
        - [x] Source fix: keep `omt_complete` artifact checks scoped to feature-sized work (`major_feature` / `new_screen`), not bug-fix dogfood phases
        - [x] Source fix: align `omt_status` with strict `design_*.md` detection and no required artifacts for lightweight task types
        - [x] Source verification: `uv run pytest tests/scripts/omt/test_mvc_check.py -q` → 25 passed
        - [x] Source verification: `uv run scripts/omt/mvc_check.py --json` → 0 errors, 6 existing warnings
        - [x] Restart opencode so plugin changes are reloaded
        - [x] After restart, run `omt_status` and confirm it returns a status summary instead of `p.split` error
        - [x] After restart, run `omt_phase` then `omt_complete` for `feature_006.opencode_process_enforcement` and confirm completion/advance works
        - [x] If live tool smoke tests pass, mark this acceptance test complete
    - [x] OMT harness comprehensive e2e guard (2026-06-28)
        - [x] Added `tests/scripts/omt/test_omt_harness_e2e.py`
        - [x] Added `.meta/.omt/omt_harness_e2e_last_run.json` runtime receipt on passing e2e run
        - [x] Enforced fresh e2e receipt before repeated edits to OMT/META harness files
- [ ] Implement feature_002.rag_retrieval_augmented_generation <!-- id:T-002-prio-med agent:false -->
    - [ ] Scaffold design doc
- [x] Implement feature_010.agent_demo_screen <!-- id:T-010-prio-med agent:true -->
    - [x] Design phase (new_screen): design_001_agent_demo_screen.md + operation_spec_001_agent_demo.md
    - [x] Model: demo/scenarios.py (DemoScenario A+B + seed_sandbox_files); GoalManager.clear(), MemoryManager.clear_volatile(), Agent.clear_state()
    - [x] Controller: AgentController.reset_state(), load_demo_scenario_by_name(), get_demo_scenario_info()
    - [x] View: AgentDemoScreen (Run/Reset/Back buttons + live cycle log); AgentTUIScreen 'd' key + 'demo [a|b]' command
    - [x] Bug fix (feature_007): tools read command.action (was command.parameters) — unblocked EXECUTE_TOOL create/query/update at runtime
    - [x] Testing: 34 tests (scenarios, clear ops, controller, Textual pilot) — all pass; 169/169 feature_007 pass; full suite 468/469 (1 pre-existing); MVC++ 0/6

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
```
