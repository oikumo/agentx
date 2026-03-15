import unittest
from agent_x.applications.repl_app.command_line_controller.command import Command
from agent_x.applications.repl_app.command_line_controller.commands_controller import CommandsController

class FakeCommand(Command):
    def run(self, arguments: list[str]):
        pass


class CommandsControllerTest(unittest.TestCase):
    def setUp(self):
        self.controller = CommandsController()

    def test_empty_on_init(self):
        self.assertEqual(len(self.controller.get_commands()), 0)

    def test_add_command_makes_it_findable(self):
        cmd = FakeCommand("greet")
        self.controller.add_command(cmd)
        result = self.controller.find_command("greet")
        self.assertIs(result, cmd)

    def test_add_multiple_commands(self):
        for key in ("sum", "q", "help", "cls"):
            self.controller.add_command(FakeCommand(key))
        self.assertEqual(len(self.controller.get_commands()), 4)

    def test_find_command_returns_none_for_unknown_key(self):
        self.assertIsNone(self.controller.find_command("nonexistent"))

    def test_get_commands_returns_all_registered_commands(self):
        cmds = [FakeCommand("a"), FakeCommand("b"), FakeCommand("c")]
        for c in cmds:
            self.controller.add_command(c)
        result = self.controller.get_commands()
        self.assertEqual(set(c.key for c in result), {"a", "b", "c"})
