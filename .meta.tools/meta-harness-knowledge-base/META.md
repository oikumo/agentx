# Meta Harness Knowledge Base

> **Purpose**: Store Knowledge using RAG  
> **Target**: AI agents (opencode) and developers  
> **Rule**: Document and test all tools

---

## Purpose

The Meta Harness Knowledge Base is a Retrieval-Augmented Generation (RAG) system that stores and retrieves project knowledge for AI agents and developers. It provides context-aware answers to questions about the project's workflows, patterns, and best practices.

---

## Structure

```
.meta.tools/meta-harness-knowledge-base/
├── META.md             # This file
├── knowledge_base.py   # Entry point with search/ask/add functions
├── src/
│   └── rag_tool.py     # Core RAG implementation
└── pyproject.toml       # Dependencies
```

---

## Usage

### Search Knowledge
```python
# Search for relevant entries
result = kb_search("TDD workflow", top_k=3, category="workflow")
```

### Ask Questions
```python
# Get RAG-augmented response to a question
result = kb_ask("Where should I write tests?")
```

### Add Knowledge
```python
# Document new findings
result = kb_add_entry(
    entry_type="pattern",
    category="workflow",
    title="Feature Implementation",
    finding="Work in .meta.sandbox/",
    solution="Copy → Modify → Test"
)
```

### Correct Knowledge
```python
# Correct existing entries
result = kb_correct(entry_id, reason, new_finding)
```

### Maintenance
```python
# Run evolution cycle
result = kb_evolve()

# Get statistics
result = kb_stats()
```

---

## Entry Types

- **pattern**: Reusable solutions to common problems
- **finding**: Discovered insights or observations
- **correction**: Updates to existing knowledge
- **decision**: Architectural or design decisions

## Categories

- **workflow**: Process patterns and procedures
- **code**: Implementation patterns and practices
- **test**: Testing strategies and approaches
- **docs**: Documentation standards and practices
- **tool**: Tool usage and configuration
- **architecture**: System design principles

---

## Quality Gates

Before adding knowledge:
- [ ] Clear title and category
- [ ] Specific finding with context
- [ ] Actionable solution
- [ ] Appropriate confidence level (0.0-1.0)
- [ ] Example if applicable

---

## References

- Core implementation: [rag_tool.py](src/rag_tool.py)
- Usage examples: [knowledge_base.py](knowledge_base.py)
- Project workflows: [.meta.project_development/WORKFLOWS.md](../../.meta.project_development/WORKFLOWS.md)

---

**Version**: 2.1.0 (added RAG capabilities) | **Lines**: 85\n\n