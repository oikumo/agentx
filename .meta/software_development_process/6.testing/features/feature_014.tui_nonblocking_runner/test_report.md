# Test Report — feature_014.tui_nonblocking_runner

> **Phase:** Testing | **Feature:** feature_014.tui_nonblocking_runner
> **Design:** `design_001_nonblocking_runner.md` | **Impl:** `impl_notes.md`

## 1. Summary

| Metric | Value |
|--------|-------|
| New tests written | 38 |
| New tests passing | 38 |
| Pre-existing freeze-fix tests still green | 4 (`TestRunningModalFreezeFix`) |
| Full suite (incl. feature_014) | 678 passed, 1 pre-existing failure |
| Pre-existing failure | `test_llm_initialization_attempted` (unchanged, unrelated) |
| MVC++ errors | 0 |
| MVC++ warnings | 1 (pre-existing `rag_screens.py`, untouched) |
| Regressions | 0 |

## 2. Test files

| File | Tests | What it covers |
|------|-------|----------------|
| `test_async_runner.py` | 23 | Unit: `BlockingTaskRunner` (start/result/error/cancel/unmount/concurrency), `TaskHandle`, `BaseAgentXScreen.run_blocking` + `on_unmount` |
| `test_freeze_regression.py` | 7 | Freeze regression: `AgentTUIScreen` (run_cycle off-thread, event-loop responsive, escape during block, save off-thread) + `AgentDemoScreen` (run_cycle off-thread, event-loop responsive) |
| `test_mvc_nonblocking.py` | 8 | MVC++ compliance: no Model imports in runner, `run_blocking`/`on_unmount` on base, modal inheritance, exports, `mvc_check.py` lint |

## 3. Test groups

### 3.1 Unit: BlockingTaskRunner (`test_async_runner.py`)

| Test | What it proves |
|------|----------------|
| `test_start_spawns_daemon_thread` | `func` runs on a different thread (daemon worker), not the caller's thread |
| `test_start_schedules_first_poll` | `start()` schedules `_poll` via `screen.set_timer(POLL_INTERVAL, ...)` |
| `test_result_delivered_via_on_result` | The return value of `func` is delivered to `on_result` on the UI thread |
| `test_none_result_delivered_correctly` | A `None` return value is correctly delivered (not confused with the sentinel) |
| `test_result_delivered_on_ui_thread` | `on_result` runs on the thread that drains the queue (the UI thread), not the worker |
| `test_error_delivered_via_on_error` | An exception in `func` is caught and delivered to `on_error`, not raised |
| `test_on_result_crash_doesnt_crash_poller` | If `on_result` raises, the poller continues (doesn't crash) |
| `test_cancel_before_start_suppresses_callback` | `cancel()` before `start()` → `func` never called, no callback |
| `test_cancel_after_start_suppresses_callback` | `cancel()` after `start()` → callback suppressed (result discarded) |
| `test_cancel_is_idempotent` | Multiple `cancel()` calls are safe |
| `test_cancel_sets_stop_event` | `cancel()` sets `_stop_evt` checked by the worker |
| `test_unmount_suppresses_callbacks` | After `_unmounted=True`, no callbacks fire |
| `test_unmount_stops_polling` | After `_unmounted=True`, `_poll` doesn't re-schedule |
| `test_multiple_runners_concurrently` | Multiple runners run simultaneously without interference |

### 3.2 Unit: TaskHandle (`test_async_runner.py`)

| Test | What it proves |
|------|----------------|
| `test_cancel_delegates` | `TaskHandle.cancel()` delegates to `BlockingTaskRunner.cancel()` |
| `test_is_done_delegates` | `TaskHandle.is_done` delegates to `BlockingTaskRunner.is_done` |
| `test_handle_from_run_blocking` | `BaseAgentXScreen.run_blocking()` returns a `TaskHandle` and tracks it |

### 3.3 Unit: BaseAgentXScreen integration (`test_async_runner.py`)

| Test | What it proves |
|------|----------------|
| `test_run_blocking_tracks_handle` | The handle is appended to `_task_handles` |
| `test_on_unmount_cancels_all_handles` | `on_unmount` cancels every tracked handle + clears the list |
| `test_on_unmount_is_safe_with_no_handles` | `on_unmount` with an empty list is a no-op |

### 3.4 Freeze regression: AgentTUIScreen (`test_freeze_regression.py`)

| Test | What it proves |
|------|----------------|
| `test_run_cycle_runs_off_ui_thread` | `run_cycle` executes on a worker thread, not the UI thread (the freeze fix) |
| `test_event_loop_responsive_during_blocking_cycle` | A UI timer fires while `run_cycle` is blocked (event loop alive) |
| `test_escape_works_while_cycle_blocks` | `on_unmount` during a blocking cycle completes in <0.1s (not ~1.0s) |
| `test_save_runs_off_ui_thread` | `save_snapshot` executes on a worker thread |

### 3.5 Freeze regression: AgentDemoScreen (`test_freeze_regression.py`)

| Test | What it proves |
|------|----------------|
| `test_run_cycle_runs_off_ui_thread` | `run_cycle` executes on a worker thread |
| `test_event_loop_responsive_during_blocking_cycle` | A UI timer fires while `run_cycle` is blocked |

### 3.6 MVC++ compliance (`test_mvc_nonblocking.py`)

| Test | What it proves |
|------|----------------|
| `test_runner_imports_no_model` | `async_runner.py` imports no `agentx.model.*` module (pure View) |
| `test_runner_imports_no_controller` | `async_runner.py` imports no `agentx.agent.controller.*` |
| `test_base_screen_has_run_blocking` | `BaseAgentXScreen.run_blocking` exists |
| `test_base_screen_has_on_unmount` | `BaseAgentXScreen.on_unmount` exists (cleanup) |
| `test_modal_inherits_run_blocking` | `BaseAgentXModalScreen` inherits `run_blocking` |
| `test_modal_inherits_on_unmount` | `BaseAgentXModalScreen` inherits `on_unmount` |
| `test_runner_is_abc_free` | `BlockingTaskRunner` is a plain class (no ABC, Textual metaclass safe) |
| `test_exports_in_framework_init` | `BlockingTaskRunner` + `TaskHandle` exported from the framework package |
| `test_mvc_check_async_runner` | `mvc_check.py` reports 0 errors on `async_runner.py` |

## 4. Pre-existing tests preserved

| Suite | Before | After |
|-------|--------|-------|
| `TestRunningModalFreezeFix` (feature_011) | 4 pass | 4 pass |
| feature_012 framework tests | 62 pass | 62 pass |
| feature_007 TUI agent screen tests | pass | pass |
| Full suite (excl. feature_014) | 640 pass, 1 pre-existing fail | 640 pass, 1 pre-existing fail |

## 5. MVC++ results

```
mvc_check.py src/agentx/ui/tui/ src/agentx/agent/view/tui/
  27 file(s) scanned — 0 error(s), 1 warning(s)
  (warning: rag_screens.py SQL — pre-existing, untouched by feature_014)
```

## 6. Conclusion

The framework-level freeze fix is complete and verified:
- `BlockingTaskRunner` runs blocking callables off the UI thread (proven by thread-id checks).
- The UI event loop stays responsive during blocking calls (proven by timer-fires-during-block tests).
- Cancellation and unmount cleanup work (proven by callback-suppression tests).
- The existing Fast Agent freeze-fix is preserved (4 regression tests green).
- MVC++ 0 errors; the runner is pure View (no Model imports).
- Full suite: 678 passed, 1 pre-existing failure (unchanged).
