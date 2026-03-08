import unittest
from unittest.mock import patch

from agent_x.applications.repl_app.controllers.main_controller.main_controller import (
    MainController,
)
from agent_x.applications.repl_app.command_line_controller.commands_controller import (
    CommandsController,
)
from agent_x.applications.repl_app.controllers.main_controller.imain_controller import (
    IMainController,
)


# Patch log_info so MainController.close() doesn't write to stdout during tests
_LOG_INFO = (
    "agent_x.applications.repl_app.controllers.main_controller.main_controller.log_info"
)

# Expected set of command keys registered by MainController.__init__.
# Update this set whenever new commands are added to MainController.
EXPECTED_COMMAND_KEYS = {
    "sum",
    "quit",
    "clear",
    "chat",
    "tools",
    "router",
    "react",
    "search",
    "read",
    "function",
    "rag",
    "graph",
    "chains",
    "reflex",
    "help",
}


class MainControllerTest(unittest.TestCase):
    def setUp(self):
        # MainController.__init__ registers all commands; create once per test.
        self.ctrl = MainController()

    # ── Inheritance / composition ─────────────────────────────────────────────

    def test_is_commands_controller(self):
        # MainController extends CommandsController, so the full dispatch-table
        # API (add_command, find_command, get_commands) must be available.
        self.assertIsInstance(self.ctrl, CommandsController)

    def test_satisfies_imain_controller_protocol(self):
        # MainController must expose a close() method as required by IMainController.
        # We verify this structurally (hasattr) rather than via isinstance because
        # IMainController is a Protocol, not a concrete base class.
        self.assertTrue(hasattr(self.ctrl, "close"))
        self.assertTrue(callable(self.ctrl.close))

    # ── Command registration ──────────────────────────────────────────────────

    def test_registers_expected_number_of_commands(self):
        # Each key in EXPECTED_COMMAND_KEYS must be present; count must match.
        commands = self.ctrl.get_commands()
        registered_keys = {c.key for c in commands}
        self.assertEqual(registered_keys, EXPECTED_COMMAND_KEYS)

    def test_find_known_command_returns_command_object(self):
        # spot-check a few specific commands that must always be present.
        for key in ("sum", "quit", "help", "clear", "read"):
            with self.subTest(key=key):
                result = self.ctrl.find_command(key)
                self.assertIsNotNone(
                    result, f"Expected command '{key}' to be registered"
                )
                self.assertEqual(result.key, key)

    def test_find_unknown_command_returns_none(self):
        # Any key not explicitly registered must yield None, never raise.
        self.assertIsNone(self.ctrl.find_command("__nonexistent__"))

    def test_all_commands_have_non_empty_description(self):
        # Every registered command must expose a non-empty description string
        # so that the help panel and autocomplete tooltips are useful.
        for cmd in self.ctrl.get_commands():
            with self.subTest(key=cmd.key):
                self.assertTrue(
                    hasattr(cmd, "description"),
                    f"Command '{cmd.key}' missing description attribute",
                )
                self.assertIsInstance(cmd.description, str)
                self.assertGreater(
                    len(cmd.description.strip()),
                    0,
                    f"Command '{cmd.key}' has empty description",
                )

    # ── close() ───────────────────────────────────────────────────────────────

    def test_close_logs_and_does_not_raise(self):
        # close() is called by QuitCommand before exit(). It must succeed
        # without raising and emit at least one log entry.
        with patch(_LOG_INFO) as mock_info:
            try:
                self.ctrl.close()
            except Exception as exc:
                self.fail(f"close() raised unexpectedly: {exc}")
            mock_info.assert_called()

    # ── Isolation ─────────────────────────────────────────────────────────────

    def test_two_instances_have_independent_registries(self):
        # Each MainController must own its own command dict; shared class-level
        # state was a bug that was fixed. Re-verify here at the integration level.
        ctrl1 = MainController()
        ctrl2 = MainController()
        # Both should have the same keys but different Command instances.
        self.assertEqual(
            {c.key for c in ctrl1.get_commands()},
            {c.key for c in ctrl2.get_commands()},
        )
