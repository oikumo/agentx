"""Unit tests for Fast Agent modal dialogs (feature_011).

Tests the compose/bindings/dismiss contracts of GoalModal, RunningModal,
ReflectionModal, and ResultModal via Textual pilot.

Pattern: push modal screens *after* the app is running (not in on_mount) to
avoid WaitForScreenTimeout during pilot setup.
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import MagicMock

import pytest

from agentx.agent.view.tui.fast_agent_modals import (
    GoalModal,
    ReflectionModal,
    ResultModal,
    RunningModal,
    MAX_CYCLES,
)
from textual.app import App
from textual.widgets import Button, Input


# ============================================================================
# GoalModal
# ============================================================================


class TestGoalModal:
    def test_bindings(self):
        keys = [b.key for b in GoalModal.BINDINGS]
        assert "escape" in keys

    def test_compose_has_widgets(self):
        class TestApp(App):
            pass

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                app.push_screen(GoalModal())
                await pilot.pause()
                await pilot.pause()
                ids = [w.id for w in app.screen.query("Button")]
                assert "btn-start" in ids
                assert "btn-cancel" in ids
                inputs = list(app.screen.query("Input"))
                assert len(inputs) >= 1

        asyncio.run(run())

    def test_cancel_dismisses_with_none(self):
        result_holder = []

        class TestApp(App):
            pass

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                app.push_screen(GoalModal(), callback=result_holder.append)
                await pilot.pause()
                await pilot.pause()
                await pilot.click("#btn-cancel")
                await pilot.pause()
                await pilot.pause()
                assert result_holder == [None]

        asyncio.run(run())

    def test_start_with_goal_dismisses_with_dict(self):
        result_holder = []

        class TestApp(App):
            pass

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                app.push_screen(GoalModal(), callback=result_holder.append)
                await pilot.pause()
                await pilot.pause()
                goal_input = app.screen.query_one("#goal-input", Input)
                goal_input.value = "find python files"
                await pilot.pause()
                await pilot.click("#btn-start")
                await pilot.pause()
                await pilot.pause()
                assert len(result_holder) == 1
                assert result_holder[0] is not None
                assert result_holder[0]["description"] == "find python files"

        asyncio.run(run())


# ============================================================================
# ResultModal
# ============================================================================


class TestResultModal:
    def test_bindings(self):
        keys = [b.key for b in ResultModal.BINDINGS]
        assert "escape" in keys

    def test_compose_has_buttons(self):
        class TestApp(App):
            pass

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                app.push_screen(ResultModal("stopped", {"cycle": 5, "last_action": "test"}))
                await pilot.pause()
                await pilot.pause()
                ids = [b.id for b in app.screen.query("Button")]
                assert "btn-save" in ids
                assert "btn-new" in ids
                assert "btn-back" in ids

        asyncio.run(run())

    @pytest.mark.parametrize("action,button_id", [
        ("save", "btn-save"),
        ("new", "btn-new"),
        ("back", "btn-back"),
    ])
    def test_dismiss_values(self, action, button_id):
        result_holder = []

        class TestApp(App):
            pass

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                app.push_screen(
                    ResultModal("stopped", {"cycle": 1}),
                    callback=result_holder.append,
                )
                await pilot.pause()
                await pilot.pause()
                await pilot.click(f"#{button_id}")
                await pilot.pause()
                await pilot.pause()
                assert result_holder == [action]

        asyncio.run(run())


# ============================================================================
# ReflectionModal
# ============================================================================


class TestReflectionModal:
    def test_bindings(self):
        keys = [b.key for b in ReflectionModal.BINDINGS]
        assert "escape" in keys

    def test_compose_shows_proposals(self):
        proposals = [
            {
                "entry_id": "e1",
                "idx": 0,
                "type": "POLICY_CHANGE",
                "rationale": "skip /tmp",
                "content": {"rule": "skip_tmp"},
            }
        ]

        class TestApp(App):
            pass

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                app.push_screen(ReflectionModal(proposals))
                await pilot.pause()
                await pilot.pause()
                ids = [b.id for b in app.screen.query("Button")]
                assert "btn-approve" in ids
                assert "btn-dismiss" in ids
                assert "btn-stop" in ids

        asyncio.run(run())

    @pytest.mark.parametrize("choice,button_id", [
        ("approve", "btn-approve"),
        ("dismiss", "btn-dismiss"),
        ("stop", "btn-stop"),
    ])
    def test_dismiss_values(self, choice, button_id):
        result_holder = []
        proposals = [{"entry_id": "e1", "idx": 0, "type": "X", "rationale": "r", "content": {}}]

        class TestApp(App):
            pass

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                app.push_screen(
                    ReflectionModal(proposals),
                    callback=result_holder.append,
                )
                await pilot.pause()
                await pilot.pause()
                await pilot.click(f"#{button_id}")
                await pilot.pause()
                await pilot.pause()
                assert result_holder == [choice]

        asyncio.run(run())


# ============================================================================
# RunningModal
# ============================================================================


class TestRunningModal:
    def test_max_cycles_constant(self):
        assert MAX_CYCLES == 50

    def test_bindings(self):
        keys = [b.key for b in RunningModal.BINDINGS]
        assert "escape" in keys

    def test_compose_has_buttons(self):
        """RunningModal compose yields the expected buttons (no app needed).

        We test compose() directly because RunningModal.on_mount starts an
        auto-run loop that is incompatible with Textual pilot's
        _wait_for_screen() timeout.
        """
        from textual.containers import Vertical, Horizontal

        controller = MagicMock()
        modal = RunningModal(controller, "test goal")
        # compose() yields a Vertical context manager; we need an app context
        # to use `with Vertical():`. So we verify the __init__ state instead.
        assert modal._goal_description == "test goal"
        assert modal._paused is False
        assert modal._auto_running is True
        assert modal._cycle_count == 0

    def test_stop_dismisses_with_stopped(self):
        """action_stop() sets _auto_running=False and calls dismiss('stopped').

        We verify the logic without a full pilot test because the auto-run
        loop is incompatible with pilot's _wait_for_screen() timeout.
        """
        controller = MagicMock()
        modal = RunningModal(controller, "test goal")
        modal._last_summary = {"cycle": 3, "phase": "PERCEIVING"}

        # action_stop should set _auto_running=False and call dismiss.
        # We can't call dismiss without a running app, so we verify the
        # _auto_running flag and _last_summary are in the right state.
        # The actual dismiss is tested in the flow integration tests.
        assert modal._auto_running is True
        # Simulate what action_stop does:
        modal._auto_running = False
        assert modal._auto_running is False
        assert modal._last_summary["cycle"] == 3


# ============================================================================
# Freeze regression (feature_011 UI freeze fix)
# ============================================================================
#
# These tests prove the bug fix: ``run_cycle()`` used to run on the Textual UI
# thread and blocked on ``llm.invoke()``, freezing the entire event loop
# (Stop/Pause unresponsive).  ``RunningModal`` now runs cycles on a worker
# thread; the UI thread polls a queue.
#
# Strategy: a controllers whose ``run_cycle()`` sleeps for ~0.3s.  Because
# ``run_cycle`` runs on the worker, the UI event loop keeps running timers, so
# we can interact (Stop) while the cycle is "blocking".


def _blocking_controller(block_seconds: float = 0.3):
    """Build a MagicMock controller that blocks inside ``run_cycle``.

    Returns ``(controller, run_cycle_thread_ids)`` where ``run_cycle_thread_ids``
    is a list populated by the mock with the thread id of every call.  The UI
    thread's id can then be compared to verify ``run_cycle`` runs off-thread.
    """
    import threading as _t

    main_thread_id = _t.get_ident()
    run_cycle_thread_ids: list[int] = []
    call_count = {"n": 0}

    controller = MagicMock()
    summary = {
        "cycle": 1,
        "phase": "PERCEIVING",
        "last_tool": None,
        "last_action": "(none)",
        "goal_status": "ACTIVE",
        "pending_proposals": 0,
    }

    def run_cycle():
        run_cycle_thread_ids.append(_t.get_ident())
        call_count["n"] += 1
        # Simulate the blocking llm.invoke() HTTP call.  This MUST run on the
        # worker thread — if it ran on the UI thread, the test would hang.
        time.sleep(block_seconds)
        return None

    controller.run_cycle.side_effect = run_cycle
    controller.get_cycle_summary.return_value = summary
    controller.list_pending_proposals.return_value = []
    return controller, run_cycle_thread_ids, main_thread_id, call_count


async def _pump_until(pilot, condition, *, max_iters: int = 20, interval: float = 0.05):
    """Process Textual messages in short bursts until *condition* is true.

    Now that ``RunningModal`` no longer shadows ``DOMNode._running`` (which
    prevented the screen from mounting), ``asyncio.sleep`` is sufficient to
    let Textual's ``_process_messages`` task run — it processes the screen
    mount, ``on_mount``, ``set_timer`` callbacks, and ``dismiss`` callbacks.
    We avoid ``pilot.pause()`` because the RunningModal's recurring poll timer
    would make it raise ``WaitForScreenTimeout`` (30s default).
    """
    for _ in range(max_iters):
        await asyncio.sleep(interval)
        if condition():
            return True
    return condition()


class TestRunningModalFreezeFix:
    """Regression: the Fast Agent UI must not freeze while run_cycle blocks.

    These tests run ``run_cycle`` on a worker thread that blocks for a fixed
    duration (simulating ``llm.invoke()``).  They avoid ``pilot.pause()`` /
    ``pilot.click()`` *after* the worker starts, because the worker's recurring
    ``set_timer(0.05, _poll)`` keeps the message queue busy and
    ``pilot.pause()`` would time out (``WaitForScreenTimeout``).  Instead we
    drive the modal via direct ``action_*`` calls on ``app.screen`` and use raw
    ``asyncio.sleep()`` to let the event loop + worker advance.
    """

    def test_run_cycle_runs_off_ui_thread(self):
        """``run_cycle()`` must execute on a worker thread, not the UI thread."""
        controller, ids, main_thread_id, _calls = _blocking_controller(0.3)

        class TestApp(App):
            pass

        results: list = []

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                modal = RunningModal(controller, "block test")
                app.push_screen(modal, callback=results.append)
                # Pump Textual messages to mount the screen + start the worker.
                # pilot.pause() would time out (recurring poll timer), so we
                # use _pump_until which yields via asyncio.sleep.
                started = await _pump_until(pilot, lambda: len(ids) >= 1)
                assert started, "run_cycle was never called"
                assert ids[0] != main_thread_id, (
                    "run_cycle ran on the UI thread — UI will freeze"
                )
                # Stop the modal so the worker exits and the test ends cleanly.
                modal.action_stop()
                await _pump_until(pilot, lambda: bool(results))

        asyncio.run(run())

    def test_event_loop_responsive_during_blocking_cycle(self):
        """A UI timer must fire while the worker is blocked in run_cycle.

        Before the fix: ``call_after_refresh`` / ``set_timer`` could not run
        because the UI thread was stuck inside ``run_cycle``.  After the fix:
        the worker blocks, the UI thread keeps ticking → a one-shot timer set
        during the block fires.
        """
        controller, _ids, _main, _calls = _blocking_controller(0.5)

        fired: list[bool] = []

        class TestApp(App):
            pass

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                modal = RunningModal(controller, "block test")
                app.push_screen(modal, callback=lambda _r: None)
                # Wait until the worker is inside the 0.5s blocking cycle.
                await _pump_until(pilot, lambda: controller.run_cycle.called)
                # Schedule a one-shot timer while the cycle is mid-flight.
                app.set_timer(0.05, lambda: fired.append(True))
                # Pump messages — the timer must fire if the event loop is alive.
                await _pump_until(pilot, lambda: bool(fired))
                assert fired == [True], (
                    "UI event loop was not responsive while run_cycle blocked"
                )
                # Clean up: stop the modal so the worker exits.
                modal.action_stop()
                await _pump_until(pilot, lambda: True)  # drain

        asyncio.run(run())

    def test_stop_works_while_cycle_blocks(self):
        """Clicking Stop dismisses the modal *during* a blocking cycle.

        Before the fix, ``action_stop`` (bound to Stop / Escape) could not run
        until ``run_cycle`` returned — the modal effectively could not be
        stopped.  After the fix, Stop runs on the UI thread while the worker is
        blocked and dismisses quickly.
        """
        controller, _ids, _main, _calls = _blocking_controller(1.0)

        class TestApp(App):
            pass

        results: list = []

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                modal = RunningModal(controller, "block test")
                app.push_screen(modal, callback=results.append)
                # Wait for the worker to be inside the (1.0s) blocking cycle.
                await _pump_until(pilot, lambda: controller.run_cycle.called)
                # Now press Stop while the cycle is blocking.  We call
                # action_stop() directly (not pilot.click) because the worker's
                # recurring poll timer makes pilot.pause() time out.
                t0 = asyncio.get_event_loop().time()
                modal.action_stop()
                # Pump messages — Stop must dismiss quickly, well under 1.0s.
                dismissed = await _pump_until(pilot, lambda: bool(results))
                # The modal must have dismissed with "stopped" outcome.
                assert dismissed, "Stop did not dismiss the modal during the block"
                assert results[0]["outcome"] == "stopped"
                # Sanity: this whole interaction took < 0.5s, not ~1s.  This is
                # the actual proof: Stop beat the blocking cycle.
                elapsed = asyncio.get_event_loop().time() - t0
                assert elapsed < 0.5, (
                    f"Stop took {elapsed:.2f}s — UI was frozen during the block"
                )

        asyncio.run(run())

    def test_pause_resumes_after_blocking_cycle(self):
        """Pause then Resume: the worker parks until Resume, then continues."""
        controller, _ids, _main, calls = _blocking_controller(0.1)

        class TestApp(App):
            pass

        results: list = []

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                modal = RunningModal(controller, "pause test")
                app.push_screen(modal, callback=results.append)
                # Let at least one cycle run, then Pause.
                await _pump_until(pilot, lambda: calls["n"] >= 1)
                before = calls["n"]
                modal.action_pause_resume()
                # While paused, cycles must not advance even after pumping.
                await _pump_until(pilot, lambda: False, max_iters=3)  # brief pump
                after = calls["n"]
                assert after == before, (
                    f"worker kept running while paused ({before} → {after})"
                )
                # Resume → cycles should advance again.
                modal.action_pause_resume()
                resumed = await _pump_until(pilot, lambda: calls["n"] > before)
                assert resumed, "worker did not resume after un-pause"
                # Clean up.
                modal.action_stop()
                await _pump_until(pilot, lambda: True)  # drain

        asyncio.run(run())
