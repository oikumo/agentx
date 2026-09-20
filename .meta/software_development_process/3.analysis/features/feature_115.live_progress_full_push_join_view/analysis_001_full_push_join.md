# Analysis 001 — O5a+b full push plus join view (scope for approval)

> Feature: `feature_115.live_progress_full_push_join_view` (`minor_feature`, project `meta_harness_11`) · Phase: Analysis · Date: 2026-09-20.
> Resumes: PROJECT.md Next O5-follow-up + feature_113 test report residuals + feature_114 operation_spec_001 (dispatch commit deferred, probe `plan[]` preview only) + gaps doc G4/G14 + O1 D19 render + O4 F7 lane-only lock.

---

## 1. Problem (reproducer)

O5 (113) shipped freshness + push skeleton but left two measured residuals (test_report.md §Residual):

- **Empty `tasks_block`:** `cli.py:356` (`_probe`), `:377` (`_fire`), `:408` (`_apply_selection`), `:442` (`_task_envelope`) all call `state.push_for_state(st, "", …)` with `rendered=""`; `state.py:670` defaults `rendered=""`; `freshness.push_record` supports text but the caller never supplies it. Reproduce hermetically: bundle at rev R → `fire(work_start, expected_revision=R)` → envelope `push == {net_revision:R+1, menu:{…}, tasks_block:""}`; WORK.md still shows `net_rev:R` until a manual `sync net_to_md`. `test_net_fresh_o5.py` pins `push.net_revision` but never asserts non-empty text.
- **Text-only view, no join:** `projection_lines(rev, marking, enabled, lanes, claims_summary)` renders one `rev R | marking {…} | enabled […]` line plus optional lanes/claims strings. It never consumes `dispatch_runtime.plan_to_dict` (batch_id, per-task worktree/lease, WIP) nor `deadlocks_complete/conflicts[]/holders[]`. Reproduce: hermetic 2-claim O4 plan → `plan_to_dict` has `tasks:[{claim,task_id,lane,worktree,lease}] + batch_id + wip` while `projection_lines` for the same rev shows none of it; `probe.plan[]` previews the batch but the projection does not.

## 2. What O5a+b must prove (oracle)

- **O5a full-text push (D4 proposal-only kept):** every mutating envelope (`fire`, `claim_task`, `release`, `apply_selection`, `dispatch_claims` join) returns `push {net_revision:R', menu counts, tasks_block: rendered}` where `rendered` is the dry-run `sync_md.render_tasks_block` compose at R' (same D19 `NEXT/Other/Blocked/Resources + Options + Lanes + <!-- net_rev:R' -->` the live `sync net_to_md` writes). `rendered` round-trips through `parse_tasks_block`; stale-R still refuses `stale_revision` with the fresh-menu hint. Empty text occurs only fail-open (render error → `""` plus reason, never a break). No auto-commit: the caller still applies via `sync net_to_md` (D4); push is a proposal.
- **O5b join/batch progress view (read-only):** a pure deterministic composer over `plan_to_dict` + live marking + lanes + conflicts/holders renders batch progress lines: `batch {id} rev R lanes {v/i/g} wip {p/a/cap}` + per-task `{task_id lane worktree lease}` in code-point order + `deadlocks_complete/blocked:*` summary. No daemon, no socket, no TS studio import (D5 boundary kept — doc-pointer reuse only); existing `projection_lines` shape stays backward-compatible (additive overload/fields only).
- **Invariants:** no new places/transitions (Tier-3 excludes net); no new `net_*` ledger kind (reuse `net_claim/net_fire/net_sync`); `src/agentx/` untouched (D1); `src/` edit serialism unchanged (O4 F7 lane-only lock holds — this slice adds no fan-out); `uv` only; receipt one-edit-per-file-per-e2e.

## 3. Resource budget

- Code: `freshness.py` additive (push-text composer passthrough + batch projection helper, stdlib-only, no net I/O) + `state.py` thin threading (post-op dry-run `sync` compose fail-open inside `push_for_state` call sites; join-view composer over `plan_to_dict`) + `cli.py` additive display (`push.tasks_block` full text + `projection` batch lines). No `model.py` change; no overlay custom keys (P10).
- Tests: new goldens `tests/scripts/omt/test_net_followup_o5.py` (push text round-trips D19 + rev-stamp; stale still refuses; batch view deterministic/ordered; fail-open empty; Tier-3 no-new-places) — needs tests/ canary approval; e2e receipt per harness-surface round (pure → state → cli); targeted + full suite green; `check 265/0` held.
- Runtime/token: one dry-run `sync` compose per mutate (bounded text; watch `.omt @budget work_md` — full text grows envelopes, re-check pin); no background loop.

## 4. Out of scope

- CLI `dispatch --expected-revision` commit subcommand (O4 deferred) — this slice only projects its plan/join; the commit path stays deferred unless O4 re-opens it.
- Revision slider interaction, live sockets, second adapter/SDK/remote/distributed/timed/colored nets; agentx bridge + directive→fragment synthesis (O6, needs D1 revisit).
- Bulk multi-mutate outside the dispatch lane (O2 bound stands).

## 5. Next (Design → code)

- `omt_phase{minor_feature, Design}` → push-text threading points + batch projection shape (pure) + golden list → Programming (helper + threading, receipt-disciplined, canary-gated goldens) → `omt_complete{advance_to:Testing}` + test report.
