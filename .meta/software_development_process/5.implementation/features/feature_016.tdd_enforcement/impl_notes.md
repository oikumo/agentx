# Implementation Notes — feature_016: TDD Enforcement

## What was built

A TDD enforcement engine (`scripts/omt/tdd_check.py`) that implements Kent Beck's
TDD spec (`.meta/doc/tdd/tdd-agent-spec.md`) as a Python script, integrated with
the existing `omt_enforcer.ts` gate via the same pattern as `mvc_check.py`.

## Files created

| File | Purpose | LOC |
|---|---|---|
| `scripts/omt/tdd_check.py` | TDD engine: 9 subcommands, AST analysis, pytest runner, ledger | ~470 |
| `tests/scripts/omt/test_tdd_check.py` | 29 unit + integration tests | ~250 |

## Files modified

| File | Changes |
|---|---|
| `.opencode/plugin/omt_enforcer.ts` | +5 TDD tools (omt_testlist/red/green/refactor/done), +tdd_mode in omt_phase, +TDD gate in tool.execute.before (tests/ + src/), +TDD after-edit in tool.execute.after (REFACTOR revert), +TDD validate-exit in omt_complete, +refactorSnapshots Map |
| `.opencode/plugin/omt_status.ts` | +runTddStatus() function, +TDD state section in status output |
| `tests/scripts/omt/test_omt_harness_e2e.py` | +tdd_check.py in HARNESS_FILES, +TDD contract checks (tools wired, gate present, script runs) |
| `.meta/doc/tdd/tdd-agent-spec.md` | 5 clarity fixes (FSM REFACTOR description, transition, mypy/pytest-cov optional notes, code example labels) |

## Architecture decisions

1. **Python script, not TypeScript** — AST analysis (test→target inference, true RED verification, coverage gaps, anti-pattern detection) is impossible in TypeScript. The `mvc_check.py` pattern (Python script → JSON → TS enforcer) is the proven approach.

2. **Two-hats gate** — The spec's "two_hats_never_same_time" principle makes the gate trivially simple: RED → tests/ only, GREEN/REFACTOR → src/ only. No file-level tracking needed.

3. **Fast/slow split** — `gate` subcommand (per src/ edit) is ledger-read only (~50ms). `start`/`green`/`refactor` run pytest (1-3s). `after-edit` runs pytest only in REFACTOR state.

4. **REFACTOR revert** — TypeScript before-hook saves pre-edit file content in `refactorSnapshots` Map. If after-edit Python call returns `revert_needed`, TypeScript restores the file.

5. **TDD auto-approves tests/** — When TDD mode is active, tests/ edits bypass the canary approval requirement (tests are written first in TDD, not bolted on).

## Key design points

- **`extract_test_references`** collects only method calls (`ast.Call` with `ast.Attribute` func), not bare attribute accesses — avoids false positives in true RED verification
- **`extract_public_methods`** uses `ast.iter_child_nodes` (module-level only), not `ast.walk` — avoids double-counting class methods as both class methods and top-level functions
- **`HAT_RULES`** lookup table: 6 states × 2 file types = 12 entries, entire gate logic in ~10 lines
- **Ledger sharing**: TypeScript writes phase/skip/complete records, Python writes tdd/tdd_testlist records — no conflict (append-only JSONL, different kinds)

## TDD spec compliance

| Spec feature | Implementation |
|---|---|
| FSM (TESTLIST→RED→GREEN→REFACTOR→DONE) | 5 TDD states in HAT_RULES + 5 tools (omt_testlist/red/green/refactor/done) |
| L1 (no prod code without failing test) | Gate blocks src/ in RED state |
| L2 (test = min to fail) | Anti-pattern detection: no assertions, skip/xfail |
| L3 (prod = min to pass) | AST law 3 check in after-edit: new methods not referenced by test |
| Two hats | HAT_RULES: RED→tests only, GREEN/REFACTOR→src only |
| REFACTOR micro-edit verification | after-edit runs pytest per src/ edit in REFACTOR; reverts on failure |
| violation→revert | After-hook restores pre-edit content if REFACTOR breaks tests |
| Anti-patterns | batch-N-tests, no-assertions, bad-naming, skip/xfail detection |
| Done checklist | Full suite + naming + refactor recorded + coverage gaps |
| True RED verification | AST: test method calls vs source defined names |

## Test results

- **tdd_check unit tests**: 29/29 pass
- **e2e harness test**: 1/1 pass (includes TDD contract checks)
- **Full suite**: 744/745 pass (1 pre-existing `test_llm_initialization_attempted`)
- **MVC++**: 0 errors, 6 baseline warnings
- **0 regressions**
