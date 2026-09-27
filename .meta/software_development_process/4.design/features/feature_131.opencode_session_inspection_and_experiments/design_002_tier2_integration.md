# Design 002 — Tier-2 integration (omt_session)

Feature: `feature_131.opencode_session_inspection_and_experiments` · Phase: Design · Date: 2026-09-27
Inputs: `design_001` (core + slice plan S5) · `PROJECT.md` §Proposed architecture/Tier-2 surface · `analysis_001` (adapter contract) · live budgets `harnessc check` 2026-09-27 (tool_args 2553/2592 = 39B headroom; tool_schemas 1871/2048 = 177B headroom).

## 1. Goal

Register one Tier-2 tool **`omt_session`** in `.opencode/plugins/omt_session.ts` as a thin proxy over the
stdlib-only `scripts/session_inspect/` core (S1–S4, frozen). No second runtime, no `src/agentx/` dependency,
no competing token accounting. Full harness integration per PROJECT.md D2: registered `omt_*` tool +
`.omt` declaration + compiler-generated config/docs + budget checks + fresh e2e receipt + tested
enforcement behavior.

## 2. Operation enum (closed, 9 ops)

```
sessions | capture | query | inspect | trace | profile | compare | experiment | export
```

`experiment` has closed subops `plan|dry_run|run|collect|validate|replay` (passed as `sub` arg; `run`
stays explicitly effectful and gated per PROJECT.md fallback clause). No new op without a design
amendment (IDEA-002 §5.0 discipline, same as `omt_net`).

Per-op core mapping:

| Op | Core entry | Effect class |
|---|---|---|
| `sessions` | adapter.snapshot + normalize (bounded selectors) | read |
| `capture` | adapter.snapshot → artifact only on explicit `dest` | read + bounded write |
| `query` | query.py typed docs + cursor | read |
| `inspect` | inspect.py exact drill-down + pages | read |
| `trace` | trace.py timeline | read |
| `profile` | profile.py hotspots/failures | read |
| `compare` | compare.py sessions/trials | read |
| `experiment` | manifest.py / collect.py / evaluate.py (`run` → `request_run` unavailable until invocation path exists) | read except `run` = effectful |
| `export` | exporter.py atomic tmp+rename to explicit `dest` | read + bounded write |

Default machine summary ≤2 KiB UTF-8 with counts/coverage/metric def/digest-bound `detail_ref`; full
evidence via typed selection + cursor (`cursor_stale` on stale digest). Human reports are derived views.

## 3. Plugin shape (thin proxy, omt_net.ts pattern)

`createSessionTool()` built inside factory so `description` resolves from compiled IR AFTER
`initOmtShared` (F2/F17 — same as `omt_net.ts` R8). `export default async ({directory, worktree})`
returns `{ tool: { omt_session } }`.

Per-op argv whitelist `OP_ARGS` mirrors the Python subparser flags exactly (pinned cross-source test,
same as `test_omt_net_plugin_args.py`):

```
sessions:   [db, directory, session_ids, time_from, time_to, limit]
capture:    [db, directory, session_ids, time_from, time_to, dest]
query:      [db, query_json, limit, cursor]
inspect:    [db, session_id, message_id, part_id, page, per_page]
trace:      [db, session_id]
profile:    [db, session_id, top_n]
compare:    [db, ids_json, basis]
experiment: [db, sub, manifest, run, dest]
export:     [db, selection_json, dest]
common:     [expected_revision] on every op (stale-rev guard, feature_050 pattern)
```

Validation before DB access or dispatch: unknown op → `unknown_op` envelope; unwhitelisted flag →
refuse; no SQL/shell fragments in query docs (typed query documents only); bounded limit/rows/pages;
`dest` must be inside repo root and outside protected paths (`.env*`, `uv.lock`, `README.md`,
`LICENSE` reuse `PROTECTED` pattern from `reason_check.ts`); `run` subop returns named unavailable
`no_safe_launch` until the Tier-2 invocation path + budget enforcement exist (never launches OpenCode
from tests).

Python entry: one dispatcher `scripts/session_inspect/service.py :: main(op, argv)` (NEW in S5) that
reuses S1–S4 modules; CLI `cli.py` stays the M1–M3 dev surface (untouched).

## 4. .omt declaration + budget discharge plan

New row in `.meta/META_HARNESS.omt` (same block as `@tool omt_net`):

