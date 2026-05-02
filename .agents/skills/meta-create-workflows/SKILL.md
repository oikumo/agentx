---
name: meta-create-workflows
description: >
  Create and document standardized workflows for Meta Project Harness.
  Ensures consistent, repeatable processes for common tasks.
version: 1.0.0
author: agentx
---

# Meta Create Workflows

Create, document, and maintain standardized workflows for consistent Meta Project Harness operations.

## Quick Start

**Load**: `skill meta-create-workflows`
**Time**: 1-3 hours
**Outcome**: Documented, tested workflows

## When to Use

- New recurring task identified
- Workflow needs optimization
- Onboarding new agents
- After major changes
- Quarterly review

## Workflow Categories

### 1. Development Workflows
- Feature implementation
- Bug fixing
- Refactoring
- Code review

### 2. Documentation Workflows
- Documentation updates
- META.md maintenance
- Example creation
- Link validation

### 3. Maintenance Workflows
- Health checks
- Token audits
- Structure analysis
- Archive operations

### 4. Quality Workflows
- Testing (TDD)
- Code quality checks
- Documentation review
- Compliance validation

## Workflow Structure

### Standard Workflow Template
```markdown
# Workflow: [Name]

## Purpose
[Why this workflow exists]

## When to Use
- [Trigger 1]
- [Trigger 2]

## Steps
1. **[Step 1]**: [Description]
   - Tools: [Tools needed]
   - Input: [What's needed]
   - Output: [What's produced]

2. **[Step 2]**: [Description]
   - Tools: [Tools needed]
   - Input: [What's needed]
   - Output: [What's produced]

## Validation
- [ ] [Check 1]
- [ ] [Check 2]

## Templates
[Relevant templates]

## Examples
[Example usage]
```

## Workflow Creation Process

### Step 1: Load Skill
```bash
skill meta-create-workflows
```

### Step 2: Identify Workflow
For each recurring task:
1. Frequency? (Daily/Weekly/Monthly)
2. Complexity? (Simple/Medium/Complex)
3. Success criteria?
4. Current approach?
5. Optimization opportunities?

### Step 3: Document Workflow
For each workflow:
1. Clear purpose
2. Trigger conditions
3. Step-by-step process
4. Required tools
5. Success criteria
6. Templates
7. Examples

### Step 4: Test Workflow
1. Execute workflow
2. Measure time
3. Validate outcome
4. Identify issues
5. Refine steps

### Step 5: Publish Workflow
1. Add to documentation
2. Link from relevant META.md
3. Create templates
4. Add examples
5. Train agents

## Templates

### Workflow Definition Template
```markdown
# Workflow: [Name]

## Metadata
- **Category**: [Development/Documentation/Maintenance/Quality]
- **Frequency**: [Daily/Weekly/Monthly/As needed]
- **Duration**: [X minutes/hours]
- **Complexity**: [Simple/Medium/Complex]

## Purpose
[Clear statement of why this workflow exists]

## When to Use
- [Trigger condition 1]
- [Trigger condition 2]
- [Trigger condition 3]

## Prerequisites
- [ ] [Requirement 1]
- [ ] [Requirement 2]

## Steps

### Step 1: [Name]
**Description**: [What to do]
**Tools**: [Required tools]
**Input**: [What's needed]
**Output**: [What's produced]
**Time**: [Estimated duration]

### Step 2: [Name]
[Continue steps...]

## Validation
- [ ] [Success criterion 1]
- [ ] [Success criterion 2]
- [ ] [Success criterion 3]

## Common Issues
| Issue | Solution | Prevention |
|-------|----------|------------|
| [Issue 1] | [Solution] | [Prevention] |

## Templates
- [Template 1](link)
- [Template 2](link)

## Examples
### Example 1: [Scenario]
[Example content]

## Related Workflows
- [Related workflow 1](link)
- [Related workflow 2](link)

## Version History
- **1.0.0** (YYYY-MM-DD): Initial version
```

### Workflow Catalog Template
```markdown
# Workflow Catalog

## Development Workflows
| Workflow | Purpose | Duration | Link |
|----------|---------|----------|------|
| Feature Implementation | Implement new features | 1-3 hrs | [Link] |
| Bug Fix | Fix production bugs | 30 min | [Link] |

## Documentation Workflows
| Workflow | Purpose | Duration | Link |
|----------|---------|----------|------|
| Doc Update | Update documentation | 30 min | [Link] |

## Maintenance Workflows
| Workflow | Purpose | Duration | Link |
|----------|---------|----------|------|
| Health Check | Monthly health check | 30 min | [Link] |

## Quality Workflows
| Workflow | Purpose | Duration | Link |
|----------|---------|----------|------|
| TDD | Test-driven development | Varies | [Link] |
```

## Best Practices

### Workflow Design
1. Clear purpose
2. Defined triggers
3. Step-by-step process
4. Required tools listed
5. Success criteria
6. Templates provided
7. Examples included

### Workflow Documentation
1. Consistent format
2. Clear language
3. Visual aids (decision trees)
4. Linked references
5. Version controlled

### Workflow Maintenance
1. Regular reviews
2. Update when processes change
3. Collect feedback
4. Track usage
5. Measure effectiveness

## Common Workflows

### Example: Health Check Workflow
```markdown
# Workflow: Monthly Health Check

## Purpose
Assess overall health of Meta Project Harness

## When to Use
- Monthly maintenance
- Before major changes
- Performance issues

## Steps
1. Load skill: `skill meta-health-check`
2. Run documentation check
3. Run structure check
4. Run token check
5. Generate report
6. Address critical issues
7. Schedule next check

## Validation
- [ ] Report generated
- [ ] Critical issues addressed
- [ ] Next check scheduled
```

## Integration

### With Other Skills
- `meta-health-check`: Health check workflow
- `meta-token-audit`: Token audit workflow
- `meta-structure-analysis`: Structure workflow

### With Tools
- `read`: Read workflow definitions
- `edit`: Create/update workflows
- `glob`: Find workflow files
- `bash`: Execute workflow steps

## Resources

- **Templates**: Workflow definition and catalog templates
- **Examples**: Common workflow examples
- **Guidelines**: Best practices for workflow creation

## Version History

- **1.0.0** (2026-05-02): Initial version with workflow creation process, templates, and best practices

---

**Maintained by**: agentx
**Review Frequency**: Quarterly
**Target**: Consistent, repeatable processes
