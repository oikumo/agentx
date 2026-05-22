# Refactor Plan — Knowledge Base MCP Server

> **Status:** Plan approved, not yet executed
> **Owner:** User
> **Target path:** `mcp_servers/knowledge_base/`
> **Created:** 2026-05-21
> **Related WORK.md item:** `[*] Implement RAG feature` (must not be blocked)

---

## 1. Current State — Diagnosis

### Layout (~2,155 LOC)

```
mcp_servers/knowledge_base/
├── server.py                  309 LOC — FastMCP tool definitions
├── pyproject.toml             uvx entry point
├── chroma_db/                 ChromaDB persistence
├── kb_module/                 "MCP-friendly wrapper"
│   ├── __init__.py
│   ├── core.py                398 LOC — wraps rag_tool with dataclasses
│   └── README.md
└── meta_harness_knowledge_base/
    ├── __init__.py            docstring-only, broken example
    ├── knowledge_base.py      113 LOC — string-formatting wrapper (unused by MCP)
    ├── kb                     193 LOC — standalone CLI (deprecated per AGENTS.md)
    ├── pyproject.toml         orphan
    └── src/
        ├── rag_tool.py        477 LOC — Chroma client + hybrid search + CRUD
        ├── rag_ingest.py      340 LOC — AST/Markdown ingestion
        └── advanced_rag.py    307 LOC — multi-hop, query rewriting (UNUSED)
```

### Problems

| # | Issue | Evidence |
|---|---|---|
| **P1** | Three redundant layers (`server.py` → `kb_module.core` → `meta_harness_knowledge_base.knowledge_base` / `src.rag_tool`) | Each layer just renames and reformats. |
| **P2** | Fragile `sys.path.insert` hacks in 5 files | `core.py:26`, `rag_tool.py:21`, `rag_ingest.py:15`, `advanced_rag.py:13`, `kb:9`. |
| **P3** | Dead code shipped to production | `advanced_rag.py` (unused), `knowledge_base.py` (unused), `kb` CLI (deprecated per AGENTS.md v4.1.0), `rag_correct` / `rag_evolve` (return "not implemented"), `chroma_rag_*` aliases. |
| **P4** | `kb_ask` does not synthesize | `rag_tool.py:262` returns an `augmented_prompt` template instead of an answer. `advanced_rag._synthesize_answer` (which formats properly) is unreachable from MCP. Today's KB query returned confidence 0.00 with this template text. |
| **P5** | No tests | `find tests -path '*kb*'` → empty. |
| **P6** | Hidden module-level globals (`_chroma_client`, `_chroma_collection`) | `rag_tool.py:124-137`. `rag_reset` mutates globals → racy. |
| **P7** | Inconsistent return shapes — dataclass for search, raw `dict` for stats/add/reset/populate | `kb_module/core.py`. |
| **P8** | Broken documentation in `meta_harness_knowledge_base/__init__.py` (advertises placeholders + invalid `python3 -m` module name). | |
| **P9** | Duplicated entry-ID logic in `rag_tool.rag_add_entry:323` and `rag_ingest._add_entry:252`. | |
| **P10** | Scoring logic copy-pasted verbatim across `rag_tool.hybrid_search_with_chroma` and `advanced_rag._search`. | |
| **P11** | `print(...)` for errors in library code → corrupts stdio MCP transport. | `rag_tool.py:223`, `rag_ingest.py:230`. **Critical.** |
| **P12** | RAG ingestion / vector-DB queries are in progress (WORK.md). Refactor must not block. | |

---

## 2. Target Architecture

A single flat package. No wrappers around wrappers.

```
mcp_servers/knowledge_base/
├── server.py            — MCP tool surface ONLY (formatting + validation)
├── pyproject.toml
├── README.md            — single source of truth
├── chroma_db/           — persistence (unchanged on disk)
├── kb/                  — the library
│   ├── __init__.py      — public API
│   ├── store.py         — KBStore class (Chroma client/collection, no globals)
│   ├── search.py        — hybrid search + scoring (one copy)
│   ├── synthesis.py     — answer synthesis (replaces dead advanced_rag)
│   ├── ingest.py        — Python AST + Markdown ingestion
│   ├── ids.py           — single entry-ID generator
│   ├── models.py        — dataclasses (KBEntry, SearchResult, AskResult, Stats)
│   └── logging.py       — stderr logger (stdio-safe)
└── tests/
    ├── test_store.py
    ├── test_search.py
    ├── test_synthesis.py
    ├── test_ingest.py
    └── test_server.py   — MCP integration round-trip
```

