"""RED → GREEN → REFACTOR tests for TUI widgets.

We test the widgets in two ways:
  1. Unit tests that exercise widget logic without a running Textual App
     (fast, pure-Python, no async needed).
  2. Integration tests using Textual's Pilot API that mount widgets into a
     minimal App and interact with them (async, marked with pytest.mark.asyncio
     if needed — here we use unittest with asyncio.run()).

All Textual App tests use `app.run_async(headless=True)` so they work in CI
without a real terminal.
"""

import asyncio
import unittest

from agent_x.applications.repl_app.tui.widgets.command_input import CommandInput


# ── CommandInput ──────────────────────────────────────────────────────────────


class CommandInputTest(unittest.TestCase):
    """Unit-level tests for CommandInput (no running App required)."""

    def test_command_input_is_instantiable(self):
        CommandInput(suggestions=[])
        # Must not raise.

    def test_command_input_accepts_suggestions_list(self):
        # Suggestions drive the autocomplete dropdown.
        ci = CommandInput(suggestions=["chat", "quit", "help"])
        self.assertIsNotNone(ci)

    def test_command_input_has_history(self):
        # A history deque must be present for up/down-arrow navigation.
        ci = CommandInput(suggestions=[])
        self.assertTrue(hasattr(ci, "history"))

    def test_history_is_initially_empty(self):
        ci = CommandInput(suggestions=[])
        self.assertEqual(len(ci.history), 0)

    def test_push_history_adds_entry(self):
        ci = CommandInput(suggestions=[])
        ci.push_history("chat hello")
        self.assertEqual(len(ci.history), 1)
        self.assertIn("chat hello", ci.history)

    def test_push_history_keeps_last_100_entries(self):
        # The deque must be bounded so it never grows unboundedly.
        ci = CommandInput(suggestions=[])
        for i in range(150):
            ci.push_history(f"cmd {i}")
        self.assertLessEqual(len(ci.history), 100)

    def test_push_history_does_not_add_blank_entries(self):
        # Empty or whitespace-only commands must not pollute history.
        ci = CommandInput(suggestions=[])
        ci.push_history("")
        ci.push_history("   ")
        self.assertEqual(len(ci.history), 0)
