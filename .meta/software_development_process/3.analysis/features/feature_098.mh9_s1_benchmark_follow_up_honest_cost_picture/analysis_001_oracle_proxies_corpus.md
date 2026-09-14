# analysis_001 — S1 benchmark follow-up (honest cost picture, no policy change)

> Feature `feature_098` · HEAD `f1be918` · extends 093 (no redo) · S0 signed base.

## 1. Oracle qualification (4 seeded classes)

The 093 oracle = trial assert/verify expectations + `refused` predicate (gate-block OR deny OR engine `ok:false`/❌⛔). Qualify with seeded probes (bench-side, no production change):

| Class | Seed | Oracle must |
|---|---|---|
| valid accept | unmodified task, all verifies pass | `success=true`, `missed=0`, `regressions=0` |
| omitted behavior | remove one verify step from transcript (simulate agent skipping check) | `success=false` (assert unmet), NOT counted as gate miss |
| stale evidence / missing check | replay prior rev `3478bb2` transcript against HEAD IR (stale) | refuse as stale (revision mismatch), never accept |
| false-success rejection | inject `ok:true` with failing verify output (mock lying agent) | `success=false`; `tokens_est` still counted (cost of lie) |

Status today: classes 1–2 covered by 093 goldens; 3–4 are S1 new (bench-side transcript mutators, no IR change).

## 2. Proxies labeled (every artifact)

- `io_bytes` = Σ args+result bytes (real). `tokens_est = io_bytes // 4` (≈4 chars/token, mh3 convention) — PROXY.
- `verify_seconds` = Σ spawn durations (real). Delivered-bytes / byte-digest (092: 432B vs ~58KB reread) — PROXY for orientation win.
- No host per-call token usage exists — every economy sentence carries "proxy, not metered" label. First-numbers rev `3478bb2` ≠ HEAD `f1be918`: S1 states delta (or re-pins) before any claim.

## 3. Corpus freeze (no expansion)

6 real + 2 fixture per S0 §5 (bugfix 11, cross_layer 12, major 13, harness_repair 12, resume 7, concurrent_conflict 11; fixture_bugfix 10, fixture_nophase 7). Attempt boundaries + paired order + cold/warm separation per `analysis_001_benchmark_design.md` TA:112c–126. No expansion past 6+2–3 repeats without written rule + budget (S0 sheet holds).

## 4. Waste ranking + removal deltas (publish)

From 093 first-numbers (66 steps, 21 harness calls, io 140218B): S1 re-runs at HEAD to publish per-gate removal table (bench-side `irOverride` filters): for each of g.nav/g.protect/g.receipt/g.tests/g.net/g.phase/g.think/g.kb — saved calls/bytes (annotated `gate:<id>` steps) vs `violations_missed` (what the gate buys). 093 proved g.phase/g.tests slips (goldens #7); S1 completes the 8-gate matrix + resume orientation counterfactual.

## Exit

Repeatable native/static/current traces with honest usage fields + waste ranking + expansion rule + resource budget. No economy claim beyond labeled proxies.
