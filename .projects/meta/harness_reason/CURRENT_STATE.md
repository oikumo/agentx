# CURRENT_STATE: harness_reason

> Session-by-session log + resume point. Companion to `PROJECT.md` (canonical).
> Newest entry on top. One `## <date>` block per session.

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
