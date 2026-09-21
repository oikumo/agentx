# Meta-Harness Toolbox — Evolutionary Live Tool System (proposal for next version)

> Status: proposal only (`.sandbox/`, non-gated, no `src/`/`tests/`/`.meta/` mutation).
> Date: 2026-09-21 · Builds on: mh8 R2 (0 wins, healthy) + `meta_harness_session_usecase_gaps.md` (G1–G16) + mh6 eval (D1 tiered template).
> Ask: a robust **toolbox** the agent knows about in-session, implemented as **bash wrappers → python scripts**, **categorized + sqlite-discoverable during an opencode session**, and **growable** when the agent hits a specific or general useful use case.

## 1. Executive summary

Add a `toolbox/` subsystem — one SQLite index + one folder of versioned tools — that turns today's
ad-hoc `uv run scripts/omt/*.py` invocations into a **named, categorized, queryable, self-growing
tool layer**. The agent learns it exists at session start (one STARTUP line + one `omt_status`
field, budget-capped), discovers tools mid-session with **sqlite queries** (not grep/glob, so it
honors the nav-gate spirit for operational knowledge), runs them through **bash entrypoints that
call python implementations**, and can **propose a new tool** when a task recurs or a one-off proves
generally useful. Growth is approval-gated (`.workflows/` mandatory gate, no auto-add, no auto-run),
usage-metered (ledger + sqlite `usage_log`), and pruned (thought-review style expiry). First slice is
docs + index + 3–5 seed tools + read-only query CLI; execution/promotion/stats follow as minor slices.
No gate removals, no auto-skip, no `src/agentx/` work (D1 holds).

## 2. Target use case (as requested, verbatim + expanded)

1. **Agent knows a toolbox exists in-session.** Cold start tells it: name, where the index lives,
   one query command, categories. No memorization across sessions required.
2. **Toolbox is an evolutionary live system.** Index updates when tools are added/deprecated;
   `sync`/`probe`-style freshness (rev-stamp) so two sessions never see a stale menu.
3. **Indexes multiple bash→python tools, categorized, discovered with sqlite queries during an
   opencode session.** Each tool = `toolbox/<category>/<name>/run.sh` (bash wrapper, arg parsing,
   env guards) + `main.py` (real logic) + `TOOL.md` (contract). The sqlite DB
   (`toolbox/index.sqlite3`, checked-in WAL + generated `index.json` projection) holds
   `tools/categories/usage_log/proposals`. Discovery = `toolbox query "…"` / raw
   `sqlite3 … SELECT …` — e.g. "which tool parses TDD behaviors?", "list git-state tools".
4. **Grows on encounter.** If the agent solves something twice, or a one-off looks reusable
   (specific: `petri-net reachability dump`; general: `ledger window slice`), it files a
   **proposal record** (sqlite `proposals` + `.sandbox/toolbox_proposals/<name>.md`) instead of
   silently forking a script. User picks → promote → indexed, tested, metered.

Success = session-start awareness → mid-session `query → run` in ≤2 calls → proposal → approve →
`run` of the new tool next session with usage counted.

## 3. Goals / non-goals

Goals: (a) single discoverable surface for operational scripts; (b) sqlite-first discovery usable
inside opencode bash; (c) bash-stable contract with python-swappable impls; (d) gated growth with
audit; (e) usage/success metering feeding prune/keep decisions; (f) tier-aware (mh6 D1: Tier-1 gets
5 core tools, Tier-2/3 get full set).

Non-goals: no new `@gate` (stays at 12, B1 net-zero holds); no autonomous tool execution or
self-modifying tools; no network fetch tools; no replacement for `omt_net`/`omt_tdd`/`omt_q` —
toolbox **wraps and indexes**, never re-implements enforcers; no `src/agentx/` runtime dispatch
(feature_001 stays out of scope per D1/G15 — toolbox serves harness-side operational work first,
agentx bridge is O6 later).

## 4. Architecture

