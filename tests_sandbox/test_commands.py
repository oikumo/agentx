import unittest
from unittest.mock import MagicMock, patch
from app.repl.commands.math_commands import SumCommand, CommandResultPrint
from app.repl.commands.cli_commands import HelpCommand, ClearCommand, ReadFile
from app.repl.commands.llm_chat_commands import (
    AIChat,
    AIRouterAgents,
    AIReactTools,
    AISearch,
    AIFunction,
    RagPDF,
)
from app.repl.commands.llm_graph_commands import (
    AIGraphSimple,
    AIGraphChains,
    AIGraphReflexion,
)


class TestSumCommand(unittest.TestCase):
    def setUp(self):
        self.controller = MagicMock()
        self.command = SumCommand("sum", self.controller)

    def test_sum_valid_numbers(self):
        result = self.command.run(["2", "3"])
        self.assertIsInstance(result, CommandResultPrint)
        self.assertEqual(result._message, "5")

    def test_sum_negative_numbers(self):
        result = self.command.run(["-1", "-4"])
        self.assertIsInstance(result, CommandResultPrint)
        self.assertEqual(result._message, "-5")

    def test_sum_zero(self):
        result = self.command.run(["0", "0"])
        self.assertIsInstance(result, CommandResultPrint)
        self.assertEqual(result._message, "0")

    def test_sum_invalid_args(self):
        result = self.command.run(["abc", "3"])
        self.assertIsNone(result)

    def test_sum_missing_args(self):
        result = self.command.run(["5"])
        self.assertIsNone(result)

    def test_sum_no_args(self):
        result = self.command.run([])
        self.assertIsNone(result)


class TestHelpCommand(unittest.TestCase):
    def setUp(self):
        self.controller = MagicMock()
        self.command = HelpCommand("help", self.controller)

    def test_help_returns_command_list(self):
        mock_cmd = MagicMock()
        mock_cmd.key = "test"
        mock_cmd.description = "Test command"
        self.controller.get_commands.return_value = [mock_cmd]

        result = self.command.run([])
        self.assertIsNotNone(result)
        result.apply()


class TestClearCommand(unittest.TestCase):
    def setUp(self):
        self.controller = MagicMock()
        self.command = ClearCommand("clear", self.controller)

    @patch("app.repl.commands.cli_commands.clear_console")
    def test_clear_calls_clear_console(self, mock_clear):
        self.command.run([])
        mock_clear.assert_called_once()


class TestReadFileCommand(unittest.TestCase):
    def setUp(self):
        self.controller = MagicMock()
        self.command = ReadFile("read", self.controller)

    @patch("builtins.open", unittest.mock.mock_open(read_data="test content"))
    def test_read_existing_file(self):
        self.command.run(["test.txt"])

    def test_read_no_args(self):
        self.command.run([])

    def test_read_nonexistent_file(self):
        self.command.run(["nonexistent.txt"])


class TestCommandDescriptions(unittest.TestCase):
    def setUp(self):
        self.controller = MagicMock()

    def test_sum_description(self):
        cmd = SumCommand("sum", self.controller)
        self.assertIn("Add", cmd.description)

    def test_help_description(self):
        cmd = HelpCommand("help", self.controller)
        self.assertIn("Show", cmd.description)

    def test_clear_description(self):
        cmd = ClearCommand("clear", self.controller)
        self.assertIn("Clear", cmd.description)

    def test_read_description(self):
        cmd = ReadFile("read", self.controller)
        self.assertIn("Read", cmd.description)


if __name__ == "__main__":
    unittest.main()
