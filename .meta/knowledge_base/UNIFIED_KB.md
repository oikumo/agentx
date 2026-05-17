# Unified Knowledge Base

## Summary

The Meta Harness Knowledge Base is now **unified** - serving both Meta Harness patterns and agentx project knowledge in a single database.

## What Changed

### Before
- Two separate KBs:
  - Meta Harness KB (`knowledge-meta.db`)
  - agentx KB (`agent-x/agent-x.db`)
- Complex routing logic
- Duplicate entries
- Confusing maintenance

### After  
- **Single unified KB** (`knowledge-meta.db`)
- All knowledge in one place
- Simplified architecture
- Easier maintenance

## Architecture

```
.meta/data/kb-meta/
└── knowledge-meta.db # Unified KB (Meta Harness + agentx)
```

## Usage

### Python API

```python
from meta_tools import kb

# Search
result = kb.kb_search("TDD workflow")

# Ask
result = kb.kb_ask("Where should I write tests?")

# Add entry
kb.kb_add_entry("pattern", "workflow", "Title", "Finding", "Solution")

# Stats
print(kb.kb_stats())
```

### CLI

```bash
# Search
python .meta/tools/meta-harness-knowledge-base/kb search "query"

# Ask
python .meta/tools/meta-harness-knowledge-base/kb ask "question?"

# Stats
python .meta/tools/meta-harness-knowledge-base/kb stats
```

## Population

All files now populate the single unified KB:

```bash
python .meta/tools/populate both
```

This populates:
- ✅ Meta Harness documentation (`.meta.*` directories)
- ✅ agentx source code (`src/`)
- ✅ Project documentation (`README.md`, etc.)

## Benefits

1. **Simplified Architecture**
   - One database to manage
   - No routing complexity
   - Easier to understand

2. **Better Search**
   - All knowledge in one place
   - Cross-referencing between Meta and agentx
   - More comprehensive results

3. **Easier Maintenance**
   - Single source of truth
   - No sync issues
   - Simpler backups

4. **Unified API**
   ```python
   from meta_tools import kb  # Single import
   ```

## Migration

The old dual-KB system has been removed:
- ❌ `agentx_kb` alias removed (now just `kb`)
- ❌ agentx KB directory removed
- ❌ Routing logic removed

All functionality now uses the unified `kb` instance.

## Current Stats

- **Total entries**: 1,640
- **Patterns**: 809 (avg confidence: 0.94)
- **Findings**: 831 (avg confidence: 0.85)
- **Categories**: documentation, workflow, directives, code, test

## Files Modified

1. `meta_tools.py` - Simplified to single KB
2. `populate_kb.py` - Unified population
3. Removed agentx KB directory

## Testing

```bash
# Test unified KB
python3 -c "
from meta_tools import kb
print(kb.kb_stats())
print(kb.kb_search('TDD'))
"
```

## See Also

- [ADVANCED_FEATURES.md](meta-harness-knowledge-base/ADVANCED_FEATURES.md) - Advanced RAG features
- [KB_GUIDE.md](KB_GUIDE.md) - General KB guide
- [META_HARNESS.md](../META_HARNESS.md) - Meta Harness documentation
