# Meta Harness KB - ChromaDB RAG

**ChromaDB-powered RAG** for project knowledge. Vector search, query expansion, multi-hop retrieval, answer synthesis.

## ⚠️ IMPORTANT: Dependency Management

**⛔ NEVER use `pip` to install dependencies.** This will break the isolated environment.

**✅ ONLY use `uv` for all dependency management:**

- All dependencies are managed via `pyproject.toml`
- Use `uv add <package>` to install dependencies
- The virtual environment is managed automatically by `uv`
- Always run commands using the venv Python: `.venv/bin/python kb ...`

**Why not `pip`?** Using `pip` directly will install packages to the wrong environment and cause import errors.

## Quick Start

```bash
cd .meta/tools/meta-harness-knowledge-base

# Install dependencies (REQUIRED - first time only)
uv sync

# Run commands (use the venv Python)
.venv/bin/python kb search "query"
.venv/bin/python kb ask "question?"
```

## CLI Commands

**Note:** Always use `.venv/bin/python` to run KB commands.

| Command | Description | Example |
|---------|-------------|---------|
| `search` | Vector search with query expansion | `.venv/bin/python kb search "TDD" -k 5` |
| `ask` | Synthesized answer with citations | `.venv/bin/python kb ask "Where write tests?"` |
| `stats` | KB statistics | `.venv/bin/python kb stats` |
| `add` | Add entry | `.venv/bin/python kb add pattern code "Title" "Finding" "Solution"` |
| `chat` | Interactive mode | `.venv/bin/python kb chat` |

## Python API

**Note:** Run Python code using `.venv/bin/python` or ensure you're in the virtual environment.

```python
from src.rag_tool import rag_search, rag_ask
from src.advanced_rag import ChromaDBAdvancedRAG

# Search
result = rag_search("query", top_k=5)

# Ask
result = rag_ask("question?", top_k=3)

# Advanced
rag = ChromaDBAdvancedRAG()
result = rag.advanced_search("query", top_k=5, use_multi_hop=True)
```

## Architecture

**Components:**
- `rag_tool.py` - ChromaDB search, ask, add (rag_search, rag_ask, rag_add_entry)
- `rag_ingest.py` - Python/Markdown ingestion
- `advanced_rag.py` - Query expansion, multi-hop, clustering, synthesis
- `knowledge_base.py` - High-level API (kb_search, kb_ask, kb_stats)
- `kb` - CLI tool

**Scoring:** 30% vector + 20% keyword + 15% semantic + 15% confidence + 10% recency + 10% title match

**Storage:** `mcp_servers/knowledge_base/chroma_db/`

## Entry Types & Categories

**Types:** pattern, finding, decision, correction  
**Categories:** code, class, method, function, workflow, documentation, architecture

## Performance

- Search: ~0.4s
- Multi-hop: ~0.8s  
- Storage: ~5MB/1000 entries

## Troubleshooting

- **No results:** Simplify query, check spelling
- **Low confidence:** Verify sources, add documentation
- **Import error / ModuleNotFoundError:** Run `uv sync` to install dependencies
- **Command not found:** Ensure you're using `.venv/bin/python kb` not just `python kb`
- **Used `pip install`?** This will break the environment. Run `uv sync` to fix it.

**⛔ NEVER run `pip install` in this directory. Always use `uv add` or `uv sync`.**

---

## Development

**Adding new dependencies:**
```bash
uv add <package-name>
```

**Running tests:**
```bash
uv run pytest
```

**Syncing dependencies:**
```bash
uv sync
```

---
**v3.0.0** \| ChromaDB backend \| 2026-05-21
