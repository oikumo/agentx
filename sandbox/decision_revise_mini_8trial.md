# Decision REVISE — mini 8-trial closeout (2026-10-12, v2 server)

Project: meta_harness_skills · Pick A (8-trial mini-matrix, zero live execution).
Supersedes dry_run `inconclusive` with a closable `revise`.

## Mini matrix (versioned, dry_run only)

- `experiment: phase4_validation_mini`, `run: mini_8trial`, `version:1`
- 4 cases × baseline/treatment × 1 rep = 8 trials, budgets 15k/200/1, rule `quality_gated_paired_compare`
- `plan/dry_run/collect/validate` → all ok, `executed:false`; dry_run enumerates 8 trials deterministic; `run` never called (run-gated held)

## Quality + cost (fake)

- Fake metrics all-`pass` with treatment cheaper on cost → `compare` per-case `baseline_held / quality_held_not_cheaper` (quality held, cost delta not recognized on this metric — cheaper-failed never wins preserved)
- Injected failed-quality (160 goldens) → `inconclusive quality_not_held` (proven) — quality gate works, cost never overrides quality
- Live: 0/8 executed → no live win claimable

## Supporting (v2 server, 2026-10-12)

- `pytest feature_160` 7 passed; `skill.py list` 3 pilots contract-ok (recover-block, resume-work, verify-closeout); doctors baseline ok
- 160 `decision.md` dry_run inconclusive stands; this doc provides the closable read on the mini proxy

## Decision: REVISE

- Retain 3 pilots manual-only (`autoinvoke:false`); drop autoinvoke enablement until real-trial launcher slice lands with safe launch path + claims
- Defer `omt-deliver-change` / `omt-session-evidence` / `omt-evaluate-skill` past this decision (unchanged OUT)
- Record thresholds held: quality must hold on every rep before cost compares; cost proxy inconclusive here → no retain-on-cost, no drop-on-quality (quality held) → `revise` (keep procedure, revisit measurement with live path)
- Provenance: `validation.py` + `expand_matrix` + `omt_session plan/dry_run/collect/validate` + 7 goldens + doctors

## Closeout

- Next: PROJECT Status Phase4 → `revise`, CURRENT_STATE mini block, pause refresh to HEAD, commit (free-commit after pick A, local-only).
