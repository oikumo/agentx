import unittest
from unittest.mock import patch
from app import Command
from agent_x.applications.repl_app import (
    CommandData, CommandParser)

class FakeCommand(Command):
    def run(self, arguments: list[str]):
        pass

class CommandDataTest(unittest.TestCase):

    def test_creation_stores_key_and_arguments(self):
        data = CommandData(key="sum", arguments=["3", "4"])
        self.assertEqual(data.key, "sum")
        self.assertEqual(data.arguments, ["3", "4"])

    def test_empty_arguments_list_is_valid(self):
        data = CommandData(key="help", arguments=[])
        self.assertEqual(data.arguments, [])

    def test_equality_is_value_based(self):
        d1 = CommandData(key="q", arguments=[])
        d2 = CommandData(key="q", arguments=[])
        self.assertEqual(d1, d2)

    def test_inequality_on_different_key(self):
        d1 = CommandData(key="sum", arguments=["1", "2"])
        d2 = CommandData(key="mul", arguments=["1", "2"])
        self.assertNotEqual(d1, d2)


class CommandParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = CommandParser()

    # ── add ───────────────────────────────────────────────────────────────────

    def test_add_appends_command_to_list(self):
        cmd = FakeCommand("ping")
        self.parser.add(cmd)
        self.assertIn(cmd, self.parser.commands_list)

    def test_add_multiple_commands(self):
        cmds = [FakeCommand(k) for k in ("a", "b", "c")]
        for c in cmds:
            self.parser.add(c)
        self.assertEqual(len(self.parser.commands_list), 3)

    def test_parse_single_word_returns_command_data(self):
        result = self.parser.parse("help")
        self.assertIsNotNone(result)
        self.assertEqual(result.key, "help")
        self.assertEqual(result.arguments, [])

    def test_parse_command_with_arguments(self):
        result = self.parser.parse("sum 3 4")
        self.assertIsNotNone(result)
        self.assertEqual(result.key, "sum")
        self.assertEqual(result.arguments, ["3", "4"])

    def test_parse_command_with_single_argument(self):
        result = self.parser.parse("read file.txt")
        self.assertIsNotNone(result)
        self.assertEqual(result.key, "read")
        self.assertEqual(result.arguments, ["file.txt"])

    def test_parse_empty_string_returns_none_and_warns(self):
        with patch(
            "agent_x.applications.repl_app.command_line_controller.command_parser.log_warning"
        ) as mock_warn:
            result = self.parser.parse("")
            self.assertIsNone(result)
            mock_warn.assert_called_once()

    def test_parse_whitespace_only_returns_none_and_warns(self):
        with patch(
            "agent_x.applications.repl_app.command_line_controller.command_parser.log_warning"
        ) as mock_warn:
            result = self.parser.parse("   ")
            self.assertIsNone(result)
            mock_warn.assert_called_once()

    def test_parse_extra_whitespace_between_tokens_is_normalised(self):
        result = self.parser.parse("sum   10   20")
        self.assertIsNotNone(result)
        self.assertEqual(result.arguments, ["10", "20"])
