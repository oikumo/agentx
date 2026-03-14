import unittest
from unittest.mock import MagicMock, patch

from agent_x.utils.utils import clear_console, safe_int


class UtilsTest(unittest.TestCase):
    def test_safe_int_with_valid_integer_string(self):
        result = safe_int("42")
        self.assertEqual(result, 42)

    def test_safe_int_with_valid_negative_integer(self):
        result = safe_int("-10")
        self.assertEqual(result, -10)

    def test_safe_int_with_invalid_string(self):
        result = safe_int("abc")
        self.assertIsNone(result)

    def test_safe_int_with_none(self):
        result = safe_int(None)
        self.assertIsNone(result)

    def test_safe_int_with_float_string(self):
        result = safe_int("3.14")
        self.assertIsNone(result)

    def test_safe_int_with_default_value(self):
        result = safe_int("invalid", default=0)
        self.assertEqual(result, 0)

    def test_safe_int_with_custom_default(self):
        result = safe_int("notanumber", default=-1)
        self.assertEqual(result, -1)

    def test_safe_int_with_whitespace_string(self):
        result = safe_int("  ")
        self.assertIsNone(result)

    # ── clear_console ─────────────────────────────────────────────────────────

    def test_clear_console_calls_cls_on_windows(self):
        # On Windows (os.name == 'nt'), clear_console must invoke `cls` via
        # os.system so the terminal buffer is actually cleared.
        with patch("agent_x.utils.utils.os") as mock_os:
            mock_os.name = "nt"
            clear_console()
            mock_os.system.assert_called_once_with("cls")

    def test_clear_console_calls_clear_on_unix(self):
        # On Unix-like systems (os.name != 'nt'), the POSIX `clear` command
        # is used instead of `cls`.
        with patch("agent_x.utils.utils.os") as mock_os:
            mock_os.name = "posix"
            clear_console()
            mock_os.system.assert_called_once_with("clear")
