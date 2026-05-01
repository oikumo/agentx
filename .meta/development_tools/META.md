# Development Tools - Agent X

> **Purpose**: Development tools and scripts
> **Target**: AI agents (opencode)
> **Rule**: Tools must be tested and documented

---

## Purpose

Safe space for:
- Creating development scripts
- Testing tool functionality
- Automating repetitive tasks
- Building helper utilities

---

## Structure

```
.meta/development_tools/
├── META.md # This file
├── scripts/ # Development scripts
├── tools/ # Helper tools
└── docs/ # Tool documentation
```

---

## Rules

**DO**: Document tools, test thoroughly, keep organized, version scripts
**DON'T**: Modify production without testing, leave undocumented tools

---

## Tool Lifecycle

```
1. CREATE: Build in .meta/sandbox/
2. TEST: Validate functionality
3. DOCUMENT: Add usage guide
4. INTEGRATE: Move to development_tools/
5. MAINTAIN: Update as needed
```

---

## References

- Workflow: [WORKFLOWS.md](../project_development/WORKFLOWS.md)
- Sandbox: [.meta/sandbox/META.md](../sandbox/META.md)

---

**Version**: 2.0.0 (lazy-optimized) | **Lines**: 40
