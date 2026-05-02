from langchain_core.vectorstores import VectorStore

from agentx.services.rag.web_ingestion.documents import process_documents, index_documents_async
from agentx.services.rag.web_ingestion.helpers import save_docs, chunk_urls
from agentx.services.rag.web_ingestion.web_extract import WebExtract
from agentx.views.common.console import Colors, Console


class WebIngestionApp:
    def __init__(self, vectorstore: VectorStore, tav: WebExtract):
        self.vectorstore = vectorstore
        self.tav = tav


    async def run(self, site_url: str, result_json_file_path: str):
        Console.log_info("INIT")
        Console.log_info(f"map and extract from: {site_url}", Colors.PURPLE)
        Console.log_info(f"generated document file path: {result_json_file_path}")

        all_docs = await self.data_ingestion(site_url)

        Console.log_info(f"SAVING DOCS")
        save_docs(all_docs, result_json_file_path)

        Console.log_info("DOCUMENTS CHUNKING PHASE")
        docs = process_documents(result_json_file_path)

        Console.log_info("DOCUMENTS INDEXING")
        await index_documents_async(self.vectorstore, docs, batch_size=500)


    async def data_ingestion(self,site_url: str):
        Console.log_info("site mapping")
        site_map = self.tav.tavily_map.invoke(site_url)
        Console.log_info(f"results: {site_map}")
        Console.log_success(f"site map: {len(site_map['results'])}")

        urls_batches = chunk_urls(site_map['results'], 3)
        all_docs = await self.tav.async_extract(urls_batches=urls_batches)
        Console.log_info(f"docs extracted: {len(all_docs)}")

        return all_docs