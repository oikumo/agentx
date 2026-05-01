# Knowledge Base - Agent X

> **Purpose**: RAG knowledge storage for AI agents and developers
> **Target**: AI agents (opencode) and developers
> **Rule**: Always query KB before answering project-specific questions

---

## Overview

**Unified RAG system** storing project knowledge for AI agents. Provides context-aware answers about workflows, patterns, and best practices.

**Database**: `.meta/data/kb-meta/knowledge-meta.db` (unified Meta Harness + agentx)

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

---

## KB Commands

| Command | Purpose |
|---------|---------|
| `meta kb populate` | Populate KB from codebase |
| `meta kb ask` | RAG-augmented Q&A |
| `meta kb search` | Search entries |
| `meta kb stats` | Show statistics |
| `meta kb add` | Add new entry |
| `meta kb evolve` | Evolve KB structure |
| `meta kb correct` | Correct entry |

---

## Structure

```
.meta/knowledge_base/
├── META.md # This file
├── entries/ # Knowledge entries (YYYY-MM-DD-id.md)
└── indexes/ # Search indexes

.meta/data/kb-meta/
└── knowledge-meta.db # Unified KB database

.meta/tools/meta-harness-knowledge-base/
├── knowledge_base.py # Entry point (search/ask/add)
├── src/
│ ├── rag_tool.py # Core RAG
│ └── advanced_rag.py # Advanced features
└── pyproject.toml # Dependencies
```

---

## Workflow (MANDATORY)

```
1. Query KB: meta kb ask "<question>"
2. Review results (confidence scores)
3. Answer based on KB + codebase
4. If KB missing info → Add entry after completion
```

**See**: [`.meta/tools/meta-harness-knowledge-base/META.md`](../../.meta/tools/meta-harness-knowledge-base/META.md) for complete API documentation

---

## Entry Structure

```markdown
# Entry ID: YYYY-MM-DD-topic
**Tags**: [tag1, tag2]
**Related**: [links]

## Context
Why this knowledge matters

## Content
The actual knowledge

## Examples
Code snippets or use cases
```

### Entry Types

| Type | Purpose | Example |
|------|---------|---------|
| `pattern` | Reusable solutions | "Work in .meta/sandbox/" |
| `finding` | Discovered facts | "uv is faster than pip" |
| `correction` | Fixed knowledge | "Workflow changed in v2.0" |
| `decision` | Architectural choice | "Use SQLite over ChromaDB" |

---

## Maintenance

- **After each session**: Add new learnings
- **Weekly**: Review and prune outdated entries
- **Monthly**: Run `kb_evolve` to optimize structure

---

## Stats (Current)

- **Total entries**: 1,640
- **Patterns**: 809 (avg confidence: 0.94)
- **Findings**: 831 (avg confidence: 0.85)
- **Categories**: documentation, workflow, directives, code, test

---

**Version**: 3.1.0 (optimized) | **Lines**: 100 (reduced from 576, -83%)
