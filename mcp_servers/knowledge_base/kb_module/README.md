# KB Module - Knowledge Base Library for MCP

This module provides a clean, MCP-friendly API for the Meta Project Harness Knowledge Base.

## Structure

```
kb_module/
├── __init__.py    # Public API exports
└── core.py        # Core implementation
```

## API Functions

### `kb_search(query, top_k=5, category=None)`

Search the knowledge base for relevant entries.

**Parameters:**
- `query` (str): Search query string
- `top_k` (int): Number of results to return (default: 5)
- `category` (str, optional): Category filter

**Returns:** `KBSearchResult` with:
- `success` (bool): Whether search succeeded
- `entries` (List[KBEntry]): List of matching entries
- `message` (str): Status message
- `error` (str, optional): Error message if failed

### `kb_ask(question, top_k=3)`

Ask a question and get RAG-augmented response.

**Parameters:**
- `question` (str): Question to ask
- `top_k` (int): Number of context entries (default: 3)

**Returns:** `KBAskResult` with:
- `success` (bool): Whether query succeeded
- `answer` (str): Synthesized answer
- `sources` (List[str]): Source citations
- `confidence` (float): Average confidence score
- `error` (str, optional): Error message if failed

### `kb_add_entry(entry_type, category, title, finding, solution, context="", confidence=0.5, example="")`

Add new entry to knowledge base.

**Parameters:**
- `entry_type` (str): pattern | finding | decision | correction
- `category` (str): code | class | method | function | workflow | documentation | architecture
- `title` (str): Entry title
- `finding` (str): Main finding/insight
- `solution` (str): Solution/recommendation
- `context` (str, optional): Additional context
- `confidence` (float, optional): Confidence 0.0-1.0 (default: 0.5)
- `example` (str, optional): Example code/text

**Returns:** Dict with success status and message

### `kb_stats()`

Get knowledge base statistics.

**Returns:** Dict with:
- `total_entries`: Total count
- `by_type`: Counts per type
- `by_category`: Counts per category
- `confidence_distribution`: High/medium/low counts
- `pending_corrections`: Number pending

## Data Classes

### `KBEntry`
Represents a knowledge base entry with fields:
- `id`, `type`, `category`, `title`
- `finding`, `solution`, `context`, `example`
- `confidence`

### `KBSearchResult`
Search operation result with fields:
- `success`, `entries`, `message`, `error`

### `KBAskResult`
Ask operation result with fields:
- `success`, `answer`, `sources`, `confidence`, `error`

## Usage Example

```python
from kb_module import kb_search, kb_ask, kb_add_entry, kb_stats

# Search
result = kb_search("TDD", top_k=5)
if result.success:
    for entry in result.entries:
        print(f"{entry.title}: {entry.finding}")

# Ask
result = kb_ask("How to write tests?")
if result.success:
    print(result.answer)
    print(f"Sources: {result.sources}")

# Add entry
result = kb_add_entry(
    "pattern", "code", "Test Pattern",
    "Use TDD", "Write tests first",
    confidence=0.9
)

# Stats
result = kb_stats()
print(f"Total entries: {result['total_entries']}")
```

## Dependencies

This module requires:
- ChromaDB (for vector storage)
- The original KB implementation at `.meta/tools/meta-harness-knowledge-base/`

## Notes

- This module wraps the original KB implementation to provide an MCP-friendly API
- All operations use ChromaDB for vector storage and retrieval
- Error handling is built into all functions
- The module is designed to be imported and used by the MCP server
