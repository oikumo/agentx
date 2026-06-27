"""End-to-end tests for the Main screen command input.

Verifies the View -> Controller wiring: typing a command into the input and
submitting it reaches ``controller.run_command`` with the exact text, and the
input field behaves correctly (cleared after submit, empty submit is a no-op).
"""

from __future__ import annotations

from textual.widgets import Input

from agentx.ui.tui.app import TUIApplication

from tests_automated.tui.conftest import drive


async def _focus_command_input(app, pilot):
    """Focus the main screen command input and return the widget."""
    command_input = app.screen.query_one("#command-input", Input)
    command_input.focus()
    await pilot.pause()
    return command_input


def test_command_submit_delegates_to_controller(controller):
    """Typing a command and pressing enter delegates to the controller."""

    async def scenario():
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()
            await _focus_command_input(app, pilot)

            await pilot.press("h", "e", "l", "p")
            await pilot.press("enter")
            await pilot.pause()

            assert controller.commands == ["help"]
            return True

    assert drive(scenario)


def test_input_cleared_after_submit(controller):
    """The command input is emptied once a command is submitted."""

    async def scenario():
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()
            command_input = await _focus_command_input(app, pilot)

            await pilot.press("l", "s")
            assert command_input.value == "ls"
            await pilot.press("enter")
            await pilot.pause()

            assert command_input.value == ""
            assert controller.commands == ["ls"]
            return True

    assert drive(scenario)


def test_empty_input_is_noop(controller):
    """Submitting an empty command does not call the controller."""

    async def scenario():
        app = TUIApplication(controller)
        async with app.run_test() as pilot:
            await pilot.pause()
            await _focus_command_input(app, pilot)

            await pilot.press("enter")
            await pilot.pause()

            assert controller.commands == []
            return True

    assert drive(scenario)
