# CURRENT_STATE: harness_reason

> Session-by-session log + resume point. Companion to `PROJECT.md` (canonical).
> Newest entry on top. One `## <date>` block per session.

---

## 2026-09-26 (Tier-2 gate re-convene — promotion CLOSED with measured negative; project close)

### Done

- Tier-2 gate re-convene (sandbox only, no src/net/toolbox change by this review) — decided on feature_130's measured discharge; **user decision at the fork: record + close (option D)** — driver-artifact diagnosis/re-capture (options A/B) and coverage refinements (C) explicitly not pursued.
- Re-ran the evidence for the record: `--ledger` 8/8 `REAL_TOKENS_OK 96ba44edc7968ca0` (measured 18/135, verdict `shrink-tier0-or-keep-planner`) + unledgered baseline `40e6ab74b10b038a` + S0 7/7 (`6e355d7189e13fb5`) + S1 12/12 + S2 7/7 + S3 7/7 (`d476df80d71d829a`) + tier0 PASS + tier1 PASS + reason tests 14.

### Verdict

- **Tier-2 promotion CLOSED**: gate item (1) discharged **negative** (kernel 1,321,729 vs harness 381,919 measured medians → −246%, ≥15% rule missed) → §15.1 kill line fired ("threshold miss — shrink to Tier 0 rather than promoting to Tier 2"); D6 (fair comparison decides) also ranks planner (486,045) below harness — no arm beat the harness discipline on real reuse-sensitive cases.
- **Terminal deliverables** (regression-green, byte-stable): Tier-0 `reason_table.ts` (zero harness cost) + Tier-1 `reason_check.ts` advisory pilot (closed enum, one allow line) + sandbox kernel suite (S0–S3 + held-out + real-token runner/harvester/measured ledger).
- Gate items (2)–(4) (budgets w/ harness-surface cost, `omt_reason.ts` surface, user-selected implementation) **closed as moot** — no positive measured case to promote; the negative result is a legitimate experimental outcome (the decision rule decided, as designed).
- Advisory boundary intact end-to-end: no grant/lease/net/ledger writes at any point; certs never minted authority.

### Next

- Project **CLOSED (complete)** via `project.py close`; reopen via `project.py reopen harness_reason` **only with new evidence** (e.g. a driver-artifact diagnosis showing the kernel-arm cost was a measurement artifact, per-rep captures, or a new measured positive case) per the locked decisions ("do not re-litigate without new evidence").
- Tier-0/1 stay as shipped (features 127/128); no pending harness-surface work from this project.

---

## 2026-09-26 (feature_130 — real-token discharge Done, item (1) discharged with a NEGATIVE measured reading)

### Done

- Implemented `harvest_ledger.py` (stdlib, read-only sqlite): label grammar on first user-message text part, exactly-6/one-per-label/fail-loudly (`harvest_label_conflict`, no partial write), token mapping `prompt = tokens_input + cache_read` / `completion = tokens_output + reasoning`, provenance-rich ledger.
- Two live-verified design corrections (in ledger provenance + TA: thought): `session_input` table is EMPTY → fallback label path (reproduces known sample); session time columns are epoch **milliseconds** → `latency_ms = t_updated - t_created` (design ×1000 would inflate 1000×).
- Negative test first: empty window → `HARVEST_FAIL harvest_label_conflict`, exit 1, no ledger written.
- Capture window `since_ms = 1790459237218` → spawned 6 labeled `general` subagents (batch 1: H1 × harness/planner/kernel; batch 2: H3 rotated kernel/planner/harness), same task text verbatim, same model (z-ai/glm-5.3 nvidia max), arm-method block the only difference; all 6 delivered, all 6 repo-untouched.
- **HARVEST_OK 6/6** → `stage_real_tokens_ledger.json` (6 rows + provenance; loads as "7 rows", provenance never matched by runner).
- **`--ledger` 8/8 PASS ×2, `REAL_TOKENS_OK 96ba44edc7968ca0` byte-stable; measured 18/135; unledgered baseline `40e6ab74b10b038a` preserved** (runner unchanged).
- Regression green: S0 7/7 (`6e355d7189e13fb5`) + S1 12/12 + S2 7/7 + S3 7/7 (`d476df80d71d829a`) + tier0 PASS + tier1 PASS + reason tests 14.
- Test report: `6.testing/features/feature_130.real_token_discharge/test_report.md`.

