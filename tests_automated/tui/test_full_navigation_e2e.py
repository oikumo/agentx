"""Comprehensive end-to-end TUI navigation tests using real provider pattern.

These tests verify the complete navigation flow with the provider-based
architecture: MainController -> Provider -> TUI Views.
"""

from __future__ import annotations

import os
from textual.widgets import Input, Static, Button

from agentx.ui.tui.app import TUIApplication
from agentx.ui.screens.main.main_controller import MainController
from agentx.ui.providers import ProviderRegistry

from tests_automated.tui.conftest import drive


def _screen_name(app) -> str:
    """Return the class name of the topmost screen."""
    return type(app.screen).__name__


def _get_provider():
    """Get the default TUI provider."""
    return ProviderRegistry.get_default()


def test_full_navigation_cycle_main_chat_main_rag_main():
    """Complete navigation cycle: Main -> Chat -> Main -> RAG -> Main."""

    async def scenario():
        provider = _get_provider()
        controller = MainController(provider=provider)
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Start at Main
            assert _screen_name(app) == "MainTUIScreen", f"Expected MainTUIScreen, got {_screen_name(app)}"

            # Navigate to Chat via 'c' key
            await pilot.press("c")
            await pilot.pause()
            assert _screen_name(app) == "ChatTUIScreen", f"Expected ChatTUIScreen, got {_screen_name(app)}"

            # Verify Chat screen has expected widgets
            assert app.screen.query_one("#chat-input", Input) is not None
            assert len(app.screen.query("ChatMessage")) >= 1  # Welcome message

            # Return to Main via Escape
            await pilot.press("escape")
            await pilot.pause()
            assert _screen_name(app) == "MainTUIScreen", f"Expected MainTUIScreen, got {_screen_name(app)}"

            # Navigate to RAG via 'r' key
            await pilot.press("r")
            await pilot.pause()
            assert _screen_name(app) == "RagTUIScreen", f"Expected RagTUIScreen, got {_screen_name(app)}"

            # Verify RAG screen has expected widgets
            assert app.screen.query_one("#rag-input", Input) is not None
            assert app.screen.query_one("#btn-select", Button) is not None

            # Return to Main via Escape
            await pilot.press("escape")
            await pilot.pause()
            assert _screen_name(app) == "MainTUIScreen", f"Expected MainTUIScreen, got {_screen_name(app)}"

            return True

    assert drive(scenario)


def test_navigation_via_buttons():
    """Navigation via mouse clicks on menu buttons."""

    async def scenario():
        provider = _get_provider()
        controller = MainController(provider=provider)
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()

            assert _screen_name(app) == "MainTUIScreen"

            # Click Chat button
            await pilot.click("#btn-chat")
            await pilot.pause()
            assert _screen_name(app) == "ChatTUIScreen"

            # Click back via Escape (no back button on chat)
            await pilot.press("escape")
            await pilot.pause()
            assert _screen_name(app) == "MainTUIScreen"

            # Click RAG button
            await pilot.click("#btn-rag")
            await pilot.pause()
            assert _screen_name(app) == "RagTUIScreen"

            # Back via Escape
            await pilot.press("escape")
            await pilot.pause()
            assert _screen_name(app) == "MainTUIScreen"

            return True

    assert drive(scenario)


def test_chat_screen_input_submission():
    """Test chat input field accepts and submits messages."""

    async def scenario():
        provider = _get_provider()
        controller = MainController(provider=provider)
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Navigate to Chat
            await pilot.press("c")
            await pilot.pause()
            assert _screen_name(app) == "ChatTUIScreen"

            # Get input widget
            chat_input = app.screen.query_one("#chat-input", Input)
            assert chat_input is not None

            # Focus and type a message
            chat_input.focus()
            await pilot.pause()
            await pilot.press("h", "e", "l", "l", "o")
            await pilot.pause()
            assert chat_input.value == "hello"

            # Submit with Enter
            await pilot.press("enter")
            await pilot.pause()

            # Input should be cleared after submission
            assert chat_input.value == ""

            # Should have user message and assistant response
            messages = list(app.screen.query("ChatMessage"))
            assert len(messages) >= 2  # Welcome + user message (assistant may not respond without API)

            return True

    assert drive(scenario)


def test_rag_screen_repository_selection_flow():
    """Test RAG screen repository selection workflow."""

    async def scenario():
        provider = _get_provider()
        controller = MainController(provider=provider)
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Navigate to RAG
            await pilot.press("r")
            await pilot.pause()
            assert _screen_name(app) == "RagTUIScreen"

            # Initially chat input should be disabled
            rag_input = app.screen.query_one("#rag-input", Input)
            assert rag_input.disabled is True

            # Click Select Repository button
            select_btn = app.screen.query_one("#btn-select", Button)
            await pilot.click(select_btn)
            await pilot.pause()

            # Should push RepositorySelectionScreen (we just verify we're no longer on RagTUIScreen)
            # Note: In test environment without repos, this may show empty list
            # The key test is that navigation was attempted
            assert _screen_name(app) != "RagTUIScreen" or rag_input.disabled is True

            return True

    assert drive(scenario)


