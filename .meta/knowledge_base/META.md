# Knowledge Base - Agent X

> **Purpose**: RAG knowledge storage for AI agents
> **Target**: AI agents (opencode)
> **Rule**: Always query KB before answering project-specific questions

---

## Purpose

Centralized knowledge storage for:
- Project-specific information
- Codebase patterns and conventions
- Workflow documentation
- Decision history
- Agent learnings

---

## Structure

```
.meta/knowledge_base/
├── META.md           # This file
├── entries/          # Knowledge entries
│   ├── YYYY-MM-DD-entry-id.md
│   └── ...
└── indexes/          # Search indexes
    └── vector.db     # Vector embeddings (if applicable)
```

---

## KB Commands

| Command | Purpose |
|---------|---------|
| `meta kb populate` | Populate KB from codebase |
| `meta kb` | Search entries |
| `meta kb ask` | RAG query |
| `meta kb stats` | Show statistics |
| `meta kb add` | Add new entry |
| `meta kb evolve` | Evolve KB structure |

**Note**: Commands require implementation in `.meta/development_tools/`

---

## Workflow

### Query Flow (Mandatory - Step 1 of any task)
```
1. Receive task
2. Query KB: "What is X?" / "How does Y work?"
3. Review relevant entries
4. Answer based on KB + codebase
5. If KB missing info → Add entry after completion
```

### Population Flow
```
1. Complete task successfully
2. Extract key learnings
3. Create dated entry in entries/
4. Update indexes if needed
5. Commit knowledge (not code)
```

---

## Entry Format

```markdown
# Entry ID: YYYY-MM-DD-topic

**Tags**: [tag1, tag2]
**Related**: [links to other entries]

## Context
Why this knowledge matters

## Content
The actual knowledge

## Examples
Code snippets or use cases

## References
- Links to source files
- Related decisions
```

---

## Rules

**DO**: Query before answering, add entries after tasks, keep entries concise, tag properly
**DON'T**: Store secrets, duplicate code, skip population, ignore outdated entries

---

## Maintenance

- **After each session**: Add new learnings
- **Weekly**: Review and prune outdated entries
- **Monthly**: Run `meta kb evolve` to optimize structure

---

## Integration

KB works with:
- `.meta/sandbox/` - Reference knowledge during modifications
- `.meta/tests_sandbox/` - Store test patterns
- `.meta/experiments/` - Document experimental findings
- `.meta/reflection/` - Store capability assessments

---

**Version**: 1.0.0 | **Lines**: 95
(End of file - total 95 lines)
