import unittest

from agent_x.applications.repl_app.command_line_controller.commands_controller import (
    CommandsController,
)
from agent_x.applications.repl_app.command_line_controller.command import Command


# ── Helpers ──────────────────────────────────────────────────────────────────


class FakeCommand(Command):
    """Stub command whose only job is to carry a `key` string.
    Used throughout this module to avoid depending on real command logic.
    """

    def run(self, arguments: list[str]):
        pass


# ── Tests ─────────────────────────────────────────────────────────────────────


class CommandsControllerTest(unittest.TestCase):
    def setUp(self):
        # Fresh controller for every test – instance state must not bleed
        # between test cases.
        self.controller = CommandsController()

    # ── Initialisation ────────────────────────────────────────────────────────

    def test_empty_on_init(self):
        # A brand-new CommandsController must have an empty command registry.
        self.assertEqual(len(self.controller.get_commands()), 0)

    # ── add_command ───────────────────────────────────────────────────────────

    def test_add_command_makes_it_findable(self):
        # After registering a command it must be retrievable by its key.
        cmd = FakeCommand("greet")
        self.controller.add_command(cmd)
        result = self.controller.find_command("greet")
        self.assertIs(result, cmd)

    def test_add_multiple_commands(self):
        # Each unique key creates a separate entry in the registry.
        for key in ("sum", "q", "help", "cls"):
            self.controller.add_command(FakeCommand(key))
        self.assertEqual(len(self.controller.get_commands()), 4)

    def test_duplicate_key_overwrites_previous_command(self):
        # Registering a second command with the same key replaces the first.
        # This mirrors dict semantics and is the documented behaviour.
        first = FakeCommand("read")
        second = FakeCommand("read")
        self.controller.add_command(first)
        self.controller.add_command(second)
        self.assertIs(self.controller.find_command("read"), second)
        self.assertEqual(len(self.controller.get_commands()), 1)

    # ── find_command ──────────────────────────────────────────────────────────

    def test_find_command_returns_none_for_unknown_key(self):
        # Querying a key that was never registered must return None, not raise.
        self.assertIsNone(self.controller.find_command("nonexistent"))

    # ── get_commands ──────────────────────────────────────────────────────────

    def test_get_commands_returns_all_registered_commands(self):
        # get_commands() returns every Command in insertion order (dict-backed).
        cmds = [FakeCommand("a"), FakeCommand("b"), FakeCommand("c")]
        for c in cmds:
            self.controller.add_command(c)
        result = self.controller.get_commands()
        self.assertEqual(set(c.key for c in result), {"a", "b", "c"})

    # ── Instance isolation ────────────────────────────────────────────────────

    def test_two_instances_do_not_share_state(self):
        # Each CommandsController must own its private dict. A command added
        # to one controller must NOT appear in a separately-created one.
        # (This was a bug where the dict lived at class level.)
        c1 = CommandsController()
        c2 = CommandsController()
        c1.add_command(FakeCommand("shared-key"))
        self.assertIsNone(c2.find_command("shared-key"))
