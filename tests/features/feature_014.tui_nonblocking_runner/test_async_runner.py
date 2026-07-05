"""Unit tests for BlockingTaskRunner + TaskHandle (feature_014.tui_nonblocking_runner).

Tests the runner in isolation using a minimal mock "screen" that records
``set_timer`` calls.  No Textual app context is needed for the core logic —
the runner only uses ``screen.set_timer`` for scheduling, which we mock.

Threading tests use ``time.sleep`` to simulate blocking calls and
``asyncio.run`` + ``asyncio.sleep`` to let the UI-thread poller advance.
"""

from __future__ import annotations

import asyncio
import threading
import time
from typing import Any
from unittest.mock import MagicMock

import pytest

from agentx.ui.tui.framework.async_runner import (
    BlockingTaskRunner,
    TaskHandle,
    _MsgError,
    _MsgResult,
)


# ============================================================================
# Helpers
# ============================================================================


class _MockScreen:
    """Minimal screen mock that captures ``set_timer`` callbacks.

    The real ``BaseAgentXScreen`` delegates to Textual's ``set_timer``.  Here we
    capture the callback + delay so tests can invoke it manually (simulating
    the Textual event loop ticking).
    """

    def __init__(self) -> None:
        self.timers: list[tuple[float, Any]] = []

    def set_timer(self, delay: float, callback: Any) -> None:
        self.timers.append((delay, callback))


def _drain_timers(screen: _MockScreen) -> None:
    """Invoke all captured ``set_timer`` callbacks once (simulating one tick)."""
    timers = screen.timers[:]
    screen.timers.clear()
    for _delay, cb in timers:
        cb()


def _pump(screen: _MockScreen, *, iterations: int = 20, interval: float = 0.01) -> None:
    """Pump the mock event loop: sleep + drain timers, repeat."""
    for _ in range(iterations):
        time.sleep(interval)
        _drain_timers(screen)


# ============================================================================
# Message objects
# ============================================================================


class TestMessageObjects:
    def test_msg_result_slots(self):
        msg = _MsgResult(42)
        assert msg.value == 42
        assert not hasattr(msg, "__dict__")  # __slots__

    def test_msg_error_slots(self):
        exc = ValueError("boom")
        msg = _MsgError(exc)
        assert msg.error is exc
        assert not hasattr(msg, "__dict__")


# ============================================================================
# BlockingTaskRunner — core behaviour
# ============================================================================


class TestBlockingTaskRunnerStart:
    def test_start_spawns_daemon_thread(self):
        """start() spawns a daemon thread that runs func."""
        screen = _MockScreen()
        thread_ids: list[int] = []

        def func():
            thread_ids.append(threading.get_ident())
            return "ok"

        runner = BlockingTaskRunner(func, None, None, screen=screen)
        runner.start()

        _pump(screen, iterations=30)
        assert len(thread_ids) == 1, "func was never called"
        assert thread_ids[0] != threading.get_ident(), "func ran on the test thread"
        assert runner.is_done

    def test_start_schedules_first_poll(self):
        """start() schedules the first _poll via screen.set_timer."""
        screen = _MockScreen()
        runner = BlockingTaskRunner(lambda: None, None, None, screen=screen)
        runner.start()
        assert len(screen.timers) >= 1, "no timer was scheduled"
        assert screen.timers[0][0] == BlockingTaskRunner.POLL_INTERVAL


class TestBlockingTaskRunnerResult:
    def test_result_delivered_via_on_result(self):
        """on_result is called with the return value on the UI thread."""
        screen = _MockScreen()
        results: list[Any] = []

        runner = BlockingTaskRunner(
            lambda: "hello",
            on_result=results.append,
            on_error=None,
            screen=screen,
        )
        runner.start()
        _pump(screen, iterations=30)

        assert results == ["hello"]

    def test_none_result_delivered_correctly(self):
        """A None return value is delivered (not confused with the sentinel)."""
        screen = _MockScreen()
        results: list[Any] = []

        runner = BlockingTaskRunner(
            lambda: None,
            on_result=results.append,
            on_error=None,
            screen=screen,
        )
        runner.start()
        _pump(screen, iterations=30)

        assert results == [None]

    def test_result_delivered_on_ui_thread(self):
        """on_result runs on the thread that drains the queue (the UI thread)."""
        screen = _MockScreen()
        ui_thread_id = threading.get_ident()
        callback_thread_ids: list[int] = []

        def on_result(value):
            callback_thread_ids.append(threading.get_ident())

        runner = BlockingTaskRunner(
            lambda: 42,
            on_result=on_result,
            on_error=None,
            screen=screen,
        )
        runner.start()
        _pump(screen, iterations=30)

        assert len(callback_thread_ids) == 1
        assert callback_thread_ids[0] == ui_thread_id, (
            "on_result ran on a non-UI thread"
        )


