# PROPOSAL_V7 — runtime-orthogonal, dev-coupled harness-wrapper split (canonical, sandbox only)

> Status: **draft proposal** (2026-10-10 V7, no approval, no promotion, no moves).
> Baselines frozen: `PROPOSAL.md` v4 + `USE_CASES.md` v4 + `CRITIQUE_V5.md` + `REFINE_V6.md`
> stay timestamped, never silently rewritten. This file is the single canonical
> refinement that merges them, closes what can be closed, and labels the rest T-gated.
> Mirror note: `.projects/README.md` is an **untracked draft** (`git status ??`,
> unreviewed, no ledger record — verified 2026-10-10), not a canonical home. This file
> **inlines** the homes rule with measurements and wins on conflict until both are
> promoted together. Do not cite `.projects/README.md` as authority.
> Sandbox changes nothing outside `sandbox/` (UC0 holds — untracked `??`, invisible to
> `project.py status`, `workc`, nav index; isolation proof, not value proof).

## 0. Terminology + pinned paths/counts (never pin a count without timestamp + command)

- **Product** = AgentX runtime + UI: `src/agentx/**`, `tools/petri-net-studio/`
  (scoped as product in V7 §1 decision), `shared/petri-net/` (product-owned contract,
  FORMAT.md LOCKED v1 + `conformance/analysis-v1/` 9 vectors), product docs/tests.
  Newcomer path `uv sync && uv run agentx` → console REPL (`c/r/f/a/t/d/m/h/q`) —
  zero harness knowledge required. Any T that breaks this path fails AgentX vision.
- **Harness (wrapper)** = META HARNESS process + tooling: `scripts/omt/**`,
  `scripts/session_inspect/`, `scripts/reason/`, `scripts/toolbox/`, `.meta/**`,
  `.opencode/**` (plugins `.opencode/plugins/` 11 files for 14 tools; predicates
  `.opencode/lib/enforcer/` 12 files). There is **no top-level `harness/` directory**;
  any "rename harness away" proof must list four dirs explicitly (§7):
  `scripts/omt/`, `scripts/session_inspect/`, `.opencode/`, `.meta/`.
- **Runtime-orthogonal, dev-coupled** (mandatory language — never bare "orthogonal").
  Runtime imports: zero both ways today (modulo fixture/path-string exemptions below).
  Dev-time: false — renaming `.opencode/` kills the `omt_*` dev loop; renaming `.meta/`
  kills ledger/projections/`WORK.md`; lanes + build roots unscoped (§2). Any UC/T that
  says bare "orthogonal" without the qualifier is rejected in review.
- **Bridges (two declared, one is an inversion):** (a) append-only ledger at
  `.meta/.omt/ledger.jsonl` + named read-only projections (contract pinned in T2 —
  counts rot every refine: v3 "2 rows" → v4 "5 rows" → v5/v6 "9 rows" via
  `wc -l .meta/.omt/ledger.jsonl`; observer effect — the refine itself appends
  `think_consult` + `phase` + `complete`; first `think_consult` embeds 60+ paths,
  i.e. wider than "minimal" suggests; rule from now on: format
  "`N` rows at `<date -u +%Y-%m-%dT%H:%M:%SZ>` via `wc -l .meta/.omt/ledger.jsonl`,
  re-count at signing"), (b) `# TA:` comment-line inversion (§4 — honest framing is
  "one declared inversion", not "two minimal bridges").
- **Home** = where a PROJECT.md lives (`.projects/meta/` vs `.projects/agentx/`).
  **Owner** = who may change it. **Location** = where the file sits. A bridge file
  has one owner and may sit anywhere; mismatch declared, not hidden.
