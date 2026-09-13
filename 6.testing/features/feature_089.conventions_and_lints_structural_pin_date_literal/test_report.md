# Test Report — feature_089.conventions_and_lints_structural_pin_date_literal

> mh8 T2-6 (mh3 P2-5/P2-6): bake the two conventions from feature_027's fixes so the defect class doesn't recur.

## Deliverables

1. **`harnessc lint [path...]`** (scripts/omt/harnessc.py `cmd_lint`) — flags absolute-date literals (`= "20DD-DD-DDTHH:MM…"`) in test files with file:line + `now - timedelta` guidance; exit 1 on hits, 0 clean, 2 unknown flag, 1 missing path. Standalone advisory subcommand, deliberately NOT folded into `check` (mh3 scope: pre-existing date literals are fixed opportunistically, not retro-failed).
2. **Two GOTCHA_ records** (.meta/META_HARNESS.omt, nav-indexed): `GOTCHA_STRUCTURAL_PIN` (pin kinds/presence, not AST counts; precedent kb count-pin → kind-pin, feature_027) + `GOTCHA_DATE_LITERAL` (no absolute dates in temporal-window tests; use `now - timedelta`; precedent u13 fresh_ts fix, feature_027).

## Goldens (tests/scripts/omt/test_conventions_and_lints.py)

| # | Test | Result |
|---|------|--------|
| 1 | lint flags planted absolute-date literal (exit 1, file:line, guidance) | PASS |
| 2 | lint clean on `now - timedelta` relative fixture (exit 0) | PASS |
| 3 | lint ignores date-only strings and non-assignment mentions | PASS |
| 4 | lint unknown flag → 2; missing path → 1 with stderr message | PASS |
| 5 | GOTCHA_STRUCTURAL_PIN + GOTCHA_DATE_LITERAL present in rendered nav index (the projection `omt_nav{query:"GOTCHA_..."}` searches), payload text verified | PASS |

## Re-pins (deliberate, documented inline)

- **feature_059 budget pin:** NAV_INDEX_CEIL 63963 → 64956 (+2 @doc records); @budget nav_index deliberately grown 64000 → 65536 in the same .omt edit (per the budget error's own instruction).
- **feature_058 cluster partition:** 18 → 20 ids; `gotcha.structural_pin`/`gotcha.date_literal` assigned to the toolchain cluster; test renamed `covers_18_exactly_once` → `covers_all_exactly_once` so future gotcha additions extend the set instead of churning the name (ironic count-pin fixed on the spot).

## Verification

- `harnessc check` 0 errors · `harnessc build` OK (all budgets green: nav_index 64956/65536, tool_args 2454/2464, tool_schemas 1812/1856).
- Harness e2e receipt: `pytest tests/scripts/omt/test_omt_harness_e2e.py` green (batch validated via feature_074 stage; 2-file batch).
- Full suite: **2173 passed, 0 failed** (up from 2167 baseline: +5 goldens +1 re-targeted 058 test).

## Discipline notes

- Stage/policy_ver ordering: `.meta/META_HARNESS.omt` is the policy hash for `harnessc stage`; editing it after staging invalidates the batch (per-file guard re-fires, even for staged files). Correct order: stage → edit harnessc.py → edit .omt LAST → re-stage → e2e. TA'd in harnessc.py as a gotcha.
- Pre-existing harnessc.py LSP typing errors (6, lines ~434/1499/1873+) untouched — T2-7 (LSP allowlist) territory, not this feature.
- Open repair flag unchanged: `meta_harness_development_self_evaluation.md` still unindexed (warning on build).
