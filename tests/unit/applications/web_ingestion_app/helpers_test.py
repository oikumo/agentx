import json
import os
import tempfile
import unittest

from langchain_core.documents import Document

from agent_x.applications.web_ingestion_app.helpers import (
    chunk_urls, load_docs_from_jsonl, save_docs)


class ChunkUrlsTest(unittest.TestCase):
    # chunk_urls is pure — no I/O, fully deterministic.

    def test_chunk_urls_splits_into_correct_number_of_chunks(self):
        urls = ["a", "b", "c", "d", "e", "f", "g"]
        chunks = chunk_urls(urls, chunk_size=3)
        self.assertEqual(len(chunks), 3)

    def test_chunk_urls_each_chunk_has_correct_size(self):
        urls = ["a", "b", "c", "d", "e", "f"]
        chunks = chunk_urls(urls, chunk_size=2)
        for chunk in chunks:
            self.assertEqual(len(chunk), 2)

    def test_chunk_urls_last_chunk_contains_remainder(self):
        # 7 items with chunk_size=3 → last chunk has 1 item.
        urls = ["a", "b", "c", "d", "e", "f", "g"]
        chunks = chunk_urls(urls, chunk_size=3)
        self.assertEqual(chunks[-1], ["g"])

    def test_chunk_urls_default_chunk_size_is_three(self):
        urls = ["a", "b", "c", "d"]
        chunks = chunk_urls(urls)
        self.assertEqual(chunks[0], ["a", "b", "c"])
        self.assertEqual(chunks[1], ["d"])

    def test_chunk_urls_empty_list_returns_empty_list(self):
        self.assertEqual(chunk_urls([]), [])

    def test_chunk_urls_single_url_returns_one_chunk(self):
        chunks = chunk_urls(["only"], chunk_size=3)
        self.assertEqual(chunks, [["only"]])

    def test_chunk_urls_preserves_order(self):
        urls = ["first", "second", "third"]
        chunks = chunk_urls(urls, chunk_size=3)
        self.assertEqual(chunks[0], ["first", "second", "third"])


class SaveDocsAndLoadDocsTest(unittest.TestCase):
    # save_docs and load_docs_from_jsonl are inverse operations.
    # Use a real temp file so no mocking is needed — these functions do only
    # local file I/O with no network or LLM calls.

    def _make_documents(self):
        return [
            Document(
                page_content="hello world", metadata={"source": "http://example.com"}
            ),
            Document(
                page_content="second doc", metadata={"source": "http://other.com"}
            ),
        ]

    def test_save_docs_creates_file_with_one_line_per_document(self):
        docs = self._make_documents()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            path = f.name
        try:
            save_docs(docs, path)
            with open(path) as f:
                lines = [l for l in f if l.strip()]
            self.assertEqual(len(lines), 2)
        finally:
            os.unlink(path)

    def test_save_docs_each_line_is_valid_json(self):
        docs = self._make_documents()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            path = f.name
        try:
            save_docs(docs, path)
            with open(path) as f:
                for line in f:
                    if line.strip():
                        json.loads(line)  # must not raise
        finally:
            os.unlink(path)

    def test_load_docs_from_jsonl_returns_document_instances(self):
        docs = self._make_documents()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            path = f.name
        try:
            save_docs(docs, path)
            loaded = load_docs_from_jsonl(path)
            self.assertEqual(len(loaded), 2)
            for doc in loaded:
                self.assertIsInstance(doc, Document)
        finally:
            os.unlink(path)

    def test_save_and_load_roundtrip_preserves_content_and_metadata(self):
        # Saving then loading must yield the same page_content and metadata.
        docs = self._make_documents()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            path = f.name
        try:
            save_docs(docs, path)
            loaded = load_docs_from_jsonl(path)
            self.assertEqual(loaded[0].page_content, "hello world")
            self.assertEqual(loaded[0].metadata["source"], "http://example.com")
            self.assertEqual(loaded[1].page_content, "second doc")
        finally:
            os.unlink(path)

    def test_load_docs_from_jsonl_empty_file_returns_empty_list(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            path = f.name
        try:
            loaded = load_docs_from_jsonl(path)
            self.assertEqual(loaded, [])
        finally:
            os.unlink(path)
