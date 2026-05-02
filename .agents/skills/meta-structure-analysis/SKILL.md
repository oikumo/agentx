---
name: meta-structure-analysis
description: >
  Analyze and optimize Meta Project Harness directory structure.
  Ensures clear navigation, consistent naming, and proper isolation.
version: 1.0.0
author: agentx
---

# Meta Structure Analysis

Comprehensive analysis of Meta Project Harness directory structure for optimal organization and navigation.

## Quick Start

**Load**: `skill meta-structure-analysis`
**Time**: 1-3 hours
**Outcome**: Optimized structure with migration plan

## When to Use

- Navigation is confusing
- Directory purpose unclear
- Before major structural changes
- Inconsistent naming patterns
- Too many sibling directories (>7)
- Directory depth >3 levels
- Regular maintenance (quarterly)

## Analysis Framework

### 1. Structure Mapping

Map current directory structure:
```bash
# Tree view (depth 3)
tree -L 3 -d

# Count siblings per directory
find . -maxdepth 2 -type d | cut -d/ -f2 | uniq -c | sort -rn

# Find META.md files
find . -name "META.md" -type f
```

### 2. Naming Consistency

Check naming patterns:
- `.meta.*` pattern for META directories
- Clear, descriptive names
- No abbreviations unless standard
- Consistent casing (snake_case)

### 3. Usage Analysis

Analyze directory usage:
```bash
# Recent modifications
find .meta -type f -mtime -30

# Git activity
git log --oneline --all -- .meta/sandbox/ | head -20

# File count per directory
find .meta -type f | cut -d/ -f2 | uniq -c | sort -rn
```

### 4. Best Practices Validation

**Guidelines**:
- Directory depth ≤ 3 levels
- Sibling directories ≤ 7
- Each directory has META.md
- Clear purpose statement
- Decision tree for navigation

## Workflow

### Step 1: Load Skill
```bash
skill meta-structure-analysis
```

### Step 2: Map Current Structure
```bash
# Generate tree
tree -L 3 -d > structure_current.txt

# Count directories
find . -type d | wc -l

# Find all META.md
find . -name "META.md" | sort
```

### Step 3: Analyze Each Directory
For each directory:
1. Has META.md?
2. Clear purpose?
3. Consistent naming?
4. Appropriate depth?
5. Clear sibling relationships?

### Step 4: Identify Issues
Common issues:
- ❌ Missing META.md
- ❌ Unclear purpose
- ❌ Inconsistent naming
- ❌ Too deep (>3 levels)
- ❌ Too many siblings (>7)
- ❌ Overlapping purposes
- ❌ Orphaned directories

### Step 5: Propose Improvements
For each issue:
1. Describe problem
2. Propose solution
3. Estimate effort
4. Identify risks
5. Plan migration

### Step 6: Implement in Sandbox
```bash
# Work in sandbox
cd .meta/sandbox/

# Create proposed structure
mkdir -p proposed_structure

# Test navigation
# Validate improvements
```

### Step 7: Document Changes
```markdown
## Structure Change: [Name]
**Date**: YYYY-MM-DD
**Reason**: [Why change needed]

### Before
```
current/structure
├── dir1
└── dir2
```

### After
```
new/structure
├── dir1
└── dir2
```

### Migration Plan
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Validation
- [ ] All links updated
- [ ] META.md created/updated
- [ ] Tests pass
- [ ] Navigation clear
```

## Analysis Templates

### Structure Report Template
```markdown
# Structure Analysis Report
Date: YYYY-MM-DD
Agent: [Agent name]

## Current State
- Total directories: X
- Depth (max): X levels
- Siblings (max): X
- META.md coverage: X%

## Issues Identified
| Issue | Severity | Location | Solution |
|-------|----------|----------|----------|
| Missing META.md | High | .meta/tools/ | Create META.md |
| Too many siblings | Medium | .meta/ | Consolidate |
| Unclear purpose | High | .meta/legacy/ | Clarify or remove |

## Recommendations
### Priority 1 (Critical)
1. [Issue] → [Action]

### Priority 2 (Important)
2. [Issue] → [Action]

### Priority 3 (Optional)
3. [Issue] → [Action]

## Migration Plan
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Validation Criteria
- [ ] All directories have META.md
- [ ] Clear purpose statements
- [ ] Consistent naming
- [ ] Depth ≤ 3 levels
- [ ] Siblings ≤ 7
```

### Directory Analysis Template
```markdown
# Directory Analysis: [name]

## Metadata
- **Path**: `.meta/[name]/`
- **Depth**: X levels
- **Siblings**: X directories
- **META.md**: Yes/No
- **Last Modified**: YYYY-MM-DD

## Purpose
[Clear purpose statement]

## Contents
- [Key files/subdirectories]

## Usage Pattern
[When to use this directory]

## Issues
- [ ] Missing META.md
- [ ] Unclear purpose
- [ ] Inconsistent naming
- [ ] Too deep
- [ ] Too many siblings
- [ ] Overlapping purpose

## Recommendations
[Specific improvements]
```

## Best Practices

### Directory Structure
1. **Depth**: Maximum 3 levels
2. **Siblings**: Maximum 7 per parent
3. **Naming**: Consistent pattern (`.meta.*`)
4. **META.md**: Required for all directories
5. **Purpose**: Clear, single responsibility

### META.md Requirements
Every META.md must contain:
- Purpose (why exists)
- Target (when to use)
- Rules (constraints)
- Structure (what's inside)

### Navigation
- Decision trees for choices
- Clear examples
- Link to related directories
- Avoid circular references

### Maintenance
- Regular audits (quarterly)
- Track usage patterns
- Remove orphaned directories
- Update documentation

## Common Patterns

### Good Structure
```
.meta/
├── sandbox/          # Safe workspace
├── experiments/      # Experimental features
├── tests_sandbox/    # TDD workspace
├── knowledge_base/   # RAG knowledge
├── reflection/       # Test logs
├── tools/            # Development tools
└── doc/              # Documentation
```

### Bad Structure (Too Deep)
```
.meta/
└── development/
    └── tools/
        └── python/
            └── scripts/  # ❌ Too deep (4 levels)
```

### Bad Structure (Too Many Siblings)
```
.meta/
├── sandbox/
├── experiments/
├── tests/
├── tools/
├── docs/
├── logs/
├── temp/
├── archive/
├── backup/
└── ...  # ❌ Too many (10+)
```

## Integration

### With Other Skills
- `meta-token-audit`: Analyze documentation structure
- `meta-harness-optimize`: Full optimization
- `meta-compress-docs`: Compress META.md files

### With Tools
- `tree`: Generate directory trees
- `find`: Locate files and directories
- `bash`: Run analysis commands
- `read`: Read META.md files
- `glob`: Find patterns

## Resources

- **Templates**: Structure report and directory analysis
- **Patterns**: Good and bad structure examples
- **Guidelines**: Best practices for organization
- **Checklists**: Validation criteria

## Version History

- **1.0.0** (2026-05-02): Initial version with structure analysis framework, workflow, templates, and best practices

---

**Maintained by**: agentx
**Analysis Frequency**: Quarterly or before major changes
**Target**: Clear navigation, consistent naming, proper isolation
