# Analysis 001 — ReAct Screen Use Cases

**Feature:** feature_018.react_screen  
**Phase:** Analysis  
**Date:** 2026-07-11

---

## Overview

The ReAct screen provides a chat-like conversation interface where the AI
agent uses LangChain's `create_agent` (ReAct pattern: **Re**asoning +
**Act**ing) to answer user questions. Unlike the plain Chat screen which
sends messages directly to an LLM, the ReAct agent can:

1. **Think** — show its reasoning process (chain-of-thought visible to user)
2. **Act** — call tools (calculator, time, etc.) when it needs information
3. **Observe** — display tool results inline
4. **Respond** — stream the final answer in real-time

---

## Actors

| Actor | Description |
|-------|-------------|
| **User** | The developer using AgentX TUI. Types questions, reads reasoning + answers. |
| **ReAct Agent** | LangChain `create_agent` instance that reasons, calls tools, and responds. |
| **LLM Provider** | The currently selected AI model (via ModelRegistry: OpenRouter, OpenAI, Gemini, NVIDIA, Ollama, LlamaCpp). |

---

## Use Case UC-1: Start ReAct Conversation

**Actor:** User  
**Precondition:** AgentX TUI is running; Main screen is visible.  

**Main flow:**
1. User presses `t` (or clicks 🧠 ReAct button) on the Main screen.
2. System pushes the ReActTUIScreen onto the screen stack.
3. System initializes the ReAct agent with the current LLM provider.
4. System displays a welcome message and focuses the input field.
5. User types a question and presses `Ctrl+Enter`.

**Alternative flows:**
- A1: LLM provider not configured → System shows error: "No AI provider selected. Press 'm' to select a model."
- A2: LLM API key missing → System shows error: "API key not set for {provider}. Check your .env file."

**Postcondition:** ReAct screen is active and ready for conversation.

---

## Use Case UC-2: Ask Question with Reasoning

**Actor:** User  
**Precondition:** ReAct screen is active (UC-1 completed).  

**Main flow:**
1. User types a question in the input field and presses `Ctrl+Enter`.
2. System displays the user's message in the chat area.
3. System starts the ReAct agent on a background thread (non-blocking).
4. Agent reasons about the question → System displays "💭 Thinking: ..." block.
5. If the agent decides no tools are needed:
   - Agent streams the final answer → System displays it token-by-token.
6. System appends the AI message to conversation history.

**Alternative flows:**
- A1: Agent decides to use a tool → continue to UC-3.
- A2: LLM call fails → System shows error message, allows retry.
- A3: User presses `Escape` during streaming → System cancels the agent run.

**Postcondition:** User's question is answered; conversation history updated.

---

## Use Case UC-3: Agent Uses a Tool

**Actor:** ReAct Agent (triggered by User's question)  
**Precondition:** UC-2 step 4 reached; agent decided tool use is needed.  

**Main flow:**
1. Agent emits a tool call (e.g., `calculator(expression="2+2")`).
2. System displays "🔧 Tool: calculator(2+2)" in the chat area.
3. Tool executes and returns a result.
4. System displays "📊 Result: 4" below the tool call.
5. Agent observes the result and reasons again → back to UC-2 step 4.
6. If agent is satisfied, it streams the final answer.

**Alternative flows:**
- A1: Tool execution fails → System shows "⚠️ Tool error: {message}", agent may retry or respond without the tool.
- A2: Agent calls multiple tools in sequence → each call + result is displayed.

**Postcondition:** Tool result is visible; agent continues reasoning.

---

## Use Case UC-4: Multi-turn Conversation

**Actor:** User  
**Precondition:** At least one exchange completed (UC-2 or UC-3).  

**Main flow:**
1. User types a follow-up question.
2. System sends it to the agent with the full conversation history (via checkpointer thread_id).
3. Agent considers prior context, reasons, and responds.
4. System displays reasoning + answer as before.

**Postcondition:** Conversation continues with context preserved.

---

## Use Case UC-5: Quit / Back to Main

**Actor:** User  
**Precondition:** ReAct screen is active.  

**Main flow:**
1. User presses `q` (quit) or `Escape` (back).
2. System cancels any in-progress agent run.
3. System pops the ReAct screen, returning to Main screen.

**Postcondition:** Main screen is visible; ReAct screen resources cleaned up.

---

## Operation List (extracted from use cases)

| # | Operation | Source UC | Layer |
|---|-----------|-----------|-------|
| OP-1 | `open_react_screen()` | UC-1 | MainController → MainTUIScreen |
| OP-2 | `initialize_agent()` | UC-1 | ReactController → ReactAgentService |
| OP-3 | `send_message(text)` | UC-2 | ReactTUIScreen → ReactController |
| OP-4 | `run_agent_stream(messages)` | UC-2 | ReactController → ReactAgentService |
| OP-5 | `show_reasoning(text)` | UC-2 | ReactController → ReactTUIScreen |
| OP-6 | `show_tool_call(name, args)` | UC-3 | ReactController → ReactTUIScreen |
| OP-7 | `show_tool_result(name, result)` | UC-3 | ReactController → ReactTUIScreen |
| OP-8 | `show_answer_stream(text)` | UC-2 | ReactController → ReactTUIScreen |
| OP-9 | `cancel_agent_run()` | UC-2/A3, UC-5 | ReactController → ReactAgentService |
| OP-10 | `get_conversation_history()` | UC-4 | ReactController → ReactAgentService |
| OP-11 | `close_screen()` | UC-5 | ReactTUIScreen → ReactController |
