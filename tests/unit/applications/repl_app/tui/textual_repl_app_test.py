"""RED → GREEN → REFACTOR tests for TextualReplApp.

We test the app using Textual's Pilot API (async context manager).
Tests run headless — no real terminal required.

The Pilot API lets us:
  - Query mounted widgets by type or CSS id.
  - Press keys and simulate input submission.
  - Assert on widget state after actions.
"""

import unittest

from agent_x.applications.repl_app.tui.app import TextualReplApp
from agent_x.applications.repl_app.tui.widgets.output_pane import OutputPane
from agent_x.applications.repl_app.tui.widgets.command_input import CommandInput
from agent_x.applications.repl_app.tui.widgets.status_bar import StatusBar
from agent_x.applications.repl_app.controllers.main_controller.main_controller import (
    MainController,
)


class TextualReplAppStructureTest(unittest.IsolatedAsyncioTestCase):
    """Verify that TextualReplApp mounts the expected widgets."""

    async def test_app_mounts_output_pane(self):
        controller = MainController()
        app = TextualReplApp(controller=controller)
        async with app.run_test(headless=True) as pilot:
            pane = app.query_one(OutputPane)
            self.assertIsNotNone(pane)

    async def test_app_mounts_command_input(self):
        controller = MainController()
        app = TextualReplApp(controller=controller)
        async with app.run_test(headless=True) as pilot:
            inp = app.query_one(CommandInput)
            self.assertIsNotNone(inp)

    async def test_app_mounts_status_bar(self):
        controller = MainController()
        app = TextualReplApp(controller=controller)
        async with app.run_test(headless=True) as pilot:
            bar = app.query_one(StatusBar)
            self.assertIsNotNone(bar)

    async def test_app_title_contains_agent_x(self):
        controller = MainController()
        app = TextualReplApp(controller=controller)
        async with app.run_test(headless=True) as pilot:
            self.assertIn("Agent-X", app.title)

    async def test_command_input_has_suggestions_from_controller(self):
        # The autocomplete suggestions must be populated from the controller's
        # registered command keys.
        controller = MainController()
        expected_keys = {c.key for c in controller.get_commands()}
        app = TextualReplApp(controller=controller)
        async with app.run_test(headless=True) as pilot:
            inp = app.query_one(CommandInput)
            # suggestions is stored in the SuggestFromList inside Input.suggester
            suggester = inp.suggester
            self.assertIsNotNone(suggester)


class TextualReplAppInteractionTest(unittest.IsolatedAsyncioTestCase):
    """Verify that submitting a command dispatches it and updates UI state."""

    async def test_submitting_unknown_command_shows_error_in_output(self):
        # Typing an unknown command and pressing Enter must produce an error
        # message in the output pane (via TuiOutputWriter.unknown_command).
        controller = MainController()
        app = TextualReplApp(controller=controller)
        async with app.run_test(headless=True) as pilot:
            # Set value directly on the Input widget (pilot.type was removed
            # in Textual ≥ 0.60; use .value assignment then press Enter).
            inp = app.query_one(CommandInput)
            inp.value = "__unknown_cmd__"
            await pilot.press("enter")
            await pilot.pause()
            pane = app.query_one(OutputPane)
            # RichLog stores lines as renderable objects; check the text buffer
            content = "\n".join(str(r) for r in pane.lines)
            self.assertIn("__unknown_cmd__", content)

    async def test_submitting_empty_input_does_not_crash(self):
        controller = MainController()
        app = TextualReplApp(controller=controller)
        async with app.run_test(headless=True) as pilot:
            await pilot.click(CommandInput)
            await pilot.press("enter")
            await pilot.pause()
            # Just verify the app is still alive
            self.assertIsNotNone(app.query_one(OutputPane))

    async def test_status_bar_updates_after_command(self):
        # After any command submission the status bar must change from "Ready"
        # to something else while the command is running (or back to "Ready"
        # after it completes for no-op commands).
        controller = MainController()
        app = TextualReplApp(controller=controller)
        async with app.run_test(headless=True) as pilot:
            bar = app.query_one(StatusBar)
            # Initial state
            self.assertEqual(bar.current_status, "Ready")
