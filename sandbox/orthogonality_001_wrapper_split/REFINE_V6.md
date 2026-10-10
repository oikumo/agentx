# REFINE_V6 — workspace-deep critical rewrite + SOTA Oracle (addendum, does not rewrite v4/v5)

> Status: **draft refine** (2026-10-10, no approval, no promotion, no moves).
> Method: re-ran every command cited in v4 §9 / v5 §E (results §F below);
> read root `README.md` end-to-end (1293 lines); listed workspace root (30 entries);
> inspected `src/agentx/`, `scripts/`, `.meta/.omt/`, `.opencode/`, `tools/`,
> `shared/`, `tests/`, `.workflows/`, `.projects/`. v4 `PROPOSAL.md` /
> `USE_CASES.md` stay frozen baselines; v5 `CRITIQUE_V5.md` stays frozen critique.
> This file refines without silent rewrite + adds the one missing harness mechanic.
> Sandbox changes nothing outside `sandbox/` (UC0 holds).

## A. Workspace — where things actually live (deep pass, with what v4/v5 under-scoped)

**Root (30 entries — the split talks about ~10, the other ~20 decide if T3 passes):**
`AGENTS.md LICENSE README.md WORK.compiled.md WORK.md WORK_ARCHIVE.md opencode.jsonc
pyproject.toml uv.lock .python-version .venv/ .git/ .idea/ .meta/ .opencode/
.projects/ .sandbox/ .workflows/ .agents/ .agents_prompts/ sandbox/ scripts/
shared/ src/ tests/ tests_automated/ toolbox/ tools/`

- **Product (AgentX runtime + UI — newcomer path):**
  `src/agentx/` (`__init__, main, model/, ui/, agent/, utils/`; `model/` =
  `ai, chat, rag, rag_v2, petri_net (6 files), session, react, coding, program/`;
  `agent/` nests its own MVC) + `tools/petri-net-studio/` (Vite+React+TS, standalone —
  `npm run check-independence` asserts zero cross-boundary imports — the ONLY leg
  with a proof today) + `shared/petri-net/` (FORMAT.md LOCKED v1 + examples +
  `conformance/analysis-v1/` 9 vectors — the canonical contract, a **fourth leg**
  v4 omits, v5 catches) + product docs/tests.
  Newcomer path `uv sync && uv run agentx` → console REPL (`c/r/f/a/t/d/m/h/q`) —
  zero harness knowledge required. **Any T that breaks this path fails AgentX vision,
  no matter how clean the homes look.**
- **Harness (META HARNESS wrapper — no top-level `harness/` dir, four dirs + three scripts):**
  `scripts/omt/` (13 CLIs) + `scripts/session_inspect/` + `scripts/reason/` +
  `scripts/toolbox/`, `.meta/` (DSL `.meta/META_HARNESS.omt` 277 records cited, not
  re-counted in v6 + software_development_process corpus + `.meta/.omt/` 7 files:
  `META_NET.petri.json, harness.ir.json, ledger.jsonl, nav.index.jsonl, net.lock,
  net_state.sidecar.json, supervisor.overlay.json`), `.opencode/` (11 plugin files:
  `enforcer + 6 omt_* feature plugins (kb_nav, nav, net, q, session, status, think —
  count carefully: enforcer is gate not tool) + reason_check/table, startup_table`;
  12 enforcer lib files; perms gate 11 `omt_*` + `reason_check`).
  Net = **21 files inc `__init__.py` = 20 modules** (v4 "20 `.py`" right excl init —
  say so explicitly from now on; v5 already pins this, v6 keeps the pin).
- **Mixed / unscoped (where T3 rename-away proofs silently depend on things neither lane claims):**
  `tests/` (product `controllers, views, model, unit` + harness `tests/scripts/` 103
  files / 71 in `omt/` + mixed `tests/features/` 100 files in 52 dirs — v6 re-verified
  §F) **plus** `tests_automated/`, `tests/test_sandbox/`, `toolbox/` tests,
  `tools/*/tests`, `.sandbox/`, `.workflows/` (catalog **above** the harness —
  `# Rules` line 1 declares follow-vs-override — NOT harness-owned, NOT product-owned),
  `.projects/` (meta + agentx + untracked `README.md`), build roots
  (`pyproject.toml / uv.lock / .venv / .python-version` — neither lane claims them;
  rename-away proofs silently depend on them staying put — declare as shared
  prerequisite in T1 or T3 is unreproducible on a clean checkout).

