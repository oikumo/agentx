# Analysis 003: Think Anywhere V2 — Tier C (Verify Lifecycle C1 + Per-File Consult C2)

> **Phase:** Analysis — `omt_agent_guide.md §2` | **Feature:** feature_022.meta_harness_think_anywhere_v2
> **Source:** `2.requirements/.../feature_022.meta_harness_think_anywhere_v2/FEATURE.md` (F4, F8-partial, intent gap; tiers C1, C2)
> **Prior:** analysis_001 (Tier A — shipped), analysis_002 (Tier B1+D1 — shipped 2026-07-18)

## Scope decision (2026-07-18)

**Tier C only** (C1 verify/stale lifecycle + C2 per-file consult granularity), per the WORK.md
task `T-022C`. B2 (suggest), E1 (index strategy beyond what C1 consumes), E2 (theory doc) are
**not** in scope. Pairing rationale: C1 and C2 jointly restore the paper's *feedback loop*
(C1 = RLVR-style outcome signal on thoughts; C2 = consult integrity that makes the gate's
"safety-relevant" claim true). Surfaces touched: C1 = `omt_think.ts` (new tool + digest) +
`omt_enforcer.ts` (gate-message weighting); C2 = `omt_think.ts` (consult record) +
`omt_enforcer.ts` (gate check). Overlap is small and both tiers share the index/ledger
read-path work, so one TDD batch is safe.

## Verified evidence (every claim re-checked against source, 2026-07-18)

| Item | Flaw | Verified evidence |
|------|------|-------------------|
| C1 | no verify tool | `omt_think.ts:476-479` — default export's tool map is exactly `{omt_think, omt_think_list, omt_think_remove}`; no `omt_think_verify` exists. |
| C1 | index is write-only (F8) | `appendIndex` (`omt_think.ts:86-91`) and `reconcileIndex` (`:94-104`) are the only index touchpoints; **nothing reads `thoughts.jsonl`** (list greps inline, `:396`; digest greps inline, `:455`). B1's `anchor:{kind,value}|null` field (`:368`) is stored but never consumed — exactly the drift-repair input C1 needs. |
| C1 | digest has no stale signal | `thinkDigest` (`:454-471`) reports count/files only; a thought whose anchor drifted (or was detached by an edit) is indistinguishable from a sound one — the RLVR-style outcome signal is absent (FEATURE.md intent-gap table row 2). |
| C1 | gate has no risk/stale weighting | `thinkGateMsg` (`omt_enforcer.ts:254-260`) renders thoughts in file order, 10-cap; no category ordering, no stale marker. FEATURE.md C1: "gate weights unverified `risk:` thoughts higher." |
| C2 | consult is session-global | `recordConsult` (`omt_think.ts:107-114`) writes `{ts, kind:"think_consult", session}` — **no file/path field**; `omt_think_list` records it unconditionally (`:398`). One consult of any file clears the gate for every file (F4). |
| C2 | cross-session window | `hasConsultedThoughts` (`omt_enforcer.ts:203-225`): exact-session match on ANY consult (`:216-219`), else ANY consult within `UNLOCK_WINDOW_MS` (8h, `:48`) regardless of session (`:220-224`) — a *previous session's* consult clears the gate (F4 second half). |
| C2 | gate check has no per-file input | call site `omt_enforcer.ts:949-955`: `hasConsultedThoughts(session)` — the target `rel` is in scope but not passed; `thinkGateDecision` (`:192-198`) is a pure 2-boolean function (keep — regression surface for feature_021 `decide`-mode tests). |
| C2 | ledger path is cwd-rooted | `hasConsultedThoughts` reads `join(process.cwd(), ".meta/.omt/ledger.jsonl")` (`:204`) — **not** the plugin's `directory` → hermetic runner tests need a root-injection parameter (production call site passes `directory`; identical in real opencode). |
| — | D1 explicitly deferred this tier | `omt_enforcer.ts:968` comment: "NO think_consult record is written … (C2 owns per-file consult — out of scope)" — now in scope; D1 injection stays consult-free (awareness ≠ consult, design_002 §2). |
| — | regression surface (feature_021) | `test_omt_think.py:228-232` counts `think_consult` records (shape-agnostic — adding a `files` field is safe); `:264-273` drives `thinkGateDecision` via runner `decide` mode (keep signature); `:275-291` source-asserts `export function hasConsultedThoughts` + `"think_consult"` (keep both). |

**Runner/instantiation facts (test design):**
- `_think_runner.mjs` maps tools by name from the default factory (`toolMap.omt_think*`); adding
  `omt_think_verify` there (1 line) reaches the real tool — args pass through.
- `_think_gate_runner.mjs` `after-hook` mode proves `OmtEnforcer({client:null,$:stub,directory:tmpdir})`
  is directly drivable; a symmetric `before-hook` mode drives `tool.execute.before`, catching
  `OmtBlock` to report block/allow. The enforcer's factory `relOf` resolves against `directory`
  (`omt_enforcer.ts:418-421`), so a tmpdir `directory` + file inside tmpdir = isolated gate run
  (protected/e2e/tests/src checks pass through for a plain non-src file).
- Digest greps `REPO_ROOT` only (`grepThoughts(pattern, ".")`, cwd-rooted) — a behavioral
  stale-count digest test needs a uniquely-named thought file **inside** the repo, cleaned up
  after (excluded dirs: `.git node_modules .omt .venv __pycache__`, `*.env*`).

