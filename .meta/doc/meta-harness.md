# Meta Harness — Current State

**Version**: 3.1.0 — MCP Server Architecture + KB-First Workflow
**Status**: ✅ Active
**Core Principle**: Auto-Populated Knowledge Through Source Code Analysis + Mandatory KB-First Workflow
**Last Updated**: 2026-05-30

---

## Philosophy

The **Meta Project Harness** evolves through a continuous cycle of **discovery**, **documentation**, and **distribution** of knowledge.

### Core Belief

> **Knowledge should be captured at the moment of discovery, validated through use, and distributed automatically to all agents.**

The Meta Harness approach:
- ✅ Captured **during** work (fresh insights)
- ✅ **Auto-populated** from source code via MCP server
- ✅ **Integrated** into workflow (unavoidable via KB-First mandate)
- ✅ **Tested** continuously via test suite

---

## Physical Structure

```
agentx/
├── mcp_servers/
│   └── knowledge_base/          # MCP server (1507 lines total)
│       ├── server.py            # MCP server entry point (320 lines)
│       ├── kb/                  # KB logic layer
│       │   ├── __init__.py      # Package init (40 lines)
│       │   ├── api.py           # High-level API (266 lines)
│       │   ├── store.py         # ChromaDB wrapper (135 lines)
│       │   ├── ingest.py        # Python/Markdown analyzer (302 lines)
│       │   ├── search.py        # Hybrid search: semantic + keyword (166 lines)
│       │   ├── synthesis.py     # RAG synthesis (94 lines)
│       │   ├── models.py        # Data models (98 lines)
│       │   ├── ids.py           # Entry ID generation (53 lines)
│       │   └── logging.py       # Logging utilities (33 lines)
│       ├── tests/               # 6 test files
│       │   ├── test_server.py
│       │   ├── test_store.py
│       │   ├── test_search.py
│       │   ├── test_synthesis.py
│       │   ├── test_ingest.py
│       │   └── test_ids.py
│       └── chroma_db/           # Persistent vector store
│
├── .meta/
│   ├── META.md                  # META directory rules
│   ├── doc/
│   │   ├── META.md              # doc/ directory rules
│   │   └── meta-harness.md      # This document
│   ├── experiments/             # Prototyping sandbox
│   │   └── META.md
│   └── projects/                # Project plans
│       └── META.md
│
└── opencode.jsonc               # MCP configuration
```

---

## Logical Layers

```
┌─────────────────────────────────────────────────────────┐
│ LAYER 1: AGENT LAYER                                    │
│ - opencode AI agent                                     │
│ - MANDATORY: Query KB before ANY task                   │
│ - MANDATORY: Cite KB sources in every response          │
│ - Documents findings (kb_add_tool) after work           │
└─────────────────────────────────────────────────────────┘
│
│ MCP Protocol (stdio transport)
▼
┌─────────────────────────────────────────────────────────┐
│ LAYER 2: MCP SERVER LAYER                               │
│ - server.py (FastMCP wrapper, 320 lines)               │
│ - 7 MCP tools exposed:                                 │
│   • knowledge_base_kb_ask_tool        (RAG Q&A)        │
│   • knowledge_base_kb_search_tool     (Search)         │
│   • knowledge_base_kb_add_tool        (Add entry)      │
│   • knowledge_base_kb_stats_tool      (Statistics)     │
│   • knowledge_base_kb_reset_tool      (Reset)          │
│   • knowledge_base_kb_populate_workspace_tool (Pop.)   │
│   • knowledge_base_kb_list_categories (Categories)     │
│ - Extended timeout: 1800s                              │
└─────────────────────────────────────────────────────────┘
│
│ Python API Layer
▼
┌─────────────────────────────────────────────────────────┐
│ LAYER 3: API LAYER (kb/api.py, 266 lines)               │
│ - search()              Hybrid search wrapper           │
│ - ask()                 RAG synthesis wrapper           │
│ - add_entry()           Entry creation                  │
│ - stats()               Statistics computation          │
│ - reset()               Collection reset                │
│ - populate_workspace()  Workspace ingestion             │
│ - All functions return Result types                     │
└─────────────────────────────────────────────────────────┘
│
│ ChromaDB Client
▼
┌─────────────────────────────────────────────────────────┐
│ LAYER 4: STORAGE LAYER (kb/store.py, 135 lines)          │
│ - KBStore class — ChromaDB persistent client           │
│ - Persistent storage (chroma_db/)                      │
│ - Automatic embedding generation                       │
│ - Hybrid search (semantic + keyword)                   │
│ - Lazy initialization (get_default_store())            │
└─────────────────────────────────────────────────────────┘
```

---

## Knowledge Base — Current State

| Metric | Value |
|--------|-------|
| **Total entries** | **170** |
| **By type** | pattern (41), finding (129) |
| **By category** | class (41), method (106), function (23) |
| **High confidence (≥0.9)** | **170 (100%)** |
| **Population method** | Auto-generated from `src/` (Python + Markdown) via `kb_populate_workspace_tool` |
| **Storage** | ChromaDB persistent vector store |

### Entry Types

| Type | Prefix | Purpose | Example |
|------|--------|---------|---------|
| `pattern` | PAT- | Reusable solution or structure | "Class MainController implements MVC" |
| `finding` | FIND- | Discovered fact or insight | "Method defined at line 14" |
| `decision` | DEC- | Architectural or design choice | "Use ChromaDB over SQLite" |
| `correction` | COR- | Fixed or updated knowledge | "Workflow changed in v3.1" |

