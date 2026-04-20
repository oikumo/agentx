# MCP Knowledge Base Tools for opencode

## ✅ Complete

This MCP toolset allows **opencode** to directly use the Meta Project Harness Knowledge Base with RAG (Retrieval-Augmented Generation).

## Quick Start

```bash
# Test all tools
python .meta.development_tools/mcp/rag_tool.py

# Test via MCP server
echo '{"tool": "kb_stats"}' | python3 .meta.development_tools/mcp/knowledge_base_server.py
```

## Available Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| `kb_search` | Search KB entries | Find specific patterns |
| `kb_ask` | Ask questions with RAG | Get context-aware answers |
| `kb_add_entry` | Add new knowledge | Document discoveries |
| `kb_correct` | Correct entries | Auto-correct knowledge |
| `kb_evolve` | Run evolution | Maintenance |
| `kb_stats` | Get statistics | Monitor KB health |

## Usage Methods

### Method 1: Via MCP Server (Recommended for opencode)

```bash
# Search
echo '{"tool": "kb_search", "params": {"query": "TDD", "top_k": 3}}' | \
  python3 .meta.development_tools/mcp/knowledge_base_server.py

# Ask question
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

### Method 2: As Python Module

```python
from rag_tool import rag_search, rag_ask, rag_add_entry, rag_correct, rag_evolve, rag_stats

# Search
result = rag_search("TDD workflow", top_k=3)
print(result)

# Ask (RAG)
result = rag_ask("Where should I write tests?")
print(result["augmented_prompt"])

# Add entry
result = rag_add_entry(
    entry_type="pattern",
    category="workflow",
    title="Feature Implementation",
    finding="Work in .meta.sandbox/",
    solution="Copy → Modify → Test",
    confidence=0.95
)

# Correct
result = rag_correct(
    entry_id="PAT-50B1",
    reason="Workflow updated",
    new_finding="Use new approach"
)

# Stats
result = rag_stats()
print(result["message"])
```

## Integration with opencode

### As MCP Tool (stdin/stdout)

The server reads JSON from stdin and writes JSON to stdout:

```python
import subprocess
import json

def kb_search(query, top_k=5):
    """Search knowledge base via MCP."""
    proc = subprocess.Popen(
        ["python3", ".meta.development_tools/mcp/knowledge_base_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    request = json.dumps({"tool": "kb_search", "params": {"query": query, "top_k": top_k}})
    stdout, _ = proc.communicate(request + "\n")
    # Parse last JSON line
    for line in reversed(stdout.strip().split("\n")):
        try:
            return json.loads(line)
        except:
            continue
    return {"success": False, "error": "No response"}
```

### Integration Patterns

#### Before a Task (Research)
```python
# Ask for guidance
result = rag_ask("Where should I implement this feature?")
# Use the augmented_prompt to generate answer
print(result["augmented_prompt"])
```

#### After a Task (Documentation)
```python
# Store new pattern
result = rag_add_entry(
    entry_type="pattern",
    category="workflow",
    title="My Discovery",
    finding="What I found",
    solution="How to handle it"
)
```

#### When Correcting (Evolution)
```python
# Fix outdated knowledge
result = rag_correct(
    entry_id="PAT-XXX",
    reason="Found better way",
    new_finding="New approach"
)
```

## Examples

### Example 1: Search for TDD patterns
```bash
$ echo '{"tool": "kb_search", "params": {"query": "TDD", "top_k": 2}}' | \
  python3 .meta.development_tools/mcp/knowledge_base_server.py

# Response:
{
  "success": true,
  "query": "TDD",
  "count": 1,
  "results": [{
    "id": "PAT-50B1",
    "type": "pattern",
    "category": "workflow",
    "title": "TDD in .meta.tests_sandbox",
    "confidence": 0.98,
    "finding": "Tests must be written before code...",
    "solution": "1. Write failing test..."
  }],
  "message": "Found 1 relevant entries"
}
```

### Example 2: Ask a question
```bash
$ echo '{"tool": "kb_ask", "params": {"question": "Where to write tests?"}}' | \
  python3 .meta.development_tools/mcp/knowledge_base_server.py

# Response includes augmented_prompt with retrieved context
```

### Example 3: Add new knowledge
```bash
$ echo '{"tool": "kb_add_entry", "params": {
  "type": "pattern",
  "category": "workflow",
  "title": "Use uv for packages",
  "finding": "uv is faster than pip",
  "solution": "Always use uv add package"
}}' | python3 .meta.development_tools/mcp/knowledge_base_server.py

# Response: {"success": true, "entry_id": "PAT-XXXX", ...}
```

## Files

```
.meta.development_tools/mcp/
├── rag_tool.py                   # Main RAG tool (Python module)
├── knowledge_base_server.py      # MCP server wrapper
├── README.md                     # This file
├── MCP_README.md                 # Detailed documentation
└── README.md                     # You are here
```

## Response Format

All tools return standardized JSON:

```json
{
  "success": true,
  "message": "Human-readable message",
  ... (tool-specific fields)
}
```

Always check `success` field first.

## Troubleshooting

**No results from search?**
- Try broader query
- Check spelling
- Verify KB exists: `.meta.knowledge_base/knowledge.db`

**Database not found?**
- Ensure you're in project root
- Check path: `.meta.knowledge_base/knowledge.db`

**Low confidence results?**
- Results with confidence < 0.6 may not appear
- Lower confidence entries need verification

## Testing

```bash
# Test all functions
python .meta.development_tools/mcp/rag_tool.py

# Test specific tool
python -c "from rag_tool import rag_ask; print(rag_ask('tests'))"

# Test via MCP
echo '{"tool": "kb_stats"}' | python3 .meta.development_tools/mcp/knowledge_base_server.py
```

---

**Status**: ✅ Complete and Ready  
**Version**: 1.0.0  
**Location**: `.meta.development_tools/mcp/`
