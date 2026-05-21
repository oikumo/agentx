# .meta Structural Change Log

> **Purpose**: Track all structural changes to `.meta/` directory
> **Updated by**: AI agents and developers

---

## 2026-05-21

### META.md Simplification & Consistency Pass

- Updated `.meta/META.md` to v3.1.0 — added missing `projects/` entry
- Populated empty `.meta/projects/META.md` with simplified template (v3.0.0)
- Populated empty `.meta/doc/META.md` with simplified template (v3.0.0)
- Populated empty `.meta/data/META.md` with simplified template (v3.0.0)
- Aligned `.meta/experiments/META.md` to v3.1.0 (added Contents section)
- Created this `LOG.md` (was missing, required by AGENTS.md rule #8)

**Rationale**: Three subdir META.md files were empty; parent index omitted `projects/`. All files now follow the same simplified template: Title → Purpose → Rules (DO/DON'T) → Contents → Version footer.

### AGENTS.md Alignment

- Updated `AGENTS.md` Decision Tree: removed stale `.meta/tools/` entry; added `.meta/projects/` and `.meta/data/` (matches actual `.meta/` layout)
- Added note pointing agents to read each subdir's `META.md` before working there
- Bumped to v4.1.0 (MCP-First + META consistency)

---
