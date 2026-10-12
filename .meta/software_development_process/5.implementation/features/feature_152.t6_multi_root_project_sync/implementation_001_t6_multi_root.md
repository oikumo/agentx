# Implementation 001 — T6 multi-root project sync (feature_152)

## Files (single staged batch, one e2e receipt)

- `scripts/omt/project_state.py` — `projects_roots()` (env → single root; else
  archive-anchored discovery, `.projects/*` except `archive`), `root_name()`,
  `homes_in(root)`, `all_homes()`, `find_home(slug)` (ValueError on multi-root
  collision), `home_exists()`; `projects_root()` env-unset fallback now
  **archive-anchored `meta`** (IR var demoted to nonstandard-layout fallback);
  `manifest_path(root=None)` / `manifest_rows(root=None)` / `build_manifest(root=None)`
  (convention line names its root); `build_work_projects_section` iterates
  `all_homes()` (union, shape LOCKED 3-col); `derive_state` filters `op == "move"`
  (state transparency; `project_events` keeps them for `last event`).
- `scripts/omt/project.py` — `_sync_all()` regenerates EVERY root manifest +
  union WORK.md + per-root header flips; `cmd_move` (new; ledger
  `{kind:project, op:move, from_root, to_root}` + `shutil.move` + sync +
  `_net_auto_sync("move")`; no-op at current root writes NO record); `cmd_new
  --root` (default `meta`, collision across ALL roots); `cmd_link`/`cmd_log`/
  `cmd_backfill`/`cmd_status`/`cmd_close`/`cmd_archive` cross-root via
  `find_home`.
- `scripts/omt/harnessc.py` — `check_projects_structure`/`_resume`/`_status`
  iterate all roots; `check_projects_links` `home_exists` (feature_138's
  agentx hardcode subsumed); `check_projects_manifest` byte-compares EVERY
  root's manifest.

## Impl corrections (live goldens exposed, 151 precedent)

1. **Archived guard order** (operation_spec said home→root→…→archived):
   archive homes live OUTSIDE the roots → `find_home` can't see them →
   archived slug reported "unknown project home". Fixed: ledger-derived
   archived check FIRST (specific error beats generic).
2. **dest-exists reachability**: with `find_home` collision semantics,
   dest-exists only fires for a NON-DIR straggler at the dest (dirs in both
   roots = multi-root collision). Golden pinned via straggler-file scenario.
3. **Hermetic hole (found the hard way)**: env-unset `projects_root()` fell to
   the IR default = REAL `.projects/meta` — in-process golden `new`/`sync`
   calls leaked ghost homes + regenerated the real manifest from tmp-ledger
   state. Recovered (rm 4 ghost dirs + `git checkout` META.md), then fixed by
   the archive-anchored fallback (OMT_PROJECTS_ARCHIVE is per-call env in
   every fixture → anchor lands in tmp).
4. **`harnessc stage` ≠ `git add`**: the receipt batch is harnessc's OWN stage
   (`harnessc stage --feature F --files …`, cleared via `stage --clear`);
   git-staging does not register. First-edit-per-file is receipt-free; mid-batch
   second edits need `harnessc stage` or a mid-batch e2e mint.

## Real-repo consequence chain (D8 revision, deliberate)

Root-aware `check_projects_status` sees the agentx root → `harness_wrapper_split`
"unknown" → backfill REQUIRED for check-green (UC8 manual home adopted via
`project.py backfill`). Ripple: state active → `_tasks_options_proj_drift`
missing proj option → resolved SURGICALLY: `proj:harness_wrapper_split` added
to the `## Tasks` Options line + `workc build` (11 options, A–K). NO
`net_to_md` run (live net rev0 vs file rev60 — the standing STALE item owns
that; check only does set-based drift + pool counts, no ## Tasks byte-compare).

## Relocations (D7 — executed)

`move` ×4 → `.projects/agentx/`: agentx_concurrent_development, rag_v2,
petri_net_studio (active preserved), agentx_1_0_0 (draft preserved).
WORK.md rows byte-identical (slug|state|features don't encode the root);
manifests re-split 21 meta / 5 agentx; hand-appended pending-moves draft
section RETIRED (moves landed). Net hook fired 1-line proposals ×4 (D4,
never auto-applied).
