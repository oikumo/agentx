# KB Population

## Usage

```bash
# Populate both KBs
python .meta/tools/populate

# Or specify which KB
python .meta/tools/populate both    # both (default)
python .meta/tools/populate meta    # Meta Harness only
python .meta/tools/populate agentx  # Agent-X only
```

## As AI Command

During conversation with AI agent:

```
?kb populate
```

## What It Does

- Finds all `.meta*` directories
- Reads all `.md` files  
- Extracts knowledge (patterns, workflows, directives)
- Populates KB databases

## Output

```
Populating both KB...
Found 8 .meta* directories
Found 67 files to analyze

Processing: AGENTS.md
  ✓ Added to Meta KB...
  ✓ Added to AgentX KB...
  ...

✓ Complete!
  Meta KB: 150 entries
  Agent-X KB: 120 entries
```
