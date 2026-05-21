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

| Directory | Purpose                           | Link |
|----------|-----------------------------------|------|
| `src/` | Production code                   | - |
| `tests/` | Unit and integration tests        | - |
| `.meta/` | META HARNESS current state        | [META.md](.meta/) |

---

## Standard Workflow (5 Steps)

1. **UNDERSTAND**: Read task + git log + relevant META.md
2. **PLAN**: Identify correct directory
3. **EXECUTE**: Work in safe space, test frequently
4. **VALIDATE**: Tests pass, no production break
5. **REPORT**: Summarize + document + cleanup

---