```
opencode session (bash tool)
  ├─ STARTUP inject: "toolbox: <n> tools, `uv run scripts/toolbox/toolbox.py query …`" (≤120B, budget-capped)
  ├─ toolbox.py query/list/show  ──►  toolbox/index.sqlite3 (tools, categories, FTS)
  ├─ toolbox.py run <name> [-- …] ──► toolbox/<cat>/<name>/run.sh ──► main.py (uv, no bare python/pip)
  ├─ toolbox.py propose … ──► proposals table + .sandbox/toolbox_proposals/<name>.md (needs approval)
  └─ toolbox.py promote/prune/stats (approval-gated; ledger kind:toolbox_* + CURRENT_STATE log)
Projections: index.json (generated, like nav.index.jsonl) · TOOL.md per tool · docs page per category
```

Why bash→python (not python-only): bash gives a **stable 1-line contract** opencode can call without
import-path knowledge, handles `uv` pinning/env guards/arg shifting uniformly, and keeps the
`uv-only` rule (AGENTS.md) in one place; python holds the logic and stays testable with pytest.
Why sqlite (not just markdown/JSONL): **queryable in-session** (`SELECT … WHERE category=… ORDER BY
success_rate`), FTS over name/description/tags, atomic usage counters, and a proposals state machine
without inventing a new ledger kind per tool.

## 5. Layout + sqlite schema (initial, small)

```
toolbox/
  index.sqlite3                 # SSOT (checked in; WAL; rev-stamped via toolbox_meta)
  index.json                    # generated projection (like .meta/.omt/*, rebuilt on promote/prune)
  <category>/<tool>/run.sh      # bash wrapper: set -euo pipefail, exec uv run python main.py "$@"
  <category>/<tool>/main.py     # impl (argparse, JSON to stdout, exit codes)
  <category>/<tool>/TOOL.md     # 15-line contract: purpose, args, I/O, example, limits
  categories.md                 # taxonomy doc (generated from categories table)
scripts/toolbox/toolbox.py      # query/list/show/run/propose/promote/prune/stats/sync
.sandbox/toolbox_proposals/     # per-proposal staging docs (approval gate input)
```

```sql
CREATE TABLE categories(id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT);
CREATE TABLE tools(
  id TEXT PRIMARY KEY,            -- e.g. git.status_summary
  name TEXT NOT NULL, category TEXT NOT NULL REFERENCES categories(id),
  bash_entry TEXT NOT NULL,       -- toolbox/git/status_summary/run.sh
  python_impl TEXT NOT NULL,      -- toolbox/git/status_summary/main.py
  description TEXT NOT NULL, tags TEXT NOT NULL DEFAULT '', -- comma list
  version TEXT NOT NULL DEFAULT '0.1.0', deprecated_by TEXT,
  uses INTEGER NOT NULL DEFAULT 0, successes INTEGER NOT NULL DEFAULT 0,
  created_by TEXT, created_at TEXT, promoted_at TEXT
);
CREATE VIRTUAL TABLE tools_fts USING fts5(name, description, tags, content='tools', content_rowid='rowid');
CREATE TABLE usage_log(ts TEXT, tool_id TEXT, session TEXT, ok INTEGER, ms INTEGER, note TEXT);
CREATE TABLE proposals(id TEXT PRIMARY KEY, title TEXT, category TEXT, motive TEXT,
  status TEXT DEFAULT 'staged', -- staged|approved|rejected|promoted
  draft_path TEXT, uses_seen INTEGER DEFAULT 1, created_at TEXT);
CREATE TABLE toolbox_meta(k TEXT PRIMARY KEY, v TEXT); -- rev, updated_at, schema_version
```

Seed taxonomy (5 cats, 3–5 tools to start, all wrapping **already-proven** one-liners so slice 1 is
indexing, not invention): `git.*` (status_summary, recent_log), `ledger.*` (window_slice, drift_scan),
`harness.*` (budget_check, nav_lookup), `text.*` (json_split, frontmatter_get), `session.*`
(pause_note_append). Each seed re-homes an existing `scripts/omt/*` or WORK.md recipe — no new logic
in slice 1.

## 6. Tool contract (hardened, small)

