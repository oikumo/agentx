# System Rules

> **⚠️ MANDATORY FIRST STEP FOR ALL AGENTS:** On the **first prompt of a session**, you MUST read `WORK.md`, then display it to the user as a reminder. This happens ONCE per session, before any other action.
>
> **⚠️ SECOND MANDATORY STEP:** Before ANY task, you MUST query the Knowledge Base first at `.meta/knowledge_base/` or run `meta kb ask <query>`. This is non-negotiable and applies to EVERY task.
>
> **FAILURE TO QUERY KB FIRST = TASK FAILURE** - Agents must demonstrate KB usage in every response

## ⚠️ Core Directives (NON-NEGOTIABLE)

**Priority 0 (Session Startup):**
0. **SHOW WORK FIRST** - On first prompt only, read `WORK.md`, display to user
0a. **ALWAYS query KB first** - Before ANY task, search `.meta/knowledge_base/` or use `meta kb ask`
0b. **IF KB IS EMPTY, POPULATE IT** - Run `meta kb populate` before proceeding
0c. **ALWAYS REFERENCE KB** - Cite KB entries or explain why not consulted

**Priority 1 (Safety - NEVER violate):**
1. **NEVER commit/push** - Not even if user asks
2. **NEVER modify .env** - Or secrets files
3. **NEVER add dependencies** - Use existing; approval required
4. **NEVER modify tests/** - Use .meta/tests_sandbox/ (requires approval)
5. **NEVER change README.md** - Only if user explicitly requests

**Priority 2 (Process - ALWAYS follow):**
6. **ALWAYS check git log** - Before ANY changes
7. **ALWAYS follow META rules** - All rules in this file
8. **ALWAYS run USER PROMPTS** - Commands start with `meta`
9. **LOG STRUCTURAL CHANGES** - All META HARNESS changes in `.meta/LOG.md`

## Meta Project Harness
Structured development system for AI-assisted development:
- **Safe spaces** - Work without affecting production
- **Clear workflows** - Consistent, high-quality output
- **Comprehensive docs** - At every level
- **Quality gates** - Ensure correctness
- **Work notebook** - Simple reminder via `WORK.md`

---

## Work Notebook (`WORK.md`)

### Work Notebook (`WORK.md`)
**What it is**: A simple reminder file that shows what the user is currently working on and the next planned work.

**When to show**: At the start of EVERY session (first prompt only), the agent MUST:
1. Read `WORK.md`
2. Display its content to the user as a reminder
3. Continue with normal workflow

**How it works**:
- Agent updates this file when user starts a new task
- Shows current task status (if any)
- Cleared when work is complete
- Not a task tracker - just a simple reminder

**Format**:
```markdown
## Current Task
**Status**: [Task description or "No active work"]
## Planned Work
1. [Next task]
2. [Other next task]
```

## Knowledge Base Rules
**MANDATORY**: Before answering any project-specific question, agents must query the KB first at `.meta/knowledge_base/META.md` or run `meta kb ask <query>`.

**ENFORCEMENT**:
- Agents must query KB before ANY task
- Agents must demonstrate KB usage in every response
- If KB is empty, agents must run `meta kb populate` BEFORE proceeding
- Every response must cite KB entries or explain why KB was not consulted
- Failure to query KB first = task failure

Based on `.meta/knowledge_base/META.md`:

### Purpose
Centralized knowledge storage for:
- Project-specific information
- Codebase patterns and conventions
- Workflow documentation
- Decision history
- Agent learnings

### Structure
```
.meta/knowledge_base/
├── META.md           # This file
├── entries/          # Knowledge entries
│   ├── YYYY-MM-DD-entry-id.md
│   └── ...
└── indexes/          # Search indexes
    └── vector.db     # Vector embeddings (if applicable)
```

### Workflow
**Query Flow (Mandatory - Step 1 of any task)**
```
1. Receive task
2. Query KB: "What is X?" / "How does Y work?"
3. Review relevant entries
4. Answer based on KB + codebase
5. If KB missing info → Add entry after completion
```

**Population Flow**
```
1. Complete task successfully
2. Extract key learnings
3. Create dated entry in entries/
4. Update indexes if needed
5. Commit knowledge (not code)
```


### Rules
**DO**: Query before answering, add entries after tasks, keep entries concise, tag properly
**DON'T**: Store secrets, duplicate code, skip population, ignore outdated entries


### Directory Structure
```
agent-x/
├── META_HARNESS.md # Master documentation
├── AGENTS.md # This file
├── .meta/sandbox/ # Safe workspace
├── .meta/experiments/ # Experimental features
├── .meta/tests_sandbox/ # TDD workspace
├── .meta/knowledge_base/ # RAG knowledge base
├── .meta/reflection/ # Test logs & capability assessment
├── .meta/tools/ # Development tools, scripts
├── .meta/doc/ # Documentation archives
├── .meta/data/ # Data storage
├── tests/ # Unit and integration tests
│   └── unit/ # Unit tests
└── test_automated/ # Automated agent tests (legacy)
```
**Rule:** All `.meta/*` subdirs contain META.md - read first.

## Workflow (5 Steps)
1. **UNDERSTAND** - **ALWAYS query KB first** (.meta/knowledge_base/ or `meta kb ask`) → **IF KB EMPTY, run `meta kb populate` FIRST** → **Demonstrate KB query in response** → Then read task + git log + META.md
2. **PLAN** - Identify correct directory (see Decision Tree)
3. **EXECUTE** - Work in safe space, test frequently
4. **VALIDATE** - Tests pass, no production break
5. **REPORT** - Summarize + document + cleanup

## Decision Tree
```
Need to...
├─ Understand something? → **KB FIRST** (.meta/knowledge_base/ or `meta kb ask`) → **IF EMPTY: `meta kb populate`** → **Cite KB in response** THEN proceed below
├─ Understand rules? → Read META.md (via KB)
├─ Modify code? → .meta/sandbox/
├─ Test idea? → .meta/experiments/
├─ Write tests? → .meta/tests_sandbox/
├─ Test agent (automated)? → .meta/tests_automated/ or test_automated/
├─ Use/create tools? → .meta/tools/
└─ Check workflows? → .meta/project_development/WORKFLOWS.md (if exists)
```

## Resources
- [META_HARNESS.md](META_HARNESS.md) - Master docs

---
**Version:** 2.3.2 (Removed non-existent directories) | **Updated:** 2026-05-02
