# Test Report: Budget Diet Bot

> **Phase:** Testing — `omt_agent_guide.md §11` | **Feature:** feature_091.budget_diet_bot
> Run everything with `uv run pytest ...` (AGENTS.md MANDATORY).

## Stage 1 — Unit / component
| Component | Normal path | Exception paths | Result |
|-----------|-------------|-----------------|--------|
| `budget_diet_warnings` (pure core) | near-cap (headroom 10) fires with full suggestion: contributor label + bytes + `free ≥55B` (need = 65−headroom) + grow-cap alternative | boundary 64 fires / 65 silent; at-cap 0 fires; over-cap silent (generic past-cap error owns it); gates (count) / cap-None / TS-pinned (size<0) never fire | [x] |
| `budget_diet_warnings` labels | tool_schemas names longest `@tool … payload`; nav_index names longest `nav record #N`; no-contributor budgets get the generic `trim, or grow the cap deliberately` hint; multi-budget render sorted | tie-break: equal contributors → lexicographically first (max over sorted) | [x] |
| `diet_longest_contributors` | tool_args from `per_tool_arg_bytes` (live TS scan), tool_schemas from corpus payloads, nav_index from longest nav line | empty inputs → absent entries → generic hint | [x] |
| `check_budget_diet` (wiring) | synthetic 2-`@tool` corpus + near-cap tool_schemas → one `c.warnings` line naming the longer payload | hermetic via monkeypatched `per_tool_arg_bytes` (no live TS read) | [x] |
| Live integration | `harnessc.main(["harnessc.py", "check"])` rc=0 with the three live diet warnings; nav_index/ir_json silent | — | [x] |

## Stage 2 — Integration
`check_budget_diet` wired into `run_all_checks` after the past-cap error loop →
both `check` and `build` print the warnings (shared stderr path). `measure_budgets`
and the pinned measure path (`test_tool_args_budget_measures_live_describes_only`)
deliberately untouched — `per_tool_arg_bytes` is a separate mirror scan.

Live CLI output (2026-09-13, after wiring):

```
harnessc: warn: budget-diet: agents_md 2918/2944B — 26B headroom (≤64B) — trim, or grow the cap deliberately in the same .omt edit
harnessc: warn: budget-diet: tool_args 2454/2464B — 10B headroom (≤64B) — diet: longest @tool omt_net arg describes 657B; free ≥55B (or grow the cap deliberately in the same .omt edit)
harnessc: warn: budget-diet: tool_schemas 1812/1856B — 44B headroom (≤64B) — diet: longest @tool omt_net payload 376B; free ≥21B (or grow the cap deliberately in the same .omt edit)
harnessc: check OK — 265 records, 0 errors
```

## Stage 3 — System (use-case driven)
Use case: "next grow-vs-trim decision has a concrete diet target" — the live
`tool_args` warning names `omt_net` (657B describes) and quantifies the exit
(≥55B), turning the implicit 10B-from-cap state into an actionable signal.

## Evidence

```
$ uv run pytest tests/scripts/omt/test_budget_diet.py -q
.........                                                                [100%]
9 passed in 0.29s

$ uv run pytest
================ 2207 passed, 10 warnings in 162.25s (0:02:42) =================
```

Baseline 2198 + 9 new goldens, 0 failures. `harnessc check` 0 errors, `build`
OK (265 records, projections unchanged — warning-only feature, no .omt edit).
Boundary e2e receipt refreshed (`test_omt_harness_e2e.py` 1 passed) for the
staged harnessc.py batch, then stage cleared.

### Live pins (deliberate re-pin when budgets move)
`tests/scripts/omt/test_budget_diet.py::test_live_check_emits_diet_warnings`
pins tool_args 2454/2464 · agents_md 2918/2944 · tool_schemas 1812/1856 firing
and nav_index 64956/65536 · ir_json 20079/20480 silent (feature_059 pin
discipline — growing any of these budgets requires re-pinning the test).

### Incidental observations (not fixed here, by design)
Editing `scripts/omt/harnessc.py` surfaces 6 pre-existing pyright diagnostics
(434 reportCallIssue/reportArgumentType, old-1499 reportOptionalMemberAccess,
old-1873 reportReturnType, old-1897/2004 reportCallIssue — verified present at
HEAD via `bun x pyright` on `git show HEAD:…`). Deliberately NOT added to
`.meta/lsp_allowlist.json`: suppressing those codes file-wide on the
most-edited harness file would hide genuine new type errors (the static
allowlist tradeoff). Candidate follow-up if the noise proves costly.