`run.sh`: `#!/usr/bin/env bash / set -euo pipefail / HERE=$(dirname …) / exec uv run python "$HERE/main.py" "$@"`.
`main.py`: argparse only, JSON object to stdout (`{"ok":…, "data":…}`), non-zero exit + `{"ok":false,
"error":…}` on failure, no network, no writes outside `$CWD/.sandbox/toolbox_runs/` + stdout unless
`--write` + approval note in TOOL.md. `TOOL.md` (≤15 lines): purpose · usage line · args · I/O example
· limits/denies. Naming: `<category>.<snake_name>`; version bump on behavior change; deprecate via
`deprecated_by`, never delete in the promoting session (prune is a separate gated op).

## 7. Discovery protocol (in-session sqlite)

Session-start (budget-capped, Tier-aware): AGENTS.md gains one line
(`toolbox: N tools — uv run scripts/toolbox/toolbox.py query "<keywords>" …`) + STARTUP inject
(`INJECT toolbox line`, feature_049 pattern) + `omt_status` gains `toolbox: rev=<r> tools=<n>`
(omit when Tier-1 minimal). Mid-session discovery is **2 calls max**:

```bash
# 1. find: FTS + category filter + quality rank
uv run scripts/toolbox/toolbox.py query "tdd behaviors prose" --limit 5
# └─ SELECT id,name,category,description FROM tools_fts JOIN tools … ORDER BY rank, successes*1.0/(uses+1) DESC
# 2. inspect then run (run echoes TOOL.md usage on --help; receipts unchanged)
uv run scripts/toolbox/toolbox.py show ledger.window_slice
uv run scripts/toolbox/toolbox.py run ledger.window_slice -- --days 7 --format json
```

Raw-sqlite escape hatch (for nav-gate-sensitive operational lookup, documented in TOOL.md):
`sqlite3 toolbox/index.sqlite3 "SELECT id,description FROM tools WHERE category='git' ORDER BY uses DESC;"`.
`list --category <c>`, `stats --top 10`, and `sync --check` (rev-stamp vs `toolbox_meta.rev`, STALE
pattern from G4) complete the read path. All read ops are side-effect-free and need no phase/claim.

## 8. Growth protocol (encounter → proposal → promotion)

