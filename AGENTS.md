# System Rules

> **⚠️ MANDATORY FIRST STEP FOR ALL AGENTS:** On the **first prompt of a session**, you MUST read `WORK.md` and display it to the user as a reminder. This happens ONCE per session, before any other action.
>
> **⚠️ SECOND MANDATORY STEP:** Before ANY task, you MUST query the Knowledge Base first at `.meta/knowledge_base/` or run `meta kb ask <query>`. This is non-negotiable and applies to EVERY task.
>
> **FAILURE TO QUERY KB FIRST = TASK FAILURE** - Agents must demonstrate KB usage in every response

## ⚠️ Core Directives (NON-NEGOTIABLE)

-2. **LOG STRUCTURAL CHANGES** - ALL structural META HARNESS changes MUST be logged in `.meta/LOG.md` - THIS IS Mandatory
-1. **SHOW WORK NOTEBOOK FIRST** - On first prompt of session only, read `WORK.md` and display it to user as reminder - THIS IS Mandatory
0. **ALWAYS query KB first** - Before ANY task, search `.meta/knowledge_base/` or use `meta kb ask` - THIS IS MANDATORY
0a. **IF KB IS EMPTY, POPULATE IT** - If KB has no entries, run `meta kb populate` BEFORE proceeding with the task
0b. **ALWAYS REFERENCE KB** - Every response must cite KB entries or explain why KB was not consulted
1. **NEVER commit/push** - Not even if user asks
2. **ALWAYS follow the META rules** Rules are in this file
3. **NEVER add dependencies** - Use existing; approval required
3. **NEVER modify .env** - Or secrets files
4. **ALWAYS check git log** - Before ANY changes
5. **NEVER modify tests/** - Use .meta/tests_sandbox/ (requires approval)
6. **Use uv & pyproject.toml** - For dependencies
7. **NEVER change README.md** - Only if user explicitly requests
8. **ALWAYS run USER PROMPTS** - Commands start with `meta` (see META_COMMANDS.md)

## Meta Project Harness
Structured development system for AI-assisted development:
- **Safe spaces** - Work without affecting production
- **Clear workflows** - Consistent, high-quality output
- **Comprehensive docs** - At every level
- **Quality gates** - Ensure correctness
- **Work notebook** - Simple reminder via `WORK.md`

---

## Work Notebook (`WORK.md`)

**What it is**: A simple reminder file that shows what the user is currently working on.

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
```

---

# User Prompts Shortcuts

Not bash commands, this an user prompts shortcuts

## KB Commands
- `meta kb populate` - Populate KBs
- `meta kb` - Search KB
- `meta kb ask` - RAG query
- `meta kb stats` - Show stats
- `meta kb add` - Add entry
- `meta kb correct` - Correct entry
- `meta kb evolve` - Evolve KB

## Work Commands
- `meta work {prompt}` - Set current work task in WORK.md

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

### Entry Format
```markdown
# Entry ID: YYYY-MM-DD-topic

**Tags**: [tag1, tag2]
**Related**: [links to other entries]

## Context
Why this knowledge matters

## Content
The actual knowledge

## Examples
Code snippets or use cases

## References
- Links to source files
- Related decisions
```

### Rules
**DO**: Query before answering, add entries after tasks, keep entries concise, tag properly
**DON'T**: Store secrets, duplicate code, skip population, ignore outdated entries

### Maintenance
- **After each session**: Add new learnings
- **Weekly**: Review and prune outdated entries
- **Monthly**: Run `meta kb evolve` to optimize structure

### Integration
KB works with:
- `.meta/sandbox/` - Reference knowledge during modifications
- `.meta/tests_sandbox/` - Store test patterns
- `.meta/experiments/` - Document experimental findings
- `.meta/reflection/` - Store capability assessments

## Optimization Commands
- `meta token audit` - Audit tokens
- `meta compress docs` - Compress docs
- `meta structure analysis` - Analyze structure
- `meta health check` - Health check
- `meta archive experiments` - Archive experiments

## Project Commands
- `meta token audit` - Quick audit (30min)
- `meta archive experiments` - Quick archive (30min)
- `meta consolidate docs` - Consolidate docs (30min)
- `meta health check` - Health check (30min)
- `meta compress docs` - Compress docs (1-3hr)
- `meta structure analysis` - Analyze structure (1-3hr)
- `meta create workflows` - Create workflows (1-3hr)
- `meta populate kb` - Populate KB (1-3hr)
- `meta optimize all` - Full optimize (3+hr)
- `meta create skill` - Create skill (3+hr)
- `meta enhance workflows` - Enhance workflows (3+hr)
- `meta test capability` - Test capability (3+hr)

## Help
- `meta` - Show commands
- `meta help` - Show help

## Decision Tree
```
Need to...
├─ Populate KB? → meta kb populate
├─ Search KB? → meta kb search
├─ Add knowledge? → meta kb add
├─ Check health? → meta health check
├─ Save tokens? → meta token audit
├─ Clean up? → meta archive experiments
├─ Compress docs? → meta compress docs
├─ Analyze structure? → meta structure analysis
└─ Create skill? → meta create skill
```

---
**Total**: 22 commands

### Directory Structure
```
agent-x/
├── META_HARNESS.md # Master documentation
├── AGENTS.md # This file
├── features/ # AgentX features organized by state
│   ├── planned/ # Planned features (not started)
│   ├── wip/ # Work in progress (developing)
│   └── ok/ # Completed features (ready to use)
├── .meta/project_development/ # Rules, standards, workflows
├── .meta/sandbox/ # Safe workspace
├── .meta/experiments/ # Experimental features
├── .meta/tests_sandbox/ # TDD workspace
├── .meta/development_tools/ # Development tools, scripts
├── .meta/knowledge_base/ # RAG knowledge base
├── .meta/reflection/ # Test logs & capability assessment
└── test_automated/ # Automated agent tests (reflection tests)
```
**Rule:** All `.meta/*` subdirs contain META.md - read first. Features have their own META.md at `features/META.md`.

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
├─ Add/modify feature? → features/ (planned/ → wip/ → ok/)
├─ Modify code? → .meta/sandbox/
├─ Test idea? → .meta/experiments/
├─ Write tests? → .meta/tests_sandbox/
├─ Test agent? → test_automated/
├─ Use/create tools? → .meta/development_tools/
└─ Check workflows? → .meta/project_development/WORKFLOWS.md
```

## Quality Gates
- [ ] **Queried KB first** (MANDATORY - before ANY task, search `.meta/knowledge_base/` or use `meta kb ask`)
- [ ] **Populated KB if empty** (If KB was empty, ran `meta kb populate` before proceeding)
- [ ] **Referenced KB in response** (Demonstrated KB usage or explained why not consulted)
- [ ] Checked git log
- [ ] Working in correct .meta/* subdirectory
- [ ] Tests pass (if applicable)
- [ ] Changes documented
- [ ] No production code modified
- [ ] No secrets exposed

## Tools
`read`, `glob`, `bash`, `edit`, `write`, `task`

## Common Scenarios
- **Add Feature** → features/planned/ → features/wip/ → features/ok/
- **Add Feature (code)** → sandbox → tests → merge → features/ok/
- **Fix Bug** → reproduce in sandbox → test → fix → merge
- **Refactor** → copy to sandbox → refactor → test → merge
- **Test Agent** → test_automated/ → run reflection tests

## Projects (User Tasks)

### Quick (30min)
- Token Audit → `.meta/sandbox/`
- Archive Experiments → `.meta/experiments/`
- Consolidate Docs → `.meta/tools/`
- Health Check → `.meta/reflection/`

### Medium (1-3hr)
- Docs Compression → `.meta/sandbox/`
- Structure Analysis → `.meta/sandbox/`
- Workflow Templates → `.meta/project_development/`
- KB Population → `.meta/knowledge_base/`

### Advanced (3+hr)
- Full Optimization → Multiple dirs
- Skill Development → `.meta/experiments/`
- Workflow Enhancement → `.meta/project_development/`
- Capability Assessment → `.meta/reflection/`

## Resources
- [META_HARNESS.md](META_HARNESS.md) - Master docs
- [WORKFLOWS.md](.meta/project_development/WORKFLOWS.md) - Workflows
- [QUICK_REFERENCE.md](.meta/project_development/QUICK_REFERENCE.md) - Quick ref
- [KB META.md](.meta/knowledge_base/META.md) - **Consolidated KB documentation (READ FIRST)**
- [Features META.md](features/META.md) - **Features organization (READ FIRST)**
- [Reflection Tests](.meta/reflection/README.md) - Automated test documentation

---
**Version:** 2.3.1 (WORK.md moved to root) | **Updated:** 2026-05-01
