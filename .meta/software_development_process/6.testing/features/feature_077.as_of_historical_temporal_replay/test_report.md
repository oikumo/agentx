# Test report — feature_077.as_of_historical_temporal_replay (T1-4)

> Date: 2026-09-12 · Type: minor_feature · Status: PASS

## Scope verified

- `omt_q{op:state|plan|drift, as_of:"<commit>"}` replays the interrogative substrate at the given commit via `git show <commit>:<path>` — never touches the working tree.
- Substrates replayed (mh2 U18 list): `harness.ir.json` (IR), `ledger.jsonl` + `ledger-YYYYMM.jsonl` archives (latest+hot for `readLedgerAt`, ALL for `readLedgerAllAt`), `thoughts.jsonl`, `kb.ir.json` (+ referenced source files for drift), `scripts/omt/tdd/state.py` (KNOWN literal).
- `as_of_commit` envelope field resolves the ref to a full sha (`git rev-parse --verify <ref>^{commit}`); unresolvable refs fail open to the as-given value with the at-commit readers returning empty (same fail-open posture as the live readers).
- Historical phase pick (`featurePhaseAt`): tombstone-aware latest-record, NO 8h liveness window (every record at a past commit is "past"; the window is meaningless for replay).
- Live-only by design (documented via `as_of_scope` in the envelope): plan's gate-impl session/phase evaluation + receipt_detail; drift's `project_drift` fold. plan marks `replayed:ir+ledger; live:session-state+receipt`.
- Ledger telemetry (`kind:"q"`): `as_of` now records the resolved sha instead of the hardcoded `"HEAD"` when a replay ran.

## Tests

- RED→GREEN (same test_node discipline): `tests/scripts/omt/test_omt_q.py::TestAsOfReplay` — 3 goldens over a hermetic two-commit git fixture (commit C: phase=Analysis + intact TA marker; HEAD: phase=Programming + marker deleted):
  1. `test_state_at_commit_c_differs_from_head` — as_of resolves to C's sha; state-at-C reports Analysis, no-as_of state reports Programming at HEAD. **(the T1-4 golden: state-at-C ≠ state-at-HEAD on seeded drift)**
  2. `test_drift_at_commit_classifies_seeded_drift` — drift-at-C clean (marker intact), drift-at-HEAD reports the `src/x.py` record MOVED.
  3. `test_plan_as_of_resolves_and_marks_scope` — plan resolves as_of and emits `as_of_scope`.
- Regression: `test_omt_q.py` + `test_omt_q_audit.py` + `test_omt_q_state_summary.py` → **24/24 pass** (all v1.3/v1.5 envelopes unchanged on the no-as_of path).
- Boundary e2e: `tests/scripts/omt/test_omt_harness_e2e.py` → **1/1 pass** (fresh receipt covers the harness-surface edits).
- `harnessc check` → 0 errors; `harnessc build` → OK; all budgets green.

## Incidental repair (feature_059 pin re-measure)

- `test_tight_budgets_unchanged` was failing pre-074..076 on +6B/+8B drift of the tight ceilings (line-number drift of later `.omt` appends + 073–076 tool additions — the pin's own docstring anticipated this class). Re-measured `_sizes()` at HEAD and re-pinned: `NAV_INDEX_CEIL 63923→63929`, `TOOL_ARGS_CEIL 2278→2284`, `TOOL_SCHEMAS_CEIL 1770→1778` (all still far under the real harness budgets; the feature_059 kind/render contract is untouched). The pin now passes — **KNOWN stays empty (A1 invariant)**, no allowlist was added.

## Full suite

- `uv run pytest -q`: **2084 passed, 1 failed** — the failure is `test_omt_live_opencode_guards.py::test_plugins_load_and_tools_execute`, a live test that spawns a real `opencode run` subprocess and times out at 240 s in this environment; verified it **fails identically on clean HEAD (stash-checked)** — environmental, unrelated to feature_077 (matches the 076 report's deselection note).

## Notes

- LSP flags a pre-existing unresolvable `import harnessc` in `test_budget_pins.py` (sys.path-injected import, runtime-fine); untouched.
- U18 gate note (`count(q with as_of != HEAD) > 0 k sessions`) is the adoption guard — replaying is now possible; uptake is measured by the `as_of` field newly recorded per `kind:"q"` ledger record.
