# analysis_001 — S4 read-only frontier experiment (the decision gate)

> Feature `feature_101.mh9_s4_frontier_experiment` · type `minor_feature` · phase `Analysis`
> HEAD: `96d319a` (short) · S0 base `f1be918` + S2 4-file diffs (F09/F05-caller/F02/F03) + S3 sidecar `.sandbox/work_contract/` · date 2026-09-14
> No `src/` / authority / store / gate / tool change in S4 (sidecar advisory only).

## 1. Overlap gate (D3 — no re-implementation)

PROJECT.md §2 row 4: "not done — highest decision value → S4 paired experiment; keep/merge/drop. Gates everything parked."

- 070–075/079–096 stand (mh8 CLOSED 31/31, ledger Done). Not re-implemented.
- 072 `typed_policy_semantics` + 073 `task_prep_op_slice` + 092 `resume_digest` + 055/062 preflight — live, reused as-is (S3 substrate). S4 consumes their outputs, changes none.
- S3 `feature_100` — Done; sidecar `.sandbox/work_contract/` (`contract.py` + 2 demos + `parity_note.md`) is the fact source for both arms. S4 adds no second contract engine.
- 093/094 bench + S1 `analysis_001_oracle_proxies_corpus.md` — oracle classes, proxy labels, frozen corpus reused; no re-run of S1-full inside S4 (S1-full stays deferred, its deltas cited not claimed).
- S2 `analysis_001_residual_order.md` + test_report + S3 `parity_note.md` — parity inputs reused; S4 records, does not re-fix.
- S4 adds ONLY: frontier advisory schema (short design note) + sidecar paired harness + paired results + keep/merge/drop verdict. No new tool/gate/nav record, no writer, no store, no authority. S5+ stays parked (§4 re-entry needs S4-keep + S2-green + payback).

## 2. Substrate inputs (what S4 composes)

| Input | Source | S4 use |
|---|---|---|
| task facts | S3 contract JSON (request/scope/obligations/next_action/stale_or_unknown/detail_refs, ≤2KB cap) | identical fact block fed to both arms |
| restrictions + next-action | 073 prep → 055/062 `preflightProjection` (block == preflight) | arm A content; arm B/C must not contradict it |
| policy line | 072 `evaluatePolicy` vocabulary (`activation_solo_skip`, etc.) | shared `via` values, no second engine |
| orientation trail | 092 digest (2048B cap pattern) | presentation-budget precedent |
| oracle classes (4) | S1 §1 (valid accept / omitted behavior / stale evidence / false-success) | detection checks only (seeded defects never count as economy) |
| proxy labels | S1 §2 (`tokens_est=io_bytes//4` PROXY, `io_bytes`/`verify_seconds` real, delivered-bytes PROXY) | every cost field labeled; no metered-token claim |
| corpus + order rules | S1 §3 + S0 freeze (6 real + 2 fixture, paired order, cold/warm split, attempt boundaries) | S4 reuses the 2 task classes below, not a new corpus |
| parity gap | S2 + `parity_note.md` (block agrees, report-shape UNKNOWN, C1/C6 open) | carried in every arm output's UNKNOWN block |
| preflight caveat | `preflight.ts` `DRY_CAVEATS[g.net]` (dry cannot verify live net; solo auto-skip) | arm outputs never claim net verdict |

KB consult 2026-09-14 for "petri frontier guidance preflight" → no new KB surface (advisory composition, documented here). Think-gate: `task_prep.ts`, `policy_decision.ts`, `preflight.ts`, `.sandbox/work_contract/contract.py` carry 0 thoughts — clear.

## 3. Frozen profile (enforcement untouched)

- Frontier is advisory: never grants, authorizes, mutates policy, writes ledger/thoughts/phase records, or dispatches edits. READ-ONLY first (§5.2).
- Candidate-action domain: closed verb set from S3 (`clear <gate>` / `edit <path>` / `run <check>` / `consult <tool>` / `ask-user <q>`). Out-of-domain suggestions are a harness defect, counted against the frontier arm.
- Revision + identity: `candidate_id = path@revision`; render rev pinned per pair; stale revision/generation cannot commit — S4 re-renders at dispatch revision and rechecks even though S4 never dispatches (parity_note §4).
- Omitted-count / continuation contract: every arm output honors the ≤2KB presentation budget with required-continuation (S3 cap rule: drop detail tail → completed tail → hard-cut with pointer, never mid-sentence; `next_action` + `stale_or_unknown` never dropped). Omitted items counted, pointer required.
- Pins frozen per pair: model/policy/compiler/net-bundle/oracle/corpus-rev + HEAD sha recorded in the pair header. No mid-pair upgrades.

