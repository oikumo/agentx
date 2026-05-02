---
name: meta-test-capability
description: >
  Test and validate Meta Project Harness capabilities.
  Comprehensive capability assessment and validation.
version: 1.0.0
author: agentx
---

# Meta Test Capability

Comprehensive capability testing for Meta Project Harness to validate agent understanding, workflow execution, and knowledge base effectiveness.

## Quick Start

**Load**: `skill meta-test-capability`
**Time**: 3+ hours
**Outcome**: Capability assessment with actionable insights

## When to Use

- After KB population
- Before agent deployment
- Monthly capability assessment
- After major workflow changes
- Performance issues detected
- New agent onboarding

## Capability Dimensions

### 1. Knowledge Base (30%)
- KB retrieval accuracy
- Entry completeness
- Search effectiveness
- RAG confidence scores

### 2. Workflow Execution (25%)
- Workflow understanding
- Step execution accuracy
- Template usage
- Success rate

### 3. Directory Navigation (20%)
- Correct directory selection
- Decision tree usage
- META.md comprehension
- Navigation efficiency

### 4. Rule Compliance (15%)
- Core directive adherence
- Safety rule compliance
- Quality gate validation
- META rule following

### 5. Tool Usage (10%)
- KB command usage
- Analysis tool proficiency
- Workflow tool execution
- Helper function usage

## Testing Framework

### Test Categories

#### Category 1: KB Retrieval (30 points)
Test knowledge base retrieval:
- Q1: What is the sandbox used for?
- Q2: How do you add a KB entry?
- Q3: What's the KB population workflow?
- Q4: When should you query KB?
- Q5: How do you correct KB entries?

#### Category 2: Workflow Execution (25 points)
Test workflow understanding:
- Q6: Describe the health check workflow
- Q7: Steps for token audit?
- Q8: How to compress documentation?
- Q9: Workflow for archiving experiments?
- Q10: Structure analysis steps?

#### Category 3: Directory Navigation (20 points)
Test directory selection:
- Q11: Where to modify code safely?
- Q12: Where to write tests?
- Q13: Where to prototype features?
- Q14: Where to store tools?
- Q15: Decision tree for directories?

#### Category 4: Rule Compliance (15 points)
Test rule understanding:
- Q16: Core directives to NEVER violate?
- Q17: Commit rules?
- Q18: Dependency rules?
- Q19: Test modification rules?
- Q20: README modification rules?

#### Category 5: Tool Usage (10 points)
Test tool proficiency:
- Q21: KB query command?
- Q22: KB search command?
- Q23: KB add entry command?
- Q24: Token audit command?
- Q25: Health check command?

### Scoring System

#### Confidence Levels
- **1.0**: Certain - Core knowledge, verified
- **0.95-0.99**: Very confident - Used successfully
- **0.80-0.94**: Confident - Tested, works well
- **0.60-0.79**: Somewhat confident - Observed
- **<0.60**: Uncertain - Speculative

#### Scoring Criteria
- **Correct Answer**: +1 point
- **Partial Answer**: +0.5 points
- **Incorrect Answer**: +0 points
- **KB Used**: Bonus +0.2 points
- **Specific Citation**: Bonus +0.1 points

#### Performance Tiers
- **Expert** (97-100%): 48-50 points
- **Proficient** (89-96%): 45-47 points
- **Competent** (78-86%): 39-44 points
- **Needs Improvement** (<78%): <39 points

## Testing Workflow

### Step 1: Load Skill
```bash
skill meta-test-capability
```

### Step 2: Prepare Test Environment
```bash
# Ensure KB populated
meta kb stats

# Clear test artifacts
rm -rf .meta/test_results/

# Create test directory
mkdir -p .meta/test_results/
```

### Step 3: Execute Test
1. Present questions from all categories
2. Record responses
3. Score each response
4. Note KB usage
5. Track confidence

