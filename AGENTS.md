# AGENTS.md — System Rules

> GENERATED from .meta/META_HARNESS.omt — DO NOT EDIT; edit the source, then `uv run scripts/omt/harnessc.py build`.

> **STARTUP:** Read WORK.md + 1x omt_net probe at session start; render GLOBAL (<=8 lines: net observation/rev, Pool p/a/d, Lanes, Projects active/complete/draft, drift counts, STALE if WORK.md NEXT != probe next) + TASKS menu (NEXT/Other/Blocked/Resources order) as question-tool selectable list with stable Options: IDs (no invented IDs in TASKS, D19) + SUGGESTED NEXT (advisory D19-exempt <=5 lines: drift-priority unlinked > aging > iter-log + pool state + <=2 IDEA: items, never auto-applied). Rest on demand via omt_nav.
> **RUNTIME:** `uv` only (no bare `python`/`pip`/`pytest`). `src/` edits → `omt_phase` first.

## Enforcement
**ENF:** mechanical via .opencode/plugins/omt_enforcer.ts + lib/enforcer ×7 + opencode.jsonc; reference = .meta/META_HARNESS.omt (query: omt_nav)

## NEVER (blocked by gate)
- bash deny: `git push *` `git pull *` `git fetch *` `git ls-remote *` `git remote *` `git clone *` `git submodule *` `python *` `python3 *` `pip *` `pip3 *` `pytest *`
- read deny: `*.env` `*.env.*`; toplevel deny: `webfetch`
- protected: `.env` `.env.*` (hard — no override) · `README.md` `uv.lock` `LICENSE` (`omt_skip{scope:"all"}` only)
- edit gates: harness-surface 2nd edit w/o fresh e2e receipt · `tests/` w/o canary approval · net permission denied — fire(work_start) required · `src/` w/o `omt_phase` · TA:-carrying files w/o `omt_think_list` consult · `src/` w/o `omt_kb_nav` KB consult

## ALWAYS
`git status` → `META.md` per dir → `omt_phase` → `omt_complete` → `uv run pytest`

## Process (full rules on demand via nav)
- **§12 artifacts:** `bug_fix` `minor_feature` `refactor` `test` → declaration only · `major_feature` `new_screen` → + design doc on disk (`new_feature.py`) · `docs` → none
- **TDD (feature_016):** `major_feature`/`new_screen` @Programming auto-activates `omt_tdd{op: testlist → red → green → refactor → done}` — two-hats: RED tests/ only · GREEN/REFACTOR src/ only (auto-revert on break)
- **Tools:** 10 `omt_*` — catalog `omt_nav{query:"CMD_", tag_type:"CMD"}` · workflows `omt_quick_ref`
- **Workflows (.workflows/):** .workflows/ operational workflow catalog — triggered procedures the agent loads on demand (markdown recipes, NOT a runtime). Sits ABOVE the harness: each workflow's `# Rules` line 1 declares follow-vs-override OMT. Two-level discovery read: .workflows/META.md → matched subject META → matched file. Mandatory approval gate (no auto-fix). Detail: @doc comp.workflows + .workflows/META.md.
- **Projects home (.projects/):** .projects/ per-feature design & project home — non-gated; PROJECT.md (canonical) + CURRENT_STATE.md (session log); companion to @phase design_doc. Lifecycle CLI: uv run scripts/omt/project.py (new|link|close|sync); manifest .projects/meta/META.md (GENERATED); WORK.md `## Projects` (synced). Detail: @doc comp.projects + .projects/meta/.
- **Nav gate (feature_020):** nav tools before grep/glob on docs (read + src/non-doc exempt) · **Think gate (feature_021):** TA: files need `omt_think{op:list}` consult (NOT skip-bypassable)
