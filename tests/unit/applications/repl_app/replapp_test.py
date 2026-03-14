import unittest
from unittest.mock import MagicMock, patch

from agent_x.applications.repl_app.replapp import ReplApp

# Patch targets – must match the import site in replapp.py
_LOG_INFO = "agent_x.applications.repl_app.replapp.log_info"
_MAIN_CONTROLLER = "agent_x.applications.repl_app.replapp.MainController"
_TEXTUAL_APP = "agent_x.applications.repl_app.replapp.TextualReplApp"


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
        mock_tui = MagicMock()

        with (
            patch(_LOG_INFO) as mock_info,
            patch(_MAIN_CONTROLLER),
            patch(_TEXTUAL_APP, return_value=mock_tui),
        ):
            app.run()

        logged_args = [c.args[0] for c in mock_info.call_args_list]
        self.assertIn("App running", logged_args)

    def test_run_creates_main_controller(self):
        # run() must construct exactly one MainController and pass it to
        # TextualReplApp so the dispatch table is wired to the TUI.
        app = ReplApp()
        mock_tui = MagicMock()

        with (
            patch(_LOG_INFO),
            patch(_MAIN_CONTROLLER) as mock_ctrl_cls,
            patch(_TEXTUAL_APP, return_value=mock_tui),
        ):
            app.run()

        mock_ctrl_cls.assert_called_once()

    def test_run_creates_textual_app_with_controller(self):
        # TextualReplApp must receive the controller instance.
        app = ReplApp()
        mock_tui = MagicMock()

        with (
            patch(_LOG_INFO),
            patch(_MAIN_CONTROLLER) as mock_ctrl_cls,
            patch(_TEXTUAL_APP, return_value=mock_tui) as mock_tui_cls,
        ):
            app.run()

        mock_tui_cls.assert_called_once_with(controller=mock_ctrl_cls.return_value)

    def test_run_calls_textual_app_run(self):
        # ReplApp.run() must call TextualReplApp.run() to start the event loop.
        app = ReplApp()
        mock_tui = MagicMock()

        with (
            patch(_LOG_INFO),
            patch(_MAIN_CONTROLLER),
            patch(_TEXTUAL_APP, return_value=mock_tui),
        ):
            app.run()

        mock_tui.run.assert_called_once()
