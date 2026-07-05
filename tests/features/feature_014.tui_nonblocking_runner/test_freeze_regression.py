"""Freeze regression tests for AgentTUIScreen + AgentDemoScreen (feature_014).

These tests prove the framework-level freeze fix: ``run_cycle()`` used to run
on the Textual UI thread and blocked on ``llm.invoke()``, freezing the entire
event loop (Escape/Back unresponsive).  Now ``run_cycle()`` runs via
``BaseAgentXScreen.run_blocking()`` on a daemon worker thread; the UI thread
polls a queue and stays responsive.

Strategy mirrors ``TestRunningModalFreezeFix`` in feature_011: a controller
whose ``run_cycle()`` sleeps for a fixed duration.  Because ``run_cycle`` runs
on the worker, the UI event loop keeps running timers, so we can interact
(Escape) while the cycle is "blocking".

Pattern: push the screen *after* the app is running (via ``app.push_screen``),
matching feature_011/feature_012's test approach.  The screen is accessed via
``app.screen``, narrowed to ``Any`` so the type checker allows action calls.
"""

from __future__ import annotations

import asyncio
import threading
import time
from typing import Any
from unittest.mock import MagicMock

from textual.app import App


# ============================================================================
# Helpers
# ============================================================================


def _blocking_controller(block_seconds: float = 0.3):
    """Build a MagicMock controller that blocks inside ``run_cycle``.

    Returns ``(controller, run_cycle_thread_ids, main_thread_id, call_count)``.
    """
    main_thread_id = threading.get_ident()
    run_cycle_thread_ids: list[int] = []
    call_count: dict[str, int] = {"n": 0}

    controller = MagicMock()

    def run_cycle():
        run_cycle_thread_ids.append(threading.get_ident())
        call_count["n"] += 1
        time.sleep(block_seconds)  # simulate llm.invoke() HTTP call
        result = MagicMock()
        result.decision.reasoning = "test decision"
        result.decision.confidence = 0.9
        result.decision.alternatives = []
        result.action_result = None
        result.reflection = None
        return result

    controller.run_cycle.side_effect = run_cycle
    controller.get_status.return_value = {
        "name": "test",
        "state": "ACTIVE",
        "goals": 1,
        "rules": 0,
        "tools": 0,
        "memory_entries": 0,
    }
    controller.list_goals.return_value = MagicMock(nodes={}, root=None)
    controller.save_snapshot.return_value = "snap-1234-abcd"
    return controller, run_cycle_thread_ids, main_thread_id, call_count


async def _pump_until(pilot, condition, *, max_iters: int = 30, interval: float = 0.05):
    """Process Textual messages in short bursts until *condition* is true."""
    for _ in range(max_iters):
        await asyncio.sleep(interval)
        if condition():
            return True
    return condition()


# ============================================================================
# AgentTUIScreen — freeze regression
# ============================================================================


