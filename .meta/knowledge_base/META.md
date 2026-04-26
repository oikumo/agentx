# Knowledge Base - Agent X

> **Purpose**: RAG knowledge storage for AI agents and developers
> **Target**: AI agents (opencode) and developers
> **Rule**: Always query KB before answering project-specific questions

---

## Overview

The Meta Harness Knowledge Base is a **unified Retrieval-Augmented Generation (RAG) system** that stores and retrieves project knowledge for AI agents and developers. It provides context-aware answers to questions about the project's workflows, patterns, and best practices.

The system has been **unified** - serving both Meta Harness patterns and agentx project knowledge in a single database (`.meta/data/kb-meta/knowledge-meta.db`).

---

## Architecture

### Structure

```
.meta/knowledge_base/
├── META.md                    # This file (consolidated documentation)
├── entries/                   # Knowledge entries
│   └── YYYY-MM-DD-entry-id.md
└── indexes/                   # Search indexes

.meta/data/kb-meta/
└── knowledge-meta.db          # Unified KB (Meta Harness + agentx)

.meta/tools/meta-harness-knowledge-base/
├── META.md                    # KB implementation docs
├── knowledge_base.py          # Entry point with search/ask/add functions
├── src/
│   ├── rag_tool.py            # Core RAG implementation
│   └── advanced_rag.py        # Advanced RAG features
└── pyproject.toml             # Dependencies
```

### Components

1. **`populate_kb.py`** - Core population logic
   - `KBPopulator` class
   - File discovery and traversal
   - Content analysis (Markdown + Python)
   - KB entry creation

2. **`meta_tools.py`** - User-facing API
   - `kb_clean_and_populate()` - Population wrapper
   - `kb_search()` - Search entries
   - `kb_ask()` - RAG-augmented Q&A
   - `kb_add_entry()` - Add knowledge
   - `kb_correct()` - Correct entries
   - `kb_evolve()` - Maintenance

3. **`knowledge_base.py`** - KB implementation
   - Search and retrieval
   - Query expansion
   - Multi-hop retrieval
   - Answer synthesis

---

## KB Commands

### Population Commands

| Command | Purpose |
|---------|---------|
| `meta kb populate` | Populate KB from codebase |
| `python .meta/tools/populate` | Populate both KBs (simple) |
| `python .meta/tools/populate meta` | Populate Meta only |
| `python .meta/tools/populate agentx` | Populate agentx only |

### Query Commands

| Command | Purpose |
|---------|---------|
| `meta kb` | Search entries |
| `meta kb ask` | RAG query |
| `meta kb stats` | Show statistics |
| `meta kb add` | Add new entry |
| `meta kb evolve` | Evolve KB structure |
| `meta kb correct` | Correct entry |

### CLI Usage

```bash
# Search
python .meta/tools/meta-harness-knowledge-base/kb search "TDD workflow" -k 5

# Ask with synthesis
python .meta/tools/meta-harness-knowledge-base/kb ask "Where should I write tests?"

# Explore by category
python .meta/tools/meta-harness-knowledge-base/kb explore
python .meta/tools/meta-harness-knowledge-base/kb explore workflow

# Interactive chat
python .meta/tools/meta-harness-knowledge-base/kb chat

# Statistics
python .meta/tools/meta-harness-knowledge-base/kb stats

# Add entry
python .meta/tools/meta-harness-knowledge-base/kb add pattern workflow "Title" "Finding" "Solution"
```

---

## KB Population

### What It Does

The population system automatically:

1. **Finds all `.meta*` directories** - `.meta/project_development`, `.meta/sandbox`, `.meta/experiments`, etc.
2. **Traverses all Markdown files** - Documentation, guides, META.md files
3. **Analyzes Python source code** - Classes, functions, imports in `src/`
4. **Extracts structured knowledge**:
   - Directives and rules (NEVER/ALWAYS/MUST)
   - Workflows and processes
   - Patterns and best practices
   - Source code architecture (classes, functions)
5. **Populates the unified KB** with categorized entries

### Usage

```bash
# Simple command (both KBs)
python .meta/tools/populate

# Specify which KB
python .meta/tools/populate both    # Both (default)
python .meta/tools/populate meta    # Meta Harness only
python .meta/tools/populate agentx  # agentx only

# Python API
from .meta.tools import meta_tools
result = meta_tools.kb_clean_and_populate(kb='both', verbose=True)
```

