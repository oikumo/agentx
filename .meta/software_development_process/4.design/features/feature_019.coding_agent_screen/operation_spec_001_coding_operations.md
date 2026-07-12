# Operation Specifications: Coding Agent Screen (feature_019)

## OP-1: Open Coding Screen
**Actor**: User  
**Trigger**: Press 'd' key or click "💻 Coding" button on Main screen  
**Controller**: `MainController.show_coding()`  
**View**: `MainTUIScreen.action_open_coding()` → `navigate_to_child(CodingTUIScreen, ...)`

**Precondition**: Main screen active, MainController instantiated  
**Postcondition**: CodingTUIScreen pushed, CodingController created/wired

**Steps**:
1. User presses 'd' or clicks "💻 Coding" button
2. `MainTUIScreen.action_open_coding()` called
3. `navigate_to_child(CodingTUIScreen, controller=main_ctrl, setup=show_coding, getter=get_coding_controller)`
4. `MainController.show_coding()` creates `CodingController` if not exists (C5 pattern)
5. `CodingTUIScreen` mounts, `on_mount()` wires controller with app/view, starts new conversation
6. Welcome message displayed, input focused

---

## OP-2: Send User Message
**Actor**: User  
**Trigger**: Type message in input + press Ctrl+Enter  
**View**: `CodingTUIScreen.action_send()`  
**Controller**: `CodingController.send_message(user_message: str) → bool`

**Precondition**: Coding screen active, agent not running (`!is_running`)  
**Postcondition**: User message shown, agent started on background thread

**Steps**:
1. `action_send()` reads input value, strips whitespace
2. If empty, return
3. Clear input
4. `show_user_message(text)` → mounts ChatMessage(role="user")
5. If controller exists: `controller.send_message(text)`
6. Controller checks `service.is_running` — if True, return False
7. Controller clears `_cancel_event`, spawns daemon thread `_run_agent(message)`
8. Thread calls `service.stream_agent(...)` with callbacks
9. Return True

---

## OP-3: Stream Agent (Worker Thread)
**Actor**: Controller (background thread)  
**Trigger**: `send_message()` spawned thread  
**Model**: `CodingAgentService.stream_agent(user_message, callbacks...)`

**Precondition**: Agent not running, valid LLM configured  
**Postcondition**: Streaming events delivered to View via `app.call_from_thread`, final `on_done` or `on_error`

**Callback Flow**:
```
stream_agent(user_message, 
    on_reasoning=lambda t: marshal(view.show_thinking, t),
    on_tool_call=lambda n,a: marshal(view.show_tool_call, n, a),
    on_tool_result=lambda n,r: marshal(view.show_tool_result, n, r),
    on_answer=lambda t: marshal(view.show_answer_chunk, t),
    on_done=lambda: marshal(view.show_answer_final),
    on_error=lambda e: marshal(view.show_error, e)
)
```

**Streaming Loop** (inside `stream_agent`):
1. Set `_is_running = True`
2. Prepare agent input: `{"messages": [{"role": "user", "content": user_message}]}`
3. Config: `{"configurable": {"thread_id": self._thread_id}}`
4. Stream: `self._agent.stream_events(input, config, version="v3")`
5. For each event in `stream.messages`:
   - Check `_cancel_event.is_set()` → break
   - For each `delta` in `message.reasoning`: `on_reasoning(delta)`
   - For each `delta` in `message.text`: `on_answer(delta)`
   - For each tool_call in `message.tool_calls.get()`: `on_tool_call(name, str(args))`
6. For each event in `stream.tool_calls`:
   - Check `_cancel_event.is_set()` → break
   - `on_tool_result(name, output)` or `on_tool_result(name, f"Error: {error}")`
7. If not cancelled: `on_done()`
8. Except Exception as e: `on_error(str(e))`
9. Finally: `_is_running = False`, `_cancel_event.clear()`

**Marshalling** (controller `_run_agent`):
```python
def marshal(fn, *args):
    if app is not None:
        app.call_from_thread(fn, *args)
    elif view is not None:
        fn(*args)  # test fallback
```

