# CURRENT_STATE: meta_harness_14

> Session-by-session log + resume point. Companion to `PROJECT.md` (canonical).
> Newest entry on top. One `## <date>` block per session.

---

## 2026-09-27 (auto — feature_135.lean_start_v1_variant Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_135.lean_start_v1_variant/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-27 (iter 1 — lean_start_v1 variant mechanism shipped)

### Done

- Feature **feature_135.lean_start_v1_variant** spawned + linked (project draft→active); `omt_phase` Programming (minor_feature).
- Swap mechanism implemented: **`scripts/omt/lean_start_swap.py`** — reversible single-surface config-swap on the SESSION STARTUP line of `.agents_prompts/build.md` (variants: `control` byte-pinned | `lean_start_v1` = control + `LEAN_START_V1` marker + direct-render clause forbidding the `startup_table` roundtrip). `.meta/META_HARNESS.omt` + `AGENTS.md` byte-identical across variants (AGENTS.md budget headroom only 73 B → OMT-swap would bust `@budget agents_md`; AGENTS.md "Show" is render-agnostic so no conflict).
- 5 unit tests green (`tests/features/feature_135.lean_start_v1_variant/`): pinned-control drift guard, single-factor delta proof (strip-variant == control), byte-identical roundtrip, idempotence, unknown-content refusal (exit 2, no write).
- Live roundtrip proven on the real repo: control → lean (`harnessc check` OK, projections untouched) → control → `git diff` clean on all three surfaces.
- run001 persisted: `.projects/meta/meta_harness_14/run001_manifest.json` (canonical; 2 cases × 2 variants × 2 reps = 8 trials, decision rule locked) + `run001_labels.jsonl` (8 rendered `[mh13.experiment]` first-message label lines).

### In progress / Blocked

- Pilot not launched (mh13 D7: human-launched only). No token claims yet (mh13 honest-reporting contract).

### Next

- User launches the 8 trials: for each trial — `uv run scripts/omt/lean_start_swap.py --variant control|lean_start_v1` to match the trial's variant → start a fresh opencode session whose first user message is the matching label line from `run001_labels.jsonl` (+ a reply letter for `known_task_resume` trials) → `--variant control` restore. Collect via `omt_session experiment collect/validate` (db + explicit directory, F1 gotcha), then `compare` → decide per decision rule.

### Notes / context

- Surface decision recorded as PROJECT.md **D5** (evidence: 73 B budget headroom; `{file:}` include in opencode.jsonc:12 is the actual system-prompt surface).
- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.

## 2026-09-27 (iter 0 — project created)

### Done

- Project home created (`project.py new`, state: draft); `omt_phase` Analysis declared (docs).
- Baseline live analysis via `omt_session` (PROJECT.md F1–F4): corpus 1,730 sessions in repo dir (3.3 GB DB); default `directory="/repo"` returns 0 rows — pass explicit db+directory; trace op unbounded (~50 KB/session); startup protocol = 3 tool roundtrips + double menu render.
- Experiment **run001** planned + dry_run validated via `omt_session experiment plan/dry_run`: 2 cases × 2 variants × 2 reps = **8 trials**, human-launched, `[mh13.experiment]` labels in first user message; `executed:false` (no auto-launch, mh13 D7).
- PROJECT.md canonical proposal written (scope, success criteria ≥30% input-token cut, D1–D4).

### In progress / Blocked

- Waiting on user `go` to implement variant `lean_start_v1` and start pilot trials.

### Next

- On user `go`: spawn feature(s) (`new_feature.py … --project meta_harness_14`), implement lean variant (config-swap or experiment plugin), run the 8 labeled trials with user-started sessions, collect + decide.

### Notes / context

- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.