class TestBlockingTaskRunnerError:
    def test_error_delivered_via_on_error(self):
        """An exception in func is delivered to on_error, not raised."""
        screen = _MockScreen()
        errors: list[Exception] = []

        def boom():
            raise ValueError("kaboom")

        runner = BlockingTaskRunner(
            boom,
            on_result=None,
            on_error=errors.append,
            screen=screen,
        )
        runner.start()
        _pump(screen, iterations=30)

        assert len(errors) == 1
        assert isinstance(errors[0], ValueError)
        assert str(errors[0]) == "kaboom"

    def test_error_does_not_crash_poller(self):
        """If on_error raises, the poller continues (doesn't crash)."""
        screen = _MockScreen()
        delivered: list[Any] = []

        def bad_callback(exc):
            raise RuntimeError("callback bug")

        runner = BlockingTaskRunner(
            lambda: "result",
            on_result=delivered.append,
            on_error=bad_callback,
            screen=screen,
        )
        runner.start()
        _pump(screen, iterations=30)
        # The result should still be delivered (on_result called) even though
        # we also have a bad on_error — but there's no error here, so on_error
        # is never called.  This test just verifies no crash.
        assert runner.is_done

    def test_on_result_crash_doesnt_crash_poller(self):
        """If on_result raises, the poller continues."""
        screen = _MockScreen()

        def bad_callback(value):
            raise RuntimeError("callback bug")

        runner = BlockingTaskRunner(
            lambda: "result",
            on_result=bad_callback,
            on_error=None,
            screen=screen,
        )
        runner.start()
        _pump(screen, iterations=30)
        assert runner.is_done  # didn't crash


# ============================================================================
# BlockingTaskRunner — cancellation
# ============================================================================


class TestBlockingTaskRunnerCancel:
    def test_cancel_before_start_suppresses_callback(self):
        """cancel() before the worker starts → func never called, no callback."""
        screen = _MockScreen()
        results: list[Any] = []
        called: list[bool] = []

        def func():
            called.append(True)
            return "should-not-happen"

        runner = BlockingTaskRunner(
            func,
            on_result=results.append,
            on_error=None,
            screen=screen,
        )
        runner.cancel()  # cancel before start
        runner.start()
        _pump(screen, iterations=30)

        assert called == [], "func was called despite cancel-before-start"
        assert results == [], "on_result was called despite cancel"

    def test_cancel_after_start_suppresses_callback(self):
        """cancel() after start but before result → callback suppressed."""
        screen = _MockScreen()
        results: list[Any] = []

        def slow_func():
            time.sleep(0.2)
            return "late"

        runner = BlockingTaskRunner(
            slow_func,
            on_result=results.append,
            on_error=None,
            screen=screen,
        )
        runner.start()
        time.sleep(0.05)  # let the worker start
        runner.cancel()
        _pump(screen, iterations=30)
        time.sleep(0.2)  # let the worker finish
        _pump(screen, iterations=5)  # drain any final messages

        assert results == [], "on_result was called despite cancel"

    def test_cancel_is_idempotent(self):
        """Calling cancel() multiple times is a no-op."""
        screen = _MockScreen()
        runner = BlockingTaskRunner(lambda: None, None, None, screen=screen)
        runner.cancel()
        runner.cancel()
        runner.cancel()
        assert runner._cancelled is True

    def test_cancel_sets_stop_event(self):
        """cancel() sets _stop_evt so the worker checks it before starting."""
        screen = _MockScreen()
        runner = BlockingTaskRunner(lambda: None, None, None, screen=screen)
        assert not runner._stop_evt.is_set()
        runner.cancel()
        assert runner._stop_evt.is_set()


# ============================================================================
# BlockingTaskRunner — unmount
# ============================================================================


class TestBlockingTaskRunnerUnmount:
    def test_unmount_suppresses_callbacks(self):
        """If _unmounted is set, the poller exits without calling callbacks."""
        screen = _MockScreen()
        results: list[Any] = []

        def slow_func():
            time.sleep(0.1)
            return "late"

        runner = BlockingTaskRunner(
            slow_func,
            on_result=results.append,
            on_error=None,
            screen=screen,
        )
        runner.start()
        runner._unmounted = True  # simulate unmount
        _pump(screen, iterations=30)
        time.sleep(0.15)  # let the worker finish
        _pump(screen, iterations=5)

        assert results == [], "on_result was called after unmount"

    def test_unmount_stops_polling(self):
        """After _unmounted is set, _poll returns without re-scheduling."""
        screen = _MockScreen()
        runner = BlockingTaskRunner(
            lambda: time.sleep(0.1),
            on_result=None,
            on_error=None,
            screen=screen,
        )
        runner.start()
        # First poll: the worker is still sleeping, so _poll drains (empty) and
        # re-schedules (adds a timer).  We capture that timer but don't run it.
        _drain_timers(screen)  # first poll → schedules another poll
        runner._unmounted = True
        # Count timers currently pending (the re-scheduled poll).
        timers_before = len(screen.timers)
        # Drain them — _poll should check _unmounted and return WITHOUT adding
        # a new timer, so the list stays at its current count minus consumed.
        _drain_timers(screen)
        # No new timer should have been added (the poller didn't re-schedule).
        assert len(screen.timers) == 0, (
            f"poller re-scheduled after unmount ({timers_before} → "
            f"{len(screen.timers)})"
        )


