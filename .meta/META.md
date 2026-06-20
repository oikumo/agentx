# .meta Directory

> **Purpose**: Safe spaces for experiments, tools, and project planning

---

## Structure

| Directory | Purpose |
|-----------|---------|
| `experiments/` | Test new libraries, prototype features |
| `projects/` | Project plans and design documents |
| `doc/` | Documentation archives and references |

## Rules

- Each subdirectory has its own `META.md`
- Agents read the relevant `META.md` before working in a directory

## MANDATORY: OMT++ Methodology

The **OMT++ Agent Guide** (`.meta/doc/omt_agent_guide.md`) is the architectural standard for ALL code in this project.

**Every agent MUST read it before modifying any source code.** It governs:
- **MVC++** — Three-layer separation (Model, View, Controller)
- **Abstract Partner Pattern** — View↔Controller contract via ABC
- **Command Pattern** — Top-level dispatch
- **Phase Model** — Analysis → Design → Programming → Testing
- **Testing Strategy** — Three-stage unit/integration/system
- **File naming and directory layout**

> Violating these rules = task failure. The guide is self-contained — no cross-references needed.

---

**Version**: 3.2.0 (OMT++ integrated) | **Lines**: ~30
