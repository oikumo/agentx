import os
import ssl

import certifi
from dotenv import load_dotenv
from langchain_core.vectorstores import VectorStore

from agent_x.applications.web_ingestion_app.documents import (
    index_documents_async, process_documents)
from agent_x.applications.web_ingestion_app.helpers import (chunk_urls,
                                                            save_docs)
from agent_x.applications.web_ingestion_app.tavily import WebExtract
from agent_x.common.logger import Colors, log_info, log_success

load_dotenv()

ssl_context = ssl.create_default_context(cafile=certifi.where())
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUEST_CA_BUNDLE"] = certifi.where()


class WebIngestionApp:
    def __init__(
        self,
        vectorstore: VectorStore,
        tav: WebExtract,
        site_url: str = "",
        result_json_file_path: str = "results.jsonl",
    ):
        self.vectorstore = vectorstore
        self.tav = tav
        self.site_url = site_url
        self.result_json_file_path = result_json_file_path

    def configure(self, site_url: str, result_json_file_path: str) -> "WebIngestionApp":
        self.site_url = site_url
        self.result_json_file_path = result_json_file_path
        return self

    async def run(self):
        log_info("INIT")
        log_info(f"map and extract from: {self.site_url}", Colors.PURPLE)
        log_info(f"generated document file path: {self.result_json_file_path}")

        all_docs = await self.data_ingestion(self.site_url)

        log_info(f"SAVING DOCS")
        save_docs(all_docs, self.result_json_file_path)

        log_info("DOCUMENTS CHUNKING PHASE")
        docs = process_documents(self.result_json_file_path)

        log_info("DOCUMENTS INDEXING")
        await index_documents_async(self.vectorstore, docs, batch_size=500)

    async def data_ingestion(self, site_url: str):
        log_info("site mapping")
        site_map = self.tav.tavily_map.invoke(site_url)
        log_info(f"results: {site_map}")
        log_success(f"site map: {len(site_map['results'])}")

        urls_batches = chunk_urls(site_map["results"], 3)
        all_docs = await self.tav.async_extract(urls_batches=urls_batches)
        log_info(f"docs extracted: {len(all_docs)}")

        return all_docs
