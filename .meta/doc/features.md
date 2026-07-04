# Feature Catalog

> **Scope:** every feature in agentx — its status, what it does, and where its
> code + phase artifacts live.
> **Status legend:** ✅ done · 🔨 in progress · ⏳ pending · 🅿️ placeholder

| # | Feature | Status | Summary |
|---|---------|--------|---------|
| 001 | session_user_objectives_driven_by_Petri_Net | ⏳ | Petri-net-driven session objectives (will swap into the agent's `IGoalManager`) |
| 002 | rag_retrieval_augmented_generation | ⏳ | RAG retrieval + generation (partially implemented; needs design scaffold) |
| 004 | modern_ui | ✅ | Textual TUI with full screen navigation (Main/Chat/RAG) |
| 005 | agentx_file_system_agentic_tools | ✅ | Agentic filesystem tools (folded into feature_007's tool registry) |
| 006 | opencode_process_enforcement | ✅ | OMT++ process gate: `mvc_check.py`, `new_feature.py`, `omt_enforcer.ts` |
| 007 | agentx_intelligent_agent_behaviour | ✅ | The intelligent agent: goals, policy DSL, memory, reflection, tools |
| 010 | agent_demo_screen | ✅ | One-trigger demo screen showcasing the agent cycle (scenarios A/B) |

> `feature_008.agent_framework` and `feature_009.feature_007_agentx_intelligent_agent_behaviour`
> are empty placeholder dirs (only `FEATURE.md` + `plan/`) — not implemented.

---

## feature_001 — Session Objectives (Petri Net) ⏳

**Goal:** drive session objectives through a Petri-net model. Will provide a
concrete `IGoalManager` implementation that replaces the current stub
(`agent/model/goal/manager.py`). The agent facade depends on the `IGoalManager`
abstraction, so this swaps in at runtime.

- **Status:** scope & success criteria not yet defined (`WORK.md`).
- **Integration point:** `agent/model/goal/manager.py` → `IGoalManager`.

## feature_002 — RAG (Retrieval Augmented Generation) ⏳

**Goal:** ingest documents (web + local) into a vector store and answer
questions with retrieval-augmented LLM responses. The `Rag` orchestrator and
`RagQuery` pipeline exist and are wired into the RAG screen; the feature needs
its design scaffold to formalise requirements.

- **Status:** partially implemented (see [subsystems.md](subsystems.md) §RAG);
  design doc pending.
- **Key code:** `src/agentx/model/rag/`.

## feature_004 — Modern UI ✅

**Goal:** a rich Textual TUI replacing the legacy console-only flow, with full
screen navigation (Main → Chat → RAG → Agent), streaming chat, and non-blocking
RAG repository selection.

- **Key code:** `src/agentx/ui/tui/` (app, screens, adapters, provider).
- **Highlights:** `MainTUIScreen` pushes sub-screens directly AND calls
  `controller.show_*()` for wiring (dual-path fix for navigation freezes);
  `TUIChatAdapter` streams chunks into a single growing widget; RAG screens use
  TUI modal screens instead of blocking console input.
- **Artifacts:** `.meta/.../features/feature_004.modern_ui/`.

## feature_005 — Agentic File System Tools ✅

**Goal:** agentic filesystem tools. Folded into feature_007's tool registry as
the `FileSystemTool` (a hybrid sensor/actuator).

- **Key code:** `src/agentx/agent/model/tools/filesystem_tool.py`.

## feature_006 — Opencode Process Enforcement ✅

**Goal:** mechanically enforce the OMT++ methodology via opencode. Provides the
MVC++ linter, the feature scaffolder, live permissions, and the process gate
plugin with phase-exit validation.

- **Key code:** `scripts/omt/mvc_check.py`, `scripts/omt/new_feature.py`,
  `.opencode/plugin/omt_enforcer.ts`, `.opencode/plugin/omt_status.ts`,
  `opencode.jsonc`.
- **Artifacts:** `.meta/.../features/feature_006.opencode_process_enforcement/`.

## feature_007 — Intelligent Agent Behaviour ✅

**Goal:** a complete intelligent-agent subsystem that runs a
perceive → decide → act → reflect cycle driven by goals, a policy condition
DSL, a tool registry, volatile/persistent memory, and a reflection engine with
self-improvement proposals.

- **Key code:** `src/agentx/agent/` (model, controller, view, persistence,
  interfaces, types).
- **Subsystems:** Agent facade, GoalManager, PolicyEngine (condition DSL +
  conflict resolver), MemoryManager, ReflectionEngine (critique parser +
  safety evaluator + proposal router), ToolRegistry (FileSystemTool,
  RagSensorTool, SessionTool), `agent_session.db`.
- **Bug-fix pass:** all bugs in `BUG_FIX_PLAN.md` resolved (P0–P3); 169 tests
  pass; MVC++ 0/0.
- **Artifacts:** `.meta/.../features/feature_007.agentx_intelligent_agent_behaviour/`
  (8 analysis docs + design + operation specs + impl notes + test report).

## feature_010 — Agent Demo Screen ✅

**Goal:** a dedicated Textual screen that demonstrates feature_007 with one
trigger. From the Agent screen, press `d` (or type `demo [a|b]`) — it seeds a
goal + rules + sandbox file, auto-runs a cycle, and offers Run/Reset/Back
buttons.

- **Key code:** `src/agentx/agent/view/tui/demo_screen.py`,
  `src/agentx/agent/demo/scenarios.py`, +
  `AgentController.load_demo_scenario_by_name()` / `reset_state()` /
  `Agent.clear_state()`.
- **Scenarios:** A = File Reader (1 cycle); B = Knowledge Assistant (read notes
  → write summary, multi-step, condition DSL showcase).
- **Side effect:** fixed a latent feature_007 bug (tools reading
  `command.parameters` instead of `command.action`) that broke runtime
  `EXECUTE_TOOL` create/query/update actions.
- **Artifacts:** `.meta/.../features/feature_010.agent_demo_screen/`.

---

## Cross-cutting characteristics

- **Persistence convention:** stdlib `sqlite3`, no ORM, idempotent DDL — three
  databases (`session.db`, `rag.db`, `agent_session.db`). See
  [persistence.md](persistence.md).
- **AI-optional:** the agent cycle runs offline; reflection is skipped when no
  AI service is wired. Chat/RAG require an LLM provider (OpenRouter default).
- **Two UIs, one controller layer:** Console and TUI share the same
  controllers via the provider pattern — see [architecture.md](architecture.md) §3.
- **Test coverage:** ~470 tests including Textual pilot e2e; feature tests live
  under `tests/features/<feature_slug>/`.
