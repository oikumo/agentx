# Analysis 001 — TUI Nonblocking Runner: Overview & Current-State

> **Phase:** Analysis — `omt_agent_guide.md §2, §4` | **Feature:** feature_014.tui_nonblocking_runner
> **Task type:** major_feature

## 1. Problem statement

AgentX's TUI framework (feature_012) provides reusable base classes for screens,
modals, adapters, and widgets. However, it has **no mechanism for running blocking
operations off the Textual UI thread**. When a screen calls a blocking operation
synchronously on the event loop, the **entire UI freezes** — keyboard bindings, timers,
and repaints all stop until the operation returns.

Three screens exhibit this freeze today:

| Screen | Method | Blocking call | What blocks | Severity |
|--------|--------|---------------|-------------|----------|
| `AgentTUIScreen` | `action_run_cycle()` :480 | `controller.run_cycle()` | `llm.invoke()` HTTP (1–30s) | **Critical** — full freeze, Escape/Back unresponsive |
| `AgentDemoScreen` | `action_run_cycle()` :118 | `controller.run_cycle()` | `llm.invoke()` HTTP (1–30s) | **Critical** — full freeze |
| `AgentTUIScreen` | `action_save()` :512 | `controller.save_snapshot()` | sqlite I/O + JSON serialize | Minor — brief stall |

### The call chain that freezes

```
AgentTUIScreen.action_run_cycle()        ← UI thread
  → AgentController.run_cycle()
    → Agent.run_cycle()
      → ReflectionEngine.reflect()
        → AIServiceAdapter.complete()
          → llm.invoke()                 ← BLOCKING HTTP call (1–30s)
```

While `llm.invoke()` blocks, Textual's event loop cannot process messages. The user
sees a frozen terminal — pressing `q`, `Escape`, or `Ctrl+C` has no effect until the
HTTP call returns.

### The proven fix (exists but is not reusable)

The Fast Agent's `RunningModal` (`fast_agent_modals.py`) **already solved this exact
bug** in feature_011's freeze-fix. The solution:

1. `run_cycle()` runs on a **daemon worker thread** (not the UI thread).
2. The worker posts plain-data messages (`_MsgCycle`, `_MsgPending`, `_MsgDone`) onto a
   `queue.Queue`.
3. The UI thread polls the queue via `set_timer(0.05, self._poll)` and updates widgets
   with the results.
4. A `threading.Event` (`_stop_evt`) signals the worker to stop; `_pause_evt` gates
   pause/resume.
5. `on_unmount` sets the stop event so the worker doesn't outlive the modal.

This was validated by 4 regression tests in `TestRunningModalFreezeFix`:
- `test_run_cycle_runs_off_ui_thread` — proves `run_cycle` runs on a different thread
- `test_event_loop_responsive_during_blocking_cycle` — proves a timer fires during the block
- `test_stop_works_while_cycle_blocks` — proves Stop dismisses in <0.5s during a 1.0s block
- `test_pause_resumes_after_blocking_cycle` — proves pause/resume works

**But this ~100 LOC of threading logic is hardcoded inline in `RunningModal`** —
`AgentTUIScreen` and `AgentDemoScreen` cannot use it. They still freeze.

## 2. Scope (what "done" looks like)

A reusable **`BlockingTaskRunner`** in `src/agentx/ui/tui/framework/` that:

1. Runs any blocking callable on a daemon worker thread.
2. Delivers the result (or exception) to the UI thread via a `queue.Queue` +
   `set_timer` poller that invokes caller-supplied `on_result` / `on_error` callbacks.
3. Returns a `TaskHandle` with a `cancel()` method (sets a `threading.Event`).
4. Cleans up on screen unmount (`on_unmount` signals all active workers to stop).
5. Is inherited by every `BaseAgentXScreen` subclass via a `run_blocking()` method.

Plus refactoring the three freeze-affected screens to use it, with:
- The existing `RunningModal` freeze-fix tests still green.
- The full test suite passing (1 pre-existing failure allowed).
- MVC++ 0 errors.

## 3. Current-state analysis — the blocking-call inventory

### 3.1 `AgentTUIScreen.action_run_cycle()` (agent_screen.py:480–510)

```python
def action_run_cycle(self) -> None:
    if not self._controller:
        return
    self._log("[bold blue]═══ Running cycle ═══[/bold blue]")
    try:
        result = self._controller.run_cycle()  # ← BLOCKS THE UI THREAD
        # ... render result (decision, action, reflection) ...
    except Exception as exc:
        self._log(f"[red]Cycle error: {exc}[/red]")
    self._refresh_status()
```

The user presses `r` or types `run`. `run_cycle()` blocks on `llm.invoke()`. The UI
freezes for the entire HTTP round-trip. The user cannot cancel, navigate away, or even
see that anything is happening.

### 3.2 `AgentDemoScreen.action_run_cycle()` (demo_screen.py:118–128)

```python
def action_run_cycle(self) -> None:
    if not self._controller:
        return
    self._log("[bold blue]─── Running cycle ───[/bold blue]")
    try:
        result = self._controller.run_cycle()  # ← BLOCKS THE UI THREAD
        self._render_cycle_result(result)
    except Exception as exc:
        self._log(f"[red]Cycle error: {exc}[/red]")
    self._refresh_status()
```

Identical pattern. The demo screen auto-runs a cycle on mount (`on_mount` →
`action_run_cycle`), so the freeze happens immediately on entering the demo.

