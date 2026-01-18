import asyncio
import json
from typing import Any, Dict, List

from langchain_core.documents import Document

from agent_x.applications.web_ingestion_app.tavily import tavily_extract
from agent_x.core.common.logger import log_info, Colors, log_error, log_header, log_success


def chunk_urls(urls: List[str], chunk_size: int = 3) -> List[List[str]]:
    """Split URLs into chunks of specified size."""
    chunks = []
    for i in range(0, len(urls), chunk_size):
        chunk = urls[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

async def extract_batch(urls: List[str], batch_num: int) -> List[Dict[str, Any]]:
    """Extract documents from a batch of URLs."""
    try:
        log_info(f"🔄 Processing batch {batch_num} with {len(urls)} URLs", Colors.BLUE)
        docs = await tavily_extract.ainvoke(input={"urls": urls})
        results = docs.get('results', [])
        log_info(f"✅ Batch {batch_num} completed - extracted {len(results)} documents", Colors.PURPLE)
        return results
    except Exception as e:
        log_error(f"❌ Batch {batch_num} failed: {e}", Colors.RED)
        return []

async def async_extract(urls_batches: List[List[str]]):
    log_header("DOCUMENT EXTRACTION")
    log_info(f"Concurrent extraction of {len(urls_batches)}", Colors.GREEN)

    tasks = [extract_batch(batch, i + 1) for i, batch in enumerate(urls_batches)]

    log_info("EXTRACT BEGIN", Colors.GREEN)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    log_info("EXTRACT END", Colors.GREEN)

    all_pages = []
    failed_batches = 0

    for result in results:
        if isinstance(result, Exception):
            log_error("Error")
            failed_batches += 1
        else:
            for extracted_page in result:
                document = Document(
                    page_content=extracted_page["raw_content"],
                    metadata={"source": extracted_page["url"]}
                )

                all_pages.append(document)

    return all_pages

def load_docs_from_jsonl(file_path):
    loaded_documents = []
    with open(file_path, "r") as jsonl_file:
        for line in jsonl_file:
            data = json.loads(line)
            loaded_documents.append(Document(**data))
    return loaded_documents


