# Knowledge Base MCP Integration Guide for opencode

## Overview

The Knowledge Base MCP (Model Context Protocol) tool provides opencode with tools to interact with the Meta Project Harness Knowledge Base using RAG (Retrieval-Augmented Generation).

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ opencode AI Agent                                       │
│                                                         │
│  1. Receives task from user                             │
│  2. Calls kb_ask() for guidance                        │
│  3. Gets augmented prompt with context                 │
│  4. Generates answer using retrieved knowledge          │
│  5. Completes task                                     │
│  6. Calls kb_add_entry() to document findings          │
└─────────────────────────────────────────────────────────┘
                            │
                            │ JSON over stdin/stdout
                            ▼
┌─────────────────────────────────────────────────────────┐
│ MCP Server (knowledge_base_server.py)                  │
│                                                         │
│  - Routes tool calls to rag_tool functions             │
│  - Handles JSON serialization                          │
│  - Manages SQLite connections                          │
└─────────────────────────────────────────────────────────┘
                            │
                            │ Python imports
                            ▼
┌─────────────────────────────────────────────────────────┐
│ RAG Tool (rag_tool.py)                                  │
│                                                         │
│  - rag_search(): Hybrid search (FTS5 + keyword)        │
│  - rag_ask(): RAG-augmented Q&A                         │
│  - rag_add_entry(): Add new knowledge                   │
│  - rag_correct(): Auto-correct knowledge                │
│  - rag_evolve(): Run evolution cycle                    │
│  - rag_stats(): Get statistics                          │
└─────────────────────────────────────────────────────────┘
                            │
                            │ SQLite
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Knowledge Base (.meta.knowledge_base/knowledge.db)     │
│                                                         │
│  - entries: Knowledge entries with embeddings          │
│  - corrections: Auto-correction history                │
│  - evolution_log: Evolution events                     │
│  - FTS5: Full-text search index                        │
└─────────────────────────────────────────────────────────┘
```

## Integration Methods

### Method 1: Direct Python Import (Recommended)

```python
from .meta.development_tools.mcp.rag_tool import (
    rag_search,
    rag_ask,
    rag_add_entry,
    rag_correct,
    rag_evolve,
    rag_stats
)

# Before task: Ask for guidance
result = rag_ask("Where should I implement this feature?")
print(result["augmented_prompt"])

# After task: Document discovery
result = rag_add_entry(
    entry_type="pattern",
    category="workflow",
    title="My Discovery",
    finding="What I found",
    solution="How to handle it"
)
```

### Method 2: MCP Server (stdin/stdout)

```python
import subprocess
import json

def call_mcp_tool(tool_name, params=None):
    """Call MCP tool via stdin/stdout."""
    proc = subprocess.Popen(
        ["python3", ".meta.development_tools/mcp/knowledge_base_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    request = json.dumps({
        "tool": tool_name,
        "params": params or {}
    })
    
    stdout, stderr = proc.communicate(request + "\n")
    
    # Parse last JSON line from output
    for line in reversed(stdout.strip().split("\n")):
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    
    return {"success": False, "error": "No valid response"}

# Usage
result = call_mcp_tool("kb_search", {"query": "TDD", "top_k": 3})
```

### Method 3: Command Line

```bash
# Search
echo '{"tool": "kb_search", "params": {"query": "TDD"}}' | \
  python3 .meta.development_tools/mcp/knowledge_base_server.py

# Ask
echo '{"tool": "kb_ask", "params": {"question": "Where to write tests?"}}' | \
  python3 .meta.development_tools/mcp/knowledge_base_server.py

