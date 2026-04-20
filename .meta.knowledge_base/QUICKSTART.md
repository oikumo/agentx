# Quick Start - Knowledge Base

## TL;DR

```bash
# Add knowledge
python .meta.knowledge_base/kb.py add --type pattern --category workflow --title "My Pattern" --finding "What I found" --solution "How to solve"

# Search
python .meta.knowledge_base/kb.py search "query"

# Ask (RAG)
python .meta.knowledge_base/kb.py ask "question?"

# Correct
python .meta.knowledge_base/kb.py correct --entry PATTERN-XXX --reason "Why" --new-finding "New info"

# Stats
python .meta.knowledge_base/kb.py stats
```

## What This Does

1. **Stores key findings** from your development work
2. **Auto-corrects** when you discover better approaches
3. **Evolves** - unused knowledge decays, good knowledge surfaces
4. **RAG-ready** - retrieves context for LLM prompts

## Example Session

```bash
# 1. You finish TDD workflow - store it
python .meta.knowledge_base/kb.py add \
  --type pattern \
  --category workflow \
  --title "TDD in .meta.tests_sandbox" \
  --finding "Tests must be written before code" \
  --solution "1. Write test 2. Implement 3. Verify" \
  --context "When implementing features" \
  --confidence 0.95

# 2. Later you discover better approach - correct it
python .meta.knowledge_base/kb.py correct \
  --entry PAT-XXXX \
  --reason "Found better workflow" \
  --new-finding "Use .meta.experiments for prototyping first"

# 3. Next time, ask before starting
python .meta.knowledge_base/kb.py ask "Where should I write tests?"

# 4. Check stats
python .meta.knowledge_base/kb.py stats
```

## Entry Types

- **pattern**: Recurring solution (TDD workflow)
- **finding**: New discovery (uv is faster)
- **correction**: Error fix (workflow changed)
- **decision**: Architecture choice (SQLite over PG)

## Confidence

- Starts at 0.5 (uncertain)
- Increases with reuse (+0.05)
- Decreases with corrections (-0.20)
- Decays if unused (-0.05 per 30 days)
- Archive if < 0.3

## Integration

Add to your workflow:

```python
# Before starting work
from rag_integration import KnowledgeBaseRAG
rag = KnowledgeBaseRAG()
results = rag.retrieve("Where do I write tests?")
# Use results to inform your approach
```

---

**No dependencies required** - uses stdlib only (SQLite FTS5)
**Optional**: Install `sentence-transformers` for semantic search