## B. Claim-by-claim verdicts (be critical — v6 goes one step harder than v5)

| # | Claim | V6 verdict |
|---|---|---|
| 0 | Orthogonal = either side builds/tests/ships absent the other, 2 bridges | **Overclaim, keep the downgrade.** Runtime imports: holds (zero both ways today, modulo fixture/path-string exemptions §F). **Dev-time: false** — renaming `.opencode/` kills the `omt_*` dev loop; renaming `.meta/` kills ledger/projections/`WORK.md`; lanes + build roots unscoped (§A). V5 "runtime-orthogonal, dev-coupled" is the mandatory language fix (D1). Any UC/T that says bare "orthogonal" without the qualifier is rejected in review. |
| 1 | Homes + `_meta` suffix, grandfather, bridge-tag, no third home | **Rule right, model wrong.** Suffix + grandfather (no renames) is lowest-churn workable. `bridge:` format pin (standalone token in Decisions log) is a real fix. But **two-home model contradicts the tree**: `petri_net_studio` = `tools/` + `src/agentx/model/petri_net/` + `.projects/meta/` + `shared/petri-net/` = four legs. V5 recommendation (scope `tools/` as product + `shared/` as product-owned contract) is promoted to **decision D-tri** in v6 (§D.6). Until then T1 cannot close. |
| 2 | Testing lanes `tests/agentx` vs `tests/harness_meta` | **Direction right, scope incomplete, acceptance unfalsifiable today.** Grandfather + mapping + canary are honest. Gaps carried: target dirs don't exist (T-gated correctly); audit covers only `tests/scripts + tests/features` — `tests_automated/, tests/test_sandbox/, toolbox/ tests, tools/*/tests, .sandbox/` unscoped; build roots undeclared. `test_omt_mvc_gate.py` (`from agentx.model.session import Session` + `print('ok')`, zero test fns — v4 correction stands) **self-falsifies UC1's Post until T1 deletes it or moves it with a real assertion** — keep as T1 row #1. |
| 3 | Mechanics as verdicts (5 parts, ledger-only, ordered predicates, fail-open net, T5 receipts) | **Holds with two downgrades + one admission.** Gate order verified (`gate_driver.ts:308-315,451-452`). "Pure over snapshot" stands. Downgrades kept: per-mechanic receipts = T5 design (global `g.receipt` still enforced); denominators always stated. **Admission carried**: which plugin file provides `phase/skip/complete/tdd` is unchecked (11 files include `enforcer` gate, not tool) — T1 pins file→tool map or states enforcer-owned (D4). |
| 4 | TA inversion (`strip-TA === AST-identical` T4) | **Wish correctly labelled, framing wrong.** Bypass is discipline-only until T4; TS-side rule unstated; index schema unverified. Deeper: bridge (b) is an **inversion, not orthogonality** — honest framing is "one declared inversion", not "two minimal bridges". V6 Oracle (§E) closes T4 with a real AST test instead of carrying the wish another round. |
| 5 | Ledger as minimal bridge | **Wider than claimed, contract unpinned.** Append-only holds; minimal does not (first `think_consult` embeds 60+ paths). Schema change is a non-goal while schema stability *is* the bridge contract — contradiction until Q4 answered. **Counts rot every refine** (v3 "2" → v4 "5" → v5 "9" → **v6 "9" still, §F — stable only because no phase/complete ran between**). Rule from now on: **never pin a count without timestamp + `wc -l` command; receipts re-count at signing** (D2). |
| 6 | Acceptance T-gated, UC0 trivially true | **Best habit in the proposal, keep verbatim.** Marking non-runnable steps T-gated instead of readable-as-runnable is harness honesty in miniature. UC0 honesty note (isolation proof, not value proof; invisible to `project.py status/workc/nav`) must stay. Startup STALE (`WORK.compiled.md` rev 60 NEXT=`agentx_concurrent_development` vs live rev 0 `next:none`) blocks stable A–J IDs — record both revs in every receipt. |
| 7 | Authority (`.projects/README.md` untracked + `OMT_PROJECTS_ROOT` unexecutable) | **Correctly demoted, still double.** `rg OMT_PROJECTS_ROOT project.py` → no hits; `link` = `link <feature> <project> --origin manual` (feature-first). "Inlines and wins on conflict" creates a **second** authority. Fix (D8): promote convention file together with any sandbox promotion (fixing or removing the `OMT_PROJECTS_ROOT` line) or drop the mirror note. Never carry two untracked authorities into T1. |
| 8 | Q5 `opencode.jsonc` webfetch-deny removal | **Real drift, still open, correctly out-of-scope.** Re-verified v6 §F: `git diff` shows `- "webfetch": "deny",` while `AGENTS.md` + `.meta/META_HARNESS.omt:74,145` still declare deny. Restore via harness-surface receipt flow, never from sandbox. Every promotion pre-check re-runs `git diff -- opencode.jsonc` (D10). |
| 9 | Counts (tests "2300+", tools "14 plugins", bench "2 hits") | **Three stale denominators the root README also carries.** Suite = **2103/2105 collected** (2 deselected, §F — not "2300+", not "2370", not "2085+283" without citing which side). Tools = **14 tools in 11 plugin files** (not "14 plugins"). Bench = **5 substring hits** (`:11,:12` path-strings + `:32,:44` fixture-strings + `:35` path-string — not 2). T2 goldens must pin an **import-statement regex** with fixture+path exemptions, never a substring. |

