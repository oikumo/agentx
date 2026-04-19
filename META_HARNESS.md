# Meta Project Harness - Agent X

> **Purpose**: Master guide for the Meta Project Harness structure optimized for opencode agent programming
> **Target**: AI agents (opencode) working on Agent-X
> **MANDATORY**: Read and understand this before any task

---

## What is the Meta Project Harness?

The Meta Project Harness is a structured project organization system designed specifically for AI-assisted development. It provides:

- **Clear separation** between production, experimentation, and testing
- **Safe spaces** for AI agents to work without affecting production
- **Structured workflows** for consistent, high-quality output
- **Comprehensive documentation** at every level

---

## Core Directives

These rules are **NON-NEGOTIABLE** and must be followed at all times:

| # | Directive | Details |
|---|-----------|---------|
| 1 | **NEVER commit or push** | Despite the user ask you, never commit or push. |
| 2 | **NEVER add new dependencies** | Use existing ones. Explicit approval required for exceptions. |
| 3 | **NEVER modify `.env`** | Or any file likely to contain secrets. |
| 4 | **ALWAYS check `git log`** | Before making any changes. |
| 5 | **NEVER modify `tests/`** | Use `.tests_sandbox/` for new tests (requires approval). |
| 6 | **Use `uv` & `pyproject.toml`** | For all dependency management. Avoid pin drift. |

---

## Directory Structure

```
agent-x/
├── .project_development/    # Development guidelines and helpers
│   ├── META.md              # Development basis and rules
│   ├── CODING_STYLE.md      # Code style guide
│   ├── ENVIRONMENT.md       # Environment setup
│   ├── PROJECT_TASKS.md     # Current tasks
│   ├── ROUTES.md            # Command routes
│   ├── TASK_WORKFLOW.md     # Workflow guide
│   └── TOOL_USAGE.md        # Tool usage
│
├── .experiments/            # Experimental workspace
│   ├── META.md              # Experiment rules
│   └── <dated-experiments>/ # Individual experiments
│
├── .sandbox/                # Safe workspace for modifications
│   ├── META.md              # Sandbox rules
│   ├── .agent/              # Agent configurations
│   ├── .user/               # User configurations
│   └── <sessions>/          # Session workspaces
│
├── .tests_sandbox/          # TDD workspace
│   ├── META.md              # TDD strategy (Kent Beck)
│   ├── features/            # Feature-level tests
│   └── test_<module>.py     # Module tests
│
├── .development_tools/      # Development tools
│   ├── META.md              # Tools documentation
│   ├── mcp/                 # MCP tools
│   └── scripts/             # Utility scripts
│
├── src/                     # Production source code
├── tests/                   # Production tests (read-only)
├── main.py                  # Entry point
└── pyproject.toml           # Project configuration
```

---

## Meta Directory Naming Convention

All Meta Project Harness directories **MUST** start with a dot (`.`):

- `.project_development/` - Development basis
- `.experiments/` - Experimental workspace
- `.sandbox/` - Safe modification space
- `.tests_sandbox/` - TDD workspace
- `.development_tools/` - Development utilities

Each directory **MUST** contain a `META.md` file that explains its purpose and rules.

---

## When to Use Each Directory

### `.project_development/`
Use when you need to:
- Understand project development rules
- Check coding standards
- Review task workflows
- Document development processes

### `.experiments/`
Use when you need to:
- Test a new library or approach
- Prototype a feature
- Validate a hypothesis
- Explore alternatives

**Example**: Testing a new LLM provider integration

### `.sandbox/`
Use when you need to:
- Modify production code safely
- Test code changes
- Work on multi-step tasks
- Keep session-specific work

**Example**: Refactoring a command implementation

### `.tests_sandbox/`
Use when you need to:
- Write new tests (TDD)
- Follow Red-Green-Refactor cycle
- Test new features before production
- Validate bug fixes

**Example**: Adding tests for a new command

### `.development_tools/`
Use when you need to:
- Create or use MCP tools
- Run development scripts
- Automate repetitive tasks
- Debug issues

**Example**: Creating a code generation tool

---

## Standard Workflow

### 1. Understand the Task
```
1.1 Read task requirements
1.2 Check git log for context
1.3 Review relevant META.md files
1.4 Identify which directory to use
```

### 2. Plan the Approach
```
2.1 For new features → .experiments/ or .tests_sandbox/
2.2 For modifications → .sandbox/
2.3 For tests → .tests_sandbox/
2.4 For tools → .development_tools/
```

