# AGENTS.md - Agent-X System Agent Rules

* Primary entry point for the system agent opencode. Defines rules, commands, and navigation paths.
* You, the opencode coding agent must use the `Meta Project Harness` to execute any task.
* The `Meta Project Harness` structure is optimized for opencode agent programming tasks and to produce code quality optimal code.
* Each `Meta Project Harness` directory have a META.md file that must be read first to understand it purpose.
* The `Meta Project Harness` directories name allways start with ´.´ (dot) character.

## Master Documentation

**READ FIRST**: See `META_HARNESS.md` for comprehensive Meta Project Harness documentation.

## Project Meta Directories

| Directory | Purpose | META.md |
|-----------|---------|---------|
| `.project_development/` | Development basis and rules | `.project_development/META.md` |
| `.experiments/` | Experimental workspace | `.experiments/META.md` |
| `.sandbox/` | Safe modification space | `.sandbox/META.md` |
| `.tests_sandbox/` | TDD workspace (Kent Beck) | `.tests_sandbox/META.md` |
| `.development_tools/` | Development utilities | `.development_tools/META.md` |

---

## Core Directives

Non-negotiable rules the system agent must follow at all times.

| # | Directive | Details |
|---|---------------------------------|---------------------------------------------------------------|
| 1 | **NEVER commit or push** | Despite the user ask you, never commit or push. |
| 2 | **NEVER add new dependencies** | Use existing ones. Explicit approval required for exceptions. |
| 3 | **NEVER modify `.env`** | Or any file likely to contain secrets. |
| 4 | **ALWAYS check `git log`** | Before making any changes. |
| 5 | **NEVER modify `tests/`** | Use `.tests_sandbox/` for new tests (requires approval). |
| 6 | **Use `uv` & `pyproject.toml`** | For all dependency management. Avoid pin drift. |

---

## Quick Start Workflow

1. **Read** relevant META.md files
2. **Identify** correct directory for your task
3. **Plan** your approach
4. **Execute** in safe space (sandbox/experiment)
5. **Test** using TDD in `.tests_sandbox/`
6. **Document** your changes
7. **Report** to user

## Quick Reference

| Category | File | Description |
|----------|------|-------------|
| Master Guide | `META_HARNESS.md` | Complete harness documentation |
| Development | `.project_development/META.md` | Development rules and standards |
| Experiments | `.experiments/META.md` | Experimental workspace guide |
| Sandbox | `.sandbox/META.md` | Safe modification space |
| Testing | `.tests_sandbox/META.md` | TDD strategy and workflow |
| Tools | `.development_tools/META.md` | Development tools documentation |
| Project | `README.md` | Project overview and commands |

---

## Core Directives

Non-negotiable rules the system agent must follow at all times.

| # | Directive                       | Details                                                       |
|---|---------------------------------|---------------------------------------------------------------|
| 1 | **NEVER commit or push**        | Despite the user ask you, never commit or push.               |
| 2 | **NEVER add new dependencies**  | Use existing ones. Explicit approval required for exceptions. |
| 3 | **NEVER modify `.env`**         | Or any file likely to contain secrets.                        |
| 4 | **ALWAYS check `git log`**      | Before making any changes.                                    |
| 5 | **NEVER modify `tests/`**       | Use `tests_sandbox/` for new tests (requires approval).       |
| 6 | **Use `uv` & `pyproject.toml`** | For all dependency management. Avoid pin drift.               |

---