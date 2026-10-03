# CURRENT_STATE: meta_harness_14

> Session-by-session log + resume point. Companion to `PROJECT.md` (canonical).
> Newest entry on top. One `## <date>` block per session.

---

## 2026-09-28 (100 past sessions — baseline closes mh14, no further data per user)

### Done

- Corpus: 100 most recent sessions in repo dir (`ses_f1aa4108…` newest 2026-09-28 → `ses_f448f3421…` oldest ≈8d ago), snapshot 100 sessions / 4791 msgs / 21022 parts via `SessionSelector(session_ids=100)` (explicit DB, read-only).
- Startup proxy = first-2-assistant message-incremental `input` (F2); first-5 also scored; `startup_table` audited in first 20 parts; model from first assistant:
  - Overall f2 (n=88 with ≥2 asst): median **11448**, mean **12102**, min 0, max 61148. f5 median **15528**, mean **19278**.
  - `startup_table` true 27 / false 73 → f2 median **11120** (true) vs **11863** (false). Tool roundtrip is NOT the dominant cost; context dominates.
  - Model: `muse-spark-1.3` 71 (f2 median 11760, mean 12861) vs `z-ai/glm-5.3` 26 (f2 median 1288, mean 8598) + 3 others. glm bimodal (many greetings/trials low + some huge); muse mostly real-work heavy. Model stratification required — confirms today-startup drift entry.
  - Clean menu-like (n_msg≤6, f2<2000): 16 (10 zero-input 2-msg greetings + rep3/rep4 trials 918/936 + `ses_f2013…` 850 with `startup_table` true + 3 more). Trials sit at the extreme low end, ≈10× below typical startup.
  - run001 trials in corpus: rep01 f2 12370 / f5 14857 (62 msgs, contaminated); rep02 f2 954 / f5 1645 with `startup_table`; rep3 f2 918; rep4 f2 936 (both direct-render).
- Interpretation for D1 (evidence-first): the ≈718-token (≈43%) observational saving from skipping `startup_table` in clean menu sessions is real but tiny vs typical session cost (median startup 11.4k, session totals up to 91k, peak message 127k per PROJECT F2). Absolute saving ≈6% of median startup, <1% of long sessions. Productivity enforcement (pool/lanes/staleness via probe + menu) must be preserved — diet cannot trade it for <1k tokens.

### Decision (final with available data — keep control)

- **Keep control, no adoption.** Missing lean-labeled arm + model drift + label collision (prior entries) stand; 100-session baseline adds: even if the ≈43% clean-menu saving generalized, it does not meet a materiality bar for typical sessions (dominated by context/model variance, st_true vs st_false medians differ by only ~743). No token-saving claim. run001 closed-inconclusive at 4/8 + today-startup supplement + 100-session baseline.
- PROJECT.md `run001 pilot collected + decision` box stays unchecked-to-checked as **decided-keep-control** only if owner accepts this 100-session baseline as the collect record; otherwise leave unchecked with pointer to these three 2026-09-28 entries.

### Next

- Optional run002 (only on explicit new direction): pin model per arm, verbatim labels, control `startup_table` mandate vs lean forbid, full 2×2×2 same-model matrix, plus materiality rule (e.g., ≥10% of median session total, not just first-5).
- Resume entry point: PROJECT.md §Scope → 2026-09-28 interim (4-trial) → today-startup drift → this 100-session baseline.

---

## 2026-09-28 (today-startup as data — drift analysis, no further trials per user)

### Done

- Today window (2026-09-28 00:00 UTC → 00:20 UTC, `time_from=1790553600000`): **2 sessions** in repo dir (all-dirs scan same 2, no hidden trials):
  - `ses_f1aa7c29bffeHymxyjmMGDy0HW` — `Fresh session menu control trial start` (rep4, label rep=4 / trial string `…_rep02` collision) — 5 msgs, 3 assistant
  - `ses_f1aa4108cffeMc69wZwJYECMvg` — `Friendly greeting` (this resume session: `hi` → menu → `resume mh14` → `drift` + today-startup analysis) — 46 msgs at read time, 8 assistant