### Files Analyzed

**Root Documentation:**
- `AGENTS.md` - Agent rules
- `META_HARNESS.md` - Master documentation
- `README.md` - Project overview

**Meta Harness KB (`.meta*` directories):**
- `.meta/project_development/*.md` - All project docs
- `.meta/sandbox/META.md` - Sandbox rules
- `.meta/tests_sandbox/META.md` - TDD guidelines
- `.meta/experiments/*.md` - Experiment docs
- `.meta/reflection/*.md` - Reflection testing
- `.meta/development_tools/*.md` - Tool docs
- `.meta/tools/*.md` - Tool usage guides

**agentx KB (Source Code):**
- `src/**/*.py` - All Python source files
- `src/**/*.md` - Source documentation
- `doc/**/*.md` - Additional documentation

### When to Use

**Recommended:**
- Initial project setup
- After major documentation updates
- After code refactoring
- KB corruption recovery
- Periodic knowledge refresh

**Not recommended:**
- Adding single entries (use `kb_add_entry`)
- Minor doc updates (use `kb_evolve`)

---

## Python API

### Import Methods

```python
# Method 1: Direct import
import sys
sys.path.insert(0, '.meta/tools')
from meta_tools import kb_ask, kb_search, kb_stats

# Method 2: Module import
import sys
sys.path.insert(0, '.meta/tools')
import meta_tools

# Method 3: From within .meta/tools
from meta_tools import kb_ask, kb_search
```

### Core Functions

#### Search

```python
# Search for relevant entries
results = kb_search("TDD workflow", top_k=3, category="workflow")
print(results)
```

#### Ask (RAG-augmented)

```python
# Get RAG-augmented response
answer = kb_ask("Where should I write tests?", top_k=3)
print(answer)
```

#### Add Entry

```python
kb_add_entry(
    entry_type="pattern",
    category="workflow",
    title="Bug Fix Workflow",
    finding="Bugs should be reproduced in .meta/sandbox/",
    solution="Reproduce → Write failing test → Fix → Verify",
    context="When fixing reported bugs",
    confidence=0.9,
    example="Example usage"
)
```

#### Correct Entry

```python
kb_correct(
    entry_id="123",
    reason="Outdated information",
    new_finding="Updated workflow for v2.0"
)
```

#### Evolve (Maintenance)

```python
# Run evolution cycle: decay unused, archive low confidence
result = kb_evolve()
print(result)
```

#### Statistics

```python
stats = kb_stats()
print(stats)
# Output example:
# Total entries: 1640
# Patterns: 809 (avg confidence: 0.94)
# Findings: 831 (avg confidence: 0.85)
```

### Advanced RAG Features

```python
from src.advanced_rag import AdvancedRAG

rag = AdvancedRAG()

# Advanced search with multi-hop retrieval
result = rag.advanced_search(
    "TDD workflow",
    top_k=5,
    use_multi_hop=True,
    use_diversification=True
)

# Query expansion
variations = rag.rewrite_query("complex query")

# Multi-hop retrieval
results = rag.multi_hop_retrieval("query", max_hops=2)

rag.close()
```

### Complete Workflow Example

```python
import sys
sys.path.insert(0, '.meta/tools')
from meta_tools import kb_ask, kb_search, kb_add_entry, kb_stats

# 1. Check current stats
print("Current KB stats:")
print(kb_stats())

# 2. Search for existing patterns
print("\nSearching for TDD patterns:")
print(kb_search("TDD", top_k=3))

# 3. Ask a question
print("\nAsking about test location:")
answer = kb_ask("Where should I write tests?")
print(answer)

# 4. Add new knowledge
kb_add_entry(
    entry_type="pattern",
    category="workflow",
    title="Bug Fix Workflow",
    finding="Bugs should be reproduced in .meta/sandbox/",
    solution="Reproduce → Write failing test → Fix → Verify",
    context="When fixing reported bugs",
    confidence=0.9
)

# 5. Verify addition
print("\nSearching for bug fix patterns:")
print(kb_search("bug fix", top_k=2))
```

---

## Entry Structure

### Entry Format

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

### Database Entry Structure

