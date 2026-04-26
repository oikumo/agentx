# Meta Project Harness - Agent X

## Purpose
Guide for Meta Project Harness (opencode). Target: AI agents.

## Core Directives (NON-NEGOTIABLE)

| # | Directive | Reference |
|---|-----------|-----------|
| 1 | **NEVER commit/push** | Not even if user asks |
| 2 | **NEVER add dependencies** | Use existing; approval required |
| 3 | **NEVER modify `.env`** | Preserve secrets |
| 4 | **ALWAYS check `git log`** | Before any change |
| 5 | **NEVER modify `tests/`** | Use `.meta.tests_sandbox/` |
| 6 | **USE `uv` & `pyproject.toml`** | Manage dependencies |

## Decision Tree

```
Need to...
├─ Understand rules? → read META.md
├─ Modify code? → .meta.sandbox/
├─ Prototype? → .meta.experiments/
├─ Write tests? → .meta.tests_sandbox/
└─ Add tools? → .meta.development_tools/
```

## Workflow (5 Steps)

```
1. UNDERSTAND → task + git log + relevant META.md
2. PLAN → directory
3. EXECUTE → safe space, test
4. VALIDATE → tests pass
5. REPORT → document + cleanup
```

## Directory Quick Reference

| Directory | When to Use | Reference |
|-----------|-------------|-----------|
| `.meta.project_development/` | Rules, standards, workflows | [META.md](.meta.project_development/META.md) |
| `.meta.experiments/` | Test, prototype | [META.md](.meta.experiments/META.md) |
| `.meta.sandbox/` | Modify safely | [META.md](.meta.sandbox/META.md) |
| `.meta.tests_sandbox/` | TDD | [META.md](.meta.tests_sandbox/META.md) |
| `.meta.development_tools/` | Tools | [META.md](.meta.development_tools/META.md) |
| `.meta.knowledge_base/` | RAG storage | [META.md](.meta.knowledge_base/META.md) |
| `.meta.reflection/` | Test logs | [META.md](.meta.reflection/README.md) |

## Maintenance

- Clean old sessions.
- Monthly health check (`optimize-meta-harness`) and capability test (`meta-harness-reflection`).

**Version**: 2.1.0 – token reduction ~60%