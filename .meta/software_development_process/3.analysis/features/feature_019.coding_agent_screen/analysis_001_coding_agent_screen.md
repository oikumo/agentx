# Analysis: Coding Agent Screen (feature_019)

## 1. Use Cases

### UC-1: Open Coding Agent Screen
**Actor**: User  
**Trigger**: Press 'k' key or click "💻 Coding" button on Main Screen  
**Precondition**: Main screen is visible  
**Postcondition**: Coding Agent screen is displayed with empty conversation  
**Main Flow**:
1. User presses 'k' or clicks "💻 Coding" button
2. MainController.show_coding() creates CodingController if not exists
3. MainTUIScreen.navigate_to_child() pushes CodingTUIScreen
4. Screen mounts, shows welcome message, focuses input

### UC-2: Send Message to Coding Agent
**Actor**: User  
**Trigger**: Type message and press Ctrl+Enter  
**Precondition**: Coding Agent screen is active, agent not running  
**Postcondition**: User message displayed, agent response streaming begins  
**Main Flow**:
1. User types message in input field
2. User presses Ctrl+Enter
3. Screen.action_send() validates input, shows user message
4. Screen calls controller.send_message(message)
5. Controller spawns worker thread, calls service.stream_agent()
6. Service streams events: reasoning, tool_calls, tool_results, answer chunks
7. Controller marshals callbacks to UI thread via app.call_from_thread()
8. Screen displays each event type appropriately

### UC-3: Agent Searches Files
**Actor**: System (agent via tool)  
**Trigger**: Agent calls `file_search` tool  
**Precondition**: Agent is running, file_search tool available  
**Postcondition**: Search results displayed in chat  
**Main Flow**:
1. Agent decides to search files, emits tool call
2. Controller receives on_tool_call("file_search", args)
3. Service executes file_search tool (grep/glob patterns)
4. Tool returns matching file paths with context snippets
5. Controller receives on_tool_result, marshals to view
6. View shows tool call + results in distinct styling

### UC-4: Agent Reads File Content
**Actor**: System (agent via tool)  
**Trigger**: Agent calls `file_read` tool  
**Precondition**: Agent is running, file_read tool available  
**Postcondition**: File content displayed in chat  
**Main Flow**:
1. Agent calls file_read(path, optional start_line, end_line)
2. Service reads file from filesystem (with sandbox restrictions)
3. Returns file content (or error if outside sandbox)
4. View displays tool result with syntax highlighting

### UC-5: Agent Edits File
**Actor**: System (agent via tool)  
**Trigger**: Agent calls `file_edit` tool  
**Precondition**: Agent is running, file_edit tool available  
**Postcondition**: File modified, diff shown in chat  
**Main Flow**:
1. Agent calls file_edit(path, old_string, new_string)
2. Service validates path within sandbox, applies edit
3. Returns success/diff or error
4. View shows tool call + result with diff highlighting

### UC-6: Agent Lists Directory
**Actor**: System (agent via tool)  
**Trigger**: Agent calls `file_list` tool  
**Precondition**: Agent is running  
**Postcondition**: Directory tree displayed  
**Main Flow**:
1. Agent calls file_list(path, recursive?)
2. Service lists directory contents (respecting sandbox)
3. Returns structured tree
4. View displays as formatted tree

### UC-7: Cancel Running Agent
**Actor**: User  
**Trigger**: Press Escape or Ctrl+C while agent running  
**Precondition**: Agent is running (is_running = True)  
**Postcondition**: Agent cancelled, UI responsive  
**Main Flow**:
1. User presses Escape
2. Screen.action_back() calls controller.cancel()
3. Service.cancel() sets cancel_event
4. Worker thread checks event, stops streaming
5. Controller.is_running becomes False

### UC-8: Close Screen and Return to Main
**Actor**: User  
**Trigger**: Press 'q' or Escape when not running  
**Precondition**: Coding screen active, agent not running  
**Postcondition**: Main screen visible, conversation preserved  
**Main Flow**:
1. User presses 'q' or Escape
2. Screen.action_quit() or action_back() pops screen
3. Controller remains alive (conversation history preserved)
4. Main screen regains focus

