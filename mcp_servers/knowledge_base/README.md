# Knowledge Base — MCP Server (v4)

Local MCP server that exposes a ChromaDB-backed knowledge base with **semantic code understanding** via knowledge graph technology. Used by `opencode` agents in this repo (see `opencode.jsonc`).

## 📐 Architecture

The KB v4 implementation consists of four main layers:

```
mcp_servers/knowledge_base/
├── server.py                 ← MCP tool surface (14 tools + 15 resources + 10 prompts)
├── pyproject.toml            ← hatchling wheel, uvx entry point
├── README.md                 ← this file
├── chroma_db/                ← ChromaDB persistence (auto-created)
│
├── kb/                       ← Core RAG library (v4)
│   ├── __init__.py           ← Public API exports
│   ├── api.py                ← search / ask / add_entry / stats / reset / populate_workspace
│   ├── store.py              ← KBStore class (ChromaDB client + collection management)
│   ├── search.py             ← Hybrid search (dense + sparse + RRF fusion + reranking)
│   ├── retrieval.py          ← DenseRetriever, FusionRetriever, hybrid_retrieve
│   ├── sparse_index.py       ← BM25 sparse retrieval implementation
│   ├── reranking.py          ← Cross-encoder neural reranking
│   ├── query_engine.py       ← Query preprocessing (rewrite, hyde, multi_query, decompose)
│   ├── synthesis.py          ← Answer synthesis (template + LLM modes)
│   ├── embedding.py          ← Embedding model registry and functions
│   ├── chunking.py           ← Text chunking for long entries
│   ├── ingest.py             ← Python AST + Markdown ingestion
│   ├── eval.py               ← Retrieval evaluation tools
│   ├── ids.py                ← Entry ID generation (make_entry_id)
│   ├── models.py             ← Dataclasses for API return types
│   └── logging.py            ← stderr-only logger ("kb")
│
├── analyzer/                 ← Semantic code analysis (v4)
│   ├── python_ast.py         ← Python AST traversal
│   ├── symbol_resolver.py    ← Symbol resolution and disambiguation
│   ├── relationships.py      ← Code relationship detection
│   ├── patterns.py           ← Code pattern recognition
│   ├── docstring.py          ← Docstring extraction and analysis
│   ├── base.py               ← Base analyzer classes
│   └── __init__.py
│
├── graph/                    ← Knowledge graph engine (v4)
│   ├── engine.py             ← Graph construction and traversal
│   ├── store.py              ← Graph persistence layer
│   ├── builder.py            ← Graph builder from code analysis
│   ├── queries.py            ← Graph query operations
│   ├── export.py             ← Graph export utilities
│   ├── sync.py               ← Graph-code synchronization
│   ├── models.py             ← Entity and relationship models
│   └── __init__.py
│
├── resources/                ← MCP resources (v4)
│   ├── registry.py           ← Resource registration
│   ├── project.py            ← Project structure resources
│   ├── arch.py               ← Architecture view resources
│   ├── flows.py              ← Data flow resources
│   ├── api.py                ← API endpoint resources
│   ├── code.py               ← Code snippet resources
│   ├── session.py            ← Session state resources
│   ├── quality.py            ← Code quality resources
│   ├── exporters.py          ← Resource export utilities
│   └── __init__.py
│
├── prompts/                  ← MCP prompts (v4)
│   ├── engine.py             ← Prompt template engine
│   ├── registry.py           ← Prompt registration
│   ├── analysis.py           ← Code analysis prompts
│   ├── modification.py       ← Code modification prompts
│   ├── navigation.py         ← Code navigation prompts
│   ├── onboarding.py         ← Project onboarding prompts
│   └── __init__.py
│
└── tests/                    ← pytest suite (unit + integration)
    ├── test_search.py        ← Search scoring tests
    ├── test_search_v3.py     ← Hybrid search pipeline tests
    ├── test_retrieval.py     ← Retrieval tests
    ├── test_query_engine.py  ← Query preprocessing tests
    ├── test_synthesis.py     ← Answer synthesis tests
    ├── test_server.py        ← MCP server tests
    └── ...                   ← (20+ test modules)
```

## 🛠️ MCP Tool Surface

### Core RAG Tools (7)

