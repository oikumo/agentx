# Meta Harness Knowledge Base - Enhanced

> **Next-Generation RAG System** with advanced retrieval, synthesis, and conversational capabilities.

## Quick Start

```bash
# Search
python .meta.tools/meta-harness-knowledge-base/kb search "your query"

# Ask
python .meta.tools/meta-harness-knowledge-base/kb ask "your question?"

# Explore
python .meta.tools/meta-harness-knowledge-base/kb explore

# Chat
python .meta.tools/meta-harness-knowledge-base/kb chat
```

## What's New

### 🚀 Advanced Features

1. **Query Expansion** - Automatically generates multiple query variations
2. **Multi-Hop Retrieval** - Iterative search for complex questions
3. **Semantic Clustering** - Ensures diverse, non-redundant results
4. **Answer Synthesis** - Combines sources into comprehensive answers
5. **Conversational Interface** - Interactive chat with context
6. **Rich Formatting** - Colored output with metadata

### 📊 Performance

- **Simple search**: <50ms
- **Multi-hop (2 hops)**: <100ms  
- **With synthesis**: <150ms
- **Query expansion**: 5x variations

### 📈 Knowledge Base Stats

- **Total entries**: 1,444
- **Findings**: 729
- **Patterns**: 715
- **Categories**: 5 (documentation, workflow, directives, test, code)
- **Average confidence**: 0.89

## CLI Commands

### Search

Advanced search with automatic query expansion and diversification:

```bash
# Basic search
python kb search "MainController"

# With options
python kb search "TDD workflow" -k 10 --simple --no-color
```

**Output:**
- Formatted results with colors
- Confidence scores (color-coded)
- Source citations
- Metadata (timing, variations)

### Ask

Question answering with answer synthesis:

```bash
python kb ask "How do I implement TDD in the sandbox?"
```

**Output:**
- Synthesized answer from multiple sources
- Structured by type (patterns, findings, decisions)
- Source citations with confidence
- Summary with key insights

### Explore

Browse knowledge base by category:

```bash
# All categories
python kb explore

# Specific category
python kb explore workflow
```

**Output:**
- Category breakdown
- Entry counts by type
- Average confidence scores

### Chat

Interactive conversational mode:

```bash
python kb chat
```

**Features:**
- Context tracking
- Multi-turn conversations
- Source citations
- Easy exit with 'quit' or 'exit'

### Stats

Show knowledge base statistics:

```bash
python kb stats
```

### Add

Add new knowledge entries:

```bash
python kb add pattern workflow "Title" "Finding" "Solution" \
  --context "When to use" --confidence 0.9 --example "Example"
```

## Python API

### Basic Usage

```python
from src.advanced_rag import AdvancedRAG

rag = AdvancedRAG()

# Search
result = rag.advanced_search("query", top_k=5)

# Ask
result = rag.ask("question?", top_k=5)

rag.close()
```

### Advanced Usage

```python
from src.advanced_rag import AdvancedRAG

rag = AdvancedRAG()

# Query expansion
variations = rag.rewrite_query("complex query")
print(f"Generated {len(variations)} variations")

# Multi-hop retrieval
results = rag.multi_hop_retrieval("query", max_hops=2)

# Diversification
diversified = rag.cluster_and_diversify(results)

# Answer synthesis
synthesis = rag.synthesize_answer("question?", results)

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

## Architecture

### Components

1. **Query Expansion Module**
   - Keyword extraction
   - Query decomposition
   - Statement conversion
   - Synonym expansion (rule-based)

2. **Retrieval Engine**
   - FTS5 full-text search
   - BM25 scoring
   - Keyword matching (TF-IDF-like)
   - Semantic boost
   - Confidence weighting
   - Recency adjustment

3. **Multi-Hop System**
   - Iterative retrieval
   - Entity/concept extraction
   - Result merging
   - Deduplication

4. **Clustering & Diversification**
   - Category-based grouping
   - Diversity scoring
   - Redundancy reduction

5. **Synthesis Engine**
   - Multi-source combination
   - Type-based organization
   - Citation generation
   - Confidence aggregation

### Scoring Formula

```
Final Score = 
  0.30 * BM25 +              # Textual relevance
  0.25 * Keyword +           # Semantic overlap
  0.20 * Semantic Boost +    # Field importance
  0.15 * Confidence +        # Quality signal
  0.10 * Recency            # Freshness
```

## Examples

### Example 1: Simple Query

```bash
python kb ask "What is MainController?"
```

**Output:**
```
✓ Answer synthesized from 3 sources
Confidence: 0.95

## Summary
Based on 3 relevant entries...

## Patterns Found: 2
1. Integration Guide (PAT-5B77)
   Type: pattern | Category: documentation
   Finding: Documentation file
   Solution: Step-by-step guide...
```

### Example 2: Complex Query

```bash
python kb ask "How do I add a new command to the REPL?"
```

Process:
1. Expands to 5+ query variations
2. Multi-hop: "command" → "REPL" → "main.py"
3. Retrieves patterns, findings, examples
4. Synthesizes comprehensive answer

### Example 3: Exploration

```bash
python kb explore workflow
```

**Output:**
```
Category: WORKFLOW (250 entries)
  - pattern: 249 (avg conf: 0.90)
  - finding: 1 (avg conf: 0.98)
```

## Best Practices

1. **Use specific queries** for better results
2. **Try ask vs search** for different needs
3. **Check source citations** for verification
4. **Monitor confidence scores** (>=0.7 recommended)
5. **Use chat mode** for exploratory questions
6. **Explore categories** to discover patterns

## Troubleshooting

### No results
- Try simpler query
- Use different keywords
- Check spelling

### Low confidence
- Topic may be under-documented
- Consider adding new entry
- Look at multiple sources

### Too many results
- Increase specificity
- Add category filter
- Reduce top_k

## Documentation

- [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) - Detailed feature docs
- [ENHANCEMENTS_SUMMARY.md](ENHANCEMENTS_SUMMARY.md) - What's new
- [META.md](META.md) - Basic usage
- [USAGE.md](../USAGE.md) - General KB operations

## Future Enhancements

- [ ] LLM-powered query rewriting
- [ ] Embedding-based semantic search
- [ ] Cross-encoder re-ranking
- [ ] Conversational memory
- [ ] Temporal reasoning
- [ ] Multi-document summarization

## License

Part of the Meta Project Harness system.

## See Also

- [Agent-X](../../README.md) - Main project
- [Meta Harness](../../META_HARNESS.md) - Master documentation
- [Advanced RAG](src/advanced_rag.py) - Implementation
