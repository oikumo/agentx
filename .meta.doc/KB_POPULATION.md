# KB Population System

## Overview

The **KB Population System** automatically traverses all project files (documentation and source code) to populate the Knowledge Bases with real project knowledge.

**Version**: 2.0.0  
**Status**: ✅ Active  
**Location**: `.meta.tools/populate_kb.py`

---

## What It Does

The system automatically:

1. **Finds all `.meta*` directories** - `.meta.project_development`, `.meta.sandbox`, `.meta.experiments`, etc.
2. **Traverses all Markdown files** - Documentation, guides, META.md files
3. **Analyzes Python source code** - Classes, functions, imports in `src/`
4. **Extracts structured knowledge**:
   - Directives and rules
   - Workflows and processes
   - Patterns and best practices
   - Source code architecture (classes, functions)
5. **Populates dual KBs**:
   - **Meta Harness KB** - Project workflows, patterns, directives
   - **Agent-X KB** - Source code, architecture, project-specific knowledge

---

## Usage

### Simple Command

```bash
# Populate both KBs (default)
python .meta.tools/populate

# Or specify which KB
python .meta.tools/populate both    # Both KBs
python .meta.tools/populate meta    # Meta Harness KB only
python .meta.tools/populate agentx  # Agent-X KB only
```

### As AI Command

During conversation:

```
?kb populate
```

### From Python

```python
from .meta.tools import meta_tools

# Populate both KBs
result = meta_tools.kb_clean_and_populate(kb='both', verbose=True)
print(result)

# Populate only Meta Harness KB
result = meta_tools.kb_clean_and_populate(kb='meta', verbose=True)
```

---

## Files Analyzed

### Root Documentation (Both KBs)
- `AGENTS.md` - Agent rules and workflows
- `META_HARNESS.md` - Master documentation
- `README.md` - Project overview

### Meta Harness KB (`.meta*` directories)
- `.meta.project_development/*.md` - All project development docs
- `.meta.sandbox/META.md` - Sandbox rules
- `.meta.tests_sandbox/META.md` - TDD guidelines
- `.meta.experiments/*.md` - Experiment documentation
- `.meta.reflection/*.md` - Reflection testing
- `.meta.development_tools/*.md` - Tool documentation
- `.meta.tools/*.md` - Tool usage guides

### Agent-X KB (Source Code)
- `src/**/*.py` - All Python source files
- `src/**/*.md` - Source documentation
- `doc/**/*.md` - Additional documentation

---

## Knowledge Extraction

### From Markdown Files

For each `.md` file, the system extracts:

- **Title** - From first heading or filename
- **Sections** - All `##` and `###` sections
- **Directives** - NEVER/ALWAYS/MUST statements
- **Workflows** - Process steps and patterns
- **Best Practices** - Recommendations and guidelines
- **Summary** - First 2000 characters as overview

### From Python Source Files

For each `.py` file, the system extracts:

- **Classes** - All class definitions
- **Functions** - All function/method definitions
- **Imports** - Dependencies and modules
- **Architecture patterns** - How code is organized
- **File location** - Relative path in project

Example output for a Python file:

```
Title: Python: main_view.py
Summary: Source: src/views/main_view/main_view.py. Classes: MainView, ChatPanel | Functions: create_view, update_display
Classes: ['MainView', 'ChatPanel']
Functions: ['create_view', 'update_display', 'handle_input']
Imports: ['from PyQt5.QtWidgets import QMainWindow', 'import sys']
```

---

## Entry Structure

Each populated entry follows this structure:

```python
{
    "type": "pattern|finding|correction|decision",
    "category": "documentation|source_code|workflow|directives|...",
    "title": "Descriptive title",
    "finding": "What was found/extracted",
    "solution": "Extracted solution or pattern",
    "context": "Source file path",
    "confidence": 0.80-1.0,
    "example": "Usage example or reference"
}
```

### Entry Types

| Type | Purpose | Example |
|------|---------|---------|
| `pattern` | Reusable solution | "Work in .meta.sandbox/" |
| `finding` | Discovered fact | "uv is faster than pip" |
| `correction` | Fixed knowledge | "Workflow changed in v2.0" |
| `decision` | Architectural choice | "Use SQLite over ChromaDB" |

---

## Example Output

```
Populating both KB...

Found 8 .meta* directories: ['.meta.data', '.meta.sandbox', '.meta.tools', ...]
Found src/ directory - analyzing source code...
Found 118 files to analyze

Processing: AGENTS.md
  ✓ Added to Meta KB: AGENTS.md - Agent-X System Agent Rules...
  ✓ Added to AgentX KB: AGENTS.md - Agent-X System Agent Rules...
  ✓ Added to Meta KB: Directives from AGENTS.md...
  ...

Processing: src/main.py
  ✓ Added to AgentX KB: Source: Python: main.py...
  ✓ Added to AgentX KB: Class: MainController...
  ...

✓ Complete!
  Meta KB: 150 entries
  Agent-X KB: 120 entries
```

