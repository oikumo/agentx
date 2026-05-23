# .meta Structural Change Log

> **Purpose**: Track all structural changes to `.meta/` directory
> **Updated by**: AI agents and developers

---

## 2026-05-21

### KB MCP Refactor Executed — Phases 0-8 (`mcp_servers/knowledge_base/`)

- **Status**: All 9 phases (0-8) of `.meta/projects/kb-mcp-refactor/PLAN.md` completed.
- **Phase 0** — Baseline snapshot at `.meta/experiments/kb_refactor_baseline/` (chroma_db copy + tool-output transcript). Confirmed P4: pre-refactor `kb_ask_tool` returned a prompt template, never a synthesized answer.
- **Phase 1** — Deleted dead code:
  - `meta_harness_knowledge_base/src/advanced_rag.py` (unused 307 LOC)
  - `meta_harness_knowledge_base/knowledge_base.py` (unused wrapper)
  - `meta_harness_knowledge_base/kb` (deprecated CLI per AGENTS.md v4.1.0)
  - `meta_harness_knowledge_base/pyproject.toml`, `meta_harness_knowledge_base/README.md`
  - `rag_correct`/`rag_evolve` placeholder functions and `chroma_rag_*` aliases from `rag_tool.py`.
- **Phases 2-5** — Replaced the three-layer wrapper stack with a single flat `kb/` package:
  - `kb/models.py` — dataclasses (`KBEntry`, `SearchResult`, `AskResult`, `AskSource`, `AddResult`, `StatsResult`, `ResetResult`, `PopulateResult`)
  - `kb/ids.py` — single `make_entry_id()` (was duplicated in `rag_tool` and `rag_ingest`)
  - `kb/search.py` — `simple_tokenize`, `keyword_score`, `semantic_boost`, `hybrid_search` (was duplicated in `rag_tool` and `advanced_rag`)
  - `kb/synthesis.py` — real `synthesize(question, results) -> AskResult` (replaces the dead-code path that `kb_ask_tool` never reached). `kb_ask_tool` now returns a markdown answer grouped by Pattern/Finding/Decision with a `## Summary` block and cited sources.
  - `kb/store.py` — `KBStore` class encapsulating ChromaDB client + collection; no module-level globals; `get_default_store()`/`set_default_store()` for the process-wide instance; tests pass `store=` to keep persistence isolated.
  - `kb/ingest.py` — `PythonCodeAnalyzer` + `WorkspaceIngestor` (uses `KBStore`, `make_entry_id`).
  - `kb/logging.py` — stderr-only `logging.getLogger("kb")`; every `print(...)` in library code replaced with `logger.warning/error` (fixes the stdio-transport hazard).
  - `kb/api.py` — `search`/`ask`/`add_entry`/`stats`/`reset`/`populate_workspace`, all dataclass-returning, accepting an explicit `store=` for tests.
  - `kb/__init__.py` — single public surface.
  - `server.py` — now a thin formatting layer. Imports `from kb import ...`; no `sys.path.insert`. The 7 MCP tool names and signatures are unchanged.
  - **Deleted**: `kb_module/` (entire directory) and `meta_harness_knowledge_base/` (entire directory). Zero `sys.path.insert` hacks remain in the repo.
  - `pyproject.toml` bumped to `0.2.0`; wheel `only-include` now ships `server.py` + `kb/`.
- **Phase 6** — Test suite at `mcp_servers/knowledge_base/tests/` (approved location, distinct from off-limits top-level `tests/`):
  - `test_ids.py`, `test_search.py`, `test_synthesis.py`, `test_ingest.py` — pure unit tests, no Chroma
  - `test_store.py` — KBStore + api integration with isolated `tmp_path` store
  - `test_server.py` — end-to-end MCP JSON-RPC round-trip (spawns the server, lists tools, calls tools)
  - **41 tests pass**. Coverage of `kb/`: **86% overall**, every module ≥ 80%.
