# Analysis 002 — TUI Nonblocking Runner: Use Cases & Operations

> **Phase:** Analysis — `omt_agent_guide.md §2, §3 (functional path)` | **Feature:** feature_014.tui_nonblocking_runner
> **Task type:** major_feature

## 1. Actors

| Actor | Description |
|-------|-------------|
| **User** | The human pressing keys / clicking buttons in the TUI. |
| **Screen** | A `BaseAgentXScreen` subclass (e.g. `AgentTUIScreen`, `AgentDemoScreen`). |
| **Worker thread** | A daemon `threading.Thread` that runs the blocking callable. |
| **UI thread** | Textual's event loop — the only thread that touches widgets. |

## 2. Use cases

### UC1: Run a single blocking operation without freezing the UI

**Primary actor:** User (pressing `r` or typing `run` on the Agent screen)

**Preconditions:**
- A screen with a controller is mounted.
- The user triggers an action that calls a blocking operation (e.g. `run_cycle`).

**Main flow:**
1. The user presses `r` (or types `run`) on the Agent screen.
2. The screen calls `self.run_blocking(self._controller.run_cycle, on_result=..., on_error=...)`.
3. The framework spawns a daemon worker thread to run `run_cycle()`.
4. The UI thread immediately returns to the event loop — the screen remains responsive.
5. The screen shows a "Running…" indicator (e.g. a log line or status update).
6. When the worker finishes, it puts the result (or exception) on a queue.
7. The UI-thread poller drains the queue and calls `on_result(result)` (or `on_error(exc)`).
8. The screen renders the cycle result (decision, action, reflection) in the activity log.

**Postconditions:**
- The UI was responsive throughout the blocking call (timers fired, keys accepted).
- The result was displayed once, on the UI thread.

**Alternative flows:**
- **A1: Operation raises an exception.** The worker catches it, puts it on the queue as
  an error message. The poller calls `on_error(exc)`. The screen shows an error log line.
- **A2: Screen unmounts during the operation.** `on_unmount` sets the stop event. The
  poller suppresses callbacks. The worker finishes (or is mid-call) and exits; no
  callback fires on the now-gone screen.

---

### UC2: Cancel a running blocking operation

**Primary actor:** User (pressing `Escape` / `Back` / `Stop` during a blocking operation)

**Preconditions:**
- A blocking operation is in progress (UC1 is active).
- The user wants to abort or navigate away.

**Main flow:**
1. The user presses `Escape` (or `Back`).
2. The screen's `action_back` pops the screen → `on_unmount` fires.
3. `on_unmount` calls `task_handle.cancel()` (sets `_stop_evt`).
4. The UI thread immediately proceeds — no waiting for the worker.
5. The worker, on its next checkpoint (or when the blocking call returns), sees
  `_stop_evt` is set and exits.
6. No callback fires on the unmounted screen.

