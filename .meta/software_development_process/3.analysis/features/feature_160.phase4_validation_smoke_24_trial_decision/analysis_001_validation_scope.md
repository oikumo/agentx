# Analysis 001 — Phase4 validation scope

Feature: feature_160.phase4_validation_smoke_24_trial_decision · Phase: Analysis · Date: 2026-10-12
Consumes: 153 + 154 + 155 + 156 + 157 + 158 + 159. Closes meta_harness_skills rollout (Phase4), opens rollout-decision.
Project: meta_harness_skills active v0.3 ALL scope · Next per PROJECT Quick Start: Phase4 validation (smoke + 24-trial + decision)

## Problem

Phase0 base-green `[x]`, Phase1 contracts `[x]` (154 contract + 155 envelope + 156 StateScope), Phase2 pilots `[x]` (157 resume-work + 158 verify-closeout + recover-block skeleton), Phase3 session-compat `[x]` (159 `version:1` + `from_session`) — but no measured evidence that the 3 manual-only pilots (`omt-recover-block`, `omt-resume-work`, `omt-verify-closeout`, all `autoinvoke:false`) cut mistaken steps vs baseline.

PROJECT §Scope(5) demands test pyramid before 24-trial live pilot (4 cases × baseline/treatment × 3 reps = 24 trials): schema/lint → contract → scenario/golden → witness-replay → integration (fake OMT) → live-smoke → experiment (quality first, tokens/time/retries second). Gates demand evidence-reliable (11-15) → rollout-decision retain/revise/drop/inconclusive (12-04) on pre-declared near-miss-rate + outcome-quality thresholds. None of that exists yet — autoinvoke decision would be opinion without it (violates D2 contracts-before-autonomy).

## Evidence

- Pilots contracted + manual-only: `.opencode/skills/omt-{recover-block,resume-work,verify-closeout}/{SKILL.md,skill.contract.json}` — `skill.py list` 3 ok, `doctor` contract-ok ×3 (verified 2026-10-12, post-`bd045cf` still `list` 3 ok).
- Envelope v1: `scripts/omt/skill_result.py` + `skill.result.schema.json` + `from_session` adapter (159) — blocked vs succeeded needs no textual heuristic; versioned errors `version:1` UPPER_SNAKE `code` + `remediation` + `read_only:true` (probe: `missing_db` + `manifest_invalid` both versioned).
- Session inspector: `omt_session` 9 ops `sessions|capture|query|inspect|trace|profile|compare|experiment|export` over read-only DB; `experiment plan|dry_run|run|collect|validate|replay`, `run` gated — no auto launch. Live DB exists 3.6 GB but skills never hardcode path (159 goldens pin no-secret-path).
- Test precedent: 154 7/7 + 155 7/7 + 156 3 goldens + 157 7/7 + 158 7/7 + 159 7/7 single-cycle TDD; `split_proof_meta 39/39` owned by CI, not re-run in skills (158 Analysis constraint kept).
- Net STALE: live `rev0 idle_empty` vs file `rev60 Pool 0/0/7` — owned by net reconciliation (`stale_rev60_vs_live0_proposal.md A1`), not skills. Do NOT bare `net_to_md`. Push preview Options now 11 incl `proj:meta_harness_skills` (WORK.compiled 10 stale).
- WORK budget tight: WORK.md 11261B / 11264 at 159 Done; CURRENT_STATE 5747B (159 block on top); pause `pause_2026-10-12_meta_harness_skills.md` frozen at `fd0b4d2` (pre-159) — refresh deferred to closeout.
- `omt_q drift 0`, `q_state Unknown no stranded_red`, status `Done expires 6h` valid next Analysis/Design/Programming/Testing.

## Constraints

- Manual-only pilots stay `autoinvoke:false` through validation — experiment measures, never enables autoinvoke. Decision only on pre-declared thresholds (near-miss-rate + outcome-quality).
- `run` gated: `experiment run` never auto-launched by skill or analysis; dry_run + collect/validate/replay first, explicit user pick for live run (META_HARNESS self-inspection rule).
- Quality first, tokens/time/retries second; deterministic stdlib-only harnesses, no LLM in measurement path, provenance-bound export.
- New files only + docs: `experiment/` harness under `scripts/omt/` or `tests/harness_meta/feature_160*/` goldens + decision doc; no second state store, no skill-side SQLite path (D4), policy by reference (D5).
- Harness-surface 2nd-edit guard: one edit per file per e2e receipt round; WORK trim-while-adding (pause-line discipline); no bare `net_to_md`.
- TDD major_feature: Programming auto-activates `omt_tdd testlist→red→green→refactor→done`, RED tests/ only, GREEN src/ only.

## Alternatives

- A) Smoke-only (rejected as sole ship — fast but no 24-trial, decision would be inconclusive by construction).
- B) Full validation: smoke + 24-trial pyramid + rollout-decision (chosen per user pick B 2026-10-12 — measures quality + cost, produces retain/revise/drop/inconclusive on thresholds).
- C) Docs-first then B (folded in — WORK/pause refresh happens in Testing closeout, not separate feature).

## Scope lock

`feature_160` ships: (1) smoke: `doctor+list` ×3 + `split_proof_meta` pin + live-smoke 4 cases baseline/treatment dry_run; (2) 24-trial `4 cases × baseline/treatment × 3 reps` via `omt_session experiment plan→dry_run→(gated)run→collect→validate→replay` with fake-OMT integration first; metrics quality (witness pass, envelope `succeeded/blocked` correctness, no-invented-state) then tokens/time/retries + near-miss-rate; (3) decision doc `retain|revise|drop|inconclusive` against pre-declared thresholds + evidence export with provenance. `omt-evaluate-skill` + `omt-deliver-change` + `omt-session-evidence` skills OUT — deferred past decision. Autoinvoke enablement OUT — decision only.