---

## OP-4: Cancel Running Agent
**Actor**: User  
**Trigger**: Press Escape while agent running (`is_running == True`)  
**View**: `CodingTUIScreen.action_back()` → checks `controller.is_running` → `controller.cancel()`  
**Controller**: `CodingController.cancel()` → `service.cancel()`

**Precondition**: Agent running (`is_running == True`)  
**Postcondition**: Agent stops, `is_running == False`, error shown "Cancelled"

**Steps**:
1. `action_back()` sees `self._controller.is_running`
2. Calls `self._controller.cancel()`
3. Controller calls `self._service.cancel()` → `self._cancel_event.set()`
4. Worker thread's `stream_agent` loop checks `_cancel_event.is_set()` each iteration
5. Loop breaks, `on_error("Cancelled")` or `on_done()` not called
6. Finally block: `_is_running = False`, `_cancel_event.clear()`
7. View receives `show_error("Cancelled")` via marshal

---

## OP-5: File Search Tool
**Tool**: `file_search(pattern: str, path: str = ".") → FileSearchResult`  
**Model**: `CodingAgentService` includes this tool in `_tools` list

**Implementation** (in `coding_tools.py`):
```python
@tool
def file_search(pattern: str, path: str = ".") -> FileSearchResult:
    """Search for files matching a glob pattern within the sandbox.
    
    Args:
        pattern: Glob pattern (e.g., "**/*.py", "src/**/test_*.py")
        path: Relative path from sandbox root (default: ".")
    
    Returns:
        FileSearchResult with matches (path, line, context), total count, truncated flag.
    """
    # Resolve path within sandbox_root
    sandbox_root = get_sandbox_root()  # from controller/service config
    target = (sandbox_root / path).resolve()
    if not target.is_relative_to(sandbox_root):
        return FileSearchResult([], 0, False, error="Path escapes sandbox")
    
    matches = []
    for file_path in target.rglob(pattern):
        if file_path.is_file():
            try:
                content = file_path.read_text(encoding="utf-8")
                for i, line in enumerate(content.splitlines(), 1):
                    if fnmatch.fnmatch(line, f"*{pattern.replace('*', '')}*"):  # simplified
                        # Get context lines
                        start = max(0, i - 4)
                        end = min(len(content.splitlines()), i + 3)
                        context = "\n".join(content.splitlines()[start:end])
                        matches.append(FileMatch(
                            path=str(file_path.relative_to(sandbox_root)),
                            line=i,
                            context=context
                        ))
                        if len(matches) >= 100:
                            break
            except Exception:
                pass
        if len(matches) >= 100:
            break
    
    return FileSearchResult(
        matches=matches,
        total=len(matches),
        truncated=len(matches) >= 100
    )
```

**Safety**: Path resolved relative to `sandbox_root`; `..` and absolute paths rejected.

---

## OP-6: File Read Tool
**Tool**: `file_read(path: str, start: int = 1, end: int = -1) → FileReadResult`

**Implementation**:
```python
@tool
def file_read(path: str, start: int = 1, end: int = -1) -> FileReadResult:
    """Read a file from the sandbox with optional line range.
    
    Args:
        path: Relative path from sandbox root
        start: 1-indexed start line (default: 1)
        end: 1-indexed end line inclusive (default: -1 = EOF)
    
    Returns:
        FileReadResult with content, line range, or error.
    """
    sandbox_root = get_sandbox_root()
    target = (sandbox_root / path).resolve()
    if not target.is_relative_to(sandbox_root):
        return FileReadResult(path, "", 0, 0, error="Path escapes sandbox")
    
    if not target.exists():
        return FileReadResult(path, "", 0, 0, error="File not found")
    
    if not target.is_file():
        return FileReadResult(path, "", 0, 0, error="Not a file")
    
    try:
        lines = target.read_text(encoding="utf-8").splitlines()
        total_lines = len(lines)
        start_idx = max(0, start - 1)
        end_idx = total_lines if end == -1 else min(total_lines, end)
        content = "\n".join(lines[start_idx:end_idx])
        return FileReadResult(
            path=path,
            content=content,
            start_line=start_idx + 1,
            end_line=end_idx
        )
    except Exception as e:
        return FileReadResult(path, "", 0, 0, error=str(e))
```

