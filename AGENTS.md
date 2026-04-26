# AGENTS.md - Agent-X System Agent Rules

## ⚠️ Core Directives (NON-NEGOTIABLE)

| # | Directive                                | What It Means                                             |
|---|------------------------------------------|-----------------------------------------------------------|
| 1 | **NEVER commit or push**                 | Not even if user asks                                     |
| 2 | **NEVER add dependencies**               | Use what exists; explicit approval required for exceptions |
| 3 | **NEVER modify .env**                    | Or any file likely to contain secrets/credentials         |
| 4 | **ALWAYS check git log**                 | Before making ANY changes                                 |
| 5 | **NEVER modify tests/**                  | Use .meta.tests_sandbox/ for new tests (requires approval) |
| 6 | **Use uv & pyproject.toml with python3** | For all dependency management; avoid pin drift            |
| 6 | **NEVER change the <root>/README.md **   | Modify it only when the User request it explicitly        |

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

### Knowledge Base Tools
...

```jade
# Additional guidelines omitted for brevity
```

## Common Scenarios

- **Add Feature**: Use sandbox, write tests, then merge
- **Fix Bug**: Reproduce in sandbox, test, then merge
- **Refactor**: Copy to sandbox, refactor, test, merge

## Available Skills

- `meta-harness-optimize`
- `meta-harness-reflection`

## Resources

- [`AGENTS.md`](AGENTS.md)
- [`META_HARNESS.md`](META_HARNESS.md)
- [`WORKFLOWS.md`](.meta.project_development/WORKFLOWS.md)

---
**Version**: 2.2.0 (2026-04-25) - Updated content
**Maintained by**: opencode AI agent
**License**: Apache 2.0
