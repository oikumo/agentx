# test_report — feature_100 S3 thin work contract (read-only projection, sidecar only)

> HEAD `3490fd5` · Analysis `analysis_001_thin_contract.md` · zero live-surface edits
> (`.meta/*.omt`, `.opencode/**`, `scripts/omt/net/**`, `tests/` untouched).

## 1. Overlap gate (no re-implementation)

- 072/073/092 + 055/062 reused live as-is (`policy_decision.ts`, `task_prep.ts`,
  `omt_status{op:resume}`, `preflight.ts`); S3 adds only the projection schema +
  sidecar renderer + 2 demos + parity note. No new tool/gate/nav record.
- Flagged, not papered over: 072/073 `6.testing` reports absent on disk
  (ledger Done, live code present) — S3 reuses the code, certifies nothing
  about the missing reports.

## 2. Sidecar (`.sandbox/work_contract/`)

| File | Role |
|---|---|
| `contract.py` | pure-stdlib renderer: schema assembly + 2048B text cap + continuation + `check_invariants` + DEMO_A/B + self-check `main` |
| `demo_a_routine_fix.{json,txt}` | routine fix: 0 open obligations → `edit` + base evidence; 1348B text / 1703B json |
| `demo_b_interrupted_resumed.{json,txt}` | interrupted/resumed: stale rev `f1be918`→`3490fd5`, 2 open (g.receipt first) → `clear g.receipt`; 1676B text / 2109B json |
| `parity_note.md` | S2-live-change record + block-agrees/shape-UNKNOWN parity + S1/C1/C6 labels |

Cap semantics (092 precedent): the bounded text view is the capped surface
(both demos fit: 1348B / 1676B ≤ 2048B); `next_action` + `stale_or_unknown`
(incl. the 4 required UNKNOWNs: parity, proxies, C6, C1) never dropped;
over-cap drops `detail_refs` tail → `completed` tail → line-boundary hard-cut
with marker (never mid-sentence). Demo-B JSON (2109B) carries the full
structure for the stale-revision case; its orienting read (1676B text) is capped.

## 3. Evidence

```
$ uv run python .sandbox/work_contract/contract.py
== demo_a_routine_fix: 1348B text / 1703B json blocked=False first=None
== demo_b_interrupted_resumed: 1676B text / 2109B json blocked=True first=g.receipt
S3 projection OK: 2/2 demos orient from projection alone, cap + invariants hold

$ uv run scripts/omt/harnessc.py check → 265 records, 0 errors (before AND after)
$ uv run scripts/omt/harnessc.py build → 265 → 5 projections OK
$ uv run scripts/omt/task_cost_benchmark.py run --task fixture_nophase
  → success=true, violations_missed=0, tokens_est=559 (S1 baseline 2238B → 559 held)

$ uv run pytest -q
2241 passed, 10 warnings in 139.34s (0:02:19)
```

Invariants asserted per demo: `blocked == preflight.would_block`,
`first_blocker` identical (single engine), `next_action` verb in the closed set
(`clear/edit/run/consult/ask-user`), all 4 required UNKNOWNs present in text,
stale-revision entry injected when render rev ≠ dispatch rev (demo B).

## 4. Orient-from-projection check (exit criterion)

- Demo A alone answers: what (null-check fix), where (`summary.py@3490fd5`),
  next (`edit` + repro + targeted suite), unknowns (parity/proxy/C6/C1) — no
  PROJECT.md/CURRENT_STATE.md re-read needed for the decision.
- Demo B alone answers: where-resume (`gate_driver.ts`, stale `f1be918` → re-render
  at `3490fd5`), what-blocks (g.receipt first, g.tests second + exact clears),
  next (`clear g.receipt`), unknowns preserved — interrupted session resumes
  without re-reading full docs; follow-ups are bounded partial reads via refs.

## 5. Result

PASS — one bounded read-only task view over shipped substrate; 2-task demo
orients from projection alone; parity note ships dry/live + proxy/C1/C6 labels;
live harness green throughout (`check` 0 + `build` OK + bench unchanged + suite
2241/2241); no economy claim beyond proxies; no authority claim; S5+ stays
parked. Ready for `Done`. Next: S4 paired frontier experiment.