## C. Vision alignment (root `README.md`, 1293 lines, read end-to-end for v6)

**Meta Harness vision** = proof a coding agent can be *mechanically* constrained to
Analysis→Design→Programming→Testing with visible auditable artifacts; single-source DSL
(`.meta/META_HARNESS.omt` → `harnessc build` → AGENTS/opencode.jsonc/IR/nav-index,
drift-tested); token discipline (every prompt/session byte budgeted:
tool schemas 2014/2048 B, `AGENTS.md` ≤3584 B, `WORK.md` ≤10240 B, `omt_status` ~350 B);
gates not willpower (IR-ordered `nav0/protect10/receipt20/tests30/net35/phase40/think50/kb55 + mvc60/tdd_after70`);
self-evolution **evidence-driven** via `omt_session` Tier-2 (usage/cost hotspots, traces,
failure witnesses, labeled experiments `plan|dry_run|run|collect|validate|replay` with `run`
gated `executed:false`, provenance-bound export; pilot unexecuted D7).
The split **helps** iff: (a) mechanical enforcement untouched in v1 (non-goals hold);
(b) every T carries evidence (`omt_session capture/query/profile`, benchmark goldens like
093's 17, real-token measurement like harness_reason kernel 1,321,729 vs harness 381,919 —
currently missing, D9 adds it); (c) zero unb budgeted surface (suffix/tags/lanes are docs
until gated — say so). It **hurts** iff bridge tags / lane dirs / dual homes become ceremony
without gates (MH6 ceremony-meter lesson — the Oracle in §E is CI-only for exactly this reason).

