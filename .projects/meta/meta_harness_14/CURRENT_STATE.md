# CURRENT_STATE: meta_harness_14

> Session-by-session log + resume point. Companion to `PROJECT.md` (canonical).
> Newest entry on top. One `## <date>` block per session.

---

## 2026-09-27 (fix shipped — feature_136 transport hardening; collect path de-risked)

### Done

- **feature_136.json_arg_object_coercion_transport_hardening** spawned (bug_fix, linked to this project) + shipped + `omt_complete` verified.
- Root cause pinned (not opencode core, not omt_session logic): the opencode SDK coerces JSON-object-looking strings fed to `tool.schema.string()` args into actual JS **objects** (feature_027 had diagnosed only the **array** half); the old per-site guard `Array.isArray(v) ? JSON.stringify(v) : String(v)` let objects fall to `String(v)` → `"[object Object]"` → `session_inspect json.loads` char-1 failure. Repros from the resume entry confirmed by signature (`[object Object]` parses exactly to `Expecting value: line 1 column 2 (char 1)`).
- Fix = single shared serializer `argvValue()` in `.opencode/lib/omt_shared.ts` (`v !== null && typeof v === "object" → JSON.stringify`, scalars pass through) applied at all 4 argv/flag push sites: **omt_session.ts** (query_json/manifest/selection_json — the run001 collect path), **omt_net.ts** (splice/synthesize/mine mutation), **tdd_hats.ts** (behaviors), **reason_check.ts** (concretize row; was unguarded even for arrays).
- New TA: gotcha at the helper (supersedes tdd_hats.ts:48 array-only note); class-level doc now single-sourced.
- Tests: new cross-source pin `tests/scripts/omt/test_argv_value_guard_pins.py` (helper + object guard + 4-site import/call pins + stale-ternary ban, TA:-prose-stripped); canary-logged tests skip. **11/11 pins green, full `tests/scripts/omt/` 743 passed, harnessc check OK (277 records, 0 errors)**, batch-boundary e2e receipt written, and **runtime proof via bun**: `argvValue({limit:3})` → `{"limit":3}` (the exact trial-breaking shape), all 4 edited modules parse.
- Harness edit batch via `harnessc.py stage` (feature_074 mechanism) — 7 files, single e2e at boundary.

### In progress / Blocked

- Pilot run001: 1/8 trials executed (previous entry); 7 remain — user-launched only (mh13 D7). No token claims (mh13 honest-reporting contract).

### Next

- User launches remaining 7 trials per PROJECT.md §New Session Quick Start. NOTE: the transport fix is **live from the next session on** — plugins load per session start; collect/validate (`manifest`/`selection_json`) is now safe against the object-coercion class.
- At collect: adjudicate rep01 observations (no-startup_table-in-control + case-script deviation) per previous entry.

### Notes / context

- Resume entry point: PROJECT.md §New Session Quick Start → this entry → previous entry's trial observations.

---

## 2026-09-27 (resume — trial rep01 executed in-session; tool-call JSON-arg fragility found)

### Done

- Resumed per PROJECT.md §New Session Quick Start → iter-1 entry.
- **Trial `fresh_session_menu_control_current_agents_start_rep01` (attempt 1) ran in THIS session**: first user message carried the run001 label; control start executed — read WORK.compiled.md header + 1x brief `omt_net` probe (max_states=0) + INTRO/GLOBAL/TASKS/SUGGESTED render.
- Variant surface verified live: `lean_start_swap.py` status → variant=control · `LEAN_START_V1` marker count 0 in build.md · `git status` clean → restore-after-trial already satisfied.
- Collection read-path validated live: `omt_session sessions` + `query` OK with explicit `db`+`directory` (F1 gotcha confirmed); bare `sessions` over full corpus hits budget cap (20/1733) → narrow with `time_from` or cursor.

### Trial observations (adjudicate at collect)

1. **No `startup_table` call in this control trial** — menu rendered directly in the agent reply (2 roundtrips: read + probe). Pinned control text is render-agnostic, so this is within control behavior space, but it is identical to lean_start_v1's mandated rendering → shrinks measured contrast (conservative bias toward keep-control). Manifest pins only lean trials (`startup_table_calls: 0`); no control-arm pin exists. Options: record as covariate / add control-side startup_table mandate / relaunch rep01.
2. **Case-script deviation**: `fresh_session_menu` expects the user to reply a letter after the menu; user replied "resume project meta harness 14" (session double-books as trial + project resume). Start-cost portion (label → menu render) is valid; the first-5-assistant-messages window includes resume work, not letter-pick handling. Consider treating attempt 1 as exploratory + rerunning a clean rep01.

### Found: tool-call JSON-string-arg fragility (collect-step risk; no code change yet)

