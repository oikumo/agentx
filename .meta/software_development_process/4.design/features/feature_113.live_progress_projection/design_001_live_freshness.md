# Design 001 — O5 live progress projection (freshness + push + minimal view)

> Feature: `feature_113.live_progress_projection` (`minor_feature`) · Phase: Design · Date: 2026-09-19.
> Consumes: Analysis 001 + O1 render (`sync_md.render_tasks_block`, D19 + rev-stamp) + `state.sync net_to_md` + `fire/claim/apply_selection` `_require_revision` + O3 `menu.claims`.

---

## 1. Freshness grammar (pure, stdlib-only)

```ebnf
stamped_rev := int ;   (* WORK.md <!-- net_rev:R --> *)
live_rev    := int ;   (* NetState.revision *)
fresh       := stamped_rev == live_rev ;
```

- `is_fresh(stamped_rev, live_rev) -> bool` (pure): equality only; `None` stamped → not-fresh (cold start → `sync` first).
- `freshness_hint(stamped_rev, live_rev) -> str`: `stale_revision (expected R, live R') — re-render (sync net_to_md) before presenting` (reuse `_require_revision` message verbatim, D19).
- Present rule (convention, no daemon): any whole-project menu present pairs `probe` (live R) + stamped R check; stale → refuse or auto `sync net_to_md` then present (caller choice, same as O2/O3 stale path).

## 2. Push record (derived, no new kinds)

- `push_record(st, rendered: str) -> dict`: `{ net_revision, menu:{projects,hygiene,unscoped,lanes,claims}, tasks_block: rendered }` — derived from existing `sync net_to_md` return (`record/info["menu"]` + rendered text), no new `net_*` kind (replay-safe).
- Threading (harness-surface, receipt-disciplined, one edit per file per e2e receipt):
  1. `state.py`: `fire`, `claim_task`, `release`, `apply_selection` return additive `push: {net_revision, menu}` alongside existing `NetState` (or via post-op `sync(dry_run=True)` compose — no extra lock, fail-open on render error).
  2. `cli.py`: `fire/claim/apply-selection` JSON gains additive `push` + `freshness` fields; `probe` JSON gains `freshness: {stamped_rev?, live_rev, fresh}` when `--expected-revision` supplied.
  3. `sync_md.py`: no format change (D19 + rev-stamp already); live view helper `projection_lines(marking, lanes, claims)` reuses `lanes_line` + `compose_menu_options` counts for minimal text view (studio reuse is doc-pointer, not code import — `tools/petri-net-studio` TS boundary kept, D5).

## 3. Minimal live view (read-only)

- `projection_lines()` (pure): `rev R | marking {…} | enabled […] | lanes … | claims N/M | deadlocks_complete?` — one screen, no slider interaction in M1 slice (slider is O4+ follow-up).
- No background loop, no socket, no second adapter; push is return-value, present is `probe+sync` pair.

## 4. Stale + error codes (stable strings)

- Reuse verbatim: `stale_revision` (present + fire + claim), `net_not_bootstrapped`, `unknown_id`. Every stale refuse prints fresh-menu hint + `push` of live R.

## 5. Goldens (new file, canary-gated)

`tests/scripts/omt/test_net_fresh_o5.py` (~10): fresh==true present passes; stale present refuses; fire returns push with live rev; push preserves D19 + rev-stamp; projection_lines deterministic; no-new-places invariant (Tier-3); probe freshness additive.

## 6. Receipt + budget plan

- 3 single-edit rounds: (1) pure `freshness.py` (or `sync_md.py` additive) → hermetic smoke + e2e; (2) `state.py` push threading → e2e; (3) `cli.py` display → e2e; goldens after tests/ canary.
- Token/runtime: one `probe` before present + one dry-run `sync` compose after each mutate; no new places/transitions; `src/agentx/` untouched (D1).