| Tool | Purpose | Default Mode |
|------|---------|--------------|
| `kb_search_tool` | Hybrid search (vector + lexical) over KB | `search_mode="hybrid"` |
| `kb_ask_tool` | Retrieve + synthesise markdown answer with citations | `search_mode="hybrid"` |
| `kb_add_tool` | Insert a single entry with auto-chunking | `enable_chunking=True` |
| `kb_stats_tool` | Counts by type/category + confidence statistics | — |
| `kb_reset_tool` | Drop & recreate the Chroma collection | — |
| `kb_populate_workspace_tool` | Walk workspace and ingest `.py` + `.md` files | `reset_first=True` |
| `kb_list_categories` | List valid entry types and categories | — |

### Knowledge Graph / Extended Tools (7)

> Names match `server.py` exactly. Via opencode they are namespaced as
> `knowledge_base_<tool>` (e.g. `knowledge_base_kb_graph_tool`).

| Tool | Purpose |
|------|---------|
| `kb_graph_tool` | Graph operations: `list`, `traverse`, `layers`, `entry_points` |
| `kb_impact_tool` | Analyze impact of changing an entity (risk-scored) |
| `kb_visualize_tool` | Render the graph as `mermaid` / `dot` / `ascii` |
| `kb_trace_flow_tool` | Find a path between two entities |
| `kb_code_location_tool` | Locate file/line for a symbol |
| `kb_find_pattern_tool` | Find design patterns in the graph |
| `kb_session_tool` | Session context: `get` / `set` / `clear` |

### MCP Resources (v4)

The server exposes 15 MCP resources for dynamic content:

- `project://` — Project structure and metadata
- `architecture://` — Architecture diagrams and descriptions
- `flows://` — Data flow and control flow visualizations
- `api://` — API endpoint documentation
- `code://` — Code snippets with context
- `session://` — Session state and history
- `quality://` — Code quality metrics and reports

### MCP Prompts (v4)

The server provides 10 MCP prompts for common tasks:

- `analyze:` — Code analysis prompts
- `modify:` — Code modification prompts
- `navigate:` — Code navigation prompts
- `onboard:` — Project onboarding prompts

## 🔍 Search Modes

The `kb_search_tool` and `kb_ask_tool` support multiple search strategies:

| Mode | Description | Use Case |
|------|-------------|----------|
| `hybrid` | Dense + sparse retrieval with RRF fusion (default) | General purpose, best overall |
| `dense` | Dense vector search only | Semantic similarity queries |
| `sparse` | BM25 lexical search only | Exact keyword matching |

### Query Preprocessing Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `direct` | No transformation (passthrough) | Simple, direct queries |
| `rewrite` | LLM-based query rewriting | Clarify ambiguous queries |
| `hyde` | Hypothetical Document Embedding | Generate synthetic answer for better retrieval |
| `multi_query` | Generate N query variants | Broader recall |
| `decompose` | Break complex questions into sub-questions | Multi-part questions |

### Synthesis Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `template` | Template-based markdown synthesis (default) | Fast, deterministic |
| `llm` | LLM-based natural language generation | Natural, conversational answers |

## 📊 Scoring Formula (Hybrid Search)

The v4 hybrid search pipeline uses a multi-stage ranking approach:

### Stage 1: Parallel Retrieval
1. **Dense retrieval** — ChromaDB ANN search with configurable embedding model (default: `bge-small-en`)
2. **Sparse retrieval** — BM25 lexical search (optional, requires `bm25s`)

### Stage 2: Reciprocal Rank Fusion

Fusion formula (RRF):

```
score(doc) = Σ 1 / (k + rank_i(doc))
```

Where:
- `rank_i(doc)` is the rank of the document in retriever i's results
- `k` is a constant (default: 60) that balances importance of top ranks

### Stage 3: Neural Reranking (Optional)

If enabled, a cross-encoder model (default: `ms-marco-MiniLM-L6-v2`) reranks the top candidates for improved precision.

### Final Scoring

Results are sorted by fused score, with optional reranker scores applied. The final output includes:
- `combined_score`: Fused RRF score
- `source`: Which retriever(s) contributed (`"dense"`, `"sparse"`, `"fusion"`, `"reranker"`)

## 📝 Entry Structure

### Entry Types

| Type | Prefix | Purpose |
|------|--------|---------|
| `pattern` | `PAT` | Reusable patterns or best practices |
| `finding` | `FIND` | Discoveries or insights |
| `decision` | `DEC` | Architectural or design decisions |
| `correction` | `COR` | Corrections to existing entries |

### Entry Categories

| Category | Purpose |
|----------|---------|
| `code` | Code-related knowledge |
| `class` | Class-level knowledge |
| `method` | Method-level knowledge |
| `function` | Function-level knowledge |
| `workflow` | Workflows and processes |
| `documentation` | Documentation guidelines |
| `architecture` | Architectural patterns |

