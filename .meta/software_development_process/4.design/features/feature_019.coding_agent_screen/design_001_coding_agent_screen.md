# Design: Coding Agent Screen (feature_019)

## 1. Overview

This document specifies the detailed design for the **Coding Agent Screen** — a TUI screen that provides a ReAct-style chat interface where the AI agent can search, read, edit, and create files in the user's workspace. It follows the exact same MVC++ architecture as the ReAct Screen (feature_018).

**Key design principle**: Reuse the ReAct screen's architecture 1:1, replacing the tool set (calculator, time) with file operations tools (search, read, edit, list, create).

---

## 2. File Structure

```
src/agentx/
├── model/
│   └── coding/
│       ├── __init__.py
│       ├── coding_agent_service.py      # Model: LangChain agent + tools
│       └── coding_tools.py              # File tools (search, read, edit, list, create)
├── ui/
│   ├── interfaces.py                    # ADD: ICodingViewPartner interface
│   └── tui/
│       └── screens/
│           ├── coding/
│           │   ├── __init__.py
│           │   ├── coding_controller.py  # Controller
│           │   └── coding_screen.py      # View (TUI)
│           └── react_screen.py           # Reference (unchanged)
└── tests/
    ├── model/
    │   └── coding/
    │       ├── test_coding_agent_service.py
    │       └── test_coding_tools.py
    └── ui/
        └── tui/
            └── screens/
                └── coding/
                    ├── test_coding_controller.py
                    └── test_coding_screen.py
```

---

## 3. Class Diagrams

### 3.1 Model Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                   CodingAgentService                            │
├─────────────────────────────────────────────────────────────────┤
│ - _llm: BaseChatModel                                           │
│ - _tools: list[BaseTool]                                        │
│ - _system_prompt: str                                           │
│ - _checkpointer: InMemorySaver                                  │
│ - _thread_id: str                                               │
│ - _cancel_event: threading.Event                                │
│ - _is_running: bool                                             │
├─────────────────────────────────────────────────────────────────┤
│ + __init__(llm?, tools?, system_prompt?)                        │
│ + stream_agent(user_message, callbacks...) → None               │
│ + cancel() → None                                               │
│ + reset_conversation() → None                                   │
│ + get_history() → list                                          │
│ + is_running: bool (property)                                   │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CodingTools (module)                       │
├─────────────────────────────────────────────────────────────────┤
│ + file_search(pattern: str, path?: str) → FileSearchResult      │
│ + file_read(path: str, start?: int, end?: int) → FileReadResult │
│ + file_edit(path: str, old_str: str, new_str: str)              │
│     → FileEditResult                                            │
│ + file_list(path: str, recursive?: bool) → list[DirectoryEntry] │
│ + file_create(path: str, content: str) → FileEditResult         │
│                                                                 │
│ (each is a @tool decorated function using sandbox_root)        │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Controller Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                    CodingController                             │
│                    (implements ICodingViewPartner)              │
├─────────────────────────────────────────────────────────────────┤
│ - _service: CodingAgentService                                  │
│ - _worker_thread: Thread | None                                 │
│ - _app: Any                                                     │
│ - _view: Any                                                    │
├─────────────────────────────────────────────────────────────────┤
│ + send_message(user_message: str) → bool                        │
│ + cancel() → None                                               │
│ + is_running: bool (property)                                   │
│ + get_history() → list                                          │
│ + close() → None                                                │
│ + start_new_conversation() → None                               │
│ + set_app(app: Any) → None                                      │
│ + set_view(view: Any) → None                                    │
│ + _run_agent(message: str, view: Any) → None                    │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 View Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                    CodingTUIScreen                              │
│                    (extends BaseAgentXScreen)                   │
├─────────────────────────────────────────────────────────────────┤
│ - _controller: ICodingViewPartner                               │
│ - _is_streaming: bool                                           │
│ - _streaming_text: str                                          │
│ - _streaming_widget: ChatMessage | None                         │
│ - _is_mounted: bool                                             │
├─────────────────────────────────────────────────────────────────┤
│ + compose() → ComposeResult                                     │
│ + on_mount() → None                                             │
│ + show_user_message(text: str) → None                           │
│ + show_thinking(text: str) → None                               │
│ + show_tool_call(name: str, args: str) → None                   │
│ + show_tool_result(name: str, result: str) → None               │
│ + show_answer_chunk(text: str) → None                           │
│ + show_answer_final() → None                                    │
│ + show_error(text: str) → None                                  │
│ + action_send() → None                                          │
│ + action_back() → None                                          │
│ + action_new_conversation() → None                              │
│ + on_unmount() → None                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Interface Definition (Add to `src/agentx/ui/interfaces.py`)

