import asyncio
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from agentx.model.rag.web_ingestion.helpers import load_docs_from_jsonl
from agentx.views.common.console import Console


async def index_documents_async(vectorstore, documents: List[Document], batch_size: int = 50):
    Console.log_info("VECTOR STORE PHASE")
    Console.log_info(f"Documents to store: {len(documents)}")

    batches = [
        documents[i: batch_size + 1] for i in range(0, len(documents), batch_size)
    ]

    Console.log_info(f"Splitted into {len(batches)} batches of size {batch_size}")

    # Process all batches concurrently
    async def add_batch(batch: List[Document], batch_num: int):
        try:
            await vectorstore.aadd_documents(batch)
            Console.log_success("OK")
        except Exception as e:
            Console.log_error(f"Error adding batch, e{e}")
            return False
        return True

    tasks = [add_batch(batch, i + 1) for i, batch in enumerate(batches)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successful = sum(1 for result in results if result is True)

    if successful == len(batches):
        Console.log_success(f"Documents processed {successful}/{len(batches)}")
    else:
        Console.log_error(f"Documents processed {successful}/{len(batches)}")

def process_documents(result_json_file_path: str) -> list[Document]:
    all_docs = load_docs_from_jsonl(result_json_file_path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
    processed_docs = text_splitter.split_documents(all_docs)
    Console.log_success(f"splitted docs: {len(processed_docs)}")
    
    return processed_docs