---

## When to Use

**Recommended scenarios:**

1. **Initial setup** - After cloning the project
2. **After major documentation updates** - When docs change significantly
3. **After code refactoring** - New architecture patterns
4. **KB corruption recovery** - Reset to clean state
5. **Periodic refresh** - Keep KB current with project state

**NOT recommended for:**

- Adding single entries (use `kb_add_entry` instead)
- Minor documentation tweaks
- Routine updates (use `kb_evolve`)

---

## Performance

Typical execution time: **10-60 seconds** depending on:
- Number of `.meta*` directories
- Python source files in `src/`
- Total files to analyze

The system processes files sequentially and creates KB entries in real-time.

---

## Architecture

### Components

1. **`populate_kb.py`** - Core population logic
   - `KBPopulator` class
   - File discovery
   - Content analysis
   - KB entry creation

2. **`meta_tools.py`** - Wrapper function
   - `kb_clean_and_populate()` function
   - User-facing API

3. **`populate`** - Simple command script
   - Command-line interface
   - Entry point for `python .meta.tools/populate`

### File Discovery

```python
# Finds all .meta* directories
meta_dirs = []
for item in base_path.iterdir():
    if item.is_dir() and item.name.startswith('.meta'):
        meta_dirs.append(item)

# Analyzes src/ Python files
src_path = base_path / 'src'
for py_file in src_path.rglob('*.py'):
    files_to_analyze.append((py_file, 'agentx'))
```

### Content Analysis

**Markdown files:**
- Extract sections (##, ###)
- Detect directives (NEVER/ALWAYS)
- Identify workflows
- Extract patterns

**Python files:**
- Parse class definitions
- Extract function definitions
- Analyze imports
- Generate architecture summary

---

## Knowledge Base Routing

### Meta Harness KB

Receives knowledge from:
- `AGENTS.md`
- `META_HARNESS.md`
- `.meta.project_development/`
- `.meta.sandbox/`
- `.meta.tests_sandbox/`
- `.meta.experiments/`
- `.meta.reflection/`
- `.meta.development_tools/`
- `.meta.tools/`

**Categories:** directives, workflow, documentation, standards, environment

### Agent-X KB

Receives knowledge from:
- `src/**/*.py` (all source code)
- `src/**/*.md`
- `doc/**/*.md`
- `README.md`

**Categories:** source_code, class, architecture, code, documentation

---

## Quality Control

### Before Population

- [ ] Verify project root directory
- [ ] Check `.meta*` directories exist
- [ ] Ensure `src/` directory present
- [ ] Confirm write access to KB databases

### After Population

- [ ] Check entry counts (should be 50-200+)
- [ ] Verify KB stats with `kb_stats()`
- [ ] Test search with `kb_search("test")`
- [ ] Validate entries have proper structure

### Entry Quality

Each entry should have:
- Clear, descriptive title
- Specific finding (not vague)
- Actionable solution
- Proper category
- Confidence 0.5-1.0
- Relevant example

---

## Troubleshooting

### No files found

**Problem:** Script reports "Found 0 files"

**Solution:**
- Verify you're in project root: `pwd`
- Check `.meta*` directories exist: `ls -la | grep .meta`
- Ensure proper permissions

### Import errors

**Problem:** `ImportError: No module named 'meta'`

**Solution:**
- Run from project root: `cd /path/to/agent-x`
- Use: `python .meta.tools/populate`

### Slow performance

**Problem:** Takes > 60 seconds

**Solution:**
- Normal for large projects (100+ files)
- Consider filtering out `.venv` directories
- Reduce verbosity: `python .meta.tools/populate --quiet`

### Duplicate entries

**Problem:** Same content appears multiple times

**Solution:**
- Expected during initial population
- Use `kb_evolve()` to clean up
- Entries are deduplicated by ID on subsequent runs

---

## Best Practices

1. **Run from project root** - Ensures correct file discovery
2. **Use verbose mode initially** - Monitor progress
3. **Verify after population** - Use `kb_stats()` to check counts
4. **Test queries** - Verify KB is searchable
5. **Document custom patterns** - Add project-specific entries manually

---

## Future Enhancements

### Phase 1: Current ✅
- Manual population trigger
- File traversal and analysis
- Dual KB population

### Phase 2: Planned
- Auto-populate on git commit
- Incremental updates (only changed files)
- Smart filtering (skip test files, etc.)

### Phase 3: Future
- Real-time KB updates
- Auto-categorization improvements
- Cross-project knowledge transfer

---

## Related Documents

- [KB Population Guide](../.meta.tools/KB_POPULATION_GUIDE.md) - Detailed guide
- [Usage Guide](../.meta.tools/USAGE.md) - General KB operations
- [AGENTS.md](../AGENTS.md) - Agent rules
- [META_HARNESS.md](../META_HARNESS.md) - Master documentation

---

**Version**: 2.0.0  
**Status**: ✅ Active  
**Maintained by**: opencode AI agent  
**License**: Apache 2.0
