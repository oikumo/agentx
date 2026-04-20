# Knowledge Base Usage Guide

## Complete Usage Examples

### 1. After Finishing a Task

You just completed implementing a feature using TDD. Store the pattern:

```bash
cd /home/oikumo/develop/projects/production/agent-x

python .meta.knowledge_base/kb.py add \
  --type pattern \
  --category workflow \
  --title "TDD for feature implementation" \
  --finding "Tests must be written before code following Kent Beck methodology" \
  --solution "1. Write failing test 2. Implement minimum code 3. Run tests 4. Refactor" \
  --context "When implementing new features or fixing bugs" \
  --confidence 0.95
```

### 2. Before Starting Work

Ask the knowledge base for guidance:

```bash
# Where should I work on this feature?
python .meta.knowledge_base/kb.py ask "Where should I write code for new features?"

# Which package manager to use?
python .meta.knowledge_base/kb.py ask "Should I use pip or uv?"

# What's the workflow for tests?
python .meta.knowledge_base/kb.py ask "How do I write tests?"
```

### 3. When You Discover Something Better

Correct existing knowledge:

```bash
python .meta.knowledge_base/kb.py correct \
  --entry PAT-XXXX \
  --reason "Workflow updated in v2.0" \
  --new-finding "Use .meta.experiments/ for prototyping instead of .meta.sandbox/"
```

### 4. Regular Maintenance

```bash
# Weekly evolution
python .meta.knowledge_base/kb.py evolve

# Check statistics
python .meta.knowledge_base/kb.py stats

# Export backup
python .meta.knowledge_base/kb.py export > kb_backup.json
```

## Integration with Your Workflow

### As an AI Agent (opencode)

```python
# At start of task
from rag_integration import KnowledgeBaseRAG

rag = KnowledgeBaseRAG()

# Ask for guidance
query = "Where do I implement this feature?"
results = rag.retrieve(query, top_k=3)
prompt = rag.augment_prompt(query, results)

# Use prompt with your LLM
# llm_response = llm.generate(prompt)

# After completing task, add new knowledge
# Run: kb.py add ...
```

### Manual Workflow

1. **Before task**: `kb.py ask "question"`
2. **During task**: Reference retrieved patterns
3. **After task**: `kb.py add` new findings
4. **Weekly**: `kb.py evolve`

## Common Queries

```bash
# Workflow questions
python kb.py search "where to write tests"
python kb.py search "TDD workflow"

# Tool questions  
python kb.py search "package manager"
python kb.py search "dependency management"

# Architecture questions
python kb.py search "safe spaces"
python kb.py search "meta directories"

# Pattern questions
python kb.py search "git log"
python kb.py search "production code"
```

## Entry Types Reference

### Pattern
Recurring solution to common problem.

```bash
python kb.py add \
  --type pattern \
  --category workflow \
  --title "My Pattern" \
  --finding "What happens" \
  --solution "How to handle it" \
  --context "When to use" \
  --confidence 0.95
```

### Finding
New discovery about codebase/workflow.

```bash
python kb.py add \
  --type finding \
  --category tool \
  --title "Tool Discovery" \
  --finding "Tool X is better than Y" \
  --solution "Use tool X instead" \
  --context "When choosing tools" \
  --confidence 0.90
```

### Decision
Architectural choice with consequences.

```bash
python kb.py add \
  --type decision \
  --category architecture \
  --title "Architecture Choice" \
  --finding "Why we chose X" \
  --solution "Use X for Y reason" \
  --context "When making similar choices" \
  --confidence 1.0
```

### Correction
Error in existing knowledge.

```bash
python kb.py correct \
  --entry PAT-XXX \
  --reason "Why correction needed" \
  --new-finding "Updated information"
```

## Confidence Guidelines

| Confidence | Meaning | When to Use |
|------------|---------|-------------|
| 1.0 | Certain | Core rules, verified multiple times |
| 0.95-0.99 | Very confident | Used successfully many times |
| 0.80-0.94 | Confident | Tested, works well |
| 0.60-0.79 | Somewhat confident | Observed once or twice |
| <0.60 | Uncertain | Speculative, needs verification |

## Troubleshooting

**No results from search?**
- Try broader query
- Check spelling
- Verify entry not deprecated
- Remove category filter

**Database errors?**
- Close other connections
- Check file permissions
- Reinitialize: `rm knowledge.db && python kb.py stats`

**Want semantic search?**
- Install: `uv add sentence-transformers numpy`
- Will automatically use embeddings

---

**Quick Reference**: See `QUICKSTART.md` for TL;DR
**Full Docs**: See `META.md` for complete documentation
