import unittest
from unittest.mock import patch

from agent_x.applications.repl_app.commands.math_commands import SumCommand


# Patch targets – match the import site inside math_commands.py
_LOG_INFO = "agent_x.applications.repl_app.commands.math_commands.log_info"
_LOG_WARN = "agent_x.applications.repl_app.commands.math_commands.log_warning"


class SumCommandTest(unittest.TestCase):
    """Tests for SumCommand.run() – arithmetic and argument validation."""

    def setUp(self):
        # SumCommand is stateless; a single instance is fine across all cases.
        self.cmd = SumCommand("sum")

    # ── Happy paths ───────────────────────────────────────────────────────────

    def test_run_returns_correct_sum_of_two_positive_integers(self):
        # Basic sanity: "sum 3 4" → logs "7"
        with patch(_LOG_INFO) as mock_info:
            self.cmd.run(["3", "4"])
            mock_info.assert_called_once_with("7")

    def test_run_handles_negative_numbers(self):
        # Negative integers must parse and compute correctly.
        with patch(_LOG_INFO) as mock_info:
            self.cmd.run(["-5", "10"])
            mock_info.assert_called_once_with("5")

    def test_run_sums_two_negative_numbers(self):
        with patch(_LOG_INFO) as mock_info:
            self.cmd.run(["-3", "-7"])
            mock_info.assert_called_once_with("-10")

    # ── Validation failures ───────────────────────────────────────────────────

    def test_run_warns_on_non_numeric_first_argument(self):
        # Non-integer first argument → "invalid params" warning, no log_info.
        with patch(_LOG_WARN) as mock_warn, patch(_LOG_INFO) as mock_info:
            self.cmd.run(["abc", "4"])
            mock_warn.assert_called_once()
            mock_info.assert_not_called()

    def test_run_warns_on_non_numeric_second_argument(self):
        with patch(_LOG_WARN) as mock_warn, patch(_LOG_INFO) as mock_info:
            self.cmd.run(["4", "xyz"])
            mock_warn.assert_called_once()
            mock_info.assert_not_called()

    # ── Wrong argument count ──────────────────────────────────────────────────

    def test_run_warns_on_no_arguments(self):
        # The match statement falls to the default `case _` branch.
        with patch(_LOG_WARN) as mock_warn:
            self.cmd.run([])
            mock_warn.assert_called_once()

    def test_run_warns_on_single_argument(self):
        with patch(_LOG_WARN) as mock_warn:
            self.cmd.run(["5"])
            mock_warn.assert_called_once()

    def test_run_warns_on_three_arguments(self):
        with patch(_LOG_WARN) as mock_warn:
            self.cmd.run(["1", "2", "3"])
            mock_warn.assert_called_once()

    # ── Known bug: zero as first operand is falsy ─────────────────────────────

    def test_run_zero_as_first_argument_is_treated_as_invalid_due_to_bug(self):
        # BUG: safe_int("0") returns 0, which is falsy. The guard
        #   `if safe_int(x) and safe_int(y)` therefore treats "0" as invalid
        #   and emits a warning instead of computing 0 + 5 = 5.
        # This test documents the existing behaviour. If the bug is fixed, the
        # assertion must be updated to expect log_info("5").
        with patch(_LOG_WARN) as mock_warn, patch(_LOG_INFO) as mock_info:
            self.cmd.run(["0", "5"])
            # Currently warns (bug: treats 0 as invalid)
            mock_warn.assert_called_once()
            mock_info.assert_not_called()

    def test_run_zero_as_second_argument_is_treated_as_invalid_due_to_bug(self):
        # Same bug: safe_int("0") == 0 → falsy → warning instead of result.
        with patch(_LOG_WARN) as mock_warn, patch(_LOG_INFO) as mock_info:
            self.cmd.run(["5", "0"])
            mock_warn.assert_called_once()
            mock_info.assert_not_called()
