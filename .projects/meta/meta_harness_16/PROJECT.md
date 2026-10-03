# PROJECT: meta_harness_16 — Meta Harness 16

> Status: **active** · **v0.1 (2026-09-27)** — created by `project.py new`. Iterate freely (non-gated); spawn features with `new_feature.py "<name>" --type <tt> --project meta_harness_16`; log sessions in CURRENT_STATE.md (newest on top).

---

## New Session Quick Start

> One line: Unified, efficient startup menu — fast, low-token, robust — that tells the agent the exact state of the whole agentx workspace at session start; inherits mh14's startup evidence + mh15's cost-driver slices.

**Next:** Approve scope below, then spawn the first mh16 feature (proposed: adopt in-tree feature_137 trace-bound work + render-once menu) via `new_feature.py "<name>" --type <tt> --project meta_harness_16`.

---

## Summary (one line)

Synthesis of mh14 (session-start efficiency, closed-inconclusive, control kept) and mh15 (dominant cost drivers) into one product goal: an opencode startup menu that is efficient, fast, low-token, robust, and workspace-complete.

---

## Purpose

### What this project is

- **Supersedes mh14 + mh15** (both closed 2026-09-28 per user direction; history preserved in their homes, nothing moved or rewritten). mh16 takes their data and ideas to a new, unified goal.
- **The goal:** the session-startup menu must be (1) **efficient** — minimal tool roundtrips before first useful action; (2) **fast** — wall-clock cheap; (3) **low-token** — measured input-token cost, never estimated; (4) **robust** — identical D19 OptionID map, pool/lanes/staleness enforcement intact, zero gate regressions; (5) **workspace-complete** — the agent learns the *exact* state of the whole agentx project at start: all active projects, pool counts, lanes, drifts, staleness.
- **Scope = whole workspace:** every active project, the pool, verification/integration lanes, drift hygiene, and freshness vs live net — not just the start path in isolation. Today's menu-staleness bug (Options listing complete `harness_reason`, missing active mh14/15) is the founding exhibit: completeness must be mechanically guarded, and now is (`check_work_tasks_canonical` Options-drift check + `test_tasks_options_drift.py`).
- Method: `omt_session` measured (profile/compare/trace/inspect, explicit db+directory, message-incremental basis, model stratification), same honest-reporting contract as mh13/mh14.

### What this project is **not**

- Not a re-litigation of mh14 run001 (keep-control stands; lean_start_v1 stays a trial variant, not the default).
- Not allowed to cite savings until measured (no char-count estimates relabeled as measured).
- Not automatic behavior change from diagnoses; not unrecorded-reasoning reconstruction; trials remain human-launched (mh13 D7).

---

## Inheritance (data taken from 14 and 15)

- **From mh14:** 100-session baseline (median startup f2 11448 / f5 15528; session totals to 91k; peak message 127k) · keep-control/inconclusive decision (43% clean-menu saving immaterial vs typical sessions; ≈11× model drift muse vs glm) · `lean_start_v1` swap mechanism (`scripts/omt/lean_start_swap.py`, feature_135) · JSON-arg transport hardening (`argvValue`, feature_136, shipped in-tree) · `[mh13.experiment]` label protocol · run001 manifest/labels as reusable trial harness.
- **From mh15:** three ordered slices — (1) trace caps (in-tree: `feature_137.trace_bounded_paging` + `tests/scripts/session_inspect/test_trace_bounded_paging.py`, adopted as first mh16 work item); (2) render-once menu (tool output + agent relay paid twice; 1093-char tool body + 883-input call turn evidence); (3) compaction-aware resume (build on feature_092 `resume_digest`; cache_read to 3.6M dominates long sessions).
- Ledger history stays where it is (features remain linked to their closed projects); adoption under mh16 happens by new link records when work resumes, never by rewriting.

---

## Scope & success criteria

- **Menu cost:** measured first-5-assistant input reduction vs the 11.4k median-startup baseline, with identical OptionID map + zero enforcer/gate regressions + model-stratified reporting (materiality judged vs session totals, not just clean menus).
- **Workspace completeness:** menu always reflects live state — active-project set (drift-guarded by the Options check shipped today), pool, lanes, drift hygiene, freshness; a stale menu is a check failure, not a silent regression.
- **Trace/inspect bounded by default** (adopt feature_137: ≤2KB default + paged rest, digest-bound `detail_ref`, replay stable).
- **Resume cheap:** compaction/resume sessions pick up the same next task at a measured fraction of today's re-read cost.
- Success: at least one slice ships with measured saving + zero regressions; otherwise keep current behavior (mh14 rule carries over).

---

## Status

- [ ] First linked feature (header flips draft → active mechanically) — proposed: trace-bound adoption (feature_137) and/or render-once menu
- [x] mh14 closed (complete; superseded) — `.projects/meta/meta_harness_14/`
- [x] mh15 closed (complete; superseded) — `.projects/meta/meta_harness_15/`

---

## Decisions log (locked — do not re-litigate without new evidence)

- **D1 — Evidence-first (inherits mh13/mh14):** all token claims measured from the session DB via `omt_session`; model-stratified; no estimates relabeled.
- **D2 — No run001 re-litigation:** mh14 keep-control stands; lean stays a variant.
- **D3 — Human-launched trials only (mh13 D7):** no auto-run; `run` stays gated.
- **D4 — Workspace scope:** completeness covers every active project + pool + lanes + drifts + freshness; staleness is a mechanical check failure.

---

## References

- mh14: `.projects/meta/meta_harness_14/PROJECT.md` + `CURRENT_STATE.md` (run001, model drift, 100-session baseline) · `run001_manifest.json` + `run001_labels.jsonl` · `scripts/omt/lean_start_swap.py`
- mh15: `.projects/meta/meta_harness_15/PROJECT.md` (three slices) · in-tree `feature_137.trace_bounded_paging`
- Founding regression guard: `scripts/omt/harnessc.py::_tasks_options_proj_drift` · `tests/scripts/omt/test_tasks_options_drift.py`
- Startup spec: `.meta/META_HARNESS.omt` · `AGENTS.md` §STARTUP · `WORK.compiled.md` · `omt_session` (9 ops) · `omt_net` probe
