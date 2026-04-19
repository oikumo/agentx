# Experiments - Agent X

> **Purpose**: Experimental workspace for testing new features, ideas, and approaches
> **Target**: AI agents (opencode) working on Agent-X
> **MANDATORY**: All experiments should be documented and either integrated or cleaned up

---

## Purpose

The `.experiments/` directory is a sandbox for:
- Testing new libraries or dependencies
- Prototyping features before integration
- Exploring alternative implementations
- Validating hypotheses about code structure or performance

---

## Rules

### DO
- Create dated experiment folders (e.g., `2024-04-19-feature-x/`)
- Document findings in experiment README files
- Clean up or integrate experiments after validation
- Use experiments to validate TDD approaches before `.tests_sandbox/`

### DON'T
- Leave experiments in an broken state
- Mix experimental code with production code
- Forget to document what you learned

---

## Structure

```
.experiments/
├── META.md                    # This file
├── YYYY-MM-DD-experiment/     # Dated experiment folder
│   ├── README.md             # Purpose and findings
│   └── code/                 # Experimental code
```

---

## Lifecycle

1. **Create**: Start with a clear hypothesis or goal
2. **Document**: Write what you're testing and why
3. **Validate**: Test the hypothesis
4. **Decide**: Integrate, iterate, or discard
5. **Clean**: Remove or archive completed experiments

---
