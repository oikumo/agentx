# Implementation Notes: feature_091.budget_diet_bot

> mh8 T3-7 / mh7 P1-4 · minor_feature · shipped 2026-09-13

## What changed

- `scripts/omt/harnessc.py` — new section `feature_091 T3-7 budget-diet-bot`
  after `measure_budgets` (~85 lines):
  - `BUDGET_DIET_PROXIMITY = 64` — headroom at/below which the diet fires.
  - `per_tool_arg_bytes(c)` — per-tool live TS arg-describe() byte sums
    (mirror of the `measure_budgets` scan; separate so the pinned measure
    path + `test_tool_args_budget_measures_live_describes_only` stay untouched).
  - `diet_longest_contributors(c, nav_text)` — longest single contributor per
    composable budget: arg describes (tool_args), payload (tool_schemas),
    longest nav line (nav_index); ties break lexicographically.
  - `budget_diet_warnings(sizes, longest)` — pure core: warn—never error—while
    headroom ∈ [0, 64]; message carries `free ≥N B` (N = 65 − headroom) and the
    contributor, or the generic trim-or-grow hint; over-cap stays the generic
    error loop's job; gates/cap-None/size<0 out of scope.
  - `check_budget_diet(c, sizes, nav_text)` — thin wiring onto `c.warnings`.
  - `run_all_checks` gains one call after the past-cap error loop → both
    `check` and `build` print the warnings.
- `tests/scripts/omt/test_budget_diet.py` — 9 goldens: pure-core (near-cap
  suggestion, 64/65 boundary, at-cap, over-cap silence, scope exclusions,
  labels + generic hint, sorted multi-budget), wiring (synthetic corpus,
  hermetic via monkeypatched arg scan; lexicographic tie-break), live pin
  (three firing budgets + two silent ones, 2026-09-13 numbers).
- Dogfooded feature_090's `new_feature.py testing/implementation` scaffolders
  for this file pair.

## What did NOT change (deliberately)

- `measure_budgets` + past-cap error loop — untouched (pinned surface).
- No `.omt` edit — warning-only feature; no budget grew; projections
  byte-identical (`build` OK, 265 records).
- `.meta/lsp_allowlist.json` — the 6 pre-existing harnessc.py pyright
  diagnostics were verified at HEAD and left UNLISTED: suppressing
  reportCallIssue/reportArgumentType/reportOptionalMemberAccess/reportReturnType
  file-wide on the most-edited harness file would hide genuine new type
  errors (static-allowlist tradeoff). Documented in test_report instead.

## Discipline notes

- Receipt batch (T4-2): `harnessc.py stage --feature feature_091…` BEFORE the
  first harnessc.py edit → both edits inside the batch → boundary e2e
  (`test_omt_harness_e2e.py`) green → `stage --clear`. No .omt in the batch,
  so the feature_089 stage/policy_ver chicken-and-egg did not apply.
- Tests canary recorded per D6 (phase re-declared first); KB consult attempted
  ("budget"/"harnessc" → no records — scripts surface has no app-KB contract);
  think-gate consult done (stage ordering gotcha noted and followed).
- Live state at ship: tool_args 2454/2464 (10B), agents_md 2918/2944 (26B),
  tool_schemas 1812/1856 (44B) inside the zone; nav_index 580B, ir_json 401B
  silent. The three firing warnings are the feature working as intended —
  these caps are genuinely tight after features 078–090.
