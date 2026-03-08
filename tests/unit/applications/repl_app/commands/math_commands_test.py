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

    # ── Zero operand regression (bug was: safe_int("0") falsy) ──────────────────

    def test_run_zero_as_first_argument_computes_correct_sum(self):
        # FIXED: guard changed from `if safe_int(x) and safe_int(y)` to
        #   `if safe_int(x) is not None and safe_int(y) is not None` so that
        #   "0" is accepted as a valid operand. 0 + 5 must produce "5".
        with patch(_LOG_INFO) as mock_info, patch(_LOG_WARN) as mock_warn:
            self.cmd.run(["0", "5"])
            mock_info.assert_called_once_with("5")
            mock_warn.assert_not_called()

    def test_run_zero_as_second_argument_computes_correct_sum(self):
        # FIXED: same guard fix; 5 + 0 must produce "5".
        with patch(_LOG_INFO) as mock_info, patch(_LOG_WARN) as mock_warn:
            self.cmd.run(["5", "0"])
            mock_info.assert_called_once_with("5")
            mock_warn.assert_not_called()
