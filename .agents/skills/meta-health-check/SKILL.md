---
name: meta-health-check
description: >
  Comprehensive health check for Meta Project Harness.
  Validates documentation, structure, tokens, and workflows.
version: 1.0.0
author: agentx
---

# Meta Health Check

Quick health assessment for Meta Project Harness covering documentation, structure, token usage, and workflow efficiency.

## Quick Start

**Load**: `skill meta-health-check`
**Time**: 30 minutes
**Output**: Health status report with recommendations

## When to Use

- Monthly maintenance
- Before major changes
- After harness updates
- Performance issues
- Agent confusion reported
- Regular checkups

## Health Dimensions

### 1. Documentation Health
- META.md presence
- Purpose clarity
- Examples current
- Links valid

### 2. Structure Health
- Naming consistency
- Depth appropriate
- Sibling count
- Clear navigation

### 3. Token Health
- Within budgets
- No redundancy
- Efficient patterns
- Clear language

### 4. Workflow Health
- Clear decision paths
- Templates current
- Examples working
- Agents successful

## Workflow

### Step 1: Load Skill
```bash
skill meta-health-check
```

### Step 2: Documentation Check
```bash
# Find all META.md files
find . -name "META.md" | wc -l

# Expected directories
expected_dirs=("sandbox" "experiments" "tests_sandbox" "knowledge_base" "reflection" "tools" "doc")

# Check coverage
for dir in "${expected_dirs[@}"; do
    if [ -f ".meta/$dir/META.md" ]; then
        echo "✅ .meta/$dir/META.md"
    else
        echo "❌ .meta/$dir/META.md MISSING"
    fi
done
```

### Step 3: Structure Check
```bash
# Check depth
find .meta -type d | awk -F/ '{print NF}' | sort -rn | head -5

# Check siblings
find .meta -mindepth 2 -maxdepth 2 -type d | wc -l
```

### Step 4: Token Check
```bash
# Count words in key files
wc -w AGENTS.md META_HARNESS.md
wc -w .meta/*/META.md
```

### Step 5: Generate Report
```markdown
# Health Check Report
Date: YYYY-MM-DD
Agent: [Agent name]

## Summary
- Overall Status: [HEALTHY | NEEDS ATTENTION | CRITICAL]
- Total Issues: X (Critical: X, Warnings: X)

## Documentation Status
| Directory | META.md | Purpose | Examples | Links |
|-----------|---------|---------|----------|-------|
| sandbox | ✅ | ✅ | ✅ | ✅ |
| experiments | ✅ | ✅ | ✅ | ✅ |
| tests_sandbox | ❌ | - | - | - |

## Structure Status
- Max depth: X (target: ≤3)
- Max siblings: X (target: ≤7)
- Naming consistent: Yes/No

## Token Status
| File | Words | Budget | Status |
|------|-------|--------|--------|
| AGENTS.md | 562 | 1,500 | ✅ |
| META_HARNESS.md | 1,136 | 2,000 | ✅ |

## Recommendations
### Priority 1 (Critical)
1. [Issue] → [Action]

### Priority 2 (Important)
2. [Issue] → [Action]

### Priority 3 (Optional)
3. [Issue] → [Action]

## Next Check
Date: YYYY-MM-DD
```

## Health Checklist

### Documentation (40%)
- [ ] All directories have META.md
- [ ] Purpose statements clear
- [ ] Examples current and working
- [ ] All links valid
- [ ] No outdated information

### Structure (30%)
- [ ] Naming consistent (`.meta.*`)
- [ ] Depth ≤ 3 levels
- [ ] Siblings ≤ 7 per parent
- [ ] Clear navigation (decision trees)
- [ ] No orphaned directories

### Tokens (20%)
- [ ] Core files within budget
- [ ] META.md files within budget
- [ ] No redundant content
- [ ] Efficient patterns used
- [ ] Cost trends tracked

### Workflows (10%)
- [ ] Decision paths clear
- [ ] Templates current
- [ ] Examples working
- [ ] Agents successful

## Scoring System

### Health Tiers
- **HEALTHY** (90-100%): All checks pass
- **NEEDS ATTENTION** (70-89%): Some issues
- **CRITICAL** (<70%): Major issues

