# features.md — Feature Catalog (compressed)

**SCOPE:** Every feature — status, summary, code + artifact locations. Status: ✅ done · 🔨 in progress · ⏳ pending · 🅿️ placeholder

| # | Feature | Status | Summary |
|---|---------|--------|---------|
| 001 | session_user_objectives_driven_by_Petri_Net | ⏳ | Petri-net-driven session objectives (will swap into agent's `IGoalManager`) |
| 002 | rag_retrieval_augmented_generation | ⏳ | RAG retrieval + generation (partially implemented; needs design scaffold) |
| 004 | modern_ui | ✅ | Textual TUI with full screen navigation (Main/Chat/RAG) |
| 005 | agentx_file_system_agentic_tools | ✅ | Agentic filesystem tools (folded into feature_007's tool registry) |
| 006 | opencode_process_enforcement | ✅ | OMT++ process gate: `mvc_check.py`, `new_feature.py`, `omt_enforcer.ts` |
| 007 | agentx_intelligent_agent_behaviour | ✅ | Intelligent agent: goals, policy DSL, memory, reflection, tools |
| 010 | agent_demo_screen | ✅ | One-trigger demo screen showcasing agent cycle (scenarios A/B) |
| 011 | fast_agent | ✅ | Modal-dialog-driven agent UX (Goal → Running → Reflection → Result) |

> `feature_008.agent_framework` and `feature_009.feature_007_agentx_intelligent_agent_behaviour` = empty placeholder dirs (only `FEATURE.md` + `plan/`).

---

## feature_001 — Session Objectives (Petri Net) ⏳
**Goal:** Drive session objectives through Petri-net model. Provides concrete `IGoalManager` impl replacing current stub (`agent/model/goal/manager.py`). Agent facade depends on `IGoalManager` abstraction → swaps at runtime.
- **Status:** Scope & success criteria not yet defined (`WORK.md`).
- **Integration point:** `agent/model/goal/manager.py` → `IGoalManager`.

## feature_002 — RAG (Retrieval Augmented Generation) ⏳
**Goal:** Ingest documents (web + local) into vector store, answer questions with retrieval-augmented LLM responses. `Rag` orchestrator and `RagQuery` pipeline exist and wired into RAG screen; needs design scaffold.
- **Status:** Partially implemented (see subsystems.md §RAG); design doc pending.
- **Key code:** `src/agentx/model/rag/`.

## feature_004 — Modern UI ✅
**Goal:** Rich Textual TUI replacing legacy console-only flow, with full screen navigation (Main → Chat → RAG → Agent), streaming chat, non-blocking RAG repository selection.
- **Key code:** `src/agentx/ui/tui/` (app, screens, adapters, provider).
- **Highlights:** `MainTUIScreen` pushes sub-screens directly AND calls `controller.show_*()` for wiring (dual-path fix for navigation freezes); `TUIChatAdapter` streams chunks into single growing widget; RAG screens use TUI modal screens instead of blocking console input.
- **Artifacts:** `.meta/.../features/feature_004.modern_ui/`.

## feature_005 — Agentic File System Tools ✅
**Goal:** Agentic filesystem tools. Folded into feature_007's tool registry as `FileSystemTool` (hybrid sensor/actuator).
- **Key code:** `src/agentx/agent/model/tools/filesystem_tool.py`.

## feature_006 — Opencode Process Enforcement ✅
**Goal:** Mechanically enforce OMT++ methodology via opencode. Provides MVC++ linter, feature scaffolder, live permissions, process gate plugin with phase-exit validation.
- **Key code:** `scripts/omt/mvc_check.py`, `scripts/omt/new_feature.py`, `.opencode/plugin/omt_enforcer.ts`, `.opencode/plugin/omt_status.ts`, `opencode.jsonc`.
- **Artifacts:** `.meta/.../features/feature_006.opencode_process_enforcement/`.

## feature_007 — Intelligent Agent Behaviour ✅
**Goal:** Complete intelligent-agent subsystem running perceive → decide → act → reflect cycle driven by goals, policy condition DSL, tool registry, volatile/persistent memory, reflection engine with self-improvement proposals.
- **Key code:** `src/agentx/agent/` (model, controller, view, persistence, interfaces, types).
- **Subsystems:** Agent facade, GoalManager, PolicyEngine (condition DSL + conflict resolver), MemoryManager, ReflectionEngine (critique parser + safety evaluator + proposal router), ToolRegistry (FileSystemTool, RagSensorTool, SessionTool), `agent_session.db`.
- **Bug-fix pass:** All bugs in `BUG_FIX_PLAN.md` resolved (P0–P3); 169 tests pass; MVC++ 0/0.
- **Artifacts:** `.meta/.../features/feature_007.agentx_intelligent_agent_behaviour/` (8 analysis docs + design + operation specs + impl notes + test report).

## feature_010 — Agent Demo Screen ✅
**Goal:** Dedicated Textual screen demonstrating feature_007 with one trigger. From Agent screen, press `d` (or type `demo [a|b]`) — seeds goal + rules + sandbox file, auto-runs cycle, offers Run/Reset/Back buttons.
- **Key code:** `src/agentx/agent/view/tui/demo_screen.py`, `src/agentx/agent/demo/scenarios.py`, `AgentController.load_demo_scenario_by_name()` / `reset_state()` / `Agent.clear_state()`.
- **Scenarios:** A = File Reader (1 cycle); B = Knowledge Assistant (read notes → write summary, multi-step, condition DSL showcase).
- **Side effect:** Fixed latent feature_007 bug (tools reading `command.parameters` instead of `command.action`) breaking runtime `EXECUTE_TOOL` create/query/update actions.
- **Artifacts:** `.meta/.../features/feature_010.agent_demo_screen/`.

## feature_011 — Fast Agent ✅
**Goal:** Streamlined, modal-dialog-driven agent UX reusing existing feature_007 `Agent` engine through stack of Textual `ModalScreen` dialogs. Existing `🤖 Agent` button relabeled `⚙️ Advanced Agent`; new `⚡ Fast Agent` (`f` key) offers simpler UX.
- **Flow:** Goal → Running (auto-runs cycles) → Reflection (on proposal) → Result
- **Simplicity:** One goal at a time, natural-language input, no raw policy authoring, auto-runs cycles pausing only on reflection proposals, auto-resumes latest snapshot
- **First `ModalScreen` use** in codebase; Textual `ModalScreen` stack with `dismiss(value)` + callbacks
- **Key code:** `src/agentx/agent/view/tui/fast_agent_screen.py`, `fast_agent_modals.py`, `fast_agent_view.py`, `src/agentx/agent/controller/agent_controller.py` (+ `get_cycle_summary()`), `src/agentx/agent/adapter.py` (+ `create_fast()`), `src/agentx/ui/screens/main/main_controller.py` (+ `show_fast_agent()`), `src/agentx/ui/tui/screens/main_screen.py` (+ `f` binding, `⚡ Fast Agent` button, grid `3 2`, relabel "Advanced Agent")
- **MVC++ clean:** View-only addition; no Model-layer changes; `FastAgentTUIView` = no-op `IAgentViewPartner` virtual subclass; `get_cycle_summary()` returns plain dicts for display
- **Tests:** 44 new tests (unit + integration + MVC), 0 regressions
- **Artifacts:** `.meta/.../features/feature_011.fast_agent/` (design, impl notes, test report)

---

## Cross-Cutting Characteristics
- **Persistence:** stdlib `sqlite3`, no ORM, idempotent DDL — three databases (`session.db`, `rag.db`, `agent_session.db`). See persistence.md.
- **AI-optional:** Agent cycle runs offline; reflection skipped when no AI service wired. Chat/RAG require LLM provider (OpenRouter default).
- **Two UIs, one controller layer:** Console and TUI share controllers via provider pattern — see architecture.md §3.
- **Test coverage:** ~470 tests including Textual pilot e2e; feature tests under `tests/features/<feature_slug>/`.