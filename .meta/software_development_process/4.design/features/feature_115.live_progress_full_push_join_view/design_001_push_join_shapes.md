# Design 001 — O5a+b full push plus join view (threading + shapes)

> Feature: `feature_115.live_progress_full_push_join_view` (`minor_feature`) · Phase: Design · Date: 2026-09-20.
> Consumes: Analysis 001 + O5 `freshness.py`/`push_for_state`/`projection_lines` + `sync_md.render_tasks_block` (D19 + rev-stamp) + O4 `plan_to_dict` + `plan_dispatch_view` + O1 `_menu_*` helpers + D4 (proposal-only, locked).

---

## 1. O5a push text (D4 proposal-only, fail-open)

**Shape (unchanged, now filled):** `push == {net_revision:R', menu:{…}, tasks_block: rendered}` — same `push_record` dict; `tasks_block` goes from always-`""` to the dry-run `sync net_to_md` Tasks text. Consumers treating `""` as absent keep working.

**Composer (new, `state.py`, fail-open):** `_render_push_text(st) -> str` — in-memory dry-run compose only:

- Inputs from the live `NetState`: `net, live_marking, overlay, resources (resource_report), conflicts`, `revision`, plus menu inputs via the existing O1 `_menu_projects/_menu_hygiene/_menu_unscoped/_menu_lanes` helpers (same call path `sync net_to_md` uses, minus writes/ledger).
- Body is one `sync_md.render_tasks_block(…)` call wrapped in try/except → `""` on any error (fail-open; never break fire/claim).
- No lock, no I/O, no ledger kind, no overlay mutation (P10 — overlay stays derived).

**Call sites (harness-surface, one edit per file per e2e receipt):**

1. `state.py`: `fire`, `claim_task`, `release`, `apply_selection`, `dispatch_claims` post-commit replace `push_for_state(st, "", menu)` with `push_for_state(st, _render_push_text(st), menu)` (lazy import, fail-open preserved). `menu` counts unchanged (additive only).
2. `cli.py`: no format change — envelopes already forward `push_for_state`; they now carry text automatically. `probe` (read-only) also pairs the same dry-run text so menu-time present == live R'.
3. `sync_md.py`: untouched (D19 + rev-stamp already; gotcha at `sync_md.py:138` honored — push never writes WORK.md, the caller still applies via `sync net_to_md`).

**Budget guard:** rendered is the existing Tasks block (~1–2KB); push rides envelopes only (not a ledger kind), so ledger/budget impact is stdout + goldens; `.omt @budget work_md` re-checked after goldens (9711/9728 at Design).

## 2. O5b join/batch view (pure, read-only)

**New pure helper (`freshness.py`, stdlib-only, no I/O):**

```ebnf
plan        := plan_to_dict shape ;
batch_line  := "batch " batch_id " rev " R " lanes " v "/" i "/" g " wip " p "/" a "/" cap ;
task_line   := "task " task_id " [" lane "] " worktree " " lease ;
tail_line   := "deadlocks_complete" | "blocked:" ids ;
```

- `batch_projection_lines(plan, marking?, lanes?, conflicts?) -> list[str]`: batch line + per-task lines in planner order (verification, integration, general-by-task_id code-point — same comparator as `plan_dispatch`) + optional tail (`deadlocks_complete`, `blocked:{…}` from lanes/conflicts/holders). Deterministic; malformed/empty plan → `[]` (fail-open).
- `projection_lines` keeps its existing first lines byte-identical (O5 compat); batch lines are appended after them (additive overload — caller passes `plan` through).

**Threading:**

1. `state.py`: `join_projection_for_state(st, plan_dict?) -> list[str]` — resolves the probe `plan[]` preview (or an explicit plan arg from `dispatch_claims`) through the pure helper, fail-open `[]`.
2. `cli.py`: `probe`/`dispatch`-preview envelopes gain the batch lines inside existing `projection` (additive tail; existing assertions on `projection[0].startswith("rev ")` keep passing).
3. No daemon, no socket, no TS studio import (D5 boundary — studio reuse stays a doc-pointer).

## 3. Stale + error codes (stable strings)

Reuse verbatim: `stale_revision` (present + fire + claim + dispatch), `net_not_bootstrapped`, `unknown_id`, `empty_plan`, planner refuses. Every stale refuse prints the fresh-menu hint plus the live-R push (now with text).

## 4. Goldens (new file, canary-gated)

`tests/scripts/omt/test_net_followup_o5.py` (~9, `minor_feature` — no TDD):

- O5a: post-fire push `tasks_block` non-empty, contains `<!-- net_rev:R' -->` + `NEXT:` + `Pool:`/`Options:`/`Lanes:` as applicable, round-trips via `parse_tasks_block`; stale-R fire refuses with hint; render-error injected → `tasks_block == ""` (fail-open).
- O5b: 2-claim plan projects deterministic ordered task lines + `batch {id} rev R lanes 0/0/2 wip …`; malformed plan → `[]`; probe `projection[0]` unchanged (backward compat).
- Tier-3: place set unchanged; no new `net_*` kind; `src/agentx/` untouched; `uv` only.

## 5. Receipt + budget plan

- 3 single-edit rounds: (1) `freshness.py` additive helpers → hermetic smoke + e2e; (2) `state.py` threading (bash-run transform, lazy import, fail-open) → e2e; (3) `cli.py` display → e2e; goldens after tests/ canary (`omt_skip{scope:tests, purpose:canary}`); targeted + full suite green; `check 265/0` held.
- Token/runtime: one dry-run compose per envelope (bounded text); no background work; sidecars only until slice approval.
