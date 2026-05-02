---
name: meta-consolidate-docs
description: >
  Consolidate and organize documentation across Meta Project Harness.
  Eliminates redundancy and ensures single source of truth.
version: 1.0.0
author: agentx
---

# Meta Consolidate Docs

Consolidate scattered documentation into organized, non-redundant structure with clear ownership.

## Quick Start

**Load**: `skill meta-consolidate-docs`
**Time**: 30 minutes
**Outcome**: Organized, non-redundant documentation

## When to Use

- Duplicate content across files
- Outdated information present
- Multiple sources of truth
- Before major updates
- Quarterly maintenance

## Consolidation Principles

### 1. Single Source of Truth
Each concept documented once:
- Primary location
- Links from other files
- Clear ownership
- Maintained currency

### 2. Hierarchy
Clear documentation structure:
```
Level 1: AGENTS.md, META_HARNESS.md (Core)
Level 2: Directory META.md files
Level 3: Skill documentation
Level 4: Examples and templates
```

### 3. Link, Don't Repeat
- Reference primary sources
- Avoid duplication
- Maintain currency
- Clear navigation

### 4. Clear Ownership
Every document has:
- Single owner
- Clear purpose
- Maintenance schedule
- Update process

## Workflow

### Step 1: Load Skill
```bash
skill meta-consolidate-docs
```

### Step 2: Map Documentation
```bash
# Find all documentation
find . -name "*.md" | sort

# Find META.md files
find . -name "META.md" | sort

# Find duplicate content
# (Similar file names, similar content)
```

### Step 3: Identify Redundancy
For each concept:
1. Where is it documented?
2. How many locations?
3. Which is primary?
4. Which are duplicates?
5. Which is current?

### Step 4: Consolidate
For each redundant set:
1. Identify primary source
2. Merge updates
3. Remove duplicates
4. Update links
5. Document ownership

### Step 5: Validate
- [ ] Single source for each concept
- [ ] All links valid
- [ ] No orphaned docs
- [ ] Clear ownership
- [ ] Maintenance schedule

## Consolidation Patterns

### Pattern 1: Merge Duplicates
**Before**:
- `guide-a.md`: Contains workflow steps
- `guide-b.md`: Contains same workflow steps

**After**:
- `guide.md`: Single source
- Links from old locations

### Pattern 2: Extract Common
**Before**:
- File A: Contains common section X
- File B: Contains common section X
- File C: Contains common section X

**After**:
- Common.md: Section X
- File A: Links to Common.md
- File B: Links to Common.md
- File C: Links to Common.md

### Pattern 3: Hierarchical Organization
**Before**:
- Random documentation structure

**After**:
```
docs/
├── core/           # Core directives
├── workflows/      # Workflow documentation
├── directories/    # Directory guides
└── examples/       # Example documentation
```

## Templates

### Consolidation Report Template
```markdown
# Documentation Consolidation Report
Date: YYYY-MM-DD
Agent: [Agent name]

## Summary
- Files analyzed: X
- Duplicates found: X
- Consolidated to: X
- Reduction: X%

## Consolidation Actions
### 1. [Concept Name]
**Before**:
- Location 1: [path]
- Location 2: [path]

**After**:
- Primary: [path]
- Links: [paths]

**Action**: Merged and removed duplicates

### 2. [Concept Name]
**Before**:
- Location 1: [path]
- Location 2: [path]

**After**:
- Primary: [path]
- Links: [paths]

**Action**: Extracted common content

## Documentation Hierarchy
| Level | Files | Owner |
|-------|-------|-------|
| Core | AGENTS.md, META_HARNESS.md | [Owner] |
| Directory | META.md files | [Owners] |
| Skills | SKILL.md files | [Owners] |
| Examples | Various | [Owners] |

## Validation
- [ ] Single source per concept
- [ ] All links valid
- [ ] Ownership clear
- [ ] Maintenance schedule set
```

### Ownership Template
```markdown
# Document Ownership: [Name]

## Metadata
- **Document**: [path/to/file.md]
- **Owner**: [Role/Person]
- **Review Schedule**: [Monthly/Quarterly]
- **Last Review**: YYYY-MM-DD

## Purpose
[Why this document exists]

## Scope
[What it covers]

## References
- Links to: [Related docs]
- Referenced by: [Dependent docs]

## Maintenance
- [ ] Reviewed monthly
- [ ] Content current
- [ ] Links valid
- [ ] No duplicates
```

## Best Practices

### Organization
1. Hierarchical structure
2. Clear ownership
3. Single source of truth
4. Link, don't repeat
5. Regular reviews

### Content
1. One concept per document
2. Clear purpose statements
3. Current examples
4. Valid links
5. Maintenance schedule

### Maintenance
1. Regular reviews (quarterly)
2. Update ownership
3. Remove orphans
4. Fix broken links
5. Track changes

## Common Issues & Solutions

| Issue | Solution | Prevention |
|-------|----------|------------|
| Duplicate content | Consolidate to single source | Clear ownership |
| Outdated info | Update primary, remove copies | Regular reviews |
| Broken links | Fix or remove | Link validation |
| Orphaned docs | Archive or remove | Ownership tracking |
| Unclear ownership | Assign owner | Documentation policy |

## Integration

### With Other Skills
- `meta-token-audit`: Check token efficiency
- `meta-compress-docs`: Compress after consolidation
- `meta-health-check`: Validate health

### With Tools
- `read`: Read and compare files
- `edit`: Consolidate content
- `glob`: Find documentation
- `bash`: Organize files

## Resources

- **Templates**: Consolidation report and ownership templates
- **Patterns**: Common consolidation patterns
- **Guidelines**: Best practices for organization

## Version History

- **1.0.0** (2026-05-02): Initial version with consolidation workflow, patterns, templates, and best practices

---

**Maintained by**: agentx
**Consolidation Frequency**: Quarterly or when redundant
**Target**: Single source of truth, clear ownership
