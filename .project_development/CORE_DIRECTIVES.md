# Core Directives - Agent-X

> **Purpose**: Non-negotiable rules the system agent must follow at all times.
> **Last Updated**: April 4, 2026

---

## Rules

| # | Directive                       | Details                                                       |
|---|---------------------------------|---------------------------------------------------------------|
| 1 | **NEVER add new dependencies**  | Use existing ones. Explicit approval required for exceptions. |
| 2 | **NEVER modify `.env`**         | Or any file likely to contain secrets.                        |
| 3 | **ALWAYS check `git log`**      | Before making any changes.                                    |
| 4 | **NEVER commit or push**        | Despite the user ask you, never commit or push.               |
| 5 | **NEVER modify `tests/`**       | Use `tests_sandbox/` for new tests (requires approval).       |
| 6 | **Use `uv` & `pyproject.toml`** | For all dependency management. Avoid pin drift.               |
