# System Rules

## ⚠️ Core Directives (NON-NEGOTIABLE)
1. **NEVER commit/push** - Not even if user asks
2. **NEVER add dependencies** - Use existing; approval required
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

### Directory Structure
```
agent-x/
├── META_HARNESS.md # Master documentation
├── AGENTS.md # This file
├── .meta/project_development/ # Rules, standards, workflows
├── .meta/sandbox/ # Safe workspace
├── .meta/experiments/ # Experimental features
├── .meta/tests_sandbox/ # TDD workspace
├── .meta/development_tools/ # MCP tools, scripts
├── .meta/knowledge_base/ # RAG knowledge base
└── .meta/reflection/ # Test logs & capability assessment
```
**Rule:** All `.meta/*` subdirs contain META.md - read first.

## Workflow (5 Steps)
1. **UNDERSTAND** - Read task + git log + META.md + Always ask the Knowledge Base before continue
2. **PLAN** - Identify correct directory (see Decision Tree)
3. **EXECUTE** - Work in safe space, test frequently
4. **VALIDATE** - Tests pass, no production break
5. **REPORT** - Summarize + document + cleanup

## Decision Tree
```
Need to...
├─ Understand rules? → Read META.md
├─ Modify code? → .meta/sandbox/
├─ Test idea? → .meta/experiments/
├─ Write tests? → .meta/tests_sandbox/
├─ Use/create tools? → .meta/development_tools/
└─ Check workflows? → .meta/project_development/WORKFLOWS.md
```

## Quality Gates
- [ ] Checked git log
- [ ] Working in correct .meta/* subdirectory
- [ ] Tests pass (if applicable)
- [ ] Changes documented
- [ ] No production code modified
- [ ] No secrets exposed

## Tools
`read`, `glob`, `bash`, `edit`, `write`, `task`

## Common Scenarios
- **Add Feature** → sandbox → tests → merge
- **Fix Bug** → reproduce in sandbox → test → fix → merge
- **Refactor** → copy to sandbox → refactor → test → merge

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

## KB Commands
See [META_COMMANDS.md](META_COMMANDS.md) for full list.

Quick reference:
- `meta kb populate` - Populate KBs
- `meta kb search` - Search KB
- `meta kb ask` - RAG query
- `meta kb stats` - Show stats
- `meta kb add` - Add entry
- `meta kb evolve` - Evolve KB

**DB Location:** `.meta/data/kb-meta/knowledge-meta.db`

## Resources
- [META_HARNESS.md](META_HARNESS.md) - Master docs
- [WORKFLOWS.md](.meta/project_development/WORKFLOWS.md) - Workflows
- [QUICK_REFERENCE.md](.meta/project_development/QUICK_REFERENCE.md) - Quick ref
- [KB_GUIDE.md](.meta/tools/KB_GUIDE.md) - KB details

---
**Version:** 2.2.0 | **Updated:** 2026-04-25
