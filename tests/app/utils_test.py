import unittest

from agent_x.utils.utils import safe_int


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
