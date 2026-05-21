# Knowledge Base

> **Purpose**: RAG knowledge storage for AI agents
> **Target**: AI agents (opencode) and developers
> **Rule**: Always query KB before answering project-specific questions

---

## Quick Start

```bash
# Query KB (MANDATORY first step)
python3 .meta/tools/meta-harness-knowledge-base/kb ask "Where should I write tests?"

# Search entries
python3 .meta/tools/meta-harness-knowledge-base/kb search "TDD workflow" -k 3

# Show statistics
python3 .meta/tools/meta-harness-knowledge-base/kb stats

# Populate KB
python3 .meta/tools/meta-harness-knowledge-base/kb populate
```

## Commands

| Command | Purpose |
|---------|---------|
| python3 .meta/tools/meta-harness-knowledge-base/kb populate` | Populate KB from codebase |
| python3 .meta/tools/meta-harness-knowledge-base/kb ask` | RAG-augmented Q&A |
| python3 .meta/tools/meta-harness-knowledge-base/kb search` | Search entries |
| python3 .meta/tools/meta-harness-knowledge-base/kb stats` | Show statistics |

## Workflow (MANDATORY)

1. Query KB: python3 .meta/tools/meta-harness-knowledge-base/kb ask "<question>"`
2. Review results (confidence scores)
3. Answer based on KB + codebase
4. If KB missing info → Add entry after completion

---

**Version**: 3.0.0 (Simplified) | **Lines**: ~40