### Entry-ID Scheme

`make_entry_id(entry_type, category, title)` returns:

```
{PREFIX}-{4-uppercase-hex}
```

Example: `PAT-A1B2`, `FIND-C3D4`, `DEC-E5F6`

The 4-char suffix is the first 4 chars of `md5(entry_type + category + timestamp + random)`, uppercased.

### Entry Fields

Each entry contains:
- `entry_id`: Unique identifier (e.g., `PAT-A1B2`)
- `type`: Entry type (`pattern`, `finding`, `decision`, `correction`)
- `category`: Category (see above)
- `title`: Short descriptive title
- `finding`: Main finding or insight
- `solution`: Solution or recommendation
- `context`: Additional context (optional)
- `example`: Example code or text (optional)
- `confidence`: Confidence score 0.0-1.0
- `created_at`: ISO timestamp
- `is_chunked`: Whether entry was auto-chunked
- `chunk_count`: Number of chunks (if chunked)

## 🗂️ Directory Exclusions

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

## 💾 Persistence

`KBStore()` defaults `persist_directory` to `<this-package>/chroma_db/`, i.e.:

```
mcp_servers/knowledge_base/chroma_db/
```

The directory is created on first use. Tests pass an explicit `persist_directory=tmp_path / "chroma_db"` to stay isolated.

### Embedding Models

The KB supports multiple embedding models via the `embedding_model` parameter:

| Model | Dimensions | Speed | Quality | Use Case |
|-------|-----------|-------|---------|----------|
| `bge-small-en` | 384 | Fast | Good | Default, general purpose |
| `bge-base-en` | 768 | Medium | Better | Higher quality retrieval |
| `bge-large-en` | 1024 | Slow | Best | Maximum accuracy |
| `miniLM-L6-v2` | 384 | Very Fast | OK | Low-latency scenarios |

Models are managed by the embedding registry in `kb/embedding.py`.

## 🚀 Running

### Via opencode (recommended)

Add to `opencode.jsonc`:

```jsonc
{
  "mcp_servers": {
    "knowledge_base": {
      "type": "local",
      "enabled": true,
      "command": ["uvx", "--from", "./mcp_servers/knowledge_base", "knowledge_base"]
    }
  }
}
```

### Standalone (development)

```bash
cd mcp_servers/knowledge_base
uv run --with chromadb --with 'mcp[cli]==1.27.1' --with fastmcp==3.3.1 python server.py
```

### With custom timeout

For long-running operations (e.g., workspace population):

```bash
KB_MCP_TIMEOUT=1800 uv run --from ./mcp_servers/knowledge_base knowledge_base
```

Default timeout: 1800s (30 minutes)

## 🧪 Tests

### Run all tests

```bash
cd mcp_servers/knowledge_base
uv run pytest tests/ -v
```

### Run specific test suites

```bash
# Core RAG tests
uv run pytest tests/test_search.py tests/test_search_v3.py -v

# Retrieval tests
uv run pytest tests/test_retrieval.py tests/test_query_engine.py -v

# Synthesis tests
uv run pytest tests/test_synthesis.py -v

# Knowledge graph tests
uv run pytest tests/test_graph_*.py -v

# Integration tests
uv run pytest tests/test_server_v4_integration.py -v
```

### Coverage

```bash
uv run pytest tests/ --cov=kb --cov-report=html
```

Current coverage: **86% line coverage** of `kb/` module.

### Test Statistics

- **Total tests**: 443 passing
- **Test modules**: 20+
- **Coverage**: 86% (kb/ module)

## 📦 Dependencies

### Core Dependencies

- `chromadb` — Vector database
- `fastmcp` — MCP server framework
- `mcp` — MCP protocol implementation

### Optional Dependencies

- `bm25s` — Sparse retrieval (BM25)
- `sentence-transformers` — Cross-encoder reranking
- `onnxruntime` — ONNX embedding inference (faster)

### Development Dependencies

