# Meta Tools Usage Guide

## Overview

The Meta Tools facade provides unified access to the Knowledge Base RAG system and other Meta Project Harness tools.

## Location

```
.meta/tools/
├── __init__.py          # Package init (exports all functions)
├── meta_tools.py        # Main facade module
└── meta-harness-knowledge-base/  # KB implementation
```

## Usage

### Method 1: Direct import from `.meta/tools`

```python
import sys
sys.path.insert(0, '.meta/tools')
from meta_tools import kb_ask, kb_search, kb_stats

# Search the knowledge base
results = kb_search("TDD workflow", top_k=3)
print(results)

# Ask a question (RAG-augmented)
answer = kb_ask("Where should I write tests?")
print(answer)

# Get statistics
stats = kb_stats()
print(stats)
```

### Method 2: Import the module

```python
import sys
sys.path.insert(0, '.meta/tools')
import meta_tools

# Use functions
meta_tools.kb_search("workflow")
meta_tools.kb_ask("Where to implement features?")
meta_tools.kb_stats()
```

### Method 3: From within `.meta/tools` directory

```python
from meta_tools import kb_ask, kb_search

kb_ask("Your question here")
```

## Available Functions

### `kb_search(query, top_k=5, category=None)`
Search the knowledge base for relevant entries.

**Parameters:**
- `query`: Search query string
- `top_k`: Number of results (default: 5)
- `category`: Optional category filter

**Returns:** Formatted search results

### `kb_ask(question, top_k=3)`
Ask a question and get RAG-augmented response.

**Parameters:**
- `question`: Question to ask
- `top_k`: Number of context entries (default: 3)

**Returns:** RAG-augmented prompt with retrieved knowledge

### `kb_add_entry(entry_type, category, title, finding, solution, context="", confidence=0.5, example="")`
Add new knowledge entry.

**Parameters:**
- `entry_type`: pattern, finding, correction, or decision
- `category`: workflow, code, test, docs, tool, or architecture
- `title`: Concise title
- `finding`: What was discovered
- `solution`: How to solve it
- `context`: When/where this applies
- `confidence`: Confidence score (0.0-1.0)
- `example`: Optional example

**Returns:** Confirmation message

### `kb_correct(entry_id, reason, new_finding)`
Add correction to existing entry.

**Parameters:**
- `entry_id`: ID of entry to correct
- `reason`: Why correction is needed
- `new_finding`: Updated information

**Returns:** Confirmation message

### `kb_evolve()`
Run evolution cycle: decay unused entries, archive low confidence.

**Returns:** Evolution results message

### `kb_stats()`
Get knowledge base statistics.

**Returns:** Formatted statistics

## Example: Complete Workflow

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

## Testing

Run the built-in test:

```bash
cd .meta/tools
uv run python meta_tools.py
```

This will execute a test sequence showing all functions in action.

## Database Location

The knowledge base SQLite database is stored at:
```
.meta/data/kb-meta/knowledge-meta.db
```

The database is auto-initialized on first use.

## See Also

- [META.md](META.md) - Meta Project Harness documentation
- [.meta/knowledge_base/META.md](../.meta/knowledge_base/META.md) - KB documentation
- [AGENTS.md](../AGENTS.md) - Agent rules and workflows
