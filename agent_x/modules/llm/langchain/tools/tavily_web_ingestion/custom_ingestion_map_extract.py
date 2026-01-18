import asyncio
import os
import ssl
from typing import Any, Dict, List

import certifi
from dotenv import load_dotenv
from rich.console import Console

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_tavily import TavilyCrawl, TavilyExtract, TavilyMap

import json

from agent_x.core.common.logger import log_info, Colors, log_error, log_header, log_success

load_dotenv()

site_url = "https://www.verifone.cloud/docs/device-management/device-management-user-guide/"
result_json_file_path = "sessions/web_ingestion/saved_documents_vf_device_management.jsonl"
vectorstore_chroma_dir = "sessions/web_ingestion/chroma_db_vf_device_management"

ssl_context = ssl.create_default_context(cafile=certifi.where())
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUEST_CA_BUNDLE"] = certifi.where()

"""
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    show_progress_bar=False,
    chunk_size=50,
    retry_min_seconds=10,)
"""
embeddings = OllamaEmbeddings(model="nomic-embed-text")
#embeddings = OllamaEmbeddings(model="embeddinggemma")

vectorstore = Chroma(persist_directory=vectorstore_chroma_dir, embedding_function=embeddings)
#vectorstore = PineconeVectorStore(index_name=os.environ["INDEX_NAME_DOCUMENT_HELPER"], embedding=embeddings)

tavily_extract = TavilyExtract()
tavily_map = TavilyMap(max_depth=1, max_breadth=2, max_pages=1000)
#tavily_crawl = TavilyCrawl()

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
    log_info(f"Concurrent extraction of {len(urls_batches)}",Colors.GREEN)

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


async def index_documents_async(documents: List[Document], batch_size: int= 50):
    log_header("VECTOR STORE PHASE")
    log_info(f"Documents to store: {len(documents)}")

    batches = [
        documents[i : batch_size + 1] for i in range(0, len(documents),batch_size)
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

async def data_ingestion():
    """Main async function"""
    log_header("INIT")

    log_info(f"Tavily Map and Extract from: {site_url}", Colors.PURPLE)
    log_info(f"Vector store Chroma: {vectorstore_chroma_dir}")
    

    log_info(f"Generated document file path: {result_json_file_path}")
    
    log_header("SITE MAPPING")
    site_map = tavily_map.invoke(site_url)
    log_success(f"Site map: {len(site_map['results'])}")

    urls_batches = chunk_urls(site_map['results'], 3)
    all_docs = await async_extract(urls_batches=urls_batches)
    log_info(f"Docs extracted: {len(all_docs)}")
    
    with open(result_json_file_path , "w") as jsonl_file:
        for doc in all_docs:
            jsonl_file.write(doc.model_dump_json() + "\n")

    all_docs = load_docs_from_jsonl(result_json_file_path)

    log_header("DOCUMENTS CHUNKING PHASE")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
    splitted_docs = text_splitter.split_documents(all_docs)

    log_success(f"splitted docs: {len(splitted_docs)}")

    await index_documents_async(splitted_docs, batch_size=500)