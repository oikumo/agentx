import unittest
from unittest.mock import MagicMock, patch, call

from agent_x.applications.repl_app.replapp import ReplApp


# Patch targets – must match the import site in replapp.py
_LOG_INFO = "agent_x.applications.repl_app.replapp.log_info"
_MAIN_CONTROLLER = "agent_x.applications.repl_app.replapp.MainController"
_COMMAND_LINE = "agent_x.applications.repl_app.replapp.CommandLine"


class ReplAppTest(unittest.TestCase):
    def test_init_does_not_raise(self):
        # ReplApp.__init__ is a simple `pass`; constructing one must be
        # side-effect-free and never raise.
        try:
            app = ReplApp()
        except Exception as exc:
            self.fail(f"ReplApp() raised unexpectedly: {exc}")

    def test_run_logs_app_running(self):
        # run() must emit "App running" so operators can confirm the REPL
        # started successfully (e.g. in log files or monitoring).
        app = ReplApp()

        # We break the infinite `while True` loop by making CommandLine.run()
        # raise StopIteration after the first call.
        mock_loop = MagicMock()
        mock_loop.run.side_effect = StopIteration

        with (
            patch(_LOG_INFO) as mock_info,
            patch(_MAIN_CONTROLLER),
            patch(_COMMAND_LINE, return_value=mock_loop),
        ):
            with self.assertRaises(StopIteration):
                app.run()

        # Verify log_info was called with the expected message at some point.
        logged_args = [c.args[0] for c in mock_info.call_args_list]
        self.assertIn("App running", logged_args)

    def test_run_creates_main_controller_and_command_line(self):
        # run() must construct exactly one MainController and pass it to
        # CommandLine – this wires the command dispatch table to the input loop.
        app = ReplApp()

        mock_loop = MagicMock()
        mock_loop.run.side_effect = StopIteration

        with (
            patch(_LOG_INFO),
            patch(_MAIN_CONTROLLER) as mock_ctrl_cls,
            patch(_COMMAND_LINE, return_value=mock_loop) as mock_cl_cls,
        ):
            with self.assertRaises(StopIteration):
                app.run()

        # MainController must be instantiated exactly once.
        mock_ctrl_cls.assert_called_once()
        # CommandLine must be instantiated with the MainController instance.
        mock_cl_cls.assert_called_once_with(mock_ctrl_cls.return_value)

    def test_run_enters_loop_by_calling_command_line_run(self):
        # The `while True` loop drives interaction; CommandLine.run() is the
        # entry point for each iteration. Verify it gets called.
        app = ReplApp()

        call_count = 0

        def fake_run():
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                # Break the infinite loop after 3 iterations.
                raise StopIteration

        mock_loop = MagicMock()
        mock_loop.run.side_effect = fake_run

        with (
            patch(_LOG_INFO),
            patch(_MAIN_CONTROLLER),
            patch(_COMMAND_LINE, return_value=mock_loop),
        ):
            with self.assertRaises(StopIteration):
                app.run()

        self.assertEqual(call_count, 3)
