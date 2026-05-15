# Knowledge Base

> **Purpose**: RAG knowledge storage for AI agents
> **Target**: AI agents (opencode) and developers
> **Rule**: Always query KB before answering project-specific questions

---

## Quick Start

```bash
# Query KB (MANDATORY first step)
meta kb ask "Where should I write tests?"

# Search entries
meta kb search "TDD workflow" -k 3

# Show statistics
meta kb stats

# Populate KB
meta kb populate
```

## Commands

| Command | Purpose |
|---------|---------|
| `meta kb populate` | Populate KB from codebase |
| `meta kb ask` | RAG-augmented Q&A |
| `meta kb search` | Search entries |
| `meta kb stats` | Show statistics |

## Workflow (MANDATORY)

1. Query KB: `meta kb ask "<question>"`
2. Review results (confidence scores)
3. Answer based on KB + codebase
4. If KB missing info → Add entry after completion

---

**Version**: 3.0.0 (Simplified) | **Lines**: ~40
