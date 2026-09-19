# Analysis 001 — O5 live progress projection (scope for approval)

> Feature: `feature_113.live_progress_projection` (`minor_feature`, project `meta_harness_11`) · Phase: Analysis · Date: 2026-09-19.
> Resumes: PROJECT.md §Plan O5 + gaps doc G4/G14 + O1 Done (feature_110, rev 60 whole-project menu) + O2 Done (feature_111, atomic apply) + O3 Done (feature_112, claim handles).

---

## 1. Problem (reproducer)

Menu-time freshness missing, fire-time only:

- Live rev 60 `drained_complete`, `enabled:[]`, `menu {next:none, other:[], blocked:[], resources 4/4 free}`, `coverage anonymous 7/7`. WORK.md `Tasks` carries `<!-- net_rev:60 -->` + `NEXT: proj:agentx_concurrent_development (recommended)` + 19 `proj:` + 9 `drift:` + 2 `unscoped:` + `Lanes:` (O1).
- `fire` / `claim_task` / `apply_selection` enforce `expected_revision` fire-time (`stale_revision` refuse + re-render hint, `_require_revision` in `state.py:642`). The menu itself has no freshness guarantee at render time: `cli._probe` returns `menu` from loaded state without auto `probe`/`sync` before present, and `state.sync net_to_md` re-render is caller-initiated (cold start, post-fire manual).
- Reproduce: session A + B both present WORK.md rev 60 menu → A `fire/claim` at rev 60 bumps to rev 61 → B fires at `expected_revision=60` → `stale_revision` refuse only at fire time (G4). Loser discovers staleness late; no pre-present `probe` forces fresh menu.
- No live view during execution: feature_043 dashboard is static-build only (explicit non-goal: no live view). During multi-task work user has only next cold-start WORK.md render — no revision slider / deadlock highlight / marking view (G14).

Reproduce: `sync net_to_md` at rev 60 → `fire/work_claim` (rev 61) → WORK.md still shows `net_rev:60` until next manual `sync`; `probe` shows new marking but menu text stale; no live projection reuses studio view.

## 2. What O5 must prove (oracle)

- **Menu-time freshness (`probe` before present):** presenting the whole-project menu always pairs a fresh `probe` (rev R, marking, `menu.claims`) with the rendered `Tasks` block. If `WORK.md net_rev != live rev`, present refuses or auto `sync net_to_md` first (same D19 stale pattern as O2/O3, extended to present scope). No new places/transitions (Tier-3 excludes net); `src/agentx/` untouched (D1).
- **Re-render push after each fire/claim:** `fire`, `claim_task`, `release`, `apply_selection` return (or trigger) a `sync net_to_md`-equivalent re-render record (`net_revision`, `menu` counts, `Tasks` text) so WORK.md never lingers one rev behind. Fail-open helpers only; single-mutate bound kept (`multi_mutate_deferred_o4` still O4); no silent auto-commit (D4 proposal-only — caller applies).
- **Minimal live view reusing studio projection:** read-only projection reusing `tools/petri-net-studio` or `sync_md` pure render (marking + deadlocks + lanes + claims) — revision slider / deadlock highlight where cheap, static fallback otherwise. No second adapter/SDK/remote/distributed/timed/colored (out-of-scope per PROJECT.md).
- **Ordering + stamp preserved:** D19 `NEXT / Other / Blocked / Resources` + `Options:` + `Lanes:` + `<!-- net_rev:R -->` round-trip through freshness check + push; stale-R present/fire refuses with fresh menu.
- Out of scope: worktree dispatch/join/WIP runtime (O4, needs F7 reversal), agentx bridge + directive→fragment synthesis (O6, needs D1 revisit), bulk multi-mutate.

## 3. Resource budget

- Code: pure helper (e.g. `scripts/omt/net/freshness.py` or `sync_md.py` additive: `menu_freshness(live_rev, stamped_rev)` + `render push` composer, stdlib-only, no net I/O) + thin threading in `state.py` (`sync` freshness field, `fire/claim/apply_selection` re-render record via existing `sync` path) + CLI `probe` freshness display (additive fields only). No new places/transitions; no `src/agentx/` changes.
- Tests: new goldens `tests/scripts/omt/test_net_fresh_o5.py` (stale-menu present refuses, fresh present passes, fire returns re-render record, push preserves D19 + rev-stamp, live view pure render) — needs tests/ canary approval; e2e receipt per harness-surface round discipline (one edit per file per receipt).
- Runtime: one `probe` before present + one `sync net_to_md` equivalent after each mutating op; no background loop (push is return-value, not daemon).

## 4. Next (Design → code)

- `omt_phase{minor_feature, Design}` → freshness grammar + push record shape (pure) + `probe`/`fire`/`sync` threading points + golden list → Programming (helper + threading, receipt-disciplined) → `omt_complete{advance_to:Testing}` + test report.