### Verdict

- Tier-2 gate item (1) **discharged — threshold MISSED on real H1/H3 medians**: harness 381,919 · planner 486,045 · kernel **1,321,729** (kernel H1 session ~1.30M prompt tokens — the sandbox-driver calling pattern re-reads large contexts per op call) → reduction vs harness **−2.461** → `meets_15pct_rule: false` → runner verdict **`shrink-tier0-or-keep-planner`** (decision rule, not prediction).
- Honest caveats held: one capture per (arm,case) × R=3 replay; `proxy: mixed` (T-cases + H2 unmeasured); kernel = sandbox scripts (Tier-0/1 reality); all three H3 arms independently chose `stage0_ir.json` (two bumped ir_version, one resolved d3 — task left the mutation choice open, disclosed).
- Boundary: git status shows only project-home sync + `.meta/.../feature_130*` + `.sandbox/harness_reason/` (4 files) — no src/tests/net/toolbox change from this feature or any capture session.

### Next

- Re-convene the Tier-2 gate to record the negative measured reading and decide: close Tier-2 (shrink to Tier-0/1 per §15.1 kill line + D6 "fair comparison decides" — promotion lacks a positive measured case) or archive the project if Tier-0/1 is deemed terminal. Gate items (2)–(4) stay open in form but no longer have a supporting measured case.

---

## 2026-09-26 (auto — feature_130.real_token_discharge Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_130.real_token_discharge/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-26 (feature_129 — real-token measurement mechanics Done, gate item 1 ready-not-discharged)

### Done

- Picked **A (span wrapper)** at the approval gate (of 3 alternatives in `stage_real_tokens_analysis.md`: A span wrapper / B manual ledger / C calibrated proxy).
- Wrote `stage_real_tokens_analysis.md` (problem, what stays identical from S3, measured-token ledger spec, 3 alternatives, threshold reading on measured medians).
- Wrote `stage_real_tokens_design.md` (closed ops delta: `open_span`/`close_span`, single `_read_host_total` seam, runtime mode detection, V8 span discipline, report envelope delta, named failures).
- Implemented `run_real_tokens.py` (stdlib only): replays S3 verdicts verbatim (same H `f7e6b89317420fbd`, R=3 rotation) with span-attributed costs; `--ledger` mode converts hand-captured live rows to `measured: true, source: "ledger"`.
- **8/8 PASS** `REAL_TOKENS_OK 40e6ab74b10b038a` byte-stable across runs; first honest report: `host_usage_mode: unavailable`, 0/135 measured, verdict `inconclusive_host_usage_unavailable`.
- Fixed during testing: wall-clock `latency_ms` broke cross-run digest stability → unmeasured spans now carry `latency_ms: null` (no fake precision).
- Ledger mechanics smoke-tested with synthetic numbers (18/135 measured, threshold evaluated) — smoke file **deleted**, synthetic numbers never recorded as measured.
- Regression: S0 7/7 (`6e355d71`) + S1 12/12 + S2 7/7 + S3 7/7 (`d476df80d71d829a` unchanged) + tier0 PASS + tier1 PASS + reason tests 14 passed.
- Test report: `6.testing/features/feature_129.harness_reason_real_token_measurement/test_report.md`.

### Verdict

- Tier-2 gate item (1) is **mechanically ready, not discharged**: seam + attribution + threshold-on-measured-tokens exist and replay byte-stable; no host exporter is wired in this environment, so the report honestly reads inconclusive.
- Discharge path: hand-capture real H1/H3 sessions per arm into `stage_real_tokens_ledger.json` and re-run with `--ledger` (or wire a live exporter through `_read_host_total`). Ledger caveat: keyed `arm:case` (one capture replayed across reps); per-rep keys are a future refinement.

