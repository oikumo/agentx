# Implementation Notes — feature_018.react_screen

**Feature:** ReAct Screen (ReAct chat with reasoning + tool calls)
**Date:** 2026-07-11
**Status:** Completed — all tests pass, 0 regressions

---

## Summary

Implemented a new "ReAct" TUI screen that provides a chat-like conversation interface powered by LangChain's `create_agent` (ReAct pattern: Reasoning + Acting). Unlike the plain Chat screen (direct LLM streaming), the ReAct agent:

1. **Thinks** — shows its reasoning chain (chain-of-thought) in real-time
2. **Acts** — calls tools (calculator, time) when it needs information
3. **Observes** — displays tool results inline
4. **Responds** — streams the final answer token-by-token

---

## Implementation Files

### Model Layer (`src/agentx/model/react/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Exports ReactAgentService, calculator, get_current_time |
| `react_tools.py` | Built-in tools: `calculator` (safe math eval via AST), `get_current_time` (ISO datetime) |
| `react_agent_service.py` | Wraps `langchain.agents.create_agent`; manages InMemorySaver checkpointer; provides `stream_agent()` with callbacks for reasoning/text/tool events; cancellation via `threading.Event` |

**Key implementation details:**
- `create_agent(model=llm, tools=[calculator, get_current_time], system_prompt=..., checkpointer=InMemorySaver())`
- `stream_agent()` uses `agent.stream_events(version="v3")` — yields typed projections: `messages` (reasoning/text/tool_calls), `tool_calls` (execution lifecycle)
- Cancel event checked between every delta; `finally` block clears event for next run
- `thread_id` (UUID4) isolates conversations; `reset_conversation()` generates new thread_id

### Controller Layer (`src/agentx/ui/screens/react/`)

| File | Purpose |
|------|---------|
| `react_controller.py` | Implements `IReactViewPartner` ABC; owns `ReactAgentService`; `send_message()` spawns daemon worker thread calling `service.stream_agent()` with callbacks marshalled via `app.call_from_thread()` |

**Key implementation details:**
- Worker thread runs `_run_agent()` which calls `service.stream_agent()` with lambdas capturing view methods
- All view callbacks go through `marshal(fn, *args)` → `app.call_from_thread(fn, *args)` — **critical**: uses `self.app.call_from_thread()`, NOT `self.call_from_thread()` (Screen doesn't have it!)
- `send_message()` returns False if agent already running (prevents concurrent runs)
- C5 pattern: reuse existing controller on re-entry

### View Layer (`src/agentx/ui/tui/screens/react_screen.py`)

| Class | Purpose |
|-------|---------|
| `ReactTUIScreen` | Extends `BaseAgentXScreen`; displays 4 message types: user (ChatMessage), thinking (Static + 💭), tool call (Static + 🔧), tool result (Static + 📊), answer (ChatMessage streaming); keybindings: q/Escape/ctrl+enter |

**Key implementation details:**
- `_is_streaming` + `_streaming_widget` + `_streaming_text` track streaming state
- `show_answer_chunk()` sets streaming state synchronously for testability, then `call_later` for UI update
- `on_unmount()` calls `super().on_unmount()` (cancels blocking tasks per feature_014) then `controller.cancel()`
- `register_partner(IReactViewPartner, ReactTUIScreen)` at module level (metaclass conflict workaround)

### Integration (Main Screen Wiring)

| File | Changes |
|------|---------|
| `src/agentx/ui/interfaces.py` | Added `IReactViewPartner(ABC)` with 6 abstract methods |
| `src/agentx/ui/screens/main/main_controller.py` | Added `_react_controller`, `show_react()` (C5), `get_react_controller()` |
| `src/agentx/ui/tui/screens/main_screen.py` | Added Binding("t", "open_react", "ReAct"), `action_open_react()`, `btn-react` handler, updated help text |
| `src/agentx/ui/tui/framework/widgets.py` | MenuGrid: added 🧠 ReAct button, `grid-size: 3 3` |

---

## Testing

| Test File | Tests | Scope |
|-----------|-------|-------|
| `test_react_agent_service.py` | 17 | Model: tools, service creation, streaming, cancel, reset, history |
| `test_react_controller.py` | 16 | Controller: send_message, cancel, is_running, conversation mgmt, worker thread |
| `test_react_screen.py` | 18 | View: layout, actions, display methods, lifecycle, pilot tests |
| `test_react_integration.py` | 11 | Main wiring: controller, bindings, button, pilot navigation |
| `test_react_mvc.py` | 16 | MVC++: View no Model imports, Controller imports Model, ABC, register_partner, mvc_check.py 0 errors |
| `test_react_freeze.py` | 9 | Freeze regression: off-UI-thread, Escape responsive, daemon thread, on_unmount cleanup |

**Total feature tests: 87** — all pass.

---

## MVC++ Compliance

- ✅ View (`react_screen.py`) imports: `agentx.ui.tui.framework`, `textual`, `agentx.ui.interfaces` — **no `agentx.model`**
- ✅ Controller (`react_controller.py`) imports: `agentx.model.react.react_agent_service`, `agentx.ui.interfaces` (View ABC)
- ✅ Abstract Partner: `IReactViewPartner(ABC)` with `@abstractmethod` for all 6 methods
- ✅ `register_partner(IReactViewPartner, ReactTUIScreen)` called
- ✅ `mvc_check.py` — 0 errors, 0 warnings on all 6 ReAct files

---

## Non-Blocking / Freeze Prevention

Following the patterns established in feature_011 (Fast Agent freeze fix) and feature_014 (BlockingTaskRunner):

- Agent runs on `threading.Thread(daemon=True, name="AgentX-ReAct-Worker")`
- Streaming callbacks marshalled via `app.call_from_thread()`
- Cancel event checked between every delta (reasoning/text/tool)
- `on_unmount()` → `super().on_unmount()` + `controller.cancel()`
- Escape/q responsive during agent execution (verified by pilot test)

---

## Known Limitations / Future Work

1. **No persistence** — Uses `InMemorySaver` only; conversation lost on screen close (like Chat screen's non-DB fallback). Could add SQLite persistence like `ChatHistoryRepository`.
2. **Fixed tools** — Only `calculator` and `get_current_time` built-in. Extensible by adding to `ReactAgentService._tools`.
3. **Provider-dependent reasoning** — `message.reasoning` only populated for models that emit reasoning blocks (e.g., some Anthropic/OpenAI models). Works with all 6 providers but reasoning visibility varies.
4. **Single conversation** — One `thread_id` per screen session. No conversation list/switching UI.

---

## Verification

- **All feature tests:** 87 pass
- **Full test suite:** 879 pass (87 new + 792 existing), 0 regressions
- **MVC++ check:** 0 errors, 33 warnings (baseline)
- **TDD cycles:** 5 component-level cycles completed (Model, Controller, View, Integration, Compliance/Freeze)