- **Counts (state the denominator every time):** 11 `omt_*` MCP tools
  (`phase,skip,complete,status,tdd,nav,think,kb_nav,q,net,session` per `opencode.jsonc`
  perms) + 3 advisory (`reason_check/reason_table/startup_table`) = **14 tools in
  11 plugin files** (`ls .opencode/plugins/*.ts` → 11; "14 plugins" conflates tools
  with files). Perms list 12 entries (11 `omt_*` + `reason_check`; `reason_table` /
  `startup_table` plugin-provided, not permission-gated). `scripts/omt/*.py` = 13 CLIs
  (`ls`). Suite = **2103/2105 collected** (`uv run pytest --collect-only -q`,
  2 deselected — not "2300+", not "2370", not "2085+283" without citing which side).
- **Test-file denominators (`rg --files` with command, not stale 206/189):**
  `rg --files tests/scripts` → **103** total (**71** in `tests/scripts/omt/`);
  `rg --files tests/features` → **100** files in 52 dirs. Retire v3's 206/189.
- **Boundary today (clean by discipline, not by test):** zero runtime imports either way
  (`rg ^import/^from`: no `scripts.omt`/`.meta`/`opencode` imports from `src/`; reverse
  hits only in `scripts/omt/bench/tasks.py:32,44`, both **inside triple-quoted fixture
  strings**, not runtime). Denominator warning: substring `rg agentx` finds **5 hits**
  (`:11,:12` + `:35` path-strings + `:32,:44` fixture-strings) — T2 goldens must pin an
  **import-statement regex** (Python `ast` + TS imports) with explicit fixture + path
  exemptions in a versioned manifest, never a substring, or they false-positive.
  No boundary test exists today (deferred T2).

## 1. Homes + `meta` suffix (decision, not recommendation)

- `.projects/meta/*` = harness-only. New slugs end `_meta` (e.g. `net_gate_meta`).
  Legacy `meta_*` accepted, grandfathered — no renames (renames churn WORK.md + ledger).
  **Decision V7 (closes Q2, was v4 recommendation):** scope `tools/petri-net-studio/`
  as product + `shared/petri-net/` as product-owned contract in T1; studio PROJECT.md
  carries a conforming `bridge:` tag **only** for harness-driven analysis slices.
  Elevate studio's `check-independence + conformance` as the T2 template (Oracle §E
  is that template generalized). Until then T1 cannot close. Alternative if you
  disagree: admit scoped tri-home for this one case — but pick one, don't pretend
  two homes cover four legs (`tools/` + `src/agentx/model/petri_net/` 6 files +
  `.projects/meta/petri_net_studio/` + `shared/petri-net/`).
- `.projects/agentx/*` = product-only. No `meta` affix (e.g. `rag_v2`,
  `agentx_concurrent_development`, `petri_net_studio`).
- Bridge work lives under the owner side + `bridge:` tag in PROJECT.md Decisions log.
  No third home. `bridge:`-tag format pin (V7 — substring tripped v3): standalone
  `bridge:` token in Decisions-log section. Prose hits (`meta_harness_11/PROJECT.md:50`
  "Harness↔agentx bridge:", `idea-002` "Sentinel bridge:") are correctly excluded.
  **No conforming tags exist yet** — backlog for T1. T1 greps the pinned format, not substring.
- `project.py` stays single-root in v1 (`--help` → `{new,link,log,status,close,archive,
  reopen,sync,backfill}`; `rg OMT_PROJECTS_ROOT scripts/omt/project.py` → no hits).
  `.projects/README.md`'s "`OMT_PROJECTS_ROOT=.projects/agentx`" is **draft-wrong /
  unexecutable**; `sync` with a root override today would clobber `WORK.md ## Projects`
  (see `.projects/agentx/META.md` pending-moves table). Until T6, promotion is
  manual-scaffold-then-`link <feature> <project> --origin manual` (flag verified:
  `--origin {backfill,inferred,manual,scaffold}`, default `manual`; arg order
  feature-first — see UC8), never `project.py new` into `.projects/agentx/`.
- Current violation (acknowledged, not hidden): product-named
  `agentx_concurrent_development`, `rag_v2`, `petri_net_studio`, `agentx_1_0_0` (draft)
  still live under `.projects/meta/` with **no conforming `bridge:` tag**.
  `.projects/agentx/META.md` pending-moves table is a **populated 4-row draft**
  (lists exactly those four slugs, unexecuted); each move needs `link --origin manual`
  + ledger record — deferred, with approval only.
