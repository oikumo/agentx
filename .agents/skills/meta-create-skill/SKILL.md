---
name: meta-create-skill
description: >
  Create new OpenCode skills for Meta Project Harness.
  Standardized skill creation with templates and best practices.
version: 1.0.0
author: agentx
---

# Meta Create Skill

Create new OpenCode skills following standardized templates and best practices for Meta Project Harness.

## Quick Start

**Load**: `skill meta-create-skill`
**Time**: 3+ hours
**Outcome**: Complete, functional OpenCode skill

## When to Use

- New recurring task identified
- Complex workflow needs automation
- Knowledge needs structured access
- Agent capability enhancement
- Best practice standardization

## Skill Categories

### 1. Analysis Skills
- Token analysis
- Structure analysis
- Code quality analysis
- Documentation analysis

### 2. Optimization Skills
- Documentation compression
- Structure optimization
- Workflow optimization
- Resource optimization

### 3. Maintenance Skills
- Health checks
- Archive operations
- KB population
- Consolidation

### 4. Creation Skills
- Workflow creation
- Documentation creation
- Test creation
- Tool creation

## Skill Structure

### Standard Skill Template
```markdown
---
name: [skill-name]
description: >
  Clear, concise description of skill purpose.
  Include key outcomes and benefits.
version: 1.0.0
author: [author]
---

# [Skill Name]

Clear introduction explaining skill purpose and scope.

## Quick Start
**Load**: `skill [name]`
**Time**: [Duration]
**Outcome**: [Expected outcome]

## When to Use
- [Use case 1]
- [Use case 2]
- [Use case 3]

## Core Functionality
[Main capabilities]

## Workflow
[Step-by-step process]

## Templates
[Reusable templates]

## Best Practices
[Guidelines and standards]

## Integration
[How it works with other skills]

## Resources
[References and tools]

## Version History
- **1.0.0** (YYYY-MM-DD): Initial version
```

## Skill Creation Process

### Step 1: Load Skill
```bash
skill meta-create-skill
```

### Step 2: Define Skill
For each new skill:
1. **Purpose**: What problem does it solve?
2. **Scope**: What's included/excluded?
3. **Users**: Who will use it?
4. **Frequency**: How often will it be used?
5. **Complexity**: Simple, medium, or complex?

### Step 3: Design Workflow
1. Identify main workflow
2. Break into steps
3. Identify required tools
4. Define success criteria
5. Create templates

### Step 4: Create Documentation
Using standard template:
1. Fill metadata
2. Write quick start
3. Document workflow
4. Create templates
5. Add examples
6. Define best practices

### Step 5: Test Skill
1. Load skill
2. Execute workflow
3. Validate outcome
4. Refine documentation
5. Test edge cases

### Step 6: Publish Skill
1. Create directory: `.agents/skills/[name]/`
2. Add SKILL.md
3. Add supporting files
4. Update skill catalog
5. Announce availability

## Templates

### Skill Definition Template
```markdown
---
name: [skill-name]
description: >
  [Clear description of skill purpose]
  [Key outcomes and benefits]
version: 1.0.0
author: [author]
---

# [Skill Name]

[Clear introduction explaining purpose, scope, and value]

## Quick Start

**Load**: `skill [name]`
**Time**: [X hours/minutes]
**Outcome**: [Expected outcome]

## When to Use

- [Use case 1]
- [Use case 2]
- [Use case 3]
- [Trigger condition]

## Core Functionality

### Feature 1
[Description]

### Feature 2
[Description]

## Workflow

### Step 1: [Name]
[Description]
```bash
[Commands if applicable]
```

### Step 2: [Name]
[Description]

## Templates

### Template 1: [Name]
```markdown
[Template content]
```

## Best Practices

### Do
- [Best practice 1]
- [Best practice 2]

### Don't
- [Anti-pattern 1]
- [Anti-pattern 2]

## Common Issues & Solutions

| Issue | Solution | Prevention |
|-------|----------|------------|
| [Issue] | [Solution] | [Prevention] |

## Integration

### With Other Skills
- `[skill-name]`: [How integrates]
- `[skill-name]`: [How integrates]

### With Tools
- `[tool]`: [How used]

## Resources

- **Templates**: [What templates available]
- **Examples**: [Example usage]
- **References**: [Related documentation]

## Version History

- **1.0.0** (YYYY-MM-DD): Initial version

---

**Maintained by**: [author]
**Update Frequency**: [As needed]
**Status**: [Active/Experimental]
```

### Skill Catalog Template
```markdown
# Skill Catalog

## Analysis Skills
| Skill | Purpose | Time | Link |
|-------|---------|------|------|
| meta-token-audit | Analyze token usage | 30 min | [Link] |

## Optimization Skills
| Skill | Purpose | Time | Link |
|-------|---------|------|------|
| meta-compress-docs | Compress documentation | 1-3 hrs | [Link] |

## Maintenance Skills
| Skill | Purpose | Time | Link |
|-------|---------|------|------|
| meta-health-check | Health assessment | 30 min | [Link] |

## Creation Skills
| Skill | Purpose | Time | Link |
|-------|---------|------|------|
| meta-create-workflows | Create workflows | 1-3 hrs | [Link] |
```

## Best Practices

### Skill Design
1. Single responsibility
2. Clear purpose
3. Documented workflow
4. Reusable templates
5. Testable outcomes

### Skill Documentation
1. Standard format
2. Quick start section
3. Clear examples
4. Best practices
5. Integration guide

### Skill Maintenance
1. Regular reviews
2. Update when needed
3. Collect feedback
4. Track usage
5. Improve continuously

## Common Patterns

### Analysis Pattern
```markdown
1. Load skill
2. Identify targets
3. Analyze each target
4. Generate report
5. Recommend actions
```

### Optimization Pattern
```markdown
1. Load skill
2. Measure current state
3. Identify improvements
4. Apply optimizations
5. Validate results
```

### Creation Pattern
```markdown
1. Load skill
2. Define requirements
3. Create structure
4. Add content
5. Test and refine
```

## Integration

### With Other Skills
- `meta-harness-optimize`: Optimize skill structure
- `meta-health-check`: Check skill health
- `meta-populate-kb`: Document skill in KB

### With Tools
- `read`: Read skill files
- `edit`: Create/update skills
- `glob`: Find skill files
- `bash`: Execute skill commands

## Resources

- **Templates**: Skill definition and catalog templates
- **Examples**: Existing skill examples
- **Guidelines**: Best practices for skill creation

## Version History

- **1.0.0** (2026-05-02): Initial version with skill creation workflow, templates, and best practices

---

**Maintained by**: agentx
**Creation Frequency**: As needed
**Target**: Standardized, reusable skills
