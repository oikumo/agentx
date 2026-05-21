# Meta Harness - Agent X

> **Purpose**: Master guide for project organization
> **Target**: AI agents

---

## What is the Meta Harness?

Structured project organization for AI-assisted development:
- **Safe spaces** - Experiment without affecting production
- **Clear separation** - Production / experimentation / testing
- **Structured workflows** - Consistent, high-quality output
- **Knowledge base** - RAG for project context

---

## Directory Quick Reference

| Directory | Purpose | Link |
|-----------|---------|------|
| `src/` | Production code | - |
| `tests/` | Unit and integration tests | - |
| `.meta/experiments/` | Test new libraries, prototype | [META.md](.meta/experiments/META.md) |
| `.meta/knowledge_base/` | RAG knowledge storage | [META.md](.meta/knowledge_base/META.md) |
| `.meta/reflection/` | Test logs & capability assessment | [META.md](.meta/reflection/META.md) |
| `.meta/tools/` | Development tools, scripts | [META.md](.meta/tools/META.md) |
| `.meta/doc/` | Documentation archives | - |
| `.meta/data/` | Data storage | - |

---

## Standard Workflow (5 Steps)

1. **UNDERSTAND**: Read task + git log + relevant META.md
2. **PLAN**: Identify correct directory
3. **EXECUTE**: Work in safe space, test frequently
4. **VALIDATE**: Tests pass, no production break
5. **REPORT**: Summarize + document + cleanup

---

## AI Agent Responsibilities

**MUST**: Read META.md first, work in correct directories, follow TDD, test thoroughly, document, respect directives
**SHOULD**: Be proactive, suggest improvements, keep clean, share learnings
**MUST NOT**: Modify production without permission, skip tests, ignore META.md, leave mess

---

**Version**: 3.0.0 (Simplified) | **Lines**: ~60
**Updated**: 2026-05-15 | **Maintained By**: opencode AI agent