```python
class ICodingViewPartner(ABC):
    """Abstract partner for Coding View (implemented by CodingController).

    The TUI View calls these methods to interact with the Controller.
    Registered as virtual subclass via register_partner() to avoid
    Textual/ABC metaclass conflict.
    """

    @abstractmethod
    def send_message(self, user_message: str) -> bool:
        """Send a user message to the Coding agent.

        Args:
            user_message: The user's input text.

        Returns:
            True if accepted (agent started), False if agent is busy.
        """
        pass

    @abstractmethod
    def cancel(self) -> None:
        """Cancel an in-progress agent run."""
        pass

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """Whether the agent is currently running."""
        pass

    @abstractmethod
    def get_history(self) -> list:
        """Get the conversation message history."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the controller and cancel any running agent."""
        pass

    @abstractmethod
    def start_new_conversation(self) -> None:
        """Start a new conversation (reset thread)."""
        pass
```

---

## 5. Operation Specifications

### OP-1: Open Coding Screen
**Trigger**: User presses 'd' key or clicks "💻 Coding" button on Main screen  
**Controller**: `MainController.show_coding()`  
**View**: `MainTUIScreen.action_open_coding()`  
**Flow**:
```
MainTUIScreen.action_open_coding()
  → navigate_to_child(CodingTUIScreen, controller=main._controller, 
                      setup=lambda c: c.show_coding(),
                      getter=lambda c: c.get_coding_controller())
MainController.show_coding()
  → if _coding_controller is None: _coding_controller = CodingController()
  → (no view creation needed; TUI screen creates its own view)
```

### OP-2: Send Message
**Trigger**: User types message + presses Ctrl+Enter  
**View**: `CodingTUIScreen.action_send()`  
**Controller**: `CodingController.send_message(str) → bool`  
**Flow**:
```
action_send()
  → input = query_one("#coding-input").value.strip()
  → if not input: return
  → input.value = ""
  → show_user_message(input)
  → if controller: controller.send_message(input)
```

### OP-3: Stream Agent (Worker Thread)
**Controller**: `CodingController._run_agent()` (runs on daemon thread)  
**Model**: `CodingAgentService.stream_agent(callbacks...)`  
**Callbacks** (marshalled via `app.call_from_thread`):
- `on_reasoning(str)` → `view.show_thinking()`
- `on_tool_call(name, args)` → `view.show_tool_call()`
- `on_tool_result(name, result)` → `view.show_tool_result()`
- `on_answer(str)` → `view.show_answer_chunk()`
- `on_done()` → `view.show_answer_final()`
- `on_error(str)` → `view.show_error()`

### OP-4: Cancel Agent
**Trigger**: User presses Escape while agent running  
**View**: `action_back()` (checks `controller.is_running`)  
**Controller**: `cancel()` → `service.cancel()` → sets `_cancel_event`  
**Model**: `stream_agent` loop checks `_cancel_event.is_set()` each iteration

### OP-5: File Search Tool
**Tool**: `file_search(pattern: str, path: str = ".") → FileSearchResult`  
**Implementation**:
- Resolve `path` relative to `sandbox_root`
- Use `pathlib.Path.rglob(pattern)` or `grep`-style search
- Return matches with line numbers and context (3 lines before/after)
- Limit to 100 results, set `truncated` flag if more

### OP-6: File Read Tool
**Tool**: `file_read(path: str, start: int = 1, end: int = -1) → FileReadResult`  
**Implementation**:
- Resolve path within sandbox
- Read file, return lines `[start-1:end]` (1-indexed, inclusive)
- If `end == -1`, read to EOF
- Return content with line numbers

### OP-7: File Edit Tool
**Tool**: `file_edit(path: str, old_str: str, new_str: str) → FileEditResult`  
**Implementation**:
- Resolve path within sandbox
- Read file content
- Find **exact** match of `old_str` (must be unique)
- Replace with `new_str`
- Write back atomically (write to temp, rename)
- Return unified diff

