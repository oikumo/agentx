"""Integration tests — Textual pilot for AgentDemoScreen (feature_010)."""

from __future__ import annotations

import asyncio

import pytest

from agentx.agent.controller.agent_controller import AgentController
from agentx.agent.interfaces import IAgentViewPartner
from agentx.agent.model.agent import Agent
from agentx.agent.view.tui.agent_screen import AgentTUIScreen
from agentx.agent.view.tui.demo_screen import AgentDemoScreen


@pytest.fixture()
def wired_screen(agent_config):
    """A wired agent + controller + demo screen (scenario a)."""
    agent = Agent(agent_config)
    controller = AgentController(agent)
    screen = AgentDemoScreen(controller, scenario_name="a")
    return agent, controller, screen


class TestAgentDemoScreenBasics:
    def test_is_view_partner(self, wired_screen):
        _, _, screen = wired_screen
        assert isinstance(screen, IAgentViewPartner)

    def test_bindings(self, wired_screen):
        _, _, screen = wired_screen
        keys = [b.key for b in screen.BINDINGS]
        assert "r" in keys  # run cycle
        assert "x" in keys  # reset
        assert "escape" in keys  # back

    def test_has_buttons(self, wired_screen):
        _, _, screen = wired_screen
        from textual.app import App, ComposeResult

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield screen

        async def run() -> None:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                ids = [b.id for b in app.query("Button")]
                assert "btn-run" in ids
                assert "btn-reset" in ids
                assert "btn-back" in ids

        asyncio.run(run())


class TestAgentDemoScreenPilot:
    def test_mount_auto_loads_scenario_and_runs_cycle(self, wired_screen):
        """On mount the screen loads scenario A and auto-runs one cycle."""
        from textual.app import App, ComposeResult
        from textual.widgets import RichLog, Static

        agent, controller, screen = wired_screen

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield screen

        async def run() -> None:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                # status bar widget rendered
                status = app.query_one("#demo-status", Static)
                assert status is not None
                # scenario goal was loaded
                assert len(controller.list_goals().nodes) == 1
                # log has cycle narration
                log = app.query_one("#demo-log", RichLog)
                assert log is not None
                # the auto-cycle ran: target.txt read -> goal completed
                from agentx.agent.types import GoalStatus

                goal = list(controller.list_goals().nodes.values())[0]
                assert goal.status == GoalStatus.COMPLETED

        asyncio.run(run())

    def test_run_cycle_button(self, wired_screen):
        """Pressing the Run Cycle button steps a cycle."""
        from textual.app import App, ComposeResult

        agent, controller, screen = wired_screen

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield screen

        async def run() -> None:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                # reset first to get a fresh active goal, then run
                await pilot.press("x")
                await pilot.pause()
                await pilot.press("r")
                await pilot.pause()
                # a cycle ran without crashing
                assert len(controller.list_goals().nodes) == 1

        asyncio.run(run())

    def test_reset_button_reseeds(self, wired_screen):
        """Pressing Reset clears + re-seeds the scenario."""
        from textual.app import App, ComposeResult

        agent, controller, screen = wired_screen

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield screen

        async def run() -> None:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                # after mount, one auto-cycle ran (goal completed, memory grown)
                assert agent.memory.count_volatile() > 0
                # press reset
                await pilot.press("x")
                await pilot.pause()
                # memory cleared (re-seeded) and goal back to a fresh scenario goal
                assert agent.memory.count_volatile() == 0
                assert len(controller.list_goals().nodes) == 1

        asyncio.run(run())


class TestAgentTUIScreenDemoWiring:
    """The AgentTUIScreen must expose the demo command + action_open_demo."""

    def test_agent_screen_has_demo_binding(self, agent_config):
        agent = Agent(agent_config)
        controller = AgentController(agent)
        screen = AgentTUIScreen(controller)
        keys = [b.key for b in screen.BINDINGS]
        assert "d" in keys  # demo keybinding

    def test_agent_screen_action_open_demo_exists(self, agent_config):
        agent = Agent(agent_config)
        controller = AgentController(agent)
        screen = AgentTUIScreen(controller)
        assert hasattr(screen, "action_open_demo")
        assert hasattr(screen, "_cmd_demo")

    def test_demo_command_dispatches_to_action(self, agent_config, monkeypatch):
        """Typing 'demo b' calls action_open_demo with 'b'."""
        agent = Agent(agent_config)
        controller = AgentController(agent)
        screen = AgentTUIScreen(controller)
        called: list[str] = []

        def fake_action(scenario_name: str = "a") -> None:
            called.append(scenario_name)

        monkeypatch.setattr(screen, "action_open_demo", fake_action)
        screen._dispatch_command("demo b")
        assert called == ["b"]

        screen._dispatch_command("demo")
        assert called == ["b", "a"]
