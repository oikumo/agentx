# Test Report: MH10 P1 Global Projection (feature_102)

> **Phase:** Testing — `omt_agent_guide.md §11` | **Feature:** feature_102.mh10_p1_global_projection (`minor_feature`, project `meta_harness_10`)
> Run everything with `uv run ...` (AGENTS.md MANDATORY). Sidecar only: `.sandbox/global_state/` + docs; no live gates/tools/budgets (net-zero holds).

## Stage 1 — Unit / component (builder)

| Component | Check | Result |
|---|---|---|
| `build.py --format md` renders advisory banner + per-section as-of, no global as-of (R3) | header lines present | [x] pass |
| ≤2KB cap, line-cut continuation, never mid-sentence | `projection.md` 1994B ≤2048, ends `… continued in projection.json (cap 2KB; cut at line boundary)` | [x] pass |
| Join keys + C4 residual named, never interpolated (R3) | `join:unmatched` line in md | [x] pass |
| Derived-row marking (R5) | `## projects (derived sync rows — never source)` | [x] pass |
| Workflow honesty (R5) | catalog subjects + last `.sandbox/` round pointer only, zero-machine-state note | [x] pass |
| Loss labeled | footer `Loss: prose truncated, labeled` + json `loss` key | [x] pass |
| R2 non-dependence | `rg src/agentx .sandbox/global_state/build.py` → no hits; stdlib + `net_check.py probe` facts only | [x] pass |
| R6 no-new-store | outputs are files (`projection.md/json`, `divergence.md`, `snapshots/` copies); no DB/writer migration | [x] pass |
| Divergence rows (C6/C1 named) | B-vs-M agree line + omission paths `state.py:819-834,837+` + absent-lane `:296-300 vs fire() :763-768` + crash `:730-742 vs WAL :672-675` | [x] pass |

## Stage 2 — Integration (facts join)

- Probe rev 57 `drained_complete` (done=7/pending=0/active=0, resources 5/5, workers 0/2, NEXT none) + WORK.md pool + `.projects/meta/META.md` derived rows + ledger tail (2 phase records, 1 project_link) joined; pool(B) vs marking(M) 0/0, 0/0, 7/7 agree with no fired transition = OMISSIONS — [x] pass
- `projection.json` carries full rows (`md_continued: true`); `divergence.md` (876B) carries long-form B-vs-M rows; `snapshots/` holds 3 timestamped mds + current json — [x] pass

## Stage 3 — System (R4 blind demo, falsifiable protocol)

- Protocol: fresh sessions working blind (projection + checklist only, no source peeking). Borrowed from S1 oracle-qualification; demo classes routine + interrupted/resumed per analysis_001 §5.
- Demo (a) routine-orient from `projection.md` alone (actual file, 1704B pre-fix build): 7/7 — pool 0/0/7, NEXT none, active `meta_harness_10 · feature_102`, rev 57 @ `f66d268d4682`, resources 5/5 + workers 2/2 free, continuation → `projection.json`, advisory banner — [x] 7/7
- Demo (b) interrupted-resume from full render (pre-fix): 8/8 — resume target, B-vs-M agree + no firing, omission paths + crash window with file:line, join keys + C4, workflow honesty, per-section as-of, derived rows — [x] 8/8
- Honesty probe (pre-fix `projection.md` alone, truncated after project rows): 7/11 — divergence/join/workflows cut by the cap (items 8–11 FAIL, continuation pointer PASS). Finding → R4 fix applied (see below), re-built 1994B.
- Demo (c) retest on FIXED `projection.md` alone (1994B, actual file): **13/13** — pool, NEXT, active project+feature, rev+HEAD, resources/workers, continuation, advisory banner, omission path + file:line, crash window + file:line, join keys + `join:unmatched`, workflow round pointer, derived label, per-section as-of — [x] 13/13
- Verdict: R4 PASS from ≤2KB md alone (bundle `divergence.md`/`projection.json` corroborates; no silent drops — cut rows labeled via continuation, unknown stays unknown).

## Evidence

```
$ uv run scripts/omt/harnessc.py check
harnessc: check OK — 265 records, 0 errors   # before AND after (budgets tool_args 2455/2464, schemas 1840/1856, agents_md 2918/2944, nav 64990/65536, gates 10/12 unchanged)

$ uv run scripts/omt/harnessc.py build
harnessc: build OK — 265 records → 5 projections   # before AND after

$ uv run .sandbox/global_state/build.py
projection.md 1994B (≤2KB) + projection.json + divergence.md  # rev 57 @ f66d268d4682, drained_complete

$ uv run scripts/omt/net_check.py probe
rev 57, marking work_pending=0/work_active=0/work_done=7, observation drained_complete, menu NEXT none/resources 5/5/workers 0/2

$ uv run pytest -q
1739 passed, 7 warnings in ~130-145s (0 failures)   # before fix AND after fix (sidecar-only change; live surfaces untouched)
```

## Finding fixed this session (was red in the pre-fix blind probe)

1. Cap-cut dropped resume-critical sections (divergence/join/workflows) behind 10 project rows → `render_md` reordered critical-first (tasks → divergence compact 3 lines → join keys → workflows → features → projects active-first with `+N more` truncation) + `_short_features` helper. Full rows unchanged in `projection.json`; `divergence.md` long-form unchanged. Re-verified: md 1994B ≤2KB, blind retest 13/13, `check` 265/0 + `build` OK + suite 1739 green after. No live surfaces touched (`.sandbox/` + this report only); net-zero 10/12 intact; no `omt_*` registration (P2 parked).
