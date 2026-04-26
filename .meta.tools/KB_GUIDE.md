# Knowledge Base Guide

## Quick Start

```bash
# During AI agent conversation
?kb clean and populate both

# Command line
python .meta.tools/commands.py kb_clean_and_populate --kb both
```

---

## Overview

Meta Tools provide unified access to Knowledge Base RAG system:
- **Meta Harness KB**: Project workflows, directives, patterns
- **Agent-X KB**: Architecture, commands, features

---

## KB Population

### What It Does

1. Finds all `.meta*` directories automatically
2. Traverses all Markdown files
3. Extracts knowledge (directives, workflows, patterns)
4. Populates both KBs with structured entries

### Usage

```bash
# User commands (AI conversation)
?kb clean and populate both     # Both KBs
?kb clean and populate meta     # Meta Harness only
?kb clean and populate agentx   # Agent-X only

# Python API
from .meta.tools import meta_tools
result = meta_tools.kb_clean_and_populate(kb='both', verbose=True)

# Command line
python .meta.tools/commands.py kb_clean_and_populate --kb both
```

### Files Analyzed

**Meta Harness KB:**
- `AGENTS.md`, `META_HARNESS.md`
- `.meta.project_development/*.md`
- `.meta.sandbox/META.md`
- `.meta.tests_sandbox/META.md`
- `.meta.experiments/*.md`
- `.meta.reflection/*.md`
- `.meta.tools/*.md`

**Agent-X KB:**
- `README.md`
- `src/**/*.md`
- `doc/**/*.md`

### When to Use

**Recommended:**
- Initial project setup
- After major doc updates
- KB corruption recovery
- Periodic knowledge refresh

**Not recommended:**
- Adding single entries (use `kb_add_entry`)
- Minor doc updates (use `kb_evolve`)

---

## Available Functions

### Search & Query

```python
from .meta.tools import kb_search, kb_ask, kb_stats

# Search KB
results = kb_search("TDD workflow", top_k=3)

# Ask question (RAG-augmented)
answer = kb_ask("Where should I write tests?")

# Get statistics
stats = kb_stats()
```

### Knowledge Management

```python
from .meta.tools import kb_add_entry, kb_correct, kb_evolve

# Add entry
kb_add_entry(
    entry_type="pattern",      # pattern|finding|correction|decision
    category="workflow",       # workflow|code|test|docs|tool|architecture
    title="Bug Fix Workflow",
    finding="Bugs reproduced in sandbox",
    solution="Reproduce → Test → Fix → Verify",
    context="When fixing bugs",
    confidence=0.9
)

# Correct entry
kb_correct(entry_id="123", reason="Outdated", new_finding="Updated info")

# Evolve KB (cleanup old entries)
kb_evolve()
```

---

## Example Workflow

```python
from .meta.tools import kb_ask, kb_search, kb_add_entry, kb_stats

# 1. Check stats
print(kb_stats())

# 2. Search
print(kb_search("TDD", top_k=3))

# 3. Ask
answer = kb_ask("Where should I write tests?")
print(answer)

# 4. Add knowledge
kb_add_entry("pattern", "workflow", "Bug Fix", 
             "Reproduce in sandbox", "Test → Fix → Verify")

# 5. Verify
print(kb_search("bug fix", top_k=2))
```

---

## Database

**Location**: `.meta.data/kb-meta/knowledge-meta.db`

Auto-initialized on first use.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No files found | Verify `.meta*` dirs exist, check project root |
| Import errors | Run from project root: `python .meta.tools/commands.py ...` |
| Slow performance | Normal for 30+ files (5-30s) |
| Duplicate entries | Expected during population, deduplicated on subsequent runs |

---

## Related

- [Usage Guide](USAGE.md) - General KB operations
- [META.md](META.md) - Meta tools overview
- [AGENTS.md](../AGENTS.md) - Agent rules
