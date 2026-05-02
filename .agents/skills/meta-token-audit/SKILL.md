---
name: meta-token-audit
description: >
  Analyze token consumption across Meta Project Harness documentation.
  Identifies optimization opportunities to reduce token usage by 30-50%.
version: 1.0.0
author: agentx
---

# Meta Token Audit

Quick token consumption analysis for Meta Project Harness documentation and codebase.

## Quick Start

**Load**: `skill meta-token-audit`
**Time**: 30 minutes
**Savings**: Identifies 30-50% token reduction opportunities

## When to Use

- Token usage seems excessive
- Before documentation updates
- Monthly cost optimization
- After major documentation changes
- When agents report slow performance
- Budget planning

## Core Functionality

### Token Analysis

Analyzes token consumption across:
- Core documentation (AGENTS.md, META_HARNESS.md)
- Directory META.md files
- Skills documentation
- Workflow files
- Examples and templates

### Token Budgets

| Type | Budget | Priority |
|------|--------|----------|
| Core (AGENTS.md) | 1,500 | Critical |
| Core (META_HARNESS) | 2,000 | Critical |
| Directory META.md | 500 | High |
| Skills | 1,000 | High |
| Examples | 300 | Medium |

## Workflow

### Step 1: Load Skill
```bash
skill meta-token-audit
```

### Step 2: Run Token Count
```bash
# Count tokens in all .md files
find . -name "*.md" -exec wc -w {} + | sort -rn
```

### Step 3: Categorize Files
```bash
# Core files
wc -w AGENTS.md META_HARNESS.md

# Directory META files
find .meta -name "META.md" -exec wc -w {} +

# Skills
find .agents/skills -name "SKILL.md" -exec wc -w {} +
```

### Step 4: Identify Overruns
Check files exceeding budgets:
- >1000 words: Consider splitting
- Multiple similar examples: Consolidate
- Verbose prose: Convert to tables
- Redundant sections: Remove or link

### Step 5: Generate Report
```markdown
# Token Audit Report
Date: YYYY-MM-DD

## Summary
- Total files analyzed: X
- Files over budget: X
- Total tokens: X,XXX
- Target tokens: X,XXX
- Reduction needed: X%

## Files Over Budget
| File | Current | Budget | Over |
|------|---------|--------|------|
| AGENTS.md | 1,121 | 1,500 | ✅ |
| META_HARNESS.md | 1,813 | 2,000 | ✅ |

## Recommendations
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]
```

## Compression Techniques

### 1. Remove Redundancy
**Before** (200 tokens):
```markdown
The sandbox is a **safe space** for AI agents to:
- Test code changes before production
- Experiment with different implementations
- Validate fixes and features
- Run potentially risky operations

The sandbox provides a safe environment where AI agents can work
without affecting the production codebase.
```

**After** (50 tokens):
```markdown
## Core Philosophy
Sandbox: Safe space for AI agents to test, modify, and experiment without affecting production.
```

**Savings**: 75%

### 2. Use Tables
**Before** (150 tokens):
```markdown
### .project_development/
Use when you need to understand rules, check standards, review workflows.

### .experiments/
Use when you need to test libraries, prototype features, validate hypotheses.
```

**After** (80 tokens):
```markdown
| Directory | Use When |
|-----------|----------|
| `.project_development/` | Rules, standards, workflows |
| `.experiments/` | Test, prototype, validate |
```

**Savings**: 47%

### 3. Simplify Language
**Before**: "It is absolutely critical that you never commit or push changes without permission."

**After**: "**NEVER commit** without permission."

**Savings**: 80%

### 4. Decision Trees
**Before**: 200 tokens of prose

**After** (50 tokens):
```
Need to...
├─ Modify code? → .sandbox/
├─ Write tests? → .tests_sandbox/
├─ Test idea? → .experiments/
└─ Use tools? → .development_tools/
```

**Savings**: 75%

## Templates

### Token Audit Report Template
```markdown
# Token Audit Report
Date: YYYY-MM-DD
Auditor: [Agent name]

## Executive Summary
- Overall Status: [HEALTHY | NEEDS ATTENTION | CRITICAL]
- Total Tokens: X,XXX
- Target Tokens: X,XXX
- Reduction: X%

## Token Breakdown
| Category | Tokens | Budget | Status |
|----------|--------|--------|--------|
| Core Docs | X,XXX | X,XXX | ✅/⚠️ |
| META Files | XXX | XXX | ✅/⚠️ |
| Skills | XXX | XXX | ✅/⚠️ |
| Examples | XXX | XXX | ✅/⚠️ |

## Top Optimization Targets
1. **File.md** (XXX tokens over budget)
   - Issue: [Description]
   - Solution: [Action]
   - Estimated savings: X%

2. **File.md** (XXX tokens over budget)
   - Issue: [Description]
   - Solution: [Action]
   - Estimated savings: X%

## Action Plan
1. [ ] Compress [File] using [Technique]
2. [ ] Remove redundant [Section]
3. [ ] Convert [Prose] to tables
4. [ ] Consolidate examples

## Cost Impact
| Usage | Before | After | Savings |
|-------|--------|-------|---------|
| 100 sessions/month | $XXX | $XXX | $XXX |
| 1,000 sessions/month | $XXX | $XXX | $XXX |
```

## Best Practices

### Writing Efficient Docs
1. One concept per sentence (<20 words)
2. Active voice
3. Lists over paragraphs
4. Examples over explanations
5. Link, don't repeat
6. Keep META.md between 100-500 words
7. Include purpose, target, rules, and structure

### Token-Efficient Patterns
**Use**: Tables, decision trees, checklists, code examples

**Avoid**: Long intros, multiple similar examples, redundant headers, verbose prose

### Quality Standards
- Regular audits (monthly)
- Track token trends
- Maintain budgets
- All tests pass
- Documentation updated
- Clarity preserved

## Common Issues & Solutions

| Issue | Solution | Savings |
|-------|----------|---------|
| Docs >1000 words | Split sections | 30-40% |
| Multiple examples | Keep best 1-2 | 50-60% |
| Verbose prose | Use tables | 40-50% |
| Cross-file redundancy | Consolidate | 20-30% |
| Long decision paths | Use trees | 60-70% |

## Integration

### With Other Skills
- `meta-harness-optimize`: Full optimization workflow
- `meta-compress-docs`: Execute compression
- `meta-structure-analysis`: Analyze structure impact

### With Tools
- `analyze_tokens.py`: Token analysis
- `read`: Read and analyze files
- `glob`: Find files and patterns
- `bash`: Structure analysis
- `edit`: Update documentation

## Resources

- **Analyzer**: `analyze_tokens.py` - Token consumption analysis tool
- **Budgets**: Token budget guidelines per file type
- **Templates**: Reusable report templates
- **Examples**: Real-world compression examples

## Version History

- **1.0.0** (2026-05-02): Initial version with token audit workflow, compression techniques, and reporting templates

---

**Maintained by**: agentx
**Audit Frequency**: Monthly or after major changes
**Target Reduction**: 30-50%