- Convention (`.projects/README.md`) hand-written, **untracked**, unenforced. Without
  T1 (audit) + T2 (boundary test) it is a wish, not a gate. Promotion must include it
  (fixing the `OMT_PROJECTS_ROOT` line) or drop the mirror note — never carry two
  untracked authorities (`.projects/README.md` + `.projects/agentx/META.md` placeholder)
  into T1.

## 2. Testing lanes (pending canary — zero moves in v1)

- Today (mixed, grandfathered, re-counted):
  `tests/{controllers,views,model,unit}` (product) beside `tests/scripts/` (103 files;
  71 in `tests/scripts/omt/`) beside `tests/features/` (100 files in 52 dirs, mixed).
- Target: `tests/agentx/**` (product lane) vs `tests/harness_meta/**` (harness lane,
  `*_meta.py` suffix on new files). Legacy files grandfathered with a mapping table in
  T1 audit — no silent moves. **Neither target dir exists today** (`ls`: no such
  directory) — any `pytest tests/agentx` / `tests/harness_meta` acceptance is T-gated (§7).
- T1 audit scope (V7 — v4 covered only `scripts+features`): `tests/scripts (103) +
  tests/features (100)` **plus** `tests_automated/`, `tests/test_sandbox/`, `toolbox/`
  tests, `tools/*/tests`, `.sandbox/` with a one-line scope-or-exclude each; build roots
  (`pyproject.toml / uv.lock / .venv / .python-version`) declared as **shared prerequisite**
  (neither lane claims them; rename-away proofs silently depend on them staying put —
  declare or T3 unreproducible clean-checkout). `.workflows/` is catalog **above** harness
  (`# Rules` line 1 follow-vs-override) — NOT harness-owned, NOT product-owned; scope line only.
- Runs (target): `uv run pytest tests/agentx` (must pass with four harness dirs renamed
  away — product-without-harness proof) vs `uv run pytest tests/harness_meta`
  (contract-pinned — harness-without-product proof) vs nightly full + `opencode_live`.
- Gate: any `tests/` move needs canary (`omt_skip{scope:"tests"}`). This sandbox proposes
  layout; it moves nothing.
- Known counterexample inside product tree: `src/agentx/ui/test_omt_mvc_gate.py`
  (53 bytes: line 1 `from agentx.model.session import Session` — real product import;
  line 2 `print('ok')`; zero test functions, top-level side effect, collected by no suite
  since under `src/`). Dead code with misleading `test_` prefix. **T1 row #1:**
  delete it (no coverage depends on it) or move to `tests/harness_meta/` with a real
  assertion — don't leave the split's own counterexample unmentioned; it self-falsifies
  UC1 Post until closed.

## 3. Orthogonal mechanics (verdicts, not files)

- One mechanic = exactly five parts: CLI + gate predicate + ledger kinds +
  `tests/harness_meta/<m>_meta/` + doc SECTION. Missing any part = not a mechanic, just a script.
- Talk only via append to `.meta/.omt/ledger.jsonl` + named read-only projections
  (projection list + "read-only = no writes outside append" pinned in T2 — see Q4).
  No direct runtime imports between `src/agentx/**` and `scripts/omt/**` /
  `scripts/session_inspect/**` (boundary goldens enforce, with bench fixture + path
  exemptions from §0).
