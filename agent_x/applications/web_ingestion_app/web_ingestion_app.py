import asyncio
import os
import ssl

import certifi
from dotenv import load_dotenv
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from agent_x.applications.web_ingestion_app.documents import index_documents_async
from agent_x.applications.web_ingestion_app.helpers import chunk_urls, load_docs_from_jsonl
from agent_x.applications.web_ingestion_app.tavily import WebExtract
from agent_x.core.common.logger import log_header, log_info, Colors, log_success, log_error

load_dotenv()

ssl_context = ssl.create_default_context(cafile=certifi.where())
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUEST_CA_BUNDLE"] = certifi.where()

class WebIngestionApp:
    def __init__(self, vectorstore: VectorStore):
        self.vectorstore = vectorstore

    def run(self, site_url: str, result_json_file_path: str):
        asyncio.run(self.data_ingestion(site_url, result_json_file_path))

    async def data_ingestion(self,site_url: str, result_json_file_path: str):
        """Main async function"""
        log_header("INIT")
        log_info(f"Tavily Map and Extract from: {site_url}", Colors.PURPLE)

        log_info(f"Generated document file path: {result_json_file_path}")

        tav = WebExtract(1,1, 1000)

        log_header("SITE MAPPING")
        site_map = tav.tavily_map.invoke(site_url)
        log_info(f"results: {site_map}")
        log_success(f"Site map: {len(site_map['results'])}")

        urls_batches = chunk_urls(site_map['results'], 3)
        all_docs = await tav.async_extract(urls_batches=urls_batches)
        log_info(f"Docs extracted: {len(all_docs)}")

        with open(result_json_file_path, "w") as jsonl_file:
            for doc in all_docs:
                jsonl_file.write(doc.model_dump_json() + "\n")

        all_docs = load_docs_from_jsonl(result_json_file_path)

        log_header("DOCUMENTS CHUNKING PHASE")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
        splitted_docs = text_splitter.split_documents(all_docs)

        log_success(f"splitted docs: {len(splitted_docs)}")

        await index_documents_async(self.vectorstore, splitted_docs, batch_size=500)