- **Phase 7** — Single new `mcp_servers/knowledge_base/README.md` documenting the actual surface, ID scheme, scoring formula, persistence path; updated this LOG entry.
- **Phase 8** — `kb_populate_workspace_tool` smoke-tested on the new `kb/` package itself: 9 files → 53 entries, search for `KBStore` returns the class entry with confidence 0.98. Persistence directory is now `mcp_servers/knowledge_base/chroma_db/` (was `meta_harness_knowledge_base/chroma_db/`); the live KB was empty at refactor time so no data migration was required (snapshot kept in `.meta/experiments/kb_refactor_baseline/chroma_db_snapshot/` for safety).
- **MCP tool contract preserved**: `kb_search_tool`, `kb_ask_tool`, `kb_add_tool`, `kb_stats_tool`, `kb_reset_tool`, `kb_populate_workspace_tool`, `kb_list_categories` — same names, same signatures. Only intentional behaviour change is `kb_ask_tool` now returns a synthesised markdown answer (was a prompt template). `opencode.jsonc` unchanged.
- **LOC delta**: 2,155 → ~1,070 in `mcp_servers/knowledge_base/` (excluding `tests/`). 50 % reduction with strictly better behaviour.

### KB MCP Refactor Plan Drafted (`.meta/projects/kb-mcp-refactor/`)

- Created `.meta/projects/kb-mcp-refactor/PLAN.md` — 9-phase refactor plan for `mcp_servers/knowledge_base/`.
- **Scope diagnosed**: ~2,155 LOC across 3 redundant wrapper layers, 5 `sys.path.insert` hacks, ~720 LOC of dead code (`advanced_rag.py`, `knowledge_base.py`, `kb` CLI, `rag_correct`/`rag_evolve` placeholders, `chroma_rag_*` aliases), duplicated entry-ID + scoring logic, module-level Chroma globals, library `print()` calls (stdio-transport hazard), no tests, and a `kb_ask` that returns a prompt template instead of a synthesis.
- **Target**: single flat `kb/` package with `store.py`, `search.py`, `synthesis.py`, `ingest.py`, `ids.py`, `models.py`, `logging.py`; thin `server.py`; tests at `mcp_servers/knowledge_base/tests/`.
- **Contract preserved**: 7 MCP tool names and signatures unchanged; ChromaDB on-disk schema unchanged; existing entries remain queryable. Only `kb_ask_tool`'s text output format changes (Phase 4, approved).
- **Status**: plan only — no code changed in this session.

### KB MCP Workspace Population Tools (affects `mcp_servers/knowledge_base/`)

- Added `rag_reset()` in `meta_harness_knowledge_base/src/rag_tool.py` — deletes and recreates the ChromaDB collection (resets global client cache).
- Added `kb_reset()` and `kb_populate_workspace()` in `kb_module/core.py` — high-level API wrappers exposed via `kb_module/__init__.py`.
- Added two new MCP tools in `server.py`:
  - `kb_reset_tool` — destructive reset of the KB.
  - `kb_populate_workspace_tool` — scans the workspace, extracts knowledge from `.py` (classes/methods/functions via AST) and `.md` files, and ingests into ChromaDB. Resets the KB first by default. Respects standard exclusions (`__pycache__`, `.venv`, `.git`, `node_modules`, `chroma_db`, etc.) with optional extras via `exclude_dirs`.
- **Verified**: Reset + populate smoke-tested on `kb_module/` subdir (2 files → 3 entries, no errors). All Python files parse-check OK; MCP server module loads cleanly.

### META.md Simplification & Consistency Pass