**AgentX vision** = educational console REPL (chat/rag/fast/advanced/react/coding/models,
`c/r/f/a/t/d/m/h/q`) + standalone Petri Net Studio (exact engine parity, conformance
vectors byte-identical, `check-independence` — the only legs with proofs) +
LangChain/LangGraph; MVC++ strict (`mvc_check.py` delta-blocking); ~2.3k tests (reconcile:
README "2,300+ / 2085+283 / ~2,370" vs measured **2103/2105 collected** — cite both with
commands until one source wins).
The split **helps** iff: (a) newcomer path (`uv run agentx`, `c`) untouched, runnable with
zero harness knowledge — per-T newcomer-cost check (D9); (b) Studio elevated as the
**exemplar** of claimed independence (it already ships the proofs the split only promises);
(c) product devs pay zero harness ceremony (bridge tags, owner/location bookkeeping) with
an attributable-failure win (UC5's promise — only real once lanes + Oracle land).
It **hurts** iff product devs pay ceremony for a split that is still discipline-only.

**Net verdict:** split intent aligned with both visions; v4/v5 honesty (T-gated acceptance,
counterexample admission, drift surfacing) *is* the harness vision in miniature. Missing:
evidence + newcomer-cost + bridge-contract discipline + one executable proof. §E adds the proof.

## D. Required v6 fixes (carry D1–D10 from v5, sharpened; no moves, no schema changes)

1. **Language:** "runtime-orthogonal, dev-coupled" — never bare "orthogonal". UC1 keeps
   rename-`.opencode/`-breaks-dev-loop as a Post item, not a footnote.
2. **Ledger-count rule:** no absolute counts; format "`N` rows at `<date -u>` via
   `wc -l .meta/.omt/ledger.jsonl`, re-count at signing". Apply at promotion (UC6/UC8).
3. **Net-file pin:** "20 modules + `__init__.py` = 21 files" everywhere §3/UC4 appear.
4. **Tool-mapping admission:** one line in §3 — "`phase/skip/complete/tdd` provider
   file(s) unchecked in v6; T1 pins file→tool map or states enforcer-owned" — or pin now with `rg`.
5. **Test-scope completion (T1):** audit covers `tests/scripts (103) + tests/features (100)`
   **plus** `tests_automated/, tests/test_sandbox/, toolbox/ tests, tools/*/tests,
   .sandbox/` with a one-line scope-or-exclude each; build roots
   (`pyproject/uv.lock/.venv`) declared as shared prerequisite.
6. **Tri-home DECISION (closes Q2, was recommendation):** scope `tools/petri-net-studio/`
   as product + `shared/petri-net/` as product-owned contract in T1; studio PROJECT.md
   carries conforming `bridge:` tag **only** for harness-driven analysis slices.
   Elevate studio's `check-independence + conformance` as the T2 template (the Oracle
   in §E is that template generalized).
7. **Bridge-contract pin (T2 before any orthogonality claim):** answer Q4 with an explicit
   projection list + "read-only = no writes outside append" test; until then §0 calls the
   ledger "the bridge under contract definition", never "minimal/stable".
8. **Authority hygiene:** promote `.projects/README.md` (+ fix or remove the
   `OMT_PROJECTS_ROOT` line) together with any sandbox promotion, or delete the mirror
   note. Never carry two untracked authorities.
9. **Evidence + newcomer-cost (all T):** each T cites an `omt_session` source
   (capture/profile/query) or benchmark golden; token/cost claims need real-token
   measurement (harness_reason precedent). Newcomer-cost check per T: "can a student
   still `uv run agentx` → `c` with zero harness knowledge?"
10. **Q5 stays open, stays out of sandbox:** UC8 keeps `git diff -- opencode.jsonc` +
    `wc -l ledger` + `git status --short` re-verification verbatim.

## E. SOTA addition — `split_proof_meta`: Orthogonality Oracle with proof-carrying lane certificates

**Problem it solves.** v4/v5 prove nothing executable: lanes don't exist, boundary has no
test, TA has no golden, ledger has no contract, rename-away is a paragraph. Reviewers must
re-run a dozen commands to trust any claim. Studio already solved this class with
`check-independence` + byte-identical `conformance` vectors — but nobody generalized the pattern.