```python
{
    "type": "pattern|finding|correction|decision",
    "category": "directives|workflow|documentation|source_code|...",
    "title": "Descriptive title",
    "finding": "What was found/discovered",
    "solution": "Extracted solution or pattern",
    "context": "Source file path / When this applies",
    "confidence": 0.80-1.0,
    "example": "Usage example or reference"
}
```

### Entry Types

| Type | Purpose | Example |
|------|---------|---------|
| `pattern` | Reusable solutions | "Work in .meta/sandbox/" |
| `finding` | Discovered facts | "uv is faster than pip" |
| `correction` | Fixed knowledge | "Workflow changed in v2.0" |
| `decision` | Architectural choice | "Use SQLite over ChromaDB" |

### Categories

- **workflow** - Process patterns and procedures
- **code** - Implementation patterns and practices
- **test** - Testing strategies and approaches
- **docs** - Documentation standards
- **tool** - Tool usage and configuration
- **architecture** - System design principles
- **directives** - NEVER/ALWAYS/MUST rules
- **source_code** - Python source analysis
- **class** - Class definitions
- **environment** - Environment setup

---

## Workflows

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

### Quality Gates

**Before adding knowledge:**
- [ ] Clear title and category
- [ ] Specific finding with context
- [ ] Actionable solution
- [ ] Appropriate confidence level (0.0-1.0)
- [ ] Example if applicable

**Before population:**
- [ ] Verify project root directory
- [ ] Check `.meta*` directories exist
- [ ] Ensure `src/` directory present
- [ ] Confirm write access to KB databases

**After population:**
- [ ] Check entry counts (should be 50-200+)
- [ ] Verify KB stats with `kb_stats()`
- [ ] Test search with `kb_search("test")`
- [ ] Validate entries have proper structure

---

## Rules

### DO:
- Query before answering
- Add entries after tasks
- Keep entries concise
- Tag properly
- Document and test all tools
- Run from project root
- Use verbose mode initially
- Verify after population
- Test queries

### DON'T:
- Store secrets
- Duplicate code
- Skip population
- Ignore outdated entries
- Add dependencies without approval
- Modify production code
- Commit/push changes

---

## Maintenance

### Schedule

- **After each session**: Add new learnings
- **Weekly**: Review and prune outdated entries
- **Monthly**: Run `kb_evolve` to optimize structure

### Quality Control

Each entry should have:
- Clear, descriptive title
- Specific finding (not vague)
- Actionable solution
- Proper category
- Confidence 0.5-1.0
- Relevant example

### Troubleshooting

| Issue | Solution |
|-------|----------|
| No files found | Verify `.meta*` dirs exist, check project root |
| Import errors | Run from project root: `python .meta/tools/commands.py ...` |
| Slow performance | Normal for 30+ files (5-30s), reduce verbosity |
| Duplicate entries | Expected during population, deduplicated on subsequent runs |
| KB corruption | Run `python .meta/tools/populate` to reset |

---

## Integration

The KB works with:

- **`.meta/sandbox/`** - Reference knowledge during modifications
- **`.meta/tests_sandbox/`** - Store test patterns
- **`.meta/experiments/`** - Document experimental findings
- **`.meta/reflection/`** - Store capability assessments
- **`.meta/development_tools/`** - Tool documentation
- **`.meta/project_development/`** - Project workflows

---

## Database

**Location**: `.meta/data/kb-meta/knowledge-meta.db`

The SQLite database is auto-initialized on first use.

**Current Stats** (as of last population):
- **Total entries**: 1,640
- **Patterns**: 809 (avg confidence: 0.94)
- **Findings**: 831 (avg confidence: 0.85)
- **Categories**: documentation, workflow, directives, code, test

---

## Testing

```bash
# Test unified KB
python3 -c "
from meta_tools import kb
print(kb.kb_stats())
print(kb.kb_search('TDD'))
"

# Run built-in test
cd .meta/tools
uv run python meta_tools.py
```

---

## Related Documents

- [META_HARNESS.md](../META_HARNESS.md) - Master documentation
- [AGENTS.md](../AGENTS.md) - Agent rules
- [.meta/tools/meta-harness-knowledge-base/META.md](../.meta/tools/meta-harness-knowledge-base/META.md) - KB implementation details
- [ADVANCED_FEATURES.md](../.meta/tools/meta-harness-knowledge-base/ADVANCED_FEATURES.md) - Advanced RAG features

---

**Version**: 3.0.0 (consolidated) | **Lines**: ~500