### UC-9: Start New Conversation
**Actor**: User  
**Trigger**: Type "/new" or press Ctrl+N  
**Precondition**: Any state  
**Postcondition**: New empty conversation, thread_id reset  
**Main Flow**:
1. User triggers new conversation
2. Screen calls controller.start_new_conversation()
3. Service.reset_conversation() generates new thread_id
4. Screen clears messages, shows welcome

---

## 2. Class Diagram (MVC++)

```
┌─────────────────────────────────────────────────────────────────┐
│                        VIEW LAYER                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ CodingTUIScreen : BaseAgentXScreen                       │   │
│  │ - _controller: ICodingViewPartner                        │   │
│  │ - _is_streaming: bool                                    │   │
│  │ - _streaming_text: str                                   │   │
│  │ - _streaming_widget: ChatMessage | None                  │   │
│  │ + compose() → ComposeResult                              │   │
│  │ + on_mount()                                             │   │
│  │ + show_user_message(text: str)                           │   │
│  │ + show_thinking(text: str)                               │   │
│  │ + show_tool_call(name: str, args: str)                   │   │
│  │ + show_tool_result(name: str, result: str)               │   │
│  │ + show_answer_chunk(text: str)                           │   │
│  │ + show_answer_final()                                    │   │
│  │ + show_error(text: str)                                  │   │
│  │ + action_send()                                          │   │
│  │ + action_back()                                          │   │
│  │ + on_unmount()                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ▲                                  │
│                              │ calls                            │
│                              │ (interface)                      │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CONTROLLER LAYER                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ CodingController : ICodingViewPartner                    │   │
│  │ - _service: CodingAgentService                           │   │
│  │ - _worker_thread: Thread | None                          │   │
│  │ - _app: Any                                              │   │
│  │ - _view: Any                                             │   │
│  │ + send_message(user_message: str) → bool                 │   │
│  │ + cancel()                                               │   │
│  │ + is_running: bool                                       │   │
│  │ + get_history() → list                                   │   │
│  │ + close()                                                │   │
│  │ + start_new_conversation()                               │   │
│  │ + set_app(app: Any)                                      │   │
│  │ + set_view(view: Any)                                    │   │
│  │ + _run_agent(message: str, view: Any)                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                               ▲
                               │ uses
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        MODEL LAYER                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ CodingAgentService                                       │   │
│  │ - _llm: BaseChatModel                                    │   │
│  │ - _tools: list[BaseTool]                                 │   │
│  │ - _system_prompt: str                                    │   │
│  │ - _checkpointer: InMemorySaver                           │   │
│  │ - _thread_id: str                                        │   │
│  │ - _cancel_event: threading.Event                         │   │
│  │ - _is_running: bool                                      │   │
│  │ + stream_agent(user_message, callbacks...)               │   │
│  │ + cancel()                                               │   │
│  │ + reset_conversation()                                   │   │
│  │ + get_history() → list                                   │   │
│  │ + is_running: bool                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ▲                                  │
│                              │ uses                             │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ CodingTools (file_search, file_read, file_edit,        │   │
│  │                    file_list, file_create)               │   │
│  │ - Sandbox-root enforcement                               │   │
│  │ - Safe path resolution                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Sequence Diagrams

### SD-1: User Sends Message → Agent Responds with Tools

```
User → CodingTUIScreen: type + Ctrl+Enter
CodingTUIScreen → CodingController: send_message("find auth.py")
CodingController → Thread: start(_run_agent)
Thread → CodingAgentService: stream_agent(...)
loop streaming events
    CodingAgentService → Thread: on_reasoning("thinking...")
    Thread → App: call_from_thread(view.show_thinking)
    App → CodingTUIScreen: show_thinking("thinking...")
    
    CodingAgentService → Thread: on_tool_call("file_search", "auth*.py")
    Thread → App: call_from_thread(view.show_tool_call)
    App → CodingTUIScreen: show_tool_call("file_search", "auth*.py")
    
    CodingAgentService → Thread: on_tool_result("file_search", "src/auth.py...")
    Thread → App: call_from_thread(view.show_tool_result)
    App → CodingTUIScreen: show_tool_result("file_search", "src/auth.py...")
    
    CodingAgentService → Thread: on_answer("Found auth.py at...")
    Thread → App: call_from_thread(view.show_answer_chunk)
    App → CodingTUIScreen: show_answer_chunk("Found auth.py...")
