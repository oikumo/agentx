# Reflection - Agent X

> **Purpose**: Test logs & capability assessment
> **Target**: AI agents (opencode)
> **Rule**: Document all reflection tests

---

## Purpose

Safe space for:
- Testing agent capabilities
- Validating META HARNESS compliance
- Running health checks
- Capability assessments

---

## Structure

```
.meta/reflection/
├── META.md # This file
├── README.md # Reflection documentation
├── MANUAL.md # Test manual
└── archive/ # Old test logs
```

---

## Workflows

### Health Check (Monthly)
```
1. Run health check script
2. Review META.md coverage
3. Check token usage
4. Validate workflows
5. Document findings
```

### Capability Test
```
1. Load reflection skill
2. Run structured questions
3. Record answers
4. Assess compliance
5. Archive results
```

---

## Rules

**DO**: Archive old tests, document findings, run monthly, track improvements
**DON'T**: Leave test logs unarchived, skip documentation

---

## References

- Skill: `meta-harness-reflection`
- Workflow: [WORKFLOWS.md](../project_development/WORKFLOWS.md)

---

**Version**: 2.0.0 (lazy-optimized) | **Lines**: 40
