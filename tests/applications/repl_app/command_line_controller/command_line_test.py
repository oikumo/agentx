import unittest
from unittest.mock import MagicMock, patch, call

from agent_x.applications.repl_app.command_line_controller.command_line import (
    CommandLine,
)
from agent_x.applications.repl_app.command_line_controller.commands_controller import (
    CommandsController,
)
from agent_x.applications.repl_app.command_line_controller.command import Command


# ── Helpers ──────────────────────────────────────────────────────────────────


def _make_table(*keys: str) -> MagicMock:
    """Return a mock CommandsController that knows about the given keys.

    find_command(key) returns a MagicMock Command for known keys, None otherwise.
    """
    table = MagicMock(spec=CommandsController)
    commands: dict[str, MagicMock] = {k: MagicMock(spec=Command) for k in keys}
    table.find_command.side_effect = lambda k: commands.get(k)
    # Expose commands dict so tests can assert on run() calls.
    table._commands = commands
    return table


# ── Tests ─────────────────────────────────────────────────────────────────────


class CommandLineTest(unittest.TestCase):
    def test_init_stores_commands_table(self):
        # CommandLine must hold a reference to the table so it can dispatch
        # user input to the correct Command at runtime.
        table = _make_table()
        cl = CommandLine(table)
        self.assertIs(cl.commands_table, table)

    def test_init_creates_command_parser(self):
        # A CommandParser must be created during __init__ so that run() can
        # tokenise input immediately without lazy setup.
        table = _make_table()
        cl = CommandLine(table)
        self.assertIsNotNone(cl.command_parser)

    def test_run_dispatches_valid_command(self):
        # When the user types a registered command, CommandLine must call
        # that command's run() with the parsed arguments.
        table = _make_table("sum")
        cl = CommandLine(table)

        with patch("builtins.input", return_value="sum 3 4"), patch("builtins.print"):
            cl.run()

        table._commands["sum"].run.assert_called_once_with(["3", "4"])

    def test_run_does_nothing_for_unknown_command(self):
        # An unrecognised command must NOT raise; CommandLine silently ignores it
        # and returns control to the caller (i.e. the while-loop in ReplApp).
        table = _make_table()  # no commands registered
        cl = CommandLine(table)

        try:
            with patch("builtins.input", return_value="ghost"), patch("builtins.print"):
                cl.run()
        except Exception as exc:
            self.fail(f"run() raised unexpectedly for unknown command: {exc}")

    def test_run_does_nothing_on_empty_input(self):
        # Empty input is parsed as None by CommandParser.parse(), so run()
        # must return without calling any command.
        table = _make_table("sum")
        cl = CommandLine(table)

        with patch("builtins.input", return_value=""), patch("builtins.print"):
            cl.run()

        table._commands["sum"].run.assert_not_called()

    def test_run_exits_zero_on_eof_error(self):
        # EOFError (piped input exhausted or Ctrl-D) must trigger exit(0) for
        # a clean shutdown rather than an unhandled exception traceback.
        table = _make_table()
        cl = CommandLine(table)

        with (
            patch("builtins.input", side_effect=EOFError()),
            patch("builtins.print"),
            patch("builtins.exit") as mock_exit,
        ):
            cl.run()
            mock_exit.assert_called_once_with(0)

    def test_run_exits_zero_on_keyboard_interrupt(self):
        # Ctrl-C (KeyboardInterrupt) should also produce a clean exit(0).
        table = _make_table()
        cl = CommandLine(table)

        with (
            patch("builtins.input", side_effect=KeyboardInterrupt()),
            patch("builtins.print"),
            patch("builtins.exit") as mock_exit,
        ):
            cl.run()
            mock_exit.assert_called_once_with(0)

    def test_run_exits_one_on_generic_exception(self):
        # Any other unexpected exception during input() results in exit(1)
        # signalling an abnormal termination to the OS / calling process.
        table = _make_table()
        cl = CommandLine(table)

        with (
            patch("builtins.input", side_effect=RuntimeError("boom")),
            patch("builtins.print"),
            patch("builtins.exit") as mock_exit,
        ):
            cl.run()
            mock_exit.assert_called_once_with(1)

    def test_show_prints_prompt(self):
        # _show() is the UI element that displays the "(agent-x)/…$" prompt.
        # It must call print() with the expected format string.
        table = _make_table()
        cl = CommandLine(table)

        with patch("builtins.print") as mock_print:
            cl._show("")
            mock_print.assert_called_once_with("(agent-x)/$ ", end="")
