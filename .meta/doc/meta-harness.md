# Meta Harness — Current State

**Version**: 4.0.0 — Semantic Code Understanding (Knowledge Graph + Hybrid RAG)
**Status**: ✅ Active
**Core Principle**: Auto-Populated Knowledge Through Source Code Analysis + Knowledge Graph + Mandatory KB-First Workflow
**Last Updated**: 2026-06-06

---

## Philosophy

The **Meta Project Harness** evolves through a continuous cycle of **discovery**, **documentation**, and **distribution** of knowledge.

### Core Belief

> **Knowledge should be captured at the moment of discovery, validated through use, and distributed automatically to all agents.**

The Meta Harness approach:
- ✅ Captured **during** work (fresh insights)
- ✅ **Auto-populated** from source code via MCP server (AST analysis)
- ✅ **Graph-aware** — entities and relationships modelled as a knowledge graph (v4)
- ✅ **Integrated** into workflow (unavoidable via KB-First mandate)
- ✅ **Tested** continuously via test suite (443 tests, 86% coverage of `kb/`)

---

## Physical Structure

```
agentx/
├── mcp_servers/
│   └── knowledge_base/              # MCP server (v4)
│       ├── server.py                # MCP entry point: 14 tools + 15 resources + 10 prompts (891 lines)
│       ├── pyproject.toml           # hatchling wheel, uvx entry point
│       ├── README.md                # Comprehensive KB docs (573 lines)
│       ├── chroma_db/               # ChromaDB persistence (auto-created)
│       │
│       ├── kb/                      # Core RAG library (v4) — ~4.6k lines
│       │   ├── __init__.py          # Public API exports (63)
│       │   ├── api.py               # search / ask / add_entry / stats / reset / populate_workspace (537)
│       │   ├── store.py             # KBStore — ChromaDB client + collection mgmt (328)
│       │   ├── search.py            # Hybrid search orchestration (227)
│       │   ├── retrieval.py         # DenseRetriever, FusionRetriever, hybrid_retrieve (307)
│       │   ├── sparse_index.py      # BM25 sparse retrieval (328)
│       │   ├── reranking.py         # Cross-encoder neural reranking (337)
│       │   ├── query_engine.py      # Query preprocessing: rewrite/hyde/multi_query/decompose (284)
│       │   ├── synthesis.py         # Answer synthesis: template + LLM modes (452)
│       │   ├── embedding.py         # Embedding model registry (330)
│       │   ├── chunking.py          # Auto-chunking for long entries (458)
│       │   ├── ingest.py            # Python AST + Markdown ingestion (375)
│       │   ├── eval.py              # Retrieval evaluation tools (419)
│       │   ├── models.py            # Dataclasses for API return types (113)
│       │   ├── ids.py               # Entry ID generation — make_entry_id (53)
│       │   └── logging.py           # stderr-only logger "kb" (33)
│       │
│       ├── analyzer/                # Semantic code analysis (v4)
│       │   ├── python_ast.py        # Python AST traversal
│       │   ├── symbol_resolver.py   # Symbol resolution & disambiguation
│       │   ├── relationships.py     # Code relationship detection
│       │   ├── patterns.py          # Code pattern recognition
│       │   ├── docstring.py         # Docstring extraction
│       │   └── base.py              # Base analyzer classes
│       │
│       ├── graph/                   # Knowledge graph engine (v4)
│       │   ├── engine.py            # KnowledgeGraph: construction + traversal
│       │   ├── builder.py           # GraphBuilder from code analysis
│       │   ├── store.py             # GraphStore persistence
│       │   ├── queries.py           # GraphQueries: traverse/layers/entry_points
│       │   ├── export.py            # Mermaid / DOT / ASCII / JSON export
│       │   ├── sync.py              # Graph-code synchronization
│       │   └── models.py            # Entity, Relationship, ImpactResult, EntityKind, RelationshipKind
│       │
│       ├── resources/               # MCP resources (v4) — 15 endpoints
│       │   ├── registry.py          # ResourceRegistry
│       │   ├── project.py           # Project tree/summary/metadata
│       │   ├── arch.py              # Components/dependencies/layers/patterns
│       │   ├── flows.py             # Data/control/import/event flows
│       │   ├── api.py               # Endpoints / public API
│       │   ├── code.py              # Code search
│       │   ├── session.py           # Session state
│       │   ├── quality.py           # Code quality metrics
│       │   └── exporters.py         # Resource export utilities
│       │
│       ├── prompts/                 # MCP prompts (v4) — 10 templates
│       │   ├── engine.py            # PromptEngine
│       │   ├── registry.py          # PromptRegistry
│       │   ├── analysis.py          # Code analysis prompts
│       │   ├── modification.py      # Code modification prompts
│       │   ├── navigation.py        # Code navigation prompts
│       │   └── onboarding.py        # Onboarding prompts
│       │
│       └── tests/                   # pytest suite (20+ modules, 443 tests)
│
├── .meta/
│   ├── META.md                      # META directory rules
│   ├── doc/
│   │   ├── META.md                  # doc/ directory rules
│   │   ├── omt_agent_guide.md       # OMT++ methodology (mandatory for code changes)
│   │   └── meta-harness.md          # This document
│   ├── experiments/                 # Prototyping sandbox
│   └── projects/
│       └── kb-mcp-v4/               # KB v4 project plan, status, implementation
│
└── opencode.jsonc                   # MCP configuration (reference)
```

