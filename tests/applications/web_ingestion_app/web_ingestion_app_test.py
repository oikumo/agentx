import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch, call

from langchain_core.documents import Document

# WebIngestionApp imports web_ingestion_app module which has module-level side
# effects (ssl.create_default_context, os.environ mutations). These run once at
# import time — they do not affect test correctness since they only set SSL
# environment variables. The vectorstore and tav dependencies are injected via
# constructor and are fully mockable.

_MOD = "agent_x.applications.web_ingestion_app.web_ingestion_app"


def _make_app():
    """Build a WebIngestionApp with fully mocked collaborators."""
    from agent_x.applications.web_ingestion_app.web_ingestion_app import WebIngestionApp

    vectorstore = MagicMock()
    tav = MagicMock()
    return WebIngestionApp(vectorstore=vectorstore, tav=tav), vectorstore, tav


class WebIngestionAppRunTest(unittest.TestCase):
    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_run_calls_data_ingestion_with_site_url(self):
        # run() must delegate site mapping + extraction to data_ingestion().
        app, vectorstore, tav = _make_app()
        docs = [Document(page_content="text", metadata={})]

        with (
            patch.object(app, "data_ingestion", new=AsyncMock(return_value=docs)),
            patch(f"{_MOD}.save_docs"),
            patch(f"{_MOD}.process_documents", return_value=docs),
            patch(f"{_MOD}.index_documents_async", new=AsyncMock()),
            patch(f"{_MOD}.log_info"),
        ):
            self._run(app.run("http://site.com", "/tmp/out.jsonl"))
            app.data_ingestion.assert_called_once_with("http://site.com")

    def test_run_saves_docs_to_provided_file_path(self):
        app, vectorstore, tav = _make_app()
        docs = [Document(page_content="text", metadata={})]

        with (
            patch.object(app, "data_ingestion", new=AsyncMock(return_value=docs)),
            patch(f"{_MOD}.save_docs") as mock_save,
            patch(f"{_MOD}.process_documents", return_value=docs),
            patch(f"{_MOD}.index_documents_async", new=AsyncMock()),
            patch(f"{_MOD}.log_info"),
        ):
            self._run(app.run("http://site.com", "/tmp/out.jsonl"))
            mock_save.assert_called_once_with(docs, "/tmp/out.jsonl")

    def test_run_processes_documents_from_file(self):
        app, vectorstore, tav = _make_app()
        docs = [Document(page_content="text", metadata={})]

        with (
            patch.object(app, "data_ingestion", new=AsyncMock(return_value=docs)),
            patch(f"{_MOD}.save_docs"),
            patch(f"{_MOD}.process_documents", return_value=docs) as mock_proc,
            patch(f"{_MOD}.index_documents_async", new=AsyncMock()),
            patch(f"{_MOD}.log_info"),
        ):
            self._run(app.run("http://site.com", "/tmp/out.jsonl"))
            mock_proc.assert_called_once_with("/tmp/out.jsonl")

    def test_run_indexes_processed_documents(self):
        app, vectorstore, tav = _make_app()
        raw_docs = [Document(page_content="raw", metadata={})]
        split_docs = [Document(page_content="chunk", metadata={})]

        with (
            patch.object(app, "data_ingestion", new=AsyncMock(return_value=raw_docs)),
            patch(f"{_MOD}.save_docs"),
            patch(f"{_MOD}.process_documents", return_value=split_docs),
            patch(f"{_MOD}.index_documents_async", new=AsyncMock()) as mock_index,
            patch(f"{_MOD}.log_info"),
        ):
            self._run(app.run("http://site.com", "/tmp/out.jsonl"))
            mock_index.assert_called_once_with(
                app.vectorstore, split_docs, batch_size=500
            )


class DataIngestionTest(unittest.TestCase):
    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_data_ingestion_invokes_site_map(self):
        # data_ingestion() must call tavily_map.invoke with the given URL.
        app, vectorstore, tav = _make_app()
        tav.tavily_map.invoke.return_value = {
            "results": ["http://a.com", "http://b.com"]
        }
        tav.async_extract = AsyncMock(return_value=[])

        with patch(f"{_MOD}.log_info"), patch(f"{_MOD}.log_success"):
            self._run(app.data_ingestion("http://site.com"))

        tav.tavily_map.invoke.assert_called_once_with("http://site.com")

    def test_data_ingestion_chunks_urls_and_passes_to_async_extract(self):
        # The URL list from the site map is chunked and forwarded to
        # async_extract. The exact chunk structure is governed by chunk_urls
        # (tested separately); here we only verify async_extract is called.
        app, vectorstore, tav = _make_app()
        tav.tavily_map.invoke.return_value = {
            "results": ["http://a.com", "http://b.com", "http://c.com"]
        }
        extracted_docs = [Document(page_content="doc", metadata={})]
        tav.async_extract = AsyncMock(return_value=extracted_docs)

        with patch(f"{_MOD}.log_info"), patch(f"{_MOD}.log_success"):
            result = self._run(app.data_ingestion("http://site.com"))

        tav.async_extract.assert_called_once()
        self.assertEqual(result, extracted_docs)

    def test_data_ingestion_returns_extracted_documents(self):
        # Return value must be exactly what async_extract returned.
        app, vectorstore, tav = _make_app()
        tav.tavily_map.invoke.return_value = {"results": ["http://x.com"]}
        docs = [
            Document(page_content="x", metadata={}),
            Document(page_content="y", metadata={}),
        ]
        tav.async_extract = AsyncMock(return_value=docs)

        with patch(f"{_MOD}.log_info"), patch(f"{_MOD}.log_success"):
            result = self._run(app.data_ingestion("http://site.com"))

        self.assertEqual(result, docs)
