# PROPOSAL — orthogonal harness-wrapper split (sandbox copy, no effect) — refined v4

> Mirror note: `.projects/README.md` is an **untracked draft** (`git status ??`,
> unreviewed, no ledger record — verified 2026-10-10 ~16:00 UTC), not a canonical
> home. This file **inlines** the homes rule with measurements and wins on conflict
> until both are promoted together. Do not cite `.projects/README.md` as authority.
> Status: **draft proposal** (refined 2026-10-10 v4, no approval, no promotion, no moves).
> v4 is the second critical-revision pass: v3's own measurements are re-checked below;
> every correction cites the command/file/line so reviewers can re-run it.

## 0. Terminology + pinned paths/counts (re-measured 2026-10-10 ~16:00 UTC)

- **Product** = AgentX runtime + UI: `src/agentx/**`, product docs, product tests.
- **Harness (wrapper)** = META HARNESS process + tooling: `scripts/omt/**`,
  `scripts/session_inspect/`, `.meta/**`, `.opencode/**` (plugins in
  `.opencode/plugins/`, predicates in `.opencode/lib/enforcer/` — 12 files, not
  `lib/enforcer`). There is **no top-level `harness/` directory**; any "rename
  harness away" proof must list the four dirs explicitly (§7).
- **Orthogonal** = either side builds / tests / ships with the other side absent,
  except for two declared bridges: (a) append-only ledger at
  `.meta/.omt/ledger.jsonl` + named read-only projections (contract pinned in
  T2 — v3 said "today only 2 rows"; **stale on arrival: 5 rows at v4
  re-measurement**, because the v3 refine itself appended `think_consult` +
  `phase` + `complete` for `unscoped:001` — observer effect, see §7; and the
  first `think_consult` row embeds 60+ file paths, i.e. the bridge is wider than
  "minimal" suggests), (b) `# TA:` comment-line inversion (§4). No other
  cross-imports at runtime.
- **Home** = where a PROJECT.md lives (`.projects/meta/` vs `.projects/agentx/`).
  **Owner** = who may change it. **Location** = where the file sits. A bridge file
  has one owner and may sit anywhere; the mismatch is declared, not hidden.
