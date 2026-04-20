# MCP Knowledge Base Tool for opencode

## Overview

This MCP (Model Context Protocol) tool allows **opencode** to interact with the Meta Project Harness Knowledge Base using RAG (Retrieval-Augmented Generation).

**Location**: `.meta.development_tools/mcp-knowledge-base/`

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
    "reason": "Workflow updated in v2.0",
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

### 6. `kb_stats` - Get Statistics

Get knowledge base statistics.

**Example:**
```json
{
  "tool": "kb_stats"
}
```

## Usage

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

### As MCP Server

Start the server:
```bash
cd .meta.development_tools/mcp-knowledge-base
python server.py
```

Send requests via stdin:
```bash
echo '{"tool": "kb_stats"}' | python server.py
```

## Integration Examples

### Example 1: Pre-task Research

Before starting a task, opencode can query the KB:

```python
from rag_tool import rag_ask

# Ask where to work
result = rag_ask("Where should I implement this feature?")
print(result["augmented_prompt"])
# → Use this prompt to generate answer
```

### Example 2: Post-task Documentation

After completing a task, store the pattern:

```python
from rag_tool import rag_add_entry

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
from rag_tool import rag_correct

result = rag_correct(
    entry_id="PAT-XXXX",
    reason="Workflow updated",
    new_finding="Use new approach"
)
```

## Response Format

All tools return a standardized response format:

```json
{
  "success": true,
  "message": "Human-readable message",
  ... (tool-specific fields)
}
```

Always check the `success` field first.

## Testing

```bash
# Test all functions
python rag_tool.py

# Test specific query
python -c "from rag_tool import rag_ask; print(rag_ask('tests'))"
```

## Files

```
mcp-knowledge-base/
├── rag_tool.py         # Main RAG tool
├── server.py           # MCP server wrapper
├── README.md           # This file
└── pyproject.toml      # Optional dependencies
```

## Best Practices

1. **Use `kb_ask` for questions**: It provides RAG-augmented context
2. **Use `kb_search` for lookups**: Direct search without augmentation
3. **Add entries immediately**: After discovering patterns
4. **Use high confidence**: Only for verified knowledge (0.9+)
5. **Run `kb_evolve` weekly**: Maintain knowledge quality

---

**Version**: 1.0.0
**Location**: `.meta.development_tools/mcp-knowledge-base/`
