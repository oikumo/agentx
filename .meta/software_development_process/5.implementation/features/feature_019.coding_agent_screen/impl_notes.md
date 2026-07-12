# Implementation Notes: Coding Agent Screen (feature_019)

## Summary

Implemented a **Coding Agent Screen** — a TUI chat interface where an AI agent can search, read, edit, and create files in the user's workspace. Follows the exact same MVC++ architecture as the ReAct Screen (feature_018).

## Files Created

### Model Layer
- `src/agentx/model/coding/coding_tools.py` — 5 file system tools with sandbox enforcement:
  - `file_search(pattern, path?)` — glob pattern search within sandbox
  - `file_read(path, start?, end?)` — read file with optional line range
  - `file_edit(path, old_str, new_str)` — precise edit (old_str must match exactly once)
  - `file_list(path?, recursive?)` — directory listing
  - `file_create(path, content)` — create new file
  - All tools use `_resolve_safe_path()` to prevent sandbox escape

- `src/agentx/model/coding/coding_agent_service.py` — LangChain agent wrapper:
  - Uses `create_agent` with file tools + InMemorySaver checkpointer
  - Streaming via `stream_events(version="v3")` with callbacks
  - Cancellation via threading.Event checked each delta

### Interface
- Added `ICodingViewPartner` to `src/agentx/ui/interfaces.py`

### Controller
- `src/agentx/ui/tui/screens/coding/coding_controller.py` — Implements `ICodingViewPartner`:
  - Spawns daemon worker thread for `stream_agent`
  - Marshals callbacks via `app.call_from_thread()`

### View
- `src/agentx/ui/tui/screens/coding/coding_screen.py` — `CodingTUIScreen`:
  - Header, scrollable messages, input with Ctrl+Enter
  - Displays: thinking (💭), tool calls (🔧), tool results (📊), streaming answer
  - Diff highlighting for file_edit/file_create results
  - Keybindings: Ctrl+Enter (send), Esc (back/cancel), Ctrl+N (new), q (quit)
  - Registered as virtual subclass via `register_partner()`

### Integration
- `MainController.show_coding()` / `get_coding_controller()` (C5 reuse pattern)
- `MainTUIScreen.action_open_coding()` with 'd' binding + 💻 button in MenuGrid
- MenuGrid updated to 8 buttons (added Coding with variant="success")

## Tests

### Model Tests (21 tests, all passing)
`tests/model/coding/test_coding_tools.py`:
- Sandbox root management (2)
- FileSearch (5): finds .py files, subdir patterns, context, sandbox escape, nonexistent
- FileRead (4): full file, line range, sandbox escape, nonexistent
- FileEdit (4): exact replace, not found, multiple matches, sandbox escape
- FileList (3): non-recursive, recursive, sandbox escape
- FileCreate (4): new file, exists, parent dirs, sandbox escape

### Main Screen Tests (updated)
- MenuGrid: 8 buttons, correct IDs, variants (Coding uses "success")
- Bindings: 10 bindings (added 'd' for Coding)
- Help text: includes 'd' - Coding
- Button handlers: btn-coding triggers action_open_coding

## Architecture Compliance

- **MVC++**: 0 errors, 33 warnings (baseline)
  - View imports no Model
  - Controller uses interfaces (ICodingViewPartner)
  - No SQL in View/Controller
- **Non-blocking**: Uses `BaseAgentXScreen.run_blocking()` (feature_014)
- **Sandbox**: All file ops confined to `sandbox_root` (session working dir)

## Test Results

```
tests/model/coding/test_coding_tools.py: 21 passed
tests/tui/test_main_screen.py: 76 passed
Full suite: 910 passed, 6 pre-existing failures
```

## Pre-existing Failures (Unrelated)
- TDD enforcement gate tests (feature_016)
- React screen pilot tests (feature_018)
- OMT harness test (test_tdd_check.py)

All 6 failures existed before this feature.