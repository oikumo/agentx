# Knowledge Base - Self-Evolving Project Knowledge (RAG + SQLite)

> **Purpose**: Store, retrieve, and evolve key findings using RAG + SQLite
> **Target**: AI agents (opencode)
> **Mechanism**: Vector-like embeddings + SQLite FTS5 + auto-correction
> **Mandatory**: Read before adding entries; use `kb.py` tool

---

## 1. Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Query: "How to handle TDD?"                            │
│  ↓                                                      │
│  1. Embed query (sentence-transformers)                │
│  2. Search SQLite FTS5 + cosine similarity              │
│  3. Retrieve top-k chunks with context                 │
│  4. Inject into LLM prompt                             │
│  5. LLM generates answer + suggests corrections        │
│  ↓                                                      │
│  Auto-evolve: New findings → Validation → Store        │
└─────────────────────────────────────────────────────────┘
```

### Components
- **SQLite DB**: `knowledge.db` with FTS5 virtual tables
- **Embeddings**: Cached in `embeddings_cache/` (avoid recomputation)
- **RAG Retriever**: Hybrid search (BM25 + semantic)
- **Auto-correct**: Contradiction detection + confidence adjustment
- **Evolution Engine**: Periodic review + merge + decay

---

## 2. Directory Structure

```
.meta.knowledge_base/
├── META.md                 # This file
├── knowledge.db            # SQLite database (FTS5 + embeddings)
├── kb.py                   # CLI tool for all operations
├── embeddings_cache/       # Cached embeddings (JSON)
├── evolution_log.json      # Auto-correction history
└── schemas/
    ├── v1_schema.sql       # Current schema
    └── migrations/         # Schema migrations
```

---

## 3. Knowledge Entry Schema

```sql
CREATE TABLE entries (
    id TEXT PRIMARY KEY,           -- e.g., "PATTERN-001"
    type TEXT NOT NULL,            -- pattern|finding|correction|decision
    category TEXT NOT NULL,        -- workflow|code|test|docs|tool
    title TEXT NOT NULL,           -- Concise title
    confidence REAL DEFAULT 0.5,   -- 0.0-1.0
    context TEXT,                  -- When/where this applies
    finding TEXT,                  -- What was discovered
    solution TEXT,                 -- How to handle it
    example TEXT,                  -- Code snippet or reference
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    reuse_count INTEGER DEFAULT 0,
    embedding BLOB                 -- Vector embedding (cached)
);

CREATE VIRTUAL TABLE entries_fts USING fts5(
    title, context, finding, solution, example,
    content='entries',
    content_rowid='rowid'
);