- Startup-as-data (message-incremental `input`, first assistant msgs = startup cost; `read` + `omt_net probe` in both, **no `startup_table` in either** — both lean-like direct render):
  - rep4 trial startup: asst1 **71** + asst2 **865** = **936** first-2-assistant input (first-5-assistant 936; session total 936; output 41+370; reasoning 2441+3576; cache_read 11520+13952; model `nvidia/z-ai/glm-5.3`, variant max)
  - current session startup (`hi` → menu): asst1 **9538** + asst2 **1031** = **10569** first-2-assistant input (first-5-assistant 16579 with resume work; output 146+352; reasoning 42+826; cache_read 2289+11761; model `opencode/muse-spark-1.3-contributor-free`, variant xhigh)
- Drift finding (blocks pooling): **model/provider drift** — identical 2-roundtrip startup path costs 936 vs 10569 input (≈11.3×) across `nvidia/glm-5.3` vs `opencode/muse-spark`. Different tokenizers + cache inclusion + reasoning accounting per mh13 contract → sessions incomparable without per-model stratification. Manifest pins no model; `evaluate.compare` quality/comparability gate therefore fails → `inconclusive` even before the missing lean arm is considered.
- Harness drift checks (`as_of=29e83bf`): `omt_q drift` → 0 drift records (`kb:477, skeleton:0, direction_b_only:true`); `fix_preview{filter:unlinked}` → `preview rev:60 (0 drift records), nothing linkable`. No structural KB/nav drift to exploit for mh14; the operative drift is session-level model drift above.
- OptionID map: both today startups rendered the same 9-option TASKS (A–G + H–I, D19 1:1); zero enforcer/gate regressions in trial parts. Quality holds, comparability does not.

### Decision (no further data per user — run001 closed as inconclusive)

- **Keep control, no adoption, no token-saving claim.** Today-startup data adds N=1 clean trial startup (936) + N=1 model-drifted startup (10569) — both same-arm (direct-render), no `lean_start_v1`-labeled contrast, no `known_task_resume` case. Combined with prior 4-trial interim (1 true-control 1645 vs 2 clean direct-render ~927): the ≈43% observational saving remains a same-arm natural experiment, now further confounded by ≈11× model effect. Formal decision rule (≥30% + identical map + zero regressions, control vs lean) cannot be evaluated → `inconclusive` / keep control.
- run001 status: **closed-inconclusive at 4/8 observed + today-startup supplement, no more trials** per explicit user direction. Manifest unchanged; this entry + prior 2026-09-28 interim entry jointly serve as the collect record (Tier-2 `experiment collect` is a stub; collection via `profile` + `compare_sessions` + `bind_labels` + parts audit, replayable from saved session IDs).

### Next

- If mh14 reopens as run002: (1) pin model/provider per arm (or stratify); (2) use `run001_labels.jsonl` verbatim (fix rep3/rep4 trial-string collision); (3) mandate `startup_table` in control (`startup_table_calls:1` fidelity pin) vs forbid in lean; (4) run full 2×2×2 matrix with same model; then `compare` → decide.
- Resume entry point: PROJECT.md §Scope/decision rule → prior 2026-09-28 interim entry (4-trial numbers) → this entry (today-startup + model drift).

---

## 2026-09-28 (interim — 4 trials observed, stop per user, no new trials, decision: keep control / inconclusive)

### Done

- Located 4 × `fresh_session_menu / control_current_agents_start` sessions in DB (`directory=/home/oikumo/develop/production/agentx`, explicit `db`+`directory`, F1 gotcha honored):
  - `ses_f1af94d22ffesQMTCDggx9IGdV` — rep01 (label rep=1, trial string `…_rep01`, 2026-09-27) — 62 msgs
  - `ses_f1ab50f78ffet5HwNedFGHzBM7` — rep02 (label rep=2, trial string `…_rep02`) — 9 msgs
  - `ses_f1ab1967fffeLy7F4y0w0lpQyH` — rep=3 but trial string `…_rep02` (collision) — 5 msgs
  - `ses_f1aa7c29bffeHymxyjmMGDy0HW` — rep=4 but trial string `…_rep02` (collision) — 5 msgs
