import os
import ssl

import certifi
from dotenv import load_dotenv
from langchain_core.vectorstores import VectorStore

from agent_x.applications.web_ingestion_app.documents import index_documents_async, process_documents
from agent_x.applications.web_ingestion_app.helpers import chunk_urls, save_docs
from agent_x.applications.web_ingestion_app.tavily import WebExtract
from agent_x.core.common.logger import log_info, Colors, log_success

load_dotenv()

ssl_context = ssl.create_default_context(cafile=certifi.where())
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUEST_CA_BUNDLE"] = certifi.where()


class WebIngestionApp:
    def __init__(self, vectorstore: VectorStore, tav: WebExtract):
        self.vectorstore = vectorstore
        self.tav = tav

    async def run(self, site_url: str, result_json_file_path: str):
        log_info("INIT")
        all_docs = await self.data_ingestion(site_url, result_json_file_path)

        log_info(f"SAVING DOCS")
        save_docs(all_docs, result_json_file_path)

        log_info("DOCUMENTS CHUNKING PHASE")
        docs = process_documents(result_json_file_path)

        log_info("DOCUMENTS INDEXING")
        await index_documents_async(self.vectorstore, docs, batch_size=500)


    async def data_ingestion(self,site_url: str, result_json_file_path: str):
        """Main async function"""

        log_info(f"Tavily Map and Extract from: {site_url}", Colors.PURPLE)
        log_info(f"Generated document file path: {result_json_file_path}")

        log_info("site mapping")
        site_map = self.tav.tavily_map.invoke(site_url)
        log_info(f"results: {site_map}")
        log_success(f"site map: {len(site_map['results'])}")

        urls_batches = chunk_urls(site_map['results'], 3)
        all_docs = await self.tav.async_extract(urls_batches=urls_batches)
        log_info(f"docs extracted: {len(all_docs)}")

        return all_docs