### Next

- Capture real H1/H3 tokens per arm (hand ledger or exporter) → re-run `--ledger` → threshold reading on measured medians; then re-convene Tier-2 gate with items (2)–(4) still open (budgets w/ harness-surface cost, `omt_reason.ts` surface, user-selected implementation). Or close/archive if Tier-0/1 deemed terminal.

---

## 2026-09-26 (auto — feature_129.harness_reason_real_token_measurement Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_129.harness_reason_real_token_measurement/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-26 (gate review — Tier-2 promotion HOLD, fixtures sound)

### Done

- Tier-2 promotion gate review (sandbox only, no src/net/toolbox change by this review).
- Re-ran: S0 probes 7/7 (digest `6e355d7189e13fb5` stable) + S1 checker 12/12 + S2 composer 7/7 (rewrite `cfcc014071b10849`) + S3 experiment 7/7 (`d476df80d71d829a`) + held-out 8/8 (`b2083b0c4dd6d610` + S0–S3 regression green) + Tier-0 PASS + Tier-1 demo PASS + `tests/scripts/reason/` 14 passed.
- Tier-2 surface audit: no `omt_reason.ts` (only `reason_check.ts`/`reason_table.ts`), no `@tool omt_reason` row in `.meta/META_HARNESS.omt`, no harnessc build, no e2e receipt, no `toolbox/harness/reason/` proposal (only `budget_check`); Tier-1 stays one `reason_check: allow` line outside harnessc blocks.
- Budgets: per-call §5 summaries ≤2KB + detail_ref hold (demo budget PASS); IR 4.9KB + contracts 9.1KB sandbox-side only; always-loaded 39B headroom still favors on-demand discovery — Tier-2 full harness-surface cost not yet accounted.

### Verdict

- HOLD promotion (repeat of S3 gate): fixtures sound, repeated utility demonstrated via byte-stable digests, no §15.1 kill criterion fired; S3 threshold still proxy bytes (33.2% reduction, `proxy:true`, `keep-kernel-candidate` decision rule, not prediction) — no real-token measurement, no toolbox review, no user-selected Tier-2 implementation yet.
- Promote only via existing toolbox review with: (1) real-token paired measurement, (2) passing budgets with explicit harness-surface cost (39B headroom), (3) `omt_reason.ts` + `@tool` row + harnessc build + e2e receipt + enforcer passthrough wired/tested, (4) user-selected implementation.

### Next

- Real-token held-out measurement or toolbox `harness/reason/` proposal draft; then re-convene gate. Or close/archive if Tier-0/1 deemed terminal.

---

## 2026-09-26 (hygiene — PROJECT.md status sync + manifest regen)

### Done

- Updated `PROJECT.md ## Status`: marked S0/S1/S2/S3/held-out/Tier-0/Tier-1 Done (features 122–128); Tier-2 stays HOLD per gate review.
- Ran `project.py sync` → manifest regenerated (`.projects/meta/META.md`).
- No src/net/toolbox/ledger change — project-home only.

### Next

- Tier-2 promotion gate (toolbox review + §15 gates) or close/archive if Tier-0/1 deemed terminal.

---

## 2026-09-26 (auto — feature_128.harness_reason_tier_1_advisory_pilot Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_128.harness_reason_tier_1_advisory_pilot/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-26 (auto — feature_127.harness_reason_tier_0_renderer Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_127.harness_reason_tier_0_renderer/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-26 (auto — feature_126.harness_reason_held_out_real_tasks Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_126.harness_reason_held_out_real_tasks/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-26 (gate review — S3 fixtures conditional-go, hold promotion)

### Done

