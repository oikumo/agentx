import unittest
from unittest.mock import MagicMock, patch

from agents.chat.chat_loop import ChatLoop


class TestChatLoopWithModelSelection(unittest.TestCase):
    def _make_chunk(self, content):
        chunk = MagicMock()
        chunk.content = content
        chunk.text = content if content else ""
        return chunk

    def test_chat_loop_accepts_model_override(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [self._make_chunk("response")]

        chat_loop = ChatLoop(llm=mock_llm)
        result = chat_loop.run_streaming("hello", model_override="gpt-4")

        self.assertEqual(result, "response")

    def test_chat_loop_uses_default_model_when_no_override(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [self._make_chunk("response")]

        chat_loop = ChatLoop(llm=mock_llm)
        result = chat_loop.run_streaming("hello")

        self.assertEqual(result, "response")

    def test_chat_loop_factory_accepts_model_name(self):
        with patch(
            "llm_managers.agent_chat_factory.OpenRouterProvider"
        ) as mock_provider_class:
            mock_provider = MagicMock()
            mock_llm = MagicMock()
            mock_provider.create_llm.return_value = mock_llm
            mock_provider_class.return_value = mock_provider

            from llm_managers.agent_chat_factory import create_chat_loop_with_model

            result = create_chat_loop_with_model("gpt-4")

            mock_provider_class.assert_called_once_with(model_name="gpt-4")
            self.assertIsInstance(result, ChatLoop)


class TestChatLoopStreamingWithMetrics(unittest.TestCase):
    def _make_chunk(self, content):
        chunk = MagicMock()
        chunk.content = content
        chunk.text = content if content else ""
        return chunk

    @patch("app.common.utils.streaming_metrics.time.perf_counter")
    def test_run_streaming_with_metrics_records_tokens(self, mock_time):
        mock_time.side_effect = [100.0, 102.0]
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [
            self._make_chunk("Hello"),
            self._make_chunk(" world"),
        ]

        chat_loop = ChatLoop(llm=mock_llm)
        result, metrics = chat_loop.run_streaming_with_metrics("hi")

        self.assertEqual(result, "Hello world")
        self.assertEqual(metrics.total_tokens, 11)
        self.assertEqual(metrics.elapsed_time, 2.0)

    @patch("app.common.utils.streaming_metrics.time.perf_counter")
    def test_run_streaming_with_metrics_returns_zero_on_empty(self, mock_time):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        result, metrics = chat_loop.run_streaming_with_metrics("")

        self.assertIsNone(result)
        self.assertEqual(metrics.total_tokens, 0)

    @patch("app.common.utils.streaming_metrics.time.perf_counter")
    def test_run_streaming_with_metrics_rolls_back_on_error(self, mock_time):
        mock_time.return_value = 100.0
        mock_llm = MagicMock()
        mock_llm.stream.side_effect = Exception("LLM error")

        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.add_user_message("before")

        with self.assertRaises(Exception):
            chat_loop.run_streaming_with_metrics("fail")

        self.assertEqual(len(chat_loop.history), 2)


class TestOpenRouterProviderWithModelName(unittest.TestCase):
    def test_openrouter_provider_accepts_model_name(self):
        from llm_managers.providers.openrouter_provider import OpenRouterProvider

        provider = OpenRouterProvider(model_name="gpt-4")
        self.assertEqual(provider._model_name, "gpt-4")

    def test_openrouter_provider_default_model(self):
        from llm_managers.providers.openrouter_provider import OpenRouterProvider

        provider = OpenRouterProvider()
        self.assertEqual(provider._model_name, "anthropic/claude-3.5-haiku")


if __name__ == "__main__":
    unittest.main()
