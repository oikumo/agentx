# Design — ReAct Screen Sequence Diagrams

**Feature:** feature_018.react_screen  
**Phase:** Design  
**Date:** 2026-07-11

---

## Sequence 1: Send Message (no tool call)

```
User        ReactTUIScreen     ReactController    ReactAgentService     LangChain Agent
 │                │                   │                   │                    │
 │  Ctrl+Enter    │                   │                   │                    │
 │───────────────▶│                   │                   │                    │
 │                │ action_send()     │                   │                    │
 │                │ show_user_message │                   │                    │
 │                │ (mount ChatMsg)   │                   │                    │
 │                │                   │                   │                    │
 │                │ send_message(text)│                   │                    │
 │                │──────────────────▶│                   │                    │
 │                │                   │ spawn worker ────▶│                    │
 │                │                   │                   │ stream_agent()     │
 │                │                   │                   │───────────────────▶│
 │                │                   │                   │                    │
 │                │                   │                   │  message.reasoning │
 │                │                   │                   │◀───────────────────│
 │                │                   │                   │ on_reasoning(t)    │
 │                │ show_thinking(t)  │◀──────────────────│                    │
 │                │ (call_from_thread)│                   │                    │
 │                │                   │                   │                    │
 │                │                   │                   │  message.text      │
 │                │                   │                   │◀───────────────────│
 │                │                   │                   │ on_answer(chunk)   │
 │                │ show_answer_chunk │◀──────────────────│                    │
 │                │ (call_from_thread)│                   │                    │
 │                │                   │                   │  ...more chunks... │
 │                │                   │                   │                    │
 │                │                   │                   │  stream.output     │
 │                │                   │                   │◀───────────────────│
 │                │                   │                   │ on_done()          │
 │                │ show_answer_final │◀──────────────────│                    │
 │                │ (call_from_thread)│                   │                    │
 │                │                   │                   │ [thread exits]     │
```

---

## Sequence 2: Send Message (with tool call)

```
User        ReactTUIScreen     ReactController    ReactAgentService     LangChain Agent
 │                │                   │                   │                    │
 │  "What is      │                   │                   │                    │
 │   15% of 240?" │                   │                   │                    │
 │───────────────▶│                   │                   │                    │
 │                │ action_send()     │                   │                    │
 │                │ show_user_message │                   │                    │
 │                │ send_message(text)│                   │                    │
 │                │──────────────────▶│                   │                    │
 │                │                   │ spawn worker ────▶│                    │
 │                │                   │                   │ stream_agent()     │
 │                │                   │                   │───────────────────▶│
 │                │                   │                   │                    │
 │                │                   │                   │  message.reasoning │
 │                │                   │                   │◀───────────────────│
 │                │ show_thinking(…)  │◀── on_reasoning ──│                    │
 │                │                   │                   │                    │
 │                │                   │                   │  message.tool_calls│
 │                │                   │                   │◀───────────────────│
 │                │                   │                   │ (model emits       │
 │                │                   │                   │  calculator call)  │
 │                │                   │                   │                    │
 │                │                   │                   │  stream.tool_calls │
 │                │                   │                   │  (tool executes)   │
 │                │                   │                   │◀───────────────────│
 │                │ show_tool_call(   │◀── on_tool_call──│                    │
 │                │  "calculator",    │                   │                    │
 │                │  "240*0.15")      │                   │                    │
 │                │ show_tool_result( │◀── on_tool_result│                    │
 │                │  "calculator",    │                   │                    │
 │                │  "36.0")          │                   │                    │
 │                │                   │                   │                    │
 │                │                   │                   │  message.reasoning │
 │                │                   │                   │◀───────────────────│
 │                │ show_thinking(…)  │◀── on_reasoning ──│                    │
 │                │                   │                   │                    │
 │                │                   │                   │  message.text      │
 │                │                   │                   │◀───────────────────│
 │                │ show_answer_chunk │◀── on_answer ─────│                    │
 │                │                   │                   │  …                 │
 │                │                   │                   │  on_done()         │
 │                │ show_answer_final │◀──────────────────│                    │
```

---

## Sequence 3: Cancel During Agent Run

```
User        ReactTUIScreen     ReactController    ReactAgentService
 │                │                   │                   │
 │  Escape        │                   │                   │
 │───────────────▶│                   │                   │
 │                │ action_back()     │                   │
 │                │ on_unmount()      │                   │
 │                │ super().on_unmount│                   │
 │                │ cancel()          │                   │
 │                │──────────────────▶│ cancel()          │
 │                │                   │──────────────────▶│
 │                │                   │                   │ _cancel_event.set()
 │                │                   │                   │
 │                │                   │                   │ [streaming loop
 │                │                   │                   │  checks event,
 │                │                   │                   │  breaks, returns]
 │                │                   │                   │
 │                │ pop_screen()      │                   │
 │                │                   │                   │ [thread exits
 │                │                   │                   │  cleanly]
```
