import unittest
from unittest.mock import MagicMock, patch

import app.commands as app_commands
from app.commands import AIChat


class TestAIChatCommandWithModelFlag(unittest.TestCase):
    def test_chat_with_model_flag_uses_custom_model(self):
        mock_loop = MagicMock()
        mock_metrics = MagicMock()
        mock_loop.run_streaming_with_metrics.return_value = (
            "Hello from gpt-4",
            mock_metrics,
        )

        with patch.object(
            app_commands.AgentFactory, "create_chat_loop", return_value=mock_loop
        ) as mock_factory:
            controller = MagicMock()
            cmd = AIChat("chat", controller)
            cmd.run(["--model", "gpt-4", "hello"])

            mock_factory.assert_called_once()
            call_kwargs = mock_factory.call_args[1]
            self.assertIsNotNone(call_kwargs.get("provider"))
            mock_loop.run_streaming_with_metrics.assert_called_once_with("hello")

    def test_chat_without_model_flag_uses_default(self):
        mock_loop = MagicMock()
        mock_metrics = MagicMock()
        mock_loop.run_streaming_with_metrics.return_value = ("Hello", mock_metrics)

        with patch.object(
            app_commands.AgentFactory, "create_chat_loop", return_value=mock_loop
        ) as mock_factory:
            controller = MagicMock()
            cmd = AIChat("chat", controller)
            cmd.run(["hello"])

            mock_factory.assert_called_once()
            mock_loop.run_streaming_with_metrics.assert_called_once_with("hello")

    def test_chat_displays_metrics_after_response(self):
        mock_metrics = MagicMock()
        mock_metrics.format.return_value = "50 tokens in 2.0s (25.0 tok/s)"
        mock_loop = MagicMock()
        mock_loop.run_streaming_with_metrics.return_value = (
            "Hello world",
            mock_metrics,
        )

        with patch.object(
            app_commands.AgentFactory, "create_chat_loop", return_value=mock_loop
        ):
            with patch("app.commands.Console") as mock_console:
                controller = MagicMock()
                cmd = AIChat("chat", controller)
                cmd.run(["--model", "gpt-4", "hi"])

                mock_console.log_info.assert_called_with(
                    "50 tokens in 2.0s (25.0 tok/s)"
                )

    def test_chat_interactive_with_model_flag(self):
        mock_loop = MagicMock()

        with patch.object(
            app_commands.AgentFactory, "create_chat_loop", return_value=mock_loop
        ) as mock_factory:
            controller = MagicMock()
            cmd = AIChat("chat", controller)
            cmd.run(["--model", "gpt-4"])

            mock_factory.assert_called_once()
            call_kwargs = mock_factory.call_args[1]
            self.assertIsNotNone(call_kwargs.get("provider"))
            mock_loop.start_interactive_streaming.assert_called_once()

    def test_chat_interactive_without_model_flag(self):
        mock_loop = MagicMock()

        with patch.object(
            app_commands.AgentFactory, "create_chat_loop", return_value=mock_loop
        ) as mock_factory:
            controller = MagicMock()
            cmd = AIChat("chat", controller)
            cmd.run([])

            mock_factory.assert_called_once()
            mock_loop.start_interactive_streaming.assert_called_once()

    def test_chat_streaming_error_handling_with_model(self):
        mock_loop = MagicMock()
        mock_loop.run_streaming_with_metrics.side_effect = Exception("LLM error")

        with patch.object(
            app_commands.AgentFactory, "create_chat_loop", return_value=mock_loop
        ):
            with patch("app.commands.Console") as mock_console:
                controller = MagicMock()
                cmd = AIChat("chat", controller)
                cmd.run(["--model", "gpt-4", "hello"])

                mock_console.log_error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
