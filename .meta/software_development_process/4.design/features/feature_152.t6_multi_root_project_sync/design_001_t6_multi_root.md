# Design 001 — T6 multi-root project sync (feature_152)

> Program: harness_wrapper_split (T6). Gap note honored: 2026-10-10 UC8 block —
> `link` ≠ project move; pre-T6 single-root sync clobbers `WORK.md ## Projects`
> (the `OMT_WORK_PATH=tmp` hermetic idiom exists solely to dodge this).

## Problem (verified at HEAD `ac54d04`)

- `project_state.homes()` walks ONE root (`projects_root()`); `build_work_projects_section()`
  iterates it → any sync against `.projects/agentx` rewrites `WORK.md ## Projects` with only
  that root's rows. UC8 paid: scaffold + `link --origin manual` needed
  `OMT_PROJECTS_ROOT=.projects/agentx OMT_WORK_PATH=<tmp>`.
- Single-root lookups assume the home sits under `projects_root()`: `cmd_link` (project.py:101),
  `cmd_log` (:120), `cmd_backfill` (:234), `harnessc` home checks (:743/:773/:799/:817).
- The 4 product project homes live in `.projects/meta/` only because moving them pre-T6
  would desync every subsequent sync (V7 Alt; `.projects/agentx/META.md` pending-moves draft).
- `harness_wrapper_split` itself shows state `unknown` in its manifest row (manual UC8
  scaffold — no `project create` record).

## Model

### Roots (D1 — discovery, zero IR churn)

- `projects_roots() -> list[Path]` = sorted subdirs of `.projects/` except `archive`
  (skip files, e.g. `README.md`). Default walk is pure filesystem truth; the ledger
  stays the state truth (unchanged split: "ledger records + filesystem dirs").
- `OMT_PROJECTS_ROOT` env (tests' hermetic idiom) → single-root mode:
  `[Path(env)]`. `@var projects_root` IR var UNTOUCHED — remains the `new` default
  root. No `.omt` edit, no TS-fallback churn, no harnessc init-template change.
- Slug uniqueness invariant: a slug may exist in at most ONE root (move/new guard).

### Ledger (D2 — kind extend, schema frozen)

New op on the EXISTING `project` kind (ops today: create/close/archive/reopen):

```json
{"kind": "project", "op": "move", "project": "<slug>",
 "from_root": "meta", "to_root": "agentx"}
```

- `from_root`/`to_root` = root dir names (`.projects/<name>`), mirroring the
  `archive` precedent (`archived_to`).
- State-transparent: `derive_state` FSM must NOT see `move` as a lifecycle last-op
  (an active project stays active across a move). Implementation:
  `project_events()` keeps all records (manifest `last event` date reflects the
  move); `derive_state` filters `op == "move"` before reading last_op.
- `_net_auto_sync("move")` — hook takes free-form event strings
  (net/state.py:3959 `lifecycle_sync_hook(event)`), proposal-only + fail-open →
  zero net edits.

### Sync semantics (D3)

- Per-root manifests: `build_manifest(records, links, root)` — each root's
  `META.md` lists ONLY that root's homes (convention line names its own root).
  `_sync_all()` iterates all roots, regenerating each manifest.
- `WORK.md ## Projects` = UNION across all roots, shape LOCKED (3-col
  `| project | state | features |`): WORK.md budget 10723/11264 — a root column
  (~25 rows × ~8B) risks the cap; root truth lives in the per-root manifests.
  This kills the clobber AND the `OMT_WORK_PATH=tmp` idiom for real runs (env
  override stays for tests).
- Header reconciliation (`_sync_all` flips) iterates homes across all roots.

### CLI (D4/D5)

- `project.py move <slug> --to-root <name>`: guards (home found cross-root,
  dest root exists, no slug collision, not archived) → `shutil.move` dir →
  ledger `move` record → `_sync_all()` + `_net_auto_sync("move")` → one-line
  stdout (house contract). Idempotent no-op when already at dest root
  (same dir → print, no record).
- `new --root <name>` (default `meta`): product projects born in the product home;
  slug-collision guard across ALL roots.
- `find_home(slug) -> Path | None`: cross-root lookup for link/log/status/backfill/move.
- `cmd_link` home check + `cmd_log` + `cmd_backfill` switch to `find_home`.
- Output strings keep their exact shapes (stdout contract pinned by 030 suite).

### harnessc (D6)

- Home-existence checks at :743/:773/:799/:817 search all roots (root-aware).
- WORK.md byte-compare (:853 `_ps.build_work_projects_section`) flows through the
  updated builder — zero harnessc-side duplication by construction.
- `_tasks_options_proj_drift` (:859) unchanged: its active-set regex matches
  `active|complete|draft` only — `unknown` (harness_wrapper_split pre-backfill)
  never trips it.

## Out of scope (D8 — deferred, deliberate)

- **`backfill harness_wrapper_split`** (unknown→active): would trip
  `_tasks_options_proj_drift` (missing proj option) → forces a WORK.md `## Tasks`
  Options change → collides with the standing "WORK.compiled rev60 vs live rev0
  STALE" reconciliation (net_to_md sync against the empty live net would clobber
  the 10-option menu). Rides the program close tail WITH that item.