- Updated `.meta/META.md` to v3.1.0 — added missing `projects/` entry
- Populated empty `.meta/projects/META.md` with simplified template (v3.0.0)
- Populated empty `.meta/doc/META.md` with simplified template (v3.0.0)
- Populated empty `.meta/data/META.md` with simplified template (v3.0.0)
- Aligned `.meta/experiments/META.md` to v3.1.0 (added Contents section)
- Created this `LOG.md` (was missing, required by AGENTS.md rule #8)

**Rationale**: Three subdir META.md files were empty; parent index omitted `projects/`. All files now follow the same simplified template: Title → Purpose → Rules (DO/DON'T) → Contents → Version footer.

### AGENTS.md Alignment

- Updated `AGENTS.md` Decision Tree: removed stale `.meta/tools/` entry; added `.meta/projects/` and `.meta/data/` (matches actual `.meta/` layout)
- Added note pointing agents to read each subdir's `META.md` before working there
- Bumped to v4.1.0 (MCP-First + META consistency)

### KB MCP Server Fix (affects `mcp_servers/knowledge_base/`)

- **Symptom**: All KB MCP tools failed with `No module named 'src'`.
- **Root causes**:
  1. `pyproject.toml` `only-include` shipped only `server.py` + `kb_module/` in the wheel; the actual RAG implementation (`meta_harness_knowledge_base/src/rag_tool.py`) was missing from every uvx install, so `from src.rag_tool import …` blew up.
  2. `rag_tool.get_chroma_client` resolved the project root by walking 5 parents from `__file__`. That works for the in-tree `kb` CLI but, once installed in a venv, pointed at a random site-packages path, silently creating an empty ChromaDB instead of using `.meta/data/kb-meta/chroma_db`.
- **Fix**:
  - `mcp_servers/knowledge_base/pyproject.toml`: added `meta_harness_knowledge_base/src/` to the wheel's `only-include`.
  - `meta_harness_knowledge_base/src/rag_tool.py`: `get_chroma_client` now honours `KB_CHROMA_DB_PATH` / `KB_PROJECT_ROOT` env vars, falling back to the legacy 5-parents walk (preserves CLI behavior).
  - `kb_module/core.py`: on import, sets `KB_PROJECT_ROOT=Path.cwd()` when `.meta/data/kb-meta/` exists there and no env var is already set, so the opencode-launched MCP server auto-targets the project's real KB.
- **Verified**: built wheel, installed in fresh venv, `kb_stats` returns the real 5 entries; legacy in-tree CLI behavior unchanged.

---

---

## 2026-05-23 — KB Population v2.0 (Full Project Scan)

- **Action**: Knowledge Base populated (full project scan with quality gates)
- **Strategy**: RESET (0 entries at session start — auto-triggered per populate-kb skill)
- **Results**: 797 entries across 7 categories
- **Quality**: Mean confidence 0.999 | Median 0.999
- **Gates**: 5/5 passed
  - Completeness: PASS (797 entries, target ≥25)
  - Diversity: PASS (7/7 categories)
  - Confidence: PASS (mean 0.999, target ≥0.75)
  - Coverage: PASS (all src/ dirs indexed)
  - Coherence: PASS (3/3 queries returned relevant answers ≥0.6 confidence)
- **Files**: Python ✓ (792 auto-extracted) | Markdown ✓ (5 manual entries)
- **Manual entries**: 5 added (META System PAT-584C, KB-First Workflow PAT-5CBF, MainController PAT-967F, RAG/ChromaDB DEC-6A48, Petri Net DEC-6182)
- **Excluded**: .venv, .git, .pytest_cache, local_sessions, .agents, .agents_prompts, .idea, .meta, __pycache__
- **MCP Operations**:
  - `kb_reset_tool`: 1 call
  - `kb_populate_workspace_tool`: 1 call (succeeded after timeout retry)
  - `kb_add_tool`: 5 calls (parallel batch)
  - `kb_stats_tool`: 3 calls
  - `kb_list_categories`: 2 calls
  - `kb_ask_tool`: 3 calls (verification queries)
  - `kb_search_tool`: 1 call (verification query)
