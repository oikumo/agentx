# App Modules - Web Ingestion - Agent-X

**Path**: `src/app_modules/web_ingestion_app/`

Web scraping pipeline: Tavily → chunk → index.

---

## Module Structure

```
src/app_modules/web_ingestion_app/
├── documents.py               # document processing
├── helpers.py                 # JSONL helpers
├── tavily.py                  # WebExtract
├── web_ingestion.py           # entry point script
└── web_ingestion_app.py       # WebIngestionApp
```

---

## Tavily Extraction

### tavily.py

**Class**: `WebExtract`

TavilyExtract and TavilyMap wrappers for web content extraction.

**Methods**:
- `__init__(max_depth: int, max_breadth: int, max_pages: int)` - initializes `TavilyExtract` and `TavilyMap`
- `async def extract_batch(urls: List[str], batch_num: int) -> List[Dict[str, Any]]` - async extraction from a batch of URLs
- `async def async_extract(urls_batches: List[List[str]])` - concurrent extraction across all batches, returns list of `Document` objects

---

## Helpers

### helpers.py

**Functions**:
- `save_docs(all_docs: list[Any], result_json_file_path: str)` - writes documents to JSONL file via `model_dump_json()`
- `chunk_urls(urls: List[str], chunk_size: int = 3) -> List[List[str]]` - splits URL list into chunks
- `load_docs_from_jsonl(file_path)` - reads documents from JSONL file

---

## Document Processing

### documents.py

**Functions**:
- `async def index_documents_async(vectorstore, documents: List[Document], batch_size: int = 50)` - async batched document insertion into vector store
- `process_documents(result_json_file_path: str) -> list[Document]` - loads docs from JSONL, splits with `RecursiveCharacterTextSplitter` (chunk_size=4000, chunk_overlap=200)

---

## Web Ingestion App

### web_ingestion_app.py

**Class**: `WebIngestionApp`

Orchestrates the complete web ingestion pipeline.

**Methods**:
- `__init__(vectorstore: VectorStore, tav: WebExtract, site_url: str, result_json_file_path: str)` - stores configuration
- `configure(site_url: str, result_json_file_path: str) -> WebIngestionApp` - fluent configuration
- `async def run()` - async full pipeline:
  1. Map site URLs via TavilyMap
  2. Extract content in batches
  3. Save docs to JSONL
  4. Process and chunk documents
  5. Index into vector store
- `async def data_ingestion(site_url: str)` - maps site URLs and extracts content

**Pipeline Flow**:
```
TavilyMap → chunk_urls → WebExtract.async_extract → save_docs (JSONL)
    → process_documents → index_documents_async → VectorStore
```

### web_ingestion.py

Standalone entry point script for web ingestion. Creates session, vector store (Chroma), and runs `WebIngestionApp`.
