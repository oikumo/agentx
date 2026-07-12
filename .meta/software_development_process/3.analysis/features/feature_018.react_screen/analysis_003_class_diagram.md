# Analysis 003 — ReAct Screen Class Diagram (Analysis Level)

**Feature:** feature_018.react_screen  
**Phase:** Analysis  
**Date:** 2026-07-11

---

## Analysis Class Diagram

```
┌─────────────────────────────────────┐     ┌──────────────────────────────────────┐
│         ReactAgentService           │     │           ReactController            │
│  (Model Layer)                      │     │  (Controller Layer)                  │
├─────────────────────────────────────┤     ├──────────────────────────────────────┤
│ - _agent: CompiledStateGraph        │◄────│ - _service: ReactAgentService        │
│ - _checkpointer: InMemorySaver      │     │ - _thread_id: str                    │
│ - _thread_id: str                   │     │ - _is_running: bool                  │
│ - _llm: BaseChatModel               │     │ - _cancel_event: threading.Event     │
│ - _tools: list[BaseTool]            │     │ - view: IReactView                   │
├─────────────────────────────────────┤     ├──────────────────────────────────────┤
│ + __init__(llm, tools, system_prompt)│    │ + __init__(service)                  │
│ + stream_agent(messages, on_reasoning,│    │ + send_message(text)                 │
│   on_tool_call, on_tool_result,       │    │ + cancel()                           │
│   on_answer, on_done, on_error)       │    │ + is_running: bool                   │
│ + get_history() -> list              │     │ + get_history() -> list              │
│ + cancel()                           │     │ + close()                            │
│ + reset_conversation()               │     │ + start_new_conversation()           │
└─────────────────────────────────────┘     └──────────────────────────────────────┘
                                                          ▲
                                                          │ implements
                                            ┌─────────────┴────────────┐
                                            │  IReactViewPartner       │
                                            │  (ABC)                   │
                                            ├──────────────────────────┤
                                            │ + send_message(text)     │
                                            │ + cancel()               │
                                            │ + is_running: bool       │
                                            │ + get_history() -> list  │
                                            │ + close()                │
                                            │ + start_new_conversation()│
                                            └──────────────────────────┘
                                                          ▲
                                                          │ calls (via partner)
┌─────────────────────────────────────┐                    │
│          ReactTUIScreen             │────────────────────┘
│  (View Layer)                       │
├─────────────────────────────────────┤
│ - _controller: IReactViewPartner    │
│ - _is_streaming: bool               │
│ - _streaming_widget: ChatMessage|None│
│ - _streaming_text: str              │
│ - _worker_thread: Thread|None       │
├─────────────────────────────────────┤
│ + compose() -> ComposeResult        │
│ + on_mount()                        │
│ + on_input_submitted(event)         │
│ + action_send()                     │
│ + action_back()                     │
│ + show_user_message(text)           │
│ + show_thinking(text)               │
│ + show_tool_call(name, args)        │
│ + show_tool_result(name, result)    │
│ + show_answer_chunk(text)           │
│ + show_answer_final(text)           │
│ + show_error(text)                  │
│ + start_streaming_answer()          │
│ + on_unmount()                      │
└─────────────────────────────────────┘
```

---

## Key Concepts

### ReactAgentService (Model)
- Wraps LangChain's `create_agent()` — creates a CompiledStateGraph (ReAct agent).
- Uses `InMemorySaver` checkpointer so conversation history persists across turns via `thread_id`.
- Provides `stream_agent()` — a synchronous generator that uses `agent.stream_events(version="v3")` to yield typed events:
  - `message.reasoning` → reasoning deltas (thinking)
  - `message.tool_calls` → tool call chunks
  - `stream.tool_calls` → tool execution lifecycle (name, input, output)
  - `message.text` → final answer text deltas
- Uses callbacks (not return values) so the caller (controller) can route events to the View on the UI thread.
- `cancel()` sets a threading.Event that the streaming loop checks.

### ReactController (Controller)
- Implements `IReactViewPartner` (ABC) — the View's abstract partner.
- Owns a `ReactAgentService` instance and a `thread_id` for conversation continuity.
- `send_message(text)`:
  1. Appends user message to agent state.
  2. Spawns a background thread that calls `service.stream_agent()`.
  3. Routes callbacks to the View via `self.app.call_from_thread()`.
- `cancel()` stops an in-progress agent run.
- `start_new_conversation()` resets the thread_id for a fresh conversation.

### ReactTUIScreen (View)
- Extends `BaseAgentXScreen` (TUI framework).
- Displays four types of content: user messages, thinking blocks, tool calls/results, and streamed answers.
- Uses a background thread for the agent invocation (streaming requires synchronous `stream_events`).
- Marshals UI updates via `self.app.call_from_thread()` (NOT `self.call_from_thread`).
- `on_unmount()` calls `super().on_unmount()` to cancel blocking tasks.

### IReactViewPartner (Abstract Partner)
- ABC interface that the View calls to interact with the Controller.
- Methods: `send_message`, `cancel`, `is_running`, `get_history`, `close`, `start_new_conversation`.
