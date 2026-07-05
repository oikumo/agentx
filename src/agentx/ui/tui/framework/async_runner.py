"""Reusable non-blocking work runner for the AgentX TUI framework.

Runs a blocking callable on a daemon worker thread and delivers the result
(or exception) to the UI thread via a ``queue.Queue`` + ``set_timer`` poller.
The worker never touches Textual widgets; only plain data crosses the queue.

This is the framework-level fix for the agent-screen freeze: ``run_cycle()``
and ``save_snapshot()`` make blocking calls (``llm.invoke()`` HTTP, sqlite I/O)
that, if run on the Textual UI thread, freeze the entire event loop.  By
routing them through :class:`BlockingTaskRunner`, the UI stays responsive
(timers fire, keys are accepted, Stop/Escape work mid-call).

Design: ``design_001_nonblocking_runner.md`` §3.
Operation spec: ``operation_spec_001_nonblocking_runner.md`` O1–O5.
MVC++: pure View — no Model import; controllers are duck-typed ``Any``.

Threading model::

    Worker thread                       UI thread
    ─────────────                       ─────────
    _worker_loop():
      if stop_evt: return                 _poll()  [scheduled by set_timer]
      try:                                  msg = queue.get_nowait()
        result = func()                     _MsgResult → _deliver(result)
        queue.put(_MsgResult(result))       _MsgError  → _deliver(error)
      except Exception as exc:              None (sentinel) → _done
        queue.put(_MsgError(exc))          if not _done: set_timer(0.05, _poll)
      finally:
        self._done = True
        queue.put(None)  # sentinel

The worker puts a ``None`` sentinel after the result/error so the poller knows
the worker has exited even if ``func`` returned ``None`` instantly (the
``_MsgResult(None)`` would otherwise be indistinguishable from an empty queue
drained after unmount).
"""

from __future__ import annotations

import queue
import threading
from typing import Any, Callable

__all__ = ["BlockingTaskRunner", "TaskHandle"]


# ============================================================================
# Worker → UI thread messages (plain data — never touch widgets)
# ============================================================================


class _MsgResult:
    """Worker → UI: the callable returned a value."""

    __slots__ = ("value",)

    def __init__(self, value: Any) -> None:
        self.value = value


class _MsgError:
    """Worker → UI: the callable raised an exception."""

    __slots__ = ("error",)

    def __init__(self, error: Exception) -> None:
        self.error = error


# ============================================================================
# BlockingTaskRunner
# ============================================================================


