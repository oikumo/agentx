# Tests Sandbox - Agent X

> **Purpose**: TDD workspace (Kent Beck methodology)
> **Target**: AI agents (opencode)
> **Rule**: RED → GREEN → REFACTOR

---

## Core Philosophy

Test-Driven Development in isolation:
- Write failing test first (RED)
- Implement minimum to pass (GREEN)
- Refactor while keeping tests green
- Never modify production `tests/` directly

---

## Structure

```
.meta/tests_sandbox/
├── META.md # This file
├── <date>-<feature>/ # Test sessions
│   ├── test_*.py # Test files
│   └── notes.md # Session notes
└── archive/ # Old tests
```

---

## Workflow (TDD)

```
1. RED: Write failing test in tests_sandbox
2. GREEN: Implement fix in .meta/sandbox/
3. REFACTOR: Clean up while tests pass
4. DOCUMENT: Record pattern in KB
5. PROPOSE: Present for production merge
```

---

## Rules

**DO**: Write tests first, isolate concerns, document patterns, archive old tests
**DON'T**: Modify production tests, skip RED phase, leave orphaned tests

---

## Integration

**Success Path**: Test passes → Document pattern → Move to production → Archive
**Failure Path**: Test fails → Debug in sandbox → Iterate

---

**Version**: 2.0.0 (lazy-optimized) | **Lines**: 50
