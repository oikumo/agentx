# Analysis 001 — O6c wild payback measurement (scope for approval)

> Feature: `feature_116.mh11_o6c_wild_payback_measurement` (`minor_feature`, project `meta_harness_11`) · Phase: Analysis · Date: 2026-09-20.
> Resumes: PROJECT.md Next O6 (needs D1 revisit) + gaps doc G15/G16 + feature_093 benchmark design + feature_098 honest-cost + MH11 M0/M1 SHIPPED (suites 1847→1880, rev 60 `drained_complete`).

---

## 1. Problem (reproducer)

O6 bridge cannot be estimated: neither side owns execution state, and no number proves M0/M1 concurrency pays back.

- **G15 split:** harness WIP-pool holds counts only (`pending=0/active=0/done=7`, `enabled=[]`, `drained_complete` rev 60); agentx adaptive net (`feature_001` scope unset, D1 forbids `src/agentx/`, `USER_OBJECTIVES.md`, `internal_state`) holds no execution net either. Selection "do rag_v2 + studio fix concurrently" has no spanning net — reproduce: `probe` rev 60 + `omt_q{drift}` hygiene vs `## Projects` 3 active — same divergence O1 closed for menu, still open for execution ownership.
- **G16 no metric:** 093 measures harness cost per task type (first numbers, removal experiments, `tokens_est=io_bytes//4`) but never ran wild multi-pick concurrency; 098 honest-cost exists but no N≥10 wild payback. WORK.md Paused residual "(a) needs wild sessions N≥10" is still open. Reproduce: M1 O4 dispatches hermetically (23 goldens) with zero wild evidence.

## 2. What O6c must prove (oracle)

- **Metric (093/098 reuse, no policy change):** per wild session — wall-time, `harness_calls`/`tool_calls`, `io_bytes` + `tokens_est`, `verify_seconds`, `success`/`regressions`, `check`/`build`/suite cost; serial baseline vs O4 dispatch (fan-out ≤2, F7 lane-only) on disjoint files. Honest-cost method from 098; transcript accounting from 093; production `.opencode/`/`.meta/META_HARNESS.omt`/`opencode.jsonc` untouched.
- **Protocol (N≥10, sidecars only):** pinned-rev worktree or fixture sandbox per run (093 §Architecture reuse); disjoint files; harness green throughout (`check 0` + `build` OK + suite + KNOWN empty; net-zero holds; Tier-3 excludes net; no new places/transitions; no new `net_*` kind; `src/agentx/` untouched — D1 locked); each run logs reproducer/oracle/budget + outcome in CURRENT_STATE + test report.
- **Pre-registered threshold:** payback (time and tokens, no green loss) → O6a contract-only (read-only D1 exception, directive→042 template map) or O6b full prototype (D1 reversal + `major_feature` TDD); no payback → defer O6, take WORK.md NEXT `proj:agentx_concurrent_development`. Decision recorded, not re-litigated without new evidence.

## 3. Resource budget

- Code: none in this slice (metric doc + protocol doc + run log template only). Measurement runs reuse `scripts/omt/bench/` driver/probe; no new harness surface, no e2e receipt round.
- Tests: no new `tests/` goldens in Analysis/Design (wild runs are evidence, not goldens; any later hermetic pin needs tests/ canary approval).
- Runtime/token: N≥10 wild sessions, each bounded (one dispatch batch, ≤2 workers, verification/integration lanes as available); `.omt @budget work_md` watched — run logs stay out of WORK.md.

## 4. Out of scope

- O6a contract (USER_OBJECTIVES ↔ fragment, directive→042 synthesis) and O6b prototype (`src/agentx/` edits, D1 reversal) — O6c only decides which, if any, pays.
- Revision slider, live sockets, second adapter/SDK/remote/distributed/timed/colored nets; bulk multi-mutate outside dispatch lane (O2 bound stands); CLI `dispatch --expected-revision` commit (O4 deferred stays deferred).

## 5. Next (Design → measurement)

- `omt_phase{minor_feature, Design}` → metric table + run-log template + threshold values + first 2 pilot runs → Programming (pilot analysis, no `src/` change) → `omt_complete{advance_to:Testing}` + test report (N results + decision O6a/O6b/defer).
