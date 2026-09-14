# Task-cost benchmark — first numbers

Pinned rev: `3478bb26f2ce9653ed28ebd567463f21657a622b`

| task | steps | harness_calls | TP/FP/missed | interv/recov | verify_s | io_bytes | tokens_est | success | regr |
|---|---|---|---|---|---|---|---|---|---|
| bugfix | 11 | 2 | 2/0/0 | 2/0 | 9.256 | 18789 | 4697 | ✅ | 0 |
| concurrent_conflict | 11 | 8 | 3/0/0 | 2/0 | 0.0 | 8513 | 2128 | ✅ | 0 |
| cross_layer | 12 | 2 | 2/0/0 | 2/0 | 5.686 | 29934 | 7483 | ✅ | 0 |
| harness_repair | 12 | 2 | 2/0/0 | 3/0 | 6.445 | 77713 | 19428 | ✅ | 0 |
| major | 13 | 6 | 2/0/0 | 5/0 | 1.147 | 3440 | 860 | ✅ | 0 |
| resume | 7 | 1 | 2/0/0 | 0/0 | 0.0 | 1829 | 457 | ✅ | 0 |
| TOTAL | 66 | 21 | 13/0/0 | 14/0 | 22.534 | 140218 | 35053 | ✅ | 0 |

## Assumptions

- scripted deterministic agent (not a live LLM) — measures harness interaction cost, not model reasoning cost; steps modeled on recent real features (087/091/092 ceremony shapes)
- bash/read denies enforced by opencode core are re-evaluated from the same opencode.jsonc rules text
- removal savings assume a rational agent skips ceremony for a removed gate (annotation model)
- session bootstrap + thought-injection bytes counted on first result per session (real hook behavior replicated in-probe)
- two-hats skip-shadowing (TA:112c): after omt_skip{scope:tests} the skip shadows the tdd phase record so the impl edit and g.tdd_after run un-two-hatted — recorded as FINDING, not failure
- net fire receipt is session-agnostic (TA:119); concurrent order is A claim → B double-claim → B no-work_start edit → B stale-rev claim → A fire → A edit → A checkpoint
- g.think consult order (TA:124): B think-consults net/state.py before the no-work_start edit, else the g.net removal slip is masked

## FINDINGS

- two-hats shadow-off: impl edit between red and green runs un-two-hatted after the RED-bootstrap canary skip (reality, not theory)
- worktree baseline: fresh pinned-rev worktrees have no .opencode/node_modules so the tdd baseline full-suite run carries pre-existing bun-import failures (lands in baseline_failures)