- Enforcer = **ordered predicates over a preflight snapshot** (deterministic order —
  verified `gate_driver.ts:308-315,451-452`: `g.nav(0)` → `g.protect(10)` →
  `g.receipt(20)` → `g.tests(30)` → `g.net(35)` → `g.phase(40)` → `g.think(50)` →
  `g.kb(55)` before-chain; `g.mvc(60)` → `g.tdd_after(70)` after-chain). "Pure, no I/O"
  as previously worded is false: `.opencode/lib/enforcer/` (12 files) snapshots live
  state (net verdict, session, file content); predicates pure *over the snapshot*.
  Precedent: `scripts/omt/net/gate.py` (feature_050).
  Net = **one gate verdict (`g.net`), fail-open** — not "one predicate file". Net impl is
  `scripts/omt/net/` (**20 modules + `__init__.py` = 21 files** — the 6-file
  `{cli,gate,state,history,lock,sync_md}` is the core gate slice; subsystem also holds
  `analysis, apply_selection, claim_handles, conformance, dispatch_runtime, errors,
  freshness, io, managed_ops, miner, model, verify_dispatch, workspace,
  worktree_lifecycle`) + `META_NET.petri.json` + `supervisor.overlay` + enforcer wiring;
  net-down degrades to advisory, never blocks product or harness mechanics (UC4, two Pre branches).
- Per-mechanic receipts are **T5 design, not current fact**: `scripts/omt/harnessc.py`
  still enforces global `g.receipt` second-edit guard + batch stage. T5 replaces it slice
  by slice; until then "bump one mechanic → re-receipt that slice only" is a goal.
- Tool counts: state the denominator every time (11 `omt_*` vs 14-in-11 vs 13 CLIs).
  Admission carried: which plugin file provides `phase/skip/complete/tdd` is unchecked
  (11 files include `enforcer` gate, not tool) — T1 pins file→tool map or states
  enforcer-owned, or the "11 files" claim stays half-cited.
- Precedent for low-churn additives: `reason_check/table + startup_table` (no `omt_`
  prefix) added **zero registry rows** (still one `opencode.jsonc` perm line + plugin file
  each — "zero *registry* rows", not "zero rows"; perms gate only `reason_check`) —
  new advisory mechanics follow the same path (Oracle §E does).

## 4. Allowed inversion

- Harness may write `# TA:` comment lines into `src/agentx/**` (30 lines across 18 files
  — `rg -c`, top `main_controller.py:5`, `react_view.py:5`; `omt_think list` on sandbox
  proposal docs → 0). TA-only diffs bypass `omt_phase`, still need `omt_think list`
  consult (think-gate applies, not skip-bypassable).
- `strip-TA === AST-identical` is **T4 work, not landed**: no such test exists today.
  (Holds almost surely for Python — comments don't reach AST — but unproven; TS-side TA
  has no stated rule — Oracle E4 closes both: Python `ast.dump` identical, TS
  `tsc --noEmit` clean + snapshot-identical.)
- Index stores `{location:product, owner:harness|product}` per thought so audits tell who
  annotated what without reading diffs (design; not verified in index schema today).
- Any logic touch alongside TA = full phase required (no bypass).

## 5. Non-goals (v1 will NOT)

- No `harness/` top-level directory, no `src/` relocation, no `tests/` file moves.
- No multi-root `project.py sync`, no ledger schema change (kinds extend, schema frozen),
  no enforcer rewrite.
- No third home (`.projects/bridge/`), no new `omt_*` tool renames (Oracle is advisory CLI,
  `reason_check` precedent — zero registry rows).
- No auto-promotion: sandbox → `.projects/` only on your explicit go (UC8).
- No `opencode.jsonc` restore in this sandbox (§8 Q5 — surfaced, fixed elsewhere via
  harness-surface receipt flow, not from sandbox).

## 6. Migration (deferred, T1–T7 sketch — not started; order advisory, T2 can precede T1)

- T1 audit: legacy slug + test-file mapping table (grandfather list incl.
  `test_omt_mvc_gate.py` disposition + conforming-`bridge:`-tag backlog + `tools/`-as-product
  + `shared/`-as-contract scoping lines + file→tool map pin + full test-scope table §2).
- T2 boundary tests: product-without-harness + harness-without-product goldens
  (AST import firewall with versioned exemption manifest §0) + ledger projection contract
  pin (Q4 list + read-only test). Studio `check-independence + conformance` is the template.
