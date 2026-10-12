# Operation Spec — T6 multi-root project sync (feature_152)

> Companion to `design_001_t6_multi_root.md`. Exact operations, signatures,
> stdout/exit contracts. All stdout strings are pinned surface.

## `project_state.py` (pure functions + paths)

### Roots

```python
def projects_roots() -> list[Path]
```
- `OMT_PROJECTS_ROOT` set → `[Path(env)]` (single-root compat mode).
- else → sorted subdirs of `REPO_ROOT/.projects/` excluding `archive` and
  non-dirs; falls back to `[projects_root()]` when `.projects/` has no
  qualifying subdir (fresh-checkout safety).

```python
def root_name(p: Path) -> str          # p.name (".projects/<name>")
def find_home(slug: str) -> Path | None
```
- `find_home`: search `projects_roots()` in order; first `<root>/<slug>` dir
  wins; None when absent; **ValueError when found in >1 root** (slug-uniqueness
  invariant — callers print + exit 2).

### Homes / manifests

```python
def homes() -> list[str]                          # UNCHANGED semantics (first root) — 030 pin
def homes_in(root: Path) -> list[str]             # per-root walk (old body)
def all_homes() -> list[tuple[Path, str]]         # union across roots (sorted)
def manifest_path(root: Path | None = None) -> Path   # default: projects_root() (030 pin)
def build_manifest(records, links, root: Path | None = None) -> str
```
- `build_manifest`: rows from `homes_in(root)`; header convention line names the
  passed root (`Convention: `.projects/<name>/<slug>/…``); archived section
  unchanged (ledger-derived).
- `manifest_rows(records, links, root=None)` gains the root param (same default).

### WORK.md section

```python
def build_work_projects_section(records, links) -> str   # shape UNCHANGED
```
- Rows now from `all_homes()` (union), sorted by root order then slug; archived
  skip + 3-col shape byte-identical to today.

### State (move transparency)

```python
def derive_state(slug, records, links) -> str
```
- Filter `r["op"] == "move"` out of `project_events` BEFORE the last-op read
  (create/reopen/close/archive FSM unchanged); `move` still visible via
  `project_events` (manifest `last event`) and to callers that don't filter.

## `project.py` (CLI)

### `move`

```
uv run scripts/omt/project.py move <slug> --to-root <name>
```
Guards (order): home exists via `find_home` (else `error: unknown project home
'<slug>'`, exit 2) · dest root in `projects_roots()` (else `error: unknown root
'<name>'`, exit 2) · dest `<dest>/<slug>` absent (else `error: destination
exists`, exit 2) · not archived (else `error: cannot move an archived project`,
exit 2).
Idempotent no-op: home already under dest root → `already at root <name>: <slug>
(no-op)`, exit 0, NO record.
Success: `shutil.move` → `write_record({"kind":"project","op":"move","project":slug,
"from_root":…,"to_root":…})` → `_sync_all()` → `_net_auto_sync("move")` →
`✅ moved <slug> → .projects/<name>/ (state: <derived>)`, exit 0.

### `new --root`

```
uv run scripts/omt/project.py new "<name>" [--slug <slug>] [--root <name>]
```
- `--root` default `meta`; must be in `projects_roots()` (same error shape as
  move's root guard); home created under `<root>/<slug>`; slug-collision guard
  across ALL roots; ledger create record UNCHANGED (no root field — root is
  filesystem truth, derivable from `find_home`).
- Success line: `✅ created project home .projects/<name>/<slug>/ (state: draft)`.

### Cross-root rewrites (behavioral, not API)

- `cmd_link`: home check → `find_home(args.project)` (+ collision error).
- `cmd_log`: `CURRENT_STATE.md` path → via `find_home`.
- `cmd_backfill`: dir check → `find_home`.
- `cmd_status`: home-derived paths → via `find_home` (none/missing → current
  error shapes preserved).
- `cmd_sync`: iterate `projects_roots()` → regenerate EVERY root's manifest;
  `upsert_work_projects` once (union); header flips across `all_homes()`.
  Stdout unchanged: `✅ manifest regenerated: <path>` (first root) + flip lines;
  per-root regen is silent beyond existing lines.
- `cmd_new`/`cmd_archive`/`cmd_close`/`cmd_reopen`: `_sync_all()` now covers all
  roots automatically (no per-cmd changes beyond `new --root`).

## `harnessc.py`

- `:743/:773/:799/:817` home checks: `_ps.projects_root()/x` → root-aware
  (`find_home(x)` / `all_homes()` membership). Error message TEXT unchanged.
- No new checks; byte-compare (:853) + drift (:859) flow via `_ps` builders.

## Net

- `_net_auto_sync("move")` only — free-form event string (net/state.py:3959
  accepts any `str`); zero net-file edits.

## Exit/stdout contract summary

| Site | Shape |
|---|---|
| move success | `✅ moved <slug> → .projects/<name>/ (state: <state>)` |
| move no-op | `already at root <name>: <slug> (no-op)` |
| new success | `✅ created project home .projects/<name>/<slug>/ (state: draft)` |
| all guards | `error: …` on stderr, exit 2 (current shapes kept verbatim) |
| sync | `✅ manifest regenerated: <first-root>/META.md` (+ flip lines) |
