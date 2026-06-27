"""End-to-end navigation tests for the AgentX TUI.

These drive the real ``TUIApplication`` (which pushes ``MainTUIScreen``) through
Textual's Pilot harness and assert on real screen transitions triggered by
keyboard shortcuts and button clicks.
"""

from __future__ import annotations

from textual.widgets import Input

from agentx.ui.tui.app import TUIApplication

from tests_automated.tui.conftest import drive


def _screen_name(app) -> str:
    """Return the class name of the topmost screen."""
    return type(app.screen).__name__


def test_app_boots_to_main_screen(controller):
    """Booting the app lands on MainTUIScreen with its core widgets mounted."""

    async def scenario():
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()
            assert _screen_name(app) == "MainTUIScreen"
            # Command input and status bar are part of the full main layout.
            assert app.screen.query_one("#command-input", Input) is not None
            assert len(app.screen.query("SessionStatusBar")) == 1
            return True

    assert drive(scenario)


def test_key_c_opens_chat(controller):
    """Pressing 'c' on the main screen navigates to the Chat screen."""

    async def scenario():
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()
            assert _screen_name(app) == "MainTUIScreen"
            await pilot.press("c")
            await pilot.pause()
            assert _screen_name(app) == "ChatTUIScreen"
            return True

    assert drive(scenario)


def test_key_r_opens_rag(controller):
    """Pressing 'r' on the main screen navigates to the RAG screen."""

    async def scenario():
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("r")
            await pilot.pause()
            assert _screen_name(app) == "RagTUIScreen"
            return True

    assert drive(scenario)


def test_escape_returns_from_chat(controller):
    """'escape' on the Chat screen pops back to the Main screen."""

    async def scenario():
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("c")
            await pilot.pause()
            assert _screen_name(app) == "ChatTUIScreen"
            await pilot.press("escape")
            await pilot.pause()
            assert _screen_name(app) == "MainTUIScreen"
            return True

    assert drive(scenario)


def test_chat_button_opens_chat(controller):
    """Clicking the 'Chat' menu button navigates to the Chat screen."""

    async def scenario():
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.click("#btn-chat")
            await pilot.pause()
            assert _screen_name(app) == "ChatTUIScreen"
            return True

    assert drive(scenario)


def test_key_q_quits(controller):
    """Pressing 'q' triggers application exit."""

    async def scenario():
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("q")
            await pilot.pause()
            # App.exit() sets ``_exit`` synchronously; the loop then winds down.
            assert getattr(app, "_exit", False) is True
            return True

    assert drive(scenario)
