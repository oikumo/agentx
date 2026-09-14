# analysis_001 — S3 thin work contract, read-only (projection over 072/073/092)

> Feature `feature_100.mh9_s3_thin_work_contract` · type `minor_feature` · phase `Analysis`
> HEAD: `3490fd5` (short) · S0 base `f1be918` + S2 4-file diffs (F09/F05-caller/F02/F03) · date 2026-09-14
> No `src/` / authority / store change in S3 (sidecar projection only).

## 1. Overlap gate (D3 — no re-implementation)

PROJECT.md §2 row 3: "072 + 073 + 092 shipped as parts; no single WorkIR → S3 read-only projection; duplicate store forbidden."

- 072 `typed_policy_semantics` — ledger Done; live `policy_decision.ts` (ONE evaluator, durable-vs-temp-vs-consult separation). Reused as-is, not re-implemented.
- 073 `task_prep_op_slice` — ledger Done; live `task_prep.ts` (ONE prep call, block == preflight, risk model, never fabricates). Reused as-is.
- 092 `resume_digest` — SHIPPED with design + 7 goldens; live `omt_status{op:resume}` (≤2KB, fail-open drops, fast path, read-only). Reused as-is.
- 055/062 preflight (`preflight.ts`) — shared A4 core, SINGLE source for restrictions/next-action. Reused as-is.
- S3 adds ONLY the thin contract projection schema + sidecar renderer + 2-task demo + parity note. No new tool/gate/nav record, no writer, no store migration.

## 2. Substrate inputs (what S3 composes)

| Input | Source | S3 use |
|---|---|---|
| restrictions + next-action | 073 `buildTaskPrep` → 055/062 `preflightProjection` (block == preflight by construction) | task-candidate-scope obligations + next action + reason |
| g.net activation/exception note | 072 `evaluatePolicy` / `explainDecision` (solo-skip C1, break-glass only override) | policy line inside restrictions (no second engine) |
| risk + evidence | 073 `riskOf` + `evidenceFor` (characteristics, not labels) | required-evidence list per risk level |
| orientation trail | 092 digest lines (banner/project/next/TDD/trail/docs/artifacts, 2048B cap) | stale-or-unknown facts + detail refs pattern |
| honest cost labels | S1 `analysis_001_oracle_proxies_corpus.md` (proxies labeled, oracle 4 classes) | every usage field carries PROXY label; oracle class cited, never claimed |
| truthful boundary | S2 `analysis_001_residual_order.md` + test_report (F09→F05-caller→F02→F03, allow/deny matrix) | parity note inputs; invalid-classes rejected stays enforced, S3 only records |

KB consult 2026-09-14 for "work contract projection task prep policy" → no KB results (new surface, documented here). Think-gate: `task_prep.ts`, `policy_decision.ts`, `preflight.ts` carry 0 thoughts — clear.

## 3. Projection schema (read-only, no store)

One bounded task view. JSON shape (sidecar renderer enforces ≤2KB default + required-continuation):

```
{
  "op": "work_contract",
  "request": { "task": "<one line>", "acceptance_refs": ["<verify/test/doc ref>"] },
  "scope": { "path": "<candidate file>", "tool": "<edit|read|...>",
              "task_type": "bug_fix|...", "candidate_id": "<path@rev>", "revision": "<sha>" },
  "obligations": { "completed": ["<gate:cleared how>"],
                    "unresolved": [{ "gate_id": "<g.*>", "clearing_action": "<concise>" }] },
  "next_action": { "action": "<normalized verb + target>",
                    "reason": "<why this unblocks>",
                    "required_evidence": ["<check/test/receipt>"] },
  "stale_or_unknown": ["<fact>: UNKNOWN (<why>)" ],
  "detail_refs": ["<file:Lline (<B>B)>"],
  "note": "<continuation pointer when capped>"
}
```

