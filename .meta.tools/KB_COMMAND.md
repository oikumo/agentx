# KB Population Command

## Quick Start

To clean and populate the Knowledge Base databases with real project knowledge:

```bash
# During conversation with AI agent
?kb clean and populate both
```

Or from command line:

```bash
python .meta.tools/commands.py kb_clean_and_populate --kb both
```

## What It Does

This command:

1. **Finds all `.meta*` directories** automatically (`.meta.project_development`, `.meta.sandbox`, etc.)
2. **Traverses all Markdown files** in those directories  
3. **Extracts knowledge** including:
   - Directives (NEVER/ALWAYS rules)
   - Workflows and processes
   - Patterns and best practices
   - Section-based content
4. **Populates both KBs**:
   - **Meta Harness KB** - Project workflows, directives, patterns
   - **Agent-X KB** - Project-specific architecture, commands, features

## Usage Examples

### User Commands (during AI conversation)

```bash
# Populate both KBs
?kb clean and populate both

# Populate only Meta Harness KB
?kb clean and populate meta

# Populate only Agent-X KB
?kb clean and populate agentx

# Show stats after population
?kb show stats
```

### Python API

```python
from .meta.tools import meta_tools

# Populate both
result = meta_tools.kb_clean_and_populate(kb='both', verbose=True)

# Populate only Meta
result = meta_tools.kb_clean_and_populate(kb='meta', verbose=True)

# Populate only Agent-X
result = meta_tools.kb_clean_and_populate(kb='agentx', verbose=True)
```

### Command Line

```bash
# Using the commands module
python .meta.tools/commands.py kb_clean_and_populate --kb both

# Or directly
python .meta.tools/populate_kb.py --kb both --verbose
```

## Files Analyzed

### Root Documentation (Both KBs)
- `AGENTS.md` - Agent rules
- `META_HARNESS.md` - Master documentation  
- `README.md` - Project overview

### Meta Harness KB (`.meta*` directories)
- `.meta.project_development/*.md` - All project docs
- `.meta.sandbox/META.md` - Sandbox rules
- `.meta.tests_sandbox/META.md` - TDD guidelines
- `.meta.experiments/*.md` - Experiment documentation
- `.meta.reflection/*.md` - Reflection testing
- `.meta.development_tools/*.md` - Tool docs
- `.meta.tools/*.md` - Tool usage

### Agent-X KB
- `src/**/*.md` - Source documentation
- `doc/**/*.md` - Additional docs

## Output

Example output:

```
======================================================================
KB Clean and Populate - File Traversal Mode
======================================================================
======================================================================
KB Population - File Traversal & LLM Analysis
======================================================================

Found 8 .meta* directories: ['.meta.data', '.meta.sandbox', ...]
Found 65 files to analyze

Processing: AGENTS.md
  ✓ Added to Meta KB: AGENTS.md - Agent-X System Agent Rules...
  ✓ Added to AgentX KB: AGENTS.md - Agent-X System Agent Rules...
  ✓ Added to Meta KB: Directives from AGENTS.md...
  ...

======================================================================
Population Complete!
  Meta Harness KB: 150 entries added
  Agent-X KB: 120 entries added
======================================================================

Clean and populate complete:
  Meta Harness KB: 150 entries added from files
  Agent-X KB: 120 entries added from files
```

## When to Use

**Recommended:**
- Initial project setup
- After major documentation updates
- KB corruption recovery
- Testing KB functionality
- Periodic knowledge refresh

**Not recommended for:**
- Adding single entries (use `kb_add_entry`)
- Minor doc updates (use `kb_add_entry`)
- Routine updates (use `kb_evolve`)

## Related Commands

```bash
# View KB statistics
?kb show stats

# Search KB
?kb search "TDD workflow"

# Ask KB
?kb ask "Where should I write tests?"

# Evolve KB (cleanup old entries)
?kb evolve kb

# Add single entry
?kb add to kb pattern "My Pattern" "Finding" "Solution"
```

## Troubleshooting

### No files found
- Ensure you're in the project root directory
- Verify `.meta*` directories exist

### Import errors
- Run from project root: `cd /path/to/agent-x`
- Use: `python .meta.tools/commands.py kb_clean_and_populate`

### Slow performance
- Normal for large projects (30+ files)
- Expect 5-30 seconds depending on file count

## See Also

- [KB Population Guide](KB_POPULATION_GUIDE.md) - Detailed documentation
- [Usage Guide](USAGE.md) - General KB operations
- [AGENTS.md](../AGENTS.md) - Agent rules
