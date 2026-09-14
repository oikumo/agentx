# test_report — feature_101 S4 frontier experiment (read-only, sidecar only, verdict MERGE)

> HEAD `96d319a` · Analysis `analysis_001_frontier_experiment.md` · Design `design_001_frontier_schema.md` · zero live-surface edits
> (`.meta/*.omt`, `.opencode/**`, `scripts/omt/net/**`, `tests/` untouched).

## 1. Overlap gate (no re-implementation)

- 072/073/092 + 055/062 + S3 projection reused live/sidecar as-is (single obligation engine; `blocked`/`first_blocker` equal contract — asserted per pair, contradiction injector detected).
- 070–075/079–096 stand (mh8 CLOSED 31/31). S1 oracle/proxy/corpus + S2 parity inputs reused, not re-run.
- S4 adds ONLY: advisory frontier schema + sidecar paired harness + 2 pairs × 3 arms + `verdict.md` (MERGE). No new tool/gate/nav record, no writer/store/authority.
- Flagged, not papered over: 072/073 `6.testing` reports absent on disk (reused code, certified nothing); S1-full deferred (no removal-delta claims); C6/C1 open (no execution/replay claim).

## 2. Sidecar (`.sandbox/frontier/`)

| File | Role |
|---|---|
| `frontier.py` | pure-stdlib advisory: `build_frontier` + arm renders (A/B/C, 2048B cap + continuation) + `check_invariants` + pair metrics (PROXY-labeled) + self-check `main` (cap/stale/contradiction probes) |
| `pair_a_routine_fix.{json,A/B/C.txt}` | routine: A 1348B / B 1600B / C 1689B, first 1/1/1, avoided 0/0/0 — converges, B/C cost more for zero benefit |
| `pair_b_interrupted_resumed.{json,A/B/C.txt}` | interrupted: A 1676B / B 1957B / C 2046B, first 3/1/1, avoided 0/1/1 — B/C order blockers first at +17–22% bytes, inside budget (C fits by 2B) |
| `verdict.md` | MERGE: fold enabled-ordering into preflight text; Petri stays analysis-only; runtime bet retired; keep re-entry needs S1-full natural wins + payback + C6 map |

Cap semantics (092/S3 precedent): bounded text is the capped surface; `frontier[0]` + `unknowns` (parity/proxy/C6/C1) never dropped; over-cap drops detail tail → completed tail → line-boundary hard-cut with marker. Stale rev appends re-render UNKNOWN and refuses commit-readiness.

## 3. Evidence

```
$ uv run python .sandbox/frontier/frontier.py
== pair_a_routine_fix: A 1348B / B 1600B / C 1689B blocked=False
== pair_b_interrupted_resumed: A 1676B / B 1957B / C 2046B blocked=True
S4 sidecar OK: 2 pairs × 3 arms ≤2048B, invariants + cap + stale + contradiction probes green

$ uv run python .sandbox/work_contract/contract.py
== demo_a_routine_fix: 1348B text / 1703B json blocked=False first=None
== demo_b_interrupted_resumed: 1676B text / 2109B json blocked=True first=g.receipt
S3 projection OK (S4 fact source unchanged)

$ uv run scripts/omt/harnessc.py check → 265 records, 0 errors (before AND after)
$ uv run scripts/omt/harnessc.py build → 265 → 5 projections OK
$ uv run scripts/omt/task_cost_benchmark.py run --task fixture_nophase
  → success=true, violations_missed=0, tokens_est=559 (S1 baseline held)

$ uv run pytest -q
2241 passed, 10 warnings in 139.95s (0:02:19)
```

Invariants asserted per pair×arm: closed verbs; `blocked`/`first_blocker` equal contract (no second engine); candidate `@rev`; all 4 required UNKNOWNs in text; arm B/C consistent with arm A facts; costs carry PROXY labels; arm C analysis cost counted in its render bytes.

## 4. Verdict check (exit criterion)

- Paired results published with frozen pins + all five metrics (first-useful, avoided, recovery, acceptance, cost).
- MERGE applied honestly: routine reproduces preflight text (earns no runtime per §6.6); interrupted ordering win is real but small, proxy-costed, and seeded — it repays a text-ordering fix, not a runtime. Keep would need S1-full natural wins + payback + C6 map (all absent, listed as re-entry).
- No economy claim beyond proxies; no authority/execution claim (C6 explicitly not claimed); S5+ stays parked.

## 5. Result

PASS — paired read-only experiment ends in a written MERGE verdict with re-entry math; live harness green throughout (`check` 0 + `build` OK + bench unchanged + suite 2241/2241). Ready for `Done`. mh9 S0–S4 complete; S5+ parked per §4.