- Measured via `omt_session profile` + direct `compare_sessions` (basis `message_incremental`, session cumulative counters preserved separately per mh13 contract):
  - rep01: first-5-assistant input **14857** (11527+843+112+2159+216), session total input **91393** (output 11097, reasoning 50376, cache_read 3653184)
  - rep02 (true control, `startup_table` called): first-5-assistant input **1645** (71+883+437+106+148), session total **1903**
  - rep3 (direct-render, no `startup_table`): first-5-assistant input **918** (71+847), session total **918**
  - rep4 (direct-render, no `startup_table`): first-5-assistant input **936** (71+865), session total **936**
- Startup path audited from parts (tool-call evidence):
  - rep01: `read` + `omt_net probe` only, no `startup_table` (direct render — lean-like, conservative bias noted in prior entry)
  - rep02: `read` + `omt_net probe` + `startup_table` (only true control per AGENTS.md STARTUP spec)
  - rep3/rep4: `read` + `omt_net probe` only, no `startup_table` (lean-like)
- Binder check (`bind_labels` over 7-day window): 2 distinct trial IDs only (`…_rep01`, `…_rep02`); rep3/rep4 collapse into `…_rep02` with `label_identity_conflict` (trial string says rep02, `rep` field 3/4) — labels must be re-rendered from `run001_labels.jsonl` for any future run (trial string ↔ rep field must agree).
- Observational contrast (NOT a randomized decision): true-control first5 1645 vs clean direct-render mean 927 → **≈718 tokens (≈43.6%)** lower when `startup_table` roundtrip is skipped. Suggestive for the ≥30% hypothesis but formally inadmissible (same arm, N=1 vs N=2, no lean-labeled trials, no `known_task_resume` case).

### Decision (run001 stopped at 4/8 per user direction — no more trials)

- **Keep control / inconclusive.** Decision rule (PROJECT.md §Scope) requires measured ≥30% cumulative input-token cut over first 5 assistant messages AND identical OptionID map AND zero gate regressions across control vs lean. Missing: entire `lean_start_v1` arm (0 trials), entire `known_task_resume` case (0 trials), control-arm fidelity split (1 true-control vs 3 lean-like), label collision on rep3/rep4, rep01 case-script deviation (resume work in first-5 window). No adoption, no token-saving claim (mh13 honest-reporting contract).
- OptionID map: all 4 menus rendered the same 9-option TASKS (A–G projects + H–I new, D19 1:1); no enforcer/gate regression observed in the 4 trial parts. Quality gate holds but comparability fails → `inconclusive` per `evaluate.compare` semantics.
- run001 status: **stopped at 4/8 by explicit user direction** (`do not do more, 4/8 enough`). Manifest (`run001_manifest.json`, 2×2×2=8) unchanged; this entry is the collect record. No `experiment collect/validate` via Tier-2 stub (service returns `experiment:collect` stub) — collection done via `profile` + `compare_sessions` + `bind_labels` with source refs above, replayable from saved session IDs.

### In progress / Blocked

- Pilot run001: 4/8 observed (all `fresh_session_menu/control`), 0/4 lean, 0/4 `known_task_resume`. Stopped — no further user-launched trials per this session's direction.
- feature_135 swap mechanism + feature_136 transport fix remain shipped; no code change in this entry.

### Next

- If mh14 reopens: (1) fix label rendering (unique trial strings per rep — use `run001_labels.jsonl` verbatim, never hand-bump `rep` alone); (2) mandate `startup_table` in control arm (or pin `startup_table_calls: 1` for control fidelity); (3) run the 4 lean trials (2 cases × 2 reps) + 2 remaining control `known_task_resume` to complete the 8-matrix; then `compare` → decide per manifest rule.
- Alternatively close run001 as pilot-inconclusive and spawn a follow-up experiment with the corrected label + fidelity pins.
- Resume entry point: PROJECT.md §New Session Quick Start → this entry → 2026-09-27 fix entry for transport + trial observations.

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
- Closed --force per user direction (feature_136 shipped in-tree, no ledger complete record); line superseded by meta_harness_16.

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