---

## Logical Layers

```
┌─────────────────────────────────────────────────────────┐
│ LAYER 1: AGENT LAYER                                      │
│ - opencode AI agent                                       │
│ - MANDATORY: Query KB before ANY task                     │
│ - MANDATORY: Cite KB sources in every response            │
│ - Documents findings (kb_add_tool) after work             │
└─────────────────────────────────────────────────────────┘
            │  MCP Protocol (stdio transport)
            ▼
┌─────────────────────────────────────────────────────────┐
│ LAYER 2: MCP SERVER LAYER (server.py, 891 lines)          │
│ - FastMCP wrapper                                         │
│ - 14 tools (7 core RAG + 7 graph/extended)                │
│ - 15 resources (knowledge-base://...)                     │
│ - 10 prompts (onboard-agent, plan-feature, ...)           │
│ - Lazy v4 component init via get_v4_components()           │
│ - Extended timeout via KB_MCP_TIMEOUT (default 1800s)     │
└─────────────────────────────────────────────────────────┘
            │  Python API + v4 components
            ▼
┌─────────────────────────────────────────────────────────┐
│ LAYER 3: RAG + ANALYSIS LAYER                             │
│ - kb/api.py        search / ask / add / stats / reset     │
│ - kb/search.py     hybrid orchestration                   │
│ - kb/retrieval.py  dense + fusion (RRF)                   │
│ - kb/sparse_index  BM25 lexical                           │
│ - kb/reranking.py  cross-encoder rerank                   │
│ - kb/query_engine  query preprocessing (5 modes)          │
│ - kb/synthesis.py  template / LLM answer synthesis        │
│ - analyzer/        Python AST → entities + relationships  │
│ - graph/           KnowledgeGraph + impact analysis       │
└─────────────────────────────────────────────────────────┘
            │  ChromaDB client / Graph store
            ▼
┌─────────────────────────────────────────────────────────┐
│ LAYER 4: STORAGE LAYER                                    │
│ - kb/store.py    KBStore — ChromaDB persistent client     │
│ - graph/store.py GraphStore — graph persistence           │
│ - Persistent vector store: chroma_db/                     │
│ - Embedding registry (bge-small-en default)               │
│ - Lazy initialization                                     │
└─────────────────────────────────────────────────────────┘
```

---

## Knowledge Base — Current State

> Live snapshot from `kb_stats_tool` (2026-06-06).

| Metric | Value |
|--------|-------|
| **Total entries** | **1879** |
| **By type** | pattern (197), finding (803) |
| **By category** | class (197), method (641), function (162) |
| **Mean confidence** | 0.9559 |
| **Median confidence** | 0.95 |
| **Population method** | Auto-generated from workspace (Python AST + Markdown) via `kb_populate_workspace_tool` |
| **Storage** | ChromaDB persistent vector store (`mcp_servers/knowledge_base/chroma_db/`) |

