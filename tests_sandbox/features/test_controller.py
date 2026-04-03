import unittest
from app.repl.controllers.main_controller import MainController
from app.repl.commands.math_commands import SumCommand
from app.repl.commands.cli_commands import (
    QuitCommand,
    ClearCommand,
    HelpCommand,
    ReadFile,
)


class TestMainController(unittest.TestCase):
    def setUp(self):
        self.controller = MainController()

    def test_empty_controller(self):
        self.assertEqual(len(self.controller.get_commands()), 0)

    def test_add_single_command(self):
        cmd = SumCommand("sum", self.controller)
        self.controller.add_command(cmd)
        self.assertEqual(len(self.controller.get_commands()), 1)

    def test_find_existing_command(self):
        cmd = SumCommand("sum", self.controller)
        self.controller.add_command(cmd)
        found = self.controller.find_command("sum")
        self.assertIsNotNone(found)
        self.assertEqual(found.key, "sum")

    def test_find_nonexistent_command(self):
        found = self.controller.find_command("nonexistent")
        self.assertIsNone(found)

    def test_multiple_commands(self):
        self.controller.add_command(SumCommand("sum", self.controller))
        self.controller.add_command(HelpCommand("help", self.controller))
        self.controller.add_command(ClearCommand("clear", self.controller))
        self.assertEqual(len(self.controller.get_commands()), 3)

    def test_overwrite_command(self):
        cmd1 = SumCommand("sum", self.controller)
        cmd2 = HelpCommand("sum", self.controller)
        self.controller.add_command(cmd1)
        self.controller.add_command(cmd2)
        self.assertEqual(len(self.controller.get_commands()), 1)
        found = self.controller.find_command("sum")
        self.assertIsInstance(found, HelpCommand)


if __name__ == "__main__":
    unittest.main()
