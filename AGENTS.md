# AGENTS.md - Agent-X System Agent Rules

> **Purpose**: This file is the primary entry point for the system agent. It defines the rules, commands, and navigation paths for interacting with the Agent-X project.
> **Last Updated**: April 4, 2026

---

## 📋 Quick Reference

| Category | Key File / Path | Description |
|----------|-----------------|-------------|
| **Navigation** | `.project_development/PROJECT_NAVIGATION_ROUTES.md` | Project structure & module map |
| **Documentation** | `.project_development/PROJECT_DOCUMENTATION.md` | Detailed module docs |
| **Current Issue** | `.project_development/CURRENT_ISSUE.md` | Active bugs & tasks |
| **Roadmap** | `.project_development/PROJECT_ROADMAP.md` | Planned features |
| **Testing Rules** | `.project_development/PROJECT_TESTING_SANDBOX_RULES.md` | TDD & testing guidelines |
| **Commands** | `.project_development/USER_COMMAND_EXTENSION.md` | Extended command reference |

---

## 🚨 Core Directives

1. **NEVER add new dependencies** without explicit approval. Use existing ones.
2. **NEVER modify `.env`** or files containing secrets.
3. **ALWAYS check `git log`** before making changes.
4. **NEVER commit** unless explicitly asked.
5. **NEVER modify `tests/`**. Use `tests_sandbox/` for new tests (requires approval).
6. **Use `uv` & `pyproject.toml`** for dependency management.

---

## 🛠️ Tool Usage Guidelines

| Tool | When to Use |
|------|-------------|
| `Glob` | File search (patterns like `**/*.py`) |
| `Grep` | Content search (regex patterns) |
| `Read` | Reading files (avoid `cat`/`head`) |
| `Edit` | Modifying files (preserve indentation) |
| `Write` | Creating new files (only when necessary) |
| `Bash` | Git, uv, pytest, etc. (batch independent commands) |

**Rules**:
- Prefer specialized tools over bash.
- Batch independent bash commands in parallel.
- Use `workdir` instead of `cd`.

---

## 💻 Coding Style

- **Language**: Python 3.14+
- **Line Length**: 88 characters
- **Docstrings**: Google-style for public APIs
- **Naming**:
  - `snake_case` for functions/variables
  - `PascalCase` for classes
  - `UPPER_SNAKE_CASE` for constants
  - `_prefix` for private members
- **Tests**: Mirror source structure in `tests_sandbox/`

---

## 🎮 User Commands

All commands start with `+`. Pipe results using `|`.

| Command | Arguments | Description |
|---------|-----------|-------------|
| `+reload` | - | Refresh context: check last 10 commits & reload this file |
| `+fix` | `{bug info}` | Fix a recent bug. Check git history first. |
| `+issue` | `{issue desc}` | Update `.project_development/CURRENT_ISSUE.md` |
| `+solve` | - | Resolve the current issue (BIG TASK) |
| `+?` | `{question}` | Ask about the project (checks last 50 commits) |
| `+find` | `{module/topic}` | Locate code using Navigation Routes |
| `+update` | - | Update navigation, issues, & docs (BIG TASK) |
| `+list` | - | List all rules in table format |
| `+focus` | `{module/topic}` | Focus attention on a specific area |
| `+tasks` | - | List current & past system tasks |
| `+tree` | - | Show project structure from Navigation Routes |
| `+big` | - | Start a BIG TASK workflow |
| `+` | - | List all available commands |
| `+test` | - | Run tests in `tests_sandbox/` |
| `+tdd` | `{scope}` | Apply TDD for a feature in `tests_sandbox/` |
| `+refactor` | `{file} {strategy}` | AST-based refactoring (requires approval) |
| `+testgen` | `{module_path}` | Generate unit tests in `tests_sandbox/` |
| `+audit` | - | Scan for secrets & security issues |
| `+bench` | `{agent} {input}` | Run performance benchmark |

---

## 📂 Project Navigation

The agent should use `.project_development/PROJECT_NAVIGATION_ROUTES.md` as the primary map for understanding project structure.

- **Entry Point**: `main.py`
- **Core App**: `app/` (REPL, models, security)
- **Agents**: `agents/` (chat, rag, react, graph)
- **LLM Managers**: `llm_managers/` (factory, providers)
- **Tests**: `tests_sandbox/` (feature & integration tests)

---

## 📝 Task Workflow

1. **Understand**: Read relevant files & check git history.
2. **Plan**: Break down into steps. Use `todowrite` for tracking.
3. **Execute**: Implement changes following coding style.
4. **Verify**: Run tests (`+test`) or create sandbox tests.
5. **Report**: Summarize changes & status.

**BIG TASK Protocol**:
- Mark as `[BIG TASK]` in todo list.
- Check in frequently with progress updates.
- Do NOT commit until explicitly approved.

---

## ⚠️ Important Notes

- **Environment**: Linux, Python 3.14+, `uv` package manager.
- **Secrets**: Keep in `.env`. Never commit.
- **Testing**: `tests/` is read-only. Use `tests_sandbox/` for new tests.
- **Communication**: Be concise. Avoid preamble. Answer directly.
