import unittest
from app.repl.command_parser import CommandParser


class TestCommandParser(unittest.TestCase):
    def test_command_parser_simple(self):
        parser = CommandParser()
        result = parser.parse("chat hello world")
        self.assertEqual(result.key, "chat")
        self.assertEqual(result.arguments, ["hello", "world"])

    def test_command_parser_no_arguments(self):
        parser = CommandParser()
        result = parser.parse("quit")
        self.assertEqual(result.key, "quit")
        self.assertEqual(result.arguments, [])

    def test_command_parser_with_extra_spaces(self):
        parser = CommandParser()
        result = parser.parse("  help  ")
        self.assertEqual(result.key, "help")
        self.assertEqual(result.arguments, [])


if __name__ == "__main__":
    unittest.main()
