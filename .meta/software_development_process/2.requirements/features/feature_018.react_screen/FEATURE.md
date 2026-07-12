# Feature 018: ReAct Screen

> **Status:** [x] Completed
> **Created:** 2026-07-11
> **WORK.md task:** Implement feature_018.react_screen — ReAct chat screen with reasoning + tool calls

---

## Summary

The ReAct screen adds a new TUI chat interface powered by LangChain's `create_agent` (the ReAct pattern: **Re**asoning + **Act**ing). Unlike the plain Chat screen which sends messages directly to an LLM, the ReAct agent can:

1. **Think** — display its reasoning process (chain-of-thought) in real-time
2. **Act** — call tools (calculator, time) when it needs information
3. **Observe** — display tool results inline
4. **Respond** — stream the final answer token-by-token

The screen uses the existing ModelRegistry/AIService for LLM selection, so it works with all 6 providers (OpenRouter, OpenAI, Gemini, NVIDIA, Ollama, LlamaCpp).

---

## Scope (one sentence — what "done" looks like)

A new "ReAct" TUI screen accessible via `t` key or 🧠 ReAct button on the Main screen, showing a chat conversation with visible reasoning steps, tool calls/results, and streaming answers, built on LangChain's `create_agent` with in-memory conversation history, non-blocking UI via background threads, and full MVC++ compliance.

---

## Task type

new_screen

---

## Phase artifacts (traceability)

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `.meta/software_development_process/2.requirements/features/feature_018.react_screen/FEATURE.md` | [x] |
| Analysis | Use cases + operations | `.meta/software_development_process/3.analysis/features/feature_018.react_screen/analysis_001_use_cases.md` | [x] |
| Analysis | Dialog diagram | `.meta/software_development_process/3.analysis/features/feature_018.react_screen/analysis_002_dialog_diagram.md` | [x] |
| Analysis | Class diagram | `.meta/software_development_process/3.analysis/features/feature_018.react_screen/analysis_003_class_diagram.md` | [x] |
| Analysis | Data dictionary | `.meta/software_development_process/3.analysis/features/feature_018.react_screen/analysis_004_data_dictionary.md` | [x] |
| Analysis | NFRs + Traceability | `.meta/software_development_process/3.analysis/features/feature_018.react_screen/analysis_005_nfrs.md` | [x] |
| Design | Design class diagram | `.meta/software_development_process/4.design/features/feature_018.react_screen/design_001_react_screen.md` | [x] |
| Design | Sequence diagrams | `.meta/software_development_process/4.design/features/feature_018.react_screen/sequence_diagrams.md` | [x] |
| Design | Operation specs | `.meta/software_development_process/4.design/features/feature_018.react_screen/operation_spec_001_react_operations.md` | [x] |
| Implementation | Model: ReactAgentService + tools | `src/agentx/model/react/` | [x] |
| Implementation | Controller: ReactController + IReactViewPartner | `src/agentx/ui/screens/react/` | [x] |
| Implementation | View: ReactTUIScreen | `src/agentx/ui/tui/screens/react_screen.py` | [x] |
| Implementation | Main wiring | `src/agentx/ui/screens/main/main_controller.py`, `src/agentx/ui/tui/screens/main_screen.py`, `src/agentx/ui/tui/framework/widgets.py` | [x] |
| Testing | Unit + Pilot + Integration + MVC++ + Freeze | `tests/features/feature_018.react_screen/` | [x] |

---

