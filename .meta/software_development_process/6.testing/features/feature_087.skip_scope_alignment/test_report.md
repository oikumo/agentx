# Test report — feature_087.skip_scope_alignment (T2-4)

> Date: 2026-09-13 · Type: minor_feature · Status: PASS

## Scope verified

- T2-4 skip-scope alignment (mh8, mh3 P2-7): the coverage-gate override
  honors the natural scope (`scope:tests`) as well as break-glass
  (`scope:all`); unrelated scopes (nav/src) still block. The TS block
  message now names the exact required call (`scope:"all"` verbatim,
  noting `scope:"tests"` also satisfies coverage).
- `scripts/omt/tdd/gates.py` `cmd_validate_exit`: `scope == "all"` →
  `scope in ("all", "tests")` (window semantics unchanged).
- `.opencode/lib/enforcer/phase_gate.ts` `omt_complete`: block text
  `omt_skip{reason:"..."}` → `omt_skip{reason:"...", scope:"all"}
  (scope:"tests" also satisfies coverage)`.

## Goldens (`tests/scripts/omt/test_skip_scope_alignment.py`, 5 green)

- Fixture blocks on a seeded coverage gap (extra() unreferenced) with no skip.
- T2-4 GOLDEN: `scope:tests` skip → ok:true with skip_override.
- `scope:all` still overrides (feature_024 hatch preserved).
- `scope:nav` does NOT clear coverage (no scope-creep).
- TS file contains `scope:"all"` verbatim in the block message.

## Incidental discipline notes

- `skip-latest-wins` (canary, scope: tests): new hermetic goldens only.
- Genuine RED: 2/5 failed pre-fix (scope:tests + message); 3/5 passed
  (baseline/ scope:all / scope:nav) — verified before GREEN.
- Receipt round-robin: ONE edit per harness-surface file per e2e receipt
  (gates.py + phase_gate.ts in one parallel round, test file edits each
  preceded by `test_omt_harness_e2e.py` refresh; test file receipt-EXEMPT
  for the final GREEN run).
- `OMT_LEDGER_PATH` unset in this env; hermetic fixtures monkeypatch
  LEDGER_PATH/SNAPSHOT_DIR/REPO_ROOT per feature_051/A1.

## Verification

- New goldens: 5/5 green.
- Neighbors: completion_hardening + coverage_on_diff — 9/9 green.
- Boundary e2e (`test_omt_harness_e2e.py`): 1/1 green.
- `harnessc check`: 0 errors (263 records) · `build`: OK (5 projections).
- Full omt suite: 557 passed + 1 flaky live-guard (passes in isolation,
  pre-existing order-dependent); re-run of the guard file: 2/2 green.
