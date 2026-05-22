---
name: meta-project-plan
description: >
  Create structured META project plans in .meta/projects/ directory.
  Use this skill when the user wants to plan a new project, feature, or refactor.
  Trigger on: "create a project plan", "plan out this feature", "design document for",
  "project folder", "META project", or when discussing new initiatives that need planning.
---

# META Project Plan Creation Skill

This skill creates structured project planning folders and markdown files in `.meta/projects/` following AgentX conventions.

## When to Use

- User wants to plan a new feature or project
- Creating design documents for complex implementations
- Refactoring proposals that need approval
- Any initiative requiring structured planning before execution

## Process

### Step 1: Gather Requirements

Ask the user for:
1. **Project name** — short, kebab-case identifier (e.g., `kb-mcp-refactor`)
2. **Project title** — human-readable name
3. **Scope** — what's being built/changed
4. **Status** — planned, in-progress, approved, complete
5. **Owner** — who's responsible
6. **Related WORK.md items** — if any

### Step 2: Create Project Folder

```bash
mkdir -p .meta/projects/<project-name>/
```

### Step 3: Create Project Plan Document

Create `<project-name>/<project-name>.md` or `<project-name>/PLAN.md` with this structure:

```markdown
# {Project Title}

> **Status:** {planned|in-progress|approved|complete}
> **Owner:** {name}
> **Created:** {YYYY-MM-DD}
> **Related WORK.md:** {link or "None"}

---

## 1. Overview

{Brief description of what this project is about}

## 2. Goals

- [ ] Goal 1
- [ ] Goal 2
- [ ] Goal 3

## 3. Scope

### In Scope
- Item 1
- Item 2

### Out of Scope
- Item 1
- Item 2

## 4. Design/Approach

{Technical approach, architecture decisions, key components}

## 5. Implementation Plan

### Phase 1 — {Phase name}
- [ ] Task 1
- [ ] Task 2

### Phase 2 — {Phase name}
- [ ] Task 1

## 6. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Risk 1 | Mitigation 1 |

## 7. Deliverables

- [ ] Deliverable 1
- [ ] Deliverable 2

## 8. Decisions

| Question | Decision |
|----------|----------|
| Decision 1 | Answer |

---

**Version:** 1.0.0
```

### Step 4: Update LOG.md

Log the structural change in `.meta/LOG.md`:

```markdown
## {YYYY-MM-DD}

- **Added**: `.meta/projects/{project-name}/` — {brief description}
```

### Step 5: Update Knowledge Base

Add a KB entry documenting the project plan:

```
Type: pattern
Category: workflow
Title: Project {project-name}
Finding: New project initiated for {scope}
Solution: See .meta/projects/{project-name}/ for full plan
```

## Examples

### Example 1: Simple Feature Plan

```bash
Project: api-rate-limiting
Title: API Rate Limiting Feature
Status: planned
Owner: dev-team
```

Creates: `.meta/projects/api-rate-limiting/api-rate-limiting.md`

### Example 2: Refactor Plan

See: `.meta/projects/kb-mcp-refactor/PLAN.md` (complex refactor with phases)

### Example 3: Completed Feature

See: `.meta/projects/petri-net-session-management/petri-net-session-management.md` (complete status)

## Rules

**DO:**
- Use kebab-case for folder names
- Include status badge at top
- Link to related WORK.md items
- Update when scope changes
- Mark deliverables as checkboxes

**DON'T:**
- Include actual code in plans
- Mix unrelated projects in one folder
- Leave plans outdated (update status)
- Create without user approval

## Output Format

After creation, provide:

```
✅ Created project plan: `.meta/projects/{name}/{name}.md`

**Next steps:**
1. Review and approve the plan structure
2. Add implementation details
3. Update .meta/LOG.md
4. Begin Phase 1 when ready
```

## Related Patterns

- `.meta/META.md` — Parent directory structure
- `.meta/projects/META.md` — Projects directory rules
- `.meta/LOG.md` — Change log for all structural changes
- `WORK.md` — Active work items