> **Note**: The headline total (1879) is the full collection count. The by-type /
> by-category / confidence breakdowns are computed over a sampled window
> (≈1000 entries) by `kb_stats_tool`, so those rows sum to the sample rather than
> the full total.

### Entry Types

| Type | Prefix | Purpose | Example |
|------|--------|---------|---------|
| `pattern` | `PAT-` | Reusable solution or structure | "Class MainController implements MVC++" |
| `finding` | `FIND-` | Discovered fact or insight | "Method defined at line 14" |
| `decision` | `DEC-` | Architectural or design choice | "Use ChromaDB over SQLite" |
| `correction` | `COR-` | Fixed or updated knowledge | "Workflow changed in v4" |

### Confidence System

- **≥ 0.9**: High confidence (trusted)
- `0.6 – 0.9`: Medium confidence (use with caution)
- **< 0.6**: Low confidence (verify independently)

Manual entries should start at 0.5–0.7; auto-extracted source-code facts at 0.95+.

### Entry-ID Scheme

`make_entry_id(entry_type, category, title)` returns `{PREFIX}-{4-uppercase-hex}`
(e.g. `PAT-A1B2`, `FIND-C3D4`). The 4-char suffix is the first 4 chars of
`md5(entry_type + category + timestamp + random)`, uppercased.

### Entry Schema (ChromaDB metadata)

```python
metadata = {
    "entry_id": "PAT-50B1",          # Unique identifier
    "type": "pattern",                # pattern|finding|decision|correction
    "category": "class",              # code|class|method|function|workflow|documentation|architecture
    "title": "Class: MainController",
    "finding": "Class MainController defined in controller.py",
    "solution": "Class MainController with methods: __init__, run, stop",
    "context": "",                    # Optional
    "example": "from src.agentx.controller import MainController",
    "confidence": 0.98,               # 0.0 to 1.0
    "created_at": "2026-06-06T...",   # ISO format
    "is_chunked": False,              # v4: whether entry was auto-chunked
    "chunk_count": 1                  # v4: number of chunks (if chunked)
}
```

---

## MCP Tool Reference (14 tools)

> Tool names below match `server.py` exactly. When called through opencode they are
> namespaced as `knowledge_base_<tool>` (e.g. `knowledge_base_kb_ask_tool`).

### Core RAG Tools (7)

| Tool | Purpose | Key defaults |
|------|---------|--------------|
| `kb_search_tool` | Hybrid search (dense + sparse + RRF) over KB | `top_k=5`, `search_mode="hybrid"`, `rerank=True` |
| `kb_ask_tool` | Retrieve + synthesise answer with citations | `top_k=3`, `synthesis_mode="template"` |
| `kb_add_tool` | Insert a single entry (auto-chunking) | `confidence=0.5` |
| `kb_stats_tool` | Counts by type/category + confidence stats | — |
| `kb_reset_tool` | Drop & recreate the Chroma collection (destructive) | — |
| `kb_populate_workspace_tool` | Walk workspace and ingest `.py` + `.md` | `reset_first=True`, `include_python=True` |
| `kb_list_categories` | List valid entry types and categories | — |

### Knowledge Graph / Extended Tools (7)

| Tool | Purpose | Key params |
|------|---------|-----------|
| `kb_graph_tool` | Graph operations: `list`, `traverse`, `layers`, `entry_points` | `operation`, `entity_id`, `depth`, `direction` |
| `kb_impact_tool` | Impact analysis of changing an entity | `entity_id`, `change_type="modify"`, `depth=3` |
| `kb_visualize_tool` | Render graph as `mermaid` / `dot` / `ascii` | `view="full"`, `format="mermaid"`, `root`, `depth` |
| `kb_trace_flow_tool` | Find a path between two entities | `source`, `target`, `max_depth=5` |
| `kb_code_location_tool` | Locate file/line for a symbol | `symbol`, `include_code=False` |
| `kb_find_pattern_tool` | Find design patterns in the graph | `pattern`, `language="python"` |
| `kb_session_tool` | Session context: `get` / `set` / `clear` | `action`, `key`, `value` |

