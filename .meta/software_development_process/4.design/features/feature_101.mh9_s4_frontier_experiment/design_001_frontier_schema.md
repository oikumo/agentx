# Design Note — S4 Frontier Schema (feature_101, short note only)

> PROJECT.md §3 S4: "short design note for the frontier schema only". Locks the advisory shape BEFORE the sidecar harness, per 092 precedent (mechanism before implementation).

## 1. Problem

Preflight (055/062) already gives consolidated restrictions + next-action from one engine. The roadmap bets joint Petri guidance beats it. S4 must test that bet with identical facts + identical presentation budget, without touching enforcement. Without a locked advisory schema, the experiment can drift into a second authority (second engine, second verdict) or into prose that reproduces preflight text and earns no runtime (§6.6).

## 2. Non-goals / boundary

- No new tool, gate, nav record, store, writer, or policy change. No `.meta/*.omt`, `.opencode/**`, `scripts/omt/net/**`, `tests/` edits.
- Frontier never grants/authorizes/dispatches. Stale revision/generation never commits (recheck at dispatch even though S4 never dispatches).
- No second obligation engine: `blocked`/`first_blocker` EQUAL the S3 contract decision (single engine, asserted). Contradiction = defect against the frontier arm.
- No economy claim beyond S1 labeled proxies; no execution claim (C6 open); no replay claim (C1 open).

## 3. Mechanism

Sidecar `.sandbox/frontier/frontier.py` (pure stdlib, no ledger/shell/network):

- Input: S3 contract dict (built by `contract.py:build_contract`) + pair pins (HEAD rev, model/policy/compiler pins, budget).
- `build_frontier(contract, analysis=None)` → advisory dict:
  `op/frontier` + `candidate_id` (= contract `scope.candidate_id`) + `facts_ref` (contract digest) + `enabled[]` + `frontier[]` (closed verbs, ordered by unblock-value) + `omitted_count` + `unknowns[]` (carried from contract `stale_or_unknown`, never dropped) + `note`.
- Arm renders (same 2048B budget, same continuation rule as S3):
  A = contract text (`render_text`); B = A facts + frontier lines; C = B + one bounded analysis line (dead-obligation / reachability note) with its cost counted.
- `render_pair` enforces: under-cap byte-identical; over-cap drops detail tail → completed tail → hard-cut on line boundary with `… frontier capped at 2048B — detail: <ref>`; `frontier[0]` + `unknowns` never dropped; omitted items counted.
- `check_invariants`: closed verbs; `blocked`/`first_blocker` equal contract; required UNKNOWNs present (parity, proxy, C6, C1); `candidate_id` carries `@rev`; stale rev appends re-render UNKNOWN.

## 4. Budgets (zero-sum)

S4 adds no live-surface bytes: no `.omt`/tool/schema/agent record changes. Sidecar only (`.sandbox/frontier/` + this note + test report). Live `check`/`build`/suite must stay green before AND after.

## 5. Acceptance (pair table + verdict)

`frontier.py main()` self-check (no harness goldens — sidecar, receipt-exempt pattern per S3):
1. two pairs render (routine-fix + interrupted/resumed) × 3 arms, all ≤2048B, invariants hold;
2. B/C consistent with A facts (no contradiction; contradiction injector detected);
3. cap/continuation enforced (pathological refs → capped with marker, `frontier[0]`+`unknowns` survive);
4. stale-revision demo appends re-render UNKNOWN and refuses commit-readiness;
5. cost fields carry PROXY labels; verdict criteria applied to the pair table (keep needs repeatable accepted-task benefit + payback; else merge/drop per §7 of analysis).

## 6. Edit surface (sidecar only)

| file | edit |
|---|---|
| `.sandbox/frontier/frontier.py` | schema + renders + self-check |
| `.sandbox/frontier/pair_*.json/.txt` | pair outputs (generated, checked in for audit) |
| `.sandbox/frontier/verdict.md` | keep/merge/drop with re-entry math |
| `6.testing/.../feature_101.../test_report.md` | report + verdict pointer |
