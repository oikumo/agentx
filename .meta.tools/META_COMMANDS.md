# Meta Commands - Agent Interaction Patterns

## Overview

Meta commands are **natural language prompts** you use during AI agent conversations to trigger specific workflows and operations.

**Format**: `meta <action> [target] [options]`

**Examples:**
- `meta token audit` - Run token audit
- `meta health check` - Check harness health
- `meta kb populate both` - Populate both KBs

### Print All Commands

```bash
# Show all available meta commands
meta

# Or with help flag
meta --help
meta -h
```

This displays the complete command reference with descriptions and examples.

---

## Knowledge Base Commands

### Population

```bash
# Clean and populate both KBs
meta kb populate both

# Populate only Meta Harness KB
meta kb populate meta

# Populate only Agent-X KB
meta kb populate agentx
```

**What happens**: Agent traverses all `.meta*` directories, extracts knowledge from Markdown files, and populates both knowledge bases.

### Search & Query

```bash
# Search knowledge base
meta kb search "TDD workflow"

# Ask question with RAG
meta kb ask "Where should I write tests?"

# Show statistics
meta kb stats
```

### Knowledge Management

```bash
# Add new entry
meta kb add pattern workflow "Bug Fix" "Reproduce in sandbox" "Test → Fix → Verify"

# Correct existing entry
meta kb correct 123 "Outdated" "New finding"

# Run evolution cycle
meta kb evolve
```

---

## Optimization Commands

### Token Management

```bash
# Analyze token usage
meta token audit

# Compress documentation
meta compress docs
```

### Structure & Health

```bash
# Run health check
meta health check

# Analyze structure
meta structure analysis

# Archive old experiments
meta archive experiments
```

---

## Project Commands

### Quick Projects (30 min - 1 hr)

```bash
# Token audit
meta token audit

# Archive experiments
meta archive experiments

# Consolidate docs
meta consolidate docs

# Monthly health check
meta health check
```

### Medium Projects (1-3 hrs)

```bash
# Documentation compression
meta compress docs

# Structure optimization
meta structure analysis

# Create workflow templates
meta create workflows

# Populate knowledge base
meta populate kb
```

### Advanced Projects (3+ hrs)

```bash
# Full optimization
meta optimize all

# Create new skill
meta create skill

# Enhance workflows
meta enhance workflows

# Capability assessment
meta test capability
```

---

## Decision Tree

```
Need to...
├─ Populate KB? → meta kb populate both
├─ Search KB? → meta kb search "query"
├─ Add knowledge? → meta kb add pattern ...
├─ Check health? → meta health check
├─ Save tokens? → meta token audit
├─ Clean up? → meta archive experiments
├─ Compress docs? → meta compress docs
├─ Analyze structure? → meta structure analysis
└─ Create skill? → meta create skill

Unsure? → meta (shows all commands)
```

---

## Usage Examples

### Example 1: Initial Setup

```bash
User: meta kb populate both

Agent: 
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

### Example 2: Quick Search

```bash
User: meta kb search "TDD workflow"

Agent:
Found 3 relevant entries:

1. **TDD Workflow** (pattern)
   Finding: Tests should be written before production code
   Solution: RED → GREEN → REFACTOR cycle
   Context: .meta.tests_sandbox/META.md

2. **Bug Fix Workflow** (pattern)
   Finding: Bugs should be reproduced in sandbox first
   Solution: Reproduce → Test → Fix → Verify
   Context: .meta.sandbox/META.md
```

### Example 3: Health Check

```bash
User: meta health check

Agent:
Running Meta Harness Health Check...
======================================================================
Documentation Status:
✓ AGENTS.md: 443/1500 tokens (29%)
✓ META_HARNESS.md: 602/2000 tokens (30%)
✓ All META.md files present and under budget

Structure Status:
✓ Directory depth: OK (≤3)
✓ Naming consistency: OK (.meta.* pattern)
✓ Navigation clarity: OK

Overall Health: EXCELLENT
======================================================================
```

### Example 4: Token Audit

```bash
User: meta token audit

Agent:
Analyzing token consumption...
======================================================================
Token Analysis Report
======================================================================
AGENTS.md                        443 tokens
META_HARNESS.md                  602 tokens
.meta.project_development/META.md 174 tokens
...

Total: 2,714 tokens
Recommendation: All files within budget ✅
======================================================================
```

### Example 5: Archive Experiments

```bash
User: meta archive experiments

Agent:
Archiving old experiments...
✓ Moved: agent-x-session-state-proposal → archive/
✓ Moved: token-optimization-skill → archive/
✓ Moved: petri-net-analyzer → archive/

