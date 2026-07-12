# Analysis 005 — ReAct Screen NFRs & Traceability

**Feature:** feature_018.react_screen  
**Phase:** Analysis  
**Date:** 2026-07-11

---

## Non-Functional Requirements

| ID | Category | Requirement | Priority |
|----|----------|-------------|----------|
| NFR-1 | **Performance** | The UI must not freeze during agent execution. All LLM/tool calls run on a background thread; the UI thread polls via `set_timer`. | High |
| NFR-2 | **Responsiveness** | `Escape` / `q` must be responsive at all times, even during a long agent run. Cancel must take effect within 1 poll cycle (50ms). | High |
| NFR-3 | **Streaming** | Answer text must appear token-by-token (not after the full response). Reasoning and tool calls must appear as they happen. | Medium |
| NFR-4 | **Architecture** | MVC++ compliance: View must not import Model. Controller mediates. Abstract Partner is ABC. Enforced by `mvc_check.py`. | High |
| NFR-5 | **Compatibility** | Must work with all 6 registered LLM providers (OpenRouter, OpenAI, Gemini, NVIDIA, Ollama, LlamaCpp) via `AIService.get_current_llm()`. | High |
| NFR-6 | **Extensibility** | New tools can be added by appending to the `tools` list in `ReactAgentService.__init__()` — no View/Controller changes needed. | Medium |
| NFR-7 | **Testability** | Controller and Model must be testable without a running TUI (mock View). View must be testable with mock controller (Textual pilot). | High |
| NFR-8 | **Resource cleanup** | Background thread must be daemon (dies with process). `on_unmount` must cancel active runs. | High |
| NFR-9 | **Error handling** | LLM API errors, tool errors, and provider misconfiguration must be shown as user-friendly messages, not tracebacks. | High |
| NFR-10 | **Conversation continuity** | Multi-turn conversations must preserve context via the checkpointer's `thread_id`. | Medium |

---

## Traceability Matrix

| Requirement / UC | Operation | Design Artifact | Implementation File | Test File |
|-----------------|-----------|-----------------|---------------------|-----------|
| UC-1: Start ReAct | OP-1 open_react_screen | design_001 §3.1 | main_controller.py, main_screen.py, widgets.py | test_react_integration.py |
| UC-1: Init agent | OP-2 initialize_agent | design_001 §3.2 | react_controller.py, react_agent_service.py | test_react_agent_service.py |
| UC-2: Ask question | OP-3 send_message, OP-4 run_agent_stream | design_001 §3.3, seq_001 | react_screen.py, react_controller.py | test_react_screen.py, test_react_controller.py |
| UC-2: Show reasoning | OP-5 show_reasoning | design_001 §3.4 | react_screen.py | test_react_screen.py |
| UC-3: Tool call | OP-6 show_tool_call | design_001 §3.5, seq_002 | react_screen.py, react_controller.py | test_react_controller.py |
| UC-3: Tool result | OP-7 show_tool_result | design_001 §3.5 | react_screen.py | test_react_screen.py |
| UC-2: Stream answer | OP-8 show_answer_stream | design_001 §3.6 | react_screen.py | test_react_screen.py |
| UC-2/A3: Cancel | OP-9 cancel_agent_run | design_001 §3.7 | react_controller.py, react_agent_service.py | test_react_controller.py |
| UC-4: Multi-turn | OP-10 get_history | design_001 §3.8 | react_agent_service.py | test_react_agent_service.py |
| UC-5: Quit/Back | OP-11 close_screen | design_001 §3.9 | react_screen.py | test_react_screen.py |
| NFR-1: No freeze | — | design_001 §4 | react_screen.py (bg thread) | test_react_freeze.py |
| NFR-4: MVC++ | — | design_001 §5 | all files | test_react_mvc.py |
| NFR-5: Providers | — | design_001 §6 | react_agent_service.py | test_react_agent_service.py |
