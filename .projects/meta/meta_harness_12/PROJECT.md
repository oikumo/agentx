# PROJECT: meta_harness_12 — Meta-Harness Toolbox (Evolutionary Live Tool System)

> Status: **draft** · **v0.1 (2026-09-21)** — created by `project.py new --slug meta_harness_12` from `.sandbox/meta_harness_toolbox_idea.md` (proposal, 2026-09-21). Iterate freely (non-gated); spawn features with `new_feature.py "<name>" --type <tt> --project meta_harness_12`; log sessions in CURRENT_STATE.md (newest on top).

---

## New Session Quick Start

> One line: toolbox/ turns ad-hoc `uv run scripts/omt/*.py` into a named, categorized, sqlite-queryable, approval-gated growing tool layer (bash→python, 5 seed tools first).

**Next:** PAUSED 2026-09-21 — next session: apply F fix (Vision/Adaptive/Size&risk) → execute approved T1 → propose T2. Resume via `.sandbox/pause_2026-09-21_mh12.md`.

---

## Summary (one line)

**Session-start awareness → mid-session `query → run` ≤2 calls → encounter-propose → approve-promote → metered `run` next session with prune.**

---

## Purpose

### What this project is

- The **sole execution home** for the toolbox proposal (`.sandbox/meta_harness_toolbox_idea.md`, 218 lines): `toolbox/` subsystem — one SQLite index + one folder of versioned tools — wrapping/indexing (never re-implementing) enforcers (`omt_net`/`omt_tdd`/`omt_q`).
- Lineage: mh8 R2 (0 wins, healthy) + `meta_harness_session_usecase_gaps.md` G1–G16 + mh6 eval D1 tiered template. Answers G7/O1 (categories join menu composer), G5/G6/O2 (per-tool directives via `run -- args`), mh6 D1 (Tier-1 payload).
- Contract: each tool = `toolbox/<cat>/<name>/run.sh` (bash: `set -euo pipefail`, `uv`-only, arg parsing, env guards) + `main.py` (argparse, JSON `{"ok":…, "data":…}` to stdout) + `TOOL.md` (≤15-line contract). Index: `toolbox/index.sqlite3` (SSOT, `tools/categories/usage_log/proposals/toolbox_meta` + FTS) + generated `index.json` projection. CLI: `scripts/toolbox/toolbox.py query/list/show/run/propose/promote/prune/stats/sync`.
- Seed taxonomy (T1: rehome proven one-liners, no new logic): `git.*` (status_summary, recent_log), `ledger.*` (window_slice, drift_scan), `harness.*` (budget_check, nav_lookup), `text.*` (json_split, frontmatter_get), `session.*` (pause_note_append). Growth: encounter → `propose` (sqlite staged + `.sandbox/toolbox_proposals/<name>.md`) → user pick → `promote` (scaffold + pytest + `index.json` rebuild + `kind:toolbox_promote` ledger) → `prune` (>90d / uses==0 → `deprecated_by` → remove, `kind:toolbox_prune`).

### What this project is **not**

- NOT a 13th gate (B1 net-zero holds: consults advisory, enforced only via existing `g.nav/g.think/g.kb/g.net` on `src/`/`tests/`/`.opencode/`/`scripts/omt/`); NOT auto-skip/auto-run/self-modifying/network tools; NOT a replacement for `omt_*` enforcers; NOT `src/agentx/` runtime dispatch (D1/G15 holds — harness-side ops first, agentx bridge O6-later); NOT touching protected paths (`.env*`, `uv.lock`, `README.md`, `LICENSE` without `omt_skip{scope:all}`), bare `python/pip/pytest`, or `git push/pull/fetch/remote/clone`.

---

## Scope & success criteria

**Scope:** T1 index+query → T2 run+metering → T3 propose/promote/prune → T4 docs+tiers (each `minor`, one approval per slice; Later O4/O6 concurrent/agentx bridge = `major`, only after T1–T3 + G12/F7 decision).

**Success:**

