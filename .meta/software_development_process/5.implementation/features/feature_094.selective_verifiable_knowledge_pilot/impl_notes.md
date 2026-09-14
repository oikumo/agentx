# Implementation notes — feature_094.selective_verifiable_knowledge_pilot

> Date: 2026-09-13 · Scaffolded by `new_feature.py implementation` (feature_090).

## What changed

- `scripts/omt/kb_pilot/__init__.py` (new, ~120 lines): pure advisory layer —
  `load_lessons` (sidecar shape assert), `active_lessons`, `lookup`
  (file/symbol/dependent match, active-only, empty→[]), `needs_refresh`,
  `promote`/`retire` (deepcopy transitions with reason + replacement check).
- `scripts/omt/kb_pilot/lessons.json` (new): 3 seeded lessons (tdd_node,
  stage_policy_order, tests_canary_shadow) with symbol/file/dependent/
  evidence_test/content_version/expiry metadata; evidence refs are live files.
- `tests/scripts/omt/test_kb_pilot.py` (new): 10 goldens, 10/10 green first run.
- `.meta/.../3.analysis/.../analysis_001_knowledge_pilot_scope.md` (new):
  E source, live-state evidence, D5 overlap check, approved Option A boundary.

## Discipline notes

- Approval gate held: 4 alternatives proposed, user picked A (sidecar + advisory)
  before any src/ edit.
- Canary ordering phase→skip→tests: Programming declared first, then
  `omt_skip{scope:tests}` canary, then tests/ write. KB consults recorded
  (2× nav, no records — expected, same as T3-4). Think-gate consulted
  (`harnessc.py` 2 thoughts) before harness-surface work.
- First-write-only on harness surface (3 new files, 1 write each) — no stage
  needed, no second-edit guard tripped; boundary e2e green as the round receipt.
- No `.omt` policy change, no new gate, no auto-learning path (E guardrail holds).
- `uv` only (no bare python/pip/pytest).
