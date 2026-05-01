# Meta Harness - Agent X

> **Purpose**: Master guide for Meta Harness (lazy-loaded)  
> **Target**: AI agents (opencode)  
> **Mandatory**: Read section 1, then reference only what you need

---

## 1. What is the Meta Harness?

Structured project organization for AI-assisted development:
- **Safe spaces**: Work without affecting production
- **Clear separation**: Production / experimentation / testing
- **Feature organization**: Features tracked by state (planned/wip/ok)
- **Structured workflows**: Consistent, high-quality output
- **Comprehensive docs**: At every level
- **Work notebook**: Simple reminder via `WORK.md`
- **Change logging**: All structural changes logged in `.meta/LOG.md`

**Directory layout**: See [`.meta/project_development/STRUCTURE.md`](.meta/project_development/STRUCTURE.md)

---

**Core Directives**: See [AGENTS.md](AGENTS.md) for the complete list of non-negotiable directives.

---

## 3. Quick Decision Tree

```
Need to...
├─ Understand rules? → Read relevant META.md
├─ Add/modify feature? → features/ (planned/ → wip/ → ok/)
├─ Modify code? → .meta/sandbox/
├─ Test new idea? → .meta/experiments/
├─ Write tests? → .meta/tests_sandbox/
├─ Test agent? → test_automated/
├─ Use/create tools? → .meta/development_tools/
└─ Check workflows? → .meta/project_development/WORKFLOWS.md
```

---

## 4. Standard Workflow (5 Steps)

```
1. UNDERSTAND: Read task + git log + relevant META.md
2. PLAN: Identify correct directory (see section 3)
3. EXECUTE: Work in safe space, test frequently
4. VALIDATE: All tests pass, no production break
5. REPORT: Summarize + document + cleanup
```

**Work Notebook**: Agent updates [WORK.md](WORK.md) as a reminder of your current task

**Detailed workflows**: [`.meta/project_development/WORKFLOWS.md`](.meta/project_development/WORKFLOWS.md)

---

## 5. Quality Gates

Before completion:
- [ ] Read relevant META.md
- [ ] Checked `git log`
- [ ] Correct directory used
- [ ] TDD followed (if applicable)
- [ ] Tests pass
- [ ] Documented changes
- [ ] Workspace clean
- [ ] No secrets exposed
- [ ] No production code modified

---

## 6. Documentation Standards

### META.md Files (Required Structure)
- Purpose statement (1 line)
- Target audience
- Mandatory rules (bullets)
- Structure overview
- Usage guidelines
- Examples (if needed)

### Session Documentation
- Dated folders
- Purpose + goals
- What was tried
- Successes / failures
- Next steps

### Change Logging (`.meta/LOG.md`)
**MANDATORY**: All structural changes to META HARNESS must be logged

**When to log**:
- Structural changes to META HARNESS
- New directives added
- Workflow modifications
- New test procedures
- Documentation reorganization
- Tool/script additions

**Log entry format**:
```markdown
## [YYYY-MM-DD] Brief Description

**Type**: Feature | Bugfix | Optimization | Documentation  
**Version**: X.X.X  
**Agent**: [agent name]  
**User Request**: [description]

### Changes Made
[List changes]

### Validation
[Test results]

### Files Modified/Created
[Table of files]

### Rationale
[Why this change]
```

**See**: [`.meta/LOG.md`](.meta/LOG.md) for complete logging rules and examples

---

## 7. AI Agent Responsibilities

**MUST**: Read META.md first, work in correct directories, follow TDD, test thoroughly, document, respect directives  
**SHOULD**: Be proactive, suggest improvements, keep clean, share learnings  
**MUST NOT**: Modify production, skip tests, ignore META.md, leave mess, commit without permission

---

## 8. Directory Quick Reference

| Directory | When to Use | META.md |
|-----------|-------------|---------|
| `.meta/LOG.md` | META HARNESS change log (auto-updated by agent) | N/A |
| `WORK.md` | Current work reminder (auto-updated by agent) | N/A |
| `features/` | AgentX features organized by state | [Link](features/META.md) |
| `features/planned/` | Features planned but not started | [Link](features/META.md) |
| `features/wip/` | Features in development (Work In Progress) | [Link](features/META.md) |
| `features/ok/` | Completed features ready for use | [Link](features/META.md) |
| `.meta/project_development/` | Rules, standards, workflows | [Link](.meta/project_development/META.md) |
| `.meta/experiments/` | Test new libraries, prototype | [Link](.meta/experiments/META.md) |
| `.meta/sandbox/` | Modify code safely | [Link](.meta/sandbox/META.md) |
| `.meta/tests_sandbox/` | TDD (Kent Beck) | [Link](.meta/tests_sandbox/META.md) |
| `.meta/development_tools/` | Development tools, scripts | [Link](.meta/development_tools/META.md) |
| `.meta/knowledge_base/` | RAG knowledge storage | [Link](.meta/knowledge_base/META.md) |
| `.meta/reflection/` | Test logs & capability assessment | [Link](.meta/reflection/README.md) |
| `test_automated/` | Automated agent tests (reflection tests) | N/A |

---

## 9. Maintenance

**Regular**: Clean old experiments, archive sessions, update META.md, remove unused tools
**Monthly**: 
- Run health check (see skill: `optimize-meta-harness`)
- Run capability test (see skill: `meta-harness-reflection`)

---

## 10. Resources

| Resource | Purpose |
|----------|---------|
| [`AGENTS.md`](AGENTS.md) | Entry point (read first) |
| [`README.md`](README.md) | Project overview |
| [`DIRECTIVES.md`](.meta/project_development/DIRECTIVES.md) | Core rules (6 directives) |
| [`WORKFLOWS.md`](.meta/project_development/WORKFLOWS.md) | Workflow patterns |
| [`QUICK_REFERENCE.md`](.meta/project_development/QUICK_REFERENCE.md) | At-a-glance guide |
| [`.meta/reflection/README.md`](.meta/reflection/README.md) | Reflection test documentation |

---

**Version**: 2.3.1 (WORK.md moved to root folder) | **Lines**: 155 (reduced from 368, ~60% token savings)
**Last Updated**: 2026-04-19 | **Maintained By**: opencode AI agent
