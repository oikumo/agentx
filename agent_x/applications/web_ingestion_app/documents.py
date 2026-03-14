import asyncio
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from agent_x.applications.web_ingestion_app.helpers import load_docs_from_jsonl
from agent_x.common.logger import log_error, log_info, log_success


async def index_documents_async(
    vectorstore, documents: List[Document], batch_size: int = 50
):
    log_info("VECTOR STORE PHASE")
    log_info(f"Documents to store: {len(documents)}")

    batches = [
        documents[i : i + batch_size] for i in range(0, len(documents), batch_size)
    ]

    log_info(f"Splitted into {len(batches)} batches of size {batch_size}")

    # Process all batches concurrently
    async def add_batch(batch: List[Document], batch_num: int):
        try:
            await vectorstore.aadd_documents(batch)
            log_success("OK")
        except Exception as e:
            log_error(f"Error adding batch, e{e}")
            return False
        return True

    tasks = [add_batch(batch, i + 1) for i, batch in enumerate(batches)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successful = sum(1 for result in results if result is True)

    if successful == len(batches):
        log_success(f"Documents processed {successful}/{len(batches)}")
    else:
        log_error(f"Documents processed {successful}/{len(batches)}")


def process_documents(result_json_file_path: str) -> list[Document]:
    all_docs = load_docs_from_jsonl(result_json_file_path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
    splitted_docs = text_splitter.split_documents(all_docs)

    log_success(f"splitted docs: {len(splitted_docs)}")
    return splitted_docs
