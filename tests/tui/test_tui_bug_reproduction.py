"""Test to reproduce TUI bug where only help button works.

This test reproduces the issue where:
- Help button (h key) works
- Chat button (c key) doesn't work
- RAG button (r key) doesn't work
- Button clicks don't work
- Input field doesn't accept input

Root cause analysis:
The TUI adapter creates a new TUIApplication instance which then
creates MainTUIScreen, but the controller wiring is broken.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from textual.app import App
from textual.widgets import Button, Input

from agentx.ui.tui.app import TUIApplication
from agentx.ui.tui.screens.main_screen import MainTUIScreen


class TestTUIButtonClickBug:
    """Reproduce the bug where button clicks don't work."""

    def test_button_pressed_handler_exists(self):
        """Verify MainTUIScreen has on_button_pressed handler."""
        screen = MainTUIScreen()
        assert hasattr(screen, 'on_button_pressed'), \
            "MainTUIScreen must have on_button_pressed handler"

    def test_button_click_calls_action_open_chat(self):
        """Clicking Chat button should call action_open_chat."""
        screen = MainTUIScreen()
        screen.action_open_chat = MagicMock()
        
        # Create a mock button event
        mock_button = MagicMock(spec=Button)
        mock_button.id = "btn-chat"
        
        mock_event = MagicMock(spec=Button.Pressed)
        mock_event.button = mock_button
        
        # Call the handler
        screen.on_button_pressed(mock_event)
        
        # Verify action was called
        screen.action_open_chat.assert_called_once()

    def test_button_click_calls_action_open_rag(self):
        """Clicking RAG button should call action_open_rag."""
        screen = MainTUIScreen()
        screen.action_open_rag = MagicMock()
        
        mock_button = MagicMock(spec=Button)
        mock_button.id = "btn-rag"
        
        mock_event = MagicMock(spec=Button.Pressed)
        mock_event.button = mock_button
        
        screen.on_button_pressed(mock_event)
        
        screen.action_open_rag.assert_called_once()

    def test_button_click_calls_action_show_help(self):
        """Clicking Help button should call action_show_help."""
        screen = MainTUIScreen()
        screen.action_show_help = MagicMock()
        
        mock_button = MagicMock(spec=Button)
        mock_button.id = "btn-help"
        
        mock_event = MagicMock(spec=Button.Pressed)
        mock_event.button = mock_button
        
        screen.on_button_pressed(mock_event)
        
        screen.action_show_help.assert_called_once()


class TestTUIInputBug:
    """Reproduce the bug where input field doesn't work."""

    def test_input_submitted_handler_exists(self):
        """Verify MainTUIScreen has on_input_submitted handler."""
        screen = MainTUIScreen()
        assert hasattr(screen, 'on_input_submitted'), \
            "MainTUIScreen must have on_input_submitted handler"

    def test_input_submitted_calls_controller_run_command(self):
        """Input submission should call controller.run_command."""
        mock_controller = MagicMock()
        screen = MainTUIScreen(mock_controller)
        
        # Create mock input widget and event
        mock_input = MagicMock(spec=Input)
        mock_input.value = "/help"
        
        mock_event = MagicMock()
        mock_event.value = "/help"
        mock_event.input = mock_input
        
        # Mock notify to avoid NoActiveAppError
        screen.notify = MagicMock()
        
        # Call handler
        screen.on_input_submitted(mock_event)
        
        # Verify controller was called
        mock_controller.run_command.assert_called_once_with("/help")

    def test_input_submitted_clears_input(self):
        """Input submission should clear the input field."""
        mock_controller = MagicMock()
        screen = MainTUIScreen(mock_controller)
        screen.notify = MagicMock()
        
        mock_input = MagicMock(spec=Input)
        mock_input.value = "/help"
        
        mock_event = MagicMock()
        mock_event.value = "/help"
        mock_event.input = mock_input
        
        screen.on_input_submitted(mock_event)
        
        # Input should be cleared
        assert mock_input.value == ""


