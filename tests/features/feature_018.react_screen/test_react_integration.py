"""Integration tests for the ReAct screen Main screen wiring.

Tests:
  - MainController.show_react / get_react_controller
  - MainTUIScreen action_open_react binding + button
  - MenuGrid has btn-react button
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest


class TestMainControllerReAct:
    """Tests for MainController ReAct integration."""

    def test_main_controller_show_react_creates_controller(self) -> None:
        """show_react should create and wire a ReactController."""
        from agentx.ui.screens.main.main_controller import MainController
        from agentx.ui.screens.react.react_controller import ReactController

        with patch("agentx.ui.screens.react.react_controller.ReactController") as mock_react_cls:
            mock_react = MagicMock()
            mock_react_cls.return_value = mock_react

            controller = MainController()
            controller.show_react()

            assert controller._react_controller is mock_react
            mock_react_cls.assert_called_once()

    def test_main_controller_show_react_idempotent(self) -> None:
        """Second call to show_react should reuse existing controller (C5 pattern)."""
        from agentx.ui.screens.main.main_controller import MainController
        from agentx.ui.screens.react.react_controller import ReactController

        with patch("agentx.ui.screens.react.react_controller.ReactController") as mock_react_cls:
            mock_react = MagicMock()
            mock_react_cls.return_value = mock_react

            controller = MainController()
            controller.show_react()
            controller.show_react()  # Second call

            # Should only create once
            assert mock_react_cls.call_count == 1

    def test_main_controller_get_react_controller(self) -> None:
        """get_react_controller should return the wired controller."""
        from agentx.ui.screens.main.main_controller import MainController
        from agentx.ui.screens.react.react_controller import ReactController

        with patch("agentx.ui.screens.react.react_controller.ReactController") as mock_react_cls:
            mock_react = MagicMock()
            mock_react_cls.return_value = mock_react

            controller = MainController()
            controller.show_react()

            result = controller.get_react_controller()
            assert result is mock_react


class TestMainScreenReAct:
    """Tests for MainTUIScreen ReAct integration."""

    def test_main_screen_has_react_binding(self) -> None:
        """MainTUIScreen.BINDINGS should include 't' for ReAct."""
        from agentx.ui.tui.screens.main_screen import MainTUIScreen

        bindings = [b.key for b in MainTUIScreen.BINDINGS]
        assert "t" in bindings

    def test_main_screen_has_react_action(self) -> None:
        """MainTUIScreen should have action_open_react method."""
        from agentx.ui.tui.screens.main_screen import MainTUIScreen

        assert hasattr(MainTUIScreen, "action_open_react")

    def test_main_screen_action_open_react_navigates(self) -> None:
        """action_open_react should call navigate_to_child with ReactTUIScreen."""
        from agentx.ui.tui.screens.main_screen import MainTUIScreen
        from agentx.ui.tui.screens.react_screen import ReactTUIScreen

        mock_controller = MagicMock()
        mock_controller.show_react = MagicMock()
        mock_controller.get_react_controller = MagicMock(return_value=(MagicMock(), None))

        screen = MainTUIScreen(mock_controller)

        with patch.object(screen, "navigate_to_child") as mock_nav:
            screen.action_open_react()
            mock_nav.assert_called_once()

            # Check the screen class passed
            args, kwargs = mock_nav.call_args
            assert args[0] is ReactTUIScreen

    def test_main_screen_button_handler_react(self) -> None:
        """on_button_pressed with btn-react should call action_open_react."""
        from agentx.ui.tui.screens.main_screen import MainTUIScreen

        mock_controller = MagicMock()
        screen = MainTUIScreen(mock_controller)

        with patch.object(screen, "action_open_react") as mock_action:
            mock_event = MagicMock()
            mock_event.button.id = "btn-react"
            screen.on_button_pressed(mock_event)
            mock_action.assert_called_once()


class TestMenuGridReAct:
    """Tests for MenuGrid ReAct button."""

    def test_menu_grid_has_react_button(self) -> None:
        """MenuGrid should yield a Button with id='btn-react'."""
        from agentx.ui.tui.framework.widgets import MenuGrid

        grid = MenuGrid()
        children = list(grid.compose())
        button_ids = [c.id for c in children if hasattr(c, "id")]
        assert "btn-react" in button_ids


class TestMainScreenReActPilot:
    """Pilot tests for ReAct integration on Main screen."""

    def test_main_screen_t_opens_react(self) -> None:
        """Pressing 't' on Main screen should push ReactTUIScreen."""
        from agentx.ui.tui.screens.main_screen import MainTUIScreen
        from agentx.ui.tui.screens.react_screen import ReactTUIScreen
        from textual.app import App, ComposeResult

        mock_main_controller = MagicMock()
        mock_main_controller.show_react = MagicMock()
        mock_main_controller.get_react_controller = MagicMock(return_value=(MagicMock(), None))

        class TestApp(App):
            def compose(self) -> ComposeResult:
                from textual.widgets import Label
                yield Label("host")

            def on_mount(self) -> None:
                self.push_screen(MainTUIScreen(mock_main_controller))

        async def run() -> None:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause(0.1)
                # Press 't'
                await pilot.press("t")
                await pilot.pause(0.2)
                # Should be on ReactTUIScreen
                assert isinstance(app.screen, ReactTUIScreen)

        asyncio.run(run())

    def test_main_screen_btn_react_click(self) -> None:
        """Clicking the ReAct button should push ReactTUIScreen."""
        from agentx.ui.tui.screens.main_screen import MainTUIScreen
        from agentx.ui.tui.screens.react_screen import ReactTUIScreen
        from textual.app import App, ComposeResult
        from textual.widgets import Button

        mock_main_controller = MagicMock()
        mock_main_controller.show_react = MagicMock()
        mock_main_controller.get_react_controller = MagicMock(return_value=(MagicMock(), None))

        class TestApp(App):
            def compose(self) -> ComposeResult:
                from textual.widgets import Label
                yield Label("host")

            def on_mount(self) -> None:
                self.push_screen(MainTUIScreen(mock_main_controller))

        async def run() -> None:
            app = TestApp()
            async with app.run_test() as pilot:
                await pilot.pause(0.1)
                # Click the ReAct button
                btn = app.screen.query_one("#btn-react", Button)
                await pilot.click(btn)
                await pilot.pause(0.2)
                assert isinstance(app.screen, ReactTUIScreen)

        asyncio.run(run())


class TestMainControllerReActClose:
    """Tests for ReactController close behavior."""

    def test_main_controller_react_close_cancels(self) -> None:
        """Calling close on ReactController should cancel the agent."""
        from agentx.ui.screens.react.react_controller import ReactController

        mock_service = MagicMock()
        mock_service.is_running = True
        controller = ReactController(service=mock_service)
        controller.close()
        mock_service.cancel.assert_called_once()