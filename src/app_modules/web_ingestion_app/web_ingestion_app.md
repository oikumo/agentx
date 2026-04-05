# App Modules - Web Ingestion

## Overview
End-to-end web scraping pipeline using Tavily → chunk → index into vector store.

## Key Files

| File | Description |
|------|-------------|
| `web_ingestion_app.py` | `WebIngestionApp` - orchestrates full pipeline |
| `web_ingestion.py` | Entry point script |
| `tavily.py` | `WebExtract` class - TavilyExtract and TavilyMap wrappers |
| `documents.py` | Document processing and async batched indexing |
| `helpers.py` | JSONL serialization, URL chunking, loading |

## Pipeline Flow
```
site_url
    │
    ▼
TavilyMap.invoke(site_url)          → discovers all URLs on site
    │
    ▼
chunk_urls(urls, chunk_size=3)      → batches URLs
    │
    ▼
WebExtract.async_extract(batches)   → concurrent TavilyExtract per batch
    │                                   → builds Document(page_content, metadata)
    ▼
save_docs(docs, "documents.jsonl")  → serializes to JSONL
    │
    ▼
process_documents(jsonl_path)       → loads + RecursiveCharacterTextSplitter
    │                                   (chunk_size=4000, overlap=200)
    ▼
index_documents_async(vectorstore)  → async batched aadd_documents (batch_size=500)
    │
    ▼
VectorStore ready for RAG queries
```

## Key Design Choices
- Async concurrency for extraction and indexing
- Batch processing to avoid rate limits
- JSONL as intermediate persistence
- SSL cert handling via `certifi`
