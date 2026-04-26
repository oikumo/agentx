# AGENTS.md - Agent-X System Agent Rules

## ⚠️ Core Directives (NON-NEGOTIABLE)

| # | Directive                                                     | What It Means                                                                   |
|---|---------------------------------------------------------------|---------------------------------------------------------------------------------|
| 1 | **NEVER commit or push**                                      | Not even if user asks                                                           |
| 2 | **NEVER add dependencies**                                    | Use what exists; explicit approval required for exceptions                      |
| 3 | **NEVER modify .env**                                         | Or any file likely to contain secrets/credentials                               |
| 4 | **ALWAYS check git log**                                      | Before making ANY changes                                                       |
| 5 | **NEVER modify tests/**                                       | Use .meta.tests_sandbox/ for new tests (requires approval)                      |
| 6 | **Use uv & pyproject.toml with python3**                      | For all dependency management; avoid pin drift                                  |
| 7 | **NEVER change the <root>/README.md **                        | Modify it only when the User request it explicitly                              |
| 8 | **ALWAYS** run USER PROMPTS. Commands starts with `meta` | The command/prompts are in the file: [`./META_COMMANDS.md`](./META_COMMANDS.md) |
|---| ------------------------------------------                    | ----------------------------------------------------------------------          |

## What is the Meta Project Harness?

A structured development system optimized for AI‑assisted development providing:
- **Safe spaces** to work without affecting production
- **Clear workflows** for consistent, high‑quality output
- **Comprehensive documentation** at every level
- **Quality gates** to ensure correctness

### Directory Structure
```
agent-x/
├── META_HARNESS.md # Master documentation
├── AGENTS.md       # This file (updated)
├── .meta.project_development/ # Rules, standards, workflows
├── .meta.sandbox/              # Your safe workspace
├── .meta.experiments/          # Experimental features
├── .meta.tests_sandbox/         # TDD workspace
├── .meta.development_tools/    # MCP tools, scripts
├── .meta.knowledge_base/       # RAG knowledge base
└── .meta.reflection/           # Test logs & capability assessment
```

**Rule:** All harness directories start with `.meta.` and contain a `META.md` file you must read first.

## Your Workflow

### 5‑Step Workflow
```
1. UNDERSTAND: Read task + git log + relevant META.md
2. PLAN: Identify correct directory (see Decision Tree)
3. EXECUTE: Work in safe space, test frequently
4. VALIDATE: All tests pass, no production break
5. REPORT: Summarize + document + cleanup
```

## Decision Tree
```
Need to...
├─ Understand rules? → Read relevant META.md
├─ Modify code? → .meta.sandbox/
├─ Test new idea? → .meta.experiments/
├─ Write tests? → .meta.tests_sandbox/
├─ Use/create tools? → .meta.development_tools/
└─ Check workflows? → .meta.project_development/WORKFLOWS.md
```

## Quality Gates

- **Check `git log`** before any change
- **Work in `.meta.sandbox/`** for code changes
- **Ensure all tests pass** (use `.meta.tests_sandbox/` if applicable)
- **Document changes** in sandbox docs
- **Never commit production changes** directly

## Tools Available

### Core Tools
`read`, `glob`, `bash`, `edit`, `write`, `task`

## Common Scenarios

- **Add Feature**: Use sandbox, write tests, then merge
- **Fix Bug**: Reproduce in sandbox, test, then merge
- **Refactor**: Copy to sandbox, refactor, test, merge

## Available Skills

- `meta-harness-optimize` - Token optimization and structure analysis
- `meta-harness-reflection` - Capability testing and assessment
- `python-static-analysis` - Code quality and type checking
- `find-skills` - Discover and install new skills

---

## Meta Harness Projects (User Tasks)

### Quick Projects (30 min - 1 hr)

| Project | Description | Directory | Output |
|---------|-------------|-----------|--------|
| **Token Audit** | Analyze token usage in docs | `.meta.sandbox/` | Token report |
| **Archive Old Experiments** | Clean up completed experiments | `.meta.experiments/` | Organized directory |
| **Consolidate Docs** | Merge redundant documentation | `.meta.tools/` | Single guide |
| **Monthly Health Check** | Review harness health | `.meta.reflection/` | Health report |

### Medium Projects (1-3 hrs)

| Project | Description | Directory | Output |
|---------|-------------|-----------|--------|
| **Documentation Compression** | Compress verbose docs (30-50%) | `.meta.sandbox/` | Optimized docs |
| **Structure Analysis** | Review and optimize structure | `.meta.sandbox/` | Structure plan |
| **Workflow Templates** | Create workflow templates | `.meta.project_development/` | Templates |
| **KB Population** | Populate knowledge base | `.meta.knowledge_base/` | Updated KB |

### Advanced Projects (3+ hrs)

| Project | Description | Directory | Output |
|---------|-------------|-----------|--------|
| **Full Optimization** | All workflows end-to-end | Multiple | Comprehensive report |
| **Skill Development** | Create new Meta Harness skill | `.meta.experiments/` | New skill |
| **Workflow Enhancement** | Improve existing workflows | `.meta.project_development/` | Enhanced workflows |
| **Capability Assessment** | Run reflection tests | `.meta.reflection/` | Assessment report |

### How to Start

**Decision Tree:**
```
Need to...
├─ Save tokens? → meta token audit
├─ Clean up? → meta archive experiments
├─ Improve docs? → meta compress docs
├─ Test capability? → meta test capability
└─ Full optimization? → meta optimize all
```

---

## Knowledge Base User Commands

This are prompt shortcuts that you must run when the User call it.


#### Population Commands
| Command | Description |
|---------|-------------|
| `meta kb populate both` | Populate both KBs (full refresh) |
| `meta kb populate meta` | Populate Meta Harness KB only |
| `meta kb populate agentx` | Populate Agent-X KB only |

#### Search & Query Commands
| Command | Description |
|---------|-------------|
| `meta kb search "TDD workflow"` | Search KB for patterns |
| `meta kb ask "Where should I write tests?"` | Ask question with RAG |
| `meta kb stats` | Show KB statistics |

#### Knowledge Management Commands
| Command | Description |
|---------|-------------|
| `meta kb add pattern workflow "Title" "Finding" "Solution"` | Add new entry |
| `meta kb correct 123 "Outdated" "New finding"` | Correct existing entry |
| `meta kb evolve` | Cleanup old entries |

#### Maintenance Commands
| Command | Description |
|---------|-------------|
| `meta token audit` | Analyze token usage |
| `meta archive experiments` | Archive old experiments |
| `meta health check` | Run harness health check |
| `meta compress docs` | Compress documentation |
| `meta structure analysis` | Analyze structure |

### Project Commands

#### Quick Projects (30 min - 1 hr)
- `meta token audit` - Analyze token usage
- `meta archive experiments` - Clean up old experiments
- `meta consolidate docs` - Merge redundant docs
- `meta health check` - Monthly health check

#### Medium Projects (1-3 hrs)
- `meta compress docs` - Compress documentation (30-50%)
- `meta structure analysis` - Review directory structure
- `meta create workflows` - Create workflow templates
- `meta populate kb` - Populate knowledge base

#### Advanced Projects (3+ hrs)
- `meta optimize all` - Full optimization
- `meta create skill` - Create new Meta Harness skill
- `meta enhance workflows` - Improve existing workflows
- `meta test capability` - Run reflection tests

### Decision Tree

```
Need to...
├─ Populate KB? → meta kb populate both
├─ Search KB? → meta kb search "query"
├─ Add knowledge? → meta kb add pattern ...
├─ Check health? → meta health check
├─ Save tokens? → meta token audit
├─ Clean up? → meta archive experiments
├─ Compress docs? → meta compress docs
├─ Analyze structure? → meta structure analysis
└─ Create skill? → meta create skill
```

**Full Documentation**: [`.meta.tools/META_COMMANDS.md`](.meta.tools/META_COMMANDS.md)

### Example Workflow

```python
from .meta.tools import kb_ask, kb_search, kb_add_entry, kb_stats

# 1. Check stats
print(kb_stats())

# 2. Search
print(kb_search("TDD", top_k=3))

# 3. Ask
answer = kb_ask("Where should I write tests?")
print(answer)

# 4. Add knowledge
kb_add_entry("pattern", "workflow", "Bug Fix", 
             "Reproduce in sandbox", "Test → Fix → Verify")

# 5. Verify
print(kb_search("bug fix", top_k=2))
```

### Database Location

`.meta.data/kb-meta/knowledge-meta.db` (auto-initialized)

**Full Guide**: [`.meta.tools/KB_GUIDE.md`](.meta.tools/KB_GUIDE.md)

---

## Resources

### Core Documentation
- [`AGENTS.md`](AGENTS.md) - Entry point (read first)
- [`META_HARNESS.md`](META_HARNESS.md) - Master documentation
- [`WORKFLOWS.md`](.meta.project_development/WORKFLOWS.md) - Workflow patterns
- [`QUICK_REFERENCE.md`](.meta.project_development/QUICK_REFERENCE.md) - At-a-glance guide

### Meta Commands & Tools
- [`META_COMMANDS.md`](.meta.tools/META_COMMANDS.md) - All meta commands reference
- [`KB_GUIDE.md`](.meta.tools/KB_GUIDE.md) - Knowledge base detailed guide
- [`OPTIMIZATION_REPORT.md`](.meta.sandbox/optimization_report.md) - Latest optimization results

### Directories
- [`.meta.project_development/`](.meta.project_development/) - Rules, standards, workflows
- [`.meta.sandbox/`](.meta.sandbox/) - Safe workspace
- [`.meta.experiments/`](.meta.experiments/) - Experimental features
- [`.meta.tests_sandbox/`](.meta.tests_sandbox/) - TDD workspace
- [`.meta.tools/`](.meta.tools/) - Development tools

## Resources

- [`AGENTS.md`](AGENTS.md)
- [`META_HARNESS.md`](META_HARNESS.md)
- [`WORKFLOWS.md`](.meta.project_development/WORKFLOWS.md)

---
**Version**: 2.2.0 (2026-04-25) - Updated content
**Maintained by**: opencode AI agent
**License**: Apache 2.0
