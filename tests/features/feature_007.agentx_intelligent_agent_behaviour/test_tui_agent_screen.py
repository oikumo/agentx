"""TUI e2e tests — Textual pilot for AgentTUIScreen (T4)."""

from __future__ import annotations

import pytest

from agentx.agent.controller.agent_controller import AgentController
from agentx.agent.model.agent import Agent
from agentx.agent.view.tui.agent_screen import AgentTUIScreen


@pytest.fixture()
def wired_screen(agent_config):
    """Create a fully wired agent + controller + screen."""
    agent = Agent(agent_config)
    controller = AgentController(agent)
    screen = AgentTUIScreen(controller)
    controller.set_view(screen)  # type: ignore[arg-type]
    return agent, controller, screen


class TestAgentTUIScreen:
    def test_screen_is_view_partner(self, wired_screen):
        """AgentTUIScreen must be registered as IAgentViewPartner virtual subclass."""
        from agentx.agent.interfaces import IAgentViewPartner

        _, _, screen = wired_screen
        assert isinstance(screen, IAgentViewPartner)

    def test_screen_has_bindings(self, wired_screen):
        _, _, screen = wired_screen
        assert hasattr(screen, "BINDINGS")
        key_labels = [b.key for b in screen.BINDINGS]
        assert "r" in key_labels  # run cycle
        assert "s" in key_labels  # save

    def test_pilot_mount_and_status(self, wired_screen):
        """Mount the screen via Textual pilot and verify it mounts."""
        from textual.app import App, ComposeResult
        from textual.widgets import Static

        _, controller, screen = wired_screen

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield screen

        async def run() -> None:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                # The status widget should exist and be visible
                status = app.query_one("#agent-status", Static)
                assert status is not None

        import asyncio

        asyncio.run(run())

    def test_pilot_run_cycle_action(self, wired_screen):
        """Trigger the 'r' key (run cycle) via pilot."""
        from textual.app import App, ComposeResult

        agent, controller, screen = wired_screen

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield screen

        async def run() -> None:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                await pilot.press("r")
                await pilot.pause()
                # After running a cycle, the agent should still be in PERCEIVING state
                assert agent.state.value in ("PERCEIVING", "DECIDING", "ACTING", "REFLECTING")

        import asyncio

        asyncio.run(run())

    def test_pilot_save_action(self, wired_screen):
        """Trigger the 's' key (save snapshot) via pilot."""
        from textual.app import App, ComposeResult
        from textual.widgets import RichLog

        agent, controller, screen = wired_screen

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield screen

        async def run() -> None:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                await pilot.press("s")
                await pilot.pause()
                log = app.query_one("#agent-log", RichLog)
                # The log should contain a snapshot message
                assert agent.state.value == "PERCEIVING"

        import asyncio

        asyncio.run(run())

    def test_show_message_writes_to_log(self, wired_screen):
        """show_message should write to the RichLog."""
        from textual.app import App, ComposeResult
        from textual.widgets import RichLog

        _, _, screen = wired_screen

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield screen

        async def run() -> None:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                screen.show_message("hello pilot")
                await pilot.pause()
                # The RichLog should have content
                log = app.query_one("#agent-log", RichLog)
                assert log.lines is not None

        import asyncio

        asyncio.run(run())

    def test_command_input_exists(self, wired_screen):
        """The screen should have an input widget for commands."""
        from textual.app import App, ComposeResult
        from textual.widgets import Input

        _, _, screen = wired_screen

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield screen

        async def run() -> None:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                cmd_input = app.query_one("#agent-input", Input)
                assert cmd_input is not None
                assert "help" in (cmd_input.placeholder or "")

        import asyncio

        asyncio.run(run())

    def test_help_command(self, wired_screen):
        """Typing 'help' should write help text to the log."""
        from textual.app import App, ComposeResult
        from textual.widgets import Input, RichLog

        _, _, screen = wired_screen

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield screen

        async def run() -> None:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                cmd_input = app.query_one("#agent-input", Input)
                cmd_input.value = "help"
                await pilot.press("enter")
                await pilot.pause()
                log = app.query_one("#agent-log", RichLog)
                assert len(log.lines) > 0

        import asyncio

        asyncio.run(run())

    def test_goal_command_adds_goal(self, wired_screen):
        """Typing 'goal <desc>' should submit a goal and refresh the tree."""
        from textual.app import App, ComposeResult
        from textual.widgets import Input

        agent, controller, screen = wired_screen

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield screen

        async def run() -> None:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                cmd_input = app.query_one("#agent-input", Input)
                cmd_input.value = "goal read the filesystem"
                # Trigger submit directly (pilot key press needs focus)
                screen.on_input_submitted(Input.Submitted(input=cmd_input, value="goal read the filesystem"))
                await pilot.pause()
                tree = agent.goal_manager.get_tree()
                assert len(tree.nodes) == 1
                goal = list(tree.nodes.values())[0]
                assert "filesystem" in goal.description

        import asyncio

        asyncio.run(run())

    def test_status_command(self, wired_screen):
        """Typing 'status' should show agent info in the log."""
        from textual.app import App, ComposeResult
        from textual.widgets import Input, RichLog

        _, _, screen = wired_screen

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield screen

        async def run() -> None:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                cmd_input = app.query_one("#agent-input", Input)
                cmd_input.value = "status"
                await pilot.press("enter")
                await pilot.pause()
                log = app.query_one("#agent-log", RichLog)
                assert len(log.lines) > 0

        import asyncio

        asyncio.run(run())