### Pre-Task Research (MANDATORY)

```python
# RAG-augmented Q&A — RECOMMENDED first step
result = knowledge_base_kb_ask_tool(
    question="Where should I implement this feature?",
    top_k=3,
    search_mode="hybrid",      # hybrid | dense | sparse
    query_mode="direct",       # direct | rewrite | hyde | multi_query | decompose
    synthesis_mode="template", # template | llm
)

# Search with optional category filter
results = knowledge_base_kb_search_tool(
    query="MVC++ implementation",
    top_k=5,
    category="class",          # optional filter
    rerank=True,               # cross-encoder reranking
)
```

`kb_ask_tool` output format:

```
✓ Answer synthesized from N sources (Confidence: 0.88)

<answer text>

📖 Sources:
  • [PAT-A1B2] Class: MainController (Conf: 0.98)
```

**System Rule** (AGENTS.md): *"⚠️ MANDATORY SECOND STEP: Before ANY task, query the KB using the MCP knowledge_base tools."*

### Post-Task Documentation (MANDATORY)

```python
result = knowledge_base_kb_add_tool(
    entry_type="pattern",       # pattern|finding|decision|correction
    category="workflow",        # code|class|method|function|workflow|documentation|architecture
    title="My Discovery",
    finding="What I found (be specific)",
    solution="How to handle it (actionable)",
    context="When/where this applies (optional)",
    confidence=0.95,
    example="code snippet (optional)",
)
```

### Populate Workspace

```python
result = knowledge_base_kb_populate_workspace_tool(
    workspace_root=None,           # defaults to repo root
    include_python=True,
    include_markdown=True,
    reset_first=True,              # clean KB before population
    exclude_dirs=[".agents", ".idea", "local_sessions"],  # extends built-in defaults
)
```

---

## Search, Query & Synthesis Modes (v4)

### Search Modes (`search_mode`)

| Mode | Description | Use Case |
|------|-------------|----------|
| `hybrid` *(default)* | Dense + sparse retrieval with RRF fusion | General purpose, best overall |
| `dense` | Dense vector search only | Semantic similarity queries |
| `sparse` | BM25 lexical search only | Exact keyword matching |

### Query Preprocessing Modes (`query_mode`)

| Mode | Description |
|------|-------------|
| `direct` *(default)* | No transformation (passthrough) |
| `rewrite` | LLM-based query rewriting |
| `hyde` | Hypothetical Document Embedding |
| `multi_query` | Generate N query variants for broader recall |
| `decompose` | Break complex questions into sub-questions |

### Synthesis Modes (`synthesis_mode`)

| Mode | Description |
|------|-------------|
| `template` *(default)* | Template-based markdown synthesis (fast, deterministic) |
| `llm` | LLM-based natural language generation |

### Hybrid Scoring Pipeline

1. **Parallel retrieval** — dense (ChromaDB ANN, default `bge-small-en`) + sparse (BM25).
2. **Reciprocal Rank Fusion** — `score(doc) = Σ 1 / (k + rank_i(doc))`, default `k=60`.
3. **Neural reranking** *(optional)* — cross-encoder `ms-marco-MiniLM-L6-v2` reranks top candidates.

### Embedding Models (`embedding_model`)

| Model | Dim | Speed | Quality |
|-------|-----|-------|---------|
| `bge-small-en` *(default)* | 384 | Fast | Good |
| `bge-base-en` | 768 | Medium | Better |
| `bge-large-en` | 1024 | Slow | Best |
| `miniLM-L6-v2` | 384 | Very Fast | OK |

---

## Knowledge Graph (v4)

The `analyzer/` layer parses Python via AST into **entities** and **relationships**;
the `graph/` layer stores them in a `KnowledgeGraph` and supports traversal,
impact analysis, path finding, and export.