- Stage-3 gate review (sandbox only, no src/net/toolbox change by this review).
- Re-ran: experiment 7/7 digest `d476df80d71d829a` stable x2 + checker 12/12 + composer 7/7 + S0 probes 7/7 (digest `6e355d71` stable).
- V1 parity PASS: shared handle `H=f7e6b89317420fbd` identical across 3 arms; fork refused (`input_fork_breaks_parity → reload_shared`); R=3 order rotation + one snapshot/rep disclosed.
- V6 report PASS: 135 rows (15 cases x 3 arms x 3 reps) + summary/per_case/variability/digests/derivation/detail_ref; byte-stable digest.
- Threshold reading: medians harness 1205 / planner 905 / kernel 805 proxy bytes → 33.2% reduction, `meets_15pct_rule: true`, `proxy: true`, verdict `keep-kernel-candidate` — decision rule, not prediction; no correctness loss (V2 agreement PASS), no authority divergence (V7 PASS).

### Verdict

- CONDITIONAL-GO fixtures, HOLD promotion: fixture harness sound; no Tier 1/2 promotion on synthetic costs.
- Note: unrelated pre-existing tree mods (`toolbox/*`, `scripts/omt/net/cli.py`, `.opencode/plugins/omt_net.ts`) untouched by this review.

### Next

- Held-out real tasks (same catalog/budgets/oracle discipline) or Tier-0 `reason_table.ts` decision (zero harness cost).

---

## 2026-09-26 (auto — feature_125.harness_reason_stage_3_paired_experiment Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_125.harness_reason_stage_3_paired_experiment/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

### Done (iter 8 — S3 paired-experiment design Done, 7/7 + 12/12 + 7/7 + 7/7)

- Scaffolded `feature_125.harness_reason_stage_3_paired_experiment` (minor_feature) linked to harness_reason; declared Analysis, filled FEATURE.md summary/scope + PLAN objective.
- Wrote `.sandbox/harness_reason/stage3_analysis.md` (3 arms, shared inputs, T01–T12 + H1–H3, oracle/snapshot/order, metrics + 15% decision rule); `omt_complete` Analysis → Design.
- Wrote `.sandbox/harness_reason/stage3_design.md` (closed experiment ops + run_experiment outline + report envelope); `omt_complete` Design → Programming.
- Implemented `.sandbox/harness_reason/run_experiment.py` (stdlib only, V1–V7 validity checks, 135-row per-case report + variability + threshold rule) → **7/7 PASS** digest `d476df80d71d829a` stable; `omt_complete` Programming → Testing.
- Testing: re-ran experiment 7/7 + checker 12/12 + composer 7/7 + probes 7/7 (digest 6e355d71 stable); `omt_complete` Testing → Done (auto ship entry above).
- No src/tests/net/toolbox change — sandbox-only (13 files in `.sandbox/harness_reason/`); unrelated pre-existing mods in `toolbox/*`, `scripts/omt/net/cli.py` untouched.

### Next

- Stage-3 gate review: confirm shared-inputs parity + report shape + threshold-rule reading (decision rule, proxies labeled); then held-out real tasks or Tier-0 `reason_table.ts` decision.

---


## 2026-09-26 (auto — feature_124.harness_reason_stage_2_composition Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_124.harness_reason_stage_2_composition/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-26 (iter 7 — S2 composer Done, 7/7 + 12/12 + 7/7)

### Done

- Scaffolded `feature_124.harness_reason_stage_2_composition` (minor_feature) linked to harness_reason; declared Analysis, filled FEATURE.md summary/scope + PLAN objective.
- Wrote `.sandbox/harness_reason/stage2_analysis.md` (fragments + 5-law allow-list + two-context cases + U1–U5 witnesses); `omt_complete` Analysis → Design.
- Wrote `.sandbox/harness_reason/stage2_design.md` (expand/rewrite/check/explain ops + rewrite cert envelope + run_composer outline); `omt_complete` Design → Programming.
- Implemented `.sandbox/harness_reason/run_composer.py` (stdlib only, Ctx-A/B reuse + U1–U5 + rewrite replay + boundary) → **7/7 PASS**; `omt_complete` Programming → Testing.
- Testing: re-ran composer 7/7 + checker 12/12 + S0 `run_probes.py` 7/7 (digest 6e355d71 stable); `omt_complete` Testing → Done (auto ship entry above).
- No src/tests/net/toolbox change — `git status` shows only `.projects/meta`, `WORK.md`, `.meta/.../feature_124/`, `.sandbox/harness_reason/` (advisory boundary holds).