```
@tool omt_session perm=allow args="op,db?,directory?,session_ids?,time_from?,time_to?,limit?,query_json?,cursor?,session_id?,message_id?,part_id?,page?,per_page?,top_n?,ids_json?,basis?,sub?,manifest?,run?,dest?,selection_json?,expected_revision?" tags="CMD_SESSION" : Session inspector + labeled experiments — SSOT (9 ops, run gated). op=sessions|capture|query|inspect|trace|profile|compare|experiment|export.
```

Measured cost (2026-09-27): `tool_args` 2553/2592 (39B free, ≤64B diet band); `tool_schemas`
1871/2048 (177B free). The new row adds ~1 description (~180B, must stay ≤177B free) + ~23 arg
`describe()` strings (largest risk — `omt_net` precedent: 16 args ≈ 674B longest single describe).

Discharge options (pick ONE in implementation, recorded in test report):

- **A — diet (preferred):** keep arg describes ≤8B average by reusing short fragments
  (`"op enum"`, `"DB path"`, `"dest path"`, …); free ≥26B via longest-`omt_net`-describe trim
  (674B → ≤648B, same technique as `budget-diet` hint). No cap change.
- **B — deliberate cap growth:** `tool_args max 2592 → 2720 (+128)` in the SAME `.omt` edit as the
  new row (compiler check requires cap + row atomically, else build error). Justified only if A
  cannot keep describes intelligible.

`harnessc build` must stay green (275 records +1, 0 errors); `AGENTS.md`/nav-index/IR budgets
unaffected (no new inject, no new nav records beyond the 1 tool row).

## 5. Enforcement boundary

- Read ops pass through enforcement (`perm=allow`, same as other `omt_*` reads).
- `capture`/`export` writes: explicit `dest` only, atomic tmp+rename, validated before DB access;
  destination rules = existing protected-path + receipt guards (no new gate — net-zero `gates max=12`).
- `experiment run`: effectful — must NOT receive read passthrough; reuses existing authorization,
  resource claims, isolation; second scheduler forbidden; bypass = tested refusal.
- Reports never mint authority (no net/ledger/src writes from output rendering).

## 6. Receipt + round-robin discipline (GOTCHA_RECEIPT_*)

Harness surface = `.meta/META_HARNESS.omt` + `.opencode/plugins/omt_session.ts` +
`.opencode/lib/omt_shared.ts` (if touched) + `scripts/omt/*` (if touched) +
`tests/scripts/omt/test_*.py` (receipt-EXEMPT). Per-file SECOND-edit guard: ONE edit per file per
e2e receipt (`uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q` refreshes
`.meta/.omt/omt_harness_e2e_last_run.json`). Order: stage → edit code freely → edit `.omt` LAST →
re-stage → single e2e (feature_089 T4-2: `.omt` edit after stage invalidates batch). Update e2e
source pins FIRST shape-agnostic, tighten at end. `service.py` + `scripts/session_inspect/*` are
NON-harness (no receipt guard) — keep the Tier-2 delta inside them where possible.

## 7. TDD behavior list (S5 — fed to omt_tdd)

1. `session.ops_closed` — unknown op → `unknown_op`; unknown `experiment.sub` → refuse; no new op.
2. `session.argv_whitelist` — per-op flags mirror Python subparsers; unwhitelisted flag refused;
   SQL/shell fragments in query docs refused; cross-source pin test (TS OP_ARGS ↔ py subparsers).
3. `session.budgets_green` — `harnessc check` 0 errors; tool_args + tool_schemas within cap after
   diet/cap-change; description/argv parity (TS fallback seed BYTE-matches `.omt` payload —
   GOTCHA feature_050 1B `?` drift).
4. `session.read_passthrough` — sessions/query/inspect/trace/profile/compare round-trip on synthetic
   fixture DB via service dispatcher; ≤2 KiB default summary + `detail_ref`; stale cursor →
   `cursor_stale`.
5. `session.write_bounded` — capture/export write ONLY to explicit `dest` (tmp+rename atomic);
   protected-path dest refused; missing `dest` → refuse (never cwd-dump).
6. `session.run_gated` — `experiment run` → `no_safe_launch` unavailable (no launch, no tokens);
   `plan|dry_run|collect|validate|replay` work read-only; replay never increases N.

S6 (NOT S5): 12-trial pilot, AC1–AC12 matrix, live-DB A2 `MH13_LIVE_DB=1`, overhead disclosure.

## 8. Exit evidence

`tests/scripts/session_inspect/test_slice5_session_service.py` (6 behaviors) green +
`tests/scripts/omt/test_omt_session_plugin_args.py` (whitelist/parity pin) green +
`harnessc check` 0 errors + `harnessc build` OK + fresh e2e receipt + full `uv run pytest -q`
no regressions. `feature_129/130` scripts untouched; fixtures synthetic only.