```python
# List / traverse the graph
knowledge_base_kb_graph_tool(operation="list")
knowledge_base_kb_graph_tool(operation="traverse", entity_id="MainController", depth=3)
knowledge_base_kb_graph_tool(operation="layers")
knowledge_base_kb_graph_tool(operation="entry_points")

# Impact of a change (risk-scored)
knowledge_base_kb_impact_tool(entity_id="SessionManager", change_type="modify", depth=3)

# Visualize (mermaid | dot | ascii)
knowledge_base_kb_visualize_tool(view="full", format="mermaid")

# Trace a path between two symbols
knowledge_base_kb_trace_flow_tool(source="MainController", target="KBStore")

# Locate a symbol / find patterns
knowledge_base_kb_code_location_tool(symbol="run")
knowledge_base_kb_find_pattern_tool(pattern="singleton")
```

`graph/models.py` defines `Entity`, `Relationship`, `ImpactResult`, `EntityKind`,
and `RelationshipKind`. Impact results carry per-entity `risk_levels`
(🔴 high / 🟡 medium / 🟢 low) and affected `test_files`.

---

## MCP Resources & Prompts (v4)

### Resources (15) — `knowledge-base://...`

| Group | URIs |
|-------|------|
| **project** | `project/tree`, `project/summary`, `project/metadata` |
| **arch** | `arch/components`, `arch/dependencies?format={format}`, `arch/layers`, `arch/patterns` |
| **flows** | `flows/data`, `flows/control`, `flows/imports`, `flows/events` |
| **api** | `api/endpoints`, `api/public` |
| **code** | `code/search?query={query}` |
| **health** | `health` |

### Prompts (10)

`onboard-agent`, `find-entry-point`, `plan-feature(feature_description)`,
`trace-bug(symptom)`, `understand-flow(source, target)`,
`review-change(planned_changes)`, `find-similar(code_pattern)`,
`write-test(module_path)`, `refactor-guide(target, goal)`,
`summarize-changes(from_ref, to_ref)`.

---

## KB-First Workflow

### Decision Tree (from AGENTS.md)

```
Need to...
├─ Understand something?  → Query KB via MCP tools first
├─ Modify code?           → Read OMT++ guide → follow MVC++ / phases
├─ Prototype/test idea?   → .meta/experiments/
├─ Write tests?           → tests/unit/ (with approval) or .meta/experiments/
├─ Plan a project?        → .meta/projects/
├─ Store data/KB?         → .meta/data/
└─ Document something?    → .meta/doc/
```

### 5-Step Workflow (OMT++ aligned)

1. **UNDERSTAND** — Query KB via MCP + check git log
2. **DESIGN** — Identify directory, interfaces (Abstract Partner ABCs), specs
3. **EXECUTE** — Implement MVC++ layers; test frequently
4. **VALIDATE** — Unit → integration → system tests pass
5. **REPORT** — Summarize + document findings (`kb_add_tool`) + cleanup

---

## Quality Gates

- [ ] **Clear finding**: What was discovered?
- [ ] **Actionable solution**: How to handle it?
- [ ] **Appropriate category**: code, class, method, function, workflow, documentation, architecture
- [ ] **Honest confidence**: 0.5–0.7 for manual entries, 0.95+ for auto-extracted facts
- [ ] **Tested in practice**: Not theoretical

---

## KB Health Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Total entries | 100+ | 1879 | ✅ Excellent |
| Mean confidence | > 0.9 | 0.9559 | ✅ Strong |
| Population coverage | 100% of workspace | Auto-populated (Python + Markdown) | ✅ Complete |
| Test suite | Green | 443 passing | ✅ Healthy |
| `kb/` coverage | > 80% | 86% | ✅ Good |
| Manual entries | Growing | ~0 (mostly auto-generated) | 🟡 Opportunity |

---

## Experimental Validation (2026-05-23)

A controlled experiment compared KB-first vs non-KB approaches:

| Metric | Without KB | With KB | Improvement |
|--------|-----------|----------|-------------|
| Search time | 2-3 min | ~30 sec | **5-10x faster** |
| Component coverage | ~70% | ~95% | **35% more complete** |
| Confidence | Medium (inferred) | High (0.95-0.98) | **Verified** |
| Cognitive load | High (guessing) | Low (direct) | **Much lower** |

