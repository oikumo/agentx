# Meta Tests Automated - Agent X

> **Purpose**: Dedicated space for automated agent reflection tests and test execution frameworks
> **Target**: AI agents running automated test suites
> **Mandatory**: Read before running automated tests

---

## 1. What is `.meta.tests_automated/`?

A specialized directory for **automated agent testing frameworks** that run reflection tests and capability assessments without manual intervention.

**Key characteristics**:
- **Automated execution**: Tests run without human intervention
- **Reflection-focused**: Tests agent knowledge of META HARNESS
- **Scheduled runs**: Can be triggered on schedule or on-demand
- **Results storage**: Test results stored in `.meta/reflection/`
- **Knowledge-based**: Tests derived from KB entries

---

## 2. Directory Structure

```
.meta.tests_automated/
├── META.md                 # This file
├── knowledge_base/         # Test-specific KB snapshots
├── scripts/                # Test execution scripts
├── configs/                # Test configuration files
└── results/                # Latest test results (symlink to .meta/reflection/)
```

---

## 3. When to Use

**Use `.meta.tests_automated/` when**:
- Running scheduled capability assessments
- Executing reflection test suites
- Validating agent knowledge after KB updates
- Testing agent behavior changes
- Running CI/CD style agent tests

**Do NOT use for**:
- Manual testing (use `.meta/tests_sandbox/`)
- Unit tests (use `tests/unit/`)
- TDD workflow (use `.meta/tests_sandbox/`)
- Feature tests (use `features/*/tests/`)

---

## 4. Workflow

### Running Automated Tests

```bash
# Run reflection test suite
uv run python .meta.tests_automated/scripts/run_reflection.py

# Run with specific config
uv run python .meta.tests_automated/scripts/run_reflection.py --config config_monthly.json

# View latest results
cat .meta/reflection/latest_reflection_log.md
```

### Test Execution Flow

1. **Setup**: Load KB snapshot
2. **Execute**: Run test suite
3. **Capture**: Record responses
4. **Score**: Calculate performance metrics
5. **Log**: Store results in `.meta/reflection/`
6. **Report**: Generate summary

---

## 5. Test Types

### 5.1 Reflection Tests
- **Purpose**: Assess agent knowledge of META HARNESS
- **Questions**: 36 structured questions
- **Scoring**: Performance tier (Expert/Proficient/Competent/Needs Improvement)
- **Frequency**: Monthly or after KB updates

### 5.2 Workflow Tests
- **Purpose**: Validate agent follows correct workflows
- **Focus**: Decision tree adherence
- **Validation**: Directory usage, quality gates

### 5.3 Knowledge Tests
- **Purpose**: Verify KB comprehension
- **Format**: RAG query accuracy
- **Metrics**: Response accuracy, confidence scores

---

## 6. Configuration

### Example Config (config_monthly.json)
```json
{
  "test_name": "monthly_reflection",
  "schedule": "0 0 1 * *",
  "questions": 36,
  "passing_score": 89,
  "output_dir": ".meta/reflection/",
  "notify_on_failure": true
}
```

---

## 7. Results Interpretation

| Tier | Score Range | Action |
|------|-------------|--------|
| Expert | 97-100% | Comprehensive understanding, ready for complex tasks |
| Proficient | 89-96% | Strong grasp, minor review needed |
| Competent | 78-86% | Adequate, review incorrect answers |
| Needs Improvement | <78% | Significant gaps, re-study required |

---

## 8. Integration

### With Knowledge Base
- Tests derived from KB entries
- Results stored in `.meta/reflection/`
- Gaps trigger KB updates

### With Workflows
- Validates workflow adherence
- Ensures quality gate compliance
- Tracks improvement over time

### With Development Tools
- Scripts in `.meta/development_tools/`
- Results feed into capability assessments
- Automated reporting

---

## 9. Maintenance

**After each test run**:
1. Review incorrect answers
2. Update KB if gaps found
3. Archive old results
4. Update test questions if needed

**Monthly**:
- Run full reflection test
- Review test effectiveness
- Prune old results (>3 months)

---

## 10. Related Directories

| Directory | Relationship |
|-----------|-------------|
| `.meta/reflection/` | Test results storage |
| `.meta/knowledge_base/` | Test source material |
| `.meta/development_tools/` | Test scripts |
| `test_automated/` | Legacy automated tests (deprecated) |

---

## 11. Quality Gates

Before marking test complete:
- [ ] KB queried first
- [ ] Correct config used
- [ ] Results stored in `.meta/reflection/`
- [ ] Gaps documented
- [ ] Follow-up actions identified

---

**Version**: 1.0.0 | **Created**: 2026-05-02 | **Status**: New
