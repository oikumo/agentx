# KB Population - Simple Guide

## Quick Start

**User command** (during AI conversation):
```bash
?kb populate
```

**Or from terminal**:
```bash
python .meta/tools/populate          # both KBs
python .meta/tools/populate meta     # Meta only  
python .meta/tools/populate agentx   # Agent-X only
```

## What It Does

1. Finds all `.meta*` directories
2. Reads all `.md` files  
3. Extracts patterns, workflows, directives
4. Populates KB databases

## Examples

```bash
# Populate both KBs
python .meta/tools/populate

# Populate only Meta Harness KB  
python .meta/tools/populate meta

# Populate only Agent-X KB
python .meta/tools/populate agentx
```

## Output

```
Populating both KB...

Found 8 .meta* directories
Found 65 files to analyze

Processing: AGENTS.md
  ✓ Added to Meta KB...
  ✓ Added to AgentX KB...
  ...

Complete!
```

## That's It!

Simple and clean. No complex commands needed.
