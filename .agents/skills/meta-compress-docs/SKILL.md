---
name: meta-compress-docs
description: >
  Compress documentation by removing redundancy, using tables,
  simplifying language, and implementing decision trees.
version: 1.0.0
author: agentx
---

# Meta Compress Docs

Documentation compression skill for reducing token consumption while maintaining clarity and completeness.

## Quick Start

**Load**: `skill meta-compress-docs`
**Time**: 1-3 hours
**Savings**: 30-50% token reduction

## When to Use

- Documentation exceeds token budgets
- Files are verbose or unclear
- Multiple similar examples exist
- Prose-heavy sections
- Before publishing documentation
- Regular maintenance (quarterly)

## Core Compression Techniques

### Technique 1: Remove Redundancy

**Pattern**: Identify and remove repeated concepts

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

### Technique 2: Use Tables

**Pattern**: Convert prose lists to tables

**Before** (150 tokens):
```markdown
### .project_development/
Use when you need to understand rules, check standards, review workflows.

### .experiments/
Use when you need to test libraries, prototype features, validate hypotheses.

### .sandbox/
Use when you need to modify code safely without affecting production.
```

**After** (80 tokens):
```markdown
| Directory | Use When |
|-----------|----------|
| `.project_development/` | Rules, standards, workflows |
| `.experiments/` | Test, prototype, validate |
| `.sandbox/` | Modify code safely |
```

**Savings**: 47%

### Technique 3: Simplify Language

**Pattern**: Use active voice, short sentences, direct commands

**Before**: "It is absolutely critical that you never commit or push changes without permission."

**After**: "**NEVER commit** without permission."

**Savings**: 80%

**Guidelines**:
- Active voice only
- <20 words per sentence
- Direct commands (NEVER, ALWAYS)
- Remove hedging language
- Remove filler words

### Technique 4: Decision Trees

**Pattern**: Replace navigation prose with visual trees

**Before** (200 tokens):
```markdown
When you need to modify code, you should use the sandbox directory.
If you need to write tests, you should use the tests_sandbox directory.
For experimental features, the experiments directory is appropriate.
When you need to use or create tools, you should work in the development_tools directory.
```

**After** (50 tokens):
```
Need to...
├─ Modify code? → .sandbox/
├─ Write tests? → .tests_sandbox/
├─ Test idea? → .experiments/
└─ Use tools? → .development_tools/
```

**Savings**: 75%

## Workflow

### Step 1: Load Skill
```bash
skill meta-compress-docs
```

### Step 2: Identify Targets
```bash
# Find large files
find . -name "*.md" -exec wc -w {} + | sort -rn | head -20

# Check against budgets
# - Core: >1500 words
# - META: >500 words
# - Skills: >1000 words
# - Examples: >300 words
```

### Step 3: Analyze Each File
For each target file:
1. Read entire content
2. Identify redundancy patterns
3. Find prose that can be tables
4. Locate verbose language
5. Check for decision points needing trees

### Step 4: Apply Compression
For each issue found:
1. Remove redundant sections
2. Convert to tables
3. Simplify language
4. Add decision trees
5. Consolidate examples

### Step 5: Validate
- [ ] All information preserved
- [ ] Clarity maintained or improved
- [ ] Token count reduced
- [ ] Budget met
- [ ] No broken links

### Step 6: Document Changes
```markdown
## Compression Summary
**File**: path/to/file.md
**Before**: X,XXX tokens
**After**: X,XXX tokens
**Reduction**: X%

**Changes**:
- Removed redundant [section]
- Converted [list] to table
- Simplified [section] language
- Added decision tree for [workflow]
```

## Compression Checklist

### Content Review
- [ ] Remove repeated concepts
- [ ] Consolidate similar examples (keep best 1-2)
- [ ] Remove long introductions
- [ ] Remove redundant headers
- [ ] Link instead of repeating

### Format Optimization
- [ ] Convert lists to tables
- [ ] Add decision trees for navigation
- [ ] Use checklists for requirements
- [ ] Use code blocks for examples
- [ ] Remove unnecessary formatting

### Language Simplification
- [ ] Active voice only
- [ ] <20 words per sentence
- [ ] Remove hedging language
- [ ] Remove filler words
- [ ] Direct commands (NEVER, ALWAYS, MUST)

### Structure Validation
- [ ] Clear hierarchy
- [ ] Logical flow
- [ ] No circular references
- [ ] All links work
- [ ] META.md present

## Templates

### Compression Report Template
```markdown
# Documentation Compression Report
Date: YYYY-MM-DD
Agent: [Agent name]

## Summary
| File | Before | After | Reduction |
|------|--------|-------|-----------|
| AGENTS.md | 1,121 | 562 | -50.0% |
| META_HARNESS.md | 1,813 | 1,136 | -37.4% |
| **Total** | 2,934 | 1,698 | **-42.2%** |

## Techniques Applied
1. **Redundancy Removal**: X sections removed
2. **Table Conversion**: X lists converted
3. **Language Simplification**: X sections simplified
4. **Decision Trees**: X navigation sections converted

## Quality Metrics
- Information preserved: 100%
- Clarity improved: Yes
- Token budget met: Yes
- All links valid: Yes

## Cost Impact
| Usage | Before | After | Monthly Savings |
|-------|--------|-------|-----------------|
| 100 sessions | $376 | $261 | $115 |
| 1,000 sessions | $3,758 | $2,610 | $1,148 |
```

### Before/After Template
```markdown
## Compression Example: [Section Name]

### Before (X tokens)
```markdown
[Original content]
```

### After (Y tokens)
```markdown
[Compressed content]
```

**Savings**: Z%
**Technique**: [Technique used]
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
**Use**:
- Tables for comparisons
- Decision trees for navigation
- Checklists for requirements
- Code blocks for examples

**Avoid**:
- Long introductions
- Multiple similar examples
- Redundant headers
- Verbose prose
- Circular references

### Quality Standards
- Regular compression (quarterly)
- Track token trends
- Maintain budgets
- All tests pass
- Documentation updated
- Clarity preserved

## Common Patterns

### Good Compression
```markdown
## Rules
- NEVER commit without permission
- ALWAYS query KB first
- ALWAYS follow META rules
```

### Bad (Verbose)
```markdown
## Rules
It is very important that you should never commit or push changes
without first obtaining explicit permission from the user.
You should also always query the knowledge base first before
starting any task.
```

## Integration

### With Other Skills
- `meta-token-audit`: Identify targets
- `meta-harness-optimize`: Full optimization
- `meta-structure-analysis`: Validate structure

### With Tools
- `read`: Read and analyze files
- `edit`: Apply compression
- `glob`: Find documentation files
- `bash`: Count tokens

## Resources

- **Templates**: Compression report and before/after templates
- **Examples**: Real-world compression examples
- **Budgets**: Token budget guidelines
- **Techniques**: Four core compression methods

## Version History

- **1.0.0** (2026-05-02): Initial version with four compression techniques, workflow, templates, and best practices

---

**Maintained by**: agentx
**Compression Frequency**: Quarterly or when over budget
**Target Reduction**: 30-50%
