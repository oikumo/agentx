# KB Refactor — Phase 0 Baseline Snapshot

> Captured before Phase 1 of the refactor (see `.meta/projects/kb-mcp-refactor/PLAN.md`).
> Date: 2026-05-21
> Git HEAD: deeff75 [WIP] RAG ingestion  * Refactor KB

## On-disk Chroma location (current)

`mcp_servers/knowledge_base/meta_harness_knowledge_base/chroma_db/` (217 KB sqlite + 2 segment dirs)

Note: this differs from the PLAN's target persistence path
(`mcp_servers/knowledge_base/chroma_db/`). The current `rag_tool.get_chroma_client()`
resolves `Path(__file__).parent.parent / "chroma_db"` which from `src/rag_tool.py`
is `meta_harness_knowledge_base/chroma_db/`.

The live KB has **0 entries**, so this snapshot is the empty collection structure.
After the refactor, the new `KBStore` will point at `mcp_servers/knowledge_base/chroma_db/`
(the empty top-level dir). On Phase 8 the KB will be re-populated.

If non-empty data ever needs to be migrated, copy
`.meta/experiments/kb_refactor_baseline/chroma_db_snapshot/` to the new
`mcp_servers/knowledge_base/chroma_db/` before starting Phase 8.

## MCP tool outputs (baseline)

### kb_stats_tool

```
📊 Knowledge Base Statistics

Total Entries: 0

📁 By Type:

📂 By Category:

📈 Confidence Distribution:
  • High (≥0.9): 0
  • Medium (0.6-0.9): 0
  • Low (<0.6): 0
```

### kb_list_categories

```
📚 Knowledge Base Categories & Types

Valid Entry Types:
  • pattern - Reusable patterns or best practices
  • finding - Discoveries or insights
  • decision - Architectural or design decisions
  • correction - Corrections to existing entries

Valid Categories:
  • code - Code-related knowledge
  • class - Class-level knowledge
  • method - Method-level knowledge
  • function - Function-level knowledge
  • workflow - Workflows and processes
  • documentation - Documentation guidelines
  • architecture - Architectural patterns
```

### kb_search_tool("test query for baseline", top_k=3)

```
No results found.
```

### kb_ask_tool("baseline test question", top_k=3)  ← **EVIDENCE OF P4**

```
💡 Answer (Confidence: 0.00)

You are an AI agent working on the Agent-X project.
Use the following retrieved knowledge from the project's knowledge base to answer the question.

No relevant knowledge found in the project knowledge base. Answer based on general knowledge.

### Question:
baseline test question

### Your Answer:
```

This confirms Plan §1 P4: `kb_ask_tool` returns a *prompt template*, not a
synthesized answer. Phase 4 fixes this.

## Tool surface (must be preserved)

- `kb_search_tool(query, top_k, category)`
- `kb_ask_tool(question, top_k)` — output format changes in Phase 4 (approved)
- `kb_add_tool(entry_type, category, title, finding, solution, context, confidence, example)`
- `kb_stats_tool()`
- `kb_reset_tool()`
- `kb_populate_workspace_tool(workspace_root, include_python, include_markdown, exclude_dirs, reset_first)`
- `kb_list_categories()`

## Module structure (before)

```
mcp_servers/knowledge_base/
├── server.py
├── __init__.py            (empty)
├── pyproject.toml
├── uv.lock
├── chroma_db/             (empty)
├── kb_module/
│   ├── __init__.py
│   ├── core.py
│   └── README.md
└── meta_harness_knowledge_base/
    ├── __init__.py
    ├── knowledge_base.py
    ├── kb                 (CLI, deprecated)
    ├── pyproject.toml
    ├── README.md
    ├── chroma_db/         ← LIVE persistence dir
    └── src/
        ├── __init__.py
        ├── rag_tool.py
        ├── rag_ingest.py
        └── advanced_rag.py
```

## Exit criteria — Phase 0

- [x] chroma_db snapshot copied
- [x] MCP tool outputs captured
- [x] Module structure documented