- T3 lanes CI: split runs wired, nightly full kept green (shared build-roots prerequisite declared).
- T4 TA inversion test: `strip-TA` golden (Python + TS rules).
- T5 per-mechanic receipts: replace global rebuild gate slice by slice (design first).
- T6 multi-root sync: `project.py sync` covers both homes without clobbering `WORK.md`.
- T7 Oracle `split_proof_meta` v2 (§E): CLI + predicate + kinds + tests + SECTION; runs
  against current mixed layout with exemption manifest in v1 (zero moves), lanes migrate under it.
- Each T needs its own canary where it touches `tests/` or harness surface. Each T cites an
  `omt_session` source (`capture`/`profile`/`query`) or benchmark golden; token/cost claims
  need real-token measurement (harness_reason precedent: kernel 1,321,729 vs harness 381,919).
  Newcomer-cost check per T: "can a student still `uv run agentx` → `c` with zero harness knowledge?"

## 7. Acceptance (all T-gated except UC0 — none of the lane proofs runnable today)

- T3: `uv run pytest tests/agentx` green with four harness dirs (`scripts/omt/`,
  `scripts/session_inspect/`, `.opencode/`, `.meta/`) renamed away. **Blocked until T1/T3.**
- T3: `uv run pytest tests/harness_meta` green with `src/agentx/` frozen. **Blocked until T1/T3.**
- UC0 (runnable now): `rm -rf sandbox/orthogonality_001_wrapper_split` leaves `git status`
  clean except the deletion itself. Trivially true today — sandbox untracked (`??`), in no
  ledger/manifest — which also means invisible to harness (`project.py status`, `workc`,
  nav index all ignore it). Isolation proof, not value proof.
- T7 (runnable once Oracle E4 lands — the only executable close in V7):
  `uv run scripts/omt/split_proof.py prove --lane both` → two certs green +
  `verify` byte-identical + `attest-bridge` zero backlog except studio slices +
  `newcomer-probe` REPL answers (§E).
- Ledger freshness (observer effect, re-count at signing — never pin): record
  "`N` rows at `<date -u>` via `wc -l .meta/.omt/ledger.jsonl`" in every receipt.
- Startup stability (known-flaky): file `WORK.compiled.md` rev 60 (10 options,
  NEXT=`agentx_concurrent_development`) vs live probe rev 0 (`next:none`, 0 claims) diverge
  by construction after bootstrap — "A–J IDs stable across a harness-only bump" assertable
  only once file and live agree; record both revs in every receipt.

## 8. Open questions (need your call — Q2 closed in V7)

1. Rename legacy `meta_*` slugs to `*_meta`, or grandfather forever? (Proposal: grandfather —
   renames churn WORK.md + ledger.)
2. **CLOSED in V7 (decision §1):** scope `tools/petri-net-studio/` as product +
   `shared/petri-net/` as product-owned contract in T1; studio PROJECT.md carries conforming
   `bridge:` tag only for harness-driven analysis slices. If you reject, admit scoped tri-home —
   but pick one.
3. Per-mechanic receipt format: extend `ledger.jsonl` kinds or sidecar `receipts/`?
   (Proposal: ledger kinds — single append path. Still T5 design.)
4. Ledger projection contract: which files are read-only projections of
   `.meta/.omt/ledger.jsonl`? (Proposal to pin in T2: `WORK.compiled.md`,
   `nav.index.jsonl`, `harness.ir.json`, `net_state.sidecar.json`, `WORK.md ## Projects`;
   "read-only = no writes outside append" test. `.meta/.omt/` today holds 7 files.)
5. **OPEN drift outside the split: `git diff opencode.jsonc` shows the `"webfetch": "deny"`
   perm line removed (working-tree `M`), while `AGENTS.md` + `.meta/META_HARNESS.omt:74,145`
   still declare toplevel `webfetch` denied.** Restore the deny via the harness-surface
   receipt flow, or amend AGENTS.md/META_HARNESS through the same flow? Sandbox will not
   touch `opencode.jsonc`; every promotion pre-check re-runs `git diff -- opencode.jsonc`.

## E. SOTA addition — `split_proof_meta` v2: proof-carrying membrane with ephemeral overlays

