# System Rules

> **⚠️ MANDATORY FIRST STEP:** On the **first prompt**, read `WORK.md` and display it.
>
> **⚠️ MANDATORY SECOND STEP:** Before ANY task, query the KB using the MCP `knowledge_base` tools.

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
8. Log structural changes in `.meta/LOG.md`
9. Query KB first using MCP tools, cite sources in every response

---

## Quick Start

1. **Query KB** → Use MCP tool `knowledge_base_ask_tool` or `knowledge_base_search_tool`
2. **Check git** → `git log --oneline -5`
3. **Work in correct directory** (see Decision Tree)
4. **Log changes** → Update `.meta/LOG.md`

---

## Decision Tree

```
Need to...
├─ Understand something?  → Query KB via MCP tools first
├─ Modify code?           → Work on source code directly
├─ Prototype/test idea?   → `.meta/experiments/`
├─ Write tests?           → `tests/unit/` (with approval) or `.meta/experiments/`
├─ Plan a project?        → `.meta/projects/`
├─ Store data/KB?         → `.meta/data/`
└─ Document something?    → `.meta/doc/`
```

> Each `.meta/<subdir>/` has its own `META.md` describing scope and rules.
> Read it before working in that directory.

---

## Workflow (5 Steps)

1. **UNDERSTAND** - Query KB via MCP + check git log
2. **PLAN** - Identify correct directory
3. **EXECUTE** - Work in safe space, test frequently
4. **VALIDATE** - Tests pass, no production break
5. **REPORT** - Summarize + document + cleanup

---

## Knowledge Base Access

The Knowledge Base is **exclusively** accessed through the MCP server:

- **Server**: `mcp_servers/knowledge_base/server.py`
- **Configuration**: `opencode.jsonc` (MCP section)
- **Tools Available**:
  - `knowledge_base_ask_tool` - RAG-augmented Q&A with citations
  - `knowledge_base_search_tool` - Search KB entries
  - `knowledge_base_add_tool` - Add new KB entries
  - `knowledge_base_stats_tool` - Get KB statistics
  - `knowledge_base_list_categories` - List valid categories/types


---

**Version:** 4.1.0 (MCP-First + META consistency) | **Updated:** 2026-05-21
