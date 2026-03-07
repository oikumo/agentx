import unittest
from unittest.mock import patch

from agent_x.applications.repl_app.command_line_controller.command_parser import (
    CommandData,
    CommandParser,
)
from agent_x.applications.repl_app.command_line_controller.command import Command


# ── Helpers ──────────────────────────────────────────────────────────────────


class FakeCommand(Command):
    """Stub used to populate CommandParser.commands_list without real logic."""

    def run(self, arguments: list[str]):
        pass


# ── Tests ─────────────────────────────────────────────────────────────────────


class CommandDataTest(unittest.TestCase):
    """Tests for the CommandData dataclass (pure data container)."""

    def test_creation_stores_key_and_arguments(self):
        # Ensure both fields are assigned correctly on construction.
        data = CommandData(key="sum", arguments=["3", "4"])
        self.assertEqual(data.key, "sum")
        self.assertEqual(data.arguments, ["3", "4"])

    def test_empty_arguments_list_is_valid(self):
        # Commands with no arguments (e.g. "help") must produce an empty list,
        # not None or some sentinel value.
        data = CommandData(key="help", arguments=[])
        self.assertEqual(data.arguments, [])

    def test_equality_is_value_based(self):
        # Being a dataclass, two instances with identical fields are equal.
        d1 = CommandData(key="q", arguments=[])
        d2 = CommandData(key="q", arguments=[])
        self.assertEqual(d1, d2)

    def test_inequality_on_different_key(self):
        d1 = CommandData(key="sum", arguments=["1", "2"])
        d2 = CommandData(key="mul", arguments=["1", "2"])
        self.assertNotEqual(d1, d2)


class CommandParserTest(unittest.TestCase):
    """Tests for CommandParser – text → CommandData tokenisation."""

    def setUp(self):
        self.parser = CommandParser()

    # ── add ───────────────────────────────────────────────────────────────────

    def test_add_appends_command_to_list(self):
        # add() grows the internal commands_list; useful when callers want to
        # register available commands for validation (future extension point).
        cmd = FakeCommand("ping")
        self.parser.add(cmd)
        self.assertIn(cmd, self.parser.commands_list)

    def test_add_multiple_commands(self):
        cmds = [FakeCommand(k) for k in ("a", "b", "c")]
        for c in cmds:
            self.parser.add(c)
        self.assertEqual(len(self.parser.commands_list), 3)

    # ── parse – happy paths ───────────────────────────────────────────────────

    def test_parse_single_word_returns_command_data(self):
        # "help" → key="help", arguments=[]
        result = self.parser.parse("help")
        self.assertIsNotNone(result)
        self.assertEqual(result.key, "help")
        self.assertEqual(result.arguments, [])

    def test_parse_command_with_arguments(self):
        # "sum 3 4" → key="sum", arguments=["3", "4"]
        result = self.parser.parse("sum 3 4")
        self.assertIsNotNone(result)
        self.assertEqual(result.key, "sum")
        self.assertEqual(result.arguments, ["3", "4"])

    def test_parse_command_with_single_argument(self):
        # "read file.txt" → key="read", arguments=["file.txt"]
        result = self.parser.parse("read file.txt")
        self.assertIsNotNone(result)
        self.assertEqual(result.key, "read")
        self.assertEqual(result.arguments, ["file.txt"])

    # ── parse – edge / error cases ────────────────────────────────────────────

    def test_parse_empty_string_returns_none_and_warns(self):
        # An empty string has no tokens; parse() must return None and emit a
        # warning so the caller (CommandLine) can bail out gracefully.
        with patch(
            "agent_x.applications.repl_app.command_line_controller.command_parser.log_warning"
        ) as mock_warn:
            result = self.parser.parse("")
            self.assertIsNone(result)
            mock_warn.assert_called_once()

    def test_parse_whitespace_only_returns_none_and_warns(self):
        # "   " splits into an empty list, same as the empty-string case.
        with patch(
            "agent_x.applications.repl_app.command_line_controller.command_parser.log_warning"
        ) as mock_warn:
            result = self.parser.parse("   ")
            self.assertIsNone(result)
            mock_warn.assert_called_once()

    def test_parse_extra_whitespace_between_tokens_is_normalised(self):
        # str.split() with no separator collapses all whitespace, so extra
        # spaces between tokens must not appear in the argument list.
        result = self.parser.parse("sum   10   20")
        self.assertIsNotNone(result)
        self.assertEqual(result.arguments, ["10", "20"])
