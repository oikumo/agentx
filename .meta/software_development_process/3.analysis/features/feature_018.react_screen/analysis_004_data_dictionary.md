# Analysis 004 — ReAct Screen Data Dictionary

**Feature:** feature_018.react_screen  
**Phase:** Analysis  
**Date:** 2026-07-11

---

## Data Entities

### 1. Conversation Thread (in-memory)

| Field | Type | Description |
|-------|------|-------------|
| `thread_id` | `str` | UUID7 string identifying the conversation. Used by LangGraph checkpointer. |
| `messages` | `list[BaseMessage]` | Accumulated message history (System, Human, AI, Tool). Managed by the checkpointer. |
| `created_at` | `datetime` | When the conversation was started. |

**Persistence:** In-memory only (InMemorySaver). Not persisted to disk — the ReAct screen is for live interactive sessions. If the user closes the screen, the conversation is lost (by design — same as the chat screen's non-DB fallback).

---

### 2. Streaming Event Types

Events yielded by `agent.stream_events(version="v3")`:

| Event | Projection | Content | UI Action |
|-------|-----------|---------|-----------|
| **Reasoning delta** | `message.reasoning` | `str` — a chunk of the model's reasoning | Append to thinking block |
| **Text delta** | `message.text` | `str` — a chunk of the final answer | Append to streaming answer |
| **Tool call (model)** | `message.tool_calls` | `dict` — tool name + args being generated | Show tool call block |
| **Tool call (exec)** | `stream.tool_calls` | `ToolCallExecution` — tool_name, input, output, error | Show tool result block |
| **Final state** | `stream.output` | `dict` — final agent state with all messages | Update conversation history |

---

### 3. Built-in Tools

| Tool | Module | Args | Returns | Description |
|------|--------|------|---------|-------------|
| `calculator` | `react_tools.py` | `expression: str` | `str` (result) | Safely evaluates a math expression (e.g., "2+2", "15% of 240" → "240*0.15"). Uses `ast.literal_eval` with a whitelist of allowed operations. |
| `get_current_time` | `react_tools.py` | (none) | `str` | Returns current date/time in ISO format. |

---

### 4. ReactAgentService Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `llm` | `BaseChatModel` | `AIService().get_current_llm()` | The LLM to use for the agent. |
| `tools` | `list[BaseTool]` | `[calculator, get_current_time]` | Tools available to the agent. |
| `system_prompt` | `str` | `"You are a helpful AI assistant..."` | System prompt for the agent. |
| `checkpointer` | `Checkpointer` | `InMemorySaver()` | LangGraph checkpointer for conversation history. |

---

### 5. ReactController State

| Field | Type | Description |
|-------|------|-------------|
| `_thread_id` | `str` | Current conversation thread ID. |
| `_is_running` | `bool` | Whether an agent run is in progress. |
| `_cancel_event` | `threading.Event` | Set to cancel an in-progress run. |
| `_worker_thread` | `Thread \| None` | The background thread running the agent. |

---

### 6. ReactTUIScreen State

| Field | Type | Description |
|-------|------|-------------|
| `_is_streaming` | `bool` | Whether the answer is currently streaming. |
| `_streaming_widget` | `ChatMessage \| None` | The widget being updated during streaming. |
| `_streaming_text` | `str` | Accumulated answer text. |
| `_worker_thread` | `Thread \| None` | Background thread for agent invocation. |