## Key Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Use `langchain.agents.create_agent` (not deprecated `create_react_agent`) | LangChain v1.0+ API; project has `langchain==1.3.10` |
| D2 | `stream_events(version="v3")` for streaming | Typed projections (`messages`, `tool_calls`) give clean access to reasoning, text, tool lifecycle |
| D3 | `InMemorySaver` checkpointer + `thread_id` | Conversation history persists across turns without DB; matches Chat screen's non-DB fallback |
| D4 | Background thread for agent invocation | `stream_events` is synchronous; running on UI thread would freeze Textual |
| D5 | Callbacks for streaming events | Controller marshals callbacks to UI thread via `app.call_from_thread()` |
| D6 | `threading.Event` for cancellation | Cancel checked between every delta; Escape/q responsive within 50ms |
| D7 | Two built-in tools: `calculator` + `get_current_time` | Simple, dependency-free tools demonstrating ReAct pattern |
| D8 | No adapter class needed | Screen pushed directly by `navigate_to_child` (like ModelsTUIScreen) |
| D9 | Keybinding `t` for ReAct | `r` taken by RAG; `t` = "Thinking" |
| D10 | MenuGrid 3×3 (7 buttons) | Added ReAct button; grid-size changed from 3×2 |

---

## Files Created / Modified

### New Files
- `src/agentx/model/react/__init__.py`
- `src/agentx/model/react/react_tools.py`
- `src/agentx/model/react/react_agent_service.py`
- `src/agentx/ui/screens/react/__init__.py`
- `src/agentx/ui/screens/react/react_controller.py`
- `src/agentx/ui/tui/screens/react_screen.py`
- `tests/features/feature_018.react_screen/test_react_agent_service.py` (17 tests)
- `tests/features/feature_018.react_screen/test_react_controller.py` (16 tests)
- `tests/features/feature_018.react_screen/test_react_screen.py` (18 tests)
- `tests/features/feature_018.react_screen/test_react_integration.py` (11 tests)
- `tests/features/feature_018.react_screen/test_react_mvc.py` (16 tests)
- `tests/features/feature_018.react_screen/test_react_freeze.py` (9 tests)

### Modified Files
- `src/agentx/ui/interfaces.py` — Added `IReactViewPartner` ABC
- `src/agentx/ui/screens/main/main_controller.py` — Added `show_react` + `get_react_controller`
- `src/agentx/ui/tui/screens/main_screen.py` — Added `t` binding, `action_open_react`, `btn-react` handler, updated help text
- `src/agentx/ui/tui/framework/widgets.py` — MenuGrid: 7th button + `grid-size: 3 3`

---

## Test Results

| Test Suite | Tests | Status |
|------------|-------|--------|
| Model (react_tools + ReactAgentService) | 17 | ✅ PASS |
| Controller (ReactController + IReactViewPartner) | 16 | ✅ PASS |
| View (ReactTUIScreen unit + pilot) | 18 | ✅ PASS |
| Integration (Main wiring) | 11 | ✅ PASS |
| MVC++ compliance | 16 | ✅ PASS |
| Freeze regression | 9 | ✅ PASS |
| **Feature Total** | **87** | ✅ **ALL PASS** |

**Full suite:** 879 tests pass (87 new + 792 existing), 0 regressions

---

## Architecture Compliance

- ✅ **MVC++**: View (`react_screen.py`) has zero `agentx.model` imports
- ✅ **Abstract Partners**: `IReactViewPartner` is `ABC` with `@abstractmethod`
- ✅ **Controller mediates**: `ReactController` imports Model + View interface
- ✅ **No SQL in Controller**: Uses in-memory checkpointer
- ✅ **`register_partner`**: Screen virtually registered as `IReactViewPartner`
- ✅ **Non-blocking**: Agent runs on daemon thread; UI stays responsive
- ✅ **Proper `call_from_thread`**: Uses `self.app.call_from_thread()` (not `self.call_from_thread()`)

---

## Usage

1. Press `t` on Main screen, or click 🧠 ReAct button
2. Type a question (e.g., "What is 15% of 240?" or "What time is it?")
3. Press `Ctrl+Enter` to send
4. Watch the agent:
   - 💭 Thinking — reasoning displayed in italic
   - 🔧 Tool call — tool name + arguments
   - 📊 Tool result — output from tool
   - 💬 Answer — streaming final response
5. Continue conversation — context preserved
6. Press `Escape` or `q` to return to Main

---

## Future Extensions

- Add more tools (web search, file I/O, code execution)
- Persist conversation history to SQLite (like Chat screen)
- Support for structured output / response format
- Sub-agent delegation (LangGraph subgraphs)