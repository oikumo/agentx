# opencode MCP Setup

## Configuration

The MCP knowledge base tool is activated in `opencode.jsonc`:

```json
{
  "mcp": {
    "knowledge-base": {
      "type": "local",
      "command": ["python3", ".meta.development_tools/mcp-knowledge-base/mcp/server.py"],
      "enabled": true
    }
  }
}
```

## Available Tools for opencode

When opencode is running, it can use these tools:

1. **`kb_search`** - Search knowledge base
2. **`kb_ask`** - Ask questions with RAG
3. **`kb_add_entry`** - Add new knowledge
4. **`kb_correct`** - Correct entries
5. **`kb_evolve`** - Run evolution cycle
6. **`kb_stats`** - Get statistics

## Usage Example

When opencode asks a question, it will automatically use the knowledge base:

```
opencode: "Where should I write tests?"
→ Uses kb_ask tool
→ Retrieves relevant patterns from KB
→ Generates answer based on retrieved knowledge
```

## Testing

Test the MCP server manually:

```bash
cd .meta.development_tools/mcp-knowledge-base
echo '{"tool": "kb_stats"}' | python3 mcp/server.py
```

Expected output:
```json
{
  "result": {
    "success": true,
    "total_entries": 6,
    ...
  }
}
```

## Files

- `mcp/__init__.py` - RAG functions
- `mcp/server.py` - MCP server
- `mcp/__main__.py` - Entry point
- `opencode.jsonc` - Configuration

## Status

✅ Activated in opencode.jsonc
✅ Server ready
✅ Tools available
