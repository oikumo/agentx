import unittest
from app.commands import parse_chat_arguments


class TestParseChatArgumentsBasic(unittest.TestCase):
    def test_no_arguments_returns_defaults(self):
        model, query = parse_chat_arguments([])
        self.assertIsNone(model)
        self.assertEqual(query, "")

    def test_simple_query_returns_query_only(self):
        model, query = parse_chat_arguments(["hello", "world"])
        self.assertIsNone(model)
        self.assertEqual(query, "hello world")

    def test_model_flag_at_start(self):
        model, query = parse_chat_arguments(["--model", "gpt-4", "hello"])
        self.assertEqual(model, "gpt-4")
        self.assertEqual(query, "hello")

    def test_model_flag_at_end(self):
        model, query = parse_chat_arguments(["hello", "--model", "gpt-4"])
        self.assertEqual(model, "gpt-4")
        self.assertEqual(query, "hello")

    def test_model_flag_in_middle(self):
        model, query = parse_chat_arguments(["hello", "--model", "gpt-4", "world"])
        self.assertEqual(model, "gpt-4")
        self.assertEqual(query, "hello world")

    def test_model_flag_no_value_returns_none_model(self):
        model, query = parse_chat_arguments(["--model"])
        self.assertIsNone(model)
        self.assertEqual(query, "")

    def test_model_flag_with_empty_query(self):
        model, query = parse_chat_arguments(["--model", "gpt-4"])
        self.assertEqual(model, "gpt-4")
        self.assertEqual(query, "")

    def test_multiple_model_flags_uses_last(self):
        model, query = parse_chat_arguments(
            ["--model", "gpt-3", "hi", "--model", "gpt-4"]
        )
        self.assertEqual(model, "gpt-4")
        self.assertEqual(query, "hi")

    def test_query_without_model_flag(self):
        model, query = parse_chat_arguments(["what", "is", "python"])
        self.assertIsNone(model)
        self.assertEqual(query, "what is python")

    def test_model_flag_preserves_query_order(self):
        model, query = parse_chat_arguments(
            ["tell", "--model", "claude", "me", "a", "joke"]
        )
        self.assertEqual(model, "claude")
        self.assertEqual(query, "tell me a joke")


class TestParseChatArgumentsEdgeCases(unittest.TestCase):
    def test_empty_list(self):
        model, query = parse_chat_arguments([])
        self.assertIsNone(model)
        self.assertEqual(query, "")

    def test_only_model_flag(self):
        model, query = parse_chat_arguments(["--model", "gpt-4"])
        self.assertEqual(model, "gpt-4")
        self.assertEqual(query, "")

    def test_model_flag_value_looks_like_query(self):
        model, query = parse_chat_arguments(["--model", "hello", "world"])
        self.assertEqual(model, "hello")
        self.assertEqual(query, "world")

    def test_model_flag_with_quoted_values(self):
        model, query = parse_chat_arguments(["--model", "gpt-4-turbo", "say", "hi"])
        self.assertEqual(model, "gpt-4-turbo")
        self.assertEqual(query, "say hi")


if __name__ == "__main__":
    unittest.main()