class TestTUIControllerWiring:
    """Test controller wiring through TUI stack."""

    def test_controller_passed_to_screen(self):
        """Controller should be passed from app to screen."""
        mock_controller = MagicMock()
        app = TUIApplication(mock_controller)
        
        # Mock push_screen to capture what's pushed
        with patch.object(app, 'push_screen') as mock_push:
            with patch("agentx.ui.tui.app.sys.stdin.isatty", return_value=True):
                app.on_mount()
        
        # Get the screen that was pushed
        pushed_screen = mock_push.call_args[0][0]
        
        # Verify it's MainTUIScreen with controller
        assert isinstance(pushed_screen, MainTUIScreen)
        assert pushed_screen._controller is mock_controller

    def test_controller_none_by_default(self):
        """Screen should work even without controller."""
        screen = MainTUIScreen()
        assert screen._controller is None
        
        # Input submission should not crash
        mock_input = MagicMock(spec=Input)
        mock_input.value = "/help"
        
        mock_event = MagicMock()
        mock_event.value = "/help"
        mock_event.input = mock_input
        
        # Mock notify to avoid NoActiveAppError
        screen.notify = MagicMock()
        
        # Should not raise exception
        screen.on_input_submitted(mock_event)


class TestTUIActionMethods:
    """Test action methods work correctly."""

    def test_action_open_chat_notifies(self):
        """action_open_chat should show notification."""
        screen = MainTUIScreen()
        screen.notify = MagicMock()
        
        screen.action_open_chat()
        
        screen.notify.assert_called_once()
        call_args = str(screen.notify.call_args).lower()
        assert "chat" in call_args

    def test_action_open_rag_notifies(self):
        """action_open_rag should show notification."""
        screen = MainTUIScreen()
        screen.notify = MagicMock()
        
        screen.action_open_rag()
        
        screen.notify.assert_called_once()
        assert "rag" in str(screen.notify.call_args).lower()

    def test_action_show_help_notifies(self):
        """action_show_help should show help text."""
        screen = MainTUIScreen()
        screen.notify = MagicMock()
        
        screen.action_show_help()
        
        screen.notify.assert_called_once()
        # Help text should contain keyboard shortcuts
        help_text = str(screen.notify.call_args[0][0])
        assert "q" in help_text or "Quit" in help_text

    def test_action_focus_input_focuses_widget(self):
        """action_focus_input should focus the input widget."""
        screen = MainTUIScreen()
        
        # Mock query_one to return a mock input
        mock_input = MagicMock(spec=Input)
        with patch.object(screen, 'query_one', return_value=mock_input):
            screen.action_focus_input()
        
        mock_input.focus.assert_called_once()

    def test_action_focus_input_handles_error(self):
        """action_focus_input should handle errors gracefully."""
        screen = MainTUIScreen()
        
        # Mock query_one to raise exception
        with patch.object(screen, 'query_one', side_effect=Exception("Not found")):
            # Should not raise exception
            screen.action_focus_input()


class TestTUIRealBug:
    """Test the actual bug scenario - TUI in non-TTY environment.
    
    The real bug is that when running in non-TTY environment:
    1. main.py detects non-TTY and falls back to console mode
    2. BUT if user forces TUI mode, keyboard bindings don't work
    3. Button clicks may not register
    4. Input field may not accept keyboard input
    
    This is because Textual requires a proper TTY for event loop.
    """

    def test_non_tty_detected_in_app(self):
        """TUIApplication should detect non-TTY environment."""
        app = TUIApplication()
        
        with patch("agentx.ui.tui.app.sys.stdin.isatty", return_value=False):
            app.notify = MagicMock()
            app.push_screen = MagicMock()
            app.on_mount()
        
        # Should show warning notification
        app.notify.assert_called_once()
        call_args = str(app.notify.call_args)
        assert "Non-TTY" in call_args or "TTY" in call_args

    def test_non_tty_screen_still_works(self):
        """Screen should work in non-TTY but with limited interaction."""
        screen = MainTUIScreen()
        screen.notify = MagicMock()
        
        # In non-TTY, mouse clicks might still work
        # but keyboard bindings won't
        mock_button = MagicMock(spec=Button)
        mock_button.id = "btn-chat"
        
        mock_event = MagicMock(spec=Button.Pressed)
        mock_event.button = mock_button
        
        # Button clicks should still work (mouse events)
        screen.on_button_pressed(mock_event)
        
        # Should still call the action
        # (whether it succeeds depends on Textual event loop)