- Inline JSON string args proved unreliable in this session's tool-call transport: query_json `{"limit": 3}` twice → `query_invalid: Expecting value: line 1 column 2 (char 1)` (value arrives quote-stripped/lossy-stringified); Write content `{"limit": 3}` → SchemaError "Expected string, got object" (typed validation caught it cleanly). A third identical emission parsed fine (`cursor.query` intact) → root cause is fragile quoting at the agent-emission layer, NOT omt_session logic.
- Risk: `experiment collect/validate` passes `manifest`/`selection_json` through the same string-arg path → same failure mode could surface at collect time, after all 8 trials are burned.
- Mitigations proven: emit such args as properly escaped JSON strings (worked); fallback path-based manifest passing. Possible harness-side hardening follow-up (omt_session silently lossy-stringified where Write's typed validation failed loudly).

### In progress / Blocked

- Pilot run001: 1/8 trials executed (this session); 7 remain — user-launched only (mh13 D7). No token claims (mh13 honest-reporting contract).

### Next

- User launches remaining 7 trials per PROJECT.md §New Session Quick Start (per-trial: swap to variant → fresh session whose first message is the matching label line → letter reply for fresh_menu trials / pick NEXT for known_task_resume → `--variant control` restore).
- Decide rep01 disposition (observations 1–2) before/at collect.
- After 8 trials: `omt_session experiment collect/validate` (explicit db+directory) → `compare` → decide per manifest rule (≥30% cumulative input-token cut AND identical OptionID map AND zero gate regressions).

### Notes / context

- Resume entry point: PROJECT.md §New Session Quick Start → this entry → §Next.


## 2026-09-27 (auto — feature_135.lean_start_v1_variant Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_135.lean_start_v1_variant/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-27 (iter 1 — lean_start_v1 variant mechanism shipped)

### Done

- Feature **feature_135.lean_start_v1_variant** spawned + linked (project draft→active); `omt_phase` Programming (minor_feature).
- Swap mechanism implemented: **`scripts/omt/lean_start_swap.py`** — reversible single-surface config-swap on the SESSION STARTUP line of `.agents_prompts/build.md` (variants: `control` byte-pinned | `lean_start_v1` = control + `LEAN_START_V1` marker + direct-render clause forbidding the `startup_table` roundtrip). `.meta/META_HARNESS.omt` + `AGENTS.md` byte-identical across variants (AGENTS.md budget headroom only 73 B → OMT-swap would bust `@budget agents_md`; AGENTS.md "Show" is render-agnostic so no conflict).
- 5 unit tests green (`tests/features/feature_135.lean_start_v1_variant/`): pinned-control drift guard, single-factor delta proof (strip-variant == control), byte-identical roundtrip, idempotence, unknown-content refusal (exit 2, no write).
- Live roundtrip proven on the real repo: control → lean (`harnessc check` OK, projections untouched) → control → `git diff` clean on all three surfaces.
- run001 persisted: `.projects/meta/meta_harness_14/run001_manifest.json` (canonical; 2 cases × 2 variants × 2 reps = 8 trials, decision rule locked) + `run001_labels.jsonl` (8 rendered `[mh13.experiment]` first-message label lines).

### In progress / Blocked

- Pilot not launched (mh13 D7: human-launched only). No token claims yet (mh13 honest-reporting contract).

### Next

- User launches the 8 trials: for each trial — `uv run scripts/omt/lean_start_swap.py --variant control|lean_start_v1` to match the trial's variant → start a fresh opencode session whose first user message is the matching label line from `run001_labels.jsonl` (+ a reply letter for `known_task_resume` trials) → `--variant control` restore. Collect via `omt_session experiment collect/validate` (db + explicit directory, F1 gotcha), then `compare` → decide per decision rule.

### Notes / context

- Surface decision recorded as PROJECT.md **D5** (evidence: 73 B budget headroom; `{file:}` include in opencode.jsonc:12 is the actual system-prompt surface).
- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.

## 2026-09-27 (iter 0 — project created)

### Done

- Project home created (`project.py new`, state: draft); `omt_phase` Analysis declared (docs).
- Baseline live analysis via `omt_session` (PROJECT.md F1–F4): corpus 1,730 sessions in repo dir (3.3 GB DB); default `directory="/repo"` returns 0 rows — pass explicit db+directory; trace op unbounded (~50 KB/session); startup protocol = 3 tool roundtrips + double menu render.
- Experiment **run001** planned + dry_run validated via `omt_session experiment plan/dry_run`: 2 cases × 2 variants × 2 reps = **8 trials**, human-launched, `[mh13.experiment]` labels in first user message; `executed:false` (no auto-launch, mh13 D7).
- PROJECT.md canonical proposal written (scope, success criteria ≥30% input-token cut, D1–D4).

### In progress / Blocked

- Waiting on user `go` to implement variant `lean_start_v1` and start pilot trials.

### Next

- On user `go`: spawn feature(s) (`new_feature.py … --project meta_harness_14`), implement lean variant (config-swap or experiment plugin), run the 8 labeled trials with user-started sessions, collect + decide.

### Notes / context

- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.