Trigger (either): **specific** ("I just hand-rolled X twice — propose it") or **general** ("this
ledger-slice recipe will recur — propose it"). Agent never writes `toolbox/` directly on encounter;
it stages:

```bash
uv run scripts/toolbox/toolbox.py propose --title "git dirty-file list" --category git \
  --motive "needed 2× in one session; 6-line status --porcelain wrapper" --draft .sandbox/toolbox_proposals/git.dirty_files.md
```

This inserts `proposals(status='staged')` + writes the draft doc (contract sketch + 2 use evidences +
denies). Then the **mandatory approval gate** (`.workflows/` rule: propose in sandbox → user picks →
execute): user approves/rejects in plain reply (D19-style single pick, no question-tool needed).
On approve, `promote` (gated, one tool per round, harness-surface discipline): scaffold
`<cat>/<name>/{run.sh,main.py,TOOL.md}` + minimal pytest (`tests/scripts/toolbox/test_<name>.py`) +
`index.json` rebuild + ledger `kind:toolbox_promote` + CURRENT_STATE line. On reject, status update
only. **Prune** (monthly or >90d untouched, thought-review pattern): `uses==0` + no dependents →
`deprecated_by` → one-cycle warning → remove, ledger `kind:toolbox_prune`. Metrics gate promotion:
a proposal needs ≥2 observed uses (or 1 + reviewer "general-use" tag) — stops one-off bloat.

## 9. Safety + harness fit (why this passes the old rejections)

No new gate (B1 holds: toolbox consults are advisory, enforced only through existing
`g.nav`/`g.think`/`g.kb`/`g.net` when touching `src/`/`tests/`/`.opencode/`/`scripts/omt/`); growth
respects protected paths (`.env*`, `uv.lock`, `README.md`, `LICENSE` — `omt_skip{scope:all}` only),
`uv-only` execution, `tests/` canary rule (new tool tests land under RED hat via `omt_tdd`), and the
receipt round-robin (one `toolbox/` file per edit round + `sync` receipt refresh). Deny list for tools:
no `git push/pull/fetch/remote/clone`, no bare `python/pip/pytest`, no `*.env` reads, no network.
Budget honesty: STARTUP inject ≤120B and `toolbox` status field are new metered strings with diet-bot
coverage (091 pattern) — if `agents_md`/`tool_args` cap pressure returns, Tier-1 collapses to
"toolbox: query …" with zero per-tool text. Evasion-safe: every `run` appends `usage_log` + optional
ledger line, so `skip`-style bypass shows up in `stats` (A2 taxonomy pattern).

## 10. Implementation plan (slices, one approval per slice)

| Slice | Type | Content | Acceptance |
|---|---|---|---|
| T1 index + query | minor | `toolbox/` layout, schema + seed 5 tools (rehomed), `toolbox.py query/list/show/sync --check`, `index.json`, STARTUP 1-liner + status field | `query` returns seed tools ranked; `sync --check` detects stale rev; budgets green |
| T2 run + metering | minor | `run` wrapper discipline + `usage_log` + `stats`; TOOL.md lint (`run.sh`/`main.py`/contract present) | 5 seeds runnable via `run`; `stats` shows uses/success; lint 0 errors |
| T3 propose/promote/prune | minor | proposals table + staging docs + approval copy + `promote` scaffold + `prune` deprecate | staged→approved→promoted e2e for 1 pilot tool with pytest; reject path leaves index untouched |
| T4 docs + tiers | docs/minor | `categories.md` gen, per-tool docs, `harnessc` tier mapping (T1 core-5, T2/3 full), onboarding snippet | tier init gets correct subset; onboarding builds |
| Later (O4/O6 bridge) | major | concurrent dispatch of independent `run`s; agentx adaptive-net bridge (needs D1 revisit) | only after T1–T3 + G12/F7 decision |

Each slice: `omt_phase` decl → tests-first for `toolbox.py` (pytest) → `omt_complete` + `invariant`
drift check. Rollback per slice is `promote --undo` / index rebuild from `index.json`.

## 11. Worked example

Agent needs "which files are dirty right now" twice. `query "git dirty status"` → `git.status_summary`
(rank 1, 12 uses, 100%). Third encounter → `propose --title git.dirty_files …` (motive cites 2
sessions). User approves. `promote` scaffolds `toolbox/git/dirty_files/{run.sh,main.py,TOOL.md}` +
`test_dirty_files.py` (RED→GREEN via `omt_tdd`), bumps `toolbox_meta.rev`, rebuilds `index.json`.
Next session STARTUP shows `toolbox: 6 tools rev=7`; `run git.dirty_files` works; `stats` counts it.
Unused after 90d → `prune` deprecates with pointer to `git.status_summary`.

## 12. Relation to prior art (do-not-revisit honored)

Shipped stays shipped (mh8 T1–T5, mh6 A1–F1, 037/038 toolchain/prose); rejected stays rejected (§3 #4
nav-strikes, #5 budget removal, #7 tighten-to-actual, D3 trio unless new evidence). This proposal
answers `session_usecase_gaps` G7/O1 (enumerable whole-project options: toolbox categories join the
menu composer as selectable ops), G5/G6/O2 (per-tool directives via `run -- …` args, no grammar change),
and mh6 D1 (tiered template gains a concrete Tier-1 payload) without touching F7 serial-execution or
D1 `src/agentx` scope. Fresh-review rule (mh5 D4/T5-8) applies: if built, the next review must show a
repeat-failure class it eliminated (candidate: "ad-hoc script re-invention across ≥2 features") with
`uses`/`successes` as evidence, else no follow-up tool.

## 13. Open questions (for approval reply, single-letter pick welcome)

A. Seed set: 5 rehomed tools (recommended) vs 8 with 3 net-new? B. DB checked-in binary vs
`schema.sql` + built sqlite (recommend checked-in + `index.json` projection for diffability)?
C. Tier-1 core-5 list — drop `text.*`? D. `stats` in menu composer now (O1) or T4?

---
*Acceptance for this doc: proposal exists at `.sandbox/meta_harness_toolbox_idea.md`, references live
rev-60 gaps + mh8/mh6 lineage, specifies schema/contract/query/growth/safety/slices; no code, no gates,
no commits.*