---

## OP-7: File Edit Tool
**Tool**: `file_edit(path: str, old_str: str, new_str: str) → FileEditResult`

**Implementation**:
```python
@tool
def file_edit(path: str, old_str: str, new_str: str) -> FileEditResult:
    """Make a precise edit to a file. old_str must match exactly once.
    
    Args:
        path: Relative path from sandbox root
        old_str: Exact text to replace (must be unique in file)
        new_str: Replacement text
    
    Returns:
        FileEditResult with success, unified diff, or error.
    """
    sandbox_root = get_sandbox_root()
    target = (sandbox_root / path).resolve()
    if not target.is_relative_to(sandbox_root):
        return FileEditResult(path, False, error="Path escapes sandbox")
    
    if not target.exists():
        return FileEditResult(path, False, error="File not found")
    
    try:
        content = target.read_text(encoding="utf-8")
        # Count occurrences
        count = content.count(old_str)
        if count == 0:
            return FileEditResult(path, False, error="old_str not found in file")
        if count > 1:
            return FileEditResult(path, False, error="old_str matches multiple locations; be more specific")
        
        new_content = content.replace(old_str, new_str, 1)
        # Atomic write
        temp = target.with_suffix(target.suffix + ".tmp")
        temp.write_text(new_content, encoding="utf-8")
        temp.replace(target)
        
        # Generate unified diff
        import difflib
        diff = "\n".join(difflib.unified_diff(
            content.splitlines(), new_content.splitlines(),
            fromfile=f"a/{path}", tofile=f"b/{path}", lineterm=""
        ))
        return FileEditResult(path, True, diff=diff)
    except Exception as e:
        return FileEditResult(path, False, error=str(e))
```

---

## OP-8: File List Tool
**Tool**: `file_list(path: str = ".", recursive: bool = False) → list[DirectoryEntry]`

**Implementation**:
```python
@tool
def file_list(path: str = ".", recursive: bool = False) -> list[DirectoryEntry]:
    """List directory contents within the sandbox.
    
    Args:
        path: Relative path from sandbox root (default: ".")
        recursive: Whether to recurse into subdirectories
    
    Returns:
        List of DirectoryEntry (name, is_dir, size, mtime, relative_path)
    """
    sandbox_root = get_sandbox_root()
    target = (sandbox_root / path).resolve()
    if not target.is_relative_to(sandbox_root):
        return [DirectoryEntry("", False, 0, datetime.min, "", error="Path escapes sandbox")]
    
    if not target.exists() or not target.is_dir():
        return [DirectoryEntry("", False, 0, datetime.min, "", error="Not a directory")]
    
    entries = []
    try:
        if recursive:
            for root, dirs, files in os.walk(target):
                for d in dirs:
                    p = Path(root) / d
                    rel = p.relative_to(sandbox_root)
                    stat = p.stat()
                    entries.append(DirectoryEntry(d, True, stat.st_size, 
                        datetime.fromtimestamp(stat.st_mtime), str(rel)))
                for f in files:
                    p = Path(root) / f
                    rel = p.relative_to(sandbox_root)
                    stat = p.stat()
                    entries.append(DirectoryEntry(f, False, stat.st_size,
                        datetime.fromtimestamp(stat.st_mtime), str(rel)))
        else:
            for p in target.iterdir():
                rel = p.relative_to(sandbox_root)
                stat = p.stat()
                entries.append(DirectoryEntry(p.name, p.is_dir(), stat.st_size,
                    datetime.fromtimestamp(stat.st_mtime), str(rel)))
    except Exception as e:
        entries.append(DirectoryEntry("", False, 0, datetime.min, "", error=str(e)))
    
    return entries
```

---

## OP-9: File Create Tool
**Tool**: `file_create(path: str, content: str) → FileEditResult`

