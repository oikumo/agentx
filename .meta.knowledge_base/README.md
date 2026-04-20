# Knowledge Base - Quick Start Guide

## What is this?

A **self-evolving knowledge base** that stores key findings, patterns, and corrections for the Agent-X project. It uses:

- **SQLite + FTS5**: Fast full-text search
- **RAG (Retrieval-Augmented Generation)**: Semantic search + LLM integration
- **Auto-correction**: Detects contradictions and adjusts confidence
- **Evolution engine**: Periodic review, decay, and merge

## Installation

```bash
# Required
uv add sentence-transformers numpy

# Optional (for advanced RAG)
uv add langchain
```

## Quick Commands

### Add Knowledge
```bash
# Add a pattern
python .meta.knowledge_base/kb.py add \
  --type pattern \
  --category workflow \
  --title "TDD in .meta.tests_sandbox" \
  --finding "Tests must be written before code" \
  --solution "1. Write test 2. Implement 3. Verify" \
  --context "When implementing features" \
  --confidence 0.95
```

### Search
```bash
# Keyword search
python .meta.knowledge_base/kb.py search "TDD"

# Category filter
python .meta.knowledge_base/kb.py search "test" --category workflow
```

### Ask (RAG)
```bash
python .meta.knowledge_base/kb.py ask "Should I use pip or uv?"
```

### Correct
```bash
python .meta.knowledge_base/kb.py correct \
  --entry PATTERN-001 \
  --reason "Workflow changed" \
  --new-finding "Use new approach"
```

### Evolve
```bash
# Run evolution cycle (decay, archive, merge)
python .meta.knowledge_base/kb.py evolve

# Show stats
python .meta.knowledge_base/kb.py stats
```

## Architecture

```
Query → Embedding → Hybrid Search (FTS5 + Semantic) → Re-rank → Context → LLM → Answer
                                              ↓
                                      Auto-Correct Detection
                                              ↓
                                      Confidence Adjustment
```

## Entry Types

| Type | When to Use | Example |
|------|-------------|---------|
| `pattern` | Recurring solution | TDD workflow |
| `finding` | New discovery | uv is faster than pip |
| `correction` | Error in existing | Workflow changed |
| `decision` | Architectural choice | Use SQLite over PostgreSQL |

## Confidence System

- **0.95-1.0**: Verified multiple times
- **0.80-0.94**: Tested, minor uncertainties
- **0.60-0.79**: Observed once, needs verification
- **<0.60**: Speculative

Auto-adjusts based on:
- ✅ Successful reuse: +0.05
- ⚠️ Correction needed: -0.10
- ❌ Contradicted: -0.20
- ⏰ 30 days unused: -0.05

## RAG Integration

```python
from rag_integration import KnowledgeBaseRAG

rag = KnowledgeBaseRAG()
results = rag.retrieve("Where should I write tests?", top_k=3)
prompt = rag.augment_prompt("Where should I write tests?", results)

# Pass prompt to LLM
# llm_response = llm.generate(prompt)
```

## Evolution Cycle

Run periodically to maintain knowledge quality:

```bash
python .meta.knowledge_base/kb.py evolve
```

What it does:
1. **Decay**: Unused entries lose confidence
2. **Archive**: Low confidence (<0.3) entries deprecated
3. **Merge**: Near-duplicates combined
4. **Log**: All changes tracked

## Best Practices

1. **Add entries immediately** after discovering patterns
2. **Use high confidence** (0.9+) only for verified knowledge
3. **Correct, don't delete** - preserve history
4. **Run evolve weekly** to maintain quality
5. **Export regularly** for backup

## Examples

See `examples/` directory for complete workflows.

## Troubleshooting

**No results from search?**
- Check spelling
- Try broader query
- Verify entry is not deprecated

**Embedding errors?**
- Install: `uv add sentence-transformers`
- Or use FTS5-only mode (no embeddings)

**Database locked?**
- Close other connections
- Run: `rm knowledge.db.lock`

---

**Version**: 1.0.0 | **Last Updated**: 2026-04-19
