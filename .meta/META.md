# .meta Directory

> **Purpose**: Safe spaces for experiments, knowledge, and tools

---

## Structure

| Directory | Purpose |
|-----------|---------|
| `experiments/` | Test new libraries, prototype |
| `knowledge_base/` | RAG knowledge storage |
| `reflection/` | Test logs & assessments |
| `tools/` | Development tools |
| `doc/` | Documentation archives |
| `data/` | Data storage |

## Rules

- **Each subdirectory** has its own `META.md`
- **All structural changes** are logged in `LOG.md`
- **Agents** read the relevant `META.md` before working in a directory