end
CodingAgentService → Thread: on_done()
Thread → App: call_from_thread(view.show_answer_final)
App → CodingTUIScreen: show_answer_final()
```

### SD-2: Cancel Running Agent

```
User → CodingTUIScreen: press Escape
CodingTUIScreen → CodingController: cancel()
CodingController → CodingAgentService: cancel()
CodingAgentService: _cancel_event.set()
Thread: checks _cancel_event.is_set() → breaks loop
Thread → App: call_from_thread(view.show_error("Cancelled"))
App → CodingTUIScreen: show_error("Cancelled")
CodingController._service.is_running → False
```

### SD-3: File Edit Tool Execution

```
Agent → CodingAgentService: tool_call("file_edit", {"path": "x.py", "old": "a", "new": "b"})
CodingAgentService → FileEditTool: invoke(args)
FileEditTool → Sandbox: resolve_path("x.py") → /sandbox/x.py
FileEditTool: read file, find "a", replace with "b", write back
FileEditTool → CodingAgentService: result("Edited x.py: -a +b")
CodingAgentService → callbacks: on_tool_result("file_edit", "Edited x.py...")
Controller → View: show_tool_result("file_edit", "Edited x.py...")
```

---

## 4. Data Dictionary

| Entity | Attributes | Description |
|--------|------------|-------------|
| **CodingMessage** | role: str, content: str, timestamp: datetime, type: Enum(user, assistant, thinking, tool_call, tool_result, error) | Single message in conversation |
| **ThreadConfig** | thread_id: str, sandbox_root: Path, llm_provider: str, model: str | Persistent conversation config |
| **FileSearchResult** | matches: list[FileMatch], total: int, truncated: bool | file_search tool output |
| **FileMatch** | path: str, line: int, context: str | Single grep match with context |
| **FileEditResult** | path: str, success: bool, diff: str \| None, error: str \| None | file_edit tool output |
| **FileReadResult** | path: str, content: str, start_line: int, end_line: int, error: str \| None | file_read tool output |
| **DirectoryEntry** | name: str, is_dir: bool, size: int, mtime: datetime | file_list tool output item |

---

## 5. State Diagram (Agent Lifecycle)

```
[IDLE] ──send_message()──▶ [RUNNING]
   ▲                         │
   │                         │ cancel() / done / error
   │                         ▼
   └─────────────────── [IDLE]
         (reset thread_id)
