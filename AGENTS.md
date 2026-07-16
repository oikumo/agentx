# AGENTS.md — System Rules (compressed)

> **STARTUP:** Read `WORK.md` → `AGENTS.md` → `.meta/META_HARNESS.md` → `omt_agent_guide.md`
> **RUNTIME:** `uv` only (no bare `python`/`pip`/`pytest`). `src/` edits → `omt_phase` first.

## Enforcement
**ENF:** mechanical via `.opencode/plugin/omt_enforcer.ts` + `opencode.jsonc`  
**REF:** `.meta/META_HARNESS.md` (R1–R3, RIGOR, ERR, WRN, PROT, ESC, EXT, TREE, CMDS)

## NEVER (blocked by gate)
`git commit|push`, `.env*`, deps w/o approval, `tests/` w/o canary, `README.md|uv.lock|LICENSE`, `src/` w/o `omt_phase`

## ALWAYS
`git log/status` → `META.md` per dir → `omt_phase{tt,ph,sc}` → artifacts per §12 → tests pass

## Phase Artifacts (per META_HARNESS.md §12 / guide §12)
| Task Type | Artifact Required |
|-----------|-------------------|
| `bug_fix` `minor_feature` `refactor` `test` | Phase declaration only |
| `major_feature` `new_screen` | Phase + **design doc on disk** (`new_feature.py`) |
| `docs` | None |

## TDD (feature_016)
`major_feature`/`new_screen` in **Programming** → auto-activates:
```
omt_testlist → omt_red → omt_green → omt_refactor → omt_done
```
**Two-hats gate:**
- `RED` state → `tests/` edits only
- `GREEN`/`REFACTOR` state → `src/` edits only (auto-revert if tests break)

## Tools
| Category | Tools |
|----------|-------|
| Phase | `omt_phase`, `omt_skip`, `omt_complete` |
| TDD | `omt_testlist`, `omt_red`, `omt_green`, `omt_refactor`, `omt_done` |
| Lint/Scaffold | `mvc_check.py`, `new_feature.py`, `tdd_check.py` |
| Status | `omt_status` |
| **Navigation** | `omt_nav`, `omt_list_sections`, `omt_cross_ref`, `omt_quick_ref` |

## Navigation Enforcement (feature_020)
**MANDATORY:** Before answering ANY question about the project (classes, components, features, architecture, codebase structure, workflows, etc.), agents MUST:
1. Use `omt_nav` / `omt_list_sections` / `omt_cross_ref` / `omt_quick_ref` to search META HARNESS documentation
2. Only fall back to `grep`/`glob` if navigation tools return no results
3. Cite documentation sections found via navigation tools in responses

**Scope of the mechanical gate:** the gate blocks `grep`/`glob` scoped to **doc paths** (`.meta/`, `AGENTS.md`, `WORK.md`) until a nav tool is used. It does **not** block:
- `read` (targeted file access — e.g. `WORK.md` at startup, or a file the user named)
- searches scoped to `src/` or other non-doc paths (nav indexes docs, not code)

**Escape hatch:** `omt_skip{reason:"...", scope:"nav"}` (logged) bypasses the nav gate for the session.

**Rationale:** Navigation tools provide structured, grep-based retrieval with proper section context and cross-references.

## Quick Reference
- **Declare phase:** `omt_phase{task_type:"bug_fix|minor_feature|major_feature|new_screen|refactor|test|docs", phase:"Analysis|Design|Programming|Testing", scope:"done definition"}`
- **Major/new needs design:** `uv run scripts/omt/new_feature.py "<name>" --type major_feature`
- **Escape hatch:** `omt_skip{reason:"...", scope:"src|tests|nav|all"}` (logged)
- **Complete phase:** `omt_complete{feature:"feature_XXX", advance_to:"Design|Programming|Testing|Done"}`
- **Architecture check:** `uv run scripts/omt/mvc_check.py [path]`