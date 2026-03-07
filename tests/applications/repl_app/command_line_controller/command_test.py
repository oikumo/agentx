import unittest
from abc import ABC

from agent_x.applications.repl_app.command_line_controller.command import Command


# ── Helpers ──────────────────────────────────────────────────────────────────


class FakeCommand(Command):
    """Minimal concrete Command used only in tests.

    The real application commands (QuitCommand, SumCommand, …) all delegate
    to external dependencies. FakeCommand isolates the Command ABC itself so
    we can verify the contract without any side-effects.
    """

    def run(self, arguments: list[str]):
        # No-op implementation – just satisfies the abstract method.
        pass


# ── Tests ─────────────────────────────────────────────────────────────────────


class CommandTest(unittest.TestCase):
    def test_command_cannot_be_instantiated_directly(self):
        # Command.run is @abstractmethod; instantiating Command directly must
        # raise TypeError because Python prevents abstract classes from being
        # constructed without all abstract methods implemented.
        with self.assertRaises(TypeError):
            Command("test_key")  # type: ignore[abstract]

    def test_concrete_subclass_stores_key(self):
        # The key is the identifier used by CommandsController to dispatch
        # input. Verify it is stored verbatim on the instance.
        cmd = FakeCommand("my-key")
        self.assertEqual(cmd.key, "my-key")

    def test_run_is_callable_on_concrete_subclass(self):
        # Ensure the overridden run() can be called with an empty argument list
        # without raising – the method signature accepts list[str].
        cmd = FakeCommand("test")
        try:
            cmd.run([])
        except Exception as exc:
            self.fail(f"run([]) raised unexpectedly: {exc}")

    def test_command_is_abstract_base_class(self):
        # Structural check: Command itself must be an ABC so that the
        # @abstractmethod decorator is honoured.
        self.assertTrue(issubclass(Command, ABC))

    def test_key_can_be_any_string(self):
        # Keys are arbitrary strings; no validation is applied at the base
        # level. Special characters, spaces, and unicode must all be accepted.
        for key in ("q", "help me", "sum!!", "", "日本語"):
            cmd = FakeCommand(key)
            self.assertEqual(cmd.key, key)