- **`project` receipt slice**: this feature is a single harness round (1 e2e);
  slice machinery (feature_151) pays off across many rounds. Global receipt covers.
- `project.py new` into `.projects/agentx/` stays BANNED pre-close (UC8 rule
  unchanged — `--root agentx` is for PRODUCT projects; harness homes stay meta).

## Tests (RED contract — `tests/harness_meta/feature_152.t6_multi_root_project_sync/`)

Hermetic env idiom (tmp roots + tmp WORK.md + tmp ledger, OMT_PROJECTS_ROOT unset
for multi-root cases, set for compat cases):

1. **Multi-root union, no clobber:** two tmp roots under a tmp `.projects/`,
   homes in both; sync → WORK.md `## Projects` contains BOTH roots' rows; second
   sync byte-stable (idempotent); WORK.md sections outside `## Projects` untouched.
2. **Per-root manifests:** each root's META.md lists only its own homes; archived
   section still ledger-derived; convention line names its root.
3. **move:** dir relocated + `move` record written (`from_root`/`to_root`); state
   unchanged across the move (active stays active — FSM transparency); WORK.md
   row byte-identical before/after move; `last event` reflects the move; no-op at
   dest root writes no record; collision + unknown-slug + unknown-root errors.
4. **new --root:** home created under named root; default stays meta; collision
   across roots refused.
5. **Cross-root lookups:** link/log/backfill resolve a home in a non-default root
   without env overrides.
6. **Env compat (single-root mode):** OMT_PROJECTS_ROOT set → manifest+WORK.md
   behave exactly as today (030 suite stays green unmodified).
7. **derive_state transparency:** create→link→move→(more events) FSM sequences.

030 suite (`tests/harness_meta/omt/test_project_lifecycle.py`, 26 tests) must stay
green with ZERO edits — it pins today's single-root idiom via env overrides.

## Acceptance gates (this unit)

- New goldens green + 030 suite green (zero edits).
- Relocations: `move` × 4 (`agentx_concurrent_development`, `rag_v2`,
  `petri_net_studio`, `agentx_1_0_0`) → `.projects/agentx/`; WORK.md `## Projects`
  rows byte-identical (moves are state-transparent); union adds exactly one NEW
  row: `harness_wrapper_split | unknown | feature_138…, feature_152… |`.
- `.projects/agentx/META.md` pending-moves hand-appended section RETIRED
  (moves landed — section obsolete).
- Budget: WORK.md ≤ 11264 (projected ~11050: +1 union row ~70B + DONE row ~250B).
- `harnessc check` 282/0 · lanes 12F/2144P/5S same-12 zero-new · `prove --lane both
  --out /tmp/opencode/` clean ×2, verify STALE-valid, certs rm'd · e2e receipt
  fresh (single global round) · THINK: TA consults recorded for project.py,
  project_state.py, harnessc.py.

## Commits (user-confirmed)

1. Implementation + goldens (harness edits + new test dir).
2. Relocations + regenerated manifests (+ retired pending-moves section).
