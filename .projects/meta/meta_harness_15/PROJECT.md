# PROJECT: meta_harness_15 — Meta Harness 15

> Status: **active** · **v0.1 (2026-09-27)** — created by `project.py new`. Iterate freely (non-gated); spawn features with `new_feature.py "<name>" --type <tt> --project meta_harness_15`; log sessions in CURRENT_STATE.md (newest on top).

---

## New Session Quick Start

> One line: Attack the session-cost drivers that dwarf startup — capped/paged traces, render-once menu, compaction-aware resume — measured via `omt_session`, not estimated.

**Next:** Approve scope below, then spawn feature_1 (trace caps, read-only, highest leverage) via `new_feature.py`.

---

## Summary (one line)

Evidence-driven reduction of per-session token cost beyond startup, continuing mh14's 100-session baseline (median startup 11.4k, session totals to 91k, traces ~100KB) with the same honest-reporting contract.

---

## Summary (one line)

<!-- -->

---

## Purpose

### What this project is

- Continuation after mh14 (closed-inconclusive, control kept): mh14 proved the `startup_table` roundtrip saving (~718 tokens / ~43% in clean menus) is immaterial vs typical sessions (median startup 11.4k, session 91k, peak 127k). mh15 attacks the drivers that dominate the 100-session baseline.
- Three slices, ordered by leverage × risk: (1) **trace caps** — `trace` is unbounded (349/391/332-entry skeletons, 92–111KB JSON in 3 sampled sessions); cap/page like `inspect` does; read-only, no behavior change. (2) **render-once menu** — control startup pays tool output (1093 chars) + agent relay (~1.5k chars) + 883-input call turn; render once with identical D19 OptionID map + pool/lanes/staleness preserved. (3) **compaction-aware resume** — build on feature_092 `resume_digest`; cheap digest vs full re-read for resume/compaction sessions that dominate totals (cache_read to 3.6M).
- Method: `omt_session` measured (profile/compare/trace/inspect), same contracts as mh13/mh14 (explicit db+directory, message-incremental basis, model stratification, no char-count relabeled as measured).

### What this project is **not**

- Not a startup-protocol re-run (mh14 closed that); not allowed to cite savings until measured on labeled or stratified historical captures.
- Not a reconstruction of unrecorded reasoning; not automatic policy/source changes from diagnoses.

---

## Scope & success criteria

- Slice 1 (trace caps): bounded `trace` (cap + cursor, stale-cursor semantics like `query`) with byte-size evidence (before ~100KB → after ≤2KB default + paged rest) and zero information loss (digest-bound `detail_ref`, replay stable).
- Slice 2 (render-once): identical OptionID map + zero gate regressions with measured first-5-assistant reduction on clean menus; materiality check vs 11.4k median startup reported honestly.
- Slice 3 (resume digest): measured resume-turn saving on compaction sessions with quality held (same next-task pickup).
- Success: at least one slice ships with measured saving + zero regressions; otherwise keep current behavior (mh14 rule carries over).

---

## Scope & success criteria

- Slice 1 (trace caps): bounded `trace` (cap + cursor, stale-cursor semantics like `query`) with byte-size evidence (before ~100KB → after ≤2KB default + paged rest) and zero information loss (digest-bound `detail_ref`, replay stable).
- Slice 2 (render-once): identical OptionID map + zero gate regressions with measured first-5-assistant reduction on clean menus; materiality check vs 11.4k median startup reported honestly.
- Slice 3 (resume digest): measured resume-turn saving on compaction sessions with quality held (same next-task pickup).
- Success: at least one slice ships with measured saving + zero regressions; otherwise keep current behavior (mh14 rule carries over).

---

## Status

- [ ] First linked feature (header flips draft → active mechanically) — proposed first: trace caps (read-only)

---

## Decisions log (locked — do not re-litigate without new evidence)

- **D1 — Evidence-first (inherits mh13/mh14):** all token claims measured from session DB via `omt_session`; model-stratified; no estimates relabeled.
- **D2 — Slice order trace → render-once → resume:** trace is read-only highest-leverage (~100KB/inspection); render-once reuses mh14 evidence but must pass materiality; resume builds on feature_092.
- **D3 — No startup re-litigation:** mh14 keep-control stands; this project does not reopen run001.

---

## References

- mh14 baseline: `.projects/meta/meta_harness_14/CURRENT_STATE.md` (2026-09-28 ×3: 4-trial, today-startup drift, 100-session baseline) + `PROJECT.md` F1–F4
- 100-session numbers: median f2 11448 / f5 15528; st_true 11120 vs st_false 11863; muse 71 vs glm 26 (median 11760 vs 1288)
- Trace samples (2026-09-28): `ses_f1af94…` 349-skeleton/97KB, `ses_f1bc71…` 391/111KB, `ses_f1aa41…` 332/92KB via `trace.timeline`
- Tool: `omt_session` (trace/inspect/profile/compare) · `startup_table` output 1093 chars + 883-input call turn (rep02 evidence)
