# Design 001 — ReAct Screen Architecture & Class Diagram

**Feature:** feature_018.react_screen  
**Phase:** Design  
**Date:** 2026-07-11

---

## 1. Overview

The ReAct screen adds a new TUI screen that provides a chat-like conversation
interface powered by LangChain's `create_agent` (the ReAct pattern). Unlike
the plain Chat screen (direct LLM streaming), the ReAct agent can reason
(think), call tools (act), observe results, and then produce a final answer —
all visible to the user in real-time.

### Key Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Use `langchain.agents.create_agent` (not deprecated `create_react_agent`) | LangChain v1.0+ API; `create_react_agent` is deprecated. Project has `langchain==1.3.10`. |
| D2 | Use `agent.stream_events(version="v3")` for streaming | Typed projections (`messages`, `tool_calls`) give clean access to reasoning, text, and tool lifecycle. Sync version works with background threads. |
| D3 | Use `InMemorySaver` checkpointer + `thread_id` | Conversation history persists across turns without DB. ReAct conversations are live sessions (no disk persistence needed — matches chat screen's non-DB fallback). |
| D4 | Background thread for agent invocation | `stream_events` is synchronous; running it on the UI thread would freeze Textual. Same pattern as chat screen's `_run_llm_async`. |
| D5 | Callbacks (not return values) for streaming | The controller passes callback functions to `stream_agent()`. The service calls them as events arrive. The controller marshals to the UI thread via `self.app.call_from_thread()`. |
| D6 | `threading.Event` for cancellation | The streaming loop checks `_cancel_event.is_set()` between events. Clean, non-blocking cancel. |
| D7 | Two built-in tools: `calculator` + `get_current_time` | Simple, always-available tools that demonstrate the ReAct pattern without external dependencies. |
| D8 | No adapter class needed | The ReAct screen is pushed directly by `navigate_to_child` (like ModelsTUIScreen). No console-view legacy to support. |
| D9 | Keybinding `t` for ReAct | `r` is taken by RAG. `t` = "Thinking". Button: 🧠 ReAct. |
| D10 | MenuGrid grows from 6→7 buttons (3×3 grid) | Add 7th button; change grid-size from `3 2` to `3 3`. |

---

## 2. File Structure

```
src/agentx/
├── model/
│   └── react/
│       ├── __init__.py
│       ├── react_agent_service.py    # Model: wraps create_agent + streaming
│       └── react_tools.py            # Model: built-in tools (calculator, time)
├── ui/
│   ├── screens/
│   │   └── react/
│   │       ├── __init__.py
│   │       └── react_controller.py   # Controller: IReactViewPartner ABC + ReactController
│   ├── tui/
│   │   └── screens/
│   │       └── react_screen.py       # View: ReactTUIScreen (BaseAgentXScreen)
│   ├── interfaces.py                 # Modified: add IReactViewPartner
│   ├── screens/main/
│   │   └── main_controller.py        # Modified: add show_react / get_react_controller
│   └── tui/
│       ├── screens/
│       │   └── main_screen.py        # Modified: add 't' binding + action_open_react
│       └── framework/
│           └── widgets.py            # Modified: MenuGrid 7th button + grid 3×3
└── main.py                           # Unchanged

tests/
└── features/
    └── feature_018.react_screen/
        ├── __init__.py
        ├── test_react_agent_service.py   # Unit: Model tests
        ├── test_react_controller.py      # Unit: Controller tests
        ├── test_react_screen.py          # Unit + Pilot: View tests
        ├── test_react_integration.py     # Integration: Main screen wiring
        ├── test_react_freeze.py          # Regression: non-blocking
        └── test_react_mvc.py             # MVC++ compliance
```

---

## 3. Design Class Diagram

### 3.1 Model Layer

```
┌──────────────────────────────────────────────────────┐
│               react_tools.py                          │
├──────────────────────────────────────────────────────┤
│  @tool                                                │
│  calculator(expression: str) -> str                  │
│    Safely evaluates a math expression.               │
│    Whitelist: +, -, *, /, %, **, (), float literals. │
│    Returns: str(result) or error message.            │
│                                                       │
│  @tool                                                │
│  get_current_time() -> str                           │
│    Returns current datetime in ISO 8601 format.      │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│            react_agent_service.py                     │
│              ReactAgentService                        │
├──────────────────────────────────────────────────────┤
│  Fields:                                              │
│    _agent: CompiledStateGraph                         │
│    _checkpointer: InMemorySaver                       │
│    _thread_id: str                                    │
│    _cancel_event: threading.Event                     │
│                                                       │
│  Methods:                                             │
│    __init__(llm=None, tools=None, system_prompt=None) │
│      → Creates agent via create_agent()               │
│      → Generates thread_id = str(uuid7())             │
│                                                       │
│    stream_agent(                                      │
│      user_message: str,                               │
│      on_reasoning: Callable[[str], None],             │
│      on_tool_call: Callable[[str, str], None],        │
│      on_tool_result: Callable[[str, str], None],      │
│      on_answer: Callable[[str], None],                │
│      on_done: Callable[[], None],                     │
│      on_error: Callable[[str], None],                 │
│    ) -> None                                          │
│      → Runs agent.stream_events(version="v3")         │
│      → Routes events to callbacks                     │
│      → Checks _cancel_event between events            │
│                                                       │
│    cancel() -> None                                   │
│      → Sets _cancel_event                             │
│                                                       │
│    reset_conversation() -> None                       │
│      → Generates new thread_id                        │
│      → Clears _cancel_event                           │
│                                                       │
│    get_history() -> list[BaseMessage]                 │
│      → Returns current thread's message history       │
│                                                       │
│    @property                                          │
│    is_running() -> bool                               │
│    thread_id() -> str                                 │
└──────────────────────────────────────────────────────┘
```

### 3.2 Controller Layer

```
┌──────────────────────────────────────────────────────┐
│                  interfaces.py                        │
│            IReactViewPartner (ABC)                    │
├──────────────────────────────────────────────────────┤
│  @abstractmethod                                      │
│  def send_message(self, user_message: str) -> bool    │
│    → Returns True if message was accepted.            │
│                                                       │
│  @abstractmethod                                      │
│  def cancel(self) -> None                             │
│    → Cancel in-progress agent run.                    │
│                                                       │
│  @property                                            │
│  @abstractmethod                                      │
│  def is_running(self) -> bool                         │
│                                                       │
│  @abstractmethod                                      │
│  def get_history(self) -> list                        │
│                                                       │
│  @abstractmethod                                      │
│  def close(self) -> None                              │
│                                                       │
│  @abstractmethod                                      │
│  def start_new_conversation(self) -> None             │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│              react_controller.py                      │
│                ReactController                        │
│            implements IReactViewPartner               │
├──────────────────────────────────────────────────────┤
│  Fields:                                              │
│    _service: ReactAgentService                        │
│    _worker_thread: Thread | None                      │
│                                                       │
│  Methods:                                             │
│    __init__(service: ReactAgentService | None = None) │
│      → Creates service if not provided                │
│      → Uses AIService().get_current_llm()             │
│                                                       │
│    send_message(user_message) -> bool                 │
│      → If _service.is_running: return False           │
│      → Spawn worker thread calling _run_agent()       │
│      → Return True                                    │
│                                                       │
│    _run_agent(user_message, view)                     │
│      → Calls service.stream_agent(                    │
│          on_reasoning=lambda t: view.show_thinking(t),│
│          on_tool_call=lambda n,a: view.show_tool_call(n,a), │
│          on_tool_result=lambda n,r: view.show_tool_result(n,r), │
│          on_answer=lambda t: view.show_answer_chunk(t),       │
│          on_done=lambda: view.show_answer_final(),    │
│          on_error=lambda e: view.show_error(e),       │
│        )                                              │
│      → All view calls marshalled via app.call_from_thread │
│                                                       │
│    cancel() -> None                                   │
│      → service.cancel()                               │
│                                                       │
│    is_running -> bool                                 │
│      → service.is_running                             │
│                                                       │
│    get_history() -> list                              │
│      → service.get_history()                          │
│                                                       │
│    close() -> None                                    │
│      → cancel() + service cleanup                     │
│                                                       │
│    start_new_conversation() -> None                   │
│      → service.reset_conversation()                   │
└──────────────────────────────────────────────────────┘
```

### 3.3 View Layer

```
┌──────────────────────────────────────────────────────┐
│                 react_screen.py                       │
│                ReactTUIScreen                         │
│            extends BaseAgentXScreen                   │
├──────────────────────────────────────────────────────┤
│  BINDINGS:                                            │
│    q → quit, escape → back, ctrl+enter → send         │
│                                                       │
│  Fields:                                              │
│    _is_streaming: bool = False                        │
│    _streaming_widget: ChatMessage | None = None       │
│    _streaming_text: str = ""                          │
│                                                       │
│  compose() -> ComposeResult                           │
│    → Header(clock) + Container(#react-container)      │
│      → ScrollableContainer(#react-messages)           │
│      → Horizontal(#react-input-section) → Input       │
│    → Footer                                           │
│                                                       │
│  on_mount()                                           │
│    → start_new_conversation()                         │
│    → show welcome message                             │
│    → focus #react-input                               │
│                                                       │
│  on_input_submitted(event)                            │
│    → action_send()                                    │
│                                                       │
│  action_send()                                        │
│    → Get input text, clear field                      │
│    → show_user_message(text)                          │
│    → self._controller.send_message(text)              │
│                                                       │
│  show_user_message(text)                              │
│    → Mount ChatMessage(text, role="user")             │
│    → Scroll to bottom                                 │
│                                                       │
│  show_thinking(text)                                  │
│    → Mount Static(text, classes="react-thinking")     │
│    → Prefix: "💭 "                                    │
│    → Scroll to bottom                                 │
│                                                       │
│  show_tool_call(name, args)                           │
│    → Mount Static(text, classes="react-tool-call")    │
│    → Prefix: "🔧 "                                    │
│    → Scroll to bottom                                 │
│                                                       │
│  show_tool_result(name, result)                       │
│    → Mount Static(text, classes="react-tool-result")  │
│    → Prefix: "📊 "                                    │
│    → Scroll to bottom                                 │
│                                                       │
│  show_answer_chunk(text)                              │
│    → If not streaming: create ChatMessage widget      │
│    → Append to _streaming_text                        │
│    → Update widget                                    │
│    → Scroll to bottom                                 │
│                                                       │
│  show_answer_final()                                  │
│    → Reset streaming state                            │
│                                                       │
│  show_error(text)                                     │
│    → Mount Static(text, classes="react-error")        │
│    → safe_error()                                     │
│                                                       │
│  on_unmount()                                         │
│    → super().on_unmount()                             │
│    → self._controller.cancel() if running             │
└──────────────────────────────────────────────────────┘
```

---

## 4. Threading Model

```
┌─────────────┐                    ┌──────────────────┐
│  UI Thread   │                    │  Worker Thread    │
│  (Textual)   │                    │  (daemon)         │
├──────────────┤                    ├──────────────────┤
│              │                    │                  │
│  action_send │──── spawn ────────▶│  _run_agent()    │
│              │                    │                  │
│              │  ◀── call_from ────│  on_reasoning()  │
│  show_thinking│   thread          │                  │
│              │                    │  on_tool_call()  │
│              │  ◀── call_from ────│                  │
│  show_tool   │   thread          │  on_tool_result()│
│              │                    │                  │
│              │  ◀── call_from ────│  on_answer()     │
│  show_chunk  │   thread          │                  │
│              │                    │  on_done()       │
│              │  ◀── call_from ────│                  │
│  show_final  │   thread          │                  │
│              │                    │  [thread exits]  │
│              │                    │                  │
│  Escape/q    │──── cancel ───────▶│  _cancel_event   │
│              │                    │  .is_set() →     │
│              │                    │  break loop      │
└──────────────┘                    └──────────────────┘
```

**Critical rules (learned from chat screen bugs):**
1. Use `self.app.call_from_thread(callback, *args)` — NOT `self.call_from_thread()` (Screen doesn't have it).
2. Worker thread is daemon (`daemon=True`) so it dies with the process.
3. `on_unmount()` calls `super().on_unmount()` then cancels the agent.

---

## 5. MVC++ Compliance

| Rule | How we comply |
|------|---------------|
| View must not import Model | `react_screen.py` imports only from `agentx.ui.tui.framework` and Textual. No `agentx.model` imports. |
| Controller imports Model + View interface | `react_controller.py` imports `ReactAgentService` (Model) and `IReactView` (View ABC, via duck-typing). |
| Abstract Partner is ABC | `IReactViewPartner(ABC)` with `@abstractmethod` in `interfaces.py`. |
| View receives partner via constructor | `ReactTUIScreen.__init__(controller: IReactViewPartner)`. |
| No SQL in Controller | No SQL anywhere — ReAct uses in-memory checkpointer. |
| `register_partner` for metaclass conflict | `register_partner(IReactViewPartner, ReactTUIScreen)` at module level. |

---

## 6. LLM Provider Compatibility

The `ReactAgentService.__init__()` accepts a `BaseChatModel` instance. The
controller obtains it via:

```python
from agentx.model.ai.service import AIService
llm = AIService().get_current_llm()
```

This returns the user's selected provider's LLM (OpenRouter, OpenAI, Gemini,
NVIDIA, Ollama, or LlamaCpp). All are `BaseChatModel` subclasses, which is
what `create_agent(model=...)` expects.

**Fallback:** If `get_current_llm()` raises (no provider configured, API key
missing), the controller catches the exception and the View shows an error
message. The screen remains usable — the user can go back, select a model
(`m`), and return.
