# Analysis 001 — T6 multi-root project sync (feature_152)

> Resume: `CURRENT_STATE 2026-10-11j` Next — "T6 multi-root sync + 4 relocations
> (RE-READ the 2026-10-10 relocations-gap note FIRST)". Re-read: confirmed —
> `link` expresses feature→project only; project DIR moves ride T6; pre-T6
> single-root sync clobbers `WORK.md ## Projects` (V7 Alt).

## Current state (verified at HEAD `ac54d04`, tree clean of code)

- T1–T5 + Oracle complete (feature_138, 139–151 all Done). Remaining program tail
  after this unit: UC0 archival, `bridge:` backlog, CI pinning, Q5, phantom-link,
  WORK.compiled rev60-vs-live STALE, harness_wrapper_split backfill (D8-coupled).
- Project homes: `.projects/meta/` (24 rows in its META.md) + `.projects/agentx/`
  (1 home: `harness_wrapper_split`, state `unknown` — manual UC8 scaffold, no
  create record) + `.projects/archive/` + `.projects/README.md` (untracked file).
- 4 pending moves (`.projects/agentx/META.md` hand-appended draft):
  `agentx_concurrent_development`, `rag_v2`, `petri_net_studio`, `agentx_1_0_0`.

## Code evidence (single-root coupling)

| Site | Fact |
|---|---|
| `project_state.projects_root()` :45 | env override → else `@var projects_root` (`.projects/meta`) |
| `project_state.homes()` :157 | walks ONE root — powers manifest rows + WORK.md section |
| `project_state.build_work_projects_section()` :264 | iterates `homes()` → the WORK.md clobber mechanism |
| `project_state.derive_state()` :138 | last-op FSM: create/reopen/close/archive only; no move op |
| `project_state.manifest_path()` :61 | `<root>/META.md` — one manifest per root run |
| `project.py _sync_all()` :46 | manifest + `upsert_work_projects` + header flips, all single-root |
| `project.py cmd_link` :101 / `cmd_log` :120 / `cmd_backfill` :234 | home lookup = `projects_root()/slug` |
| `project.py _net_auto_sync()` :68 | fail-open, free-form event string (net/state.py:3959) |
| `harnessc` :743/:773/:799/:817 | home-existence checks via `_ps.projects_root()` |
| `harnessc` :853 | WORK.md byte-compare via `_ps.build_work_projects_section` (flows through) |
| `harnessc` :859 `_tasks_options_proj_drift` | active-set regex = `active\|complete\|draft` — `unknown` never trips |

## Invariants to preserve

- **030 suite green, zero edits:** `tests/harness_meta/omt/test_project_lifecycle.py`
  (26 tests, 7 classes) — hermetic via OMT_PROJECTS_ROOT/OMT_WORK_PATH; single-root
  env override must keep exact current behavior.
- **WORK.md budget:** 10723/11264 bytes (`.omt @budget work_md=11264` is truth;
  pin at `tests/harness_meta/omt/test_omt_docs_drift_pins.py:185`). Union must keep
  the 3-col shape (a root column ≈ +200B risks the cap).
- **Stdout contracts:** one-line lifecycle outputs (feature_041 R6 TA at
  project.py:81 — hook output is part of the contract).
- **Ledger schema frozen; kinds extend:** `move` joins ops of existing `project`
  kind (archive's `archived_to` field precedent for payload fields).
- **`_ir_var("projects_root")` untouched** → no `.omt` edit, no TS-fallback
  byte-compat risk, no harnessc init-template change for this feature.
- **Never `project.py new` into `.projects/agentx/`** (UC8) — `--root` is for
  product homes; harness homes stay meta.

## Coupling found during analysis (drives D8)

- Backfilling `harness_wrapper_split` (unknown→active) flips
  `_tasks_options_proj_drift` to `missing:harness_wrapper_split` → requires a
  WORK.md `## Tasks` Options change via `net_check.py sync --direction
  net_to_md` — but the live net is rev 0/idle (the standing startup STALE), so
  that sync would clobber the 10-option menu. Backfill therefore rides the close
  tail WITH the STALE reconciliation. Pre-backfill `unknown` row is drift-free.
- Moves are WORK.md-invisible: `| slug | state | features |` rows don't encode
  the root → the 4 relocations leave `## Projects` byte-identical. The union
  change adds exactly one row (`harness_wrapper_split`, `unknown`).

## Test surface map

- New: `tests/harness_meta/feature_152.t6_multi_root_project_sync/` (goldens 1–7
  per design §Tests).
- Guard: 030 re-export sentinel `feature_030.project_lifecycle/test_project_lifecycle_goldens.py`
  re-imports the omt-home suite — untouched.
- `test_omt_docs_drift_pins.py` WORK_BUDGET line: unchanged this unit (projection
  ~11050 ≤ 11264).

## Alternatives rejected

- **`@var projects_roots` IR var** — pays a full harness-surface round (.omt edit,
  TS fallback seed sync, harnessc build/check churn) for info the filesystem
  already holds; discovery (D1) gets identical behavior with zero IR churn.
- **Root column in WORK.md table** — budget risk; per-root manifests already own
  root truth.
- **`move` as new ledger kind** — schema-frozen rule prefers op-extend within the
  existing `project` kind (create/close/archive/reopen precedent).