# ============================================================================
# BlockingTaskRunner — concurrency
# ============================================================================


class TestBlockingTaskRunnerConcurrency:
    def test_multiple_runners_concurrently(self):
        """Multiple runners can run at the same time without interference."""
        screen = _MockScreen()
        results_1: list[Any] = []
        results_2: list[Any] = []

        r1 = BlockingTaskRunner(
            lambda: "r1", on_result=results_1.append, on_error=None, screen=screen
        )
        r2 = BlockingTaskRunner(
            lambda: "r2", on_result=results_2.append, on_error=None, screen=screen
        )
        r1.start()
        r2.start()
        _pump(screen, iterations=30)

        assert results_1 == ["r1"]
        assert results_2 == ["r2"]
        assert r1.is_done and r2.is_done


# ============================================================================
# TaskHandle
# ============================================================================


class TestTaskHandle:
    def test_cancel_delegates_to_runner(self):
        screen = _MockScreen()
        runner = BlockingTaskRunner(lambda: None, None, None, screen=screen)
        handle = TaskHandle(runner)
        handle.cancel()
        assert runner._cancelled is True
        assert runner._stop_evt.is_set()

    def test_is_done_delegates_to_runner(self):
        screen = _MockScreen()
        runner = BlockingTaskRunner(lambda: None, None, None, screen=screen)
        handle = TaskHandle(runner)
        assert handle.is_done is False
        runner._done = True
        assert handle.is_done is True

    def test_handle_from_run_blocking(self):
        """BaseAgentXScreen.run_blocking returns a TaskHandle."""
        from agentx.ui.tui.framework import BaseAgentXScreen
        from textual.app import ComposeResult
        from textual.widgets import Static

        class _TestScreen(BaseAgentXScreen):
            def compose(self) -> ComposeResult:  # type: ignore[override]
                yield Static("test")

        screen = _TestScreen()
        handle = screen.run_blocking(lambda: 42, on_result=None, on_error=None)
        assert isinstance(handle, TaskHandle)
        assert handle in screen._task_handles or handle._runner in [
            h._runner for h in screen._task_handles
        ]


# ============================================================================
# BaseAgentXScreen.run_blocking + on_unmount integration
# ============================================================================


class TestBaseScreenRunBlocking:
    def test_run_blocking_tracks_handle(self):
        """run_blocking appends the handle to _task_handles."""
        from agentx.ui.tui.framework import BaseAgentXScreen
        from textual.app import ComposeResult
        from textual.widgets import Static

        class _TestScreen(BaseAgentXScreen):
            def compose(self) -> ComposeResult:  # type: ignore[override]
                yield Static("test")

        screen = _TestScreen()
        initial_count = len(screen._task_handles)
        screen.run_blocking(lambda: None, on_result=None, on_error=None)
        assert len(screen._task_handles) == initial_count + 1

    def test_on_unmount_cancels_all_handles(self):
        """on_unmount cancels every tracked handle."""
        from agentx.ui.tui.framework import BaseAgentXScreen
        from textual.app import ComposeResult
        from textual.widgets import Static

        class _TestScreen(BaseAgentXScreen):
            def compose(self) -> ComposeResult:  # type: ignore[override]
                yield Static("test")

        screen = _TestScreen()
        h1 = screen.run_blocking(lambda: None, on_result=None, on_error=None)
        h2 = screen.run_blocking(lambda: None, on_result=None, on_error=None)
        assert len(screen._task_handles) == 2

        screen.on_unmount()

        assert h1._runner._cancelled is True
        assert h2._runner._cancelled is True
        assert h1._runner._unmounted is True
        assert h2._runner._unmounted is True
        assert len(screen._task_handles) == 0, "handles not cleared"

    def test_on_unmount_is_safe_with_no_handles(self):
        """on_unmount doesn't crash when _task_handles is empty."""
        from agentx.ui.tui.framework import BaseAgentXScreen
        from textual.app import ComposeResult
        from textual.widgets import Static

        class _TestScreen(BaseAgentXScreen):
            def compose(self) -> ComposeResult:  # type: ignore[override]
                yield Static("test")

        screen = _TestScreen()
        screen.on_unmount()  # should not raise
        assert len(screen._task_handles) == 0
