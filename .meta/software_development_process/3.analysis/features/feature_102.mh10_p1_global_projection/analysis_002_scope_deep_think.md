# Analysis 002 — Deep scope think: what "Meta Harness" and "Petri global state" cover

> Feature: `feature_102.mh10_p1_global_projection` (`minor_feature`, project `meta_harness_10`) · Phase: Analysis · Date: 2026-09-18.
> Status: **adopted v0.3 (2026-09-18)** — R1–R6 user-approved; folded into PROJECT.md Scope + D6 (analysis_001 R3/R4/R5 deltas binding on Programming/Testing). Proposal history preserved below.
> Consults: `omt_think{op:list, query:"scope"}` (11 thoughts, 5 files — no existing global-state-authority thought) + `...{query:"global state petri net authority advisory"}` (0) · `petri_net_library/PROJECT.md` D11 + iter log · `feature_001.../FEATURE.md` (10-line stub) · net probe rev 57 · `omt_q{op:state}`.

---

## 1. What "the meta harness" is (the thing being scoped)

The harness = the methodology tooling that governs how work is done: `.meta/META_HARNESS.omt` (SSOT) · `.opencode/**` (enforcer, gates, `omt_*` tools) · `scripts/omt/**` · harness tests · the WORK.md protocol · the `.projects/` + `.workflows/` catalogs · AKB consult machinery. It is the **governor**, and MH projects improve the governor.

Scope trap (seen in mh6–mh9 logs): harness work that touches product code leaks scope. `src/agentx/` product behavior is OUT for MH10 — including `src/agentx/model/petri_net/` (product library, feature_031 DONE) and `src/agentx/model/internal_state` (does not exist yet; belongs to feature_001).

## 2. "Global state" has 4 readings — the request uses all of them at once

| # | Reading | Shape | MH10 status |
|---|---|---|---|
| 1 | Global **view** | one derived read joining the 4 domains | **P1 (now)** |
| 2 | Global **store** | one durable record all domains write through | nobody proposed; = parked S6a storage question (SQLite vs generations, WAL order C1) |
| 3 | Global **authority** | one gate every move checks ("must always use") | **P2 (parked, needs a–e)** |
| 4 | Global **model** | one net template covering all 4 domains (C6 transition map) | precondition of 3, also parked |

"Must always use … as a global state" = readings 3+4 as end-state. The staged hybrid earns 3 via 1+4. Until PROJECT.md says this table out loud, "global state" stays ambiguous and P1 success can't be judged. **(→ R1)**

## 3. The 4 domains are differently shaped — unification cost differs

- **Features/tasks are net-shaped already**: phase pipeline + TDD machine + ledger records; WORK.md pool + rev-57 marking. Cheap to project, plausible to gate later.
- **Projects/workflows are document-shaped**: PROJECT.md prose + ledger lifecycle rows; workflow catalog is agent-read markdown with zero machine state (only `.sandbox/` rounds as residue).
- Covering doc-shaped domains needs (a) projecting docs into tokens — cheap, lossy, loss must be labeled — or (b) migrating docs into a store — expensive, reopens storage/identity questions. P1 = (a) with loss labeled. Claiming (b)'s guarantees on (a)'s substrate is exactly the C6 overclaim mh9 closed. **(→ R1, R5)**

## 4. Boundaries: what MH10 is not (locks to add)

- **Product boundary**: feature_001 (adaptive product net from `USER_OBJECTIVES.md` CRC; 10-line stub, scope unset) and feature_002 (RAG) are OUT. Direction of dependence: harness must never import `src/agentx/*` (bootstrap circularity + failure-mode coupling). feature_001 stays a separate consumer of the product library; MH10 consumes `scripts/omt/net` facts only. **(→ R2)**
- **Sibling harness concerns** (reuse, don't reopen): budgets/diet, nav index, KB/AKB behavior, TDD toolchain, lane/lock/worktree machinery (079–085). Cited as substrate, never re-implemented (D3 overlap gate already covers; R2 extends it to product).
- **No new store in P1**: any durable global record is reading 2 = S6a territory. P1 derives; it does not persist. **(→ R6)**

## 5. Blind spots in the current P1 scope (found by this iteration)

1. **Join keys**: WORK.md tasks vs ledger features vs net bindings vs project slugs use different identities (C4 residual). Without specified join keys the "global" view is four juxtaposed lists. S4-lesson analog: a projection that reproduces four lists side-by-side earns no "global" the way frontier reproducing preflight text earned no runtime.
2. **As-of**: sources refresh on different rhythms (ledger append, WORK.md edit, live probe). There is no global as-of; each section needs its own `rev/HEAD/ts` (S3 parity-note pattern).
3. **Workflow projection honesty**: catalog position + last `.sandbox/` round pointer is all there is; show it as such.
4. **Second-engine trap**: re-affirmed — derive from probe + ledger + files; no new net engine (analysis_001 §5 already; lock it).
5. **Falsifiability**: "orients a real task from ≤2KB alone" needs a protocol — blind resume by a fresh session + acceptance checklist — else untestable at Testing. Borrow the S1 oracle-qualification pattern (seeded classes: routine, interrupted).
6. **Derived rows**: `project.py sync` mutates WORK.md + META.md (visible in this session's `git status`). Projection must mark sync-generated rows as derived, not source, or it double-counts.

**(→ R3, R4, R5)**

## 6. Proposed refinements (approval needed)

- **R1 — Lock the 4-readings table** (§2) into PROJECT.md Scope; "global state" in MH10 means reading 1 now, 2–4 only via P2 re-entry.
- **R2 — Harness↔product non-dependence rule**: MH10 never imports `src/agentx/*`; feature_001/002 explicitly out; D3 overlap gate extended to product.
- **R3 — Join keys + per-section as-of** in the P1 schema (fixes blind spots 1–2).
- **R4 — Falsifiable demo protocol**: blind fresh-session resume + acceptance checklist for the 2 demo tasks (fixes 5).
- **R5 — Derived-row marking**: sync-generated content labeled derived (fixes 6); workflow section shows catalog + last-round pointer only (fixes 3).
- **R6 — No-new-store non-goal** in P1 (fixes 4 by locking it; reading 2 stays S6a territory).

Cost if adopted: PROJECT.md Scope edit + analysis_001 schema deltas (2 small doc edits, non-gated, no live surfaces). Nothing in P1 Programming changes shape — keys/as-of/derived flags fold into the sidecar builder's existing rows.