**Deleted:** `kb_module/`, `meta_harness_knowledge_base/` (entire nested directory), the `kb` CLI, `advanced_rag.py`, `knowledge_base.py`, `rag_correct`/`rag_evolve` placeholders, `chroma_rag_*` aliases.

### Design rules

1. `server.py` is **thin**: parse, call `kb.*`, format. No business logic, no `sys.path` hacks.
2. All library imports are absolute (`from kb.store import …`).
3. ChromaDB client encapsulated in `KBStore` class — no module globals. `reset()` re-instantiates.
4. All errors go through `kb.logging` to **stderr** (never stdout — stdio transport corruption).
5. `kb_ask` actually synthesizes via `synthesis.py`.
6. Tests live in `mcp_servers/knowledge_base/tests/` (top-level `tests/` is off-limits per AGENTS.md without explicit approval — confirmed).

---

## 3. Backward-Compatibility Contract

The MCP tool **names and signatures stay identical**:

- `kb_search_tool`
- `kb_ask_tool`  ← **output text format changes (Phase 4)** — see §6
- `kb_add_tool`
- `kb_stats_tool`
- `kb_reset_tool`
- `kb_populate_workspace_tool`
- `kb_list_categories`

→ `opencode.jsonc` and every agent calling these tools keeps working. Only internals change.

The on-disk `chroma_db/` schema is **unchanged** (same metadata keys, same ID prefix scheme: `PAT-XXXX`, `FIND-XXXX`, `DEC-XXXX`, `COR-XXXX`) → existing entries remain queryable.

---

## 4. Migration Phases

Each phase is small, individually verifiable, and leaves the MCP working.

### Phase 0 — Safety net (no code change)
- Snapshot current behavior: run every MCP tool, capture outputs into `.meta/experiments/kb_refactor_baseline/`.
- Record `kb_stats` numbers; copy `chroma_db/` to `.meta/experiments/kb_refactor_baseline/chroma_db_snapshot/`.
- **Exit criteria:** baseline reproducible.

### Phase 1 — Delete dead code
- Repo-wide `grep` for `meta_harness_knowledge_base`, `kb_module`, `advanced_rag`, `chroma_rag_`, `rag_correct`, `rag_evolve` to find any hidden callers.
- Remove `advanced_rag.py`, `knowledge_base.py`, the `kb` CLI, `rag_correct`, `rag_evolve`, `chroma_rag_*` aliases.
- Remove `meta_harness_knowledge_base/pyproject.toml`, fix `__init__.py` docstring.
- Update `pyproject.toml` `[tool.hatch.build.targets.wheel].only-include` to drop deleted paths.
- **Exit criteria:** `uvx --from ./mcp_servers/knowledge_base knowledge_base` still serves all 7 tools; baseline behavior unchanged.

### Phase 2 — Flatten package layout
- Create `kb/` package.
- Split `rag_tool.py` → `kb/store.py` + `kb/search.py` + `kb/ids.py`.
- Move `rag_ingest.py` → `kb/ingest.py` (using shared `kb/ids.py`).
- Delete `meta_harness_knowledge_base/` directory entirely.
- Delete `kb_module/` (functionality inlined in `kb/`).
- Update `server.py` imports: `from kb import search, ask, add_entry, stats, reset, populate_workspace`.
- Update `pyproject.toml` packaging.
- **Exit criteria:** zero `sys.path.insert` in the repo; MCP tools functionally identical to baseline; uvx reinstall works.

### Phase 3 — Encapsulate Chroma client
- Introduce `KBStore` class in `kb/store.py` holding `client` + `collection`.
- Remove module-level `_chroma_client` / `_chroma_collection`.
- `kb/__init__.py` exposes a single default store instance, lazy-constructed.
- `reset()` re-instantiates the collection cleanly.
- **Exit criteria:** stats/search/reset still pass baseline parity tests.