**Postconditions:**
- The UI responded instantly to the cancel (well under the blocking call's duration).
- No zombie thread remains (daemon + stop event).

**Note:** The worker cannot interrupt a blocking `llm.invoke()` mid-call (Python threads
can't be killed). Cancellation is **cooperative**: the stop event is checked before
starting the next cycle/step. A mid-flight HTTP call runs to completion but its result is
discarded. This matches `RunningModal`'s existing behaviour.

---

### UC3: Clean up workers on screen unmount

**Primary actor:** System (screen popped from the stack)

**Preconditions:**
- One or more blocking operations are in progress on the screen.

**Main flow:**
1. The screen is popped (`app.pop_screen()` or `app.exit()`).
2. Textual calls `on_unmount`.
3. The framework's unmount hook iterates all active `TaskHandle`s and sets their stop
   events.
4. The poller (still scheduled via `set_timer`) checks an `_unmounted` flag and exits
   without calling callbacks.
5. Workers finish their current blocking call and exit (daemon threads).

**Postconditions:**
- No callbacks fire on the unmounted screen (would crash — no widget context).
- No zombie threads (daemon + stop events).

---

### UC4: Run a save/snapshot operation without stalling

**Primary actor:** User (pressing `s` or typing `save` on the Agent screen)

**Preconditions:**
- A screen with a controller is mounted.

**Main flow:**
1. The user presses `s` (or types `save`).
2. The screen calls `self.run_blocking(self._controller.save_snapshot, on_result=..., on_error=...)`.
3. The worker runs `save_snapshot()` (sqlite I/O) off-thread.
4. On completion, `on_result(snapshot_id)` fires → the screen logs "Snapshot saved".

**Postconditions:**
- The UI did not stall during the I/O.
- The snapshot ID was displayed.

---

### UC5 (optional): Refactor RunningModal to use the framework runner

**Primary actor:** Developer (refactoring)

**Preconditions:**
- `RunningModal` has its own inline worker/queue/poll logic (~100 LOC).
- The framework now provides `BlockingTaskRunner`.

**Main flow:**
1. `RunningModal._worker_loop` is replaced by a `run_blocking` call (or a loop variant).
2. The modal's `_poll` callback is replaced by `on_result` / `on_progress` callbacks.
3. The 4 freeze-fix regression tests are re-run.

**Postconditions:**
- The 4 `TestRunningModalFreezeFix` tests pass.
- The modal's public behaviour (pause/resume/stop/dismiss) is unchanged.

**Note:** This use case is **optional**. If refactoring `RunningModal` proves risky (its
pause/resume/progress loop is specialised), it may be deferred. The primary deliverable
is fixing `AgentTUIScreen` and `AgentDemoScreen`.

## 3. Operations list (extracted from use cases)

These are the public methods that the framework must provide. Each becomes an operation
specification in the Design phase (`operation_spec_001`).

| # | Operation | Owner | UC | Description |
|---|-----------|-------|----|-------------|
| O1 | `run_blocking(func, on_result, on_error)` | `BaseAgentXScreen` | UC1, UC4 | Run `func` on a daemon worker thread; deliver result/error to the UI thread via callbacks. Returns a `TaskHandle`. |
| O2 | `TaskHandle.cancel()` | `TaskHandle` | UC2 | Signal the worker to stop (cooperative — sets a `threading.Event`). |
| O3 | `TaskHandle.is_done` | `TaskHandle` | UC1, UC2 | `True` if the worker has finished (result delivered or cancelled). |
| O4 | `_on_unmount_cleanup()` | `BaseAgentXScreen` | UC3 | Cancel all active task handles; suppress further callbacks. |
| O5 | `_poll_queue()` | `BlockingTaskRunner` | UC1 | UI-thread poller: drain the result/error queue, invoke callbacks, re-schedule via `set_timer`. |

## 4. Key behavioural contracts (for Design)

1. **Thread isolation:** The worker thread NEVER calls `query_one`, `notify`, `dismiss`,
   or any Textual widget method. It only puts plain data (`_MsgResult` / `_MsgError`)
   on the `queue.Queue`.

2. **UI thread is the sole widget mutator:** All `on_result` / `on_error` callbacks run
   on the UI thread (inside the `set_timer` poller), so they can safely touch widgets.

3. **Cooperative cancellation:** `cancel()` sets a `threading.Event`. The worker checks
   it before starting work. A blocking call already in flight runs to completion; its
   result is discarded if the task was cancelled.

4. **Unmount safety:** After `on_unmount`, the poller exits without calling callbacks.
   Workers are daemon threads, so they don't block process exit.

5. **Single-shot by default:** `run_blocking()` runs `func` once. A multi-step loop
   (like `RunningModal`'s auto-run) can be built on top: call `run_blocking` in the
   `on_result` callback to chain the next step. This keeps the framework simple.

6. **Error isolation:** If `func` raises, the exception is caught on the worker thread,
   put on the queue as `_MsgError`, and delivered to `on_error` on the UI thread. The
   worker never crashes silently.

7. **No callback after cancel/unmount:** If `cancel()` was called or the screen
   unmounted, `on_result` / `on_error` are NOT invoked. The result is silently dropped.
