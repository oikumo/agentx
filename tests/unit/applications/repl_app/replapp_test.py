import unittest
from unittest.mock import MagicMock, patch

from agent_x.applications.repl_app.replapp import ReplApp

# Patch targets – must match the import site in replapp.py
_LOG_INFO = "agent_x.applications.repl_app.replapp.log_info"
_MAIN_CONTROLLER = "agent_x.applications.repl_app.replapp.MainController"
_COMMAND_PARSER = "agent_x.applications.repl_app.replapp.CommandParser"


class ReplAppTest(unittest.TestCase):
    def test_init_does_not_raise(self):
        # ReplApp.__init__ creates controller and parser; constructing one must be
        # side-effect-free and never raise.
        try:
            app = ReplApp()
        except Exception as exc:
            self.fail(f"ReplApp() raised unexpectedly: {exc}")

    def test_run_logs_app_running(self):
        # run() must emit "App running" so operators can confirm the REPL
        # started successfully (e.g. in log files or monitoring).
        app = ReplApp()

        with (
            patch(_LOG_INFO) as mock_log_info,
            patch(_MAIN_CONTROLLER),
            patch(_COMMAND_PARSER),
        ):
            # We need to simulate the loop running briefly then exiting
            # We'll mock input to raise EOFError immediately to exit loop
            with patch("builtins.input", side_effect=EOFError):
                app.run()

        # Check that the expected messages were logged
        mock_log_info.assert_any_call("Agent-X CLI REPL started")
        mock_log_info.assert_any_call("Type 'help' for commands, Ctrl+C to exit")

    def test_run_creates_main_controller(self):
        # run() should use the MainController instance created in __init__
        app = ReplApp()
        mock_controller = MagicMock()

        # Patch the constructor to return our mock, and verify the instance is stored
        with patch(
            _MAIN_CONTROLLER, return_value=mock_controller
        ) as mock_ctrl_constructor:
            # Re-instantiate to capture the constructor call
            app = ReplApp()
            mock_ctrl_constructor.assert_called_once()

            # Verify the controller was stored
            self.assertIs(app.controller, mock_controller)

    def test_run_creates_command_parser(self):
        # run() should use the CommandParser instance created in __init__
        app = ReplApp()
        mock_parser = MagicMock()

        # Patch the constructor to return our mock, and verify the instance is stored
        with patch(
            _COMMAND_PARSER, return_value=mock_parser
        ) as mock_parser_constructor:
            # Re-instantiate to capture the constructor call
            app = ReplApp()
            mock_parser_constructor.assert_called_once()

            # Verify the parser was stored
            self.assertIs(app.parser, mock_parser)

    def test_run_handles_keyboard_interrupt(self):
        # Test that Ctrl+C is handled gracefully
        app = ReplApp()

        with (
            patch(_LOG_INFO) as mock_log_info,
            patch(_MAIN_CONTROLLER),
            patch(_COMMAND_PARSER),
        ):
            # Simulate KeyboardInterrupt on first input call
            with patch("builtins.input", side_effect=KeyboardInterrupt):
                app.run()  # Should not raise

        # Check that exit message was logged
        mock_log_info.assert_any_call("\nReceived interrupt, exiting...")

    def test_run_processes_command(self):
        # Test that a command is parsed and executed
        app = ReplApp()
        mock_controller = MagicMock()
        mock_parser = MagicMock()
        mock_command = MagicMock()

        # Set up the instances that will be created in __init__
        app.controller = mock_controller
        app.parser = mock_parser

        # Configure mocks
        mock_controller.find_command.return_value = mock_command
        mock_parser.parse.return_value = MagicMock(key="test_cmd", arguments=["arg1"])

        with (
            patch(_LOG_INFO),
            patch("builtins.input", side_effect=["test_cmd arg1", EOFError]),
        ):
            app.run()

        # Verify command was found and executed
        mock_controller.find_command.assert_called_once_with("test_cmd")
        mock_command.run.assert_called_once_with(["arg1"])