Archived 3 experiments (6,000 tokens)
======================================================================
```

---

## Best Practices

### When to Use

✅ **Recommended:**
- Starting a new task
- Need to find existing patterns
- Adding new knowledge
- Regular maintenance
- Health checks

❌ **Not needed for:**
- Simple questions
- Production code changes
- Emergency fixes

### Command Patterns

**Pattern 1: Find then Act**
```bash
?meta kb search "existing pattern"
?meta kb add to kb ...
```

**Pattern 2: Check then Modify**
```bash
?meta health check
?meta run <optimization>
```

**Pattern 3: Periodic Maintenance**
```bash
?meta token audit          # Monthly
?meta archive experiments  # Quarterly
?meta kb evolve            # As needed
```

---

## Response Format

Agent responses follow this structure:

```
======================================================================
<Command Name> - <Description>
======================================================================

<Progress/Status updates>
✓ Success indicator
✓ Success indicator

======================================================================
Summary/Result
======================================================================
```

---

## Related

- [KB_GUIDE.md](KB_GUIDE.md) - Detailed KB documentation
- [AGENTS.md](../AGENTS.md) - Agent rules
- [WORKFLOWS.md](../.meta.project_development/WORKFLOWS.md) - Workflow patterns

---

## Complete Command Reference

### Quick Reference Card

```
# Knowledge Base
meta kb populate [both|meta|agentx]
meta kb search "<query>" [--top_k N]
meta kb ask "<question>"
meta kb stats
meta kb add pattern <category> "<title>" "<finding>" "<solution>"
meta kb correct <id> "<reason>" "<new_finding>"
meta kb evolve

# Optimization
meta token audit [--output file.md]
meta compress docs [--target ratio]
meta structure analysis
meta health check
meta archive experiments [--older_than_days N]

# Projects
meta token audit              # Quick (30 min)
meta archive experiments      # Quick (30 min)
meta consolidate docs         # Quick (30 min)
meta health check             # Quick (30 min)
meta compress docs            # Medium (1-2 hrs)
meta structure analysis       # Medium (1-2 hrs)
meta create workflows         # Medium (1-2 hrs)
meta populate kb              # Medium (1-2 hrs)
meta optimize all             # Advanced (3+ hrs)
meta create skill             # Advanced (3+ hrs)
meta enhance workflows        # Advanced (3+ hrs)
meta test capability          # Advanced (3+ hrs)

# Help
meta                          # Show this reference
meta --help                   # Show help
```

### All Commands by Category

#### Knowledge Base (10 commands)
1. `meta kb populate both` - Clean and populate both KBs
2. `meta kb populate meta` - Populate Meta Harness KB only
3. `meta kb populate agentx` - Populate Agent-X KB only
4. `meta kb search "<query>"` - Search knowledge base
5. `meta kb ask "<question>"` - Ask question with RAG
6. `meta kb stats` - Show KB statistics
7. `meta kb add pattern ...` - Add pattern entry
8. `meta kb add finding ...` - Add finding entry
9. `meta kb correct ...` - Correct existing entry
10. `meta kb evolve` - Run evolution cycle

#### Optimization (5 commands)
11. `meta token audit` - Analyze token consumption
12. `meta compress docs` - Compress documentation
13. `meta structure analysis` - Analyze directory structure
14. `meta health check` - Run harness health check
15. `meta archive experiments` - Archive old experiments

#### Projects (12 commands)
16. `meta token audit` - Quick token audit (30 min)
17. `meta archive experiments` - Quick archive (30 min)
18. `meta consolidate docs` - Quick consolidation (30 min)
19. `meta health check` - Quick health check (30 min)
20. `meta compress docs` - Medium compression (1-2 hrs)
21. `meta structure analysis` - Medium analysis (1-2 hrs)
22. `meta create workflows` - Medium workflow creation (1-2 hrs)
23. `meta populate kb` - Medium KB population (1-2 hrs)
24. `meta optimize all` - Advanced full optimization (3+ hrs)
25. `meta create skill` - Advanced skill development (3+ hrs)
26. `meta enhance workflows` - Advanced enhancement (3+ hrs)
27. `meta test capability` - Advanced reflection test (3+ hrs)

#### Help & Info (2 commands)
28. `meta` - Show all commands (this reference)
29. `meta --help` - Show help information

**Total**: 29 meta commands available

---

**Version**: 1.0.0  
**Maintained by**: opencode AI agent  
**Updated**: 2026-04-25