1. T1: `toolbox/` layout + schema + 5 rehomed seeds; `query` ranked, `sync --check` detects stale rev; STARTUP 1-liner (≤120B) + `omt_status` `toolbox: rev=<r> tools=<n>`; budgets green.
2. T2: 5 seeds runnable via `run`; `usage_log` + `stats` counted; TOOL.md lint 0 errors.
3. T3: staged→approved→promoted e2e for 1 pilot (pytest RED→GREEN via `omt_tdd`); reject leaves index untouched.
4. T4: `categories.md` gen, per-tool docs, `harnessc` tier map (T1 core-5, T2/3 full); onboarding builds.
5. Fresh-review rule: next review shows a repeat-failure class eliminated (candidate: ad-hoc script re-invention across ≥2 features) with `uses`/`successes` evidence, else no follow-up tool.

**Out of scope:** second adapter/SDK/remote/distributed/timed/colored/self-modification; P2-style enforcement before T1–T3 evidence; any Git/publication allowance change.

---

## Status

- [x] v0.1 (2026-09-21): created (`project.py new --slug meta_harness_12`, state: draft) from toolbox idea doc; this PROJECT.md drafted (non-gated iterate).
- [x] Scoping pick (step 4→5, 2026-09-21): V assumed on "continue project" (no explicit letter; recommended full T1→T4: 5 rehomed seeds, checked-in sqlite + `index.json`, keep `text.*`, stats at T4). W/X/Y remain available on re-pick.
- [ ] Plan approval (step 6 — awaiting user): T1 plan below.
- [ ] T1 execution (step 7, one approval per slice).

---

## Plan — T1 (this approval; T2–T4 queued, one approval each)

**T1 index + query (minor, read-only):** `toolbox/` layout + `schema.sql` + built `index.sqlite3` (checked-in + WAL) + generated `index.json` + 5 rehomed seeds (each `run.sh`+`main.py`+`TOOL.md`, no new logic: `git.status_summary`, `ledger.window_slice`, `harness.budget_check`, `text.json_split`, `session.pause_note_append`) + `scripts/toolbox/toolbox.py query/list/show/sync --check` + STARTUP 1-liner (≤120B) + `omt_status` `toolbox:` field (Tier-aware omit on minimal).
Files: `toolbox/*`, `scripts/toolbox/toolbox.py`, `tests/scripts/toolbox/test_query.py` (pytest, canary `omt_skip{scope:tests}` per RED-hat rule). Acceptance: `query` ranks seeds; `sync --check` detects stale rev; budgets green; `invariant` drift 0. Rollback: delete `toolbox/` + revert STARTUP/status line (index rebuild from `index.json`).
Queued (separate approvals): T2 run+metering (`run` + `usage_log` + `stats` + TOOL lint) → T3 propose/promote/prune (1 pilot e2e, pytest RED→GREEN via `omt_tdd`) → T4 docs+tiers (`categories.md`, per-tool docs, `harnessc` tier map).

---

## Decisions log (locked — do not re-litigate without new evidence)

- **D1 — `src/agentx/` stays out (mh6 D1/G15 holds):** toolbox serves harness-side ops first; agentx bridge is O6-later. Rationale: proposal §3 non-goals + §12.
- **D2 — Gate count stays 12 (B1 net-zero):** toolbox advisory only. Rationale: proposal §9.
- **D3 — uv-only + deny list carries over:** no bare python/pip/pytest, no network, no `*.env` reads, no push/fetch/clone. Rationale: proposal §6/§9.
- **D4 — Growth is approval-gated, ≥2 uses (or 1 + general-use tag) to promote:** stops one-off bloat. Rationale: proposal §8.
- **D5 — Fresh-review evidence required for follow-up tools:** `uses`/`successes` must show eliminated re-invention class. Rationale: proposal §12.

---

## References

- Proposal: `.sandbox/meta_harness_toolbox_idea.md` (218 lines, 2026-09-21; §§1–13: summary/use-case/goals/arch/layout+schema/contract/discovery/growth/safety/slices/example/prior-art/open-questions A–D).
- Gaps: `.sandbox/meta_harness_session_usecase_gaps.md` (G1–G16, O1/O2/O6 context from mh11).
- Prior: `.projects/meta/meta_harness_11/PROJECT.md` (M0–M2 closed, F7 lane-only, D1 locked), `.projects/meta/meta_harness_8/` (T1–T5 shipped), mh6 D1 tiered template (`feature_059`).
- Workflow: `.workflows/meta_harness/loops/meta_harness_project.md` (steps 1–7; this session at step 4).
