# Test report — feature_086.ordered_skip_audit_plus_bootstrap_fingerprint (T1-1)

> Date: 2026-09-13 · Type: minor_feature · Status: PASS

## Scope verified

- `op:audit` ordered skip audit + U12 bootstrap fingerprint (mh8 T1-1,
  mh2 U4 + U12): `foldSkipAudit` over `readLedgerAll[At]` (ALL archives +
  hot, FILE ORDER preserved — never re-sorted) returns `skip_audit`
  (`{ts, scope, reason, session}` per `kind:skip`), `scope_tally`
  (per-scope counts), and `bootstrap_templates` (last-3 reasons matching
  `/bootstrap/i`; with `feature`, only reasons containing the feature
  substring — skip records carry no feature field, the slug is matched in
  reason text). `as_of` replays the full ledger at the commit with
  `as_of_scope: "replayed:ledger-all; live:schema-join+project_drift"`;
  the q-ledger records the resolved sha (U18 adoption-gate measurable).
- T1-2 schema half untouched: `design_only` / `testing_only` / `fix_it` /
  `project_drift` byte-identical shape (068 goldens green unmodified).
- No schema-text change: `feature` arrives via the `omt_q` dispatch args
  (the unregistered `omt_audit` signature keeps `{as_of}` only) — budgets
  UNCHANGED (tool_args 2454/2464, tool_schemas 1812/1856).

## Goldens (`tests/scripts/omt/test_omt_q_audit_t1_1.py`, 3 green)

- Live ordered audit matches ledger file order (ts sequence equality vs
  ALL archives + hot); `scope_tally` sums to skip count and equals the
  Counter over scopes.
- Live template list returns the last-3 bootstrap reasons (computed
  independently from the ledger files).
- Hermetic seeded ledger (6 skips + 1 phase record): file order preserved
  with the non-skip excluded; `scope_tally == {tests:4, nav:1, src:1}`;
  global last-3 bootstrap reasons; `feature: feature_900.alpha` filters to
  the 3 reasons mentioning that slug and echoes `feature`.

## Incidental discipline notes

- `skip-latest-wins` (canary, scope: tests): new hermetic goldens only
  (single `omt_skip`, newest wins).
- Genuine RED: goldens drafted pre-implementation fail with
  `skip_audit`/`scope_tally`/`bootstrap_templates` absent (envelope shape
  assertion) — verified by running the new file against the pre-patch
  plugin (3 failed) before GREEN.
- Round discipline: one harness-surface round on `.opencode/plugins/omt_q.ts`
  (header comment + `foldSkipAudit` + rewired `omt_audit` applied in a
  single `uv`-run script = ONE edit for the round), e2e receipt refreshed
  before any further touch; the test file itself is receipt-EXEMPT.
- `OMT_LEDGER_PATH` unset in this env; tests still `delenv(..., raising=False)`
  per the feature_051/A1 gotcha so tmp-root probes never follow the env.

## Verification

- New goldens: 3/3 green.
- Neighbors: audit + q + state-summary suites — 27/27 green.
- Boundary e2e (`test_omt_harness_e2e.py`): 1/1 green.
- `harnessc check`: 0 errors (263 records) · `build`: OK (5 projections).
- Full suite: 2156 passed, 0 failed.
