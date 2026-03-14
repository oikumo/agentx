import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.documents import Document

from agent_x.applications.web_ingestion_app.documents import (
    index_documents_async, process_documents)


class IndexDocumentsAsyncTest(unittest.TestCase):
    # index_documents_async batches documents, calls vectorstore.aadd_documents
    # for each batch concurrently, and logs success/failure.

    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def _make_docs(self, n: int):
        return [Document(page_content=f"doc {i}", metadata={}) for i in range(n)]

    def test_all_batches_succeed_logs_success(self):
        # When all aadd_documents calls succeed, success log is emitted.
        vectorstore = MagicMock()
        vectorstore.aadd_documents = AsyncMock(return_value=None)
        docs = self._make_docs(5)

        with (
            patch(
                "agent_x.applications.web_ingestion_app.documents.log_success"
            ) as mock_success,
            patch(
                "agent_x.applications.web_ingestion_app.documents.log_error"
            ) as mock_error,
            patch("agent_x.applications.web_ingestion_app.documents.log_info"),
        ):
            self._run(index_documents_async(vectorstore, docs, batch_size=5))
            mock_success.assert_called()
            mock_error.assert_not_called()

    def test_batching_respects_batch_size(self):
        # 10 documents with batch_size=3 → aadd_documents called 4 times
        # (batches of 3, 3, 3, 1).
        vectorstore = MagicMock()
        vectorstore.aadd_documents = AsyncMock(return_value=None)
        docs = self._make_docs(10)

        with patch("agent_x.applications.web_ingestion_app.documents.log_info"):
            with patch("agent_x.applications.web_ingestion_app.documents.log_success"):
                self._run(index_documents_async(vectorstore, docs, batch_size=3))

        self.assertEqual(vectorstore.aadd_documents.call_count, 4)

    def test_failed_batch_logs_error(self):
        # When aadd_documents raises, an error is logged and the function
        # does not re-raise (partial failure is silent to the caller).
        vectorstore = MagicMock()
        vectorstore.aadd_documents = AsyncMock(
            side_effect=RuntimeError("network error")
        )
        docs = self._make_docs(3)

        with (
            patch(
                "agent_x.applications.web_ingestion_app.documents.log_error"
            ) as mock_error,
            patch("agent_x.applications.web_ingestion_app.documents.log_success"),
            patch("agent_x.applications.web_ingestion_app.documents.log_info"),
        ):
            # Must not raise even though all batches fail.
            self._run(index_documents_async(vectorstore, docs, batch_size=10))
            mock_error.assert_called()

    def test_empty_document_list_does_not_call_vectorstore(self):
        vectorstore = MagicMock()
        vectorstore.aadd_documents = AsyncMock()

        with (
            patch("agent_x.applications.web_ingestion_app.documents.log_info"),
            patch("agent_x.applications.web_ingestion_app.documents.log_success"),
        ):
            self._run(index_documents_async(vectorstore, [], batch_size=50))

        vectorstore.aadd_documents.assert_not_called()

    def test_partial_failure_logs_error_not_success(self):
        # First batch succeeds, second fails → log_error should be called.
        vectorstore = MagicMock()
        call_count = {"n": 0}

        async def flaky(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 2:
                raise RuntimeError("batch 2 failed")

        vectorstore.aadd_documents = flaky
        docs = self._make_docs(6)  # 2 batches of 3

        with (
            patch(
                "agent_x.applications.web_ingestion_app.documents.log_error"
            ) as mock_error,
            patch("agent_x.applications.web_ingestion_app.documents.log_success"),
            patch("agent_x.applications.web_ingestion_app.documents.log_info"),
        ):
            self._run(index_documents_async(vectorstore, docs, batch_size=3))
            mock_error.assert_called()


class ProcessDocumentsTest(unittest.TestCase):
    # process_documents loads docs from a JSONL file and splits them.
    # Both collaborators are patched so no real file I/O occurs.

    def test_process_documents_calls_load_and_splitter(self):
        raw_docs = [Document(page_content="some text " * 100, metadata={})]
        split_docs = [
            Document(page_content="chunk1", metadata={}),
            Document(page_content="chunk2", metadata={}),
        ]

        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = split_docs

        with (
            patch(
                "agent_x.applications.web_ingestion_app.documents.load_docs_from_jsonl",
                return_value=raw_docs,
            ) as mock_load,
            patch(
                "agent_x.applications.web_ingestion_app.documents.RecursiveCharacterTextSplitter",
                return_value=mock_splitter,
            ),
            patch("agent_x.applications.web_ingestion_app.documents.log_success"),
        ):
            result = process_documents("/fake/path.jsonl")

            mock_load.assert_called_once_with("/fake/path.jsonl")
            mock_splitter.split_documents.assert_called_once_with(raw_docs)
            self.assertEqual(result, split_docs)

    def test_process_documents_returns_split_documents(self):
        # Return value must be the list produced by the text splitter.
        split_docs = [Document(page_content="a", metadata={})]

        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = split_docs

        with (
            patch(
                "agent_x.applications.web_ingestion_app.documents.load_docs_from_jsonl",
                return_value=[],
            ),
            patch(
                "agent_x.applications.web_ingestion_app.documents.RecursiveCharacterTextSplitter",
                return_value=mock_splitter,
            ),
            patch("agent_x.applications.web_ingestion_app.documents.log_success"),
        ):
            result = process_documents("/any/path.jsonl")
            self.assertEqual(result, split_docs)
