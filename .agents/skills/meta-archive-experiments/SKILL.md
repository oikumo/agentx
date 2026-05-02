---
name: meta-archive-experiments
description: >
  Archive completed experiments and clean up workspace.
  Preserves learnings while reducing clutter.
version: 1.0.0
author: agentx
---

# Meta Archive Experiments

Archive completed experimental work to maintain clean workspace while preserving valuable learnings.

## Quick Start

**Load**: `skill meta-archive-experiments`
**Time**: 30 minutes
**Outcome**: Clean workspace, preserved learnings

## When to Use

- Experiment completed (success or failure)
- Monthly cleanup
- Workspace cluttered
- Before major structural changes
- Quarterly maintenance

## Archiving Criteria

### Archive When
- ✅ Experiment completed
- ✅ Results documented
- ✅ Learnings extracted
- ✅ No active work
- ✅ Old (>30 days)

### Keep Active When
- 🔄 Work in progress
- 🔄 Results pending
- 🔄 Referenced frequently
- 🔄 Template for future work

## Workflow

### Step 1: Load Skill
```bash
skill meta-archive-experiments
```

### Step 2: Identify Candidates
```bash
# Find old experiments
find .meta/experiments -type d -mtime +30

# List by date
ls -lt .meta/experiments/

# Check last modification
find .meta/experiments -name "*.md" -exec stat -c "%y %n" {} \; | sort
```

### Step 3: Evaluate Each Experiment
For each experiment:
1. Completed?
2. Documented?
3. Learnings extracted?
4. Referenced by other work?
5. Template value?

### Step 4: Archive Process
For each experiment to archive:
```bash
# Create archive directory
mkdir -p .meta/archive/experiments/YYYY/

# Move experiment
mv .meta/experiments/exp-name .meta/archive/experiments/YYYY/

# Update references
# (Update any links or references)
```

### Step 5: Document Archive
```markdown
## Archived Experiments
**Date**: YYYY-MM-DD
**Count**: X experiments

| Experiment | Date | Result | Learnings |
|------------|------|--------|-----------|
| exp-1 | 2026-01 | Success | [Summary] |
| exp-2 | 2026-02 | Failed | [Summary] |

## Preserved Learnings
- [Learning 1]
- [Learning 2]
- [Learning 3]
```

## Archive Structure

### Directory Layout
```
.meta/
├── experiments/        # Active experiments
│   ├── exp-1/
│   └── exp-2/
└── archive/
    └── experiments/    # Archived experiments
        ├── 2025/
        │   ├── exp-1/
        │   └── exp-2/
        └── 2026/
            ├── exp-3/
            └── exp-4/
```

### Archive Metadata
Each archived experiment should have:
- Original date
- Archive date
- Result (success/failure)
- Key learnings
- References to related work

## Templates

### Archive Report Template
```markdown
# Experiment Archive Report
Date: YYYY-MM-DD
Agent: [Agent name]

## Summary
- Experiments archived: X
- Total learnings preserved: X
- Workspace reduced: X%

## Archived Experiments
| Name | Original Date | Result | Key Learning |
|------|---------------|--------|--------------|
| exp-1 | 2026-01-15 | Success | [Learning] |
| exp-2 | 2026-02-20 | Failed | [Learning] |

## Learnings Preserved
1. **Learning 1**: [Description]
2. **Learning 2**: [Description]
3. **Learning 3**: [Description]

## Workspace Impact
- Before: X experiments
- After: Y experiments
- Archived: Z experiments
- Reduction: W%

## References Updated
- [ ] META.md files updated
- [ ] Links fixed
- [ ] Documentation current
```

### Experiment Summary Template
```markdown
# Experiment Summary: [Name]

## Metadata
- **Created**: YYYY-MM-DD
- **Archived**: YYYY-MM-DD
- **Result**: Success/Failure
- **Status**: Archived

## Objective
[What was tested]

## Outcome
[What happened]

## Key Learnings
1. [Learning 1]
2. [Learning 2]
3. [Learning 3]

## Related Work
- [References to other experiments]
- [References to production code]

## Archive Location
`.meta/archive/experiments/YYYY/[name]/`
```

## Best Practices

### When to Archive
- After 30 days of inactivity
- When experiment is complete
- Before major cleanup
- When workspace cluttered

### What to Preserve
- All learnings (success or failure)
- Key code snippets
- Test results
- References to related work

### What to Remove
- Temporary files
- Incomplete notes
- Duplicate content
- Broken experiments

### Organization
- Group by year
- Maintain metadata
- Update references
- Keep learnings accessible

## Common Patterns

### Good Archive Candidate
```
.meta/experiments/feature-test/
├── SESSION.md          # Complete session log
├── results.md          # Documented results
├── learnings.md        # Key takeaways
└── code/               # Working code samples
```

**Action**: Archive with full metadata

### Keep Active
```
.meta/experiments/ongoing-research/
├── SESSION.md          # Active work
├── notes.md            # In progress
└── tests/              # Active tests
```

**Action**: Keep in active experiments

## Integration

### With Other Skills
- `meta-health-check`: Check archive health
- `meta-structure-analysis`: Organize archives
- `meta-token-audit`: Audit archived docs

### With Tools
- `read`: Read experiment logs
- `bash`: Move and organize files
- `glob`: Find experiment files
- `edit`: Update references

## Resources

- **Templates**: Archive report and summary templates
- **Structure**: Recommended archive organization
- **Criteria**: Decision framework for archiving

## Version History

- **1.0.0** (2026-05-02): Initial version with archiving workflow, templates, and best practices

---

**Maintained by**: agentx
**Archive Frequency**: Monthly or when cluttered
**Target**: Clean workspace, preserved learnings
