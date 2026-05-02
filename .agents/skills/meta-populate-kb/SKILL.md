---
name: meta-populate-kb
description: >
  Populate and maintain Meta Project Harness knowledge base.
  Ensures KB contains current, accurate information.
version: 1.0.0
author: agentx
---

# Meta Populate KB

Comprehensive knowledge base population and maintenance for Meta Project Harness RAG system.

## Quick Start

**Load**: `skill meta-populate-kb`
**Time**: 1-3 hours
**Outcome**: Complete, current knowledge base

## When to Use

- Initial KB setup
- After major changes
- Knowledge gaps identified
- Monthly maintenance
- Before agent deployment

## KB Population Strategies

### 1. Initial Population
When setting up KB from scratch:
- Scan existing documentation
- Extract key patterns
- Create structured entries
- Validate coverage

### 2. Incremental Updates
After changes or new learnings:
- Identify new knowledge
- Create/update entries
- Link related entries
- Validate consistency

### 3. Gap Filling
When gaps identified:
- Analyze missing information
- Create targeted entries
- Validate with examples
- Test retrieval

### 4. Maintenance
Regular upkeep:
- Review outdated entries
- Remove obsolete information
- Consolidate duplicates
- Update links

## Workflow

### Step 1: Load Skill
```bash
skill meta-populate-kb
```

### Step 2: Scan Documentation
```bash
# Find all documentation
find . -name "*.md" | sort

# Identify key files
# - AGENTS.md
# - META_HARNESS.md
# - */META.md
# - */SKILL.md
```

### Step 3: Extract Knowledge
For each key document:
1. Read content
2. Identify patterns
3. Extract concepts
4. Note relationships
5. Create entries

### Step 4: Create Entries
For each concept:
```markdown
# KB Entry: [Concept Name]

## Category
[Category: pattern/rule/workflow/tool]

## Description
[Clear description]

## Usage
[When/how to use]

## Examples
[Concrete examples]

## Related
- [Related concept 1]
- [Related concept 2]

## Source
[Source document]
```

### Step 5: Validate
- [ ] All key concepts covered
- [ ] No duplicates
- [ ] Links valid
- [ ] Examples current
- [ ] Retrieval tested

### Step 6: Test Retrieval
```bash
# Test queries
meta kb ask "What is [concept]?"
meta kb search "[pattern]"

# Verify results
# Check confidence scores
```

## Entry Categories

### Patterns
Recurring solutions or approaches:
- Directory usage patterns
- Workflow patterns
- Documentation patterns
- Code patterns

### Rules
Non-negotiable requirements:
- Core directives
- Safety rules
- Quality gates
- Naming conventions

### Workflows
Step-by-step processes:
- Development workflows
- Documentation workflows
- Maintenance workflows
- Quality workflows

### Tools
Available utilities and commands:
- KB commands
- Analysis tools
- Automation scripts
- Helper functions

## Templates

### KB Entry Template
```markdown
# KB Entry: [Name]

## Metadata
- **ID**: [PAT-XXXX]
- **Category**: [pattern/rule/workflow/tool]
- **Created**: YYYY-MM-DD
- **Updated**: YYYY-MM-DD

## Description
[Clear, concise description]

## Purpose
[Why this exists]

## Usage
[When to use]
- [Use case 1]
- [Use case 2]

## Examples
### Example 1: [Scenario]
[Example content]

### Example 2: [Scenario]
[Example content]

## Related Entries
- [Related entry 1](link)
- [Related entry 2](link)

## Source
[Source document or location]

## Confidence
[Confidence level: High/Medium/Low]
```

### Population Report Template
```markdown
# KB Population Report
Date: YYYY-MM-DD
Agent: [Agent name]

## Summary
- Entries created: X
- Entries updated: X
- Entries removed: X
- Total entries: X

## Coverage by Category
| Category | Count | Coverage |
|----------|-------|----------|
| Patterns | X | X% |
| Rules | X | X% |
| Workflows | X | X% |
| Tools | X | X% |

## New Entries
1. **[Name]** ([Category])
   - Description: [Brief]
   - Source: [Document]

2. **[Name]** ([Category])
   - Description: [Brief]
   - Source: [Document]

## Updated Entries
1. **[Name]**: [What changed]

## Removed Entries
1. **[Name]**: [Why removed]

## Gaps Identified
1. [Missing concept 1]
2. [Missing concept 2]

## Validation
- [ ] All key concepts covered
- [ ] No duplicates
- [ ] Links valid
- [ ] Retrieval tested
```

## Best Practices

### Entry Creation
1. One concept per entry
2. Clear, concise descriptions
3. Concrete examples
4. Link related entries
5. Cite sources

### Entry Maintenance
1. Regular reviews
2. Update when source changes
3. Remove obsolete entries
4. Consolidate duplicates
5. Validate retrieval

### Organization
1. Consistent categories
2. Clear naming
3. Logical structure
4. Easy navigation
5. Searchable content

### Quality
1. Accurate information
2. Current examples
3. Valid links
4. Clear descriptions
5. Test retrieval

## Common Issues & Solutions

| Issue | Solution | Prevention |
|-------|----------|------------|
| Duplicate entries | Consolidate | Check before creating |
| Outdated info | Update entry | Regular reviews |
| Missing concepts | Create entry | Gap analysis |
| Broken links | Fix links | Link validation |
| Poor retrieval | Improve content | Test queries |

## Integration

### With Other Skills
- `meta-health-check`: Check KB health
- `meta-harness-reflection`: Test KB knowledge
- `meta-harness-optimize`: Optimize KB structure

### With Tools
- `kb.py`: KB management commands
- `read`: Read source documents
- `edit`: Create/update entries
- `glob`: Find documentation

## Resources

- **Templates**: Entry and report templates
- **Categories**: Standard KB categories
- **Guidelines**: Best practices for population

## Version History

- **1.0.0** (2026-05-02): Initial version with KB population workflow, templates, and best practices

---

**Maintained by**: agentx
**Population Frequency**: Monthly or after major changes
**Target**: Complete, current, retrievable knowledge