- `pytest` — Testing framework
- `pytest-cov` — Coverage reporting
- `anyio` — Async I/O support

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KB_MCP_TIMEOUT` | `1800` | Timeout for long-running operations (seconds) |
| `KB_PERSIST_DIR` | `./chroma_db` | ChromaDB persistence directory |
| `KB_EMBEDDING_MODEL` | `bge-small-en` | Default embedding model |
| `KB_RERANKER_MODEL` | `ms-marco-MiniLM-L6-v2` | Default reranker model |

### Tool Parameters

Most tools accept these common parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search_mode` | `str` | `"hybrid"` | Search strategy |
| `embedding_model` | `str` | `"bge-small-en"` | Embedding model for dense retrieval |
| `rerank` | `bool` | `True` | Enable cross-encoder reranking |
| `reranker_model` | `str` | `"ms-marco-MiniLM-L6-v2"` | Reranker model |
| `query_mode` | `str` | `"direct"` | Query preprocessing mode |
| `synthesis_mode` | `str` | `"template"` | Answer synthesis mode |

## 📚 API Reference

### Core Functions

```python
from kb import (
    search,           # Search the KB
    ask,              # Ask a question
    add_entry,        # Add an entry
    stats,            # Get statistics
    reset,            # Reset the KB
    populate_workspace,  # Ingest workspace files
)
```

### Retrieval Components

```python
from kb import (
    DenseRetriever,      # Dense vector retrieval
    FusionRetriever,     # RRF fusion
    SparseRetriever,     # BM25 sparse retrieval
    hybrid_retrieve,     # Combined hybrid retrieval
    QueryEngine,         # Query preprocessing
    CrossEncoderReranker, # Neural reranking
)
```

### Evaluation

```python
from kb import (
    RetrievalEvaluator,  # Retrieval evaluation
    quick_eval,          # Quick evaluation helper
    compare_configs,     # Compare retrieval configurations
)
```

## 🎯 Usage Examples

### Search with hybrid mode

```python
from kb import search

results = search(
    query="How to implement RAG?",
    top_k=5,
    search_mode="hybrid",
    rerank=True,
)
```

### Ask with LLM synthesis

```python
from kb import ask

answer = ask(
    question="What is the KB architecture?",
    top_k=3,
    search_mode="hybrid",
    query_mode="multi_query",
    synthesis_mode="llm",
)
```

### Add entry with auto-chunking

```python
from kb import add_entry

result = add_entry(
    entry_type="pattern",
    category="architecture",
    title="MVC++ Pattern",
    finding="Separation of concerns...",
    solution="Use three layers...",
    confidence=0.95,
    enable_chunking=True,
)
```

### Populate workspace

```python
from kb import populate_workspace

result = populate_workspace(
    workspace_root="/path/to/project",
    include_python=True,
    include_markdown=True,
    reset_first=True,
)
```

## 📈 Performance

### Typical Latencies

| Operation | Latency | Notes |
|-----------|---------|-------|
| Dense search (top_k=5) | 50-100ms | Depends on embedding model |
| Hybrid search | 100-200ms | Includes RRF fusion |
| With reranking | 200-500ms | Cross-encoder adds latency |
| Query preprocessing | 10-50ms | Direct mode is instant |
| LLM synthesis | 500-2000ms | Depends on LLM and context |

### Scaling

- **Entries**: Tested up to 10,000+ entries
- **Query throughput**: ~10-20 queries/second (hybrid mode)
- **Index size**: ~100MB per 1,000 entries (varies by embedding model)

## 🐛 Troubleshooting

### Common Issues

**Issue**: "No results found"
- **Solution**: Try `search_mode="dense"` or adjust `embedding_model`

**Issue**: "Reranker not available"
- **Solution**: Install `sentence-transformers` or set `rerank=False`

**Issue**: "Timeout during population"
- **Solution**: Increase `KB_MCP_TIMEOUT` environment variable

**Issue**: "Out of memory"
- **Solution**: Reduce `top_k` or use smaller embedding model

### Debug Mode

Enable verbose logging:

```bash
KB_LOG_LEVEL=DEBUG uv run ...
```

## 📝 Version History

### v4.0.0 (Current)
- ✅ Knowledge graph integration
- ✅ Semantic code analysis
- ✅ MCP resources and prompts
- ✅ Hybrid search (dense + sparse + RRF)
- ✅ Query preprocessing (5 modes)
- ✅ LLM synthesis
- ✅ Auto-chunking
- ✅ Progress callbacks

### v3.x (Legacy)
- Hybrid search pipeline
- Query engine
- Reranking support

### v2.x (Legacy)
- Basic vector search
- Template synthesis

### v1.x (Legacy)
- Initial implementation

## 📄 License

Same license as the parent project.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `uv run pytest tests/ -v`
4. Submit a pull request

## 📞 Support

For issues and questions, please refer to the main project documentation or open an issue in the repository.