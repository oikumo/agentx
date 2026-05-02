# Projects Tracker

> **Purpose**: Track multiple projects and their status across the AgentX ecosystem
> **Updated by**: Agent (automatically when starting new projects or upon user request)
> **Shown**: When user asks about project status or at session start if relevant
> **Philosophy**: Same as WORK.md - simple reminder, not a detailed task tracker

---

## Active Projects

| ID | Project                                        | Status | Priority | Notes                                                        |
|----|------------------------------------------------|--------|----------|--------------------------------------------------------------|
| 0  | Agentx Systemic Petri Net Software Development | 🟡 Planned | High | agentx software development driven by Petri Net global state |
| 1  | Session Petri Net Module                       | 🟡 Planned | High | Isolate with single interface                                |
| 2  | Goal Integration in Chat Controller            | 🟡 Planned | High | LLM-driven petri net changes                                 |

### Status Legend
- 🟢 **Active**: Currently being worked on
- 🟡 **Planned**: Defined and ready to start
- 🟠 **In Progress**: Actively developing
- 🔴 **Blocked**: Waiting on something
- ⚪ **Backlog**: Future consideration
- ✅ **Completed**: Done

---

## Project Details

### 0. Agentx Systemic Petri Net Software Development

### 1. Session Petri Net Module
**Goal**: Create isolated Python module with single interface
**Current State**: Planned
**Location**: TBD (likely `features/ok/` or `src/`)
**Dependencies**: None
**Next Step**: Define module interface

### 2. Goal Integration in Chat Controller
**Goal**: Integrate goal tracking with chat controller, petri net changes via LLM
**Current State**: Planned
**Location**: Chat controller + petri net integration
**Dependencies**: #1 (Session Petri Net Module)
**Next Step**: Design goal-petri net integration pattern

---

## Completed Projects (Recent)

| ID | Project | Completed | Notes |
|----|---------|-----------|-------|

---

## Guidelines

**When to update**:
- Starting a new project
- Completing a project
- Changing project priorities
- Adding new project ideas to backlog

**What to track**:
- Significant development efforts
- Multi-step features
- Integration work
- Major refactoring

**What NOT to track**:
- Individual small tasks
- Temporary experiments
- Bug fixes (use git issues/PRs)

---

## Relationship to WORK.md

| WORK.md | PROJECTS.md |
|---------|-------------|
| Single current task | Multiple projects |
| Session-level focus | Project-level focus |
| Auto-updated each session | Updated on project changes |
| Quick reminder | Status overview |

**Workflow**:
1. Check `PROJECTS.md` for project status
2. Check `WORK.md` for current session task
3. Work on task that advances a project
4. Update both files as needed

---

> **Note**: This file complements `WORK.md` - use both for effective project tracking
