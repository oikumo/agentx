# Advanced RAG Features

## Overview

The Meta Harness Knowledge Base now includes **advanced RAG capabilities** powered by state-of-the-art retrieval and synthesis techniques.

## Features

### 1. Query Expansion & Rewriting

Automatically expands queries into multiple variations for better retrieval:

```python
from src.advanced_rag import AdvancedRAG

rag = AdvancedRAG()
query = "How do I implement TDD workflow in the sandbox?"

# Generates variations:
# - "How do I implement TDD workflow in the sandbox?"
# - "implement TDD workflow sandbox"
# - "TDD", "workflow", "sandbox", "implement"
# - "do implement TDD workflow in the"
# - "how TDD workflow in the sandbox"

variations = rag.rewrite_query(query)
```

**Benefits:**
- Better recall for complex queries
- Handles different query formulations
- Extracts key concepts automatically

### 2. Multi-Hop Retrieval

Performs iterative retrieval for complex questions:

```python
# First hop: "MainController"
# → Finds: MainController class definition
# 
# Second hop: Extracts "Session", "commands", "view"
# → Finds: Related Session, Command patterns
# 
# Result: Comprehensive coverage

results = rag.multi_hop_retrieval("MainController", max_hops=2)
```

**Use cases:**
- Complex architectural questions
- Understanding relationships
- Comprehensive topic exploration

### 3. Semantic Clustering & Diversification

Ensures diverse, non-redundant results:

```python
# Without diversification: 5 similar results
# With diversification: 5 results from different categories

diversified = rag.cluster_and_diversify(results)
```

**Benefits:**
- Broader coverage
- Reduces redundancy
- Better for exploratory queries

### 4. Advanced Search

Combines all techniques:

```python
result = rag.advanced_search(
    "TDD workflow sandbox",
    top_k=5,
    use_multi_hop=True,
    use_diversification=True
)

# Returns:
# - Query variations used
# - Multi-hop results
# - Diversified set
# - Metadata (timing, etc.)
```

### 5. Answer Synthesis

Generates comprehensive answers from retrieved results:

```python
result = rag.synthesize_answer(
    "What is MainController?",
    results
)

# Returns:
# - Structured answer
# - Source citations
# - Confidence scores
# - Organized by type
```

### 6. Conversational Interface

Interactive chat mode with context tracking:

```bash
python kb chat

You: What is MainController?
KB: [Synthesized answer with sources]

You: How does it relate to Session?
KB: [Contextual answer]
```

## CLI Usage

### Search

```bash
# Basic search
python kb search "query"

# With options
python kb search "query" -k 10 --simple --no-color

# Advanced (default)
python kb search "TDD workflow in sandbox"
```

### Ask

```bash
# Ask with synthesis
python kb ask "How do I implement TDD?"

# Simple retrieval
python kb ask "TDD" --simple
```

### Explore

```bash
# Explore all categories
python kb explore

# Explore specific category
python kb explore workflow
```

### Chat Mode

```bash
python kb chat
```

## API Reference

### AdvancedRAG Class

```python
from src.advanced_rag import AdvancedRAG

rag = AdvancedRAG()

# Query expansion
variations = rag.rewrite_query("query")

# Multi-hop retrieval
results = rag.multi_hop_retrieval("query", max_hops=2)

# Diversification
diversified = rag.cluster_and_diversify(results)

# Advanced search
result = rag.advanced_search("query", top_k=5)

# Ask with synthesis
result = rag.ask("question?", top_k=5)

rag.close()
```

### Convenience Functions

```python
from src.advanced_rag import advanced_search, advanced_ask

# Search
result = advanced_search("query", top_k=5)

# Ask
result = advanced_ask("question?", top_k=5)
```

## Configuration

### Scoring Weights

The hybrid search uses weighted scoring:

- **BM25**: 30% (textual relevance)
- **Keyword matching**: 25% (semantic overlap)
- **Semantic boost**: 20% (field importance)
- **Confidence**: 15% (quality signal)
- **Recency**: 10% (freshness)

### Retrieval Parameters

```python
result = rag.advanced_search(
    "query",
    top_k=5,              # Number of results
    use_multi_hop=True,   # Enable multi-hop
    use_diversification=True  # Enable diversification
)
```

## Performance

Typical retrieval times:
- Simple search: <50ms
- Multi-hop (2 hops): <100ms
- With synthesis: <150ms

## Examples

### Example 1: Simple Query

```bash
python kb ask "What is MainController?"
```

**Output:**
- Synthesized answer
- 3-5 sources cited
- Confidence score
- Structured format

### Example 2: Complex Query

```bash
python kb ask "How do I add a new command to the REPL?"
```

**Process:**
1. Query expansion (5 variations)
2. Multi-hop retrieval (commands, REPL, main.py)
3. Diversification (patterns, findings, decisions)
4. Synthesis with citations

### Example 3: Exploration

```bash
python kb explore workflow
```

**Output:**
- All workflow entries
- Grouped by type
- Average confidence
- Entry counts

## Best Practices

1. **Use specific queries**: More specific = better results
2. **Try different forms**: Ask vs Search for different needs
3. **Check sources**: Always verify with cited sources
4. **Use chat for exploration**: Iterative questioning works well
5. **Monitor confidence**: Low confidence = verify manually

## Troubleshooting

### No results found
- Try simpler query
- Use query expansion (automatic)
- Check spelling

### Too many results
- Increase specificity
- Add category filter
- Use top_k parameter

### Low confidence
- Check if topic is well-documented
- Look at multiple sources
- Consider adding new entry

## Future Enhancements

- [ ] LLM-powered query rewriting
- [ ] Cross-encoder re-ranking
- [ ] Semantic similarity with embeddings
- [ ] Temporal reasoning
- [ ] Multi-document synthesis
- [ ] Conversational memory

## See Also

- [META.md](META.md) - Basic usage
- [USAGE.md](../USAGE.md) - General KB operations
- [KB_POPULATION_GUIDE.md](../KB_POPULATION_GUIDE.md) - Population guide
