# KB MCP v4 — Universal Project Understanding System

> **Status**: 📋 Planned
> **Target**: `mcp_servers/knowledge_base/` — full MCP server overhaul
> **Version**: 4.0.0
> **Confidence**: 0.97
> **Target Audience**: Any project, any language, any scale
> **MCP Protocol Features Used**: Tools, Prompts, Resources (files)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
   - [1.4 Release Strategy: v4.0 Core + v4.1 Advanced](#14-release-strategy-v40-core--v41-advanced)
2. [The Problem — Why Current KB Fails Agents](#2-the-problem--why-current-kb-fails-agents)
3. [Design Principles](#3-design-principles)
4. [Architecture Overview](#4-architecture-overview)
   - [4.3 File Directory Map](#43-file-directory-map)
   - [4.4 Performance Budget](#44-performance-budget)
   - [4.5 Dependency Audit](#45-dependency-audit)
5. [Phase 1: Semantic Code Understanding Engine](#5-phase-1-semantic-code-understanding-engine)
6. [Phase 2: Knowledge Graph](#6-phase-2-knowledge-graph)
7. [Phase 3: MCP Resources Layer](#7-phase-3-mcp-resources-layer)
8. [Phase 4: MCP Prompts Layer](#8-phase-4-mcp-prompts-layer)
9. [Phase 5: Multi-Language Support](#9-phase-5-multi-language-support) *(v4.1)*
10. [Phase 6: Continuous Learning & Self-Healing](#10-phase-6-continuous-learning--self-healing) *(v4.1)*
11. [Phase 7: Evaluation & Quality Gates](#11-phase-7-evaluation--quality-gates) *(v4.1)*
12. [MCP Tool Reference](#12-mcp-tool-reference)
13. [MCP Resource Reference](#13-mcp-resource-reference)
14. [MCP Prompt Reference](#14-mcp-prompt-reference)
15. [Migration Path](#15-migration-path)
16. [Use Cases](#16-use-cases)
17. [Glossary](#17-glossary)

---

## 1. Executive Summary

### 1.1 The Core Insight

The current Knowledge Base (v3) is a **RAG system over extracted code facts** — it knows *where* things are but not *what they mean*, *how they connect*, or *why they exist*.

This was proven in our live test:

> **User**: "What is RAG in AgentX?"
>
> **KB v3**: "Method Rag.web_ingestion is defined in rag.py at line 47.
> Method RagProvider.__init__ is defined in rag_provider.py at line 10."
>
> **What an agent actually needs**: "RAG is a subsystem with two layers:
> Model (Rag → RagQuery → ChromaDB → LLM) and UI (Controller → View).
> Data flows: Web → WebExtract → ChromaDB → User query → RagQuery → LLM → Answer."

### 1.2 The Vision

**KB MCP v4** transforms the MCP server from a **passive fact database** into an **active project understanding system** that can answer — for *any* project, in *any* language:

- "What is the architecture of this project?"
- "How does data flow from input to output?"
- "What files would I need to change to add feature X?"
- "What is the dependency chain for this module?"
- "What design patterns are used here?"
- "Where is the best place to add this new functionality?"

### 1.3 Why MCP v4 Is Different

| Aspect | v3 (Current) | v4 (Target) |
|--------|-------------|-------------|
| **MCP Features Used** | Tools only | Tools + Prompts + Resources |
| **Code Understanding** | AST-level (flat) | Semantic (graph + flow + intent) |
| **Knowledge Model** | Flat entries in vector DB | Knowledge Graph (entities + relationships) |
| **Ingestion** | Python + Markdown only | Python, JS/TS, Rust, Go, Java, Ruby, C/C++, MD, config files |
| **Query Interface** | Search + Ask (text) | Search + Ask + Traverse + Visualize + Impact Analysis |
| **Output** | Text strings | Structured data (JSON, GraphML, Mermaid), Prompt templates |
| **Agent Context** | One-shot Q&A | Persistent session with context accumulation |
| **Self-Improvement** | None | Gap detection + auto-ingestion + feedback loops |
| **Project Type** | AgentX-specific | ANY project |

### 1.4 Release Strategy: v4.0 Core + v4.1 Advanced

The full v4 vision spans 7 phases, but not all are needed for the initial release.
To ship value faster and reduce risk, the implementation is split into two releases:

| Release | Phases | Scope | Timeline | New Dependencies |
|---------|--------|-------|----------|-----------------|
| **v4.0 Core** | 1–4 | Python semantic engine, knowledge graph, MCP resources + prompts | ~4–5 weeks | networkx, jinja2 |
| **v4.1 Advanced** | 5–7 | Multi-language backends, continuous learning, evaluation gates | ~4–6 weeks after v4.0 | tree-sitter (optional), radon (optional) |

**v4.0 Core** closes Gaps #1–#4 (Structural→Semantic, Flat→Graph, Static→Dynamic, Passive→Active)
from §2.1 by shipping architecture-level understanding for Python projects with
full MCP Tools + Resources + Prompts support.

**v4.1 Advanced** closes Gap #5 (Monolingual→Polyglot) and hardens the system for
production use with self-healing and quality gates.

All phases are designed with backward compatibility in mind — v3 tools continue
to work throughout both releases.

---

## 2. The Problem — Why Current KB Fails Agents

### 2.1 The Five Gaps

```
┌────────────────────────────────────────────────────────────┐
│                    THE FIVE GAPS                            │
├──────────┬─────────────────────────────────────────────────┤
│ GAP #1   │ STRUCTURAL vs SEMANTIC                          │
│          │ "Method X in file Y" ≠ "How does X work?"       │
├──────────┼─────────────────────────────────────────────────┤
│ GAP #2   │ FLAT vs GRAPH                                   │
│          │ No relationships, no dependencies, no flow       │
├──────────┼─────────────────────────────────────────────────┤
│ GAP #3   │ STATIC vs DYNAMIC                               │
│          │ One-shot population, no incremental learning    │
├──────────┼─────────────────────────────────────────────────┤
│ GAP #4   │ PASSIVE vs ACTIVE                               │
│          │ Waits for queries, doesn't guide the agent       │
├──────────┼─────────────────────────────────────────────────┤
│ GAP #5   │ MONOLINGUAL vs POLYGLOT                         │
│          │ Python-only AST parsing, misses entire projects │
└──────────┴─────────────────────────────────────────────────┘
```

### 2.2 The Live Proof

During a real session, the KB failed to answer "What is RAG in AgentX?"
with anything beyond file/line locations. It took 3 rounds of KB queries
plus reading actual source code to synthesize a coherent answer.

**Root cause**: The KB stored *what* exists (classes, methods) but not
*how they connect* (data flow, call graph, architecture layers).

### 2.3 The Missing MCP Features

The MCP protocol supports three primitives. v3 only uses one:

| MCP Primitive | Current Use | v4 Target |
|---------------|------------|-----------|
| **Tools** | ✅ 7 tools (search, ask, add, stats, reset, populate, list) | ✅ Expanded toolset |
| **Resources** | ❌ Not used | 📁 `/project/` filesystem with architecture, flows, API, decisions |
| **Prompts** | ❌ Not used | 📝 Pre-built templates for common agent tasks |

---

## 3. Design Principles

### 3.1 Universal (Any Project)

```
PRINCIPLE 1: Language-agnostic core
  └─ Every analysis phase must work for Python, JS/TS, Rust, Go,
     Java, Ruby, C/C++, and any future language.

PRINCIPLE 2: Framework-agnostic
  └─ Should work for Django, React, Actix, Spring Boot — or no framework.

PRINCIPLE 3: Scale-agnostic
  └─ From 10-file microservice to 10,000-file monorepo.
```

### 3.2 Agent-First

```
PRINCIPLE 4: Answer before facts
  └─ When an agent asks "what is X?", synthesize architecture-level
     answers FIRST, then provide structural details as backup.

PRINCIPLE 5: Proactive guidance
  └─ Use MCP Prompts to automatically suggest the right questions
     and workflows based on what the agent is doing.

PRINCIPLE 6: Context accumulation
  └─ Remember what the agent has already learned in a session.
     Don't re-explain. Build on previous answers.
```

### 3.3 Self-Improving

```
PRINCIPLE 7: Gap-driven ingestion
  └─ When a query fails (0 results, low confidence), auto-ingest
     the missing knowledge from the source code.

PRINCIPLE 8: Feedback loops
  └─ Let agents rate answers. Use ratings to improve retrieval,
     synthesis, and prioritization.

PRINCIPLE 9: Staleness detection
  └─ Track git changes. Re-index only changed files. Flag outdated
     synthesized knowledge.
```

---

## 4. Architecture Overview

### 4.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     MCP SERVER (KB MCP v4)                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    LAYER 1: TOOLS                         │   │
│  │  ┌──────┐ ┌────────┐ ┌────────┐ ┌──────┐ ┌──────────┐  │   │
│  │  │Query │ │Graph   │ │Impact  │ │Visual│ │Code      │  │   │
│  │  │Tools │ │Tools   │ │Analysis│ │Tools │ │Mod.Tools │  │   │
│  │  └──────┘ └────────┘ └────────┘ └──────┘ └──────────┘  │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                    LAYER 2: RESOURCES                     │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │   │
│  │  │/project/ │ │/arch/    │ │/flows/   │ │/api/       │  │   │
│  │  │ tree     │ │ deps     │ │ dataflow │ │ endpoints  │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                    LAYER 3: PROMPTS                       │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐  │   │
│  │  │onboarding    │ │navigation    │ │modification      │  │   │
│  │  │prompt        │ │prompt        │ │prompt            │  │   │
│  │  └──────────────┘ └──────────────┘ └──────────────────┘  │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                    LAYER 4: ENGINE                        │   │
│  │  ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │Semantic  │ │Knowledge   │ │Synthesis │ │Learning  │  │   │
│  │  │Analyzer  │ │Graph Engine│ │Engine    │ │Engine    │  │   │
│  │  └──────────┘ └────────────┘ └──────────┘ └──────────┘  │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                    LAYER 5: STORAGE                       │   │
│  │  ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ChromaDB  │ │Neo4j/SG   │ │DocStore │ │GitCache  │  │   │
│  │  │(vectors) │ │(graph)    │ │(SQLite) │ │(metadata)│  │   │
│  │  └──────────┘ └────────────┘ └──────────┘ └──────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               LANGUAGE BACKENDS (pluggable)                │   │
│  │  ┌────────┐ ┌────────┐ ┌──────┐ ┌──────┐ ┌──────────┐  │   │
│  │  │Python  │ │JS/TS   │ │Rust  │ │Go    │ │Java/...  │  │   │
│  │  │(LSP)   │ │(ts-m)  │ │(ra)  │ │(gop) │ │(LSP)     │  │   │
│  │  └────────┘ └────────┘ └──────┘ └──────┘ └──────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 Three-Pillar MCP Strategy

```
PILLAR 1: TOOLS  ───── Actions agents can take
│
├─ kb_query_tool          → Ask questions, get synthesized answers
├─ kb_graph_tool          → Traverse dependency graph
├─ kb_impact_tool         → "What breaks if I change X?"
├─ kb_visualize_tool      → Generate mermaid/GraphML diagrams
├─ kb_code_location_tool  → "Where is the implementation of X?"
├─ kb_trace_flow_tool     → "How does data flow from A to B?"
├─ kb_find_pattern_tool   → "Find all uses of pattern X"
├─ kb_compare_tool        → "What changed between git refs?"
├─ kb_add_tool            → Add manual knowledge
├─ kb_populate_tool       → Full/partial re-ingest
├─ kb_stats_tool          → KB health metrics
└─ kb_reset_tool          → Reset (caution)

PILLAR 2: RESOURCES ─── Structured data exposed as virtual filesystem
│
│  scheme: "knowledge-base://"
│
├─ knowledge-base://project/tree           → Full project tree with metadata
├─ knowledge-base://project/summary        → One-paragraph project summary
├─ knowledge-base://arch/components        → All components with descriptions
├─ knowledge-base://arch/dependencies      → Dependency graph (JSON/DOT/Mermaid)
├─ knowledge-base://arch/layers            → Architecture layers with boundaries
├─ knowledge-base://arch/patterns          → Detected design patterns
├─ knowledge-base://flows/data             → End-to-end data flow paths
├─ knowledge-base://flows/control          → Call graphs / control flow
├─ knowledge-base://flows/imports          → Import/require dependency chains
├─ knowledge-base://api/endpoints          → All API endpoints (for web services)
├─ knowledge-base://api/public             → Public API surface
├─ knowledge-base://api/events             → Event/pub-sub channels
├─ knowledge-base://decisions              → Architecture Decision Records
├─ knowledge-base://config/settings        → Configuration surface
├─ knowledge-base://config/env             → Environment variables
├─ knowledge-base://code/entity/{id}       → Full details on one entity
├─ knowledge-base://code/search/{query}    → Semantic code search results
├─ knowledge-base://quality/complexity     → Cyclomatic complexity map
├─ knowledge-base://quality/coverage       → Test coverage map
├─ knowledge-base://quality/smells         → Code smell locations
├─ knowledge-base://session/context        → Current agent session context
└─ knowledge-base://health                 → KB health & staleness report

PILLAR 3: PROMPTS ─── Pre-built templates for common agent tasks
│
├─ onboard-agent          → "I'm new to this project. Explain it to me."
├─ find-entry-point       → "Where does this application start?"
├─ plan-feature           → "I need to add feature X. What do I modify?"
├─ trace-bug              → "Bug in Y. Trace the root cause."
├─ understand-flow        → "Explain how data flows from A to B."
├─ review-change          → "Review my planned changes for issues."
├─ find-similar           → "Find code similar to this pattern."
├─ write-test             → "Generate tests for module X."
├─ refactor-guide         → "Guide me through refactoring X."
└─ summarize-changes      → "Summarize what changed between refs."
```

### 4.3 File Directory Map

The v4 codebase introduces new directories alongside the existing `kb/` package.
Existing v3 modules remain in `kb/` for backward compatibility; new code lives
in the dedicated directories below.

```
mcp_servers/knowledge_base/
├── server.py              # MODIFIED: register new tools, resources, prompts
├── kb/                    # UNCHANGED: v3 modules (search, synthesis, store, etc.)
│   ├── api.py             # MINOR: expose new API functions for v4 tools
│   ├── models.py          # EXTENDED: add Entity, Relationship, Resource models
│   ├── ingest.py          # SUPERSEDED by analyzer/ but kept for backward compat
│   └── ...
├── analyzer/              # NEW: Phase 1 — Semantic Code Understanding Engine
│   ├── base.py            # LanguageBackend ABC
│   ├── python_ast.py      # Python semantic analyzer
│   ├── symbol_resolver.py # Cross-file symbol resolution
│   ├── relationships.py   # Relationship extractor
│   ├── patterns.py        # Design pattern detector (heuristic)
│   └── docstring.py       # Structured docstring parser
├── graph/                 # NEW: Phase 2 — Knowledge Graph
│   ├── engine.py          # NetworkX + SQLite persistence
│   ├── models.py          # Entity + Relationship dataclasses
│   ├── builder.py         # Build from analyzer output
│   ├── queries.py         # High-level query operations
│   ├── export.py          # JSON, GraphML, DOT, Mermaid
│   └── sync.py            # Incremental sync with git
├── resources/             # NEW: Phase 3 — MCP Resources Layer
│   ├── registry.py        # Resource registration + URI routing
│   ├── project.py         # Project-level resources
│   ├── arch.py            # Architecture resources
│   ├── flows.py           # Flow resources
│   ├── api.py             # API surface resources
│   ├── code.py            # Code entity resources
│   ├── quality.py         # Quality metric resources (v4.1)
│   ├── session.py         # Agent session context
│   └── exporters.py       # DOT, Mermaid, ASCII, JSON exporters
├── prompts/               # NEW: Phase 4 — MCP Prompts Layer
│   ├── registry.py        # Prompt registration + argument handling
│   ├── onboarding.py      # Onboarding prompts
│   ├── navigation.py      # Navigation prompts
│   ├── modification.py    # Feature/bug fix prompts
│   └── analysis.py        # Analysis prompts
├── learning/              # NEW: v4.1 — Continuous Learning (Phase 6)
│   ├── feedback.py        # Feedback store + processing
│   ├── gap_detector.py    # Knowledge gap detection
│   ├── incremental.py     # Incremental update from git diff
│   ├── staleness.py       # Staleness detection
│   └── session.py         # Agent session context
├── eval/                  # NEW: v4.1 — Evaluation & Quality Gates (Phase 7)
│   ├── metrics.py         # Quality metric implementations
│   ├── queries.py         # Standard test query suite
│   ├── reporter.py        # Quality report generator
│   └── benchmark.py       # Performance benchmark suite
├── backends/              # NEW: v4.1 — Multi-Language Backends (Phase 5)
│   └── ...                # Third-party backend install stubs
└── tests/
    ├── test_*.py          # Existing v3 tests (UNCHANGED)
    ├── test_analyzer_*.py # NEW: Phase 1 tests
    ├── test_graph_*.py    # NEW: Phase 2 tests
    └── ...
```

**Key integration points:**
- `server.py` imports from both `kb/` (v3) and new top-level packages (v4)
- `kb/models.py` is extended with `Entity`, `Relationship`, and `Resource` models
- The v3 `WorkspaceIngestor` remains for backward compat; the new analyzer pipeline
  is selected via an `analyzer_mode` parameter on `kb_populate_workspace_tool`
- The `quality.py` resource module is marked v4.1 because it depends on external
  tools (linters, coverage) not bundled with the KB

### 4.4 Performance Budget

| Scenario | Target | Measurement |
|----------|--------|-------------|
| Full ingest, small project (<500 files) | <30 seconds | CI benchmark |
| Full ingest, medium project (500–5000 files) | <3 minutes | CI benchmark |
| Full ingest, large project (5000–10000 files) | <10 minutes | CI benchmark |
| KB query response (any project) | <2 seconds | Automated |
| Graph traversal (depth=3) | <500ms | Automated |
| Graph → SQLite save | <3 seconds for 10k entities | Automated |
| SQLite → NetworkX load | <3 seconds for 10k entities | Automated |
| Resource URI read | <500ms | Automated |
| Prompt render (with data loading) | <3 seconds | Automated |

Exceeding any budget requires optimization before shipping. The primary strategy
is **single-pass analysis** (2 passes instead of 4 — see §5.2).

### 4.5 Dependency Audit

New dependencies required for v4, with version constraints and fallback behavior:

| Package | Version | Phase | Required? | Fallback |
|---------|---------|-------|-----------|----------|
| `networkx` | ≥3.0 | Phase 2 | Required | None — graph engine core |
| `jinja2` | ≥3.1 | Phase 4 | Required | None — prompt template engine |
| `pydantic` | ≥2.0 | Phase 1 | Required | Data models (already present in v3) |
| `tree-sitter` | ≥0.21 | Phase 5 | Optional (v4.1) | Regex heuristic backend |
| `pygraphviz` | ≥1.11 | Phase 3 | Optional | ASCII/Mermaid fallback for DOT export |
| `radon` | ≥6.0 | Phase 3 | Optional (v4.1) | Not included; `quality/*` resources deferred |
| `mypy` | ≥1.8 | Phase 1 | Optional | Type information deferred to LSP backend (v4.1) |

**Existing v3 dependencies** (unchanged): chromadb, sentence-transformers,
bm25s, anyio, mcp (FastMCP), typing_extensions.

---

## 5. Phase 1: Semantic Code Understanding Engine

**Goal**: Move from AST-level fact extraction to deep semantic understanding.

### 5.1 Current vs Target

| Aspect | Current (v3) | Target (v4) |
|--------|-------------|-------------|
| Python parsing | AST (classes, methods, functions) | AST + aliases + decorator semantics; **type inference deferred to LSP backend (v4.1)** |
| Docstring analysis | None | Structured docstring parsing (args, returns, raises, examples) |
| Type resolution | None | Cross-file symbol resolution; **full type graph deferred to LSP backend (v4.1)** |
| Relationship detection | None | Inheritance, composition, dependency injection, event hooks |
| Entry point detection | None | `main()`, `if __name__`, CLI entry points, app factories |
| Configuration surface | None | All config files, env vars, CLI args combined |
| Test mappings | None | Test → source code traceability |

### 5.2 Analyzer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  SEMANTIC CODE ANALYZER                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  AST Pass 1: Structure + Relationships + Semantics     │ │
│  │  (Single pass — collects everything from the AST)      │ │
│  │                                                         │ │
│  │  • Classes, functions, methods, variables              │ │
│  │  • Inheritance chain, import graph, call graph (static)│ │
│  │  • Type annotations, decorator semantics               │ │
│  │  • Mixin detection, async boundaries                   │ │
│  │  • Data flow (local scope)                             │ │
│  │  • Design pattern heuristics, framework conventions    │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  AST Pass 2: Cross-File Symbol Resolution              │ │
│  │  (Resolves references across files)                    │ │
│  │                                                         │ │
│  │  • Cross-file symbol tracking                          │ │
│  │  • Third-party vs internal boundary                    │ │
│  │  • Re-export chain resolution (__all__, index files)   │ │
│  │  • Relationship graph across file boundaries           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ⚡ Performance note: 2 passes instead of 4 reduces ingest  │
│     time by ~50% on large projects. Design pattern detection │
│     is heuristic (low confidence flagged in metadata).      │
│     Full type inference is deferred to LSP backend (v4.1).  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Knowledge Schema (Per Entity)

```json
{
  "entity_id": "...",
  "kind": "class | function | method | module | interface | config | test",
  "name": "Rag",
  "file_path": "src/agentx/model/rag/rag.py",
  "line_start": 21,
  "line_end": 67,
  "docstring": {
    "summary": "Main RAG orchestrator connecting ingestion, ChromaDB, and LLM query",
    "args": [],
    "returns": null
  },
  "relationships": {
    "imports": [
      {"target": "agentx.model.ai.service.AIService", "kind": "direct"},
      {"target": "agentx.model.rag.rag_db.RagDatabase", "kind": "direct"}
    ],
    "inherits_from": [],
    "composes": [
      {"target": "RagDatabase", "field": "rag_db", "kind": "composition"},
      {"target": "RagQuery", "field": "rag_query", "kind": "composition"}
    ],
    "instantiated_by": [
      {"source": "RagController", "kind": "direct_instantiation"}
    ],
    "called_by": [],
    "calls": [
      {"target": "RagQuery.ask", "kind": "method_call"},
      {"target": "WebIngestionApp.run", "kind": "method_call"}
    ]
  },
  "semantics": {
    "layer": "model",
    "pattern": ["facade", "orchestrator"],
    "stability": "core",
    "test_coverage": {"has_test": true, "test_file": "tests/test_rag.py"}
  },
  "metadata": {
    "confidence": 0.97,
    "language": "python",
    "created_at": "...",
    "git_last_modified": "...",
    "git_author": "..."
  }
}
```

### 5.4 Deliverables

| Module | Description | Files | Release |
|--------|-------------|-------|---------|
| `analyzer/__init__.py` | Analyzer registry, plugin loader | 1 | v4.0 |
| `analyzer/python_ast.py` | Python semantic analyzer (AST + patterns) | 1 | v4.0 |
| `analyzer/base.py` | Abstract base for language backends | 1 | v4.0 |
| `analyzer/symbol_resolver.py` | Cross-file symbol resolution | 1 | v4.0 |
| `analyzer/patterns.py` | Design pattern detector (heuristic) | 1 | v4.0 |
| `analyzer/relationships.py` | Relationship extractor | 1 | v4.0 |
| `analyzer/docstring.py` | Structured docstring parser | 1 | v4.0 |
| `models/semantic.py` | Semantic entity + relationship models | 1 | v4.0 |

**Tests**: ~40 unit tests, ~10 integration tests (v4.0)

---

## 6. Phase 2: Knowledge Graph

**Goal**: Transform flat KB entries into a navigable graph of entities and relationships.

### 6.1 Why a Graph

A vector DB (ChromaDB) is great for **semantic similarity search** but terrible for:

- "What does Module A depend on?" → Needs graph traversal
- "What breaks if I delete this function?" → Needs dependency chain
- "Show me the full call chain from main() to this function" → Needs graph path
- "Which tests cover this class?" → Needs relationship traversal

The solution: **Dual storage** — ChromaDB for vector search + lightweight graph store for relationships.

### 6.2 Graph Model

```
┌──────────────────┐          ┌────────────────────┐
│    ENTITY        │          │    RELATIONSHIP     │
├──────────────────┤          ├────────────────────┤
│ • id: str        │─────────►│ • source_id: str   │
│ • kind: str      │   has    │ • target_id: str   │
│ • name: str      │          │ • kind: str         │
│ • file_path: str │          │ • weight: float     │
│ • doc: str       │          │ • metadata: dict    │
│ • metadata: dict │          └────────────────────┘
└──────────────────┘

RELATIONSHIP KINDS:
  imports         → Module A imports Module B
  extends         → Class A extends Class B
  implements      → Class A implements Interface B
  composes        → Class A has-a Class B
  calls           → Function A calls Function B
  creates         → Function A instantiates Class B
  passes_to       → Function A passes type to Function B
  defines         → Module defines Class/Function
  tests           → Test file tests source file
  configures      → Config file sets value for module
  routes          → URL route maps to handler
  emits_event     → Function emits event E
  listens_event   → Function listens for event E
  deco_related    → Decorator A is applied to Class/Function B
```

### 6.3 Graph Engine Options

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **NetworkX** | Zero deps, pure Python, full graph algorithms | In-memory only, no persistence | ✅ **Primary** for small-medium projects |
| **SQLite + adjacency** | Persistent, no deps | Query complexity, no graph algorithms out of box | ✅ **Secondary** for persistence layer |
| **Neo4j embedded** | Full graph DB, Cypher queries | Heavy dependency, 100MB+ | ❌ Overkill for most projects |
| **JSON + indices** | Simple, portable | Slow for large graphs | ⚠️ Fallback for minimal deps |

**Design Decision**: Use NetworkX as the in-memory query engine with SQLite for persistence. Export/import from JSON for portability.

### 6.4 Graph Query API

```python
# Find all callers of a function
graph.traverse(target_id="Rag.query", direction="incoming", relationship="calls")

# Find the shortest dependency path between two modules
graph.find_path(source="rag.py", target="llm.py")

# Find all tests related to a class
graph.find_related(entity_id="Rag", relationship_kind="tests")

# Find all entities in a layer
graph.filter(layer="model")

# Find circular dependencies
graph.find_cycles()

# Compute change impact
graph.impact_analysis(entity_id="RagDatabase", depth=3)
```

### 6.5 Deliverables

| Module | Description | Files | Release |
|--------|-------------|-------|---------|
| `graph/engine.py` | Graph engine (NetworkX + SQLite persistence) | 1 | v4.0 |
| `graph/models.py` | Entity + Relationship dataclasses | 1 | v4.0 |
| `graph/builder.py` | Build graph from analyzer output | 1 | v4.0 |
| `graph/queries.py` | High-level query operations | 1 | v4.0 |
| `graph/export.py` | Export to JSON, GraphML, DOT, Mermaid | 1 | v4.0 |
| `graph/sync.py` | Incremental sync with git changes | 1 | v4.0 |

**Tests**: ~30 unit tests, ~10 integration tests

**Design constraints:**
- **Hydration budget:** SQLite → NetworkX load for 10k entities must complete
  in <3 seconds. If exceeded, implement lazy-loading (load on traversal request).
- **Transactional consistency:** Graph writes go to SQLite first. If ChromaDB
  write fails, the graph entry is marked `pending_chromadb` for reconciliation.
  A periodic job (every 1000 writes) reconciles pending entries.

---

## 7. Phase 3: MCP Resources Layer

**Goal**: Expose project knowledge as a virtual filesystem that agents can browse.

### 7.1 What Are MCP Resources?

MCP Resources let a server expose data as `scheme://path` URIs that agents
can read like files. This is fundamentally different from tools:

| Aspect | Tools | Resources |
|--------|-------|-----------|
| Invocation | Agent calls explicitly | Agent reads like a file |
| Parameters | Full parameter set | Implicit in the URI path |
| Caching | Per-call | Can be cached and watched |
| Use case | Actions ("do something") | Data ("show me something") |
| Discovery | Listed in tools list | Listed in resources list |

### 7.2 Virtual Filesystem Structure

```
knowledge-base://
│
├── project/
│   ├── tree                    → Full directory tree with entity annotations
│   ├── summary                 → One-paragraph AI-generated project summary
│   └── metadata                → Language, framework, package manager, deps
│
├── arch/
│   ├── components              → List of all components with descriptions
│   ├── dependencies            → Full dependency graph (DOT or JSON)
│   ├── dependencies.dot        → Graphviz DOT format
│   ├── dependencies.mermaid    → Mermaid.js format
│   ├── layers                  → Architecture layers (model/view/controller/etc)
│   ├── layers.dot              → Layer diagram in DOT
│   ├── patterns                → Detected design patterns with locations
│   └── decisions               → Architecture Decision Records
│
├── flows/
│   ├── data                    → End-to-end data flow descriptions
│   ├── control                 → Main call chains
│   ├── imports                 → Import/require hierarchy
│   └── events                  → Event/pub-sub channels
│
├── api/
│   ├── endpoints               → All endpoints (for web/API projects)
│   ├── public                  → Public API surface
│   ├── events                  → Event definitions
│   └── config                  → Configuration surface & env vars
│
├── code/
│   ├── entity/{id}             → Full entity details with relationships
│   ├── search/{query}          → Semantic code search results
│   ├── file/{path}             → Annotated file view
│   └── recent                  → Recently modified entities
│
├── quality/
│   ├── complexity              → Cyclomatic complexity hotspots
│   ├── coverage                → Test coverage gaps
│   └── smells                  → Code smells and anti-patterns
│
├── session/
│   └── context                 → Current agent session accumulated context
│
└── health                      → KB health: coverage, staleness, confidence
```

### 7.3 Resource Template System

Each resource path maps to a **resource template** that generates content
dynamically. Templates produce content in multiple formats:

```
knowledge-base://arch/dependencies           → JSON (default)
knowledge-base://arch/dependencies?format=dot  → DOT graph format
knowledge-base://arch/dependencies?format=mermaid → Mermaid format
knowledge-base://arch/dependencies?format=ascii  → ASCII art for CLI agents
```

### 7.4 Resource Implementation

```python
# Conceptual implementation
@mcp.resource("knowledge-base://arch/dependencies")
def get_dependency_graph(format: str = "json") -> str:
    graph = knowledge_graph.get_full_graph()
    if format == "dot":
        return export_dot(graph)
    elif format == "mermaid":
        return export_mermaid(graph)
    elif format == "ascii":
        return export_ascii_tree(graph)
    return export_json(graph)

@mcp.resource_template("knowledge-base://code/entity/{entity_id}")
def get_entity(entity_id: str) -> str:
    entity = knowledge_graph.get_entity(entity_id)
    if not entity:
        return json.dumps({"error": "Entity not found"})
    relationships = knowledge_graph.get_relationships(entity_id)
    return json.dumps({
        "entity": entity,
        "relationships": relationships
    })
```

### 7.5 Benefits Over Current Approach

| Scenario | Current (v3) | With Resources (v4) |
|----------|-------------|---------------------|
| Agent wants to understand architecture | Must ask multiple `kb_ask_tool` calls | Reads `knowledge-base://arch/layers` like a file |
| Agent needs to know all entry points | Must search "main" or "entry" | Reads `knowledge-base://arch/components` |
| Agent exploring dependencies | Must trace manually via grep | Reads `knowledge-base://flows/imports` |
| Agent checking test coverage | Must search test files | Reads `knowledge-base://quality/coverage` |
| Agent needs a diagram | Must reason from text | Gets ready-to-render Mermaid/DOT |

### 7.6 Deliverables

| Module | Description | Files |
|--------|-------------|-------|
| `resources/registry.py` | Resource registration + URI routing | 1 |
| `resources/project.py` | Project-level resources | 1 |
| `resources/arch.py` | Architecture resources (components, deps, layers) | 1 |
| `resources/flows.py` | Data/control flow resources | 1 |
| `resources/api.py` | API surface resources | 1 |
| `resources/code.py` | Code entity resources | 1 |
| `resources/quality.py` | Quality metrics resources | 1 |
| `resources/session.py` | Agent session context | 1 |
| `resources/exporters.py` | DOT, Mermaid, ASCII, JSON exporters | 1 |

**Tests**: ~25 unit tests, ~10 integration tests

---

## 8. Phase 4: MCP Prompts Layer

**Goal**: Provide pre-built prompt templates that guide agents through common tasks.

### 8.1 What Are MCP Prompts?

MCP Prompts are **reusable prompt templates** that the server exposes.
The agent can load them and use them as starting points for complex tasks.

```
┌──────────────────────────────────────────────────────────────┐
│                    MCP PROMPT CONTRACT                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Server defines:                      Agent uses:            │
│  ┌──────────────────────┐            ┌────────────────────┐ │
│  │ Name: "onboard-agent"│            │ "Load the          │ │
│  │ Arguments: none      │───────────►│  onboard-agent     │ │
│  │ Template: "..."      │            │  prompt"           │ │
│  └──────────────────────┘            └────────────────────┘ │
│                                                              │
│  Result: Agent receives a structured prompt with placeholders│
│  filled in with live KB data.                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 8.2 Prompt Catalog

```yaml
onboard-agent:
  description: "I'm new to this project. Explain it to me."
  arguments: []
  template: |
    # Project Overview

    {{ project_summary }}

    ## Architecture

    {{ arch_layers }}

    ## Key Components

    {{ key_components }}

    ## Entry Points

    {{ entry_points }}

    ## How to Navigate

    The KB exposes these resources to help you:
    - `knowledge-base://arch/components` — all components
    - `knowledge-base://flows/data` — data flow
    - `knowledge-base://api/endpoints` — API surface

    Suggested first steps:
    1. Read `knowledge-base://project/tree`
    2. Read `knowledge-base://arch/dependencies`
    3. Ask a specific question via `kb_query_tool`

find-entry-point:
  description: "Where does this application start?"
  arguments: []
  template: |
    # Entry Points

    {{ entry_points_detailed }}

    ## Main Flow

    ```mermaid
    {{ main_flow_diagram }}
    ```

plan-feature:
  description: "I need to add feature X. What do I modify?"
  arguments:
    - name: feature_description
      description: "Brief description of the feature"
      required: true
  template: |
    # Feature Plan: {{ feature_description }}

    ## Related Components

    {{ related_components }}

    ## Suggested Modification Order

    1. {{ step_1 }}
    2. {{ step_2 }}
    ...

    ## Files Likely Affected

    {{ affected_files }}

    ## Tests to Update

    {{ related_tests }}

    ## Impact Analysis

    {{ impact_summary }}

trace-bug:
  description: "Bug in Y. Trace the root cause."
  arguments:
    - name: symptom
      description: "What's the bug symptom?"
      required: true
  template: |
    # Bug Trace: {{ symptom }}

    ## Potential Root Cause Paths

    {{ trace_paths }}

    ## Relevant Code Paths

    {{ code_paths }}

    ## Suggested Investigation Order

    1. {{ investigation_step_1 }}
    ...

understand-flow:
  description: "Explain how data flows from A to B."
  arguments:
    - name: source
      description: "Starting point"
      required: true
    - name: target
      description: "End point"
      required: true
  template: |
    # Data Flow: {{ source }} → {{ target }}

    ## Flow Path

    {{ flow_path }}

    ## Key Functions

    {{ key_functions }}

    ## Diagram

    ```mermaid
    {{ flow_diagram }}
    ```
```

### 8.3 Prompt Benefits for Agents

| Benefit | Explanation |
|---------|------------|
| **Reduced token waste** | Agent doesn't need to figure out *how* to ask — the prompt guides it |
| **Consistent depth** | Every agent gets the same thorough onboarding |
| **Live data** | Prompts are filled with up-to-date KB data, not static text |
| **Just-in-time** | Load a prompt when you need it, not before |
| **Language-agnostic** | Same prompts work for any project |

### 8.4 Deliverables

| Module | Description | Files |
|--------|-------------|-------|
| `prompts/registry.py` | Prompt registration + argument handling | 1 |
| `prompts/onboarding.py` | Onboarding prompts | 1 |
| `prompts/navigation.py` | Navigation prompts | 1 |
| `prompts/modification.py` | Feature/bug fix prompts | 1 |
| `prompts/analysis.py` | Analysis prompts (flow, impact, change) | 1 |

**Tests**: ~15 unit tests

---

## 9. Phase 5: Multi-Language Support (v4.1 Advanced)

**Goal**: Support any programming language via pluggable backends.

### 9.1 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   LANGUAGE BACKEND REGISTRY                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Each backend implements:                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ class LanguageBackend(ABC):                            │ │
│  │     @abstractmethod                                    │ │
│  │     def analyze_file(self, path: Path) -> List[Entity]:│ │
│  │     @abstractmethod                                    │ │
│  │     def analyze_project(self, root: Path) -> Project:  │ │
│  │     @property                                          │ │
│  │     def supported_extensions(self) -> set[str]:        │ │
│  │     @property                                          │ │
│  │     def confidence(self) -> float:                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌────────┐ ┌──────┐  │
│  │ Python   │ │ JS/TS    │ │ Rust   │ │ Go     │ │ ...  │  │
│  │ (builtin)│ │ (tree-   │ │ (syn + │ │ (gop   │ │ (LSP │  │
│  │          │ │  sitter) │ │  ra_ap)│ │  ast)  │ │  ext) │  │
│  └──────────┘ └──────────┘ └────────┘ └────────┘ └──────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 9.2 Backend Methods

Each backend can use one or more strategies:

| Strategy | Quality | Performance | Dependency | Use Case |
|----------|---------|-------------|------------|----------|
| **AST parser** | High | Fast | Language-specific lib | Python, JS/TS, Go, Rust |
| **Tree-sitter** | High | Fast | tree-sitter lib | Any language with grammar |
| **LSP proxy** | Very High | Medium | LSP server | Best-effort understanding |
| **Regex heuristic** | Low | Very fast | None | Quick scan, unknown langs |
| **LLM-assisted** | Very High | Slow | LLM API | Deep understanding fallback |

### 9.3 Strategy: Language Detection

```yaml
python:
  extensions: [.py, .pyi, .pyx]
  backend: python_ast
  config_files: [setup.py, pyproject.toml, requirements.txt, Pipfile]

javascript:
  extensions: [.js, .jsx, .mjs]
  backend: tree_sitter
  config_files: [package.json]

typescript:
  extensions: [.ts, .tsx]
  backend: tree_sitter
  config_files: [tsconfig.json, package.json]

rust:
  extensions: [.rs]
  backend: syn_parser
  config_files: [Cargo.toml]

go:
  extensions: [.go]
  backend: go_ast
  config_files: [go.mod]

java:
  extensions: [.java]
  backend: tree_sitter
  config_files: [pom.xml, build.gradle]

ruby:
  extensions: [.rb]
  backend: tree_sitter
  config_files: [Gemfile]

c_cpp:
  extensions: [.c, .h, .cpp, .hpp]
  backend: tree_sitter
  config_files: [CMakeLists.txt, Makefile]
```

### 9.5 Deliverables

| Module | Description | Files |
|--------|-------------|-------|
| `analyzer/registry.py` | Language → backend mapping | 1 |
| `analyzer/base.py` | `LanguageBackend` ABC | 1 |
| `analyzer/python_ast.py` | Python AST backend | 1 |
| `analyzer/tree_sitter.py` | Generic tree-sitter backend | 1 |
| `analyzer/lsp_proxy.py` | LSP-based backend | 1 |
| `analyzer/heuristic.py` | Regex fallback backend | 1 |
| `analyzer/language_detect.py` | Language detection from files | 1 |
| `backends/` | Third-party backend install stubs | 1 |

**Tests**: ~20 unit tests, ~15 integration tests (multi-language)

---

## 10. Phase 6: Continuous Learning & Self-Healing (v4.1 Advanced)

**Goal**: KB improves itself over time based on agent interactions and code changes.

### 10.1 Gap-Driven Ingestion (v4.1)

> ⚠️ **Release note:** This phase ships in **v4.1 Advanced**. The v4.0 Core
> release logs failed queries for analysis but does not auto-heal.

```
Agent asks question
        │
        ▼
   KB query
        │
        ├── High confidence answer (>0.8) → Return answer
        │
        └── Low confidence answer (<0.6) or empty
                │
                ├── 1. Log the failed query
                │
                ├── 2. Keyword extraction & entity guessing
                │    Extract key terms from the failed query using
                │    TF-IDF or simple noun-phrase extraction.
                │    Map terms to likely entity names (capitalized words,
                │    dotted paths like "Rag.query", file paths).
                │    Search source file names and content for matches.
                │
                ├── 3. Targeted ingestion of candidate files
                │    For each candidate entity name:
                │    a. Search workspace for files containing that name
                │    b. Run semantic analysis only on those files
                │    c. Re-index into KB + graph
                │    Limit: max 20 files per gap-fill cycle to avoid
                │    runaway ingestion.
                │
                ├── 4. Re-query KB with original question
                │
                └── Still failing (< 0.6)?
                    └── Log as "confirmed gap" for manual review.
                        Optionally ask user: "KB couldn't answer this.
                        Would you like me to analyze the code
                        and add this knowledge?"
```

**Design notes:**
- Step 2 uses **keyword overlap** (query terms × entity names) rather than
  semantic understanding — this is intentionally simple and avoids circular
  dependency (needing a working KB to fix the KB).
- Step 3 has a **guard limit** (20 files) to prevent accidental full re-ingest.
- The gap detector is **opt-in** in v4.1; in v4.0 only logging occurs.

### 10.2 Incremental Updates

```
Git post-commit hook / polling:
        │
        ▼
   git diff HEAD~1
        │
        ├── New files      → Run semantic analysis on them
        ├── Modified files → Re-analyze + update graph relationships
        ├── Deleted files  → Remove entities from graph + KB
        └── No changes     → Skip
                │
                ▼
        Update knowledge graph incrementally
                │
                ▼
        Mark affected synthesized answers as "stale"
                │
                ▼
        Optionally: regenerate summaries
```

### 10.3 Feedback Loop

```python
@mcp.tool()
def kb_feedback_tool(
    query_id: str,
    rating: int,  # 1-5
    correct_answer: Optional[str] = None,
) -> str:
    """
    Provide feedback on a KB answer.

    Args:
        query_id: The ID returned by a previous kb_query_tool call
        rating: 1 (useless) to 5 (perfect)
        correct_answer: Optional correction if the answer was wrong

    Returns:
        Confirmation + improvement actions taken
    """
    # 1. Store feedback in feedback store
    # 2. If rating < 3 and correct_answer given:
    #    - Extract key entities from correct answer
    #    - Search KB for related content
    #    - If missing: add as manual entry
    #    - If present but not retrieved: adjust ranking parameters
    # 3. If rating >= 4:
    #    - Boost confidence of used sources
    #    - Record as positive example for future synthesis
```

### 10.4 Staleness Detection

```python
staleness_algorithm:
  for each entity in graph:
    git_last_modified = get_git_mtime(entity.file_path)
    kb_last_updated = entity.metadata.created_at
    
    if git_last_modified > kb_last_updated:
      entity.status = "stale"
      schedule_reanalysis()

    if git_last_modified - kb_last_updated > 30 days:
      entity.status = "stale"
      schedule_reanalysis()

  for each synthesized_answer:
    if any(its_source_entities are "stale"):
      synthesized_answer.status = "maybe_stale"
```

### 10.5 Deliverables (v4.1)

| Module | Description | Files | Release |
|--------|-------------|-------|---------|
| `learning/feedback.py` | Feedback store + processing | 1 | v4.1 |
| `learning/gap_detector.py` | Knowledge gap detection (keyword-based) | 1 | v4.1 |
| `learning/incremental.py` | Incremental update from git diff | 1 | v4.1 |
| `learning/staleness.py` | Staleness detection + re-analysis scheduler | 1 | v4.1 |
| `learning/session.py` | Agent session context management | 1 | v4.1 |
| `feedback_store.sql` | SQLite schema for feedback storage | 1 | v4.1 |

**Tests**: ~20 unit tests

> **v4.0 note:** Failed query logging is implemented in v4.0 Core even though
> auto-healing is not. The `gap_detector.py` stub in v4.0 only logs; the full
> ingestion pipeline is activated in v4.1.

---

## 11. Phase 7: Evaluation & Quality Gates (v4.1 Advanced)

**Goal**: Quantify how well the KB serves agents.

### 11.1 Quality Metrics

| Metric | Current (v3) | Target (v4) | How to Measure |
|--------|-------------|-------------|----------------|
| **Answer depth** | Filename + line number | Architecture + flow + rationale | Human evaluation of query answers |
| **Relationship coverage** | 0% | >80% of all relationships | % of known deps captured in graph |
| **Multi-hop accuracy** | N/A | >70% | Agent can trace 3+ hop chains |
| **Query success rate** | ~60% (structural only) | >90% | % of queries with conf > 0.7 |
| **Agent task efficiency** | Baseline | 2x faster | Time to complete standard tasks |
| **Cross-language support** | Python only | 6+ languages | Number of detected languages |
| **Self-heal rate** | 0% | >50% | % of detected gaps auto-filled |

### 11.2 Quality Gate Suite

```python
# ⚠️ Gates are labeled v4.0 or v4.1 by release.
# v4.0 gates are mandatory before shipping Core.

# ── v4.0 CORE ─────────────────────────────────────────────────

GATE A — COMPLETENESS (v4.0)
  Expected: ≥ 85% of source files have entity entries
  Files found: {N}
  Source files: {M}
  Status: PASS / FAIL

GATE B — RELATIONSHIP DENSITY (v4.0, project-type aware)
  Expected: ≥ threshold depending on project archetype
    Application (web/service): ≥ 1.5 relationships/entity
    Library/CLI: ≥ 0.8 relationships/entity
    Small (< 20 files): no minimum (density warning only)
  Actual: {mean_relations}
  Status: PASS / WARN / FAIL

GATE C — QUERY COHERENCE (v4.0)
  Expected: ≥ 75% of Level 1–2 test queries return conf > 0.7
  Test queries: {list}
  Pass rate: {rate}
  Status: PASS / FAIL

GATE D — GRAPH INTEGRITY (v4.0)
  Expected: 0 unintended circular dependencies at module level
    (Explicitly skip well-known intentional patterns: event loops,
    bidirectional protocols, plugin systems — flag as INFO not FAIL.)
  Cycles found: {N}
  Status: PASS / WARN / FAIL

# ── v4.1 ADVANCED ──────────────────────────────────────────────

GATE E — MULTI-LANGUAGE (v4.1)
  Expected: ≥ 90% of detected language files analyzed
  Languages: {list}
  Coverage: {rate}%
  Status: PASS / FAIL

GATE F — STALENESS (v4.1)
  Expected: < 10% of entities stale
  Stale: {N}/{Total}
  Status: PASS / FAIL
```

### 11.3 Test Query Suite (Universal)

These queries should work for ANY project:

```
Level 1 — Structural:
  "What are the main modules/components?"
  "Where is the entry point?"
  "What classes are in module X?"

Level 2 — Relational:
  "What does module X depend on?"
  "What depends on class Y?"
  "Show the inheritance chain for class Z"

Level 3 — Flow:
  "How does data flow from input to output?"
  "What happens when the user calls endpoint X?"
  "Trace the call chain from main() to function Y"

Level 4 — Semantic:
  "What architecture pattern does this project use?"
  "Where should I add feature X?"
  "What's the test coverage for module Y?"
  "Find all places where config is loaded"

Level 5 — Impact:
  "What breaks if I remove function X?"
  "What's the blast radius of changing class Y?"
  "Which tests need updating for change Z?"
```

### 11.4 Deliverables (v4.1)

| Module | Description | Files | Release |
|--------|-------------|-------|---------|
| `eval/metrics.py` | All quality metric implementations | 1 | v4.1 |
| `eval/queries.py` | Standard test query suite | 1 | v4.1 |
| `eval/reporter.py` | Quality report generator | 1 | v4.1 |
| `eval/benchmark.py` | Performance benchmark suite | 1 | v4.1 |

**Tests**: ~15 unit tests, ~5 integration tests

---

## 12. MCP Tool Reference

### 12.1 Existing Tools (Upgraded)

| Tool | Current | v4 Upgrade |
|------|---------|------------|
| `kb_search_tool` | Text-only search | + structured JSON output option, + graph context |
| `kb_ask_tool` | Template/LLM synthesis | + depth parameter (structural/relational/semantic), + session context |
| `kb_add_tool` | Manual entry add | + relationship specification, + batch mode |
| `kb_stats_tool` | Basic counts | + quality gate results, + gap analysis |
| `kb_populate_workspace_tool` | Full scan only | + incremental mode, + language-specific, + watch mode |
| `kb_reset_tool` | Full reset | + selective reset (per-language, per-category) |
| `kb_list_categories` | Static list | + dynamic categories from project |

### 12.2 New Tools — Operation Specs

Each tool includes MCP-compatible JSON Schema parameter constraints, OMT++-style
pre/post conditions, and known error cases.

```yaml
kb_graph_tool:
  summary: "Query the project's knowledge graph."
  phase: "v4.0 Core"
  operation_spec:
    preconditions:
      - Knowledge graph must be populated (kb_populate_workspace_tool run)
      - Referenced entity_id must exist in graph (if provided)
    postconditions:
      - Read-only; no side effects
      - Returns structured JSON with entities and relationships
    parameters:
      operation:
        type: string
        required: true
        enum: ["traverse", "find_path", "filter", "cycles", "impact"]
        description: "Graph operation to perform"
      entity_id:
        type: string
        description: "Start entity for traverse/find_path/impact"
      relationship_kind:
        type: string
        enum: ["imports", "extends", "implements", "composes", "calls",
               "creates", "passes_to", "defines", "tests", "configures",
               "routes", "emits_event", "listens_event", "deco_related"]
        description: "Filter by relationship type"
      depth:
        type: integer
        default: 2
        minimum: 1
        maximum: 10
        description: "Traversal depth"
      direction:
        type: string
        enum: ["incoming", "outgoing", "both"]
        default: "both"
        description: "Edge direction"
    error_cases:
      - entity_id not found → return {"error": "Entity not found", "code": 404}
      - operation unknown → return {"error": "Unknown operation", "code": 400}
  returns: "JSON object with entities[] and relationships[]"

kb_impact_tool:
  summary: "Analyze change impact for an entity."
  phase: "v4.0 Core"
  operation_spec:
    preconditions:
      - Entity must exist in knowledge graph
    postconditions:
      - No side effects
      - Returns transitive closure of affected entities up to depth
    parameters:
      entity_id:
        type: string
        required: true
        description: "Entity being changed"
      change_type:
        type: string
        required: true
        enum: ["modify", "delete", "rename"]
      depth:
        type: integer
        default: 3
        minimum: 1
        maximum: 10
    error_cases:
      - entity_id not found → return {"error": "Entity not found", "code": 404}
      - change_type invalid → return {"error": "Invalid change_type", "code": 400}
  returns: "JSON with affected entities, risk levels, and test files"

kb_visualize_tool:
  summary: "Generate a diagram from KB data."
  phase: "v4.0 Core"
  operation_spec:
    preconditions:
      - Knowledge graph populated
      - pygraphviz is optional; fallback to ASCII/Mermaid if absent
    postconditions:
      - No side effects
      - Returns diagram string in requested format
    parameters:
      view:
        type: string
        required: true
        enum: ["dependencies", "layers", "dataflow", "inheritance", "callgraph"]
      format:
        type: string
        default: "mermaid"
        enum: ["mermaid", "dot", "ascii", "json"]
        description: "Output format"
      root:
        type: string
        description: "Optional root entity to scope the diagram"
      depth:
        type: integer
        default: 2
        minimum: 1
        maximum: 10
    error_cases:
      - view unknown → fallback to "dependencies"
      - format unsupported → return error with supported formats list
  returns: "String in requested format"

kb_trace_flow_tool:
  summary: "Trace data flow between two entities."
  phase: "v4.0 Core"
  operation_spec:
    preconditions:
      - Both source and target entities exist in graph
    postconditions:
      - No side effects
      - Returns shortest path through call/compose/import relationships
    parameters:
      source:
        type: string
        required: true
        description: "Starting entity ID or file path"
      target:
        type: string
        required: true
        description: "Ending entity ID or file path"
      max_depth:
        type: integer
        default: 10
        minimum: 1
        maximum: 50
    error_cases:
      - source/target not found → return partial path with missing segment noted
      - no path found at max_depth → return empty path with nearest intermediate
  returns: "JSON with ordered flow path + key functions"

kb_code_location_tool:
  summary: "Find the exact location and context of code."
  phase: "v4.0 Core"
  operation_spec:
    preconditions:
      - Project has been ingested into KB
    postconditions:
      - No side effects
      - Returns exact file/line/code
    parameters:
      symbol:
        type: string
        required: true
        description: "Fully qualified symbol name (e.g., module.ClassName.method)"
      include_code:
        type: boolean
        default: false
        description: "Whether to include source lines in response"
      context_lines:
        type: integer
        default: 5
        minimum: 0
        maximum: 50
    error_cases:
      - symbol not found → return similar symbols with edit distance ≤ 3
  returns: "File path, line range, code snippet, relationships"

kb_find_pattern_tool:
  summary: "Find code matching a structural or design pattern."
  phase: "v4.1 Advanced"
  operation_spec:
    preconditions:
      - Project ingested; patterns analyzed (Phase 1)
    postconditions:
      - No side effects
      - Results are heuristic — low confidence patterns are flagged
    parameters:
      pattern:
        type: string
        required: true
        enum: ["singleton", "factory", "observer", "mvc", "repository",
               "facade", "adapter", "strategy", "command", "decorator"]
        description: "Design pattern to search for"
      language:
        type: string
        description: "Optional language filter (e.g., python, typescript)"
        enum: ["python", "typescript", "javascript", "rust", "go", "java", "ruby"]
    error_cases:
      - pattern not recognized → return available patterns list
      - pattern detected with low confidence → include confidence in results
  returns: "All locations implementing the pattern with confidence scores"

kb_compare_tool:
  summary: "Compare KB state between git references."
  phase: "v4.0 Core"
  operation_spec:
    preconditions:
      - Working directory is a git repository
      - KB has been populated at least once
    postconditions:
      - No side effects
      - Git diff is cached for efficiency
    parameters:
      from_ref:
        type: string
        default: "HEAD~1"
        description: "Git ref A (start of comparison)"
      to_ref:
        type: string
        default: "HEAD"
        description: "Git ref B (end of comparison)"
    error_cases:
      - git ref not found → return error with available refs
      - not a git repo → return error
  returns: "List of added, removed, modified entities"

kb_feedback_tool:
  summary: "Rate a KB answer to improve future results."
  phase: "v4.1 Advanced"
  operation_spec:
    preconditions:
      - query_id must correspond to a previous kb_ask_tool response
    postconditions:
      - Stores feedback in feedback store (SQLite)
      - If rating < 3 and correct_answer provided: triggers re-index
      - If rating >= 4: boosts confidence of used sources
    parameters:
      query_id:
        type: string
        required: true
        description: "ID from kb_ask_tool response"
      rating:
        type: integer
        required: true
        minimum: 1
        maximum: 5
        description: "1 (useless) to 5 (perfect)"
      correct_answer:
        type: string
        description: "Optional correction if the answer was wrong"
    error_cases:
      - query_id not found → return error with recent query IDs
      - rating out of range → return error
  returns: "Improvement actions taken"

kb_session_tool:
  summary: "Manage agent session context."
  phase: "v4.0 Core"
  operation_spec:
    preconditions:
      - Session initialized on first tool call
    postconditions:
      - "set": stores key-value in session store
      - "clear": removes all session state
      - "summarize": returns context summary (no side effects)
    parameters:
      action:
        type: string
        required: true
        enum: ["get", "set", "clear", "summarize"]
      key:
        type: string
        description: "Context key (required for get/set)"
      value:
        type: string
        description: "Context value (required for set)"
    error_cases:
      - get with missing key → return null (not error)
      - set with missing key or value → return error
  returns: "Session state or confirmation"
```

---

## 13. MCP Resource Reference

### 13.1 Resource URI Scheme

```
knowledge-base://<category>/<path>[?format=<fmt>]
```

### 13.2 Complete Resource Table

| URI | Description | Formats | Dynamic? | Release | Data Source |
|-----|-------------|---------|----------|---------|------------|
| `project/tree` | Full project tree with annotations | json, ascii | No | v4.0 | Filesystem walk |
| `project/summary` | AI-generated project overview | markdown | Regenerated on change | v4.0 | KB synthesis |
| `project/metadata` | Language, framework, deps | json | No | v4.0 | Config file parser |
| `arch/components` | All components/entities | json, mermaid, ascii | No | v4.0 | Knowledge graph |
| `arch/dependencies` | Dependency graph | json, dot, mermaid, ascii | No | v4.0 | Knowledge graph |
| `arch/layers` | Architecture layers | json, mermaid, ascii | No | v4.0 | Knowledge graph |
| `arch/patterns` | Design patterns detected | json, markdown | No | v4.0 | Analyzer (heuristic) |
| `arch/decisions` | Architecture Decision Records | markdown | No | v4.0 | Manual/user entries |
| `flows/data` | End-to-end data flow | json, mermaid, ascii | Per query | v4.0 | Graph traversal |
| `flows/control` | Main call chains | json, mermaid, ascii | Per query | v4.0 | Graph traversal |
| `flows/imports` | Import dependency chains | json, dot, ascii | No | v4.0 | Knowledge graph |
| `flows/events` | Event/pub-sub channels | json | No | v4.1 | Analyzer (event detect) |
| `api/endpoints` | API endpoints | json, markdown | No | v4.0 | Framework convention |
| `api/public` | Public API surface | json, markdown | No | v4.0 | Symbol visibility |
| `api/config` | Configuration surface | json, markdown | No | v4.0 | Config file parser |
| `code/entity/{id}` | Entity details | json | Per entity | v4.0 | Knowledge graph |
| `code/search/{query}` | Semantic code search | json | Per query | v4.0 | KB vector search |
| `code/file/{path}` | Annotated file | markdown | Per file | v4.0 | Source + KB metadata |
| `code/recent` | Recently changed entities | json | No | v4.0 | Git log |
| `quality/complexity` | Complexity hotspots | json, markdown | No | v4.1 | External tool (radon etc.) |
| `quality/coverage` | Test coverage map | json, markdown | No | v4.1 | External tool (pytest-cov etc.) |
| `quality/smells` | Code smells | json, markdown | No | v4.1 | External linter |
| `session/context` | Agent session context | json | Per session | v4.0 | Session store |
| `health` | KB health & staleness | json, markdown | No | v4.0 | KB metrics |

### 13.3 Resource Auto-Discovery

When an agent first connects, it should be able to discover all available
resources via the MCP `resources/list` call, which returns:

```json
[
  {
    "uri": "knowledge-base://project/tree",
    "name": "Project Tree",
    "description": "Full annotated project directory tree",
    "mimeType": "text/plain"
  },
  {
    "uri": "knowledge-base://arch/components",
    "name": "Components",
    "description": "All components and modules with descriptions",
    "mimeType": "application/json"
  },
  ...
]
```

---

## 14. MCP Prompt Reference

### 14.1 Complete Prompt Table

| Prompt | Arguments | When to Use |
|--------|-----------|-------------|
| `onboard-agent` | none | First contact with a project |
| `find-entry-point` | none | Need to understand startup |
| `plan-feature` | `feature_description` | Adding a new feature |
| `trace-bug` | `symptom` | Debugging an issue |
| `understand-flow` | `source`, `target` | Need data flow understanding |
| `review-change` | `planned_changes` (optional) | Before executing changes |
| `find-similar` | `code_pattern` | Need examples of similar code |
| `write-test` | `module_path` | Need to add tests |
| `refactor-guide` | `target`, `goal` | Planning a refactor |
| `summarize-changes` | `from_ref`, `to_ref` | Code review context |

### 14.2 Prompt Template Engine

Each prompt is a **Jinja2 template** (or similar) that:
1. Receives arguments from the agent
2. Queries the KB + graph to fill dynamic sections
3. Returns a complete prompt with live data

```python
# Conceptual prompt rendering
class PromptEngine:
    def render(self, prompt_name: str, args: dict) -> str:
        template = self._load_template(prompt_name)
        
        # Build context from KB + graph
        context = {
            "project_summary": self._get_resource("project/summary"),
            "arch_layers": self._get_resource("arch/layers", fmt="ascii"),
            "entry_points": self._get_entry_points(),
            "key_components": self._get_key_components(),
            "related_tests": self._get_related_tests(args.get("module_path")),
        }
        
        return template.render(**context, **args)
```

---

## 15. Migration Path

### 15.1 Backward Compatibility

| v3 Feature | v4 Compatibility | Migration Effort |
|------------|-----------------|------------------|
| `kb_search_tool` | Full backward compat | None |
| `kb_ask_tool` | Full backward compat | None |
| `kb_add_tool` | Full backward compat | None |
| `kb_stats_tool` | Full backward compat | None |
| `kb_populate_workspace_tool` | Full backward compat | None |
| `kb_reset_tool` | Full backward compat | None |
| `kb_list_categories` | Full backward compat | None |
| `chroma_db` data | Migrated to new schema | Auto-migration script |

### 15.2 Release Roadmap

```
═══ v4.0 CORE (Phases 1–4) — Ships together ═══

  Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4
    │            │            │            │
    ▼            ▼            ▼            ▼
  Semantic    Knowledge    MCP         MCP
  Code        Graph       Resources   Prompts
  Engine                            
                                      
  ┌── Phase 1: Semantic Engine         🔴 CRITICAL    ~2 weeks
  │   2-pass AST analysis, symbol resolution, docstring parsing
  │   (No type inference — deferred to v4.1 LSP backend)
  │
  ├── Phase 2: Knowledge Graph         🔴 CRITICAL    ~1 week
  │   NetworkX + SQLite, 16 relationship kinds, impact analysis
  │
  ├── Phase 3: MCP Resources           🔴 CRITICAL    ~1 week
  │   15 resources (project, arch, flows, api, code, session)
  │   quality/* resources deferred to v4.1
  │
  └── Phase 4: MCP Prompts             🟠 HIGH        ~3 days
      10 prompt templates with Jinja2 rendering

═══ v4.1 ADVANCED (Phases 5–7) — Ships later ═══

  ┌── Phase 5: Multi-Language          🟡 MEDIUM     ~2 weeks/backend
  │   tree-sitter backends (JS/TS, Rust, Go), LSP proxy
  │
  ├── Phase 6: Continuous Learning     🟡 MEDIUM     ~1 week
  │   Gap-driven ingestion, feedback loop, staleness detection
  │
  └── Phase 7: Evaluation              🟢 LOW        ~1 week
      Quality gates, benchmark suite, test queries
```

### 15.3 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ChromaDB + graph data inconsistency | Medium | High | Transactional sync (graph writes first); periodic full reconcile |
| Performance on large projects (10k+ files) | Medium | High | Single-pass analysis; lazy loading; incremental indexing; paginated resources |
| Graph hydration from SQLite too slow | Medium | Medium | Hydration budget (<3s for 10k entities); lazy-load if exceeded |
| Gap-driven ingestion circular dependency | Low | Medium | Use keyword overlap (not semantic); no KB needed for gap detection |
| Tree-sitter dependency weight | Medium | Low | Make optional; fallback to regex/LSP |
| Agent prompt template overfit | Low | Medium | Version prompts; allow custom overrides |

---

## 16. Use Cases

### 16.1 Agent Onboarding (Phase 3+4)

```
Agent connects to a new project repo:

1. Agent discovers resources via resources/list
2. Agent loads `onboard-agent` prompt
3. Prompt fires multiple KB queries + graph traversals
4. Agent receives: project summary, architecture layers,
   entry points, key components, data flow path
5. Agent can now answer user questions about the project
   without reading a single source file
```

### 16.2 Feature Implementation (Phase 1+2+3)

```
User: "Add a caching layer to the RAG query system"

Agent:
1. Loads `plan-feature` prompt with description
2. KB identifies: RagQuery, Rag, AIService as relevant
3. Graph shows: RagQuery.ask() → ChromaDB → LLM
4. Impact analysis suggests: Add cache between RagQuery and ChromaDB
5. Resources provide: entity details for all touched files
6. Agent produces a modification plan with file list
```

### 16.3 Bug Investigation (Phase 2+3)

```
User: "Web ingestion sometimes hangs for large sites"

Agent:
1. Loads `trace-bug` prompt
2. KB traces: RagController → Rag.web_ingestion → WebIngestionApp → WebExtract
3. Graph shows: no timeout handling, syncio.run() blocks
4. Agent suggests fix: add timeout parameter, use asyncio properly
5. Impact analysis: only affects WebIngestionApp call path
```

### 16.4 Cross-Language Project (Phase 5)

```
Project has Python backend + TypeScript frontend:

1. KB detects both languages (Phase 5)
2. Python backend analyzed via AST, TypeScript via tree-sitter
3. Both populate the SAME knowledge graph
4. Resources show: "api/endpoints" maps TS routes ↔ Python handlers
5. Agent can answer: "How does the frontend login call reach the backend?"
```

---

## 17. Glossary

| Term | Definition |
|------|------------|
| **Entity** | A named code element (class, function, method, module, interface, config) |
| **Relationship** | A directed connection between two entities (imports, calls, extends) |
| **Knowledge Graph** | A graph database of entities connected by relationships |
| **Semantic Analysis** | Understanding code meaning beyond syntax (type resolution, design patterns) |
| **MCP Resource** | A virtual file exposed by the MCP server via URI scheme |
| **MCP Prompt** | A pre-built prompt template served by the MCP server |
| **Gap-Driven Ingestion** | Auto-analyzing code when the KB can't answer a query |
| **Impact Analysis** | Determining what code breaks when a specific entity changes |
| **Graph Traversal** | Walking the knowledge graph along relationship edges |
| **Synthesis Mode** | How the KB combines multiple sources into an answer |
| **Backend** | A language-specific analyzer plugin |
| **Agent Session** | Accumulated context of an agent's interaction with the KB |

---

## Implementation Summary

| Phase | Name | Release | Priority | Estimated Time | Files | Tests |
|-------|------|---------|----------|---------------|-------|-------|
| 1 | Semantic Code Engine | v4.0 | 🔴 Critical | ~2 weeks | 7 | 50 |
| 2 | Knowledge Graph | v4.0 | 🔴 Critical | ~1 week | 6 | 40 |
| 3 | MCP Resources | v4.0 | 🔴 Critical | ~1 week | 8 | 30 |
| 4 | MCP Prompts | v4.0 | 🟠 High | ~3 days | 5 | 15 |
| | **v4.0 Core Total** | | | **~4–5 weeks** | **26** | **135** |
| 5 | Multi-Language | v4.1 | 🟡 Medium | ~2 weeks/backend | 6 | 35 |
| 6 | Continuous Learning | v4.1 | 🟡 Medium | ~1 week | 5 | 20 |
| 7 | Evaluation | v4.1 | 🟢 Low | ~1 week | 4 | 20 |
| | **v4.1 Advanced Total** | | | **~4–6 weeks** | **15** | **75** |
| | **Grand Total** | | | **~8–11 weeks** | **41** | **210** |

---

*Knowledge is not facts. Knowledge is connections.*