### OP-8: File List Tool
**Tool**: `file_list(path: str = ".", recursive: bool = False) → list[DirectoryEntry]`  
**Implementation**:
- Resolve path within sandbox
- `os.scandir()` or `Path.iterdir()`
- For each entry: name, is_dir, size, mtime
- If recursive, recurse into subdirectories

### OP-9: File Create Tool
**Tool**: `file_create(path: str, content: str) → FileEditResult`  
**Implementation**:
- Resolve path within sandbox
- Create parent directories if needed
- Write content (fail if exists, unless override flag)
- Return success + diff (new file)

### OP-10: New Conversation
**Trigger**: User presses Ctrl+N  
**View**: `action_new_conversation()`  
**Controller**: `start_new_conversation()` → `service.reset_conversation()`  
**View**: Clear messages, show welcome

---

## 6. Data Models (dataclasses)

```python
# In coding_agent_service.py or separate types.py
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

@dataclass
class FileMatch:
    path: str           # Relative to sandbox root
    line: int           # 1-indexed line number
    context: str        # Matching line ±3 context lines

@dataclass
class FileSearchResult:
    matches: list[FileMatch]
    total: int
    truncated: bool

@dataclass
class FileReadResult:
    path: str
    content: str
    start_line: int
    end_line: int
    error: Optional[str] = None

@dataclass
class FileEditResult:
    path: str
    success: bool
    diff: Optional[str] = None
    error: Optional[str] = None

@dataclass
class DirectoryEntry:
    name: str
    is_dir: bool
    size: int
    mtime: datetime
    path: str  # Relative to sandbox root
```

---

## 7. System Prompt for Coding Agent

```python
DEFAULT_CODING_SYSTEM_PROMPT = (
    "You are a coding assistant that helps users explore, understand, and modify "
    "codebases. You have access to file system tools:\n\n"
    "• file_search(pattern, path?) — find files matching a glob pattern\n"
    "• file_read(path, start?, end?) — read a file (with optional line range)\n"
    "• file_edit(path, old_str, new_str) — make a precise edit (old_str must match exactly)\n"
    "• file_list(path?, recursive?) — list directory contents\n"
    "• file_create(path, content) — create a new file\n\n"
    "Workflow:\n"
    "1. Understand the user's request\n"
    "2. Use file_search/file_list to explore the codebase\n"
    "3. Use file_read to examine relevant files\n"
    "4. Use file_edit to make changes (or file_create for new files)\n"
    "5. Verify changes with file_read\n\n"
    "Always prefer reading files before editing. Show your reasoning (thinking) "
    "before each tool call. Make minimal, focused edits."
)
```

---

## 8. Main Controller Integration

Add to `MainController` (`src/agentx/ui/screens/main/main_controller.py`):

```python
# In __init__:
self._coding_controller: "CodingController | None" = None

# New methods:
def show_coding(self) -> None:
    """Create and wire a CodingController for the Coding screen."""
    if self._coding_controller is not None:
        return
    from agentx.ui.tui.screens.coding.coding_controller import CodingController
    self._coding_controller = CodingController()

def get_coding_controller(self) -> "CodingController | None":
    """Get the Coding controller for screen connection."""
    return self._coding_controller
```

Add to `MainTUIScreen` (`src/agentx/ui/tui/screens/main_screen.py`):

```python
# In BINDINGS:
Binding("d", "open_coding", "Coding", show=True),

# In MenuGrid (widgets.py) - add 7th button:
yield Button("💻 Coding", id="btn-coding", variant="primary")

# In on_button_pressed:
elif button_id == "btn-coding":
    self.action_open_coding()

# New action:
def action_open_coding(self) -> None:
    from agentx.ui.tui.screens.coding.coding_screen import CodingTUIScreen
    self.navigate_to_child(
        CodingTUIScreen,
        controller=self._controller,
        setup=lambda c: c.show_coding() if hasattr(c, "show_coding") else None,
        getter=lambda c: (
            c.get_coding_controller()
            if hasattr(c, "get_coding_controller")
            else None
        ),
    )
```

---

## 9. CSS Design (CodingTUIScreen)

