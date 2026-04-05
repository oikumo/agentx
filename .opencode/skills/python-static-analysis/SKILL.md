---
name: python-static-analysis
description: >
  Run static analysis on Python code to catch bugs, style issues, and type errors — before the
  code ever runs. Use this skill whenever the user wants to lint or check Python files, find
  bugs or code smells, review code quality, enforce PEP 8 or type safety, or get a code health
  report. Trigger on phrases like "analyze my Python", "check this code", "lint this",
  "find bugs in", "review my script", "type check", or any time a .py file is uploaded and
  the user wants feedback on it.
---

# Python Static Analysis

Three complementary tools, run ephemerally via `uv run --with` — no project, no installs, no files written.

| Tool       | What it catches                                 |
|------------|-------------------------------------------------|
| **ruff**   | Style, unused imports, complexity, common bugs  |
| **mypy**   | Type errors (uses type hints when present)      |
| **pylint** | Code smells, duplication, overall quality score |

## Run

```bash
uv run --with ruff ruff check <file> --output-format=full 2>&1
uv run --with mypy mypy <file> --ignore-missing-imports 2>&1
uv run --with pylint pylint <file> --output-format=text 2>&1
```

Run all three even if earlier ones fail — each catches different things.

## Report

Don't dump raw output. Write a structured report:

**Summary table** — issues found and score per tool.

**Issues grouped by severity** — Errors (bugs/crashes) → Warnings (code smells) → Style/Convention. For each: location, which tool flagged it, plain-English explanation, suggested fix.

**Top 3–5 recommendations** — prioritized, actionable.

## Notes

- No type hints → skip mypy or note results will be limited
- Large files (500+ lines) → add `--disable=C` to pylint to cut convention noise
- Ruff can auto-fix many issues: `uv run --with ruff ruff check <file> --fix`
- Offer to apply fixes and return a corrected file if the user wants