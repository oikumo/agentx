# CRITIQUE_V5 — critical review + vision alignment (addendum, does not rewrite v4)

> Status: **draft critique** (2026-10-10 ~16:20 UTC, no approval, no promotion, no moves).
> Method: re-ran the proposal's own commands; read root `README.md` end-to-end
> (1293 lines); inspected workspace root (30 entries), `.projects/`, `scripts/`,
> `src/agentx/`, `tools/`, `tests/`. v4 `PROPOSAL.md` / `USE_CASES.md` stay as
> timestamped baselines — this file corrects without silent rewrite.
> Sandbox changes nothing outside `sandbox/` (UC0 holds).

## A. Workspace — where things actually live

- **Product (AgentX runtime + UI):** `src/agentx/` (`__init__, main, model/, ui/, agent/, utils/` —
  `model/` holds `ai, chat, rag, rag_v2, petri_net (6 files), session, react, coding, program/`;
  `agent/` nests its own MVC), `tools/petri-net-studio/` (Vite+React+TS, standalone —
  `npm run check-independence` asserts zero cross-boundary imports), `shared/petri-net/`
  (FORMAT.md LOCKED v1 + examples — the canonical contract, a **fourth leg** v4 omits),
  product docs/tests. Newcomer path is `uv sync && uv run agentx` → console REPL
  (`c/r/f/a/t/d/m/h/q`) — zero harness knowledge required. That path must survive any split.
- **Harness (META HARNESS wrapper):** `scripts/omt/` (13 CLIs, verified `ls`),
  `scripts/session_inspect/` + `scripts/reason/` + `scripts/toolbox/`,
  `.meta/` (DSL `.meta/META_HARNESS.omt` 277 records + software_development_process corpus +
  `.meta/.omt/` 7 files: `META_NET.petri.json, harness.ir.json, ledger.jsonl,
  nav.index.jsonl, net.lock, net_state.sidecar.json, supervisor.overlay.json`),
  `.opencode/` (11 plugin files: enforcer + 7 `omt_*` feature plugins + `reason_check/table,
  startup_table`; 12 enforcer lib files; perms gate 11 `omt_*` + `reason_check`).
  Net subsystem is **21 files inc `__init__.py` = 20 modules** (v4 "20 `.py` files"
  is right excl `__init__` — say so explicitly from now on).
- **Mixed / unscoped (the split does not yet cover):** `tests/` (product
  `controllers, views, model, unit` + harness `tests/scripts/` 103 files + mixed
  `tests/features/` 100 files in 52 dirs — v4 denominators confirmed), plus
  `tests_automated/`, `tests/test_sandbox/`, `toolbox/`, `.sandbox/`, `.workflows/`
  (catalog **above** the harness, `# Rules` line 1 declares follow-vs-override),
  `.projects/` (meta + agentx + untracked `README.md`), `pyproject.toml / uv.lock /
  .venv / .python-version` (build roots — neither lane claims them; rename-away
  proofs silently depend on them staying put).

## B. Claim-by-claim verdicts (be critical)

