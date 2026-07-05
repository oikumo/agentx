# Operation Spec 001 — TUI Nonblocking Runner

> **Phase:** Design — `omt_agent_guide.md §10` | **Feature:** feature_014.tui_nonblocking_runner
> **Design:** `design_001_nonblocking_runner.md`

## O1: `BaseAgentXScreen.run_blocking(func, on_result, on_error)`

```
Operation: Run a blocking callable on a daemon worker thread; deliver the
           result (or exception) to the UI thread via callbacks.

Preconditions:
  - The screen is mounted (has an app context for set_timer).
  - func is a callable taking no arguments and returning Any.
  - on_result / on_error are optional callbacks taking (Any) / (Exception).

Exceptions:
  - func raises: the exception is caught on the worker thread, put on the
    queue as _MsgError, and delivered to on_error on the UI thread.
  - on_result / on_error raises: caught by _deliver's try/except; the poller
    continues. The exception is silently swallowed (callbacks must be robust).
  - set_timer fails (no app context): _schedule_poll swallows it; polling
    stops. The worker still finishes (result discarded).

Postconditions:
  - A TaskHandle is returned and tracked in self._task_handles.
  - A daemon worker thread is running func (or about to start).
  - The UI thread is free (not blocked).
  - On completion, on_result(result) or on_error(exc) is called exactly once
    on the UI thread — UNLESS the task was cancelled or the screen unmounted
    (in which case no callback fires).
```

## O2: `TaskHandle.cancel()`

```
Operation: Signal the worker to stop and suppress callbacks.

Preconditions:
  - The task handle was returned by run_blocking().
  - The worker may or may not have finished.

Exceptions:
  - None. cancel() is idempotent — calling it multiple times is a no-op.

Postconditions:
  - _stop_evt is set (the worker checks it before starting func).
  - _cancelled is True (the poller suppresses on_result / on_error).
  - If the worker is mid-flight in a blocking call, it cannot be interrupted;
    it will finish, but its result is discarded (no callback).
  - If the worker has not started yet, it returns without calling func.
```

## O3: `TaskHandle.is_done` (property)

```
Operation: Check whether the worker has finished.

Preconditions:
  - The task handle was returned by run_blocking().

Exceptions:
  - None.

Postconditions:
  - Returns True after the worker's _worker_loop exits (func returned, raised,
    or the worker was cancelled before starting).
  - Returns False while the worker is running func.
  - Does NOT indicate whether on_result was called (callback may be suppressed
    if cancelled/unmounted).
```

## O4: `BaseAgentXScreen.on_unmount()`

```
Operation: Cancel all active blocking tasks when the screen is popped.

Preconditions:
  - Textual calls on_unmount when the screen is removed from the stack.

Exceptions:
  - None. Each handle.cancel() is wrapped (it never raises).

Postconditions:
  - Every active TaskHandle has cancel() called → _stop_evt set, _cancelled True.
  - Every runner's _unmounted flag is set → poller exits without callbacks.
  - _task_handles is cleared.
  - Workers are daemon threads → they do not block process exit.
  - No callback fires on the now-unmounted screen.
```

## O5: `BlockingTaskRunner._poll()` (internal)

```
Operation: Drain the worker→UI queue and deliver results/errors, then re-schedule.

Preconditions:
  - _poll is scheduled on the UI thread via set_timer(0.05, ...).

Exceptions:
  - queue.Empty: normal — no message available; re-schedule if not done.
  - _deliver raises: caught inside _deliver; poller continues.

Postconditions:
  - All available messages are drained from the queue.
  - _MsgResult → on_result(value) called (unless cancelled/unmounted).
  - _MsgError → on_error(error) called (unless cancelled/unmounted).
  - None (sentinel) → worker is done; note _done.
  - If _done is False, _poll is re-scheduled via set_timer(0.05, ...).
  - If _done is True, no re-schedule (final result already delivered).
  - If _unmounted is True, _poll returns immediately without draining.
```

## Screen operations (refactored)

## O6: `AgentTUIScreen.action_run_cycle()`

```
Operation: Run one agent cycle without freezing the UI.

Preconditions:
  - A controller is connected.
  - No cycle is already in flight (or a new one is acceptable — concurrent
    cycles are allowed but the user should not spam 'r').

Exceptions:
  - Controller.run_cycle raises: delivered to _on_cycle_error → logged in red.
  - Rendering raises: caught in _on_cycle_result → logged in red.

Postconditions:
  - A worker thread is running run_cycle().
  - The UI is responsive (user can press Escape, type commands).
  - On completion, the cycle result (decision, action, reflection) is rendered
    in the activity log, and the status bar + goal tree are refreshed.
```

## O7: `AgentTUIScreen.action_save()`

```
Operation: Save a session snapshot without stalling the UI.

Preconditions:
  - A controller is connected.

Exceptions:
  - save_snapshot raises: delivered to _on_save_error → logged in red.

Postconditions:
  - A worker thread is running save_snapshot().
  - On completion, the snapshot ID is logged in green.
```

## O8: `AgentDemoScreen.action_run_cycle()`

```
Operation: Run one demo cycle without freezing the UI.

Preconditions:
  - A controller is connected.

Exceptions:
  - run_cycle raises: delivered to _on_cycle_error → logged in red.

Postconditions:
  - A worker thread is running run_cycle().
  - On completion, the cycle result is rendered via _render_cycle_result,
    and the status bar + summary panel are refreshed.
```
