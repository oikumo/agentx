import unittest
from unittest.mock import MagicMock, patch

from agents.chat.main_view import ChatLoop
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
    @patch("llm_managers.factory.local_llm_provider")
    def test_create_chat_loop_local_returns_chat_loop(self, mock_local):
        from llm_managers.factory import AgentFactory

        mock_provider = MagicMock()
        mock_llm = MagicMock()
        mock_provider.create_llm.return_value = mock_llm
        mock_local.return_value = mock_provider

        result = AgentFactory.create_chat_loop()

        self.assertIsInstance(result, ChatLoop)
        self.assertIs(result.llm, mock_llm)


class TestChatLoopStreaming(unittest.TestCase):
    def _make_chunk(self, content):
        chunk = MagicMock()
        chunk.content = content
        if content is None:
            chunk.text = ""
        elif isinstance(content, str):
            chunk.text = content
        else:
            chunk.text = " ".join(str(item) for item in content if item is not None)
        return chunk

    def test_get_streaming_response_yields_chunks(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [
            self._make_chunk("Hello"),
            self._make_chunk(" world"),
        ]

        chat_loop = ChatLoop(llm=mock_llm)
        chunks = list(chat_loop.get_streaming_response("test"))

        self.assertEqual(chunks, ["Hello", " world"])

    def test_get_streaming_response_passes_history_to_stream(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [self._make_chunk("response")]

        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.add_user_message("hello")
        list(chat_loop.get_streaming_response("hello"))

        call_args = mock_llm.stream.call_args[0][0]
        self.assertEqual(len(call_args), 2)

    def test_get_streaming_response_handles_none_content(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [
            self._make_chunk("start"),
            self._make_chunk(None),
            self._make_chunk("end"),
        ]

        chat_loop = ChatLoop(llm=mock_llm)
        chunks = list(chat_loop.get_streaming_response("test"))

        self.assertEqual(chunks, ["start", "end"])

    def test_get_streaming_response_handles_list_content(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [self._make_chunk(["part1", "part2"])]

        chat_loop = ChatLoop(llm=mock_llm)
        chunks = list(chat_loop.get_streaming_response("test"))

        self.assertEqual(chunks, ["part1 part2"])

    def test_run_streaming_collects_full_response(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [
            self._make_chunk("Hello"),
            self._make_chunk(" world"),
        ]

        chat_loop = ChatLoop(llm=mock_llm)
        result = chat_loop.run_streaming("hi")

        self.assertEqual(result, "Hello world")

    def test_run_streaming_appends_full_response_to_history(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [
            self._make_chunk("Hi"),
            self._make_chunk(" there"),
        ]

        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.run_streaming("hello")

        self.assertEqual(len(chat_loop.history), 3)
        self.assertEqual(chat_loop.history[2].content, "Hi there")

    def test_run_streaming_with_empty_input_returns_none(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        result = chat_loop.run_streaming("")

        self.assertIsNone(result)

    def test_run_streaming_with_quit_returns_none(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        result = chat_loop.run_streaming("quit")

        self.assertIsNone(result)
        self.assertEqual(len(chat_loop.history), 1)

    def test_run_streaming_sets_running_flag_during_execution(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [self._make_chunk("response")]

        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.run_streaming("test")

        self.assertFalse(chat_loop.is_running)

    def test_run_streaming_rolls_back_on_error(self):
        mock_llm = MagicMock()
        mock_llm.stream.side_effect = Exception("LLM error")

        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.add_user_message("before")

        with self.assertRaises(Exception):
            chat_loop.run_streaming("fail")

        self.assertEqual(len(chat_loop.history), 2)
        self.assertEqual(chat_loop.history[1].content, "before")

    def test_start_interactive_streaming_prints_chunks(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [
            self._make_chunk("Hello"),
            self._make_chunk(" world"),
        ]

        chat_loop = ChatLoop(llm=mock_llm)
        import io
        import sys

        captured = io.StringIO()
        sys.stdout = captured

        with patch.object(chat_loop, "_read_input", side_effect=["hi", "quit"]):
            chat_loop.start_interactive_streaming()

        sys.stdout = sys.__stdout__
        output = captured.getvalue()

        self.assertIn("Hello", output)
        self.assertIn(" world", output)

    def test_start_interactive_streaming_exits_on_quit(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [self._make_chunk("response")]

        chat_loop = ChatLoop(llm=mock_llm)
        with patch.object(chat_loop, "_read_input", side_effect=["hello", "quit"]):
            chat_loop.start_interactive_streaming()

        self.assertFalse(chat_loop.is_running)

    def test_start_interactive_streaming_exits_on_exit(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [self._make_chunk("response")]

        chat_loop = ChatLoop(llm=mock_llm)
        with patch.object(chat_loop, "_read_input", side_effect=["hello", "exit"]):
            chat_loop.start_interactive_streaming()

        self.assertFalse(chat_loop.is_running)

    def test_start_interactive_streaming_skips_empty_input(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [self._make_chunk("response")]

        chat_loop = ChatLoop(llm=mock_llm)
        with patch.object(
            chat_loop, "_read_input", side_effect=["", "  ", "hello", "quit"]
        ):
            chat_loop.start_interactive_streaming()

        self.assertEqual(mock_llm.stream.call_count, 1)

    def test_start_interactive_streaming_adds_response_to_history(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [
            self._make_chunk("Hello"),
            self._make_chunk(" world"),
        ]

        chat_loop = ChatLoop(llm=mock_llm)
        with patch.object(chat_loop, "_read_input", side_effect=["hi", "quit"]):
            chat_loop.start_interactive_streaming()

        self.assertEqual(len(chat_loop.history), 3)
        self.assertEqual(chat_loop.history[2].content, "Hello world")


class TestChatLoopRag(unittest.TestCase):
    def test_chat_loop_without_retriever_has_none(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        self.assertIsNone(chat_loop.retriever)

    def test_chat_loop_with_retriever_stores_it(self):
        mock_llm = MagicMock()
        mock_retriever = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm, retriever=mock_retriever)
        self.assertIs(chat_loop.retriever, mock_retriever)

    def test_set_retriever_assigns_retriever(self):
        mock_llm = MagicMock()
        mock_retriever = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.set_retriever(mock_retriever)
        self.assertIs(chat_loop.retriever, mock_retriever)

    def test_clear_retriever_removes_retriever(self):
        mock_llm = MagicMock()
        mock_retriever = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm, retriever=mock_retriever)
        chat_loop.clear_retriever()
        self.assertIsNone(chat_loop.retriever)

    def test_has_retriever_returns_false_when_none(self):
        mock_llm = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm)
        self.assertFalse(chat_loop.has_retriever())

    def test_has_retriever_returns_true_when_set(self):
        mock_llm = MagicMock()
        mock_retriever = MagicMock()
        chat_loop = ChatLoop(llm=mock_llm, retriever=mock_retriever)
        self.assertTrue(chat_loop.has_retriever())

    def test_run_streaming_without_retriever_does_not_call_retriever(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [self._make_chunk("response")]
        mock_retriever = MagicMock()

        chat_loop = ChatLoop(llm=mock_llm)
        chat_loop.run_streaming("hello")

        mock_retriever.invoke.assert_not_called()

    def test_run_streaming_with_retriever_includes_context_in_history(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [self._make_chunk("answer based on docs")]

        mock_retriever = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "This is relevant context from the document."
        mock_retriever.invoke.return_value = [mock_doc]

        chat_loop = ChatLoop(llm=mock_llm, retriever=mock_retriever)
        chat_loop.run_streaming("What is this about?")

        mock_retriever.invoke.assert_called_once()
        self.assertEqual(len(chat_loop.history), 3)
        self.assertIn("relevant context", chat_loop.history[1].content.lower())

    def test_run_streaming_with_retriever_formats_context_prompt(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [self._make_chunk("answer")]

        mock_retriever = MagicMock()
        mock_doc1 = MagicMock()
        mock_doc1.page_content = "Context one."
        mock_doc2 = MagicMock()
        mock_doc2.page_content = "Context two."
        mock_retriever.invoke.return_value = [mock_doc1, mock_doc2]

        chat_loop = ChatLoop(llm=mock_llm, retriever=mock_retriever)
        chat_loop.run_streaming("Test query")

        call_args = mock_llm.stream.call_args[0][0]
        user_message = call_args[1]
        self.assertIn("Context one.", user_message.content)
        self.assertIn("Context two.", user_message.content)

    def test_run_streaming_with_retriever_handles_empty_results(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [self._make_chunk("no docs found")]

        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = []

        chat_loop = ChatLoop(llm=mock_llm, retriever=mock_retriever)
        result = chat_loop.run_streaming("query with no results")

        self.assertEqual(result, "no docs found")
        self.assertEqual(len(chat_loop.history), 3)

    def test_run_streaming_with_retriever_handles_retriever_error(self):
        mock_llm = MagicMock()
        mock_retriever = MagicMock()
        mock_retriever.invoke.side_effect = Exception("Retrieval error")

        chat_loop = ChatLoop(llm=mock_llm, retriever=mock_retriever)

        with self.assertRaises(Exception):
            chat_loop.run_streaming("query that fails retrieval")

    def test_run_streaming_with_metrics_with_retriever(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [self._make_chunk("rag answer")]

        mock_retriever = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "RAG context."
        mock_retriever.invoke.return_value = [mock_doc]

        chat_loop = ChatLoop(llm=mock_llm, retriever=mock_retriever)
        result, metrics = chat_loop.run_streaming_with_metrics("RAG query")

        self.assertEqual(result, "rag answer")
        mock_retriever.invoke.assert_called_once()

    def test_run_streaming_with_retriever_rolls_back_on_llm_error(self):
        mock_llm = MagicMock()
        mock_llm.stream.side_effect = Exception("LLM error")

        mock_retriever = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "Context."
        mock_retriever.invoke.return_value = [mock_doc]

        chat_loop = ChatLoop(llm=mock_llm, retriever=mock_retriever)
        chat_loop.add_user_message("before")

        with self.assertRaises(Exception):
            chat_loop.run_streaming("fail query")

        self.assertEqual(len(chat_loop.history), 2)
        self.assertEqual(chat_loop.history[1].content, "before")

    @staticmethod
    def _make_chunk(content):
        chunk = MagicMock()
        chunk.content = content
        if content is None:
            chunk.text = ""
        elif isinstance(content, str):
            chunk.text = content
        else:
            chunk.text = " ".join(str(item) for item in content if item is not None)
        return chunk


class TestChatLoopRagFactory(unittest.TestCase):
    @patch("llm_managers.factory.FAISS")
    @patch("llm_managers.factory.local_llm_provider")
    @patch("llm_models.local.ollama.ollama_embeddings.create_embeddings_model")
    @patch("llm_managers.factory.pdf_loader")
    def test_create_chat_loop_rag_returns_chat_loop_with_retriever(
        self, mock_pdf_loader, mock_create_embeddings, mock_local_llm, mock_faiss
    ):
        from llm_managers.factory import AgentFactory

        mock_llm = MagicMock()
        mock_local_llm.return_value.create_llm.return_value = mock_llm

        mock_vectorstore = MagicMock()
        mock_retriever = MagicMock()
        mock_vectorstore.as_retriever.return_value = mock_retriever
        mock_faiss.from_documents.return_value = mock_vectorstore
        mock_faiss.load_local.return_value = mock_vectorstore

        mock_pdf_loader.return_value = [MagicMock()]
        mock_create_embeddings.return_value = MagicMock()

        result = AgentFactory.create_chat_loop_rag(
            pdf_path="_resources/react.pdf",
            vectorstore_path="/tmp/test_faiss",
        )

        self.assertIsInstance(result, ChatLoop)
        self.assertIs(result.llm, mock_llm)
        self.assertIsNotNone(result.retriever)

    @patch("llm_managers.factory.FAISS")
    @patch("llm_managers.factory.local_llm_provider")
    @patch("llm_models.local.ollama.ollama_embeddings.create_embeddings_model")
    @patch("llm_managers.factory.pdf_loader")
    def test_create_chat_loop_rag_uses_custom_provider(
        self, mock_pdf_loader, mock_create_embeddings, mock_local_llm, mock_faiss
    ):
        from llm_managers.factory import AgentFactory

        mock_provider = MagicMock()
        mock_llm = MagicMock()
        mock_provider.create_llm.return_value = mock_llm

        mock_vectorstore = MagicMock()
        mock_retriever = MagicMock()
        mock_vectorstore.as_retriever.return_value = mock_retriever
        mock_faiss.from_documents.return_value = mock_vectorstore
        mock_faiss.load_local.return_value = mock_vectorstore

        mock_pdf_loader.return_value = [MagicMock()]
        mock_create_embeddings.return_value = MagicMock()

        result = AgentFactory.create_chat_loop_rag(
            pdf_path="_resources/react.pdf",
            vectorstore_path="/tmp/test_faiss",
            llm_provider=mock_provider,
        )

        mock_provider.create_llm.assert_called_once()
        mock_local_llm.assert_not_called()
        self.assertIsInstance(result, ChatLoop)


if __name__ == "__main__":
    unittest.main()
