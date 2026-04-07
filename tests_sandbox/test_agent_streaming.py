import unittest
from unittest.mock import MagicMock

from views.main_view import ChatLoop


class TestSimpleChatStreaming(unittest.TestCase):
    def _make_chunk(self, content):
        chunk = MagicMock()
        chunk.content = content
        chunk.text = content if content else ""
        return chunk

    def test_simple_chat_has_stream_method(self):
        mock_llm = MagicMock()
        chat = ChatLoop(llm=mock_llm)
        self.assertTrue(hasattr(chat, "run_streaming"))

    def test_simple_chat_streaming_returns_response(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [self._make_chunk("Hello")]

        chat = ChatLoop(llm=mock_llm)

        result = chat.run_streaming("test query")

        self.assertEqual(result, "Hello")

    def test_simple_chat_streaming_accumulates_chunks(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [
            self._make_chunk("Hello"),
            self._make_chunk(" world"),
        ]

        chat = ChatLoop(llm=mock_llm)

        result = chat.run_streaming("test query")

        self.assertEqual(result, "Hello world")

    def test_simple_chat_streaming_handles_none_content(self):
        mock_llm = MagicMock()
        mock_llm.stream.return_value = [
            self._make_chunk("start"),
            self._make_chunk(None),
            self._make_chunk("end"),
        ]

        chat = ChatLoop(llm=mock_llm)

        result = chat.run_streaming("test")

        self.assertEqual(result, "startend")


class TestAgentReactWebSearchStreaming(unittest.TestCase):
    def test_agent_react_web_search_has_streaming_method(self):
        mock_llm = MagicMock()
        from agents.react_web_search.agent_react_web_search import AgentReactWebSearch

        agent = AgentReactWebSearch(llm=mock_llm)
        self.assertTrue(hasattr(agent, "run_streaming"))


class TestAgentRagPdfStreaming(unittest.TestCase):
    def test_agent_rag_pdf_has_streaming_method(self):
        mock_llm = MagicMock()
        mock_embeddings = MagicMock()
        from agents.rag_pdf.agent_rag_pdf import AgentRagPdf

        agent = AgentRagPdf(
            pdf_path="test.pdf",
            vectorstore_path="/tmp/vs",
            llm=mock_llm,
            embeddings=mock_embeddings,
        )
        self.assertTrue(hasattr(agent, "run_streaming"))


if __name__ == "__main__":
    unittest.main()
