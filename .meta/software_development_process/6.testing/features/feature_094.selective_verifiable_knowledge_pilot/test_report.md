# Test Report: Selective Verifiable Knowledge Pilot

> **Phase:** Testing — `omt_agent_guide.md §11` | **Feature:** feature_094.selective_verifiable_knowledge_pilot
> Run everything with `uv run pytest ...` (AGENTS.md MANDATORY).

## Stage 1 — Unit / component
| Component | Normal path | Exception paths | Result |
|-----------|-------------|-----------------|--------|
| `kb_pilot.load_lessons` | sidecar loads, 3 active lessons, all REQUIRED_FIELDS + evidence/version/expiry present | missing file / bad shape raises (assert) | [x] |
| `kb_pilot.lookup` | file match, symbol match, dependent match return exact lesson | empty surface / unrelated surface → [] | [x] |
| `kb_pilot.needs_refresh` | same version False, changed version True | — | [x] |
| `kb_pilot.promote` / `retire` | new record with status + check/reason, original unmutated | — | [x] |

## Stage 2 — Integration
- Advisory-only contract: result keys exactly ADVISORY_KEYS (no grant/allow/
  authority fields); sidecar deep-equal before/after lookup (no side effects).
- Representative-task retrieval quality: 4 seeded tasks (tdd file, stage file,
  canary symbol, unrelated UI file) → exact expected id sets (precision/recall 1.0).

## Stage 3 — System (use-case driven)
- T3-6 acceptance: relevant change surfaces the lesson (refresh path via
  `needs_refresh`); unrelated edits stay silent (no re-consult); retrieval
  quality green; promotion/retirement carry documented reason + replacement check.
- Harness integrity: `harnessc check` 0 errors + `build` OK (budgets green,
  265 records → 5 projections); boundary e2e green; full suite 2241/2241.

## Evidence

```
$ uv run pytest tests/scripts/omt/test_kb_pilot.py -q
10 passed in 0.05s
$ uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q
1 passed in 0.76s
$ uv run pytest -q -p no:cacheprovider
2241 passed, 10 warnings in 148.37s (0:02:28)
```