**Idea (creative, state-of-the-art).** One new harness mechanic — `split_proof_meta` —
that turns every orthogonality claim into a **deterministic, content-addressed,
byte-identical certificate** produced in an **ephemeral overlay** (worktree + tmpfs copy,
never a rename in the dev tree), **provenance-bound** to ledger + `omt_session` evidence,
**budget-capped** (cert ≤2 KiB, `preflight` text untouched), **zero-ceremony for devs**
(CI-only; local run is advisory fail-open — MH6 ceremony-meter lesson). It dogfoods the
proposal's own rule: *one mechanic = exactly five parts* (CLI + gate predicate + ledger
kinds + `tests/harness_meta/<m>_meta/` + doc SECTION). No new `omt_*` tool (advisory CLI
only, `reason_check` precedent — zero registry rows).

- **E1. CLI `scripts/omt/split_proof.py` (the oracle).** Verbs:
  `prove --lane product|harness|both --overlay tmpfs` (copies tree minus the four
  harness dirs for product-lane / minus `src/agentx/` freeze-check for harness-lane,
  runs the lane suite, emits cert), `verify <cert.json>` (re-runs, asserts byte-identical
  minus timestamps), `attest-bridge` (checks `bridge:` conforming-tag format + owner/location
  index), `newcomer-probe` (boots `uv run agentx` → sends `c` → asserts REPL answers with
  zero harness env — the AgentX-vision guard). Output: canonical JSON LOCKED v1 (field order
  fixed, like `shared/petri-net/FORMAT.md`): `{oracle, lane, file_rev, live_rev,
  ledger_sha, firewall_verdict, ta_ast_hash, newcomer, tokens_ms, cert_sha}`.
- **E2. Gate predicate `g.split_proof` (pure over preflight snapshot, ordered after
  `g.net(35)`, before `g.phase(40)`).** Reads the cert + snapshot (net verdict, file list,
  ledger sha); never runs the suite itself (no I/O in predicate — the §3 "pure over snapshot"
  correction, enforced). Fail-open locally (advisory), fail-closed in CI (`--strict`).
  Second-edit receipt flow reuses T5 per-mechanic receipts slice-by-slice once T5 lands;
  until then global `g.receipt` still guards.
- **E3. Ledger kinds `split_proof.{cert,attest}` (append-only, narrow waist).**
  Each `prove` appends one `cert` row (cert_sha + lane + ledger_sha chain — hash-linked,
  Merkle-style, so projection drift is detectable). Q4 answered: projections pinned as
  `WORK.compiled.md, nav.index.jsonl, harness.ir.json, net_state.sidecar.json,
  WORK.md ## Projects` + "read-only = no writes outside append" test in T2. Schema change
  stays a non-goal — kinds extend, schema doesn't.
- **E4. Tests `tests/harness_meta/split_proof_meta/` (the T2/T3/T4 closure).**
  `test_firewall_meta.py` — **AST import firewall, not substring**: parses Python `ast`
  + TS import statements; bench fixture-strings (`tasks.py:32,44`) + path-strings
  (`:11,:12,:35`) live in a versioned exemption manifest (so the 5-hit false-positive class
  dies). `test_rename_away_meta.py` — overlay lane proofs (product-without-harness green,
  harness-without-product contract-pinned). `test_ta_strip_meta.py` — closes T4:
  `strip-TA === ast.dump-identical` (Python; TS rule: comment-strip === `tsc --noEmit`
  clean + snapshot-identical). `test_newcomer_meta.py` — newcomer probe (console boot,
  zero harness knowledge). All emit byte-identical certs (Studio `conformance` precedent).
- **E5. Doc SECTION `SECTION:split_proof` (nav-indexed, budgeted).** States denominators
  every time (11 `omt_*` vs 14-in-11 vs 13 CLIs), the 20+1 net pin, the ledger-count rule,
  the four-dir rename list, the exemption manifest path. Derives at projection time where
  possible (harnessc precedent — no hand-mirrored constants).

**Why state-of-the-art.** Proof-carrying lane certificates (like Sigstore/Reproducible-builds
attestations, but ≤2 KiB and harness-native); hermetic overlay proofs (Bazel/Nix hermeticity,
but worktree-cheap, no daemon); AST firewall with versioned exemptions (Buck2 visibility,
but docs-first); hash-chained ledger narrow waist (Merkle projection manifest); evidence-bound
evolution (`omt_session profile/query` + benchmark goldens + real-token measurement per cert —
harness_reason precedent); ceremony-meter safe (CI-strict / local-advisory split). Nothing in
v4/v5 proposes anything executable — this is the first mechanic that makes the split falsifiable.