Field rules:
- `request.acceptance_refs` — refs to verify/test expectations (oracle class 1); missing → `"acceptance_refs": "UNKNOWN (no verify ref found)"`, never invented.
- `scope.candidate_id` — `path@revision`; revision = HEAD sha at render time. Stale revision (render rev ≠ dispatch rev) → consumer must re-render (S4 rechecks at dispatch even though S4 never dispatches).
- `obligations` — completed = consults already paid (nav/kb/think receipts) + green checks; unresolved = preflight `before` fired+blocked rows (clearing_action truncated 160c, same copy as preflight). `blocked == (unresolved.length > 0) == preflight.would_block`; `first_blocker` identical (no second engine).
- `next_action` — normalized verbs only: `clear <gate>`, `edit <path>`, `run <check>`, `consult <tool>`, `ask-user <question>`. Reason cites the blocking gate or risk signal. Evidence from 073 `evidenceFor(risk)` + acceptance refs.
- `stale_or_unknown` — REQUIRED entries (never dropped to fit the cap):
  1. dry/live parity (F03/F10): "live evaluates all obligations (S2 F03); dry `op:plan` continues-all — prediction vs enforcement agree on block, differ on report shape → UNKNOWN report-parity" unless re-verified.
  2. cost proxies (S1): "no host per-call token usage — `tokens_est`/`io_bytes`/delivered-bytes are PROXY, not metered."
  3. C6: "lifecycle ops bypass transition relation (`state.py` direct counters) — no Petri execution guarantee claimed."
  4. C1: "clear-before-record crash window open — do not depend on replay surviving it."
  5. Missing/inconsistent inputs labeled per-field (`UNKNOWN (...)` / `INCONSISTENT (a vs b)`), never silently dropped.
- `detail_refs` — bounded pointers with byte sizes + line anchors (092 pattern), so follow-up reads are partial `Read(offset,limit)`, never full re-reads.
- Cap: default 2048B (092 `RESUME_DIGEST_CAP` precedent). Under-cap byte-identical, no marker. Over-cap: drop `detail_refs` tail → `obligations.completed` tail → hard-cut with `… contract capped at 2048B — detail: <first dropped ref>` (never mid-sentence cut; `next_action` + `stale_or_unknown` never dropped).

Q/A, candidate-identity, normalized-action, decision-result (PROJECT.md §3 S3 "schema as a projection"):
- Q = `request.task` + `obligations.unresolved` questions; A = `next_action` + evidence.
- candidate-identity = `scope.candidate_id` (+ generation/owner when present, else `UNKNOWN (solo, no claim)`).
- normalized-action = `next_action.action` (closed verb set above).
- decision-result = `{ blocked, first_blocker, via }` where `via` reuses 072 `PolicyVia` vocabulary (`activation_solo_skip` / `exception_break_glass` / `deny_concurrent_no_grant` / `defer_untyped`).

## 4. Migration log (future one-writer per action — designated, NOT migrated)

No store, no writer moves in S3 (duplicate store forbidden). Designated future mapping (S5+ re-entry only, needs S4-keep + S2-green + payback):

| Action verb | Future one-writer | Today (S3) |
|---|---|---|
| `clear <gate>` | the gate's owning surface (`omt_skip` for grants, consult tools for evidence) | projection only cites `clearing_action` |
| `edit <path>` | single editor session (no dual-write) | projection only names target |
| `run <check>` | the check runner (receipt carries digests) | projection only names evidence |
| `consult <tool>` | the consulted tool (relevance, never authority) | pointers only, `consulted:false` |
| `ask-user` | user reply | question text only |

## 5. Sidecar surface (non-interference)

- Writes: `.sandbox/work_contract/` (renderer + 2 demo contracts + parity note) + this analysis doc + test report. No `.meta/*.omt`, `.opencode/**`, `scripts/omt/net/**`, `tests/` edits.
- Renderer: pure python stdlib, no ledger writes, no shell-outs, no network. Inputs = caller-supplied prep-like dict + digest-like dict (seeded for demo; S4 wires live composition). Outputs = contract JSON + capped text render.
- Live check/build/suite must stay green before AND after (S3 touches none, verified both sides).

## 6. Exit (S3 met when)

1. Renderer + schema land in `.sandbox/work_contract/` with 2048B cap + continuation enforced.
2. Two demo contracts render from projection alone and orient without re-reading full docs:
   (a) routine fix (low-risk file, all clear → `edit` + evidence);
   (b) interrupted/resumed (stale revision + unresolved obligations → `clear` chain + UNKNOWNs preserved).
3. `parity_note.md` ships: dry/live agreement on block + UNKNOWN report-parity + proxy/C1/C6 labels.
4. `check` 265/0 + `build` OK + suite green (S3 adds no live-surface risk; bench fixtures unchanged).
5. No economy claim beyond labeled proxies; no authority claim; S5+ stays parked.

## 7. Risks / unknowns kept UNKNOWN

- 072/073 `6.testing` reports absent on disk (ledger Done, live code present) — S3 reuses live code, does not certify the missing reports; flagged here, not papered over.
- S1-full (real 6-task re-run + 8-gate matrix) deferred — S3 demos carry proxy labels, no removal-delta claims.
- Frontier value unproven — S3 proves resumability from projection, not guidance superiority (S4's paired experiment).
