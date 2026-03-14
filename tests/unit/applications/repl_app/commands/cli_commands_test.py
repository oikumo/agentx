import os
import tempfile
import unittest
from unittest.mock import MagicMock, call, patch

from agent_x.applications.repl_app.command_line_controller.command import \
    Command
from agent_x.applications.repl_app.command_line_controller.commands_controller import \
    CommandsController
from agent_x.applications.repl_app.commands.cli_commands import (ClearCommand,
                                                                 HelpCommand,
                                                                 QuitCommand,
                                                                 ReadFile)
from agent_x.applications.repl_app.controllers.main_controller.imain_controller import \
    IMainController

# Patch targets – must match the import site in cli_commands.py
_LOG_INFO = "agent_x.applications.repl_app.commands.cli_commands.log_info"
_CLEAR_CONSOLE = "agent_x.applications.repl_app.commands.cli_commands.clear_console"


# ── QuitCommand ───────────────────────────────────────────────────────────────


class QuitCommandTest(unittest.TestCase):
    def _make_controller(self) -> MagicMock:
        """Return a mock that satisfies the IMainController protocol."""
        return MagicMock(spec=IMainController)

    def test_stores_key_and_controller(self):
        controller = self._make_controller()
        cmd = QuitCommand("q", controller)
        self.assertEqual(cmd.key, "q")
        self.assertIs(cmd.controller, controller)

    def test_run_calls_controller_close(self):
        # QuitCommand.run() must invoke controller.close() to allow the app
        # to perform cleanup before the process exits.
        controller = self._make_controller()
        cmd = QuitCommand("q", controller)
        with patch(_LOG_INFO), patch("builtins.exit"):
            cmd.run([])
        controller.close.assert_called_once()

    def test_run_calls_exit_zero(self):
        # After closing, the process must exit with code 0 (clean shutdown).
        controller = self._make_controller()
        cmd = QuitCommand("q", controller)
        with patch(_LOG_INFO), patch("builtins.exit") as mock_exit:
            cmd.run([])
            mock_exit.assert_called_once_with(0)

    def test_run_logs_quit_message(self):
        # A log entry must be emitted for auditability.
        controller = self._make_controller()
        cmd = QuitCommand("q", controller)
        with patch(_LOG_INFO) as mock_info, patch("builtins.exit"):
            cmd.run([])
            mock_info.assert_called()


# ── ClearCommand ──────────────────────────────────────────────────────────────


class ClearCommandTest(unittest.TestCase):
    def test_stores_key(self):
        cmd = ClearCommand("cls")
        self.assertEqual(cmd.key, "cls")

    def test_run_delegates_to_clear_console(self):
        # ClearCommand's entire job is to call clear_console(); nothing else.
        cmd = ClearCommand("cls")
        with patch(_CLEAR_CONSOLE) as mock_clear:
            cmd.run([])
            mock_clear.assert_called_once()

    def test_run_ignores_arguments(self):
        # clear_console takes no arguments; extra tokens must not cause errors.
        cmd = ClearCommand("cls")
        with patch(_CLEAR_CONSOLE) as mock_clear:
            cmd.run(["--force", "now"])
            mock_clear.assert_called_once()


# ── HelpCommand ───────────────────────────────────────────────────────────────


class HelpCommandTest(unittest.TestCase):
    def _make_controller_with_commands(self, keys: list[str]) -> MagicMock:
        """Return a mock CommandsController that exposes fake commands."""
        fake_cmds = [MagicMock(spec=Command, key=k) for k in keys]
        ctrl = MagicMock(spec=CommandsController)
        ctrl.get_commands.return_value = fake_cmds
        return ctrl

    def test_run_logs_every_command_key(self):
        # HelpCommand must call log_info once for each registered command key
        # so the user can see all available commands.
        controller = self._make_controller_with_commands(["sum", "q", "help", "cls"])
        cmd = HelpCommand("help", controller)

        with patch(_LOG_INFO) as mock_info:
            cmd.run([])
            logged_args = [c.args[0] for c in mock_info.call_args_list]
            for key in ("sum", "q", "help", "cls"):
                self.assertIn(key, logged_args)

    def test_run_with_empty_controller_logs_nothing(self):
        # If no commands are registered, help must produce no output at all.
        controller = self._make_controller_with_commands([])
        cmd = HelpCommand("help", controller)

        with patch(_LOG_INFO) as mock_info:
            cmd.run([])
            mock_info.assert_not_called()

    def test_run_log_count_equals_command_count(self):
        # Each command key produces exactly one log line; no duplicates.
        keys = ["a", "b", "c", "d", "e"]
        controller = self._make_controller_with_commands(keys)
        cmd = HelpCommand("help", controller)

        with patch(_LOG_INFO) as mock_info:
            cmd.run([])
            self.assertEqual(mock_info.call_count, len(keys))


# ── ReadFile ──────────────────────────────────────────────────────────────────


class ReadFileTest(unittest.TestCase):
    def setUp(self):
        # ReadFile has no explicit __init__ key param in the source; it
        # inherits Command.__init__(key).
        self.cmd = ReadFile("read")

    def test_run_without_arguments_logs_usage(self):
        # With no filename provided, ReadFile must print usage instructions
        # rather than crashing or doing nothing silently.
        with patch(_LOG_INFO) as mock_info:
            self.cmd.run([])
            mock_info.assert_called_once()
            self.assertIn("Usage", mock_info.call_args.args[0])

    def test_run_reads_existing_file_and_logs_content(self):
        # Create a real temporary file; ReadFile must log its content exactly.
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("hello world")
            tmp_path = f.name
        try:
            with patch(_LOG_INFO) as mock_info:
                self.cmd.run([tmp_path])
                mock_info.assert_called_once_with("hello world")
        finally:
            os.unlink(tmp_path)

    def test_run_logs_file_not_found_for_missing_path(self):
        # A path that does not exist must produce a "File not found" message,
        # not an unhandled FileNotFoundError.
        with patch(_LOG_INFO) as mock_info:
            self.cmd.run(["/nonexistent/path/file_xyz_999.txt"])
            logged = mock_info.call_args.args[0]
            self.assertIn("File not found", logged)

    def test_run_uses_first_argument_as_filename(self):
        # Extra arguments beyond the first are silently ignored; only [0] is
        # used as the filename.
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("data")
            tmp_path = f.name
        try:
            with patch(_LOG_INFO) as mock_info:
                # Pass two args – only the first should be used.
                self.cmd.run([tmp_path, "extra-arg"])
                mock_info.assert_called_once_with("data")
        finally:
            os.unlink(tmp_path)