### Step 4: Generate Report
```markdown
# Capability Test Report
Date: YYYY-MM-DD
Agent: [Agent name]
Duration: X minutes

## Summary
- Total Score: XX/50 (XX%)
- Performance Tier: [Tier]
- Time Taken: X minutes

## Category Breakdown
| Category | Score | Max | % | Status |
|----------|-------|-----|---|--------|
| KB Retrieval | X | 15 | X% | ✅/⚠️/❌ |
| Workflow Execution | X | 12 | X% | ✅/⚠️/❌ |
| Directory Navigation | X | 10 | X% | ✅/⚠️/❌ |
| Rule Compliance | X | 8 | X% | ✅/⚠️/❌ |
| Tool Usage | X | 5 | X% | ✅/⚠️/❌ |

## Detailed Results
### Category 1: KB Retrieval
- Q1: ✅ Correct (+1.0)
- Q2: ✅ Correct (+1.0, KB used +0.2)
- Q3: ⚠️ Partial (+0.5)
- Q4: ✅ Correct (+1.0)
- Q5: ❌ Incorrect (+0.0)

[Continue for all categories...]

## Knowledge Gaps
1. [Gap 1]
2. [Gap 2]
3. [Gap 3]

## Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

## Next Steps
- [ ] Review incorrect answers
- [ ] Update KB if gaps found
- [ ] Retest after improvements
```

### Step 5: Follow-up Actions
Based on results:
- **Expert**: Deploy for production
- **Proficient**: Minor review needed
- **Competent**: Additional training required
- **Needs Improvement**: Comprehensive retraining

## Templates

### Test Question Template
```markdown
## Question [N]: [Question Text]

**Category**: [Category Name]
**Points**: 1.0
**KB Required**: Yes/No

### Expected Answer
[Key points for correct answer]

### Scoring
- **Full points**: All key points present
- **Partial**: Some key points
- **None**: Missing or incorrect

### Related KB Entries
- [PAT-XXXX]: [Entry name]
- [PAT-YYYY]: [Entry name]
```

### Capability Report Template
```markdown
# Capability Assessment Report
Date: YYYY-MM-DD
Agent: [Agent name]
Assessor: [Assessor name]

## Executive Summary
**Overall Score**: XX/50 (XX%)
**Performance Tier**: [Tier]
**Status**: [Ready for production / Needs improvement]

## Detailed Scores
[Category breakdown with charts]

## Strengths
1. [Strength 1]
2. [Strength 2]
3. [Strength 3]

## Weaknesses
1. [Weakness 1]
2. [Weakness 2]
3. [Weakness 3]

## Recommendations
### Immediate
1. [Action 1]
2. [Action 2]

### Short-term
1. [Action 3]
2. [Action 4]

### Long-term
1. [Action 5]

## Deployment Readiness
- [ ] Ready for production
- [ ] Ready with supervision
- [ ] Needs additional training
- [ ] Not ready

## Next Assessment
Date: YYYY-MM-DD
Focus: [Areas to improve]
```

## Best Practices

### Test Administration
1. Consistent environment
2. Clear instructions
3. Unbiased scoring
4. Document anomalies
5. Regular reassessment

### Question Design
1. Cover all categories
2. Vary difficulty
3. Include practical scenarios
4. Test KB retrieval
5. Validate with examples

### Scoring
1. Objective criteria
2. Consistent application
3. Document rationale
4. Allow for partial credit
5. Track trends

### Follow-up
1. Immediate feedback
2. Actionable recommendations
3. Schedule retesting
4. Track improvement
5. Update training

## Common Issues & Solutions

| Issue | Solution | Prevention |
|-------|----------|------------|
| Low KB scores | Re-populate KB | Regular KB updates |
| Workflow confusion | Clarify workflows | Better documentation |
| Directory errors | Decision trees | Clear navigation |
| Rule violations | Reinforce rules | Regular reminders |
| Tool misuse | Training | Practice sessions |

## Integration

### With Other Skills
- `meta-harness-reflection`: Reflection testing
- `meta-populate-kb`: Update KB based on gaps
- `meta-health-check`: Overall health

### With Tools
- `kb.py`: KB queries
- `read`: Read test files
- `edit`: Update test results
- `glob`: Find test files

## Resources

- **Templates**: Test question and report templates
- **Questions**: Standardized question bank
- **Scoring**: Objective scoring criteria

## Version History

- **1.0.0** (2026-05-02): Initial version with comprehensive capability testing framework, scoring system, templates, and best practices

---

**Maintained by**: agentx
**Test Frequency**: Monthly or after major changes
**Target**: Proficient or higher (89%+)
