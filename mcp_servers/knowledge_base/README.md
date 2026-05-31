# Knowledge Base — MCP Server

Local MCP server that exposes a ChromaDB-backed knowledge base via seven
tools. Used by `opencode` agents in this repo (see `opencode.jsonc`).

## Layout

```
mcp_servers/knowledge_base/
├── server.py            ← FastMCP tool surface (formatting + validation only)
├── pyproject.toml       ← hatchling wheel, uvx entry point
├── README.md            ← this file
├── chroma_db/           ← Chroma persistence (auto-created)
├── kb/                  ← the library
│   ├── __init__.py      ← public API
│   ├── api.py           ← search / ask / add_entry / stats / reset / populate_workspace
│   ├── store.py         ← KBStore class (Chroma client + collection)
│   ├── search.py        ← hybrid scoring (tokenize, keyword, semantic boost)
│   ├── synthesis.py     ← AskResult builder used by kb_ask_tool
│   ├── ingest.py        ← Python AST + Markdown ingestion
│   ├── ids.py           ← make_entry_id()
│   ├── models.py        ← dataclasses returned by api.* functions
│   └── logging.py       ← stderr-only logger ("kb")
└── tests/               ← pytest suite (unit + MCP round-trip)
```

## MCP tool surface

| Tool                         | Purpose                                       |
| ---------------------------- | --------------------------------------------- |
| `kb_search_tool`             | Hybrid search (vector + lexical) over KB      |
| `kb_ask_tool`                | Retrieve + synthesise a markdown answer       |
| `kb_add_tool`                | Insert a single entry                         |
| `kb_stats_tool`              | Counts by type / category + confidence buckets|
| `kb_reset_tool`              | Drop & recreate the Chroma collection         |
| `kb_populate_workspace_tool` | Walk a workspace and ingest `.py` + `.md`     |
| `kb_list_categories`         | List valid entry types and categories         |

Names and signatures are stable across the v0.2.0 refactor; only the
`kb_ask_tool` text output changed (now a real synthesised answer, no longer
a prompt skeleton).

## Directory Exclusions

The `kb_populate_workspace_tool` automatically excludes sensitive and unnecessary directories:

**Default Exclusions:**
- Build/artifact dirs: `__pycache__`, `build`, `dist`, `.tox`, `.eggs`, `site-packages`
- Virtual environments: `.venv`, `venv`
- Version control: `.git`, `node_modules`
- Cache dirs: `.pytest_cache`, `.mypy_cache`, `.ruff_cache`
- KB data: `chroma_db`

**Sensitive Files Protection:**
- `.env` directories and files (exact match)
- `.env.*` patterns (e.g., `.env.local`, `.env.production`, `.env.test`)

Additional directories can be excluded via the `exclude_dirs` parameter.

## Entry-ID scheme

`make_entry_id(entry_type, category, title)` returns:

```
{PREFIX}-{4-uppercase-hex}
```

Prefix map:

| entry_type   | prefix |
| ------------ | ------ |
| `pattern`    | `PAT`  |
| `finding`    | `FIND` |
| `decision`   | `DEC`  |
| `correction` | `COR`  |
| (other)      | `KB`   |

The 4-char suffix is the first 4 chars of `md5(entry_type + category +
timestamp + random)`, uppercased. Existing entries from earlier versions
remain queryable since the on-disk ChromaDB metadata schema is unchanged.

## Scoring formula (hybrid search)

For each candidate retrieved by `collection.query(...)`:

```
similarity     = 1 / (1 + chroma_distance)
keyword        = keyword_score(document_text, query)        # [0, 1]
sem_boost      = semantic_boost(entry, query)               # ~[0.8, 1.2]
confidence     = entry.confidence (from metadata)           # [0, 1]
recency        = 1 / (1 + 0.01 * days_since_created)        # ~[0, 1]
title_bonus    = 2.0 if query is substring of title
                 else 1.0 if >= 2 query tokens in title
                 else 0.5 if any query token in title
                 else 0.0

combined = 0.30*similarity + 0.20*keyword + 0.15*sem_boost
         + 0.15*confidence + 0.10*recency + 0.10*title_bonus
```

Results are sorted by descending `combined`.

## Persistence

`KBStore()` defaults `persist_directory` to
`<this-package>/chroma_db/`, i.e.
`mcp_servers/knowledge_base/chroma_db/`. The directory is created on first
use. Tests pass an explicit `persist_directory=tmp_path / "chroma_db"` to
stay isolated.

## Running

Via `opencode` (see `opencode.jsonc`):

```jsonc
"knowledge_base": {
  "type": "local",
  "enabled": true,
  "command": ["uvx", "--from", "./mcp_servers/knowledge_base", "knowledge_base"]
}
```

Standalone, for development:

```sh
cd mcp_servers/knowledge_base
uv run --with chromadb --with 'mcp[cli]==1.27.1' --with fastmcp==3.3.1 python server.py
```

## Tests

```sh
cd mcp_servers/knowledge_base
uv run --with chromadb --with pytest --with 'mcp[cli]==1.27.1' --with fastmcp==3.3.1 pytest tests/ -v
```

41 tests, 86 % line coverage of `kb/` at the time of the v0.2.0 refactor.