**Problem.** v4/v5 prove nothing executable: lanes don't exist, boundary has no test, TA has
no golden, ledger has no contract, rename-away is a paragraph. Reviewers re-run a dozen
commands to trust any claim. Studio solved this class with `check-independence` +
byte-identical `conformance` vectors — but nobody generalized the pattern. V6 proposed the
Oracle; V7 hardens it into a closable mechanic.

**Idea.** One new harness mechanic that turns every orthogonality claim into a deterministic,
content-addressed, byte-identical certificate ≤2 KiB, produced in an **ephemeral overlay**
(`git worktree` + tmpfs copy, never a rename in the dev tree), **provenance-bound** to ledger
+ `omt_session` evidence, **budget-capped** (`preflight` text +0), **zero-ceremony for devs**
(CI-strict / local-advisory split — MH6 ceremony-meter lesson). Dogfoods §3's own rule:
*one mechanic = exactly five parts*. No new `omt_*` tool (advisory CLI only, `reason_check`
precedent — zero registry rows).

- **E1. CLI `scripts/omt/split_proof.py` (the oracle).** Verbs:
  `prove --lane product|harness|both --overlay tmpfs` (copies tree minus four harness dirs
  for product-lane / minus frozen `src/agentx/` for harness-lane, runs the lane suite, emits
  cert), `verify <cert.json>` (re-runs, asserts byte-identical minus timestamps),
  `attest-bridge` (checks conforming `bridge:` format + owner/location index),
  `newcomer-probe` (boots `uv run agentx` → sends `c` → asserts REPL answers with zero
  harness env — the AgentX-vision guard). Output: canonical JSON LOCKED v1 (field order fixed,
  like `shared/petri-net/FORMAT.md`): `{oracle, lane, file_rev, live_rev, ledger_sha,
  firewall_verdict, ta_ast_hash, newcomer, tokens_ms, cert_sha}`.
- **E2. Gate predicate `g.split_proof` (pure over preflight snapshot, ordered after
  `g.net(35)`, before `g.phase(40)`).** Reads cert + snapshot (net verdict, file list, ledger
  sha); never runs the suite itself (no I/O in predicate — §3 correction, enforced).
  Fail-open locally (advisory), fail-closed in CI (`--strict`). Second-edit receipt flow reuses
  T5 slices once landed; until then global `g.receipt` still guards.
- **E3. Ledger kinds `split_proof.{cert,attest}` (append-only narrow waist).** Each `prove`
  appends one `cert` row (cert_sha + lane + ledger_sha chain — hash-linked, Merkle-style, so
  projection drift detectable). Q4 answered by the T2 pin (§8.4). Schema change stays a
  non-goal — kinds extend, schema doesn't.
- **E4. Tests `tests/harness_meta/split_proof_meta/` (the T2/T3/T4 closure).**
  `test_firewall_meta.py` — **AST import firewall, not substring**: parses Python `ast` + TS
  imports; bench fixture-strings (`tasks.py:32,44`) + path-strings (`:11,:12,:35`) live in a
  versioned exemption manifest (5-hit false-positive class dies).
  `test_rename_away_meta.py` — overlay lane proofs (product-without-harness green,
  harness-without-product contract-pinned; build roots declared shared prerequisite).
  `test_ta_strip_meta.py` — closes T4: `strip-TA === ast.dump-identical` (Python; TS rule:
  comment-strip === `tsc --noEmit` clean + snapshot-identical).
  `test_newcomer_meta.py` — newcomer probe (console boot, zero harness knowledge).
  All emit byte-identical certs (Studio `conformance` precedent).
- **E5. Doc SECTION `SECTION:split_proof` (nav-indexed, budgeted).** States denominators every
  time (11 `omt_*` vs 14-in-11 vs 13 CLIs), the 20+1 net pin, the ledger-count rule, the
  four-dir rename list, the exemption manifest path. Derives at projection time where possible
  (harnessc precedent — no hand-mirrored constants).