CREATE TABLE corrections (
    id TEXT PRIMARY KEY,
    entry_id TEXT REFERENCES entries(id),
    reason TEXT,
    new_finding TEXT,
    confidence_delta REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE relationships (
    from_id TEXT REFERENCES entries(id),
    to_id TEXT REFERENCES entries(id),
    type TEXT,                   -- references|contradicts|extends
    PRIMARY KEY (from_id, to_id, type)
);
```

---

## 4. Usage (kb.py Tool)

### Add Entry
```bash
python .meta.knowledge_base/kb.py add \
  --type pattern \
  --category workflow \
  --title "TDD in .meta.tests_sandbox" \
  --context "When implementing features" \
  --finding "Tests before code" \
  --solution "Write test → Implement → Verify"
```

### Search (RAG)
```bash
# Semantic search
python .meta.knowledge_base/kb.py search "how to test" --top-k 5

# With LLM answer (RAG)
python .meta.knowledge_base/kb.py ask "Should I use .meta.sandbox or .meta.experiments?"

# Filter by category
python .meta.knowledge_base/kb.py search "workflow" --category workflow
```

### Auto-Correct
```bash
# Add correction
python .meta.knowledge_base/kb.py correct \
  --entry PATTERN-005 \
  --reason "Workflow changed in v2.0" \
  --new-finding "Use .meta.experiments/ for prototyping"

# Auto-detect contradictions
python .meta.knowledge_base/kb.py detect-contradictions
```

### Evolution
```bash
# Run evolution cycle
python .meta.knowledge_base/kb.py evolve

# Show confidence changes
python .meta.knowledge_base/kb.py show-decay

# Merge duplicate entries
python .meta.knowledge_base/kb.py merge-duplicates
```

### Export/Import
```bash
# Export for backup
python .meta.knowledge_base/kb.py export --format json > kb_backup.json

# Import entries
python .meta.knowledge_base/kb.py import kb_backup.json
```

---

## 5. RAG Implementation

### Retrieval Strategy
1. **Query Embedding**: Convert query to vector (all-MiniLM-L6-v2)
2. **Hybrid Search**:
   - FTS5 for keyword match (BM25)
   - Cosine similarity for semantic match
   - Combine scores: `final = 0.3*bm25 + 0.7*semantic`
3. **Re-ranking**: Boost by confidence, recency, reuse_count
4. **Context Assembly**: Top-k chunks with metadata

### Prompt Template
```
You are an AI agent working on Agent-X project.
Use the following retrieved knowledge to answer:

[RETRIEVED KNOWLEDGE]
{context_chunks}

[QUESTION]
{user_query}

[ANSWER]
```

### Auto-Correction Detection
```python
# Detect contradiction
if similarity(new_finding, existing_finding) < 0.3:
    # Low similarity = potential contradiction
    create_correction_entry()
    adjust_confidence(existing_id, delta=-0.2)
```

---

## 6. Auto-Correction Mechanism

### Triggers
1. **Manual correction**: User adds correction entry
2. **Contradiction detection**: New entry conflicts with existing
3. **Confidence decay**: Unused entries lose confidence over time
4. **Validation failure**: Entry proven wrong in practice

### Correction Workflow
```
1. Detect issue (manual or automatic)
   ↓
2. Create CORRECTION-XXX entry
   ↓
3. Link to original entry
   ↓
4. Adjust confidence: old_entry.confidence -= 0.2
   ↓
5. If confidence < 0.3: mark as deprecated
   ↓
6. Log to evolution_log.json
```

### Confidence Adjustment Rules
| Event | Delta | Cap |
|-------|-------|-----|
| Successful reuse | +0.05 | max 1.0 |
| Correction needed | -0.10 | min 0.0 |
| Contradicted by new finding | -0.20 | min 0.0 |
| 30 days unused | -0.05 | min 0.0 |
| 90 days unused | -0.15 | min 0.0 |

---

## 7. Evolution Engine

### Periodic Tasks
- **Daily** (on session start):
  - Decay confidence for unused entries
  - Detect contradictions in new entries
  - Log to `evolution_log.json`

- **Weekly**:
  - Merge near-duplicate entries (similarity > 0.95)
  - Archive low-confidence entries (< 0.3)
  - Validate all references

- **Monthly**:
  - Review all corrections
  - Update patterns based on corrections
  - Generate evolution report

### Evolution Log Format
```json
{
  "timestamp": "2026-04-19T20:30:00Z",
  "type": "correction|merge|decay|archive",
  "entry_id": "PATTERN-001",
  "action": "confidence_adjusted",
  "old_value": 0.95,
  "new_value": 0.85,
  "reason": "30 days unused"
}
```

---

## 8. LLM Optimization

### Token Efficiency
- **Chunking**: Split large entries into 256-token chunks
- **Compression**: Use abbreviations (TDD, ADR, KB)
- **Deduplication**: Shared context stored once
- **Lazy loading**: Only load relevant chunks

### Embedding Strategy
- **Model**: `sentence-transformers/all-MiniLM-L6-v2` (fast, small)
- **Dimension**: 384 (balance quality vs size)
- **Cache**: Store in `embeddings_cache/` to avoid recomputation
- **Batch**: Embed multiple entries together

### Retrieval Optimization
```sql
-- Hybrid search query
SELECT e.*, 
       (0.3 * bm25(entries_fts, e.id) + 0.7 * cosine_similarity(e.embedding, :query_embedding)) as score
FROM entries e
WHERE e.confidence > 0.6
ORDER BY score DESC
LIMIT 5;
```

---

## 9. Example Workflow

### Scenario: Agent discovers new pattern
```bash
# 1. Agent finishes task, has insight
python .meta.knowledge_base/kb.py add \
  --type pattern \
  --category tool \
  --title "Use uv for dependency management" \
  --context "When adding Python packages" \
  --finding "uv is faster and more reliable than pip" \
  --solution "Always use 'uv add package' instead of 'pip install'" \
  --example "uv add requests --dev"

# 2. System auto-generates embedding, stores in DB
# 3. Next time agent asks about dependencies, RAG retrieves this
# 4. Agent uses pattern, confidence increases
# 5. If uv changes behavior, correction adjusts entry
```

---

## 10. Integration with Harness

### With AGENTS.md
- KB referenced in decision tree
- Patterns inform workflow choices
- Corrections update AGENTS.md if rules change

### With META_HARNESS.md
- High-level patterns documented in both
- KB provides detailed, queryable knowledge
- Bidirectional links

### With Workflows
- Workflow steps reference KB entries by ID
- KB corrections trigger workflow updates
- Findings inform new workflows

---

## 11. Scripts Reference

| Command | Description |
|---------|-------------|
| `kb.py add` | Add new entry |
| `kb.py search` | Semantic search |
| `kb.py ask` | RAG query with LLM answer |
| `kb.py correct` | Add correction |
| `kb.py evolve` | Run evolution cycle |
| `kb.py export` | Export to JSON |
| `kb.py import` | Import from JSON |
| `kb.py stats` | Show statistics |
| `kb.py validate` | Validate all entries |

---

## 12. Dependencies

```txt
# Core
sqlite3 (built-in)
sentence-transformers
numpy

# Optional (for LLM features)
langchain
chromadb (alternative to SQLite for vectors)
```

Install:
```bash
uv add sentence-transformers numpy
```

---

**Version**: 1.0.0 | **Lines**: 350
**Last Updated**: 2026-04-19 | **Maintained By**: opencode AI agent
