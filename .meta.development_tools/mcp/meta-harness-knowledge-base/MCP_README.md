# MCP Knowledge Base Tool for opencode

## Overview

This MCP (Model Context Protocol) tool allows **opencode** to interact with the Meta Project Harness Knowledge Base using RAG (Retrieval-Augmented Generation).

## Available Tools

### 1. `kb_search` - Search Knowledge Base

Search for relevant entries in the knowledge base.

**Parameters:**
- `query` (string): Search query
- `top_k` (int, optional): Number of results (default: 5)
- `category` (string, optional): Filter by category

**Example:**
```json
{
  "tool": "kb_search",
  "params": {
    "query": "TDD workflow",
    "top_k": 3
  }
}
```

**Response:**
```json
{
  "success": true,
  "query": "TDD workflow",
  "count": 1,
  "results": [
    {
      "id": "PAT-50B1",
      "type": "pattern",
      "category": "workflow",
      "title": "TDD in .meta.tests_sandbox",
      "confidence": 0.98,
      "finding": "Tests must be written before code",
      "solution": "1. Write test 2. Implement 3. Verify"
    }
  ],
  "message": "Found 1 relevant entries"
}
```

### 2. `kb_ask` - Ask Question (RAG)

Ask a question and get RAG-augmented response with retrieved context.

**Parameters:**
- `question` (string): Question to ask
- `top_k` (int, optional): Number of context entries (default: 3)

**Example:**
```json
{
  "tool": "kb_ask",
  "params": {
    "question": "Where should I write tests?",
    "top_k": 3
  }
}
```

**Response:**
```json
{
  "success": true,
  "question": "Where should I write tests?",
  "augmented_prompt": "You are an AI agent...\n\n### Retrieved Knowledge:\n[1] **TDD in .meta.tests_sandbox**...\n\n### Question:\nWhere should I write tests?\n\n### Your Answer:\n",
  "context_count": 1,
  "retrieved_context": [...],
  "message": "Retrieved 1 relevant entries"
}
```

### 3. `kb_add_entry` - Add Knowledge Entry

Add a new entry to the knowledge base.

**Parameters:**
- `type` (string): Entry type (pattern, finding, decision, correction)
- `category` (string): Category (workflow, code, test, docs, tool, architecture)
- `title` (string): Concise title
- `finding` (string): What was discovered
- `solution` (string): How to solve it
- `context` (string, optional): When/where this applies
- `confidence` (float, optional): Confidence score (0.0-1.0, default: 0.5)

**Example:**
```json
{
  "tool": "kb_add_entry",
  "params": {
    "type": "pattern",
    "category": "workflow",
    "title": "TDD Workflow",
    "finding": "Tests before code",
    "solution": "Write test → Implement → Verify",
    "context": "Feature development",
    "confidence": 0.95
  }
}
```

### 4. `kb_correct` - Add Correction

Add a correction to an existing entry.

**Parameters:**
- `entry_id` (string): ID of entry to correct
- `reason` (string): Why correction is needed
- `new_finding` (string): Updated information

**Example:**
```json
{
  "tool": "kb_correct",
  "params": {
    "entry_id": "PAT-50B1",
    "reason": "Workflow changed in v2.0",
    "new_finding": "Use .meta.experiments/ for prototyping"
  }
}
```

### 5. `kb_evolve` - Run Evolution Cycle

Run the evolution cycle to decay unused entries and archive low-confidence ones.

**Example:**
```json
{
  "tool": "kb_evolve"
}
```

**Response:**
```json
{
  "success": true,
  "decayed": 0,
  "archived": 0,
  "pending_corrections": 0,
  "message": "Evolution complete: 0 decayed, 0 archived"
}
```

### 6. `kb_stats` - Get Statistics

Get knowledge base statistics.

**Example:**
```json
{
  "tool": "kb_stats"
}
```

**Response:**
```json
{
  "success": true,
  "total_entries": 10,
  "by_type": {
    "pattern": {"count": 4, "avg_confidence": 0.95},
    "finding": {"count": 2, "avg_confidence": 0.93},
    "decision": {"count": 1, "avg_confidence": 1.0}
  },
  "by_category": {
    "workflow": 4,
    "tool": 2,
    "architecture": 1
  },
  "confidence_distribution": {
    "high": 5,
    "medium": 1,
    "low": 0
  },
  "pending_corrections": 0,
  "message": "KB Stats: 10 entries, 0 pending corrections"
}
```

## Usage with opencode

### As MCP Server

Start the server:
```bash
python .meta.development_tools/mcp/knowledge_base_server.py
```

Send requests:
```bash
echo '{"tool": "kb_stats"}' | python .meta.development_tools/mcp/knowledge_base_server.py
```

### As Python Module

```python
from rag_tool import rag_search, rag_ask, rag_add_entry

# Search
results = rag_search("TDD workflow", top_k=3)

# Ask
answer = rag_ask("Where should I write tests?")

# Add entry
result = rag_add_entry(
    entry_type="pattern",
    category="workflow",
    title="My Pattern",
    finding="What I found",
    solution="How to solve",
    confidence=0.95
)
```

## Integration Examples

### Example 1: Pre-task Research

Before starting a task, opencode can query the KB:

```python
# Ask where to work
result = rag_ask("Where should I implement this feature?")
print(result["augmented_prompt"])
# → Use this prompt to generate answer
```

### Example 2: Post-task Documentation

After completing a task, store the pattern:

```python
# Add new pattern
result = rag_add_entry(
    entry_type="pattern",
    category="workflow",
    title="Feature Implementation Workflow",
    finding="Features should be implemented in .meta.sandbox/",
    solution="1. Copy to sandbox 2. Modify 3. Test 4. Propose",
    confidence=0.95
)
```

### Example 3: Correction

When discovering better approaches:

```python
# Correct old pattern
result = rag_correct(
    entry_id="PAT-XXXX",
    reason="Workflow updated",
    new_finding="Use new approach"
)
```

## Error Handling

All tools return a standardized response format:

```json
{
  "success": true/false,
  "message": "Human-readable message",
  "error": "Error details if success=false",
  ... (other fields)
}
```

Always check `success` field first.

## Best Practices

1. **Use `kb_ask` for questions**: It provides RAG-augmented context
2. **Use `kb_search` for lookups**: Direct search without augmentation
3. **Add entries immediately**: After discovering patterns
4. **Use high confidence**: Only for verified knowledge (0.9+)
5. **Run `kb_evolve` weekly**: Maintain knowledge quality

## Troubleshooting

**No results from search?**
- Try broader query
- Check spelling
- Verify KB exists at `.meta.knowledge_base/knowledge.db`

**Database not found?**
- Ensure you're in project root
- Check path: `.meta.knowledge_base/knowledge.db`

**Low confidence results?**
- Results with confidence < 0.6 may not appear
- Lower confidence entries need verification

---

**Version**: 1.0.0
**Location**: `.meta.development_tools/mcp/`
