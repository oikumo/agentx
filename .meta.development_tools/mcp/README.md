# MCP Knowledge Base Tools for opencode

## ✅ Complete

This MCP toolset allows **opencode** to directly use the Meta Project Harness Knowledge Base with RAG.

## Available Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| `kb_search` | Search KB entries | Find specific patterns |
| `kb_ask` | Ask questions with RAG | Get context-aware answers |
| `kb_add_entry` | Add new knowledge | Document discoveries |
| `kb_correct` | Correct entries | Auto-correct knowledge |
| `kb_evolve` | Run evolution | Maintenance |
| `kb_stats` | Get statistics | Monitor KB health |

## Usage Examples

### 1. Search for Patterns
```python
from rag_tool import rag_search

result = rag_search("TDD workflow", top_k=3)
# Returns: List of relevant entries
```

### 2. Ask Questions (RAG)
```python
from rag_tool import rag_ask

result = rag_ask("Where should I write tests?")
# Returns: Augmented prompt with retrieved context
print(result["augmented_prompt"])
```

### 3. Add New Knowledge
```python
from rag_tool import rag_add_entry

result = rag_add_entry(
    entry_type="pattern",
    category="workflow",
    title="Feature Implementation",
    finding="Work in .meta.sandbox/",
    solution="Copy → Modify → Test",
    confidence=0.95
)
```

### 4. Correct Existing Knowledge
```python
from rag_tool import rag_correct

result = rag_correct(
    entry_id="PAT-50B1",
    reason="Workflow updated",
    new_finding="Use new approach"
)
```

## Integration with opencode

When opencode needs to:

### Before a Task
```python
# Ask for guidance
result = rag_ask("Where should I implement this feature?")
# → Use augmented_prompt to answer
```

### After a Task
```python
# Store new pattern
result = rag_add_entry(
    entry_type="pattern",
    category="workflow",
    title="My Discovery",
    finding="What I found",
    solution="How to handle"
)
```

### When Correcting
```python
# Fix outdated knowledge
result = rag_correct(
    entry_id="PAT-XXX",
    reason="Found better way",
    new_finding="New approach"
)
```

## Files Created

```
.meta.development_tools/mcp/
├── rag_tool.py              # Main RAG tool
├── knowledge_base_server.py # MCP server wrapper
├── README.md                # This file
└── MCP_README.md            # Detailed documentation
```

## Testing

```bash
# Test all functions
python .meta.development_tools/mcp/rag_tool.py

# Test specific query
python -c "from rag_tool import rag_ask; print(rag_ask('tests'))"
```

## Response Format

All tools return standardized format:

```json
{
  "success": true,
  "message": "Human-readable message",
  ... (tool-specific fields)
}
```

---

**Status**: ✅ Complete and Ready
**Version**: 1.0.0
