# Test report — feature_075.completion_hardening_content_bound_evidence (T4-3)

> Date: 2026-09-12 · Task type: minor_feature · Project: meta_harness_8 (T4-3)

## Scope

Strengthen completion beyond public-method call-coverage (Improvement002 D-part):
`validate-exit` now **runs the feature's own tests** (`tests/features/<feature>/`)
and FAILS completion when they fail; the e2e receipt additionally carries a
`results` block and the guard rejects a receipt whose recorded run did not pass.

## What changed

- `scripts/omt/tdd/gates.py` — `_run_feature_tests` + `_parse_failed_nodes`;
  `cmd_validate_exit` gains the behavioral dimension (`failing_tests`,
  `summary.behavioral.{ran,failures}`); `scope:all` skip override still bypasses
  (feature_024 escape hatch untouched). No test dir → no behavioral run
  (legacy behavior unchanged).
- `.opencode/lib/enforcer/phase_gate.ts` — the completion block message now
  lists `failing_tests`.
- `.opencode/lib/omt_shared.ts` — `receiptResultsPassed()`; a receipt whose
  `results.status !== "passed"` is treated as stale (absent `results` =
  pre-075 receipt, accepted).
- `tests/scripts/omt/test_omt_harness_e2e.py` — `_write_receipt` writes
  `results:{status,checks}`; contract section 3c pins the T4-3 wiring.
- `tests/scripts/omt/test_validate_exit_coverage_on_diff.py` — hermetic
  fixture hardened for the new behavioral run (conftest sys.path + regular
  `__init__.py` package so the tmp `agentx` wins over the installed one).

## Goldens (new: tests/scripts/omt/test_completion_hardening.py, 5 tests)

| # | Case | Verdict |
|---|------|---------|
| 1 | Green feature tests → completion ok, behavioral.ran | ✅ |
| 2 | **Seeded broken behavior** (value() 1→2) fails completion, coverage/dangling clean, failing_tests names the node | ✅ |
| 3 | scope:all skip override still bypasses (flagged in summary) | ✅ |
| 4 | No test dir → legacy behavior unchanged (no run) | ✅ |
| 5 | Collection error is a behavioral failure (never silent) | ✅ |

## Suite evidence

- Focused: 65/65 (`test_completion_hardening` + `test_validate_exit_coverage_on_diff`
  + `test_tdd_check` + `test_done_baseline_regressions`).
- Boundary e2e: `test_omt_harness_e2e.py` green; receipt refreshed with
  digests + `policy_ver` + `toolchain` + `results`.
- Full suite: 2063/2064 — the only failure is the pre-existing
  `feature_059.test_tight_budgets_unchanged` budget-pin (uncommitted
  071–073 WORK.md drift, present before this feature).
- `harnessc.py check`: OK — 263 records, 0 errors. Batch staged via
  `harnessc.py stage` (T4-2 mechanism), single boundary e2e, stage cleared.