| # | v4 claim | Verdict |
|---|---|---|
| 0 | Orthogonal = either side builds/tests/ships absent the other, 2 bridges | **Overclaims.** Runtime imports: holds (zero both ways, modulo fixture/path-string exemptions). **Dev-time: false** — renaming `.opencode/` kills the `omt_*` dev loop; renaming `.meta/` kills ledger/projections/`WORK.md`; lanes + build roots unscoped. Split must say **runtime-orthogonal, dev-coupled** or it will fail its own T3. |
| 1 | Homes + `_meta` suffix, grandfather `meta_*`, bridge-tag, no third home | **Mostly holds, one contradiction.** Suffix rule + grandfather (no renames) is the lowest-churn workable choice. `bridge:` format pin (standalone token in Decisions log, not substring) is a real fix — prose hits (`meta_harness_11:50`, `idea-002`) are correctly excluded. But **non-goal "no third home" contradicts `petri_net_studio`** (tools/ + src/ + .projects/meta/ + shared/ = four legs). v4's "scope tools/ as product" recommendation is right — promote it to a decision, add `shared/petri-net/` as product-owned contract, or admit a scoped tri-home. Don't ship the contradiction into T1. |
| 2 | Testing lanes `tests/agentx` vs `tests/harness_meta` | **Direction right, scope incomplete.** Target layout is clean; grandfather + mapping table + canary gate are honest. Gaps: target dirs don't exist (T-gated correctly); audit scope covers only `tests/scripts + tests/features` — `tests_automated/, tests/test_sandbox/, toolbox/ tests, tools/*/tests, .sandbox/` unscoped; `test_omt_mvc_gate.py` disposition (delete vs move-with-assertion) is correctly surfaced — keep it as T1's first row, it self-falsifies UC1 until closed. |
| 3 | Mechanics as verdicts (5 parts, ledger-only talk, ordered predicates, fail-open net, T5 receipts) | **Holds with two downgrades.** Gate order cited (`gate_driver.ts:308-315,451-452`: nav0/protect10/receipt20/tests30/net35/phase40/think50/kb55 + mvc60/tdd_after70) verified. "Predicates pure over snapshot" correction stands. Downgrades correctly kept: per-mechanic receipts = T5 design (global `g.receipt` still enforced); tool denominators must always be stated (11 `omt_*` vs 14-in-11 vs 13 CLIs). Open: **which plugin file provides `phase/skip/complete/tdd`?** (11 files include `enforcer` which is gate, not tool — mapping unchecked; pin or admit). |
| 4 | TA inversion (`strip-TA === AST-identical` T4, index owner/location) | **Wish, correctly labelled.** Bypass rule is discipline-only until T4; TS-side TA rule unstated; index schema unverified. Keep, but don't let any UC depend on it pre-T4. Note bridge (b) is an **inversion, not orthogonality** — the honest framing is "one declared inversion", not "two minimal bridges". |
| 5 | Ledger as minimal bridge | **Wider than claimed.** Append-only holds; minimal does not — first `think_consult` row embeds 60+ paths. Ledger schema stability *is* the bridge contract, yet schema change is a non-goal. Pin the projection list (Q4: `WORK.compiled.md`? `nav.index`? `harness.ir`? `net_state.sidecar`? `WORK.md ## Projects`?) in T2 **before** claiming the bridge is stable. Counts rot on every refine (v3 "2 rows" → v4 "5 rows" → **9 rows at ~16:20 UTC today**, the v4 refine itself appended 4). Rule from now on: **never pin a count without timestamp + `wc -l` command; receipts re-count at signing.** |
| 6 | Acceptance T-gated, UC0 trivially true | **Honest and keep.** Marking non-runnable steps T-gated instead of readable-as-runnable is the proposal's best habit. UC0's honesty note (isolation proof, not value proof; invisible to `project.py status/workc/nav`) must stay verbatim. Startup STALE (`WORK.compiled.md` rev 60 NEXT=`agentx_concurrent_development` vs live rev 0 `next:none`) correctly blocks asserting stable A–J IDs — record both revs in every receipt. |
| 7 | Authority (`.projects/README.md` untracked + `OMT_PROJECTS_ROOT` unexecutable) | **Correctly demoted, still half-cited.** `rg OMT_PROJECTS_ROOT project.py` → no hits; `link` syntax is `link <feature> <project> --origin manual` (feature-first). Until promotion, "inlines and wins on conflict" creates a **second** authority. Fix: promote the convention file together with the sandbox or drop the mirror note; don't carry two untracked authorities (`.projects/README.md` + `.projects/agentx/META.md` placeholder) into T1. |
| 8 | Q5 `opencode.jsonc` webfetch-deny removal | **Real drift, still open, correctly out-of-scope for sandbox.** Re-verified ~16:20 UTC: `git diff` shows `-      "webfetch": "deny",` while `AGENTS.md` + `.meta/META_HARNESS.omt:74,145` still declare deny. Restore via harness-surface receipt flow, never from sandbox. Every promotion pre-check must re-run `git diff -- opencode.jsonc`. |

## C. Vision alignment (root `README.md`, 1293 lines, read end-to-end)

