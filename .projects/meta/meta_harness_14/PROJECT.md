# PROJECT: meta_harness_14 — Meta Harness 14

> Status: **active** · **v0.1 (2026-09-27)** — created by `project.py new`. Iterate freely (non-gated); spawn features with `new_feature.py "<name>" --type <tt> --project meta_harness_14`; log sessions in CURRENT_STATE.md (newest on top).

---

## New Session Quick Start

> One line: Make the meta-harness opencode **session start** cheap and disciplined — minimal input tokens, fast path to first useful action, productivity gates preserved — proven with `omt_session` evidence (mh13).

**Next:** run001 pilot — 8 human-launched trials. Mechanism shipped: `uv run scripts/omt/lean_start_swap.py --variant control|lean_start_v1` (flips the SESSION STARTUP line of `.agents_prompts/build.md`; control is byte-pinned; restore after each trial). Labels: `.projects/meta/meta_harness_14/run001_labels.jsonl`. Collect → decide per decision rule.

---

## Summary (one line)

Evidence-driven reduction of per-session startup token cost of the AGENTS.md STARTUP protocol, with a labeled A/B experiment whose trials are launched by the user starting real opencode sessions.

---

## Purpose

### What this project is

- Continuation of the meta-harness self-evolution line: **mh13** (complete, feature_131–134) shipped `omt_session` — session DB inspection + labeled experiments. mh14 spends that capital on the most frequent harness path: **session start**.
- Three sub-goals: (1) **efficiency** — fewer tool roundtrips before the user can act; (2) **minimal token consumption** — measured, not estimated; (3) **productivity enforcement** — gates/pool/lanes/staleness still firmly communicated; no enforcement regression is acceptable as a side effect of the diet.
- Method: baseline measurement via `omt_session` → probe variants (STARTUP md-swap and/or experiment test plugin) → human-launched labeled trials → collect/validate → decide.

### What this project is **not**

- Not an automated live launch: per mh13 **D7**, auto-run is gated (`no_safe_launch`) and stays so. The launcher of mh14 trials is **the user starting sessions** (explicit, per-trial).
- Not a general session-mid-cost optimization project; scope is the start path (first ≈5 assistant messages).
- Not allowed to cite token savings until the pilot is actually collected (mh13 honest-reporting contract: no claims from un-executed pilots).

---

## Current startup protocol (baseline, as of net rev 60)

Per `AGENTS.md` STARTUP (GENERATED from `.meta/META_HARNESS.omt`): read `WORK.compiled.md` header + one `omt_net` brief probe + render via `startup_table` tool → = **3 tool roundtrips before the user can act** (read + probe + startup_table), each returning JSON the model then re-renders as user text (double token cost).

## Baseline evidence (2026-09-27, omt_session live analysis)

- **F1 — corpus:** 1,863 sessions total, 1,730 in this repo directory, DB 3.3 GB (`~/.local/share/opencode/opencode.db`). Gotcha: `omt_session` default `directory="/repo"` silently returns 0 rows / `source_unreadable` without explicit `db` — always pass both.
- **F2 — in-session growth dwarfs but doesn't exempt start cost:** `ses_f1b6cb…` startup ≈ 879–1,973 incremental input tokens, peak message 25,318; `ses_f1bc7169…` peak message **127,075** input. Start protocol pays out in *every* fresh session; compaction/resume sessions re-pay it.
- **F3 — the tool itself leaks tokens:** `trace` is unbounded (one session → 388 events + 152-part skeleton ≈ 50 KB JSON). Fellow sub-improvement: cap/page trace like `inspect` does.
- **F4 — menu cost is structural:** GLOBAL+TASKS+SUGGESTED text is rendered twice (tool body + agent relay) at every start.

## Scope & success criteria

Experiment **run001** (`experiment= mh14_session_start_token_cost`):

- Cases: `fresh_session_menu` (user opens session, replies a letter), `known_task_resume` (user picks NEXT).
- Variants: `control_current_agents_start` vs `lean_start_v1` (single probe + direct plain-text render; no `startup_table` roundtrip; header-only WORK read).
- Reps: 2 → **8 trials**, human-launched, labels in first user message (`[mh13.experiment]` protocol, mh13).
- **Success:** ≥30% reduction of cumulative input tokens over the first 5 assistant messages (measured via `compare`/`profile`, not estimated) AND identical menu OptionID map AND zero enforcer/gate regressions. Failure to meet reduces to "keep control".

---

## Status

- [x] First linked feature (header flips draft → active mechanically) — feature_135.lean_start_v1_variant
- [ ] run001 pilot collected + decision recorded

---

## Decisions log (locked — do not re-litigate without new evidence)

- **D1 — Evidence-first via `omt_session`:** all token claims measured from the session DB (mh13 contract: no char-count estimates relabeled as measured).
- **D2 — Human-launched trials only:** user starts each opencode session; no automated `run` (mh13 D7 honored; `run` → `no_safe_launch` untouched).
- **D3 — Probe mechanism:** reversible config-swap of the STARTUP block in `.meta/META_HARNESS.omt` + `harnessc build`, or experiment plugin under `.opencode/plugins/`; control = current AGENTS.md as-is; restore after each trial.
- **D4 — Label protocol:** `[mh13.experiment] {v,experiment,run,trial,case,variant,rep,attempt,event}` as first user-message line (mh13 protocol); attribution by label, never by session title.
- **D5 — Swap surface = `.agents_prompts/build.md` SESSION STARTUP line only** (iter 1, feature_135): that `{file:}` include (opencode.jsonc:12) is the system-prompt surface that produced the measured 3-roundtrip start; swapping the `@doc startup` line instead would grow AGENTS.md past `@budget agents_md` (3511/3584 → only 73 B headroom) and change a second surface (`.meta/META_HARNESS.omt` → all projections), contaminating single-factor attribution. AGENTS.md "Show ..." is render-agnostic — no conflict; control vs lean differ in exactly one line. Pinned constants + drift-guard tests keep "control" honest.

---

## References

- mh13: `.projects/meta/meta_harness_13/PROJECT.md` (label protocol, D7, AC6 un-executed pilot) · `scripts/session_inspect/`
- Startup spec: `.meta/META_HARNESS.omt` (doc boots, comp.session @ line 201) · `AGENTS.md` §STARTUP · `WORK.compiled.md`
- Tool: `omt_session` (9 ops) · `startup_table` tool · `omt_net` probe
- Iter 1 (feature_135): `scripts/omt/lean_start_swap.py` · `tests/features/feature_135.lean_start_v1_variant/` · `run001_manifest.json` + `run001_labels.jsonl` (this dir)
