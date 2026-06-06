# System Rules

> **⚠️ MANDATORY FIRST STEP:** On the **first prompt**, read `WORK.md` and display it.
>
> **⚠️ MANDATORY SECOND STEP:** Before ANY task, query the KB using the MCP `knowledge_base` tools.
>
> **⚠️ MANDATORY THIRD STEP:** Read `AGENTS.md` in full (you're reading it now).
>
> **⚠️ MANDATORY FOURTH STEP (ARCHITECTURE):** Before modifying any source code, read `.meta/doc/omt_agent_guide.md` — the **OMT++ Agent Guide**. All code must follow its rules.

---

## Core Directives

**NEVER:**
1. Commit/push code
2. Read nor Modify `.env` or secrets
3. Add dependencies (approval required)
4. Modify `tests/` dir (use canary tests, requires approval)
5. Change `README.md` (unless explicitly asked)

**ALWAYS:**
6. Check `git log` before changes
7. Follow META rules (read `.meta/META.md`)
8. Query KB first using MCP tools, cite sources in every response
9. **Follow OMT++ methodology** (`.meta/doc/omt_agent_guide.md`) — all code must conform to MVC++, Abstract Partner, and phase rules

---

## Quick Start

1. **Read OMT++ guide** (first time only) → `.meta/doc/omt_agent_guide.md`
2. **Query KB** → Use MCP tool `knowledge_base_ask_tool` or `knowledge_base_search_tool`
3. **Check git** → `git log --oneline -5`
4. **Work in correct directory** (see Decision Tree)
5. **Identify OMT++ phase** — Analysis? Design? Programming? Testing? State it explicitly.


---

## Decision Tree

```
Need to...
├─ Understand something?  → Query KB via MCP tools first
├─ Modify code?           → Read OMT++ guide → follow MVC++ / phases
├─ Prototype/test idea?   → `.meta/experiments/`
├─ Write tests?           → `tests/unit/` (with approval) or `.meta/experiments/`
├─ Plan a project?        → `.meta/projects/`
├─ Store data/KB?         → `.meta/data/`
└─ Document something?    → `.meta/doc/`
```

> Each `.meta/<subdir>/` has its own `META.md` describing scope and rules.
> Read it before working in that directory.

---

## Workflow (OMT++ 5+5 Steps)

Every task follows the OMT++ Phase Model. State which phase you are in.

### Pre-Step: Feasibility
```
0. FEASIBILITY — Before any phase, answer:
   • Do I understand the requirements?
   • Is the scope clear?
   • Do I know the files affected?
   • What is the risk level?
   • Which OMT++ phase am I entering?
```

### Main Steps (OMT++ Integrated)

| # | Step | OMT++ Phase | Action |
|---|---|---|---|
| 1 | **UNDERSTAND** | Analysis | Query KB + git log. Write use case if new feature. Identify domain concepts. |
| 2 | **DESIGN** | Design | Define interfaces (Abstract Partner ABCs), class structures, operation specs. |
| 3 | **EXECUTE** | Programming | Implement following MVC++ layers: Model first, then View (with ABC), then Controller. |
| 4 | **VALIDATE** | Testing | Unit → Integration → System tests. Mock interfaces, not concretions. |
| 5 | **REPORT** | Close | Summarize, log changes, update KB if new architecture patterns emerged. |

### Artifact Rules

| Task Type | Required Artifacts |
|---|---|
| Bug fix (1 file) | Tests |
| Minor feature (2-3 files) | Operation spec + tests |
| New screen | Use case, operation list, dialog diagram, design class diagram, operation specs, unit tests, integration tests |
| New project | Full methodology — all analysis, design, and testing artifacts |

> See `.meta/doc/omt_agent_guide.md§12` for the full Essential vs Optional matrix.

---

## Knowledge Base Access

The Knowledge Base is **exclusively** accessed through the MCP server:

### Server Configuration
- **Server**: `mcp_servers/knowledge_base/server.py`
- **Configuration**: `opencode.jsonc` (MCP section)
- **Documentation**: `mcp_servers/knowledge_base/README.md` (572 lines, comprehensive)
- **Project Status**: `.meta/projects/kb-mcp-v4/STATUS.md`

### Core RAG Tools (7)

| Tool | Purpose | Default Parameters |
|------|---------|-------------------|
| `knowledge_base_kb_search_tool` | Hybrid search (vector + lexical) over KB | `search_mode="hybrid"`, `top_k=5` |
| `knowledge_base_kb_ask_tool` | Retrieve + synthesise markdown answer with citations | `search_mode="hybrid"`, `top_k=3`, `synthesis_mode="template"` |
| `knowledge_base_kb_add_tool` | Insert a single entry with auto-chunking | `enable_chunking=True`, `confidence=0.5` |
| `knowledge_base_kb_stats_tool` | Counts by type/category + confidence statistics | — |
| `knowledge_base_kb_reset_tool` | Drop & recreate the Chroma collection | — |
| `knowledge_base_kb_populate_workspace_tool` | Walk workspace and ingest `.py` + `.md` files | `reset_first=True`, `include_python=True` |
| `knowledge_base_kb_list_categories` | List valid entry types and categories | — |

### Knowledge Graph / Extended Tools (v4 - 7 tools)

> Names match `server.py`. Via opencode they are namespaced `knowledge_base_<tool>`.

| Tool | Purpose |
|------|---------|
| `kb_graph_tool` | Graph operations: `list`, `traverse`, `layers`, `entry_points` |
| `kb_impact_tool` | Analyze impact of changing an entity (risk-scored) |
| `kb_visualize_tool` | Render the graph as Mermaid / DOT / ASCII |
| `kb_trace_flow_tool` | Find a path between two entities |
| `kb_code_location_tool` | Locate file/line for a symbol |
| `kb_find_pattern_tool` | Find design patterns in the graph |
| `kb_session_tool` | Session context: `get` / `set` / `clear` |

### Search Modes

The KB supports multiple search strategies via `search_mode` parameter:

- **`hybrid`** (default) — Dense + sparse retrieval with RRF fusion (best overall)
- **`dense`** — Dense vector search only (semantic similarity)
- **`sparse`** — BM25 lexical search only (exact keyword matching)

### Query Preprocessing

Advanced query transformation via `query_mode` parameter:

- **`direct`** (default) — No transformation
- **`rewrite`** — LLM-based query rewriting
- **`hyde`** — Hypothetical Document Embedding
- **`multi_query`** — Generate N query variants for broader recall
- **`decompose`** — Break complex questions into sub-questions

### KB Entry Structure

**Entry Types** (with ID prefixes):
- `pattern` → `PAT-XXXX` — Reusable patterns or best practices
- `finding` → `FIND-XXXX` — Discoveries or insights
- `decision` → `DEC-XXXX` — Architectural or design decisions
- `correction` → `COR-XXXX` — Corrections to existing entries

**Entry Categories**:
- `code`, `class`, `method`, `function`, `workflow`, `documentation`, `architecture`

### Usage Examples

#### Query the KB (Recommended First Step)
```python
# Ask a question with synthesized answer
result = knowledge_base_kb_ask_tool(
    question="What is the MVC++ architecture?",
    top_k=3,
    search_mode="hybrid",
    query_mode="direct",
)

# Search for specific entries
result = knowledge_base_kb_search_tool(
    query="RAG implementation",
    top_k=5,
    category="architecture",
    search_mode="hybrid",
    rerank=True,
)
```

#### Add New Knowledge
```python
# Add a new pattern
result = knowledge_base_kb_add_tool(
    entry_type="pattern",
    category="architecture",
    title="MVC++ Pattern",
    finding="Separation of concerns with three layers",
    solution="Use Model-View-Controller with Abstract Partner pattern",
    context="All screens must follow MVC++ structure",
    confidence=0.95,
    example="MainController ↔ MainView (ABC) ↔ SessionManager",
)
```

#### Populate Workspace
```python
# Scan and ingest the entire workspace
result = knowledge_base_kb_populate_workspace_tool(
    workspace_root="/path/to/project",
    include_python=True,
    include_markdown=True,
    reset_first=True,
)
```

### KB v4 Features

The v4 implementation includes:

1. **Semantic Code Understanding** — AST analysis with relationship detection
2. **Knowledge Graph** — 16 relationship types, graph traversal, impact analysis
3. **Hybrid Search** — Dense + sparse retrieval with Reciprocal Rank Fusion
4. **Neural Reranking** — Cross-encoder for improved precision
5. **Query Preprocessing** — 5 modes for query enhancement
6. **LLM Synthesis** — Natural language answers with citations
7. **Auto-Chunking** — Automatic chunking of long entries
8. **MCP Resources** — 15 dynamic resource endpoints
9. **MCP Prompts** — 10 pre-built prompt templates
10. **Progress Callbacks** — Real-time progress for long operations

### Performance Characteristics

| Operation | Typical Latency |
|-----------|----------------|
| Hybrid search (top_k=5) | 100-200ms |
| With reranking | 200-500ms |
| LLM synthesis | 500-2000ms |
| Workspace population | 30-300 seconds (depends on size) |

### Important Notes

- **ALWAYS query KB first** before starting any task (mandatory per Core Directives #8)
- **Cite KB sources** in every response (entry IDs like `PAT-A1B2`, `FIND-C3D4`)
- **Use hybrid mode** for best results (default)
- **Enable reranking** for critical queries (default: `True`)
- **KB is v4-only** — all v2/v3 legacy code has been removed
- **443 tests passing** — KB is production-ready

### Related Documentation

- **Full KB Documentation**: `mcp_servers/knowledge_base/README.md`
- **KB v4 Implementation Plan**: `.meta/projects/kb-mcp-v4/PLAN.md`
- **KB v4 Status**: `.meta/projects/kb-mcp-v4/STATUS.md`
- **KB v4 Implementation Details**: `.meta/projects/kb-mcp-v4/IMPLEMENTATION.md`
- **OMT++ Guide**: `.meta/doc/omt_agent_guide.md` (mandatory for code changes)

---

**Version:** 5.0.0 (OMT++ integrated) | **Updated:** 2026-06-06 (KB v4 references added)
