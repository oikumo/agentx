# UV Setup for MCP Knowledge Base

## Configuration

The MCP tool is configured to use `uv` in `opencode.jsonc`:

```json
{
  "mcp": {
    "knowledge-base": {
      "type": "local",
      "command": ["uv", "run", ".meta.development_tools/mcp-knowledge-base/mcp/server.py"],
      "enabled": true
    }
  }
}
```

## Usage

### Run with uv

```bash
# Run server directly
uv run .meta.development_tools/mcp-knowledge-base/mcp/server.py

# Or from the directory
cd .meta.development_tools/mcp-knowledge-base
uv run mcp/server.py
```

### Test with uv

```bash
# Test stats
echo '{"tool": "kb_stats"}' | uv run .meta.development_tools/mcp-knowledge-base/mcp/server.py

# Test ask
echo '{"tool": "kb_ask", "params": {"question": "Where write tests?"}}' | uv run .meta.development_tools/mcp-knowledge-base/mcp/server.py
```

## Dependencies

The `pyproject.toml` specifies:

```toml
[project]
name = "agent-x-mcp-knowledge-base"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = []  # No external dependencies - stdlib only
```

**Benefits of using uv:**
- ✅ Fast dependency resolution
- ✅ Consistent Python environment
- ✅ No external dependencies needed
- ✅ Isolated from system Python
- ✅ Reproducible builds

## Files

- `pyproject.toml` - Project metadata for uv
- `mcp/server.py` - MCP server
- `mcp/__init__.py` - RAG functions
- `mcp/__main__.py` - Entry point for `uv run`
- `opencode.jsonc` - opencode configuration

## Status

✅ Configured for uv
✅ No external dependencies
✅ Works with `uv run`
✅ Activated in opencode.jsonc