# Add entry
echo '{"tool": "kb_add_entry", "params": {
  "type": "pattern",
  "category": "workflow",
  "title": "My Pattern",
  "finding": "What I found",
  "solution": "How to handle"
}}' | python3 .meta.development_tools/mcp/knowledge_base_server.py
```

## Tool Reference

### kb_search

Search the knowledge base for relevant entries.

**Parameters:**
- `query` (string, required): Search query
- `top_k` (int, optional): Number of results (default: 5)
- `category` (string, optional): Filter by category

**Example:**
```python
result = rag_search("TDD workflow", top_k=3, category="workflow")
# Returns:
# {
#   "success": true,
#   "query": "TDD workflow",
#   "count": 1,
#   "results": [...],
#   "message": "Found 1 relevant entries"
# }
```

### kb_ask

Ask a question with RAG-augmented context.

**Parameters:**
- `question` (string, required): Question to ask
- `top_k` (int, optional): Number of context entries (default: 3)

**Example:**
```python
result = rag_ask("Where should I write tests?")
# Returns:
# {
#   "success": true,
#   "question": "Where should I write tests?",
#   "augmented_prompt": "You are an AI agent...\n\n### Retrieved Knowledge:\n...",
#   "context_count": 3,
#   "retrieved_context": [...],
#   "message": "Retrieved 3 relevant entries"
# }
```

### kb_add_entry

Add a new knowledge entry.

**Parameters:**
- `type` (string, required): Entry type (pattern, finding, decision, correction)
- `category` (string, required): Category (workflow, code, test, docs, tool, architecture)
- `title` (string, required): Concise title
- `finding` (string, required): What was discovered
- `solution` (string, required): How to solve it
- `context` (string, optional): When/where this applies
- `confidence` (float, optional): Confidence score (0.0-1.0, default: 0.5)

**Example:**
```python
result = rag_add_entry(
    entry_type="pattern",
    category="workflow",
    title="Feature Implementation",
    finding="Work in .meta.sandbox/",
    solution="Copy → Modify → Test",
    context="When implementing features",
    confidence=0.95
)
# Returns:
# {
#   "success": true,
#   "entry_id": "PAT-XXXX",
#   "message": "Added PATTERN entry: PAT-XXXX - Feature Implementation"
# }
```

### kb_correct

Add a correction to an existing entry.

**Parameters:**
- `entry_id` (string, required): ID of entry to correct
- `reason` (string, required): Why correction is needed
- `new_finding` (string, required): Updated information

**Example:**
```python
result = rag_correct(
    entry_id="PAT-50B1",
    reason="Workflow updated in v2.0",
    new_finding="Use .meta.experiments/ for prototyping"
)
# Returns:
# {
#   "success": true,
#   "correction_id": "COR-XXXX",
#   "old_confidence": 0.95,
#   "new_confidence": 0.75,
#   "message": "Added correction to PAT-50B1. Confidence: 0.95 → 0.75"
# }
```

### kb_evolve

Run evolution cycle (decay unused entries, archive low confidence).

**Parameters:** None

**Example:**
```python
result = rag_evolve()
# Returns:
# {
#   "success": true,
#   "decayed": 0,
#   "archived": 0,
#   "pending_corrections": 2,
#   "message": "Evolution complete: 0 decayed, 0 archived, 2 pending corrections"
# }
```

### kb_stats

Get knowledge base statistics.

**Parameters:** None

**Example:**
```python
result = rag_stats()
# Returns:
# {
#   "success": true,
#   "total_entries": 10,
#   "by_type": {...},
#   "by_category": {...},
#   "confidence_distribution": {...},
#   "pending_corrections": 2,
#   "message": "KB Stats: 10 entries, 2 pending corrections"
# }
```

## Usage Patterns

### Pattern 1: Pre-Task Research

```python
# 1. Ask for guidance before starting
result = rag_ask("Where should I implement this feature?")

# 2. Use the augmented prompt to generate answer
print(result["augmented_prompt"])

# 3. Generate response using retrieved context
# LLM uses the augmented_prompt to answer the question
```

### Pattern 2: Post-Task Documentation

```python
# After completing a task, document the pattern
result = rag_add_entry(
    entry_type="pattern",
    category="workflow",
    title="My Discovery",
    finding="What I discovered",
    solution="How to handle it"
)
```

### Pattern 3: Knowledge Evolution

```python
# Periodically run evolution
result = rag_evolve()
print(result["message"])

# Check statistics
result = rag_stats()
print(f"Total entries: {result['total_entries']}")
```

### Pattern 4: Error Correction

```python
# When discovering outdated knowledge
result = rag_correct(
    entry_id="PAT-XXXX",
    reason="Better approach found",
    new_finding="New approach details"
)
```

## Best Practices

1. **Use `kb_ask` for questions**: It provides RAG-augmented context
2. **Use `kb_search` for lookups**: Direct search without augmentation
3. **Add entries immediately**: After discovering patterns
4. **Use high confidence**: Only for verified knowledge (0.9+)
5. **Run `kb_evolve` weekly**: Maintain knowledge quality

## Troubleshooting

### No results from search
- Try broader query
- Check spelling
- Verify KB exists: `.meta.knowledge_base/knowledge.db`

### Database locked error
- Wait for other processes to finish
- Check for long-running queries
- Increase timeout in `get_db_connection()`

### Low confidence results
- Results with confidence < 0.6 may not appear
- Lower confidence entries need verification

## Testing

```bash
# Run test suite
python .meta.development_tools/mcp/test_kb_tools.py

# Test individual tool
python -c "from rag_tool import rag_ask; print(rag_ask('tests'))"
```

## Files

```
.meta.development_tools/mcp/
├── rag_tool.py                   # Main RAG tool (Python module)
├── knowledge_base_server.py      # MCP server wrapper
├── test_kb_tools.py              # Test suite
├── README.md                     # User guide
├── MCP_README.md                 # Detailed documentation
└── INTEGRATION.md                # This file
```

---

**Version**: 1.0.0  
**Location**: `.meta.development_tools/mcp/`  
**Status**: ✅ Complete and Ready
