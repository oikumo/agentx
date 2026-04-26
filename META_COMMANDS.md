# Meta Commands - Agent Interaction Patterns

## Overview

Meta commands are **natural language prompts** you use during AI agent conversations to trigger specific workflows and operations.

**Format**: `meta <action> [target] [options]`

**Examples:**
- `meta token audit` - Run token audit
- `meta health check` - Check harness health
- `meta kb populate both` - Populate both KBs

### Print All Commands

**Commands:**
- `meta`- Show all commands that are in this file

This displays the complete command reference with descriptions and examples.

---

## Knowledge Base Commands

### Population

**Commands:**
- `meta kb populate both` - Clean and populate both KBs
- `meta kb populate meta` - Populate only Meta Harness KB
- `meta kb populate agentx` - Populate only Agent-X KB

**What happens**: Agent traverses all `.meta*` directories, extracts knowledge from Markdown files, and populates both knowledge bases.

### Search & Query

**Commands:**
- `meta kb search "TDD workflow"` - Search knowledge base
- `meta kb ask "Where should I write tests?"` - Ask question with RAG
- `meta kb stats` - Show statistics

### Knowledge Management

**Commands:**
- `meta kb add pattern workflow "Bug Fix" "Reproduce in sandbox" "Test → Fix → Verify"` - Add new entry
- `meta kb correct 123 "Outdated" "New finding"` - Correct existing entry
- `meta kb evolve` - Run evolution cycle

---

## Optimization Commands

### Token Management

**Commands:**
- `meta token audit` - Analyze token usage
- `meta compress docs` - Compress documentation

### Structure & Health

**Commands:**
- `meta health check` - Run health check
- `meta structure analysis` - Analyze structure
- `meta archive experiments` - Archive old experiments

---

## Project Commands

### Quick Projects (30 min - 1 hr)

**Commands:**
- `meta token audit` - Token audit
- `meta archive experiments` - Archive experiments
- `meta consolidate docs` - Consolidate docs
- `meta health check` - Monthly health check

### Medium Projects (1-3 hrs)

**Commands:**
- `meta compress docs` - Documentation compression
- `meta structure analysis` - Structure optimization
- `meta create workflows` - Create workflow templates
- `meta populate kb` - Populate knowledge base

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

User: `meta kb populate both`

Agent response shows file traversal, LLM analysis, and population results with entry counts for both KBs.

### Example 2: Quick Search

User: `meta kb search "TDD workflow"`

Agent returns relevant entries with pattern details, findings, solutions, and file context.

### Example 3: Health Check

User: `meta health check`

Agent runs health check showing documentation token usage, structure status, and overall health assessment.

### Example 4: Token Audit

User: `meta token audit`

Agent analyzes token consumption across all META.md files and provides total count with budget recommendation.

### Example 5: Archive Experiments

User: `meta archive experiments`

Agent archives old experiments and reports the number of experiments archived with token count.

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
- `meta kb search "existing pattern"`
- `meta kb add to kb ...`

**Pattern 2: Check then Modify**
- `meta health check`
- `meta run <optimization>`

**Pattern 3: Periodic Maintenance**
- `meta token audit` (Monthly)
- `meta archive experiments` (Quarterly)
- `meta kb evolve` (As needed)

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

1. Header with command name and description
2. Progress/status updates with success indicators
3. Summary/result section

---

## Related

- [KB_GUIDE.md](KB_GUIDE.md) - Detailed KB documentation
- [AGENTS.md](../AGENTS.md) - Agent rules
- [WORKFLOWS.md](../.meta.project_development/WORKFLOWS.md) - Workflow patterns

---

## Complete Command Reference

### Quick Reference Card

**Knowledge Base**
- `meta kb populate [both|meta|agentx]`
- `meta kb search "<query>" [--top_k N]`
- `meta kb ask "<question>"`
- `meta kb stats`
- `meta kb add pattern <category> "<title>" "<finding>" "<solution>"`
- `meta kb correct <id> "<reason>" "<new_finding>"`
- `meta kb evolve`

**Optimization**
- `meta token audit [--output file.md]`
- `meta compress docs [--target ratio]`
- `meta structure analysis`
- `meta health check`
- `meta archive experiments [--older_than_days N]`

**Projects**
- `meta token audit` - Quick (30 min)
- `meta archive experiments` - Quick (30 min)
- `meta consolidate docs` - Quick (30 min)
- `meta health check` - Quick (30 min)
- `meta compress docs` - Medium (1-2 hrs)
- `meta structure analysis` - Medium (1-2 hrs)
- `meta create workflows` - Medium (1-2 hrs)
- `meta populate kb` - Medium (1-2 hrs)
- `meta optimize all` - Advanced (3+ hrs)
- `meta create skill` - Advanced (3+ hrs)
- `meta enhance workflows` - Advanced (3+ hrs)
- `meta test capability` - Advanced (3+ hrs)

**Help**
- `meta` - Show this reference
- `meta --help` - Show help
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