**Cost.** One CLI file + one predicate + two ledger kinds + one test dir + one SECTION.
Zero `omt_*` renames, zero `src/` moves, zero `tests/` moves in v1 (Oracle runs against current
mixed layout with an exemption manifest; lanes migrate under it in T1–T3). Token cost: one
`--help` line + cert schema (~300 B); `preflight` text +0 (predicate reuses existing line).

**Acceptance (T-gated, runnable once E4 lands — unlike all of §7 today):**
`uv run scripts/omt/split_proof.py prove --lane both` → two certs green +
`verify` byte-identical + `attest-bridge` zero conforming-tag backlog except studio slices +
`newcomer-probe` REPL answers. Until then this section is design, labelled as such.

## F. Re-verification log (v6, 2026-10-10 — deltas vs v5 §E)

- `ls -1` root → 30 entries (v5 "30" stands; note `.venv/` + `.idea/` + `toolbox/` + `tests_automated/` are the unscoped legs).
- `wc -l .meta/.omt/ledger.jsonl` → **9** (stable since v5 — no phase/complete ran between; rows: think_consult, net_sync bootstrap rev 0, think_consult, phase+complete unscoped:001 (v3), think_consult, phase+complete unscoped:001 (v4), think_consult (v5), think_consult (v6 current) — re-count at signing, never pin).
- `ls .opencode/plugins/*.ts` → 11 (`enforcer, kb_nav, nav, net, q, session, status, think, reason_check, reason_table, startup_table`); perms gate 11 `omt_*` + `reason_check` (12 lines); `webfetch:deny` still removed in working tree (`git diff -- opencode.jsonc` shows `- "webfetch": "deny",`).
- `ls scripts/omt/*.py` → 13; `ls scripts/omt/net/*.py` → 21 inc `__init__` (20 modules); `ls .meta/.omt/` → 7; `ls .opencode/lib/enforcer/` → 12.
- `uv run pytest --collect-only -q` → **2103/2105 collected (2 deselected)**; `rg --files tests/scripts` → 103 (71 in `omt/`); `rg --files tests/features` → 100.
- `rg -c "# TA:" src/agentx` → 30 lines / 18 files; no `strip-TA` test (T4 still open — §E closes it); TS-side TA rule still unstated.
- `cat src/agentx/ui/test_omt_mvc_gate.py` → `from agentx.model.session import Session` + `print('ok')`, zero test fns (disposition still pending — T1 row #1).
- `rg -n "bridge:" .projects/meta --glob "*PROJECT.md"` → 1 prose hit (`meta_harness_11:50` "Harness↔agentx bridge:") — still zero *conforming* tags.
- `.projects/agentx/META.md` → placeholder + populated 4-row pending-moves draft (stands).
- `WORK.compiled.md` rev 60 NEXT=`agentx_concurrent_development` vs live probe rev 0 `next:none` (STALE by construction — record both revs in every receipt).
- Carried unchecked in v6 (verify or drop before promotion): DSL 277 records, `tests/features` 52 dirs, `idea-002` prose hit, `phase/skip/complete/tdd` provider mapping — cited from v4/v5, not re-run in this pass.

## G. What changed in the sandbox (this refine)

- Added this file only (`REFINE_V6.md`). `PROPOSAL.md` / `USE_CASES.md` v4 frozen.
  `CRITIQUE_V5.md` frozen. Next step on your explicit go only: T1 audit (+ Oracle E4
  scaffold under `tests/harness_meta/split_proof_meta/` with canary) → T2 firewall goldens
  → promotion via UC8 (manual scaffold + `link <feature> <project> --origin manual`,
  never `sync` with root override before T6; pre-checks `git diff -- opencode.jsonc` +
  `wc -l ledger` + `git status --short` re-run at signing).
