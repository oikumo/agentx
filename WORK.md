# WORK

> Single-developer + coding-agent roadmap. Machine-parseable, minimal friction, git-friendly.

---

## Convention

| Symbol | Meaning |
|--------|---------|
| `[ ]`  | Pending |
| `[~]`  | In progress (agent working on it) |
| `[x]`  | Done |
| `[!]`  | Blocked / needs decision |

**Hierarchy** - top-level task -> optional subtasks (indented 4 spaces).
**Metadata** - optional inline comment: `<!-- id:T-123 prio:medium agent:true -->`
**Thoughts** - separate `---` line then bullet list; tools can strip it.

---

## Tasks

- [x] **feature_007.agentx_intelligent_agent_behaviour**
    - Full OMT++ cycle: Analysis (8) -> Design -> Impl -> 132 tests, 0 regressions; user validated
- [x] **Fix feature_007 bugs per BUG_FIX_PLAN.md**
    - 39 files, all P0-P3 fixed, 32 regression tests, 169/169 pass, MVC++ 0/0
- [x] **feature_004.modern_ui**
    - TUI infra, MainTUIScreen, main.py, e2e; 4 fix rounds; user accepted; FEATURE.md
- [x] **Update README.md with feature_006 and agentic workflow**
- [x] **Update application design overview in .meta/.../4.design/**
- [ ] **feature_001.session_user_objectives_driven_by_Petri_Net**
    - Define scope & success criteria
- [x] **feature_006.opencode_process_enforcement**
    - MVC++ linter, scaffolder, permissions, gate plugin, AGENTS.md, phase exit, omt_status/omt_complete, e2e guard; user accepted
- [ ] **feature_002.rag_retrieval_augmented_generation**
    - Scaffold design doc
- [x] **feature_012.tui_framework**
    - Reusable TUI base-class lib (framework/), 9 screens refactored, MVC++ 0/6
- [x] **feature_010.agent_demo_screen**
    - Design, model (A+B), controller, AgentDemoScreen, MVC++ 0/6
- [x] **feature_011.fast_agent**
    - Design + impl (3 View + 4 edited), 44 tests, 0 regressions, MVC++ 0/6
- [x] **feature_013.ai_model_provider_selector**
    - Models screen (m), ModelRegistry (5 providers, JSON persist, factory), AIService delegates, 4 call sites refactored, MVC++ 0/6
- [x] **feature_014.tui_nonblocking_runner**
    - BlockingTaskRunner (async_runner.py), BaseAgentXScreen.run_blocking(), refactored Agent/Demo, MVC++ 0/1
- [x] **Fix feature_011.fast_agent UI freeze**
    - Root cause: _running shadowed DOMNode._running + sync llm.invoke(); fix: _auto_running, daemon thread + queue + polling; MVC++ 0/0
- [x] **feature_016.tdd_enforcement**
    - TDD engine (tdd_check.py, 9 cmds), AST inference, true-RED, two-hats gate, 5 tools, hooks, MVC++ 0/6; docs updated
- [x] **Fix feature_017.chat_screen_conversation_history_bug**
    - RagChatHistory class attrs shared; fix: @dataclass + default_factory; MVC++ 0/0
- [x] **feature_017.improve_chat_screen**
    - ChatHistoryRepository (SQLite), controller persistence, TUI sidebar (Ctrl+L), timestamps, CRUD keys, MVC++ 0/33
- [x] **feature_018.chat_screen_improvements**
    - ChatMessage: prefixes, visual distinction; ChatTUIScreen: no sidebar/timestamps, 3 keys; removed ConversationSidebar; MVC++ 0/33
- [x] **Fix chat screen "no assistant message" bug**
    - _run_llm_async used self.call_from_thread() on Screen; fix: self.app.call_from_thread(); MVC++ 0
- [x] **Fix chat screen "no conversation history" bug**
    - Throwaway local history per turn; fix: worker uses controller.history + on_mount calls start_new_conversation(); MVC++ 0
- [x] **feature_018.react_screen**
    - Analysis, Design, TDD: Model (ReactAgentService, 2 tools) -> Controller -> View (ReactTUIScreen) -> Integration (t, 3x3); MVC++ 0; ReAct with thinking, tools, results, streaming
- [x] **feature_019.coding_agent_screen**
    - Analysis, Design, TDD: Model (5 file tools + CodingAgentService) -> Controller -> View (diff highlighting) -> Integration (d, 3x3); MVC++ 0/33; Coding Agent with file tools, sandbox, non-blocking

---

## Agent Scratchpad (auto-managed, do not edit manually)

```
[2026-06-27] Completed feature_004 nav fixes; all tests pass
[2026-06-27] Next: write FEATURE.md for feature_004
[2026-06-27] Fixed TUI RAG screen freeze on Select - replaced blocking console with TUI
[2026-06-28] Moved feature_003 to feature_007 (scaffolded); Analysis started
[2026-06-29] Completed 8 Analysis artifacts for feature_007; usability validated; Design next
[2026-06-29] Updated WORK.md per PLAN.md; creating design_001_agent_framework.md
[2026-06-29] Architecture decision: persistence = stdlib sqlite3 only (no SQLAlchemy/Alembic)
[2026-06-29] Design D6/D7/D8 done: ToolSpec, ToolRegistry, policy engine, reflection engine
[2026-06-29] Fixed META HARNESS bug: feature dir resolution (short vs full-slug); added resolveFeatureDir(); e2e passes
[2026-06-29] OMT harness verified post-restart; advanced feature_007 Design->Programming; implemented full agent framework; MVC 0/0; cycle test passed
[2026-06-29] Testing complete (T1-T6): 132 tests, 11 files, all pass; 0 regressions on 262 existing; moved agent_adapter.py to fix MVC++ violation
[2026-06-29] Fixed AI service wiring: AIServiceAdapter + IAIServicePartner; ReflectionEngine shows "AI unavailable" without keys; 137/137 pass
[2026-07-04] Independent review feature_007 (39 files): 17/18 bugs verified, 9 new found; updated BUG_FIX_PLAN.md
[2026-07-04] All P0/P1 fixes done (Groups 1-9): resume_session restores tools/memory/config/goal/reflection; 21 regression tests; 158/158 pass, MVC++ 0/0
[2026-07-04] All P2/P3 fixes done: 32 regression tests total; 169/169 feature_007 pass, MVC++ 0/0; ALL bugs resolved (M4 dropped)
[2026-07-04] Implemented feature_011.fast_agent: "Fast Agent" (f key), ModalScreen stack (Goal->Running->Reflection->Result); 3 View files, 4 edited; 44 tests + 5 updated; MVC++ 0/6
[2026-07-05] Fixed feature_011 UI freeze: (1) _running shadowed DOMNode._running; (2) sync run_cycle on UI thread; fix: _auto_running + daemon worker + queue + polling; 4 regression tests; 48/48 pass, MVC++ 0/0
[2026-07-05] Implemented feature_012.tui_framework: reusable base-class lib at src/agentx/ui/tui/framework/; refactored 9 screens/adapters + app; 62 tests; MVC++ 0/6
[2026-07-05] Implemented feature_013.ai_model_provider_selector: Models screen (m), ModelRegistry (5 providers, JSON persist, factory), AIService delegates, 4 call sites refactored; 56 tests + 6 updates; MVC++ 0/6
[2026-07-05] Added NVIDIA as 6th provider (minor_feature): langchain-nvidia-ai-endpoints, NvidiaProvider, catalog entry changes; tests extended; MVC++ 0/6
[2026-07-05] Implemented feature_014.tui_nonblocking_runner: BlockingTaskRunner (async_runner.py), BaseAgentXScreen.run_blocking(), refactored Agent/Demo screens; 38 tests; MVC++ 0/1
[2026-07-11] Closed feature_016.tdd_enforcement: verified impl, 52 tests pass, MVC++ 0/6; filled FEATURE.md/PLAN.md/WORK.md; Testing->Done via omt_complete
[2026-07-11] Integrated TDD into meta docs: README (v0.2.0, TDD section, roadmap), AGENTS.md (enforcement 6), omt_agent_guide.md (11.4); e2e passes
[2026-07-11] Fixed feature_017 bug: RagChatHistory class attrs shared; fix: @dataclass + default_factory; 5 tests; MVC++ 0/0
[2026-07-11] Implemented feature_017 chat improvements: ChatHistoryRepository (SQLite), controller persistence, TUI sidebar (Ctrl+L), timestamps, CRUD keys; 31 tests; MVC++ 0/33
[2026-07-11] Fixed "no assistant message": _run_llm_async used self.call_from_thread() on Screen; fix: self.app.call_from_thread(); MVC++ 0
[2026-07-11] Fixed "no conversation history": throwaway local history; fix: worker uses controller.history + on_mount calls start_new_conversation(); MVC++ 0
```
