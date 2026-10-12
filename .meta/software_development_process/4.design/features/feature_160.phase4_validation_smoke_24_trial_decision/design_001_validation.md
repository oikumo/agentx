# Design 001 — Phase4 validation smoke + 24-trial + decision

Feature: feature_160.phase4_validation_smoke_24_trial_decision · Date: 2026-10-12
Supersedes: `analysis_001_validation_scope.md`.

## Artifacts (additive only, reuse cores, no second harness)

1. `tests/harness_meta/feature_160.phase4_validation_smoke_24_trial_decision/test_validation_meta.py` — 7 goldens (stdlib, deterministic, no LLM, fake executor only):
   - manifest-valid: `manifest.create(experiment="phase4_validation", run="smoke_24trial", cases=[4], variants=["baseline","treatment"], reps=3, budgets={tokens,time_s,concurrency}, decision_rule="quality_gated_paired_compare")` validates, `version==1`.
   - matrix-24: `expand_matrix` yields 24 trials deterministic order `4 cases × 2 variants × 3 reps`, trial ids stable, dry_run basis no execution.
   - budgets-gate: `run_gate.gate_run` without budgets → `budget_missing` refused; without `claims`/`explicit_p` → `no_safe_launch` refused `executed:False` (proves run-gated, no auto launch).
   - isolation-guard: `check_isolation` with protected dest (`.env|opencode.db|.git/`) → `isolation_unavailable`; `/tmp` base ok.
   - smoke-doctor: `skill.py list` 3 pilots ok + `doctor` contract-ok ×3 via subprocess (fast, hermetic, no full suite).
   - compare-quality-gated: `evaluate.compare` with one failed quality rep → `inconclusive quality_not_held`; all-pass + cheaper candidate → per-case `retain` support; cheaper-failed never wins.
   - envelope-mapping: `skill_result.from_session` + `validate_envelope` on experiment refusals (`MANIFEST_INVALID`, `MISSING_DB`) → `blocked` with `blocker{gate,code,remediation}` clean.
2. `scripts/session_inspect/` reuse only (no edits this feature): `manifest|run_gate|launcher(plan_trials+dispatch_fake)|collect|evaluate(validate_collection+compare)|exporter(BUNDLE_VERSION=1)` — proves pyramid without forking cores (harness-surface 2nd-edit guard respected).
3. Decision doc template `6.testing/features/feature_160.../decision.md` (filled in Testing): pre-declared thresholds `near-miss-rate + outcome-quality` → `retain|revise|drop|inconclusive`, quality first then tokens/time/retries, provenance-bound export reference.
4. Cases (4, from pilots + compat):
   - `recover-block-positive` (blocked-toolchain recovery via `omt-recover-block` checklist)
   - `resume-work-reconcile` (pause→CURRENT_STATE→fingerprints via `omt-resume-work`, no invented state)
   - `verify-closeout-checklist` (FEATURE+4 docs + doctor + goldens via `omt-verify-closeout`)
   - `session-compat-envelope` (live-DB refusal versioned + `from_session` mapping, no secret path)
   Baseline = prose/no-skill procedure; treatment = manual SKILL.md procedure (`autoinvoke:false` preserved). Each ×3 reps = 24.
5. No new skill, no autoinvoke change, no live `executed:true` launch this feature — fake executor only (`executed:False`); live run deferred to explicit user-gated run after dry_run green.

## Non-goals

- No `omt-evaluate-skill` / `omt-deliver-change` / `omt-session-evidence` new skills; no autoinvoke enablement; no live-DB writes; no `data_migration` creation; no bare `net_to_md`; no full-suite re-run in goldens (`split_proof_meta 39/39` CI-owned pin only).

## Acceptance

- `manifest.validate` + `expand_matrix 24` + `gate_run` refusals + `compare` quality-gating all green; `skill.py list/doctor` 3 ok; 159 7/7 + 154–158 24/24 still green (no-regression subprocess subset); WORK ≤11264 trim-while-adding; TDD single-cycle RED→GREEN same node; decision doc filled with thresholds + `inconclusive`-by-default until live run.

## Rollout

- Land test file + decision template in one commit (docs + tests only, no src core edits → 2nd-edit guard clean); Testing fills decision as `inconclusive (dry_run only, live run gated)` unless user explicitly gates live run; closeout refreshes CURRENT_STATE + pause file + WORK Paused line.