**Implementation**:
```python
@tool
def file_create(path: str, content: str) -> FileEditResult:
    """Create a new file in the sandbox.
    
    Args:
        path: Relative path from sandbox root
        content: File content
    
    Returns:
        FileEditResult with success and diff (new file).
    """
    sandbox_root = get_sandbox_root()
    target = (sandbox_root / path).resolve()
    if not target.is_relative_to(sandbox_root):
        return FileEditResult(path, False, error="Path escapes sandbox")
    
    if target.exists():
        return FileEditResult(path, False, error="File already exists; use file_edit")
    
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        diff = f"--- /dev/null\n+++ b/{path}\n@@ -0,0 +1,{len(content.splitlines())} @@\n"
        diff += "\n".join(f"+{line}" for line in content.splitlines())
        return FileEditResult(path, True, diff=diff)
    except Exception as e:
        return FileEditResult(path, False, error=str(e))
```

---

## OP-10: Start New Conversation
**Actor**: User  
**Trigger**: Press Ctrl+N  
**View**: `CodingTUIScreen.action_new_conversation()`  
**Controller**: `CodingController.start_new_conversation()` → `service.reset_conversation()`

**Precondition**: Any state  
**Postcondition**: New thread_id, messages cleared, welcome shown

**Steps**:
1. `action_new_conversation()` called
2. `controller.start_new_conversation()` → `service.reset_conversation()`
3. Service: `_cancel_event.set()`, `_thread_id = uuid.uuid4()`, `_cancel_event.clear()`
4. View: Clear `#coding-messages` container, show welcome message
5. Focus input

---

## OP-11: Close Screen (Return to Main)
**Actor**: User  
**Trigger**: Press 'q' or Escape (when not running)  
**View**: `CodingTUIScreen.action_back()` or `action_quit()`  
**Controller**: No explicit call (screen pops, controller stays alive)

**Precondition**: Coding screen active, agent not running  
**Postcondition**: Main screen visible, conversation preserved in controller

**Steps**:
1. `action_back()` calls `self.app.pop_screen()` (BaseAgentXScreen)
2. Screen `on_unmount()` calls `super().on_unmount()` → cancels any running task
3. Controller remains in `MainController._coding_controller`
4. Re-opening via OP-1 reuses same controller (C5 pattern)

---

## OP-12: Show Tool Result with Diff Highlighting
**Trigger**: `file_edit` or `file_create` tool returns `FileEditResult` with diff  
**View**: `CodingTUIScreen.show_tool_result(name, result)` parses diff, applies syntax highlighting

**Implementation**:
```python
def show_tool_result(self, name: str, result: str) -> None:
    """Display tool result; if result contains unified diff, highlight it."""
    def _do_mount():
        try:
            container = self.query_one("#coding-messages", ScrollableContainer)
            # Check if result looks like a diff
            if result.startswith("--- ") and "+++ " in result:
                # Render with diff highlighting
                widget = Static(result, classes="coding-tool-result coding-diff")
            else:
                widget = Static(f"📊 {result}", classes="coding-tool-result")
            container.mount(widget)
            self.call_later(container.scroll_end, animate=False)
        except Exception:
            pass
    self.call_later(_do_mount)
```

**CSS** (add to DEFAULT_CSS):
```css
CodingTUIScreen .coding-diff {
    font-family: monospace;
    white-space: pre;
}
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

## OP-13: Show Thinking/Reasoning
**Trigger**: `on_reasoning` callback from streaming  
**View**: `show_thinking(text: str)` → mounts Static with class "coding-thinking"

---

## OP-14: Show Tool Call
**Trigger**: `on_tool_call` callback  
**View**: `show_tool_call(name, args)` → mounts Static with class "coding-tool-call"

---

## OP-15: Show Streaming Answer
**Trigger**: `on_answer` callback (per token/delta)  
**View**: `show_answer_chunk(text)` → creates/updates ChatMessage(role="assistant")  
**Final**: `show_answer_final()` → resets streaming state

---

*Operations complete. Ready for Programming phase.*