### In progress / Blocked

- Nothing in progress. Blocked on nothing.

### Next

- Stage-2 gate review: confirm two-context reuse + U1–U5 witnesses + rewrite replay; then Stage-3 paired experiment design or Tier-0 `reason_table.ts` decision.

### Notes / context

- Resume: PROJECT.md §New Session Quick Start → this entry → §Next; S0 7/7 + S1 12/12 + S2 7/7 artifacts in `.sandbox/harness_reason/` (10 files).

---

## 2026-09-26 (iter 6 — S1 checker Done, 12/12 + 7/7)

### Done

- Wrote `.sandbox/harness_reason/stage1_design.md` (closed check/explain/import ops + cert envelope + run_checker outline, sandbox only); `omt_complete` Design → Programming.
- Implemented `.sandbox/harness_reason/run_checker.py` (stdlib only, 12 cases valid/invalid variants, cert+explain per case) → **12/12 PASS**; `omt_complete` Programming → Testing.
- Testing: re-ran checker 12/12 + S0 `run_probes.py` 7/7 (digest 6e355d71 stable); `omt_complete` Testing → Done (auto ship entry below).
- No src/tests/net/toolbox change — `git status` shows only `.projects/meta`, `WORK.md`, `.meta/.../feature_123/`, `.sandbox/harness_reason/` (advisory boundary holds).

### In progress / Blocked

- Nothing in progress. Blocked on nothing.

### Next

- Stage-1 gate review: confirm 12/12 agreement + Tier-0 renderer decision; then Stage-2 composition (fragments + reuse certs) or Tier-0 `reason_table.ts` (zero harness cost).

### Notes / context

- Resume: PROJECT.md §New Session Quick Start → this entry → §Next.

---

## 2026-09-26 (auto — feature_123.harness_reason_stage_1_checker Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_123.harness_reason_stage_1_checker/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-26 (iter 5 — S1 Analysis done, Design)

### Done

- Confirmed 12 §14.1 cases (proposal lines 980-991, valid+invalid variants) + S0 reuse map (all 8 generators cover all 12).
- Wrote `.sandbox/harness_reason/stage1_analysis.md` (12-case table + check/explain subset + immutable import + exit criteria, sandbox only).
- `omt_complete` Analysis → Design passed (minor_feature declaration-only); declared `omt_phase minor_feature Design`.

### In progress / Blocked

- Design in progress (quick op list: check/explain ops, context import, slice format). Blocked on nothing.

### Next

- Draft `.sandbox/harness_reason/stage1_design.md` (op list + I/O + certificate envelope), then declare Programming and implement `run_checker.py` sandbox probe for 12/12 agreement.

### Notes / context

- Resume: PROJECT.md §New Session Quick Start → this entry → §Next; no src/net/toolbox change (think-gate clear on run_probes.py).

---

## 2026-09-26 (iter 4 — S1 scaffold feature_123, Analysis)

### Done

- Scaffolded `feature_123.harness_reason_stage_1_checker` (minor_feature) linked to harness_reason via `new_feature.py`.
- Declared `omt_phase minor_feature Analysis` (scope: check+explain on 12 §14.1 cases, immutable import, sandbox only); filled FEATURE.md summary/scope + PLAN objective.

### In progress / Blocked

- Analysis in progress. Blocked on nothing.

### Next

- Finish Analysis (confirm 12 §14.1 case list + S0 IR reuse), then declare Design (quick op list: check/explain/compare-withheld plan) and implement sandbox checker.

### Notes / context

- Resume: PROJECT.md §New Session Quick Start → this entry → §Next; S0 artifacts in `.sandbox/harness_reason/` (8 contracts + IR + 7/7 probes).

---

## 2026-09-26 (auto — feature_122.harness_reason_stage_0_contract_extraction Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_122.harness_reason_stage_0_contract_extraction/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-26 (iter 3 — S0 probes 1–7 PASS 7/7, Testing)

