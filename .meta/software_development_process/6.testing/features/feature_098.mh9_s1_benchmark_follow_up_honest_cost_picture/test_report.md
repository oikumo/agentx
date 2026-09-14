# test_report — feature_098 S1 benchmark follow-up (measurement, no policy change)

> HEAD `f1be918` · fixture re-baseline at HEAD · real first-numbers carried with delta note.

## Fixture re-baseline at HEAD (oracle valid-accept holds)

| task | steps | harness_calls | TP/FP/missed | io_bytes | tokens_est (PROXY) | success |
|---|---|---|---|---|---|---|
| fixture_nophase | 7 | 2 | 2/0/0 | 2238 | 559 | true |
| fixture_bugfix | 10 | 2 | 2/0/0 | 2586 | 646 | true |

Oracle class 1 (valid accept) GREEN at HEAD; violations caught (TP=2 each, missed=0).

## Removal deltas (what each gate buys, fixture_nophase)

| removal | TP/missed | io_bytes | Δ vs baseline 2238B | success |
|---|---|---|---|---|
| baseline | 2/0 | 2238 | — | true |
| --remove g.phase | 1/1 | 1875 | -363B (-91 tokens_est PROXY) | false |
| --remove g.tests | 1/1 | 2253 | +15B noise (≈0 saved) | true (leaking) |

Reading: g.phase costs ~363B to catch 1 no-phase slip; g.tests catches 1 canary slip for ~0 saved bytes (ceremony is the test itself — removal stays "successful but leaking" per TA:120 success semantics). Full 8-gate matrix + real-mode re-run deferred to S1-full (needs worktree pre-warm); this smoke proves repeatability at HEAD.

## Proxies labeled

All `tokens_est` = `io_bytes // 4` (mh3 convention) — PROXY, not metered. No host per-call token usage exists. First-numbers real run pinned at `3478bb2` (66 steps, 21 calls, io 140218B, TP=13/FP=0/missed=0) ≠ HEAD — delta stated here, no economy claim past proxies.

## Oracle classes 2–4

- omitted behavior (skip verify → success=false, not gate miss): covered by 093 success semantics (TA:120).
- stale evidence (replay `3478bb2` transcript at HEAD): S1 rule = refuse as stale (revision mismatch) — bench-side mutator proposed, not yet run.
- false-success (`ok:true` + failing verify): S1 rule = success=false, cost still counted — mutator proposed.

## Result

PASS (smoke) — honest cost picture holds at HEAD; expansion rule + budget unchanged (S0 sheet). Ready for `Done`. S1-full (real 6-task re-run + 8-gate matrix) is follow-on, not blocking S2/S3.