```

- **IDLE**: No agent running, accepts new messages
- **RUNNING**: Agent streaming, rejects new messages, accepts cancel
- Transitions guarded by `_service.is_running` and `_cancel_event`

---

## 6. Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Agent runs on background thread; UI never freezes | P0 |
| NFR-2 | Streaming updates appear within 50ms of callback | P0 |
| NFR-3 | File operations confined to sandbox directory | P0 |
| NFR-4 | Cancellation takes effect within 1 token | P0 |
| NFR-5 | Conversation history persists across screen close/open | P1 |
| NFR-6 | Syntax highlighting for code blocks in tool results | P1 |
| NFR-7 | Support for 100+ file search results without UI lag | P2 |
| NFR-8 | Graceful degradation when LLM unavailable | P2 |

---

## 7. Architecture Decisions

### AD-1: Reuse React Screen Architecture
The Coding Agent screen follows the exact same MVC++ pattern as `feature_018.react_screen`:
- `CodingTUIScreen` extends `BaseAgentXScreen`
- `CodingController` implements `ICodingViewPartner`
- `CodingAgentService` wraps LangChain agent with file tools
- Background thread + `app.call_from_thread()` for UI marshalling

### AD-2: Sandbox-Rooted File Tools
All file tools (`file_search`, `file_read`, `file_edit`, `file_list`, `file_create`) resolve paths relative to a **sandbox root** (session working directory). Absolute paths and `..` traversal are rejected.

### AD-3: Reuse Existing LLM Provider
Use `AIService().get_current_llm()` (from feature_013) so user's selected model provider works automatically.

### AD-4: LangChain Agent with Custom Tools
Use `langchain.agents.create_agent` with:
- Built-in tools: calculator, get_current_time (from react_tools.py)
- New tools: file_search, file_read, file_edit, file_list, file_create
- `InMemorySaver` checkpointer for conversation history

### AD-5: Register as Virtual Subclass
Use `register_partner(ICodingViewPartner, CodingTUIScreen)` to avoid Textual/ABC metaclass conflict (same pattern as React screen).

---

## 8. Operation Specifications

### OP-1: Open Coding Screen
**Controller**: `MainController.show_coding()`  
**View**: `MainTUIScreen.action_open_coding()` → `navigate_to_child(CodingTUIScreen, ...)`

### OP-2: Send Message
**View**: `CodingTUIScreen.action_send()`  
**Controller**: `CodingController.send_message(str) → bool`

### OP-3: Stream Agent
**Controller**: `CodingController._run_agent()` on worker thread  
**Model**: `CodingAgentService.stream_agent(callbacks...)`

### OP-4: Cancel
**View**: `CodingTUIScreen.action_back()` (when running)  
**Controller**: `CodingController.cancel()`

### OP-5: File Search Tool
**Model**: `FileSearchTool.invoke(pattern: str, path?: str) → FileSearchResult`

### OP-6: File Read Tool
**Model**: `FileReadTool.invoke(path: str, start?: int, end?: int) → FileReadResult`

### OP-7: File Edit Tool
**Model**: `FileEditTool.invoke(path: str, old_str: str, new_str: str) → FileEditResult`

### OP-8: File List Tool
**Model**: `FileListTool.invoke(path: str, recursive?: bool) → list[DirectoryEntry]`

### OP-9: File Create Tool
**Model**: `FileCreateTool.invoke(path: str, content: str) → FileEditResult`

### OP-10: New Conversation
**View**: `action_new_conversation()` (Ctrl+N)  
**Controller**: `start_new_conversation()` → `service.reset_conversation()`

---

## 9. Traceability Matrix

| Use Case | Operation Spec | Class | Test |
|----------|----------------|-------|------|
| UC-1 | OP-1 | MainController.show_coding, CodingTUIScreen | test_open_coding_screen |
| UC-2 | OP-2, OP-3 | CodingController.send_message, CodingAgentService.stream_agent | test_send_message_streams |
| UC-3 | OP-5 | FileSearchTool | test_file_search_tool |
| UC-4 | OP-6 | FileReadTool | test_file_read_tool |
| UC-5 | OP-7 | FileEditTool | test_file_edit_tool |
| UC-6 | OP-8 | FileListTool | test_file_list_tool |
| UC-7 | OP-4 | CodingController.cancel | test_cancel_agent |
| UC-8 | — | CodingTUIScreen.action_back | test_close_screen |
| UC-9 | OP-10 | CodingController.start_new_conversation | test_new_conversation |

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| File tool sandbox escape | Low | Critical | Path resolution with `Path.resolve().relative_to(sandbox_root)` |
| UI freeze on large file ops | Medium | High | Run all tools on worker thread; stream results |
| LLM tool call format changes | Medium | Medium | Version-pin langchain; integration tests |
| Conversation history loss | Low | Medium | InMemorySaver persists in controller lifetime |

---

## 11. Open Questions

1. **Tool set scope**: Start with 5 file tools (search, read, edit, list, create) or add more (grep, replace, patch)?
2. **Diff display**: Use Textual's built-in syntax highlighting or custom diff widget?
3. **Multi-file edits**: Support atomic multi-file edits in one tool call?
4. **Session persistence**: Save conversation to SQLite (like ChatHistoryRepository) or keep in-memory only?

---

*Analysis complete. Ready for Design phase.*