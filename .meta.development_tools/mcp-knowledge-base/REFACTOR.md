# Knowledge Base - Refactored Structure

## Overview

Refactored into modular structure with clear separation of concerns:

```
.meta.knowledge_base/          # Core knowledge base
├── core/                      # Core logic (stdlib only)
│   └── __init__.py           # Exports: init_db, hybrid_search, add_entry, etc.
├── cli/                       # CLI interface
│   └── __init__.py           # CLI commands
├── kb.py                      # CLI wrapper
├── __main__.py               # Module entry point
└── schemas/                   # DB schema

.meta.development_tools/mcp-knowledge-base/  # MCP tool
├── mcp/                       # MCP module
│   ├── __init__.py           # RAG functions
│   ├── server.py             # MCP server
│   └── __main__.py          # Server entry
└── README.md                 # Documentation
```

## Key Changes

### 1. Separated Core Logic
- **`core/__init__.py`**: All database operations, search, evolution
- No external dependencies (stdlib only)
- Easily testable

### 2. Clean CLI
- **`cli/__init__.py`**: CLI commands
- **`kb.py`**: Simple wrapper
- **`__main__.py`**: Module entry

### 3. MCP Module
- **`mcp/__init__.py`**: RAG functions
- Imports from `.meta.knowledge_base.core`
- Standalone, no external deps

## Usage

### CLI
```bash
python .meta.knowledge_base/kb.py stats
python .meta.knowledge_base/kb.py search "TDD"
python .meta.knowledge_base/kb.py add --type pattern ...
```

### MCP Module
```python
from .meta.development_tools.mcp_knowledge_base.mcp import rag_ask, rag_stats

result = rag_ask("Where write tests?")
print(result['augmented_prompt'])

stats = rag_stats()
print(f"Total: {stats['total_entries']}")
```

### Python Module
```python
from core import init_db, hybrid_search, add_entry

# Works from anywhere in project
conn = init_db()
results = hybrid_search(conn, "TDD")
```

## Benefits

1. **Modular**: Clear separation (core, cli, mcp)
2. **Testable**: Core logic isolated
3. **Maintainable**: Smaller, focused files
4. **Reusable**: Import from anywhere
5. **No deps**: Still stdlib only

## Files

### Core (11 files → 6 essential)
- `core/__init__.py` - Core logic
- `cli/__init__.py` - CLI
- `kb.py` - CLI wrapper
- `__main__.py` - Entry
- `knowledge.db` - Database
- `schemas/` - Schema
- `META.md`, `README.md`, `USAGE.md`, `QUICKSTART.md` - Docs
- `seed.py` - Seeding
- `pyproject.toml` - Metadata

### MCP (4 files)
- `mcp/__init__.py` - RAG functions
- `mcp/server.py` - Server
- `mcp/__main__.py` - Entry
- `README.md` - Docs
- `pyproject.toml` - Metadata

## Status

✅ Refactored and working
✅ All imports resolved
✅ No external dependencies
✅ Modular structure
✅ Easy to maintain
