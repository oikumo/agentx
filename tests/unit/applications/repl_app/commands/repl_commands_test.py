import unittest
from unittest.mock import MagicMock

from agent_x.applications.repl_app.commands.repl_commands import ReplCommand
from agent_x.applications.repl_app.command_line_controller.commands_controller import (
    CommandsController,
)


# ── Helpers ──────────────────────────────────────────────────────────────────


class ConcreteReplCommand(ReplCommand):
    """Minimal concrete subclass to satisfy the ReplCommand ABC.

    ReplCommand inherits from both Command (which has abstract run()) and ABC.
    Any testable subclass must implement run().
    """

    def run(self, arguments: list[str]):
        pass


# ── Tests ─────────────────────────────────────────────────────────────────────


class ReplCommandTest(unittest.TestCase):
    def test_repl_command_cannot_be_instantiated_directly(self):
        # ReplCommand inherits Command's abstract run() method, so it must
        # also be abstract and raise TypeError when constructed directly.
        with self.assertRaises(TypeError):
            ReplCommand("some-key", MagicMock())  # type: ignore[abstract]

    def test_concrete_subclass_stores_key_and_controller(self):
        # The constructor must persist both the command key (from Command.__init__)
        # and the controller reference (from ReplCommand.__init__).
        mock_controller = MagicMock(spec=CommandsController)
        cmd = ConcreteReplCommand("help", mock_controller)

        self.assertEqual(cmd.key, "help")
        self.assertIs(cmd.controller, mock_controller)

    def test_key_is_inherited_from_command(self):
        # key must be set via super().__init__(key) so the dispatch table in
        # CommandsController can index on it correctly.
        mock_controller = MagicMock(spec=CommandsController)
        cmd = ConcreteReplCommand("info", mock_controller)
        self.assertEqual(cmd.key, "info")

    def test_run_callable_on_concrete_subclass(self):
        # Ensure that our concrete implementation's run() can be invoked
        # without raising – the base class must not interfere.
        mock_controller = MagicMock(spec=CommandsController)
        cmd = ConcreteReplCommand("test", mock_controller)
        try:
            cmd.run([])
        except Exception as exc:
            self.fail(f"run([]) raised unexpectedly: {exc}")