**Conclusion**: KB-first workflow is **5-10x more efficient** with **verified accuracy**.

---

## Common Pitfalls

| Pitfall | Mistake | Solution |
|---------|---------|----------|
| Overconfidence | Setting confidence to 1.0 on first entry | Start at 0.5-0.7 for manual, 0.95+ for source-code facts |
| Vague findings | "Things work better this way" | Be specific: "Method MainController.run() initializes subsystems at line 45" |
| Wrong category | Using "misc" | Choose from the 7 valid categories |
| Skipping documentation | "I'll document later" | Document immediately via `kb_add_tool` |
| Ignoring auto-generated entries | Assuming auto-KB is complete | Manual entries needed for workflows, decisions, insights |
| Not querying KB first | Starting work without KB query | KB-First is MANDATORY |
| Wrong tool name | Guessing graph tool names | Use the names in this doc / `server.py` (e.g. `kb_graph_tool`, not `kb_graph_query`) |

---

## MCP Server Configuration

Current `opencode.jsonc` (reference) registers the server via `uvx`:

```jsonc
// opencode.jsonc
{
  "mcp": {
    "knowledge_base": {
      "type": "local",
      "enabled": true,
      "command": [
        "uvx",
        "--from",
        "./mcp_servers/knowledge_base",
        "knowledge_base"
      ],
      "timeout": 180000000
    }
  }
}
```

The server also honours the `KB_MCP_TIMEOUT` environment variable (seconds,
default `1800`) for long-running operations such as workspace population.

---

## Core Principles

1. **Capture Immediately** — Document at moment of discovery
2. **Validate Through Use** — Confidence comes from repeated use
3. **Distribute Automatically** — RAG ensures knowledge reaches those who need it
4. **Query First (MANDATORY)** — KB-first workflow before ANY task
5. **Cite Sources (MANDATORY)** — All responses must cite KB sources with confidence scores
6. **Auto-Discover Knowledge** — Scan source code (AST) for factual structure + relationships
7. **Hybrid Search** — Dense + sparse + RRF fusion, with optional neural reranking
8. **Model the Graph** — Entities and relationships drive impact analysis and navigation
9. **Measure Everything** — `kb_stats_tool` drives improvement

---

## UI Input Component Pattern (established 2026-05-30)

All input components under `src/agentx/ui/common/input/` follow a strict **Controller/View separation**:

| Layer | Responsibility | Example |
|-------|---------------|---------|
| **Controller** | Owns all business logic, validation, state | `InputCreateFolderController` |
| **View** | Pure I/O — prompt user, display messages only | `InputCreateFolderView` |

### Pattern

- Controller holds the result as a public attribute (e.g. `folder_name`, `items`, `url`)
- `Controller.show()` orchestrates the flow: calls view → validates → stores result
- View methods return raw values; never call setters on the controller
- View display methods are named `show_*` (e.g. `show_error_folder_exists`, `show_done`)
- Circular imports avoided with `from __future__ import annotations` + `TYPE_CHECKING`

### Existing Components

| Component | Directory | Controller | View | Result |
|-----------|-----------|------------|------|--------|
| Folder name | `create_folder/` | `InputCreateFolderController` | `InputCreateFolderView` | `folder_name: str \| None` |
| Text list | `text_list/` | `InputTextListController` | `InputTextView` | `items: list[str]` |
| URL entry | `url_entry/` | `InputUrlController` | `InputUrlView` | `url: str \| None` |
| Options | `options/` | `InputOptionsController` | `InputOptionsView` | `selected_option: int \| None` |

---

**Status**: ✅ Active
**Location**: `.meta/doc/meta-harness.md`
**Version**: 4.0.0 (Knowledge Graph + Hybrid RAG)
**KB Implementation**: ChromaDB vector store + knowledge graph via MCP server
**MCP Surface**: 14 tools · 15 resources · 10 prompts
**Current Stats**: 1879 entries (mean confidence 0.96) · 443 tests passing
**Last Updated**: 2026-06-06