class BlockingTaskRunner:
    """Run a single blocking callable on a daemon worker thread.

    Created by :meth:`BaseAgentXScreen.run_blocking`.  The runner:

    1. Spawns a daemon :class:`threading.Thread` that calls ``func``.
    2. The worker puts the result (or exception) onto a
       :class:`queue.Queue` as a plain message object.
    3. The UI thread polls the queue via ``set_timer(0.05, self._poll)`` and
       invokes ``on_result`` / ``on_error`` **on the UI thread** (safe to touch
       widgets).
    4. ``cancel()`` sets a :class:`threading.Event`; the worker checks it
       before starting.  A mid-flight blocking call runs to completion but its
       result is discarded (callbacks suppressed).

    The runner never imports or touches Textual widgets directly — it uses the
    duck-typed ``screen`` reference only for ``set_timer`` scheduling.
    """

    #: Poll interval in seconds — short enough for responsive UI updates,
    #: long enough to avoid excessive timer churn.
    POLL_INTERVAL: float = 0.05

    def __init__(
        self,
        func: Callable[[], Any],
        on_result: Callable[[Any], None] | None,
        on_error: Callable[[Exception], None] | None,
        *,
        screen: Any,
    ) -> None:
        """Configure the runner (does not start the worker).

        Args:
            func:       The blocking callable (takes no args, returns Any).
            on_result:  Callback invoked on the UI thread with the return value.
                        May be ``None`` (result silently discarded).
            on_error:   Callback invoked on the UI thread with the exception.
                        May be ``None`` (error silently discarded).
            screen:     The owning screen (duck-typed).  Used only for
                        ``set_timer`` scheduling — never for widget access.
        """
        self._func: Callable[[], Any] = func
        self._on_result: Callable[[Any], None] | None = on_result
        self._on_error: Callable[[Exception], None] | None = on_error
        self._screen: Any = screen

        # Worker → UI communication.
        self._queue: "queue.Queue[Any]" = queue.Queue()
        self._stop_evt: threading.Event = threading.Event()

        # State flags — mutated on the UI thread (poller) except _done which
        # is set on the worker thread's finally block (single write, safe).
        self._worker: threading.Thread | None = None
        self._done: bool = False
        self._cancelled: bool = False
        self._unmounted: bool = False

    # ----------------------------------------------------------- public API

    def start(self) -> None:
        """Spawn the daemon worker thread and schedule the first poll."""
        self._worker = threading.Thread(
            target=self._worker_loop,
            name="AgentX-BlockingTaskRunner",
            daemon=True,
        )
        self._worker.start()
        self._schedule_poll()

    def cancel(self) -> None:
        """Signal the worker to stop and suppress callbacks.

        Idempotent — safe to call multiple times or after the worker finished.
        The worker checks ``_stop_evt`` before starting ``func``.  If already
        in flight, the result is discarded (``_cancelled`` suppresses the
        callback).
        """
        self._stop_evt.set()
        self._cancelled = True

    @property
    def is_done(self) -> bool:
        """``True`` after the worker exits (func returned / raised / pre-cancelled)."""
        return self._done

    # ----------------------------------------------------------- worker (off UI thread)

    def _worker_loop(self) -> None:
        """Run ``func`` on the worker thread; put result/error on the queue.

        MUST NOT touch Textual widgets or call ``query_one`` / ``notify`` /
        ``dismiss``.  Only plain data (``_MsgResult`` / ``_MsgError``) crosses
        the queue.
        """
        try:
            if self._stop_evt.is_set():
                return  # cancelled before starting — don't call func
            result = self._func()
            self._queue.put(_MsgResult(result))
        except Exception as exc:  # noqa: BLE001 — surface to UI thread, don't crash
            self._queue.put(_MsgError(exc))
        finally:
            self._done = True
            # Sentinel: tells the poller the worker has exited.  This is
            # necessary because _MsgResult(None) is a valid result and
            # indistinguishable from "queue was empty" on a get_nowait().
            self._queue.put(None)

    # ----------------------------------------------------------- poller (UI thread)

    def _poll(self) -> None:
        """Drain the queue and deliver results/errors, then re-schedule.

        Scheduled on the UI thread via ``set_timer``.  This is the ONLY place
        that calls ``on_result`` / ``on_error`` — guaranteeing they run on the
        UI thread (safe to touch widgets).
        """
        if self._unmounted:
            return  # screen gone — stop polling, suppress callbacks

        while True:
            try:
                msg = self._queue.get_nowait()
            except queue.Empty:
                break  # no more messages right now

            if msg is None:
                # Sentinel — worker has exited.  We may have already delivered
                # the result/error above; just note _done (already set by the
                # worker's finally block, but set it here too for clarity).
                continue
            elif isinstance(msg, _MsgResult):
                self._deliver(result=msg.value, error=None)
            elif isinstance(msg, _MsgError):
                self._deliver(result=None, error=msg.error)

        # Keep polling until the worker is done.
        if not self._done:
            self._schedule_poll()

    def _deliver(self, result: Any, error: Exception | None) -> None:
        """Invoke ``on_result`` / ``on_error`` on the UI thread.

        Suppressed if the task was cancelled or the screen unmounted.  Callback
        exceptions are silently swallowed — a buggy callback must not crash the
        poller (which would leave the worker's result undelivered and the
        timer re-scheduling dead).
        """
        if self._cancelled or self._unmounted:
            return
        try:
            if error is not None:
                if self._on_error is not None:
                    self._on_error(error)
            else:
                if self._on_result is not None:
                    self._on_result(result)
        except Exception:  # noqa: BLE001 — never crash the poller
            pass

    def _schedule_poll(self) -> None:
        """Schedule ``_poll`` on the UI thread via ``screen.set_timer``.

        Wrapped in try/except so a missing app context (unit tests) does not
        crash — polling simply stops and the worker's result is discarded.
        """
        try:
            self._screen.set_timer(self.POLL_INTERVAL, self._poll)
        except Exception:  # noqa: BLE001 — no app context
            pass


# ============================================================================
# TaskHandle
# ============================================================================


class TaskHandle:
    """Handle returned by :meth:`BaseAgentXScreen.run_blocking`.

    A thin wrapper around :class:`BlockingTaskRunner` that exposes the
    cancellation and completion API without exposing the runner's internals.
    This allows future extension (``join()``, ``add_progress_callback()``)
    without changing the ``run_blocking`` signature.
    """

    def __init__(self, runner: BlockingTaskRunner) -> None:
        self._runner: BlockingTaskRunner = runner

    def cancel(self) -> None:
        """Signal the worker to stop and suppress callbacks (idempotent)."""
        self._runner.cancel()

    @property
    def is_done(self) -> bool:
        """``True`` after the worker exits."""
        return self._runner.is_done
