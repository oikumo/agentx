import unittest
from unittest.mock import MagicMock, patch

from agents.chat.chat_loop import ChatLoop
from llm_managers.providers.openai_provider import OpenAIProvider


class TestChatLoopInitialization(unittest.TestCase):
    def test_chat_loop_has_llm(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        self.assertIs(chat_loop.llm, mock_llm)

    def test_chat_loop_starts_with_system_message(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        self.assertEqual(len(chat_loop.history), 1)
        self.assertEqual(chat_loop.history[0].content, "You are a helpful assistant.")

    def test_chat_loop_custom_system_prompt(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm, system_prompt="Custom prompt")
        self.assertEqual(chat_loop.history[0].content, "Custom prompt")

    def test_chat_loop_is_not_running_initially(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        self.assertFalse(chat_loop.is_running)


class TestChatLoopHistory(unittest.TestCase):
    def test_add_user_message_appends_to_history(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.add_user_message("hello")
        self.assertEqual(len(chat_loop.history), 2)
        self.assertEqual(chat_loop.history[1].content, "hello")

    def test_add_multiple_messages_preserves_order(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.add_user_message("first")
        chat_loop.add_user_message("second")
        self.assertEqual(len(chat_loop.history), 3)
        self.assertEqual(chat_loop.history[1].content, "first")
        self.assertEqual(chat_loop.history[2].content, "second")

    def test_add_assistant_message_appends_to_history(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.add_assistant_message("hi there")
        self.assertEqual(len(chat_loop.history), 2)
        self.assertEqual(chat_loop.history[1].content, "hi there")


class TestChatLoopResponse(unittest.TestCase):
    def test_get_response_calls_llm_with_history(self):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "test response"
        mock_llm.invoke.return_value = mock_response

        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.add_user_message("hello")
        result = chat_loop.get_response()

        mock_llm.invoke.assert_called_once()
        self.assertEqual(result, "test response")

    def test_get_response_appends_assistant_reply_to_history(self):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "reply"
        mock_llm.invoke.return_value = mock_response

        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.add_user_message("hi")
        chat_loop.get_response()

        self.assertEqual(len(chat_loop.history), 3)
        self.assertEqual(chat_loop.history[2].content, "reply")

    def test_get_response_passes_full_history_to_llm(self):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "reply"
        mock_llm.invoke.return_value = mock_response

        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.add_user_message("msg1")
        chat_loop.add_assistant_message("resp1")
        chat_loop.add_user_message("msg2")
        chat_loop.get_response()

        call_args = mock_llm.invoke.call_args[0][0]
        self.assertEqual(len(call_args), 5)


class TestChatLoopExit(unittest.TestCase):
    def test_exit_stops_running(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.is_running = True
        chat_loop.exit()
        self.assertFalse(chat_loop.is_running)

    def test_should_exit_returns_false_for_normal_input(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        self.assertFalse(chat_loop.should_exit("hello"))
        self.assertFalse(chat_loop.should_exit("what is python?"))

    def test_should_exit_returns_true_for_quit(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        self.assertTrue(chat_loop.should_exit("quit"))
        self.assertTrue(chat_loop.should_exit("quit "))
        self.assertTrue(chat_loop.should_exit(" quit"))

    def test_should_exit_returns_true_for_exit(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        self.assertTrue(chat_loop.should_exit("exit"))
        self.assertTrue(chat_loop.should_exit("exit "))


class TestChatLoopRun(unittest.TestCase):
    def test_run_starts_loop_and_processes_single_message(self):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "hello back"
        mock_llm.invoke.return_value = mock_response

        chat_loop = ChatLoop(llm=mock_llm)
        result = chat_loop.run("hi")

        self.assertEqual(result, "hello back")
        self.assertEqual(len(chat_loop.history), 3)

    def test_run_sets_running_flag_during_execution(self):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "response"
        mock_llm.invoke.return_value = mock_response

        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.run("test")

        self.assertFalse(chat_loop.is_running)

    def test_run_with_quit_returns_none(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        result = chat_loop.run("quit")

        self.assertIsNone(result)
        self.assertEqual(len(chat_loop.history), 1)

    def test_run_with_empty_input_returns_none(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        result = chat_loop.run("")

        self.assertIsNone(result)

    def test_run_with_whitespace_only_returns_none(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        result = chat_loop.run("   ")

        self.assertIsNone(result)


class TestChatLoopInteractive(unittest.TestCase):
    def test_start_interactive_begins_loop(self):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "hi"
        mock_llm.invoke.return_value = mock_response

        chat_loop = ChatLoop(llm=mock_llm)
        with patch.object(chat_loop, "_read_input", side_effect=["hello", "quit"]):
            chat_loop.start_interactive()

        self.assertFalse(chat_loop.is_running)
        self.assertEqual(mock_llm.invoke.call_count, 1)

    def test_start_interactive_processes_multiple_turns(self):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "response"
        mock_llm.invoke.return_value = mock_response

        chat_loop = ChatLoop(llm=mock_llm)
        with patch.object(
            chat_loop, "_read_input", side_effect=["msg1", "msg2", "msg3", "exit"]
        ):
            chat_loop.start_interactive()

        self.assertEqual(mock_llm.invoke.call_count, 3)
        self.assertEqual(len(chat_loop.history), 7)

    def test_start_interactive_skips_empty_input(self):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "response"
        mock_llm.invoke.return_value = mock_response

        chat_loop = ChatLoop(llm=mock_llm)
        with patch.object(
            chat_loop, "_read_input", side_effect=["", "  ", "hello", "quit"]
        ):
            chat_loop.start_interactive()

        self.assertEqual(mock_llm.invoke.call_count, 1)


class TestChatLoopFactory(unittest.TestCase):
    @patch("llm_managers.agent_chat_factory.OpenRouterProvider")
    def test_create_chat_loop_local_returns_chat_loop(self, mock_provider_class):
        from llm_managers.agent_chat_factory import create_chat_loop_local

        mock_provider = MagicMock()
        mock_llm = MagicMock()
        mock_provider.create_llm.return_value = mock_llm
        mock_provider_class.return_value = mock_provider

        result = create_chat_loop_local()

        self.assertIsInstance(result, ChatLoop)
        self.assertIs(result.llm, mock_llm)


if __name__ == "__main__":
    unittest.main()
