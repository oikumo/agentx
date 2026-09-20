# IMPROVEMENT_OPTIONS — startup session summary: friendly, informative, selectable + agent-suggested Next

> Workflow: `.workflows/meta_harness/loops/meta_harness_evolution.md` — step 3 proposal (sandbox only, no src/harness edits).
> Trigger: "start session summary do not present easy to select options, make more user friendly and more informative about global state" + "include suggested work next section made by agent based on global state and new ideas".

## 1. Current state (fresh-start analysis, toolbox only, no src search)

**Canonical rule** — `.meta/META_HARNESS.omt:185` `@doc startup tags="STARTUP"`:
> Read `WORK.md` (only) at session start; summarize ≤15 lines (in-progress/blocked/next). Present Tasks menu (NEXT/Other/Blocked/Resources) in order; no invented options (D19). All other docs on demand via `omt_nav`.

**Related machinery:**
- `@inject session_bootstrap on=first_tool_result budget=1536` — ONE emission/session; nav-tip ≤512B + TA digest ≤1024B. Any richer summary must fit this budget or re-budget (F32/F33 sensitive: AGENTS.md 3072, work_md 9728, tool_schemas 1920).
- `@budget work_md max=9728` — WORK.md read every startup; Tasks block is net-generated (`omt_net probe push.tasks_block`: NEXT/Other/Blocked/Resources/Pool/Options/Lanes).
- `feature_110 whole_project_menu_composer` + `feature_111 multi-select` + `feature_112 identity-aware pool` + `feature_113 live progress` — menu already has stable IDs in `Options:` line (proj:*, drift:*, unscoped:*), but startup rule does NOT surface them as selectable; agent renders plain text, user must retype.
- `omt_status` (phase/unlock/artifacts/lint/WORK.md next) + `omt_q state/drift/audit` + `omt_net probe` (marking/observation/menu/claims/lanes/git_plane) — the "global state" already exists machine-readable, but startup deliberately reads WORK.md ONLY, so it hides: pool drained_complete rev60, lanes verification/integration free, drift (aging-draft ×2, iteration-log ×5, unlinked-project-backed ×2 — 17 records), Projects table (3 active / 9 complete / 3 draft), phase/unlock/lint, ledger health.

**Live probe at proposal time (rev 60):** `drained_complete` — pending=0 active=0 done=7, resources 4/4 free, workers 2/2 free, lanes 1/1 free each, NEXT=none (WORK.md still says `proj:agentx_concurrent_development (recommended)` — stale vs net `next:none`). This staleness is exactly why users distrust the current summary.

**Root causes of complaint:**
1. Text-only menu → no `question`-tool selectable IDs (typing `proj:agentx_concurrent_development` is error-prone).
2. WORK.md-only → global state (net/drift/projects/lanes/health) invisible.
3. D19 "no invented options" → agent FORBIDDEN from suggesting anything beyond the Tasks block — directly blocks the requested "suggested work next" feature.

## 2. Constraints (from Improvement strategy rules)

- Token minimization first (future agent consumption); human-readable is secondary — prefer DSL/composer over prose.
- Performance: startup is on the critical path of EVERY session; extra tool calls must be bounded (≤2 probe calls, no full-suite reads).
- Flexibility: rule change in ONE place (`.meta/META_HARNESS.omt` `@doc startup` + optionally `@inject`), regenerate via `harnessc build`, never hand-edit projections.
- No new gate without retiring one (`@budget gates max=12`, 10 now).

## 3. Options

### OPT-A — Minimal: selectable menu + slightly richer summary (no rule-structure change)
- Change `@doc startup` payload only: keep "Read WORK.md (only)" but add "render Options: line as numbered `question`-tool menu with stable IDs; keep ≤15-line summary + add 3-line Global snapshot (Pool/Lanes/Projects-active)".
- Suggested-Next: one advisory line prefixed `SUGGEST (non-binding, D19-exempt):` — e.g. `SUGGEST: link feature_kb_akb (unlinked-project-backed ×10) or close aging drafts` — clearly separated from NEXT so D19 holds.
- Pros: 1-line diff, zero budget change, zero new tool, immediate usability win.
- Cons: still WORK.md-only (drift detail, net observation, lint/phase hidden); suggestion is a single line, no reasoning trace; stale-NEXT problem remains.
- Token cost: ~+3 lines/session (~150B) — fits `session_bootstrap 1536`.

