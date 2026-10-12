# Rollout Decision — feature_160 (dry_run only)

Date: 2026-10-12 · Rule: `quality_gated_paired_compare` · Thresholds (pre-declared): near-miss-rate + outcome-quality must both hold on every rep of every case; cost (tokens/time/retries) compared only after quality holds; cheaper-failed never wins.

## Matrix

- 4 cases (recover-block-positive, resume-work-reconcile, verify-closeout-checklist, session-compat-envelope) x baseline/treatment x 3 reps = 24 trials.
- Fake executor only (`executed:False`); live run gated (requires explicit user pick + claims + budgets).

## Outcome

- Dry_run: manifest valid v1, matrix 24 stable, gates refuse without claims (proven), compare inconclusive on injected failed-quality (proven), smoke doctors ok.
- Live evidence: 0/24 executed → `inconclusive (dry_run only, live run gated)`.

## Decision

- `inconclusive` — retain pilots manual-only, do NOT enable autoinvoke, proceed to user-gated live 24-trial when approved. Options retain/revise/drop deferred to live evidence.
- Provenance: test_report 7/7 + `validation.py` + `expand_matrix` dry_run + TDD DONE cycles 4.
