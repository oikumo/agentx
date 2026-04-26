# Meta Commands - Agent Interaction Patterns

## Overview

Meta commands are **natural language prompts** you use during AI agent conversations to trigger specific workflows and operations.

**Format**: `meta <action> [target] [options]`

**Examples:**
- `meta token audit` - Run token audit
- `meta health check` - Check harness health
- `meta kb populate both` - Populate both KBs

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

**Version**: 1.0.0  
**Maintained by**: opencode AI agent
