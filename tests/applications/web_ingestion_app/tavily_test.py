import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.documents import Document

# WebExtract instantiates TavilyExtract and TavilyMap inside __init__, so
# both must be patched at the import site before the class is constructed.
_TAVILY_EXTRACT_PATH = "agent_x.applications.web_ingestion_app.tavily.TavilyExtract"
_TAVILY_MAP_PATH = "agent_x.applications.web_ingestion_app.tavily.TavilyMap"


def _make_web_extract(max_depth=2, max_breadth=5, max_pages=10):
    """Construct a WebExtract with both Tavily clients stubbed out."""
    with patch(_TAVILY_EXTRACT_PATH) as MockExtract, patch(_TAVILY_MAP_PATH) as MockMap:
        from agent_x.applications.web_ingestion_app.tavily import WebExtract

        instance = WebExtract(
            max_depth=max_depth, max_breadth=max_breadth, max_pages=max_pages
        )
    return instance


class WebExtractInitTest(unittest.TestCase):
    def test_init_stores_depth_breadth_pages_on_tavily_map(self):
        with patch(_TAVILY_EXTRACT_PATH), patch(_TAVILY_MAP_PATH) as MockMap:
            from agent_x.applications.web_ingestion_app.tavily import WebExtract

            WebExtract(max_depth=3, max_breadth=7, max_pages=20)
            MockMap.assert_called_once_with(max_depth=3, max_breadth=7, max_pages=20)


class ExtractBatchTest(unittest.TestCase):
    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_extract_batch_returns_results_from_tavily(self):
        with patch(_TAVILY_EXTRACT_PATH) as MockExtract, patch(_TAVILY_MAP_PATH):
            from agent_x.applications.web_ingestion_app.tavily import WebExtract

            mock_extract_instance = MagicMock()
            mock_extract_instance.ainvoke = AsyncMock(
                return_value={
                    "results": [{"raw_content": "text", "url": "http://a.com"}]
                }
            )
            MockExtract.return_value = mock_extract_instance

            we = WebExtract(max_depth=1, max_breadth=1, max_pages=1)

        with patch("agent_x.applications.web_ingestion_app.tavily.log_info"):
            results = self._run(we.extract_batch(["http://a.com"], batch_num=1))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["url"], "http://a.com")

    def test_extract_batch_returns_empty_list_on_exception(self):
        # Any exception from ainvoke must be caught and [] returned.
        with patch(_TAVILY_EXTRACT_PATH) as MockExtract, patch(_TAVILY_MAP_PATH):
            from agent_x.applications.web_ingestion_app.tavily import WebExtract

            mock_extract_instance = MagicMock()
            mock_extract_instance.ainvoke = AsyncMock(
                side_effect=RuntimeError("timeout")
            )
            MockExtract.return_value = mock_extract_instance

            we = WebExtract(max_depth=1, max_breadth=1, max_pages=1)

        with (
            patch("agent_x.applications.web_ingestion_app.tavily.log_info"),
            patch("agent_x.applications.web_ingestion_app.tavily.log_error"),
        ):
            results = self._run(we.extract_batch(["http://bad.com"], batch_num=1))

        self.assertEqual(results, [])

    def test_extract_batch_missing_results_key_returns_empty_list(self):
        # If the response has no "results" key, the default [] is returned.
        with patch(_TAVILY_EXTRACT_PATH) as MockExtract, patch(_TAVILY_MAP_PATH):
            from agent_x.applications.web_ingestion_app.tavily import WebExtract

            mock_extract_instance = MagicMock()
            mock_extract_instance.ainvoke = AsyncMock(return_value={})
            MockExtract.return_value = mock_extract_instance

            we = WebExtract(max_depth=1, max_breadth=1, max_pages=1)

        with patch("agent_x.applications.web_ingestion_app.tavily.log_info"):
            results = self._run(we.extract_batch(["http://a.com"], batch_num=1))

        self.assertEqual(results, [])


class AsyncExtractTest(unittest.TestCase):
    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_async_extract_converts_pages_to_documents(self):
        # Each extracted page dict must become a Document with the correct
        # page_content and metadata["source"].
        raw_page = {"raw_content": "page text", "url": "http://example.com/page"}

        with patch(_TAVILY_EXTRACT_PATH) as MockExtract, patch(_TAVILY_MAP_PATH):
            from agent_x.applications.web_ingestion_app.tavily import WebExtract

            mock_extract_instance = MagicMock()
            mock_extract_instance.ainvoke = AsyncMock(
                return_value={"results": [raw_page]}
            )
            MockExtract.return_value = mock_extract_instance

            we = WebExtract(max_depth=1, max_breadth=1, max_pages=1)

        with patch("agent_x.applications.web_ingestion_app.tavily.log_info"):
            docs = self._run(we.async_extract([[" http://example.com/page"]]))

        self.assertEqual(len(docs), 1)
        self.assertIsInstance(docs[0], Document)
        self.assertEqual(docs[0].page_content, "page text")
        self.assertEqual(docs[0].metadata["source"], "http://example.com/page")

    def test_async_extract_returns_empty_list_when_all_batches_fail(self):
        with patch(_TAVILY_EXTRACT_PATH) as MockExtract, patch(_TAVILY_MAP_PATH):
            from agent_x.applications.web_ingestion_app.tavily import WebExtract

            mock_extract_instance = MagicMock()
            mock_extract_instance.ainvoke = AsyncMock(side_effect=RuntimeError("fail"))
            MockExtract.return_value = mock_extract_instance

            we = WebExtract(max_depth=1, max_breadth=1, max_pages=1)

        with (
            patch("agent_x.applications.web_ingestion_app.tavily.log_info"),
            patch("agent_x.applications.web_ingestion_app.tavily.log_error"),
        ):
            docs = self._run(we.async_extract([["http://fail.com"]]))

        self.assertEqual(docs, [])

    def test_async_extract_aggregates_pages_across_batches(self):
        # Two batches each returning one page → total 2 documents.
        page_a = {"raw_content": "A", "url": "http://a.com"}
        page_b = {"raw_content": "B", "url": "http://b.com"}

        call_count = {"n": 0}

        async def fake_ainvoke(input, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return {"results": [page_a]}
            return {"results": [page_b]}

        with patch(_TAVILY_EXTRACT_PATH) as MockExtract, patch(_TAVILY_MAP_PATH):
            from agent_x.applications.web_ingestion_app.tavily import WebExtract

            mock_extract_instance = MagicMock()
            mock_extract_instance.ainvoke = fake_ainvoke
            MockExtract.return_value = mock_extract_instance

            we = WebExtract(max_depth=1, max_breadth=1, max_pages=1)

        with patch("agent_x.applications.web_ingestion_app.tavily.log_info"):
            docs = self._run(we.async_extract([["http://a.com"], ["http://b.com"]]))

        self.assertEqual(len(docs), 2)
