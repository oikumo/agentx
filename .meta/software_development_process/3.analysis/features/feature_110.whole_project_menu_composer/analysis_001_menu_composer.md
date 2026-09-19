# Analysis 001 — O1 whole-project menu composer (scope for approval)

> Feature: `feature_110.whole_project_menu_composer` (`minor_feature`, project `meta_harness_11`) · Phase: Analysis · Date: 2026-09-19.
> Resumes: PROJECT.md §Plan O1 + §Quick Start + gaps doc G1/G2/G3/G7 + live rev 60 `drained_complete`.

---

## 1. Problem (reproducer)

Cold start on rev 60 presents an empty menu and stops:

- `probe rev 60`: `marking {work_done:7, pending:0, active:0}`, `enabled:[]`, `observation:drained_complete`, `menu {next:none, other:[], blocked:[], resources 4/4 free}`.
- Same rev: 3 projects `active` (petri_net_studio, project_lifecycle, rag_v2) + 3 `draft` (incl. aging 27d `feature_kb_akb`, `workflows`) + PENDING `feature_001/002 scope unset` + `drift` hygiene (`unlinked-project-backed ×10`, `aging-draft`, `iteration-log ×5`).
- `sync_md.render_tasks_block` uses only `enabled[]/holders/conflicts` + pool counts; Projects table (`project.py sync` rows), `drift`, PENDING 001/002 never enter NEXT/Other/Blocked text. User sees "nothing to do" while active projects exist (G1).
- Empty-menu path has no next-step generator (G2); verification/integration lanes + deadlock explanation do not flow into menu text (G3); no uniform selectable IDs across pool/projects/hygiene/unscoped (G7).

Reproduce: `omt_net{probe}` rev 60 → `omt_q{drift}` → `WORK.md` Tasks `NEXT:none` vs `## Projects` 3 active — divergence is the bug.

## 2. What O1 must prove (oracle)

- Cold start renders **one whole-project menu** with stable IDs, D19 ordering (`NEXT / Other enabled / Blocked / Resources`), rev-stamp:
  - Pool counts line kept (`Pool: pending/active/done (places N/15)`).
  - `project.py sync` rows (3 active / 3 draft) as selectable proposals with `proj:<slug>` IDs.
  - `omt_q{drift}` hygiene as selectable proposals (`drift:<class>:<key>`), at least `unlinked-project-backed`, `aging-draft`, `iteration-log`.
  - PENDING 001/002 as selectable proposals (`unscoped:001`, `unscoped:002`).
  - Verification/integration capacity + deadlock hint in Blocked/Resources text (G3 slice: one line, no live view).
- Empty menu (`enabled:[]`) still yields NEXT proposals (no longer `NEXT:none` with stop); stale rev refuses with re-render (keep `--expected-revision` guard).
- Deterministic, stdlib-only, no net I/O inside `sync_md.py` (caller `state.sync` supplies live net/overlay/resources/drift/projects); D19 ordering + rev-stamp preserved; TA gotcha at `sync_md.py:66` honored (no hand rows between `Pool:` and `## Projects`).
- Out of scope: multi-select grammar (O2), claim handles (O3), dispatch/worktrees (O4), live view (O5), agentx bridge (O6). Still serial.

## 3. Resource budget

- Code: `scripts/omt/net/sync_md.py` (+ `state.py` caller threading drift/projects) only; Tier-3 excludes net — no new places/transitions.
- Tests: extend existing `sync_md`/menu goldens in `tests/` (canary approval needed — tests/ gate); e2e receipt per harness-surface round discipline (one edit per file per receipt).
- Runtime: pure render, no extra probe (menu-time freshness is O5); token cost = one render pass.

## 4. ID scheme (proposal, O2 will consume)

- `pool:<transition>` for enabled pool transitions (existing `NEXT` names).
- `proj:<project-slug>` for Projects rows.
- `drift:<class>:<short-key>` for hygiene (e.g. `drift:unlinked:feature_kb_akb`).
- `unscoped:001`, `unscoped:002` for PENDING FEATURES.
- Stable across revs; ordering D19 (NEXT recommended first, then Other, Blocked, Resources).

## 5. Next (Design → code)

- `omt_phase{minor_feature, Design}` → extend `render_tasks_block`/`menu_lines` signatures (additive optional args, no break) + `state.sync` threading + goldens → `omt_complete{advance_to:Testing}`.
