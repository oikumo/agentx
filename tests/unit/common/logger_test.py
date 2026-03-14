import unittest
from io import StringIO
from unittest.mock import patch

from agent_x.common.logger import (Colors, log_error, log_header, log_info,
                                   log_success, log_warning)


class LoggerTest(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_log_info(self, mock_stdout):
        log_info("test message")
        output = mock_stdout.getvalue()
        self.assertIn("test message", output)
        self.assertIn(Colors.CYAN, output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_log_success(self, mock_stdout):
        log_success("success message")
        output = mock_stdout.getvalue()
        self.assertIn("success message", output)
        self.assertIn(Colors.GREEN, output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_log_error(self, mock_stdout):
        log_error("error message")
        output = mock_stdout.getvalue()
        self.assertIn("error message", output)
        self.assertIn(Colors.RED, output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_log_warning(self, mock_stdout):
        log_warning("warning message")
        output = mock_stdout.getvalue()
        self.assertIn("warning message", output)
        self.assertIn(Colors.YELLOW, output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_log_header(self, mock_stdout):
        log_header("header message")
        output = mock_stdout.getvalue()
        self.assertIn("header message", output)
        self.assertIn(Colors.BOLD, output)
        self.assertIn(Colors.PURPLE, output)

    def test_colors_defined(self):
        self.assertEqual(Colors.PURPLE, "\033[95m")
        self.assertEqual(Colors.CYAN, "\033[96m")
        self.assertEqual(Colors.BLUE, "\033[94m")
        self.assertEqual(Colors.GREEN, "\033[92m")
        self.assertEqual(Colors.YELLOW, "\033[93m")
        self.assertEqual(Colors.RED, "\033[91m")
        self.assertEqual(Colors.BOLD, "\033[1m")
        self.assertEqual(Colors.UNDERLINE, "\033[4m")
        self.assertEqual(Colors.END, "\033[0m")
