# .meta Structural Change Log

> **Purpose**: Track all structural changes to `.meta/` directory
> **Updated by**: AI agents and developers

---

## 2026-05-21

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