**Why state-of-the-art.** Proof-carrying lane certificates (Sigstore/reproducible-builds
attestations, but ≤2 KiB harness-native); hermetic overlay proofs (Bazel/Nix hermeticity,
worktree-cheap, no daemon); AST firewall with living exemptions (Buck2 visibility, docs-first);
hash-chained ledger narrow waist (Merkle projection manifest); evidence-bound evolution
(`omt_session profile/query` + benchmark goldens + real-token measurement per cert —
harness_reason precedent); ceremony-meter safe (CI-strict / local-advisory). Nothing in v4/v5
proposes anything executable — this is the first mechanic that makes the split falsifiable.

**Cost.** One CLI file + one predicate + two ledger kinds + one test dir + one SECTION.
Zero `omt_*` renames, zero `src/` moves, zero `tests/` moves in v1 (Oracle runs against current
mixed layout with exemption manifest; lanes migrate under it in T1–T3). Token cost: one
`--help` line + cert schema (~300 B); `preflight` text +0.

**Acceptance (T-gated until E4 lands — unlike all of §7 today, this one becomes runnable):**
`prove --lane both` → two certs green + `verify` byte-identical + `attest-bridge` zero backlog
except studio slices + `newcomer-probe` REPL answers. Until then this section is design,
labelled as such.

**Vision fit.** Meta Harness: preserves mechanical enforcement untouched in v1 (non-goals hold);
every T carries evidence (D9); zero unbudgeted surface (suffix/tags/lanes docs until gated —
ceremony-meter safe). AgentX: newcomer path untouched and probed per-cert; Studio elevated from
example to template; product pays zero ceremony (CI-only, local advisory) for an
attributable-failure win (UC5 real once lanes + Oracle land).

## 9. Verification log (re-measure at signing — do not quote stale rows)

- Rule: every receipt re-runs `wc -l .meta/.omt/ledger.jsonl` with `date -u`, `git status
  --short`, `git diff -- opencode.jsonc`, `WORK.compiled.md` rev + live probe rev. Counts
  without timestamp + command are rejected in review.
- Baselines carried (v4 §9 / v5 §E / v6 §F — re-verify or drop before promotion):
  suite 2103/2105 (2 deselected); `tests/agentx/`, `tests/harness_meta/` absent;
  `rg --files tests/scripts` 103 (71 in `omt/`); `rg --files tests/features` 100;
  `ls .opencode/plugins/*.ts` 11 for 14 tools; perms 11 `omt_*` + `reason_check`;
  `.opencode/lib/enforcer/` 12 files; `scripts/omt/*.py` 13; `scripts/omt/net/*.py` 21 inc
  `__init__` (20 modules); `.meta/.omt/` 7 files; `rg -c "# TA:" src/agentx` 30 / 18 files;
  no `strip-TA` test; `test_omt_mvc_gate.py` real import + `print`, zero fns;
  `rg bridge:` prose hits only, zero conforming tags; `.projects/agentx/META.md` placeholder +
  populated 4-row pending-moves draft; `WORK.compiled.md` rev 60 vs live rev 0 STALE;
  `git status` → `M opencode.jsonc` (webfetch-deny removal) + `?? .projects/README.md` +
  `?? .projects/agentx/` + `?? sandbox/…`; gate order `gate_driver.ts:308-315,451-452`.
- Carried unchecked (verify or drop before promotion): DSL 277 records, `tests/features`
  52 dirs, `idea-002` prose hit, `phase/skip/complete/tdd` provider mapping.

## Promotion (UC8 — the only way out of sandbox, on your explicit go only)

Manual scaffold `.projects/agentx/harness_wrapper_split/{PROJECT.md,CURRENT_STATE.md}` →
`project.py link <feature> <project> --origin manual` per pending move (feature-first) →
ledger records → multi-root sync only after T6. Never `project.py new` into
`.projects/agentx/`; never `sync` with root override before T6 (clobbers `WORK.md`).
Pre-checks at signing: `git diff -- opencode.jsonc` (Q5 resolved first) +
`wc -l ledger.jsonl` + `git status --short` + file rev + live rev. Then sandbox deleted via
UC0 or archived.
