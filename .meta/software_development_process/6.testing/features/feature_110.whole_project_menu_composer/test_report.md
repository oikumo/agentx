# Test Report: O1 Whole-Project Menu Composer

> **Phase:** Programming → Testing — `omt_agent_guide.md §11` | **Feature:** feature_110.whole_project_menu_composer (minor_feature, project meta_harness_11)
> Run everything with `uv ...` (AGENTS.md MANDATORY — no bare python/pip/pytest).

## Scope

O1 renders one whole-project menu (pool counts + Projects + drift/hygiene + unscoped 001/002 with stable IDs, D19 ordering + rev-stamp) via pure `sync_md` render + `state.sync net_to_md` threading. Out of scope: O2 multi-select grammar, O3 claim handles, O4 dispatch, O5 live view, O6 bridge (still serial).

## Stage 1 — Unit / component (new goldens `tests/scripts/omt/test_net_menu_o1.py`, 14 tests)

| Component | Normal path | Exception / edge | Result |
|-----------|-------------|------------------|--------|
| compose_menu_options (proj/drift/unscoped stable IDs, sorted) | dict + list forms | empty inputs → [] | [x] 2/2 |
| lanes_line (verification/integration + deadlocks + blocked) | full line | None → None | [x] 2/2 |
| render_tasks_block O1 (empty enabled → NEXT first option; enabled wins; lanes appended; D19 order) | drained f001 + bootstrap + lanes | non-pool net has no Pool line | [x] 3/3 |
| menu_lines O1 (empty enabled → NEXT option + Options + Lanes + rev-stamp) | full menu | — | [x] 1/1 |
| state helpers (projects slug-sorted; unscoped PENDING-only; lanes None/dict; hygiene fail-open sorted) | hermetic WORK.md | missing WORK.md → [] | [x] 5/5 |
| sync dry-run threading (menu counts + rendered Options, no write) | bootstrap→splice→dry-run | — | [x] 1/1 |

## Stage 2 — Integration

- Targeted: e2e + O1 goldens + sync_md/menu/sync/state → [x] 43/43 (14 new + 28 existing + 1 e2e).
- Budget trim (user-approved): persisted Tasks block keeps `Options:` IDs line + `Lanes:` line only — 30 per-option checklist rows dropped (labels stay in `compose_menu_options`). 11562 → 9507 B.
- Budget growth (user-approved, same commit): `.omt @budget work_md` 8704 → 9728 + `test_omt_docs_drift_pins.py` WORK_BUDGET pin 8704 → 9728 + `harnessc build` (5 projections).
- `harnessc check` → [x] 265 records, 0 errors. `harnessc build` → [x] OK (work_md 9507/9728).

## Stage 3 — System (use-case driven)

- Live `sync net_to_md --dry-run` rev 60 renders `NEXT: proj:agentx_concurrent_development (recommended)` + 19 proj + 9 drift + 2 unscoped + `Lanes: verification 0/1 free 1, integration 0/1 free 1`.
- Live `sync net_to_md` (non-dry-run) applied → WORK.md Tasks is the whole-project menu (idempotent re-render).
- Full suite: [x] 1817 passed, 1 failed — `test_plugins_load_and_tools_execute` (live opencode run TimeoutExpired after 240 s, infra/LLM flake, unrelated to O1; skip-tally live-smoke 131 known-flaky).

## Evidence

```
$ uv run pytest tests/scripts/omt/test_omt_harness_e2e.py tests/scripts/omt/test_net_menu_o1.py tests/scripts/omt/test_net_sync_md.py tests/scripts/omt/test_net_menu.py tests/scripts/omt/test_net_sync.py tests/scripts/omt/test_net_state.py -q
43 passed in 2.90s

$ uv run scripts/omt/harnessc.py check
harnessc: check OK — 265 records, 0 errors

$ uv run scripts/omt/harnessc.py build
harnessc: build OK — 265 records → 5 projections (work_md 9507/9728 OK)

$ uv run pytest -q
1 failed, 1817 passed in 466s — sole failure live-smoke TimeoutExpired (infra flake)
```

## Non-interference

No places/transitions added (Tier-3 excludes net); helpers fail-open; hermetic env overrides respected; TA gotcha `sync_md.py:138` honored (no hand rows between Pool and ## Projects).
