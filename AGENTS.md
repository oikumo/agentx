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

- **Server**: `mcp_servers/knowledge_base/server.py`
- **Configuration**: `opencode.jsonc` (MCP section)
- **Tools Available**:
  - `knowledge_base_kb_ask_tool` - RAG-augmented Q&A with citations
  - `knowledge_base_kb_search_tool` - Search KB entries
  - `knowledge_base_kb_add_tool` - Add new KB entries
  - `knowledge_base_kb_stats_tool` - Get KB statistics
  - `knowledge_base_kb_list_categories` - List valid categories/types


---

**Version:** 5.0.0 (OMT++ integrated) | **Updated:** 2026-05-30