## 4. Arms (same facts + same budget)

- **Arm A — consolidated preflight:** explicit task/dependency/resource facts (S3 contract rendered as text, ≤2KB). No Petri content.
- **Arm B — Petri frontier on the same facts + budget:** contract facts + frontier advisory (enabled/next-frontier actions with reasons + omitted-count), same 2KB budget. Frontier must be consistent with arm A facts (contradiction = defect against B).
- **Arm C — frontier + bounded analysis (cost included):** arm B + one bounded analysis pass (e.g. reachability / dead-obligation check over the projected obligations), with its query/compute cost counted in the pair cost fields (proxies labeled).

Task classes (2, paired order, frozen criteria):
1. routine fix (low-risk file, mostly clear → `edit` + evidence);
2. interrupted/resumed (stale revision + unresolved obligations → `clear` chain + UNKNOWNs preserved).
Seeded defects (S1 classes 2–4) used ONLY for detection checks; economic return needs naturally occurring avoided failures too (PROJECT.md §3 S4).

Metrics per pair (all arms, proxies labeled):
first-useful-action (steps to first action that survives acceptance) · avoided attempts (dead-end clears/edits not taken) · recovery accuracy (interrupted-task resume orients without full re-read) · acceptance (oracle class-1 pass) · cost (all-agent `io_bytes` + `tokens_est` PROXY + analysis/query cost for arm C).

## 5. Frontier schema (short design note preview; full note in Design)

Advisory-only JSON, sidecar-validated, never executed:

```
{
  "op": "frontier",
  "candidate_id": "<path@rev>",
  "facts_ref": "<contract digest>",
  "enabled": [{ "action": "<closed verb + target>", "reason": "<blocking gate / risk signal>" }],
  "frontier": [{ "action": "<closed verb + target>", "reason": "<why this unblocks>" }],
  "omitted_count": "<n>",
  "unknowns": ["<carried from contract stale_or_unknown, incl. dry/live report-parity + C1 + C6 + proxy labels>"],
  "note": "<continuation pointer when capped>"
}
```

Rules: `enabled` ⊆ closed verbs; `frontier` ordered by unblock-value; contradiction with contract `blocked`/`first_blocker` is a defect; `unknowns` always carries the parity/proxy/C1/C6 labels (renderer injects when caller omits, never dropped); cap/continuation identical to S3 (never mid-sentence; `frontier[0]` + `unknowns` never dropped).

## 6. Sidecar surface (non-interference)

- Writes: `.sandbox/frontier/` (schema + paired harness + pair results + verdict draft) + this analysis doc + short design note + test report. No `.meta/*.omt`, `.opencode/**`, `scripts/omt/net/**`, `tests/` edits.
- Harness: pure python stdlib, no ledger writes, no shell-outs, no network. Inputs = S3 demo contracts (seeded) + live-composed contracts for the 2 task classes (read-only composition). Outputs = arm A/B/C renders + pair table + verdict.
- Live check/build/suite green before AND after (S4 touches none, verified both sides). Runs in sidecar, never the live checkout (§5.4).

## 7. Exit (S4 met when)

1. Frontier schema + sidecar harness land in `.sandbox/frontier/` with 2KB budget + continuation enforced on all arms.
2. Paired results published for both task classes × 3 arms (A/B/C) with frozen pins per pair + all five metrics + proxy labels.
3. Written **keep / merge / drop verdict** (PROJECT.md §3 S4 + §8.5 self-limit):
   - keep → S5 re-entry proposal (needs S2-green + one-template transition map + payback math);
   - merge → fold remedies into preflight, keep Petri analysis-only;
   - drop → retire frontier, keep the smaller compiler/resume/evidence product.
   A frontier reproducing preflight text earns no runtime (§6.6): keep requires repeatable accepted-task benefit with setup+support payback stated.
4. `check` 265/0 + `build` OK + suite green; no economy claim beyond labeled proxies; no authority/execution claim (C6 explicitly not claimed).

## 8. Risks / unknowns kept UNKNOWN

- Frontier value unproven — that is the experiment, not the premise.
- S1-full deferred — no removal-delta claims inside S4; waste ranking cited, not extended.
- 072/073 `6.testing` reports absent on disk — S4 reuses live code, certifies nothing about them.
- Dry/live report-parity UNKNOWN stands (parity_note §2); S4 asserts block-agreement only.
