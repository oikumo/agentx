# System Rules

## ⚠️ Core Directives (NON-NEGOTIABLE)
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

# Meta Commands

## KB Commands
- `meta kb populate` - Populate KBs
- `meta kb` - Search KB
- `meta kb ask` - RAG query
- `meta kb stats` - Show stats
- `meta kb add` - Add entry
- `meta kb correct` - Correct entry
- `meta kb evolve` - Evolve KB

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
├── .meta/project_development/ # Rules, standards, workflows
├── .meta/sandbox/ # Safe workspace
├── .meta/experiments/ # Experimental features
├── .meta/tests_sandbox/ # TDD workspace
├── .meta/development_tools/ # Development tools, scripts
├── .meta/knowledge_base/ # RAG knowledge base
└── .meta/reflection/ # Test logs & capability assessment
```
**Rule:** All `.meta/*` subdirs contain META.md - read first.

## Workflow (5 Steps)
1. **UNDERSTAND** - Read task + git log + **ALWAYS query KB first** + META.md
2. **PLAN** - Identify correct directory (see Decision Tree)
3. **EXECUTE** - Work in safe space, test frequently
4. **VALIDATE** - Tests pass, no production break
5. **REPORT** - Summarize + document + cleanup

## Decision Tree
```
Need to...
├─ Understand something? → Query KB first (.meta/knowledge_base/)
├─ Understand rules? → Read META.md
├─ Modify code? → .meta/sandbox/
├─ Test idea? → .meta/experiments/
├─ Write tests? → .meta/tests_sandbox/
├─ Use/create tools? → .meta/development_tools/
└─ Check workflows? → .meta/project_development/WORKFLOWS.md
```

## Quality Gates
- [ ] **Queried KB first** (mandatory before any task)
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
- [KB META.md](.meta/knowledge_base/META.md) - KB guidelines

---
**Version:** 2.2.0 | **Updated:** 2026-04-25