### Phase 4 — Fix `kb_ask` synthesis  *(behavior change — approved)*
- Implement `kb/synthesis.py` with a `synthesize(question, results) -> AskResult` function. Port working logic from `advanced_rag._synthesize_answer`; drop multi-hop until proven needed.
- Update `kb_ask_tool` in `server.py` to use it.
- **Exit criteria:** `kb_ask_tool` returns a real synthesized answer with sources and average confidence, not a prompt template.

### Phase 5 — Stdio-safe logging
- Add `kb/logging.py`: `logging.getLogger("kb")` with `StreamHandler(sys.stderr)`.
- Replace every `print(...)` in library code with `logger.warning/error`.
- **Exit criteria:** no library function writes to stdout; MCP responses parse cleanly under stdio transport.

### Phase 6 — Tests
- Create `mcp_servers/knowledge_base/tests/` (approved).
- Unit tests for store, ids, search scoring, ingest (AST shapes), synthesis.
- One end-to-end MCP test spawning the server and round-tripping `kb_stats_tool`.
- **Exit criteria:** `uv run pytest` green; coverage of public API ≥ 80 %.

### Phase 7 — Documentation refresh
- Replace both READMEs with one `mcp_servers/knowledge_base/README.md`.
- Document actual MCP tool surface, ID scheme, scoring formula, persistence path.
- Do **not** change `AGENTS.md` (MCP tool names are preserved).
- Log structural change in `.meta/LOG.md`.
- **Exit criteria:** docs match the code.

### Phase 8 — KB self-population
- Run `kb_populate_workspace_tool` so the KB has entries about itself. (Today's empty KB caused 0.00 confidence on architecture queries.)
- **Exit criteria:** `kb_stats_tool` shows > 0 entries; a query about `KBStore` returns it.

---

## 5. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| ChromaDB collection corruption during refactor | Phase 0 snapshot; never run `reset` outside tests on the live DB. |
| Hidden caller of deleted module | Phase 1 starts with a repo-wide grep for old names. |
| uvx packaging breaks after moving files | `pyproject.toml` `only-include` updated per phase; test `uvx` reinstall at end of each phase. |
| Conflicts with in-progress RAG work (WORK.md) | Each phase is independently mergeable. Ingestion code is touched only in Phase 2 (mechanical move) — no redesign of ingestion semantics. |
| stdio transport corruption from leftover `print` | Phase 5 explicitly removes them; tested by Phase 6 integration test. |

---

## 6. Behavior Changes (User-Visible)

Only **one** behavior change is intentional in this refactor:

**`kb_ask_tool` output text format** — Phase 4
- **Before:** returns a prompt template starting with `"You are an AI agent working on the Agent-X project. Use the following retrieved knowledge…"` followed by raw retrieval dump. Confidence is averaged over retrieved entries but the *answer* is just a prompt skeleton.
- **After:** returns a synthesized markdown answer grouping results by entry type (Pattern/Finding/Decision), each with title, ID, category, confidence, and a `## Summary` block at the top. Same `confidence` float, same `sources` list.

This is approved as a bug fix (the current behavior is what caused the session-start KB query to return confidence 0.00).

All other tools preserve exact input/output contracts.

---

## 7. Deliverables Checklist

- [ ] Phase 0 — Baseline snapshot in `.meta/experiments/kb_refactor_baseline/`
- [ ] Phase 1 — Dead code removed; uvx still works
- [ ] Phase 2 — Flat `kb/` package; zero `sys.path` hacks
- [ ] Phase 3 — `KBStore` class; no module globals
- [ ] Phase 4 — `kb_ask` produces real synthesis
- [ ] Phase 5 — stderr-only logging in library
- [ ] Phase 6 — Test suite at `mcp_servers/knowledge_base/tests/`, ≥80 % coverage of public API
- [ ] Phase 7 — Single accurate README; `.meta/LOG.md` updated
- [ ] Phase 8 — KB self-populated; `kb_stats_tool` > 0 entries

---

## 8. Decisions Locked In (from approval session)

| Question | Decision |
|---|---|
| Tests location | `mcp_servers/knowledge_base/tests/` |
| `kb_ask` behavior change | Approved — fix it (Phase 4) |
| Scope of execution | Plan only — write to file, do not execute yet |

---

**Version:** 1.0.0