### Scoring
- Documentation: 40 points
- Structure: 30 points
- Tokens: 20 points
- Workflows: 10 points

### Performance Metrics
Track over time:
- Documentation completeness
- Token count trends
- Structure changes
- Agent success rate

## Templates

### Health Check Report Template
```markdown
# Meta Harness Health Report
Date: YYYY-MM-DD
Agent: [Agent name]
Duration: X minutes

## Executive Summary
**Overall Status**: HEALTHY / NEEDS ATTENTION / CRITICAL
**Score**: XX/100
**Total Issues**: X (Critical: X, Warnings: X)

## Documentation (Score: X/40)
| Directory | META.md | Purpose | Examples | Links | Score |
|-----------|---------|---------|----------|-------|-------|
| sandbox | ✅ | ✅ | ✅ | ✅ | 10/10 |
| experiments | ✅ | ✅ | ✅ | ✅ | 10/10 |
| tests_sandbox | ❌ | - | - | - | 0/10 |

**Subtotal**: X/40

## Structure (Score: X/30)
- Max depth: X levels (target: ≤3) [✅/❌]
- Max siblings: X (target: ≤7) [✅/❌]
- Naming consistent: Yes/No [✅/❌]
- Clear navigation: Yes/No [✅/❌]

**Subtotal**: X/30

## Tokens (Score: X/20)
| File | Words | Budget | Status |
|------|-------|--------|--------|
| AGENTS.md | 562 | 1,500 | ✅ |
| META_HARNESS.md | 1,136 | 2,000 | ✅ |

**Subtotal**: X/20

## Workflows (Score: X/10)
- Decision paths clear: Yes/No [✅/❌]
- Templates current: Yes/No [✅/❌]
- Examples working: Yes/No [✅/❌]

**Subtotal**: X/10

## Issues
### Critical
1. [Issue] → [Action]

### Warnings
1. [Issue] → [Action]

## Recommendations
### Immediate (This Week)
1. [Action]

### Short-term (This Month)
2. [Action]

### Long-term (This Quarter)
3. [Action]

## Next Check
**Scheduled**: YYYY-MM-DD
**Focus Areas**: [Areas to watch]
```

### Quick Check Template (5 min)
```markdown
# Quick Health Check
Date: YYYY-MM-DD

## Status
- [ ] All META.md present
- [ ] No critical errors
- [ ] Token budgets met
- [ ] Agents successful

## Issues
[None / List critical only]

## Action Required
[None / Immediate action]
```

## Best Practices

### Frequency
- **Quick Check**: Weekly (5 min)
- **Full Check**: Monthly (30 min)
- **Deep Dive**: Quarterly (2-3 hrs)

### Automation
```bash
# Quick health check script
./meta_health_check.sh --quick

# Full health check
./meta_health_check.sh --full

# Generate report
./meta_health_check.sh --report
```

### Tracking
- Keep historical reports
- Track trends over time
- Set up alerts for critical issues
- Schedule regular reviews

## Common Issues & Solutions

| Issue | Solution | Priority |
|-------|----------|----------|
| Missing META.md | Create META.md | Critical |
| Token overrun | Compress docs | High |
| Unclear navigation | Add decision tree | High |
| Too many siblings | Consolidate | Medium |
| Outdated examples | Update examples | Medium |
| Broken links | Fix links | Low |

## Integration

### With Other Skills
- `meta-token-audit`: Token health check
- `meta-structure-analysis`: Structure health
- `meta-compress-docs`: Fix token issues

### With Tools
- `read`: Read META.md files
- `glob`: Find files and patterns
- `bash`: Run health checks
- `tree`: Visualize structure

## Resources

- **Templates**: Health check report templates
- **Checklists**: Comprehensive checklists
- **Scripts**: Automated health check scripts
- **Metrics**: Performance tracking

## Version History

- **1.0.0** (2026-05-02): Initial version with comprehensive health check framework, scoring system, templates, and best practices

---

**Maintained by**: agentx
**Check Frequency**: Monthly (full), Weekly (quick)
**Target**: HEALTHY (90-100%)

</parameter