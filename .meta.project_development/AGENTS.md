# AGENTS.md

## Purpose
Central entry point for Agent‑X system. Guides agent navigation, usage, and safeguards.

## Core Features
- **Safe sandbox** – ` .meta.sandbox/` for experimental changes.
- **Testing ground** – ` .meta.tests_sandbox/` for TDD.
- **Experimentation space** – ` .meta.experiments/` for prototypes.
- **Tool expansion** – ` .meta.development_tools/` for custom tools.
- **Rule repository** – ` .meta.project_development/` for standards, workflows, and meta‑directives.

## Decision Tree
```
Need to...
├─ Modify code? → .meta.sandbox/
├─ Write tests? → .meta.tests_sandbox/
├─ Prototype? → .meta.experiments/
└─ Add tools? → .meta.development_tools/
```

## Core Directives
| Directive | Actions |
|-----------|---------|
| Never commit to production | Never push without approval |
| Never add dependencies | Use existing toolset |
| Never modify `.env` | Preserve secrets |
| Always review `git log` | Before any change |
| Never modify `tests/` | Use sandbox for tests |
| Use `uv` & `pyproject.toml` | Manage deps |

## Quick Start
```bash
# Work in sandbox
cd .meta.sandbox
# Run a session
python3 session.py
```
