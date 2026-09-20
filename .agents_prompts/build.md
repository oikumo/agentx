# Build Agent

**SESSION STARTUP (First Prompt Only):**
Read `WORK.compiled.md` (11-line startup header; full detail in `WORK.md` on demand) + 1x `omt_net` probe at session start; render `GLOBAL` (probe runs `max_states=0` startup brief: observation+menu+freshness only; <=8 lines: net observation/rev, Pool p/a/d, Lanes, Projects active/complete/draft, drift counts, STALE if `WORK.compiled.md` NEXT != probe next) + `TASKS` menu (NEXT/Other/Blocked/Resources order) as letter-shortcut list (A/B/C... mapped 1:1 to stable `Options:` IDs, no invented IDs in TASKS, D19; user replies with single letter, never question-tool) + `SUGGESTED NEXT` (advisory D19-exempt <=5 lines: drift-priority unlinked > aging > iter-log + pool state + <=2 IDEA: items, never auto-applied). Rest on demand via `omt_nav` (op=nav|list_sections|cross_ref|quick_ref).

**Before answering ANY question about the project** (classes, components, features, architecture, codebase structure, workflows, etc.), you MUST follow the software development process defined for the project
