import json
from typing import List, Any

from langchain_core.documents import Document

def save_docs(all_docs: list[Any], result_json_file_path: str):
    with open(result_json_file_path, "w") as jsonl_file:
        for doc in all_docs:
            jsonl_file.write(doc.model_dump_json() + "\n")

def chunk_urls(urls: List[str], chunk_size: int = 3) -> List[List[str]]:
    """Split URLs into chunks of specified size."""
    chunks = []
    for i in range(0, len(urls), chunk_size):
        chunk = urls[i:i + chunk_size]
        chunks.append(chunk)
    return chunks


def load_docs_from_jsonl(file_path):
    loaded_documents = []
    with open(file_path, "r") as jsonl_file:
        for line in jsonl_file:
            data = json.loads(line)
            loaded_documents.append(Document(**data))
    return loaded_documents