**Meta Harness vision** = proof a coding agent can be *mechanically* constrained to
Analysis→Design→Programming→Testing with visible auditable artifacts; single-source DSL
(`.meta/META_HARNESS.omt` → `harnessc build` → AGENTS/opencode.jsonc/IR/nav-index,
drift-tested); token discipline (every prompt/session byte budgeted); gates, not willpower;
self-evolution **evidence-driven** via `omt_session` Tier-2 (usage/cost hotspots, traces,
failure witnesses, labeled experiments, provenance-bound export; `run` gated, pilot unexecuted).
The split **helps** this vision iff: (a) it preserves mechanical enforcement untouched in v1
(non-goals hold); (b) every T carries evidence (`omt_session capture/query/profile`,
benchmark goldens like 093's 17, real-token measurement like harness_reason) — currently
missing, add it; (c) it never adds unb budgeted surface (suffix/tags/lanes are docs until
gated — say so). It **hurts** iff bridge tags / lane dirs / dual homes become ceremony
without gates (MH6 ceremony-meter lesson).

**AgentX vision** = educational console REPL (chat/rag/fast/advanced/react/coding/models) +
standalone Petri Net Studio (exact engine parity, conformance vectors, independence-checked) +
LangChain/LangGraph; MVC++ strict; ~2.3k tests. The split **helps** iff: (a) newcomer path
(`uv run agentx`, `c/r/f/a/t/d/m`) is untouched and runnable with zero harness knowledge;
(b) Studio is elevated as the **exemplar** of the claimed independence (it already ships
`check-independence` + `conformance` — the only legs with proofs); (c) product test counts get
one source (README "2,300+ / 2085+283" vs measured 2103/2105 collected — reconcile or cite
both with commands). It **hurts** iff product devs pay harness ceremony (bridge tags,
owner/location bookkeeping) with no attributable-failure win (UC5's promise).

**Net verdict:** the split intent is aligned with both visions; v4's honesty (T-gated
acceptance, counterexample admission, drift surfacing) *is* the harness vision in miniature.
What is missing is evidence + newcomer-cost + bridge-contract discipline — the three disciplines running through §D (D9 evidence, D9 newcomer-cost, D7 bridge-contract; full list D1–D10).

## D. Required v5 fixes (minimal, ordered; no moves, no schema changes)

1. **Language fix (all docs):** "runtime-orthogonal, dev-coupled" — never bare "orthogonal".
   UC1 keeps its side note (renaming `.opencode/` breaks the dev loop) as a Post item, not a footnote.
2. **Ledger-count rule:** no absolute row counts; format "`N` rows at `date -u +%Y-%m-%dT%H:%M:%SZ`
   via `wc -l .meta/.omt/ledger.jsonl`, re-count at signing". Apply to PROPOSAL §0/§7, UC6/UC8 at promotion.
3. **Net-file pin:** "20 modules + `__init__.py` = 21 files" everywhere §3/UC4 appear.
4. **Tool-mapping admission:** add one line to §3 — "`phase/skip/complete/tdd` provider file(s)
   unchecked in v5; T1 pins file→tool map or states enforcer-owned" — or pin it now with `rg`.
5. **Test-scope completion (T1):** audit covers `tests/scripts (103) + tests/features (100)` **plus**
   `tests_automated/, tests/test_sandbox/, toolbox/ tests, tools/*/tests, .sandbox/` with a one-line
   scope-or-exclude each; build roots (`pyproject/uv.lock/.venv`) declared as shared prerequisite.
6. **Tri-home decision (closes Q2):** scope `tools/petri-net-studio/` as product + `shared/petri-net/`
   as product-owned contract in T1; studio PROJECT.md carries conforming `bridge:` tag **only** for
   harness-driven analysis slices. Elevate studio's `check-independence + conformance` as the T2 template.
7. **Bridge-contract pin (T2 before any orthogonality claim):** answer Q4 with an explicit
   projection list + "read-only = no writes outside append" test; until then §0 calls the ledger
   "the bridge under contract definition", never "minimal/stable".
8. **Authority hygiene:** promote `.projects/README.md` (+ fix or remove the `OMT_PROJECTS_ROOT` line)
   together with any sandbox promotion, or delete the mirror note. Never carry two untracked authorities.
9. **Evidence requirement (all T):** each T cites an `omt_session` source (capture/profile/query) or
   benchmark golden; token/cost claims need real-token measurement (harness_reason precedent).
   Newcomer-cost check: "can a student still `uv run agentx` → `c` with zero harness knowledge?" per T.
10. **Q5 stays open, stays out of sandbox:** pre-promotion checklist (UC8) keeps
    `git diff -- opencode.jsonc` + `wc -l ledger` + `git status --short` re-verification verbatim.

## E. Re-verification log (2026-10-10 ~16:20 UTC — deltas vs v4 §9)

- `git status --short` → `M opencode.jsonc` + `?? .projects/README.md` + `?? .projects/agentx/` +
  `?? sandbox/orthogonality_001_wrapper_split/` (unchanged; sandbox still untracked/invisible).
- `wc -l .meta/.omt/ledger.jsonl` → **9** (v4's "5" rotted via its own refine + this session's
  `think_consult`; rows: think_consult, net_sync bootstrap rev 0, think_consult, phase+complete
  unscoped:001 (v3), think_consult, phase+complete unscoped:001 (v4), think_consult (current)).
- `grep -n omt_/reason_/startup_/webfetch opencode.jsonc` → 11 `omt_*` + `reason_check` (12 perm lines);
  `webfetch:deny` still removed in working tree; `reason_table/startup_table` plugin-provided, not gated.
- `ls scripts/omt/*.py` → 13; `ls scripts/omt/net/*.py` → 21 inc `__init__` (20 modules);
  `ls .meta/.omt/` → 7; `ls .opencode/plugins/*.ts` → 11; `ls .opencode/lib/enforcer/` → 12.
- `rg --files tests/scripts | wc -l` → 103; `rg --files tests/features | wc -l` → 100.
- `rg -c "# TA:" src/agentx` → 30 lines / 18 files (top `main_controller.py:5`, `react_view.py:5`);
  no `strip-TA` test (T4 still open); TS-side TA rule still unstated.
- `cat src/agentx/ui/test_omt_mvc_gate.py` → `from agentx.model.session import Session` +
  `print('ok')`, zero test functions (v4 correction stands; T1 disposition still pending).
- `rg -n "bridge:" .projects/meta --glob "*PROJECT.md"` → 1 prose hit (`meta_harness_11:50`
  "Harness↔agentx bridge:") — still zero *conforming* tags under the §1 format pin.
- `.projects/agentx/META.md` → `_(none)_` + populated 4-row pending-moves draft (v4 correction stands).
- `WORK.compiled.md` rev 60 NEXT=`agentx_concurrent_development` vs live probe rev 0 `next:none`
  (STALE by construction — record both revs in every receipt).
- Carried unchecked in v5 (verify or drop before promotion): DSL 277 records, `tests/features` 52 dirs,
  `idea-002` "Sentinel bridge:" prose hit — cited from v4/README, not re-run in this pass.
