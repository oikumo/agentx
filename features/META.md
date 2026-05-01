# Features - AgentX

> **Purpose**: Organize and track AgentX features by development state
> **Target**: AI agents and developers
> **Mandatory**: Read before modifying feature folders

---

## 1. What is the Features Folder?

The `features/` folder organizes AgentX features by their development state:

- **`planned/`** - Features that are planned but not yet started
- **`wip/`** - Features currently in development (Work In Progress)
- **`ok/`** - Completed and tested features ready for use

This structure provides:
- **Clear visibility** - See at a glance what's being worked on
- **State tracking** - Features move through states as they develop
- **Safe organization** - Separate active work from completed features
- **Documentation** - Each feature has its own documentation

---

## 2. Feature States

### 2.1 Planned (`planned/`)
Features that are:
- Documented and approved
- Not yet started
- Ready for development

**When to use**: Add feature proposals here before starting work

### 2.2 Work In Progress (`wip/`)
Features that are:
- Actively being developed
- Not yet complete
- May be unstable

**When to use**: Move features here when development starts

### 2.3 OK (`ok/`)
Features that are:
- Complete and tested
- Ready for production use
- Fully documented

**When to use**: Move features here when development is complete and tests pass

---

## 3. Feature Lifecycle

```
planned/ → wip/ → ok/
   ↓       ↓      ↓
   └──→ cancelled/ (if abandoned)
```

**State Transitions**:
1. **planned → wip**: Start development (update WORK.md)
2. **wip → ok**: Complete and test (update WORK.md)
3. **wip → planned**: Pause development (document why)
4. **any → cancelled**: Feature abandoned (keep for reference)

---

## 4. Feature Documentation Format

Each feature should have a `.md` file with:

```markdown
# Feature: {Feature Name}

**State**: planned | wip | ok
**Created**: YYYY-MM-DD
**Updated**: YYYY-MM-DD
**Author**: {agent/developer name}

## Description
What this feature does

## Goals
- [ ] Goal 1
- [ ] Goal 2

## Implementation Plan
Steps to implement

## Progress
Current status

## Testing
How to test

## Dependencies
Related features or requirements

## Notes
Additional context
```

---

## 5. Workflow

### Adding a New Feature

1. **Create feature file** in `planned/` with description
2. **Document goals** and implementation plan
3. **Wait for approval** (if required)
4. **Move to `wip/`** when starting development
5. **Update WORK.md** with current task
6. **Move to `ok/`** when complete and tested

### During Development

1. **Work in `wip/`** folder
2. **Update progress** in feature file
3. **Test frequently** in `.meta/tests_sandbox/`
4. **Document changes** as you go

### Completing a Feature

1. **Ensure all tests pass**
2. **Complete documentation**
3. **Move to `ok/`** folder
4. **Update WORK.md**
5. **Log in `.meta/LOG.md`** (if structural change)

---

## 6. Quality Gates

Before moving feature to `ok/`:

- [ ] All goals completed
- [ ] Tests passing
- [ ] Documentation complete
- [ ] No secrets exposed
- [ ] Follows project standards
- [ ] WORK.md updated
- [ ] Feature file updated with final state

---

## 7. Examples

### Example: Petri Net Session Management

**Location**: `features/wip/petri-net-session-management.md`

This feature manages session state using Petri Nets. It's currently in development.

**State**: wip
**Goals**:
- [x] Define Petri Net structure
- [x] Implement state transitions
- [ ] Complete visualization
- [ ] Add error handling

---

## 8. Rules

**DO**:
- Keep feature files updated
- Move features between states as they progress
- Document progress and decisions
- Test before marking as ok

**DON'T**:
- Skip the planned state
- Mark as ok without testing
- Remove old feature files (keep history)
- Work directly in production code

---

## 9. Integration with META Harness

The features folder works with:

- **WORK.md** - Track current feature being developed
- **`.meta/sandbox/`** - Safe space for feature development
- **`.meta/tests_sandbox/`** - Test feature functionality
- **`.meta/LOG.md`** - Log structural changes
- **`.meta/knowledge_base/`** - Store feature knowledge

---

## 10. Maintenance

**Regular**:
- Review `wip/` features for completion
- Archive old `planned/` features if no longer relevant
- Ensure `ok/` features are properly documented

**Per Session**:
- Update WORK.md with current feature
- Move features between states as needed

---

**Version**: 1.0.0 | **Created**: 2026-05-01
**Maintained By**: AgentX AI Agent
