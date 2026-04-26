# Knowledge Base System - agentx

## Overview

The agentx project uses **two separate knowledge bases** to store different types of knowledge:

1. **Meta Harness KB** (`knowledge-meta.db`) - Meta Project Harness patterns and workflows
2. **agentx KB** (`agent-x/agent-x.db`) - agentx project-specific knowledge

## Database Locations

```
.meta/data/kb-meta/
├── knowledge-meta.db           # Meta Harness KB
├── agent-x/
│ └── agent-x.db # agentx KB
└── README.md                   # This file
```

## Usage

### Import Both KBs

```python
from .meta/tools import meta_kb, agentx_kb

# Search Meta Harness KB (workflows, patterns)
meta_kb.kb_search("TDD workflow")
meta_kb.kb_ask("Where should I write tests?")

# Search agentx KB (project-specific knowledge)
agentx_kb.kb_search("REPL controller")
agentx_kb.kb_ask("How does the chat command work?")
```

### Available Functions

Both KBs support the same interface:

| Function | Description | Example |
|----------|-------------|---------|
| `kb_search(query, top_k=5, category=None)` | Search for entries | `kb_search("TDD", top_k=3)` |
| `kb_ask(question, top_k=3)` | RAG-augmented Q&A | `kb_ask("Where to write tests?")` |
| `kb_add_entry(type, category, title, finding, solution, ...)` | Add entry | See below |
| `kb_correct(entry_id, reason, new_finding)` | Correct entry | `kb_correct("PAT-123", "...", "...")` |
| `kb_evolve()` | Run evolution cycle | `kb_evolve()` |
| `kb_stats()` | Get statistics | `kb_stats()` |

### Adding Entries

```python
from .meta/tools import agentx_kb

# Add agentx specific knowledge
agentx_kb.kb_add_entry(
    entry_type="pattern",           # pattern, finding, correction, decision
    category="code",                # code, workflow, test, docs, tool, architecture
    title="REPL Command Pattern",
    finding="Commands implement run() method",
    solution="Use Command pattern with run() interface",
    context="When adding new REPL commands",
    confidence=0.95,
    example="class Chat(Command): def run(self): ..."
)
```

## When to Use Each KB

### Meta Harness KB (`meta_kb`)
- Meta project workflows
- Development patterns
- Testing methodologies
- Project structure standards
- Tool usage patterns

### agentx KB (`agentx_kb`)
- REPL interface details
- Command implementations
- Agent architecture
- Project-specific patterns
- Feature documentation

## Example Workflow

```python
from .meta/tools import meta_kb, agentx_kb

# 1. Before starting work, ask Meta Harness KB
print(meta_kb.kb_ask("Where should I implement this feature?"))
# → "Use .meta/sandbox/ for code modifications"

# 2. Work on implementation...

# 3. Document in agentx KB
agentx_kb.kb_add_entry(
    entry_type="pattern",
    category="code",
    title="Chat Command Implementation",
    finding="Chat command uses OpenRouter API",
    solution="Call openrouter.chat.completions.create()",
    confidence=0.95
)

# 4. Verify documentation
print(agentx_kb.kb_search("chat command"))
```

## Database Initialization

Both databases are auto-initialized on first use with the following schema:

- `entries` - Knowledge entries with FTS5 full-text search
- `corrections` - Entry corrections
- `evolution_log` - Evolution cycle history

## Tools Location

The KB facade and implementation are in:
- Facade: `.meta/tools/meta_tools.py`
- Implementation: `.meta/tools/meta-harness-knowledge-base/src/rag_tool.py`

## See Also

- [Meta Harness Documentation](../../../META_HARNESS.md)
- [agentx README](../../../README.md)
- [Meta Tools Usage](../../../.meta/tools/USAGE.md)