```css
CodingTUIScreen {
    layout: vertical;
}

CodingTUIScreen #coding-container {
    height: 1fr;
    padding: 1;
}

CodingTUIScreen #coding-main-area {
    width: 1fr;
    height: 1fr;
    layout: vertical;
}

CodingTUIScreen #coding-messages {
    height: 1fr;
    border: solid $primary;
    padding: 1;
    margin-bottom: 1;
    overflow-y: auto;
}

CodingTUIScreen #coding-input-section {
    height: auto;
    dock: bottom;
}

CodingTUIScreen #coding-input-section Input {
    width: 100%;
}

/* Thinking blocks — dimmed/italic */
CodingTUIScreen .coding-thinking {
    color: $text-muted;
    text-style: italic;
    padding: 0 2;
    margin: 0 0 1 0;
    width: 100%;
}

/* Tool call blocks — distinct background */
CodingTUIScreen .coding-tool-call {
    background: $surface;
    color: $accent;
    padding: 0 2;
    margin: 0 0 0 0;
    width: 100%;
}

/* Tool result blocks */
CodingTUIScreen .coding-tool-result {
    background: $surface-darken-1;
    color: $success;
    padding: 0 2;
    margin: 0 0 1 0;
    width: 100%;
}

/* Error blocks */
CodingTUIScreen .coding-error {
    color: $error;
    text-style: bold;
    padding: 0 2;
    margin: 0 0 1 0;
    width: 100%;
}

/* File diff highlight */
CodingTUIScreen .coding-diff-add {
    color: $success;
    background: $success-darken-3;
}
CodingTUIScreen .coding-diff-remove {
    color: $error;
    background: $error-darken-3;
}
```

---

## 10. Test Plan Summary

| Layer | Test File | Key Tests |
|-------|-----------|-----------|
| Model | `test_coding_agent_service.py` | stream_agent callbacks, cancel, reset_conversation, history, tool integration |
| Model | `test_coding_tools.py` | file_search, file_read, file_edit, file_list, file_create (sandbox enforcement) |
| Controller | `test_coding_controller.py` | send_message, cancel, is_running, get_history, start_new_conversation, thread marshalling |
| View | `test_coding_screen.py` | compose, on_mount, all show_* methods, action_send, action_back, action_new_conversation |
| Integration | `test_coding_integration.py` | Full cycle: open → send → tool calls → answer → cancel → new conversation |
| MVC++ | `test_mvc_compliance.py` | No Model imports in View, Controller implements interface, no SQL in View/Controller |

---

## 11. Dependencies

| Dependency | Purpose | Already in project? |
|------------|---------|---------------------|
| `langchain-core` | BaseChatModel, BaseTool, create_agent | Yes (feature_018) |
| `langgraph` | InMemorySaver, create_agent | Yes (feature_018) |
| `textual` | TUI framework | Yes |
| `pathlib` | Sandbox path resolution | Stdlib |
| `difflib` | Unified diff for edits | Stdlib |

---

## 12. Traceability to Analysis

| Analysis Artifact | Design Section |
|-------------------|----------------|
| Use Cases (UC-1..9) | §5 Operation Specs |
| Class Diagram | §3 Class Diagrams |
| Sequence Diagrams | §5 OP-2, OP-3, OP-4 |
| Data Dictionary | §6 Data Models |
| State Diagram | §5 OP-2/OP-4 (IDLE ↔ RUNNING) |
| NFRs | §5 (threading, sandbox, streaming) |
| Architecture Decisions | §2, §3, §8 (reuse React pattern) |
| Risk Assessment | §5 (sandbox enforcement, threading) |

---

## 13. Implementation Order

1. **Model**: `coding_tools.py` → `coding_agent_service.py`
2. **Interface**: Add `ICodingViewPartner` to `interfaces.py`
3. **Controller**: `coding_controller.py`
4. **View**: `coding_screen.py`
5. **Integration**: `MainController.show_coding()`, `MainTUIScreen.action_open_coding()`, MenuGrid button
6. **Registration**: `register_partner(ICodingViewPartner, CodingTUIScreen)` in coding_screen.py
7. **Tests**: All layers (TDD: testlist → red → green → refactor → done)

---

*Design complete. Ready for Programming phase (TDD).*