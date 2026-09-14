# verdict — S4 keep / merge / drop (feature_101)

> HEAD `96d319a` · S0 base `f1be918` · pins frozen per pair (HEAD + S3 contract revs) · costs PROXY-only (S1 §2) · seeded defects detection-only.

## 1. Pair table (2 classes × 3 arms, same facts + 2048B budget)

| pair | A preflight | B +frontier | C +analysis | first-useful (A/B/C) | avoided (A/B/C) | acceptance |
|---|---|---|---|---|---|---|
| routine fix | 1348B | 1600B (+252) | 1689B (+341) | 1 / 1 / 1 | 0 / 0 / 0 | pass |
| interrupted/resumed | 1676B | 1957B (+281) | 2046B (+370) | 3 / 1 / 1 | 0 / 1 / 1 | pass |

- Routine converges: B/C cost +19–25% bytes for zero avoided attempts and identical first-useful. Frontier text reproduces preflight facts (§6.6: earns no runtime).
- Interrupted shows the only directional win: B/C order blockers first (first-useful 3→1, 1 avoided re-read) at +17–22% bytes, still inside budget (C fits by 2B — tight, honest).
- Arm C's bounded analysis adds +89B (routine) / +89B (interrupted) over B for zero extra avoided attempts in these seeded demos. Cost counted, benefit absent here.
- Seeded defects (S1 classes 2–4) exercised only as detection probes (cap/stale/contradiction self-checks green). No naturally occurring avoided failures observed — economic return unproven by design (PROJECT.md §3 S4).

## 2. Verdict: MERGE

Fold the remedy into preflight, keep Petri analysis-only, retire the runtime bet:

- **Merge into preflight (ship the smaller product):** preflight/contract text should surface enabled-actions ordered by unblock-value (the B win) — a text-ordering fix in the existing single engine, not a second engine. No new tool/gate/nav record.
- **Petri stays analysis-only:** keep `frontier.py` + schema as an offline lens (dead-obligation scan, ordering audits). It never grants/authorizes, never runs live, claims no C6 execution guarantee.
- **Drop the runtime frontier:** no live advisory path, no M4/managed claim, no S5 executable closure. S5+ stays parked.

Why not keep: keep needs repeatable accepted-task benefit with setup+support payback (payback gate §5.7) + S2-green (met) + one-template C6 transition map (absent). One seeded-demo ordering win at +17–22% proxy bytes, with C adding cost for no benefit, does not repay a runtime.

Why not full drop: B's ordering win is real, cheap, and inside budget on the harder (interrupted) class. Deleting the lens loses the audit that found it. Merge keeps the win at ~0 maintenance (sidecar, no live surface).

## 3. Re-entry (keep needs ALL of these — not dates)

1. S1-full: real 6-task re-run + 8-gate matrix with natural avoided failures (not seeded) showing repeatable accepted-task benefit for B/C over A.
2. Payback math: benefit (avoided attempts × cost) > build + eval + maintenance incl. analysis/query cost metered (not proxied).
3. S5 C6 map: one template where every managed op = checked transition (projection(B)=M + invariants across pass/fail/cancel/recovery).
4. S2-green holds + live harness green throughout + presentation budget honored on natural tasks.

Without all four, the net stays a partial control abstraction with omitted behavior named (PROJECT.md §1 C6) — the roadmap's honest line, kept.
