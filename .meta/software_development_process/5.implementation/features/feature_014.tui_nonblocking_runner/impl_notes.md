# Implementation Notes — feature_014.tui_nonblocking_runner

> **Phase:** Programming | **Feature:** feature_014.tui_nonblocking_runner
> **Design:** `design_001_nonblocking_runner.md` | **Operation spec:** `operation_spec_001_nonblocking_runner.md`

## 1. Files created

| File | Purpose |
|------|---------|
| `src/agentx/ui/tui/framework/async_runner.py` | `BlockingTaskRunner` + `TaskHandle` + `_MsgResult` / `_MsgError` |

## 2. Files modified

| File | Change |
|------|--------|
| `src/agentx/ui/tui/framework/base_screen.py` | +`_task_handles` list in `__init__`; +`run_blocking()` method; +`on_unmount()` override (cancels all handles) |
| `src/agentx/ui/tui/framework/__init__.py` | Export `BlockingTaskRunner`, `TaskHandle` |
| `src/agentx/agent/view/tui/agent_screen.py` | `action_run_cycle()` → `run_blocking()` + `_on_cycle_result` / `_on_cycle_error`; `action_save()` → `run_blocking()` + `_on_save_result` / `_on_save_error` |
| `src/agentx/agent/view/tui/demo_screen.py` | `action_run_cycle()` → `run_blocking()` + `_on_cycle_result` / `_on_cycle_error` |
| `src/agentx/agent/view/tui/fast_agent_modals.py` | `RunningModal.on_unmount()` → calls `super().on_unmount()` first (cleanup chain) |

## 3. Implementation details

### 3.1 BlockingTaskRunner (`async_runner.py`)

- **Worker thread**: daemon `threading.Thread` running `_worker_loop`.
- **Queue**: `queue.Queue` for worker→UI communication. Three message types:
  - `_MsgResult(value)` — func returned successfully.
  - `_MsgError(error)` — func raised an exception.
  - `None` (sentinel) — worker has exited (put in `finally`).
- **Poller**: `_poll()` scheduled on the UI thread via `screen.set_timer(0.05, ...)`.
  Drains the queue, calls `_deliver()` for each message, re-schedules if `not _done`.
- **Cancellation**: `cancel()` sets `_stop_evt` + `_cancelled = True`. Worker checks
  `_stop_evt` before starting `func`. Mid-flight calls can't be interrupted (Python
  threads); their results are discarded by the `_cancelled` check in `_deliver`.
- **Unmount safety**: `on_unmount` sets `_unmounted = True` on each runner + calls
  `cancel()`. The poller checks `_unmounted` at the top and returns without callbacks.

### 3.2 BaseAgentXScreen integration (`base_screen.py`)

- `__init__` gains `self._task_handles: list[Any] = []`.
- `run_blocking(func, on_result, on_error) -> TaskHandle`: creates a
  `BlockingTaskRunner`, wraps it in a `TaskHandle`, appends to `_task_handles`,
  calls `runner.start()`, returns the handle.
- `on_unmount()`: iterates `_task_handles`, sets `_unmounted` + `cancel()` on each,
  clears the list. Subclasses overriding `on_unmount` must call `super().on_unmount()`.

### 3.3 Screen refactors

**AgentTUIScreen.action_run_cycle** — before: synchronous `self._controller.run_cycle()`
blocking the UI thread. After: `self.run_blocking(self._controller.run_cycle,
on_result=self._on_cycle_result, on_error=self._on_cycle_error)`. The rendering logic
(decision/action/reflection) moved to `_on_cycle_result`, which runs on the UI thread.

**AgentTUIScreen.action_save** — same pattern: `save_snapshot()` runs via
`run_blocking`, result/error delivered to `_on_save_result` / `_on_save_error`.

**AgentDemoScreen.action_run_cycle** — same pattern as AgentTUIScreen.

**RunningModal.on_unmount** — added `super().on_unmount()` call at the top so the
base class cleanup runs (cancels any `run_blocking` handles — none today, but
future-proof). The modal's own worker/queue/poll logic is unchanged.

## 4. MVC++ compliance

- `async_runner.py`: pure View — no `agentx.model.*` import. `func`, `on_result`,
  `on_error` are all `Callable[..., Any]`. The `screen` ref is duck-typed `Any`.
- `base_screen.py`: `run_blocking` imports `BlockingTaskRunner` / `TaskHandle` lazily
  (inside the method) to avoid circular imports.
- `mvc_check.py`: 0 errors, 0 warnings on all 8 framework files + 6 agent view files.

## 5. Test results (pre-testing-phase)

- Existing suite: 640 passed, 1 pre-existing failure (`test_llm_initialization_attempted`,
  unrelated to feature_014 — never touched `ChatTUIScreen`).
- feature_011 freeze-fix tests: all 4 `TestRunningModalFreezeFix` pass (the
  `super().on_unmount()` change didn't break the modal).
- feature_012 framework tests: all pass.