### Confidence System

- **≥ 0.9**: High confidence (trusted) — **Current KB: 100%**
- `0.6 – 0.9`: Medium confidence (use with caution)
- **< 0.6**: Low confidence (verify independently)

### Entry Schema (ChromaDB)

```python
metadata = {
    "entry_id": "PAT-50B1",         # Unique identifier
    "type": "pattern",               # pattern|finding|decision|correction
    "category": "class",             # code|class|method|function|workflow|documentation|architecture
    "title": "Class: MainController",
    "finding": "Class MainController defined in controller.py",
    "solution": "Class MainController with methods: __init__, run, stop",
    "context": "",                   # Optional
    "example": "from src.agentx.controller import MainController",
    "confidence": 0.98,              # 0.0 to 1.0
    "created_at": "2026-05-30T..."   # ISO format
}
```

---

## MCP Tools Reference

### 1. Pre-Task Research (MANDATORY)

```python
# RAG-augmented Q&A — RECOMMENDED
result = knowledge_base_ask_tool(
    question="Where should I implement this feature?",
    top_k=3
)

# Search with optional category filter
results = knowledge_base_search_tool(
    query="MVC implementation",
    top_k=5,
    category="class"  # Optional filter
)
```

**System Rule** (AGENTS.md): *"⚠️ MANDATORY SECOND STEP: Before ANY task, query the KB using the MCP knowledge_base tools."*

### 2. Post-Task Documentation (MANDATORY)

```python
result = knowledge_base_add_tool(
    entry_type="pattern",       # pattern|finding|decision|correction
    category="workflow",        # code|class|method|function|workflow|documentation|architecture
    title="My Discovery",
    finding="What I found (be specific)",
    solution="How to handle it (actionable)",
    context="When/where this applies (optional)",
    confidence=0.95,
    example="code snippet (optional)"
)
```

**System Rule** (AGENTS.md): *"ALWAYS: 9. Query KB first using MCP tools, cite sources in every response"*

### 3. KB Statistics

```python
stats = knowledge_base_kb_stats_tool()
# Output:
# Total Entries: 170
# By Type: pattern (41), finding (129)
# By Category: class (41), method (106), function (23)
# Confidence: High (≥0.9): 170
```

### 4. Populate Workspace

```python
result = knowledge_base_populate_workspace_tool(
    include_python=True,
    include_markdown=True,
    reset_first=True,              # Clean KB before population
    exclude_dirs=[".agents", ".idea", "local_sessions"]  # Extends built-in defaults
)
```

### 5. List Valid Categories

```python
categories = knowledge_base_list_categories()
# Valid Entry Types: pattern, finding, decision, correction
# Valid Categories: code, class, method, function, workflow, documentation, architecture
```

### 6. Reset KB (Destructive)

```python
# WARNING: Deletes ALL entries — irreversible
result = knowledge_base_reset_tool()
```

---

## KB-First Workflow

### Decision Tree (from AGENTS.md)

```
Need to...
├─ Understand something?  → Query KB via MCP tools first
├─ Modify code?           → Work on source code directly
├─ Prototype/test idea?   → .meta/experiments/
├─ Write tests?           → tests/unit/ (with approval) or .meta/experiments/
├─ Plan a project?        → .meta/projects/
├─ Store data/KB?         → `.meta/data/` (planned)
└─ Document something?    → `.meta/doc/`
```

### 5-Step Workflow

1. **UNDERSTAND** — Query KB via MCP + check git log
2. **PLAN** — Identify correct directory
3. **EXECUTE** — Work in safe space, test frequently
4. **VALIDATE** — Tests pass, no production break
5. **REPORT** — Summarize + document + cleanup

---

## Quality Gates

- [ ] **Clear finding**: What was discovered?
- [ ] **Actionable solution**: How to handle it?
- [ ] **Appropriate category**: code, class, method, function, workflow, documentation, architecture
- [ ] **Honest confidence**: Start at 0.5-0.7 for manual entries, 0.95+ for auto-extracted facts
- [ ] **Tested in practice**: Not theoretical

---

## KB Health Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Total entries | 100+ | 170 | ✅ Excellent |
| High confidence (≥0.9) | > 50% | 100% (170/170) | ✅ Perfect |
| Population coverage | 100% of src/ | Auto-populated | ✅ Complete |
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

---

## MCP Server Configuration

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
      "env": {
        "KB_MCP_TIMEOUT": "1800"  // 30 minutes for population
      }
    }
  }
}
```

---

## Core Principles

1. **Capture Immediately** — Document at moment of discovery
2. **Validate Through Use** — Confidence comes from repeated use
3. **Distribute Automatically** — RAG ensures knowledge reaches those who need it
4. **Query First (MANDATORY)** — KB-first workflow before ANY task
5. **Cite Sources (MANDATORY)** — All responses must cite KB sources with confidence scores
6. **Auto-Discover Knowledge** — Scan source code for factual structure
7. **Hybrid Search** — Semantic + keyword matching for best results
8. **Measure Everything** — `kb_stats_tool` drives improvement

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
**Version**: 3.1.0 (MCP Architecture + KB-First Mandate)
**KB Implementation**: ChromaDB vector store via MCP server
**Current Stats**: 170 entries (100% high confidence)
**Last Updated**: 2026-05-30