### 3.3 `AgentTUIScreen.action_save()` (agent_screen.py:512–519)

```python
def action_save(self) -> None:
    if not self._controller:
        return
    try:
        snapshot_id = self._controller.save_snapshot()  # ← sqlite I/O
        self._log(f"[green]Snapshot saved: {snapshot_id[:8]}…[/green]")
    except Exception as exc:
        self._log(f"[red]Save error: {exc}[/red]")
```

Less severe (sqlite is fast), but still a synchronous I/O call on the UI thread. If the
database is large or on a slow filesystem, the UI stutters.

### 3.4 `RunningModal` — the inline threading solution (fast_agent_modals.py:232–485)

The modal's threading is correct and tested, but it is **self-contained**:

- `_worker_loop()` — the daemon thread target, runs cycles in a loop.
- `_poll()` — the UI-thread poller, drains the queue via `set_timer(0.05, ...)`.
- `_MsgCycle` / `_MsgPending` / `_MsgDone` — plain message objects.
- `_stop_evt` / `_pause_evt` — `threading.Event` for cancellation and pause.
- `on_unmount` — sets `_stop_evt` so the worker exits.

This is ~100 LOC of threading infrastructure that cannot be reused by
`AgentTUIScreen` or `AgentDemoScreen` without copy-paste.

### 3.5 What the framework currently provides (feature_012)

`BaseAgentXScreen` provides: `__init__`/`set_controller`, `action_quit`/`action_back`,
`compose_chrome`, `safe_notify`/`safe_error`/`safe_update`/`safe_log`,
`handle_input_submitted`, `navigate_to_child`. **No async/threading support at all.**

`BaseAgentXModalScreen` adds: `safe_dismiss` (double-dismiss guard). **No threading.**

## 4. Goals of the framework addition (derived from analysis)

1. **One `BlockingTaskRunner`** — runs a blocking callable on a daemon worker thread,
   delivers result/error to the UI thread via queue + `set_timer` poll.
2. **A `TaskHandle`** — returned by `run_blocking()`, with `cancel()` and `is_done`.
3. **A `run_blocking()` method on `BaseAgentXScreen`** — the public API every screen
   inherits. Accepts `func`, `on_result`, `on_error`; returns a `TaskHandle`.
4. **Unmount cleanup** — `BaseAgentXScreen.on_unmount` (or a hook) cancels all active
   workers so no zombie threads remain after the screen is popped.
5. **Refactor `AgentTUIScreen.action_run_cycle`** — use `run_blocking()`.
6. **Refactor `AgentDemoScreen.action_run_cycle`** — use `run_blocking()`.
7. **Refactor `AgentTUIScreen.action_save`** — use `run_blocking()` (optional, low risk).
8. **Preserve `RunningModal`'s freeze-fix** — its 4 regression tests stay green. The
   modal may optionally be refactored to use the runner if it reduces duplication
   without breaking tests.

## 5. Non-goals

- **No async/await rewrite** — the codebase is synchronous (Textual's async event loop
  drives the UI, but all controller/model calls are sync). We use threads, not asyncio.
- **No new dependencies** — `threading`, `queue` are stdlib; no new Textual features.
- **No Textual `@work`/`run_worker` migration** — the existing queue+timer pattern is
  proven and gives finer control over cancellation and progress. Textual's worker API
  could be evaluated later but is out of scope for this freeze fix.
- **No controller/model changes** — the runner is pure View-layer; controllers stay sync.
- **No new screens** — this fixes existing screens, doesn't add UI.

## 6. Risk assessment

| Risk | Level | Mitigation |
|---|---|---|
| RunningModal freeze-fix regresses | **High** | Keep its 4 regression tests as the gate; do not change the modal's public behaviour. If refactored, prove tests stay green. |
| Thread-safety bugs (race on widget access) | Medium | The worker NEVER touches widgets — it only puts plain data on the queue. The UI thread is the sole widget mutator. |
| Zombie threads after unmount | Medium | `on_unmount` sets `_stop_evt`; workers are daemon threads (killed on process exit). Test: unmount-during-block. |
| Double-callback (on_result called after unmount) | Medium | The poller checks an `_unmounted` flag before calling callbacks; cancelled tasks' callbacks are suppressed. |
| MVC++ violation (runner imports Model) | Low | Runner is pure View; controllers duck-typed `Any`. `mvc_check.py` after each edit. |
| Full-suite regressions | Medium | Run the suite after each screen refactor; 1 pre-existing failure allowed. |

## 7. Feasibility statement

- **Phase:** Analysis → Design (clear feature, major size, threading complexity).
- **Files affected:**
  - New: `src/agentx/ui/tui/framework/async_runner.py` (the `BlockingTaskRunner` +
    `TaskHandle`).
  - Edit: `src/agentx/ui/tui/framework/base_screen.py` (add `run_blocking` +
    unmount hook), `base_modal.py` (inherits it), `__init__.py` (export).
  - Edit: `src/agentx/agent/view/tui/agent_screen.py` (refactor `action_run_cycle` +
    `action_save`).
  - Edit: `src/agentx/agent/view/tui/demo_screen.py` (refactor `action_run_cycle`).
  - Optional: `src/agentx/agent/view/tui/fast_agent_modals.py` (refactor `RunningModal`
    to use the runner, if it reduces duplication without breaking tests).
- **Risk:** Medium-High (threading correctness + must preserve the existing freeze-fix).
- **Effort estimate:** Design ~30 min, Implementation ~60 min, Testing ~45 min.