### 3. Execute in Safe Space
```
3.1 Create session/experiment folder
3.2 Document your plan
3.2 Work incrementally
3.3 Test frequently
3.4 Document findings
```

### 4. Validate
```
4.1 Run all relevant tests
4.2 Verify no production code broken
4.3 Check against requirements
4.4 Document what works
```

### 5. Report
```
5.1 Summarize changes made
5.2 Show test results
5.3 Explain next steps
5.4 Clean up workspace
```

---

## Documentation Standards

### META.md Files
Every Meta directory must have a META.md with:
- Purpose statement
- Target audience
- Mandatory rules
- Structure overview
- Usage guidelines
- Examples

### Session Documentation
When working in sandbox/experiments:
- Create dated folders
- Document purpose and goals
- Record what was tried
- Note successes and failures
- List next steps

### Code Documentation
- Use docstrings for public APIs
- Add inline comments for complex logic
- Follow existing code style
- Keep documentation updated

---

## Quality Gates

Before considering a task complete:

### Code Quality
- [ ] Follows PEP 8 style
- [ ] Type hints included
- [ ] Docstrings present
- [ ] No linting errors

### Testing
- [ ] Tests written in `.tests_sandbox/`
- [ ] All tests pass
- [ ] Edge cases covered
- [ ] TDD cycle followed

### Documentation
- [ ] META.md updated if needed
- [ ] Changes documented
- [ ] README updated if applicable
- [ ] Commit messages clear (if allowed)

### Safety
- [ ] No secrets exposed
- [ ] No production code modified directly
- [ ] Tests validate changes
- [ ] Rollback plan if needed

---

## Common Scenarios

### Scenario 1: Adding a New Feature
```
1. Read .project_development/META.md
2. Create experiment in .experiments/
3. Write tests in .tests_sandbox/
4. Implement in .sandbox/
5. Validate and document
6. Report to user
```

### Scenario 2: Fixing a Bug
```
1. Reproduce bug in .sandbox/
2. Write failing test in .tests_sandbox/
3. Fix bug in .sandbox/
4. Verify test passes
5. Document fix
6. Report to user
```

### Scenario 3: Refactoring Code
```
1. Copy code to .sandbox/
2. Write tests for current behavior
3. Refactor in .sandbox/
4. Verify tests still pass
5. Document improvements
6. Report to user
```

### Scenario 4: Testing New Library
```
1. Create experiment folder
2. Document hypothesis
3. Test in isolation
4. Validate benefits
5. Document findings
6. Recommend integration or not
```

---

## AI Agent Responsibilities

### As an AI Agent, You MUST:
- Always read META.md files first
- Work in appropriate directories
- Follow TDD principles
- Document all changes
- Test thoroughly
- Respect core directives
- Never commit without explicit permission
- Never modify .env or secrets
- Use uv for dependencies
- Check git log before changes

### As an AI Agent, You SHOULD:
- Be proactive about documentation
- Suggest improvements to the harness
- Keep workspaces clean
- Share learnings from experiments
- Follow Kent Beck's TDD principles
- Use incremental approaches
- Validate before proposing

### As an AI Agent, You MUST NOT:
- Modify production code directly
- Skip the testing phase
- Work outside the harness structure
- Ignore META.md guidelines
- Leave messy workspaces
- Commit or push without permission
- Add dependencies without approval

---

## Maintenance

### Regular Tasks
- Clean up old experiments
- Archive completed sandbox sessions
- Update META.md files as needed
- Remove unused tools
- Consolidate learnings

### Housekeeping
- Keep directory structure clean
- Remove temporary files
- Update documentation
- Archive old sessions
- Maintain test coverage

---

## Getting Started Checklist

For any new task:

- [ ] Read AGENTS.md
- [ ] Read relevant META.md files
- [ ] Check git log
- [ ] Identify correct directory
- [ ] Create session/experiment folder
- [ ] Document your plan
- [ ] Follow appropriate workflow
- [ ] Test thoroughly
- [ ] Document results
- [ ] Clean up workspace

---

## Additional Resources

- **AGENTS.md**: Main entry point for system agent rules
- **README.md**: Project overview and commands
- **pyproject.toml**: Project configuration
- **.tests_sandbox/META.md**: TDD strategy
- **.project_development/**: Development guidelines

---

## Version

- **Version**: 1.0.0
- **Last Updated**: 2026-04-19
- **Maintained By**: opencode AI agent

---
