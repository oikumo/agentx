# KB Population Guide

## Overview

The KB Population system allows you to **clean and repopulate** both Knowledge Base databases (Meta Harness KB and Agent-X KB) by **automatically traversing** all project documentation files.

## How It Works

The system:

1. **Finds all `.meta*` directories** in the project root
2. **Traverses all Markdown files** within those directories
3. **Analyzes each file** to extract:
   - Key patterns and practices
   - Workflows and processes
   - Directives and rules
   - Section-based knowledge
4. **Creates structured KB entries** with proper categorization
5. **Populates the appropriate KB** (Meta Harness or Agent-X)

## Usage

### As a User Command

During your conversation with the AI agent, you can trigger KB population:

```bash
# Populate both KBs
?kb clean and populate both

# Populate only Meta Harness KB
?kb clean and populate meta

# Populate only Agent-X KB  
?kb clean and populate agentx
```

### From Python

```python
from .meta/tools import meta_tools

# Clean and populate both KBs
result = meta_tools.kb_clean_and_populate(kb='both', verbose=True)
print(result)

# Clean only Meta Harness KB
result = meta_tools.kb_clean_and_populate(kb='meta', verbose=True)

# Clean only Agent-X KB
result = meta_tools.kb_clean_and_populate(kb='agentx', verbose=True)
```

### From Command Line

```bash
# Using the commands module
python .meta/tools/commands.py kb_clean_and_populate --kb both

# Or directly
python .meta/tools/populate_kb.py --kb both --verbose
```

## What Gets Populated

### Meta Harness KB

Files analyzed:
- `AGENTS.md` - Agent rules and workflows
- `META_HARNESS.md` - Master documentation
- `.meta/project_development/*.md` - All project development docs
- `.meta/sandbox/META.md` - Sandbox rules
- `.meta/tests_sandbox/META.md` - TDD guidelines
- `.meta/experiments/META.md` - Experiment protocols
- `.meta/reflection/META.md` - Reflection testing
- `.meta/development_tools/META.md` - Tool documentation
- `.meta/tools/*.md` - Tool usage guides

Content extracted:
- Core directives (NEVER/ALWAYS rules)
- Workflow patterns
- Quality gates
- Directory structure guidelines
- Best practices

### Agent-X KB

Files analyzed:
- `README.md` - Project overview
- `src/**/*.md` - Source documentation
- `doc/**/*.md` - Additional documentation

Content extracted:
- Architecture patterns
- Command implementations
- Agent behaviors
- Integration patterns
- Feature documentation

## Entry Structure

Each populated entry follows this structure:

```python
{
    "type": "pattern|finding|correction|decision",
    "category": "directives|workflow|documentation|...",
    "title": "Descriptive title from file content",
    "finding": "What was found in the file",
    "solution": "Extracted solution or pattern",
    "context": "Source file path",
    "confidence": 0.80-1.0,
    "example": "Usage example or reference"
}
```

## When to Use

**Recommended scenarios:**

1. **Initial setup** - After cloning the project
2. **KB corruption** - If KB has invalid entries
3. **After major docs update** - When documentation changes significantly
4. **Testing** - To verify KB population logic
5. **Knowledge refresh** - Periodic cleanup and repopulation

**NOT recommended for:**

- Routine KB updates (use `kb_add_entry` instead)
- Adding single entries (use `kb_add_entry` directly)
- Minor documentation tweaks

## Performance

Typical execution time: **5-30 seconds** depending on:
- Number of `.meta*` directories
- Total markdown files found
- File sizes

## Monitoring Progress

When `verbose=True` (default), you'll see:

```
======================================================================
KB Population - File Traversal & LLM Analysis
======================================================================

Found 8 .meta* directories: [...]
Found 64 files to analyze

Processing: AGENTS.md
  ✓ Added to Meta KB: AGENTS.md - Agent-X System Agent Rules...
  ✓ Added to AgentX KB: AGENTS.md - Agent-X System Agent Rules...
  ...

======================================================================
Population Complete!
  Meta Harness KB: 150 entries added
  Agent-X KB: 120 entries added
======================================================================
```

## Troubleshooting

### No files found

**Problem**: Script reports "Found 0 files"

**Solution**: 
- Verify `.meta*` directories exist
- Check file permissions
- Ensure you're in project root

### Import errors

**Problem**: `ImportError: attempted relative import`

**Solution**:
- Run from project root
- Use: `python .meta/tools/commands.py kb_clean_and_populate`

### Duplicate entries

**Problem**: Same content appears multiple times

**Solution**:
- This is expected during population
- Entries are deduplicated by ID on subsequent runs
- Use `kb_evolve()` to clean up old entries

## Best Practices

1. **Run from project root** - Ensures correct file discovery
2. **Use verbose mode** - Monitor progress and catch errors
3. **Verify after population** - Use `kb_stats()` to check counts
4. **Test queries** - Verify KB is queryable with `kb_search()` and `kb_ask()`

## Example Session

```bash
# 1. Check current KB stats
?kb show stats

# 2. Clean and populate both KBs
?kb clean and populate both

# 3. Verify population
?kb show stats

# 4. Test search
?kb search "TDD workflow"

# 5. Test ask
?kb ask "Where should I write tests?"
```

## Advanced Usage

### Custom file filtering

Edit `populate_kb.py` and modify `find_all_meta_files()`:

```python
# Add custom patterns
custom_patterns = ["custom/**/*.md"]
for pattern in custom_patterns:
    for md_file in self.base_path.glob(pattern):
        files_to_analyze.append((md_file, "agentx"))
```

### Custom entry creation

Override `create_kb_entries()` to customize how entries are created from files.

## See Also

- [KB Usage Guide](USAGE.md) - General KB operations
- [Meta Tools](META.md) - Development tools documentation
- [AGENTS.md](../AGENTS.md) - Agent rules and workflows