## Problem analysis per item

### C1 — `omt_think_verify{path, line}` + stale surfacing

**Semantics decision (analysis-level):** verification is *structural*, not semantic. Whether a
thought's claim is still true requires agent judgement (that happens at consult/read time);
what the harness can re-check mechanically is **placement integrity** — does the thought still
exist at the recorded position, and does its recorded anchor still resolve to it? That is the
RLVR-analogue signal this tier adds: drifted/detached thoughts get flagged `stale` instead of
silently persisting as trustworthy.

- Validate like `omt_think_remove`: path required, file exists, line in range, line matches
  `THOUGHT_PATTERN` (anchored — prose mentions refused), parse `{cat, text}` via the existing
  `parseThoughtLine`.
- Look up the latest **add-record** for `(path, line)` in `thoughts.jsonl` (fallback: latest
  add-record for `(path, thought-text)` — covers line drift since insert).
  - Record has `anchor` → re-resolve with the B1 `resolveAnchor` logic: unique match **and**
    resolved insertion point == thought's current line → `verified` (basis `anchor`); else
    `stale` (basis `anchor`, reason: anchor missing/ambiguous/moved).
  - No record / no anchor → existence check only → `verified` (basis `exists`, weaker —
    message says so).
- Append a verify record to the index: `{ts, kind:"verify", path, line, category, thought,
  status, basis}` — first **read-consumer** of the index follows: digest + gate read the latest
  verify status per `(path, line)` (partial F8 progress; full index strategy is E1).
- Digest: count current grep hits whose latest verify record is `stale`; when > 0, the digest
  header gains `N stale — run omt_think_verify{path,line}`.
- Gate weighting: `thinkGateMsg` renders `risk:`-category thoughts first and appends
  ` ⚠️ STALE` to thoughts whose latest verify record is stale. Enforcer reads the index via the
  same cwd-rooted path (root-injectable, shared helper).

### C2 — Per-file consult granularity

- `omt_think_list` records `{ts, kind:"think_consult", session, files: [<rel paths of grep
  hits>]}` (capped for ledger hygiene). The consulted set = the files the listing actually
  matched (what the agent was shown), not the path argument.
- `hasConsultedThoughts(session, rel, {risk})`:
  - exact-session record whose `files` includes `rel` → consulted.
  - exact-session **legacy** record (no `files` field, pre-C2) → consulted (grandfathered;
    such records age out of the window).
  - cross-session record within `UNLOCK_WINDOW_MS` covering `rel` → consulted **only if the
    file carries no `risk:`-category thought** (FEATURE.md C2: "drop cross-session window for
    `risk:` category" — a risk thought demands *this* session looked).
- Gate call site computes `risk` from the already-fetched `thinkHits` (category position only:
  `/TA:\s*risk:/i` — A4 lowercases categories at insert; `i` covers pre-A4 legacy tags) and
  passes `rel` + `risk`; `thinkGateDecision` stays pure/unchanged.
- `omt_think_list` on a thought-free target records `files: []` (covers nothing — preserves
  the v1 "always records" behavior without granting clearance).

## Risks / open questions → Design

| # | Risk/question | Design must decide |
|---|---------------|--------------------|
| R1 | Index verify-match fallback (by thought-text) could bind to the wrong record if two thoughts share text | Design pins match order: `(path,line)` add-record first, then `(path,text)`; ties → latest wins. Documented limitation. |
| R2 | `risk:` detection by content regex could miss exotic formatting | Categories are normalized at insert (A4); regex anchors at category position. Accept + test both positive and negative cases. |
| R3 | Editing `omt_think.ts` (carries TA: at EOF) during Programming | `omt_think_list` consult first; harness-e2e receipt refresh between plugin edits; ONE batched write per plugin (Tier A/B1+D1 gotcha). |
| R4 | Real-ledger pollution from runner-based tool tests | Accepted precedent (feature_021/Tier A/B1+D1: tools write to the real gitignored ledger/index); hermeticism only where it matters (gate decision via root-injected `hasConsultedThoughts` + tmpdir before-hook). |
| R5 | Digest stale test needs a thought file inside REPO_ROOT | Unique-name file in repo root + `finally` cleanup (`omt_think_remove` + unlink); never in excluded dirs. |
| R6 | `files` array unbounded in consult record (huge repo listing) | Cap (design picks: 200) with `files_truncated: true` marker; gate-side treat truncated records as covering only listed files (safe direction: re-consult with narrower path). |
| R7 | Grandfathering legacy no-`files` records weakens per-file semantics until they age out | Accepted: v1 consults expire with sessions/window; grandfathering avoids bricking in-flight sessions on deploy. |

## Test strategy (feeds design §3)

New module `test_omt_think_v2_tier_c.py` in the existing
`tests/features/feature_022.meta_harness_think_anywhere_v2/` dir. `_think_runner.mjs` gains
`omt_think_verify` (1 line). `_think_gate_runner.mjs` gains: `consulted '<json:{session,rel,
risk,root}>'` mode (root-injected real `hasConsultedThoughts`) and `before-hook '<directory>'
'<json:[calls]>'` mode (real `OmtEnforcer` before-hook, `OmtBlock` → `{blocked,message}`).
Regression gates: Tier A suite (15), Tier B1+D1 suite (19), feature_021 suite (30).