class TestAgentScreenFreezeFix:
    """Regression: the Advanced Agent screen must not freeze while run_cycle blocks."""

    def test_run_cycle_runs_off_ui_thread(self):
        """``run_cycle()`` must execute on a worker thread, not the UI thread."""
        from agentx.agent.view.tui.agent_screen import AgentTUIScreen

        controller, ids, main_thread_id, _calls = _blocking_controller(0.3)

        class TestApp(App):
            pass

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                app.push_screen(AgentTUIScreen(controller))
                await pilot.pause()
                await pilot.pause()
                screen: Any = app.screen
                screen.action_run_cycle()
                started = await _pump_until(pilot, lambda: len(ids) >= 1)
                assert started, "run_cycle was never called"
                assert ids[0] != main_thread_id, (
                    "run_cycle ran on the UI thread — UI will freeze"
                )
                # Wait for the cycle to finish so the worker exits cleanly.
                await _pump_until(pilot, lambda: _calls["n"] >= 1)
                await asyncio.sleep(0.1)

        asyncio.run(run())

    def test_event_loop_responsive_during_blocking_cycle(self):
        """A UI timer must fire while the worker is blocked in run_cycle."""
        from agentx.agent.view.tui.agent_screen import AgentTUIScreen

        controller, _ids, _main, _calls = _blocking_controller(0.5)
        fired: list[bool] = []

        class TestApp(App):
            pass

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                app.push_screen(AgentTUIScreen(controller))
                await pilot.pause()
                await pilot.pause()
                screen: Any = app.screen
                screen.action_run_cycle()
                # Wait until the worker is inside the 0.5s blocking cycle.
                await _pump_until(pilot, lambda: controller.run_cycle.called)
                # Schedule a one-shot timer while the cycle is mid-flight.
                app.set_timer(0.05, lambda: fired.append(True))
                # Pump messages — the timer must fire if the event loop is alive.
                await _pump_until(pilot, lambda: bool(fired))
                assert fired == [True], (
                    "UI event loop was not responsive while run_cycle blocked"
                )
                # Clean up: wait for the cycle to finish.
                await _pump_until(pilot, lambda: True)

        asyncio.run(run())

    def test_escape_works_while_cycle_blocks(self):
        """Pressing Back during a blocking cycle must respond quickly."""
        from agentx.agent.view.tui.agent_screen import AgentTUIScreen

        controller, _ids, _main, _calls = _blocking_controller(1.0)

        class TestApp(App):
            pass

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                app.push_screen(AgentTUIScreen(controller))
                await pilot.pause()
                await pilot.pause()
                screen: Any = app.screen
                screen.action_run_cycle()
                # Wait for the worker to be inside the (1.0s) blocking cycle.
                await _pump_until(pilot, lambda: controller.run_cycle.called)
                # Now call on_unmount (simulates pop_screen / Escape).
                t0 = asyncio.get_event_loop().time()
                screen.on_unmount()
                # The unmount must be near-instant (< 0.1s), not ~1.0s.
                elapsed = asyncio.get_event_loop().time() - t0
                assert elapsed < 0.1, (
                    f"on_unmount took {elapsed:.2f}s — UI was frozen during the block"
                )
                # Drain.
                await _pump_until(pilot, lambda: True)

        asyncio.run(run())

    def test_save_runs_off_ui_thread(self):
        """``save_snapshot()`` must execute on a worker thread."""
        from agentx.agent.view.tui.agent_screen import AgentTUIScreen

        main_thread_id = threading.get_ident()
        save_thread_ids: list[int] = []
        controller = MagicMock()

        def save_snapshot():
            save_thread_ids.append(threading.get_ident())
            time.sleep(0.2)
            return "snap-1234"

        controller.save_snapshot.side_effect = save_snapshot
        controller.get_status.return_value = {}
        controller.list_goals.return_value = MagicMock(nodes={}, root=None)

        class TestApp(App):
            pass

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                app.push_screen(AgentTUIScreen(controller))
                await pilot.pause()
                await pilot.pause()
                screen: Any = app.screen
                screen.action_save()
                started = await _pump_until(pilot, lambda: len(save_thread_ids) >= 1)
                assert started, "save_snapshot was never called"
                assert save_thread_ids[0] != main_thread_id, (
                    "save_snapshot ran on the UI thread"
                )
                await _pump_until(pilot, lambda: True)

        asyncio.run(run())


# ============================================================================
# AgentDemoScreen — freeze regression
# ============================================================================


class TestDemoScreenFreezeFix:
    """Regression: the Agent Demo screen must not freeze while run_cycle blocks."""

    def test_run_cycle_runs_off_ui_thread(self):
        """``run_cycle()`` must execute on a worker thread, not the UI thread."""
        from agentx.agent.view.tui.demo_screen import AgentDemoScreen

        controller, ids, main_thread_id, _calls = _blocking_controller(0.3)

        class TestApp(App):
            pass

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                app.push_screen(AgentDemoScreen(controller, scenario_name="a"))
                await pilot.pause()
                await pilot.pause()
                screen: Any = app.screen
                # The demo auto-runs on mount, but also trigger explicitly.
                screen.action_run_cycle()
                started = await _pump_until(pilot, lambda: len(ids) >= 1)
                assert started, "run_cycle was never called"
                assert ids[0] != main_thread_id, (
                    "run_cycle ran on the UI thread — UI will freeze"
                )
                await _pump_until(pilot, lambda: True)

        asyncio.run(run())

    def test_event_loop_responsive_during_blocking_cycle(self):
        """A UI timer must fire while the worker is blocked in run_cycle."""
        from agentx.agent.view.tui.demo_screen import AgentDemoScreen

        controller, _ids, _main, _calls = _blocking_controller(0.5)
        fired: list[bool] = []

        class TestApp(App):
            pass

        async def run():
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                app.push_screen(AgentDemoScreen(controller, scenario_name="a"))
                await pilot.pause()
                await pilot.pause()
                screen: Any = app.screen
                screen.action_run_cycle()
                await _pump_until(pilot, lambda: controller.run_cycle.called)
                app.set_timer(0.05, lambda: fired.append(True))
                await _pump_until(pilot, lambda: bool(fired))
                assert fired == [True], (
                    "UI event loop was not responsive while run_cycle blocked"
                )
                await _pump_until(pilot, lambda: True)

        asyncio.run(run())
