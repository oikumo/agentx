# Design 004 DRAFT — Pilot launch path (12-trial real execution)

> Status: **DRAFT, not approved** · Feature: `feature_131` follow-up (project `meta_harness_13` is `complete`) · Date: 2026-09-27
> Inputs: PROJECT.md §Labeled experiments + lifecycle · design_003 §5 (plan-only) · `service.py:87` + `evaluate.request_run()` (`no_safe_launch`) · test_report Addendum S6 full.
> This draft only plans how `run` could become real. No launches, no tokens, no code changes by writing this file.

## 1. Goal

Turn `experiment run` from `no_safe_launch` into guarded real execution for `context_strategy/run_001` (2 variants × 2 cases × 3 reps = 12 independent captures), then collect/validate/compare per PROJECT.md without inventing N or smearing costs.

## 2. Matrix (frozen for run_001)

- Experiment `context_strategy`, run `run_001`, seed recorded.
- Cases: `markdown-summary`, `python-fix` (digests pinned, `/tmp` isolation).
- Variants: `baseline`, `candidate` (only intended factor differs).
- Reps: 3 independent captures per (case, variant).
- Labels: `[mh13.experiment]` v1 `trial_start|span_start|span_end|trial_end|checkpoint`, attempt=1 new identity on retry.
- `dry_run` reference: 12 trials, `executed: false` (verified S6).

## 3. Pre-approval checklist (explicit `p` required)

- [ ] Hypothesis, decision rule (`quality_gated_paired_compare`), outcome checks frozen in manifest v1.
- [ ] Model/provider/settings, task digests, budgets (tokens/time/concurrency) pinned.
- [ ] Isolation paths confirmed (`/tmp` per-trial worktree/selector, no repo writes outside allowlist).
- [ ] `omt_net` resource claims + dispatch/claim controls available (no second scheduler).
- [ ] Protected-path + content-is-data rules acknowledged (transcript bodies never dumped by default).
- [ ] Overhead disclosure plan (instrumentation cost separate from trial cost).
- [ ] Cancellation/resume + checkpoint procedure agreed.
- [ ] Project reopen (or follow-up feature) approved — `meta_harness_13` is `complete`.

## 4. Proposed run contract (to be built, not present)

- `experiment run` remains explicitly effectful (never under read-only passthrough).
- Per-trial independent OpenCode launch via supported execution + existing META HARNESS gates.
- Marker injection verified after capture (emitter identity stored; echoes never become trials).
- Concurrency/token/time bounds enforced; over-budget → named `query_limit_exceeded` / `run_budget_exceeded` + cursor, never silent truncation.
- Child sessions bound only via recorded parent/delegation or verified binding.
- Missing end markers = incomplete, never implicit success.

## 5. Collect / validate / compare (reuse S1–S4 core)

- Collect: bind labels → manifest, trial/span/session membership, raw usage + source refs, consistent snapshot.
- Validate: expected vs observed (12/12 for success); reject duplicates/conflicts/missing/drift/contamination/spoofed echoes/orphan-reversed spans; classify usable/incomplete/invalid/excluded with reasons.
- Compare: paired per-case/per-rep, independent N=usable, quality must hold on every rep of both variants or `inconclusive`; cheaper failure never wins.
- Replay: recompute from saved snapshot/manifest, digests stable, N never increases.

## 6. Exit evidence (for future Test Report addendum)

- 12 independent real captures with manifest-bound message labels.
- Quality results + per-trial metrics (input/output/reasoning/cache-read/cache-write/cost/latency/errors).
- Negative battery still green (synthetic invalid trials excluded with reasons).
- Regression `uv run pytest -q` + `harnessc check 0 errors` + fresh e2e receipt if harness-surface touched.
- One auditable report bundle (JSON/JSONL + compact report + digests + replay manifest).

## 7. Non-goals / risks

- No unrecorded-reasoning reconstruction; no auto policy/src changes; no remote log services.
- Small N=3/rep → no significance claims; pilot is feasibility, not promotion evidence.
- `harness_reason` closed promotion unchanged by any new result.
- If safe launch or budget enforcement unavailable, keep `no_safe_launch` (current behavior).

## 8. Next

1. Approve this draft → allocate follow-up feature (`new_feature.py`) linked to `meta_harness_13` reopen.
2. Declare Design → Programming with TDD (`run` + isolation + bounds + collect/validate).
3. Execute only on explicit `p` invocation.