- **Counts (don't quote stale ones):** 11 `omt_*` MCP tools
  (`phase,skip,complete,status,tdd,nav,think,kb_nav,q,net,session` per
  `opencode.jsonc` perms) + 3 advisory tools (`reason_check/reason_table/startup_table`)
  = **14 tools in 11 plugin files** (`ls .opencode/plugins/*.ts` → 11; v3 wrote "14 TS
  plugins total", conflating tools with files — corrected). Perms list 12 entries
  (11 `omt_*` + `reason_check`; `reason_table`/`startup_table` are plugin-provided,
  not permission-gated). `scripts/omt/*.py` = 13 CLIs (verified `ls`). Suite =
  **2103/2105 collected** (`uv run pytest --collect-only -q`, 2 deselected — not "2300+").
- **Test-file counts (v3's 206/189 are unreproducible — corrected):**
  `rg --files tests/scripts` → **103** total (**71** in `tests/scripts/omt/`,
  matching `.projects/README.md`'s "71+"); `rg --files tests/features` → **100**
  files in 52 dirs. v3's "`omt`×206 files / 189 feature files" matches no
  denominator re-run here (not `rg --files`, not `ls`, not with/without
  `__pycache__`) — treat as stale, quote the `rg --files` numbers with the command.
- **Boundary today (clean by discipline, not by test):** zero runtime imports
  either way (`rg ^import/^from` 2026-10-10: no `scripts.omt`/`.meta`/`opencode`
  imports from `src/`; reverse import-pattern hits only in
  `scripts/omt/bench/tasks.py:32,44`, both **inside triple-quoted fixture strings**
  `CHAT_REGRESSION_APPEND` / `MAJOR_TEST_CONTENT`, not runtime imports). Note the
  denominator: substring `rg agentx` finds **5 hits** (`:11,:12` path-strings
  `MODEL_FILE`/`UI_FILE`, `:32` + `:44` fixture-strings, `:35` path-string
  `MAJOR_SRC`) — T2 goldens must pin an **import-statement regex**, not a substring,
  with explicit exemptions for fixture-strings AND path-strings, or they will
  false-positive. No boundary test exists today (deferred T2).

## 1. Homes + `meta` suffix

- `.projects/meta/*` = harness-only. New slugs end `_meta` (e.g. `net_gate_meta`). Legacy `meta_*` accepted, grandfathered — no renames.
- `.projects/agentx/*` = product-only. No `meta` affix (e.g. `rag_v2`, `agentx_concurrent_development`, `petri_net_studio`).
- Bridge work lives under the owner side + `bridge:` tag in PROJECT.md Decisions log. No third home — **with one known tri-home exception:** `petri_net_studio` spans `tools/petri-net-studio/` (TS frontend+engine: `package.json`, `src/`, `tests/`, verified) + `src/agentx/model/petri_net/` (6 files) + `.projects/meta/petri_net_studio/` (§8 Q2). Recommendation (v4, was a question): scope `tools/` as product in the T1 audit with a one-line scoping rule; don't leave three legs uncovered. Alternative if you disagree: admit tri-home for this one case — but pick one, don't pretend two homes cover it.
- `project.py` stays single-root in v1 (`--help` → subcommands `{new,link,log,status,close,archive,reopen,sync,backfill}`; `rg OMT_PROJECTS_ROOT scripts/omt/project.py` → no hits — verified). `.projects/README.md`'s line "`OMT_PROJECTS_ROOT=.projects/agentx`" is therefore **draft-wrong / unexecutable**; running `sync` with a root override today would clobber `WORK.md ## Projects` (see `.projects/agentx/META.md` pending-moves table). Until T6, promotion is manual-scaffold-then-`link <feature> <project> --origin manual` (flag verified: `--origin {backfill,inferred,manual,scaffold}`, default `manual`; note arg order is feature-first — see UC8), never `project.py new` into `.projects/agentx/`.
- Current violation (acknowledged, not hidden): product-named `agentx_concurrent_development`, `rag_v2`, `petri_net_studio`, `agentx_1_0_0` (draft) still live under `.projects/meta/` with **no conforming `bridge:` tag** (see format note below). `.projects/agentx/META.md` pending-moves table is a **populated 4-row draft** (v3 wrongly called it "empty-by-design" — corrected: it lists exactly those four slugs, unexecuted); each move needs `link --origin manual` + ledger record — deferred, with approval only.
- `bridge:`-tag format (v4 pin — v3's claim tripped on prose): prose occurrences of
  `bridge:` exist in the wild (`meta_harness_11/PROJECT.md:50` "Harness↔agentx bridge:",
  `idea-002` "Sentinel bridge:") but **no conforming tag** (standalone `bridge:` token
  in a PROJECT.md Decisions-log section). T1 must grep the pinned format, not the substring.
- The convention (`.projects/README.md`) is hand-written, **untracked**, unenforced. Without T1 (audit table) + T2 (boundary test) it is a wish, not a gate. Say so to reviewers. V4 correction: it is not even committed — promotion must include it, or drop the mirror note.

## 2. Testing lanes (pending canary — zero moves in v1)

- Today (mixed, grandfathered, re-counted):
  `tests/{controllers,views,model,unit}` (product) beside
  `tests/scripts/` (103 files recursive; 71 in `tests/scripts/omt/`) beside
  `tests/features/` (100 files in 52 dirs, mixed).
- Target:
  `tests/agentx/**` (product lane) vs `tests/harness_meta/**` (harness lane, `*_meta.py` suffix on new files).
  Legacy files grandfathered with a mapping table in `harness_wrapper_split` T1 audit — no silent moves.
  **Neither target dir exists today** (`ls` 2026-10-10: no such directory) — any `pytest tests/agentx` / `tests/harness_meta` acceptance is T-gated, not runnable now (§7).
- Runs (target):
  `uv run pytest tests/agentx` (must pass with the four harness dirs renamed away — product-without-harness proof) vs
  `uv run pytest tests/harness_meta` (contract-pinned — harness-without-product proof) vs
  nightly full + `opencode_live` (integration proof).
- Gate: any `tests/` move needs canary (`omt_skip{scope:"tests"}`). This sandbox proposes the layout; it moves nothing.
- Known counterexample inside the product tree: `src/agentx/ui/test_omt_mvc_gate.py` (53 bytes; v3 called it "2-line `print('ok')`" — **wrong:** line 1 is `from agentx.model.session import Session`, a real product import; line 2 is `print('ok')`; zero test functions, top-level side effect, collected by no suite since it lives under `src/`). It is dead code with a misleading `test_` prefix. T1 disposition: delete it (no coverage depends on it) or move it to `tests/harness_meta/` with a real assertion — don't leave the split's own counterexample unmentioned.

## 3. Orthogonal mechanics (verdicts, not files)

- One mechanic = exactly five parts: CLI + gate predicate + ledger kinds + `tests/harness_meta/<m>_meta/` + doc SECTION.
  Missing any part = not a mechanic, just a script.
- Talk only via append to `.meta/.omt/ledger.jsonl` + named read-only projections (projection file list + "read-only = no writes outside append" pinned in T2). No direct runtime imports
  between `src/agentx/**` and `scripts/omt/**` / `scripts/session_inspect/**` (boundary goldens enforce, with the bench fixture-string + path-string exemption from §0).
- Enforcer = **ordered predicates over a preflight snapshot** (deterministic order, fixed sequence — verified in `.opencode/lib/enforcer/gate_driver.ts:308-315,451-452`: `g.nav(0)` → `g.protect(10)` → `g.receipt(20)` → `g.tests(30)` → `g.net(35)` → `g.phase(40)` → `g.think(50)` → `g.kb(55)` before-chain; `g.mvc(60)` → `g.tdd_after(70)` after-chain). "Pure, no I/O" as previously worded is false: `.opencode/lib/enforcer/` (12 files, verified `ls`) snapshots live state (net verdict, session, file content); predicates are pure *over the snapshot*. The pure helper precedent is `scripts/omt/net/gate.py` (`feature_050`, unchecked in v4 — cite, don't assert).
  Net = **one gate verdict (`g.net`), fail-open** — not "one predicate file". Net implementation is `scripts/omt/net/` (**20 `.py` files**, not the 6-file `{cli,gate,state,history,lock,sync_md}` slice v3 listed — the 6 are the core gate slice; the subsystem also holds `analysis, apply_selection, claim_handles, conformance, dispatch_runtime, errors, freshness, io, managed_ops, miner, model, verify_dispatch, workspace, worktree_lifecycle`, verified `ls`) + `META_NET.petri.json` + `supervisor.overlay` + enforcer wiring; net-down degrades to advisory, never blocks product or harness mechanics (see UC4, two Pre branches).
- Per-mechanic receipts are **T5 design, not current fact**: `scripts/omt/harnessc.py` still enforces the global `g.receipt` second-edit guard + batch stage (`receipt_fresh`, stage/clear — verified `rg`). T5 replaces it slice by slice; until then "bump one mechanic → re-receipt that slice only" is a goal. Don't cite it as landed.
- Tool counts: say which denominator you mean (11 `omt_*` MCP tools vs 14 tools in 11 plugin files vs 13 Python CLIs) whenever "11 tools" appears.
- Precedent for low-churn additives: `reason_check/table + startup_table` (no `omt_` prefix) added **zero registry rows** (still one `opencode.jsonc` perm line + plugin file each — "zero *registry* rows", not "zero rows"; note perms only gate `reason_check`, not `reason_table`/`startup_table`) — new advisory mechanics follow the same path (see UC6).

## 4. Allowed inversion

- Harness may write `# TA:` comment lines into `src/agentx/**` (30 lines across 18 files today — verified `rg -c`, top files `main_controller.py:5`, `react_view.py:5`; `omt_think list` on this PROPOSAL.md → 0 thoughts; preflight edit-clear 2026-10-10). TA-only diffs bypass `omt_phase`, still need `omt_think list` consult (think-gate applies, not skip-bypassable).
- `strip-TA === AST-identical` is **T4 work, not landed**: no such test exists today. (Holds almost surely for Python — comments don't reach the AST — but unproven, and TS-side TA has no stated rule.)
- Index stores `{location:product, owner:harness|product}` per thought so audits can tell who annotated what without reading diffs (design; not verified in index schema today).
- Any logic touch alongside TA = full phase required (no bypass).

## 5. Non-goals (v1 will NOT)

- No `harness/` top-level directory, no `src/` relocation, no `tests/` file moves.
- No multi-root `project.py sync`, no ledger schema change, no enforcer rewrite.
- No third home (`.projects/bridge/`), no new `omt_*` tool renames.
- No auto-promotion: sandbox → `.projects/` only on your explicit go (see UC8).
- No `opencode.jsonc` restore in this sandbox (see §8 Q5 — surfaced, fixed elsewhere via the harness-surface receipt flow, not from sandbox).

## 6. Migration (deferred, T1–T6 sketch — not started)

- T1 audit: legacy slug + test-file mapping table (grandfather list, incl. `test_omt_mvc_gate.py` delete-vs-move disposition + conforming-`bridge:`-tag backlog + `tools/`-as-product scoping line).
- T2 boundary tests: product-without-harness + harness-without-product goldens (import-statement regex with bench fixture-string + path-string exemptions from §0) + ledger projection contract pin.
- T3 lanes CI: split runs wired, nightly full kept green.
- T4 TA inversion test: `strip-TA === AST-identical` golden.
- T5 per-mechanic receipts: replace global rebuild gate slice by slice (design first).
- T6 multi-root sync: `project.py sync` covers both homes without clobbering `WORK.md`.
- Each T needs its own canary where it touches `tests/` or harness surface. Order is advisory; T2 can land before T1 is complete.

## 7. Acceptance (all T-gated — none runnable today)

- T3: `uv run pytest tests/agentx` green with the four harness dirs (`scripts/omt/`, `scripts/session_inspect/`, `.opencode/`, `.meta/`) renamed away (rename-away proof). **Blocked until target dirs exist (T1/T3).**
- T3: `uv run pytest tests/harness_meta` green with `src/agentx/` frozen (contract proof). **Blocked until target dirs exist.**
- UC0 (runnable now): `rm -rf sandbox/orthogonality_001_wrapper_split` leaves `git status` clean except the deletion itself (zero-churn proof). Trivially true today — sandbox is untracked (`??`), in no ledger/manifest — which also means it is invisible to the harness (`project.py status`, `workc`, nav index all ignore it).
- Ledger freshness (observer effect, record at receipt time): v3 pinned "2 rows"; v4 re-measurement shows **5 rows** (`think_consult`, `net_sync bootstrap rev 0`, `think_consult`, `phase docs/Programming unscoped:001`, `complete unscoped:001` — the last three are the v3 refine itself). Any receipt citing a row count must re-run `wc -l .meta/.omt/ledger.jsonl` at signing time.
- Startup stability (known-flaky today): file `WORK.compiled.md` rev 60 (10 options, NEXT=`agentx_concurrent_development`) vs live probe rev 0 (`next:none`, 0 claims) diverge by construction after bootstrap — "A–J IDs stable across a harness-only bump" can only be asserted once file and live agree; record both revs in the receipt.

## 8. Open questions (need your call)

1. Rename legacy `meta_*` slugs to `*_meta`, or grandfather forever? (Proposal: grandfather — renames churn WORK.md + ledger.)
2. `petri_net_studio` + `tools/`: accept v4 recommendation (scope `tools/petri-net-studio/` as product in T1, studio PROJECT.md carries a conforming `bridge:` tag only for harness-driven analysis slices)? If yes, Q2 closes without a tri-home.
3. Per-mechanic receipt format: extend `ledger.jsonl` kinds or sidecar `receipts/`? (Proposal: ledger kinds — single append path. Still T5 design.)
4. Ledger projection contract: which files are read-only projections of `.meta/.omt/ledger.jsonl` (`WORK.compiled.md`? `nav.index.jsonl`? `harness.ir.json`? `net_state.sidecar.json`? `WORK.md ## Projects`?)? (Proposal: pin the list in T2; "read-only = no writes outside append". `.meta/.omt/` today holds 7 files — verified `ls`.)
5. **NEW (v4, drift found outside the split): `git diff opencode.jsonc` shows the `"webfetch": "deny"` perm line removed (working-tree `M`), while `AGENTS.md` + `.meta/META_HARNESS.omt:74,145` still declare toplevel `webfetch` denied.** Restore the deny via the harness-surface receipt flow, or amend AGENTS.md/META_HARNESS through the same flow? Sandbox will not touch `opencode.jsonc`; surfacing here so the receipt for any promotion re-checks `git diff -- opencode.jsonc`.

## 9. Verification log (so reviewers don't re-measure)

- 2026-10-10 (v3): `pytest --collect-only` → 2103/2105 (2 deselected); `tests/agentx/`, `tests/harness_meta/` absent.
- 2026-10-10 (v3): `rg` boundary sweep clean at runtime (both directions); `bench/tasks.py` import-pattern hits `:32,:44` fixture-strings only.
- 2026-10-10 (v3): `opencode.jsonc` perms = 11 `omt_*` + `reason_check`; `.opencode/plugins/` = 11 `omt_*` + 3 advisory; `.opencode/lib/enforcer/` = 12 files; `scripts/omt/*.py` = 13.
- 2026-10-10 (v3): `project.py --help` = `{new,link,log,status,close,archive,reopen,sync,backfill}`, no root-override flag; `WORK.md ## Projects` (L33–87) meta-only.
- 2026-10-10 (v3): ledger `.meta/.omt/ledger.jsonl` = 2 rows; `net_state.sidecar.json` rev 0 `live_marking [1,1,0,1,1,1,1]`; `WORK.compiled.md` rev 60 vs live rev 0 (STALE by construction).
- 2026-10-10 (v3): `rg -c "# TA:" src/agentx` ≈ 30 lines / 18 files; no `strip-TA` test found; `rg bridge:` finds no live conforming tags.
- 2026-10-10 ~16:00 UTC (v4 re-measurement — corrections):
  `rg --files tests/scripts` → 103 (71 in `tests/scripts/omt/`); `rg --files tests/features` → 100 (52 dirs); v3's 206/189 unreproducible.
  `ls .opencode/plugins/*.ts` → 11 files for 14 tools (v3 "14 plugins" conflated tools/files).
  `ls scripts/omt/net/` → 20 `.py` files (v3 listed 6 — the gate slice, not the subsystem).
  `rg agentx scripts/omt/bench/tasks.py` → 5 hits (`:11,:12,:35` path-strings + `:32,:44` fixture-strings; v3 listed 2).
  `cat src/agentx/ui/test_omt_mvc_gate.py` → `from agentx.model.session import Session` + `print('ok')` (v3 "2-line print" wrong; zero test functions).
  `rg bridge:` → also hits `meta_harness_11/PROJECT.md:50` + `idea-002` prose (v3 "only proposal docs" wrong) — no *conforming* tag still holds under the §1 format pin.
  `cat .projects/agentx/META.md` → populated 4-row pending-moves draft (v3 "empty-by-design" wrong).
  `rg OMT_PROJECTS_ROOT scripts/omt/project.py` → no hits; `project.py link --help` → `--origin {backfill,inferred,manual,scaffold}` default `manual`, syntax `link <feature> <project>` (v3 arg order imprecise — fixed in UC8).
  `wc -l .meta/.omt/ledger.jsonl` → 5 (v3's "2 rows" rotted the same day via its own refine).
  `git status --short` → `M opencode.jsonc` (webfetch-deny removal) + `?? .projects/README.md` + `?? .projects/agentx/` + `?? sandbox/…` (authority + drift findings).
  Gate order verified: `gate_driver.ts:308-315,451-452` (`nav0/protect10/receipt20/tests30/net35/phase40/think50/kb55` + `mvc60/tdd_after70`).
  `rg -c "# TA:" src/agentx` → exactly 30 / 18 files (v3 "≈" confirmed exact); `ls tests/agentx`, `ls tests/harness_meta` → both absent (T-gated holds).