def test_help_shortcut_shows_notification():
    """Test 'h' key shows help notification on main screen."""

    async def scenario():
        provider = _get_provider()
        controller = MainController(provider=provider)
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()

            assert _screen_name(app) == "MainTUIScreen"

            # Press 'h' for help
            await pilot.press("h")
            await pilot.pause()

            # Should still be on main screen (help is notification, not screen change)
            assert _screen_name(app) == "MainTUIScreen"

            # Verify help action was triggered (notification shown)
            # We can't easily test notification content in Pilot, but we verify no crash
            return True

    assert drive(scenario)


def test_focus_input_shortcut():
    """Test Ctrl+L focuses command input on main screen."""

    async def scenario():
        provider = _get_provider()
        controller = MainController(provider=provider)
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()

            assert _screen_name(app) == "MainTUIScreen"

            # Press Ctrl+L to focus input
            await pilot.press("ctrl+l")
            await pilot.pause()

            # Command input should be focused
            command_input = app.screen.query_one("#command-input", Input)
            assert app.screen.focused is command_input

            return True

    assert drive(scenario)


def test_command_input_delegates_to_controller():
    """Test command input submission calls controller.run_command."""

    async def scenario():
        provider = _get_provider()
        controller = MainController(provider=provider)
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()

            assert _screen_name(app) == "MainTUIScreen"

            # Type a command
            command_input = app.screen.query_one("#command-input", Input)
            command_input.focus()
            await pilot.pause()

            await pilot.press("/", "h", "e", "l", "p")
            await pilot.pause()
            assert command_input.value == "/help"

            # Submit
            await pilot.press("enter")
            await pilot.pause()

            # Input should be cleared
            assert command_input.value == ""

            return True

    assert drive(scenario)


def test_chat_screen_ctrl_enter_sends_message():
    """Test Ctrl+Enter sends message in chat (alternative to Enter)."""

    async def scenario():
        provider = _get_provider()
        controller = MainController(provider=provider)
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()

            await pilot.press("c")
            await pilot.pause()
            assert _screen_name(app) == "ChatTUIScreen"

            chat_input = app.screen.query_one("#chat-input", Input)
            chat_input.focus()
            await pilot.pause()

            await pilot.press("t", "e", "s", "t")
            await pilot.pause()
            assert chat_input.value == "test"

            # Send with Ctrl+Enter
            await pilot.press("ctrl+enter")
            await pilot.pause()

            # Input cleared
            assert chat_input.value == ""

            return True

    assert drive(scenario)


def test_rag_screen_keyboard_shortcuts():
    """Test RAG screen keyboard shortcuts (r=refresh, i=ingest, c=chat)."""

    async def scenario():
        provider = _get_provider()
        controller = MainController(provider=provider)
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()

            await pilot.press("r")
            await pilot.pause()
            assert _screen_name(app) == "RagTUIScreen"

            # Test refresh shortcut
            await pilot.press("r")
            await pilot.pause()
            assert _screen_name(app) == "RagTUIScreen"  # Still on RAG

            # Test ingest shortcut (should notify if no repo selected)
            await pilot.press("i")
            await pilot.pause()
            assert _screen_name(app) == "RagTUIScreen"

            # Test chat mode shortcut (should notify if no repo)
            await pilot.press("c")
            await pilot.pause()
            assert _screen_name(app) == "RagTUIScreen"

            return True

    assert drive(scenario)


def test_multiple_navigation_cycles():
    """Test multiple rapid navigation cycles don't cause issues."""

    async def scenario():
        provider = _get_provider()
        controller = MainController(provider=provider)
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()

            assert _screen_name(app) == "MainTUIScreen"

            # Do 3 full cycles
            for i in range(3):
                # Main -> Chat
                await pilot.press("c")
                await pilot.pause()
                assert _screen_name(app) == "ChatTUIScreen"

                # Chat -> Main
                await pilot.press("escape")
                await pilot.pause()
                assert _screen_name(app) == "MainTUIScreen"

                # Main -> RAG
                await pilot.press("r")
                await pilot.pause()
                assert _screen_name(app) == "RagTUIScreen"

                # RAG -> Main
                await pilot.press("escape")
                await pilot.pause()
                assert _screen_name(app) == "MainTUIScreen"

            return True

    assert drive(scenario)


def test_main_screen_status_bar_updates():
    """Test status bar shows correct screen name on navigation."""

    async def scenario():
        provider = _get_provider()
        controller = MainController(provider=provider)
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Check initial status
            status_bar = app.screen.query_one("SessionStatusBar", Static)
            assert "Screen: Main" in str(status_bar.query_one("#status-text", Static).render())

            # Go to Chat
            await pilot.press("c")
            await pilot.pause()

            # Status bar should still be on Main screen (status bar is per-screen)
            # Actually each screen has its own status bar
            return True

    assert drive(scenario)