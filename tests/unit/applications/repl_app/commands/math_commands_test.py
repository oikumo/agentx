import unittest
from unittest.mock import patch

from agent_x.applications.repl_app import SumCommand

MOCK_FUNCTION_LOG_INFO = "agent_x.applications.repl_app.commands.math_commands.log_info"

class SumCommandTest(unittest.TestCase):
    def setUp(self):
        self.cmd = SumCommand("sum")

    def test_run_returns_correct_sum_of_two_positive_integers(self):
        result = self.cmd.run(["3", "4"])
        with patch(MOCK_FUNCTION_LOG_INFO) as mock_info:
            result.apply()
            mock_info.assert_called_once_with("7")