### OPT-B — Structured startup v2 (RECOMMENDED): Global + Menu + Suggested-Next, question-tool selectable ⭐
- Rewrite `@doc startup` to three fixed sections with hard line caps (total ≤25 lines, budget bump `session_bootstrap 1536→2048` — deliberate, compiled):
  ```
  1. GLOBAL (≤8 lines, from WORK.md Projects table + net probe push.tasks_block + omt_q drift count — NO extra reads beyond probe):
     State: drained_complete rev60 | Pool p=0 a=0 d=7 | Lanes verif 1/1 integ 1/1 | Workers 2/2
     Projects: active 3 (studio, lifecycle, rag_v2) | complete 9 | draft 3 (agentx_concurrent, kb_akb, workflows)
     Health: drift 17 (aging 2, iter-log 5, unlinked 2) | NEXT: none (WORK.md says agentx_concurrent — STALE ⚠️)
  2. TASKS (question-tool menu, stable IDs from Options: line, in order NEXT/Other/Blocked/Resources):
     [1] proj:agentx_concurrent_development (recommended) [2] drift:aging-draft:workflows ... — user picks number, agent maps to ID.
  3. SUGGESTED NEXT (agent-generated, ≤5 lines, marked ADVISORY — D19-exempt by construction):
     logic: highest-value = unlinked-project-backed (10× feature_kb_akb link = 1 cmd fix) > aging drafts (28d) > iteration-log sync > unscoped 001/002 scoping.
     e.g. "1. link feature_kb_akb (1 cmd, clears 10 drift) 2. scope unscoped:001/002 3. new ideas: <agent proposes 1 fresh>");
     new-ideas slot: agent MAY propose ≤2 novel items (e.g. "startup composer DSL", "drift auto-fix dry-run") tagged `IDEA:` — never auto-applied.
  ```
- Selectability: agent MUST use `question` tool (or numbered reply contract) for section 2 — no retyping.
- Staleness guard: if `WORK.md NEXT ≠ net probe menu.next`, emit `STALE ⚠️` line (as above) instead of silently recommending.
- Pros: fixes all three root causes; machine-readable (fixed sections, stable IDs); suggestion logic is auditable (drift-class priority); bounded cost (WORK.md + 1× probe + cached drift count).
- Cons: needs budget bump + `harnessc check` update; D19 needs rewording ("no invented options in TASKS; SUGGESTED is advisory-only").
- Token cost: ~+10 lines/session (~600B); pays back by killing 1–2 follow-up `omt_status/omt_q` rounds per session.
- Execution path: edit `.meta/META_HARNESS.omt` `@doc startup` + `@inject session_bootstrap budget` → `harnessc check` → `build` → e2e receipt refresh.

### OPT-C — Full DSL: startup composer (max performance, max work)
- New pure composer (mirrors feature_110 `verify_dispatch`/`report join`): `render_startup(work_md_tasks, probe_menu, drift_summary, projects_table) → {global: DSL, menu: [{id,label}], suggested: [{reason,action}]}` in `scripts/omt/` + thin `@doc startup` pointer ("call composer, render its output").
- Suggested-Next becomes scored: `drift_weight(unlinked=10, aging=5, iter-log=1) + pool_state_bonus + novelty_slot` — deterministic, testable with goldens.
- Pros: lowest per-session tokens (composer output is minimal DSL), fully testable, most flexible for future changes.
- Cons: new code + tests + receipt round-robin (harness surface 2nd-edit guard); 3–5× the work of OPT-B; overkill while pool is drained_complete (no active work to schedule).
- Token cost: session-cheapest, implementation-most-expensive. Defer until OPT-B proves the sections.

## 4. Recommendation

**OPT-B.** It delivers the user's two asks (selectable friendly menu + informative global + agent-suggested Next with new-ideas slot) in a single `@doc startup` rewrite, respects token budgets explicitly, keeps D19's spirit (TASKS stays closed; SUGGESTED is fenced advisory), and leaves OPT-C as a measured follow-up once wild sessions (N≥10 residual from meta_harness_10) validate the sections.

## 5. Approval gate (STOP — do not execute)

Pick one: **OPT-A** (minimal) / **OPT-B** (recommended) / **OPT-C** (DSL) / **defer**. On approval, execution follows the improvement's step 5–6: edit ONLY `.meta/META_HARNESS.omt`, then `uv run scripts/omt/harnessc.py build` (check → build → e2e receipt).

# Result (2026-09-20 — OPT-B executed)

- Approved: OPT-B structured v2 (question-tool pick).
- Patched `.meta/META_HARNESS.omt` in ONE round via `uv run python` (receipt round-robin safe): `@inject session_bootstrap budget 1536→2048`, `@doc startup` → GLOBAL+TASKS(selectable)+SUGGESTED NEXT (D19 fenced), `@budget agents_md max 3072→3584 (+512 deliberate)`.
- `harnessc check` OK (274 records, 0 errors; agents_md 3221/3584), `build` OK (5 projections), harness e2e 1 passed → receipt refreshed.
- AGENTS.md STARTUP line now renders the new 3-section contract. Dogfood demo below in this session.
