import unittest

from app.common.utils import safe_int


class UtilsTest(unittest.TestCase):
    def test_safe_int_with_valid_integer_string(self):
        result = safe_int("42")
        self.assertEqual(result, 42)
        result = safe_int("999999999999999999999")
        self.assertEqual(result,  999999999999999999999)

    def test_safe_int_with_valid_negative_integer(self):
        result = safe_int("-10")
        self.assertEqual(result, -10)
        result = safe_int("-999999999999999999999999999999")
        self.assertEqual(result, -999999999999999999999999999999)

    def test_safe_int_with_invalid_string(self):
        result = safe_int("abc")
        self.assertIsNone(result)

    def test_safe_int_with_float_string(self):
        result = safe_int("3.14")
        self.assertIsNone(result)

    def test_safe_int_with_whitespace_string(self):
        result = safe_int("  ")
        self.assertIsNone(result)

    def test_safe_int_with_invalid_string_negative(self):
        result = safe_int("- 10")
        self.assertIsNone(result)