### Done

- Implemented `.sandbox/harness_reason/run_probes.py` (stdlib only) covering §15.8 1–7; `uv run --no-sync python` → 7/7 PASS (probe 1 cites both NEXT + refuses + missing premise, never diagnosis; probe 2 split with (h1,h0) witness; probe 3 subject_digest_mismatch agreement; probe 4 duplicate_exclusive_claim reject; probe 5 snapshot_inconsistent; probe 6 fresh obligations + h2-with-h1 refuse; probe 7 digest 6e355d71 byte-stable).
- Advanced feature_122 Programming → Testing via `omt_complete`; `git status` shows only `CURRENT_STATE.md` mod + `.sandbox/harness_reason/` new — no src/test/net/toolbox change (advisory boundary holds).

### In progress / Blocked

- Nothing in progress. Blocked on nothing.

### Next

- Close Testing → Done for feature_122; then Stage 1 gate review (12/12 §14.1 agreement + Tier 0 renderer optional).

### Notes / context

- Resume: PROJECT.md §New Session Quick Start → this entry → §Next.

## 2026-09-26 (iter 2 — S0 Design: 8 contracts + IR + probes outline)

### Done

- Declared `omt_phase minor_feature Design` for feature_122 (scope: 6–10 contracts + IR ready for probes 1–7); src edits unlocked, no src/net/toolbox change made.
- Wrote `.sandbox/harness_reason/stage0_contracts.json` (8 generators v1: evidence/context/equalizer/preserves/realize/compare/macro/next-discrepancy, each with authority + validator_ref + unknown_if) — JSON parses.
- Wrote `.sandbox/harness_reason/stage0_ir.json` (§2 Obs/D/A + HarnessObs d1/d2/d3 + F preserves + aligned query + refresh compute + concretize cases) — JSON parses.
- Wrote `.sandbox/harness_reason/stage0_probes.md` (probes 1–7 pass criteria per §15.8 + §15.9 gates).
- Sandbox check via `uv run python`: contracts 8/8 fields+authority, equalizer d1/d2/d3, reorder edit;test=(h1,h1) vs test;edit=(h1,h0), probe-1 refuse-equality discipline — ALL PASS.

### In progress / Blocked

- Nothing in progress. Blocked on nothing.

### Next

- Declare Testing for feature_122 and run probes 1–7 fully in sandbox (probe 1 cite both NEXT + refuse; probe 2 split verdicts; probe 3 adapter agreement; probe 4 lease reject; probe 5 snapshot race; probe 6 two-context reuse; probe 7 byte-stable replay), then close or advance to Tier 0 renderer.

### Notes / context

- Resume: PROJECT.md §New Session Quick Start → this entry → §Next; artifacts in `.sandbox/harness_reason/` only.

## 2026-09-26 (iter 1 — v0.1 PROJECT.md drafted)

### Done

- Project home created (`project.py new --slug harness_reason`, state: draft).
- PROJECT.md v0.1 drafted from `.sandbox/category_theory_meta_harness.md`: one-product lock (D1), advisory-only boundary (D2), JSON-IR-first + no-prover/runtime-change (D3), §§3–5 normative core (D4), Tier 0→1→2-promotion-only with kill line (D5), fair-comparison decides (D6); S0–S4 scope + S0/S1/S2/S3/S4 success gates + kill/shrink rule.

### In progress / Blocked

- Nothing in progress. Blocked on nothing (non-gated iterate).

### Next

- Stage 0 contract extraction: draft 6–10 versioned generator contracts + JSON IR for §2 example and §3 three-row tables, then run probes 1–7 in sandbox (probe 1 passes only on cited NEXT contracts + refused comparison).

### Notes / context

- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.
- Source doc authorizes research + design only; no engine/source/test/policy/net/toolbox-registration change.
- First linked feature flips header draft → active mechanically.
- Linked feature_122.harness_reason_stage_0_contract_extraction (origin: scaffold) — state draft to active, now in startup menu as proj:harness_reason
