# Design 001 — O2 apply_selection (M0 serial-atomic batch)

> Feature: `feature_111.multi_select_directive_protocol` (`minor_feature`) · Phase: Design · Date: 2026-09-19.
> Consumes: Analysis 001 + O1 IDs (`compose_menu_options`) + `fire`/`claim_task` `_transact` authority + D19/rev-stamp render.

---

## 1. Grammar (parse-only, pure)

```ebnf
selection  := "pick" ws "{" ws id (ws "," ws id)* ws "}" [ws "+" ws directive (ws "+" ws directive)*] ;
id         := pool_id | proj_id | drift_id | unscoped_id ;
pool_id    := "pool:" transition ;
proj_id    := "proj:" slug ;
drift_id   := "drift:" class ":" key ;
unscoped_id:= "unscoped:" digits ;
directive  := id ":" quoted_string ;   (* per-id opaque annotation *)
```

- `parse_selection(text) -> {ids:[...], directives:{id:str}} | SelectionError(unknown_id | bad_syntax | dup_id | directive_without_id)`.
- Validation source: the live O1 `Options:` list from the same rev R menu (caller supplies `valid_ids: set[str]`); unknown → refuse + re-render valid options (D19, no invented options).
- `question`-tool binding (convention, no code): agent presents O1 `Options:` via `question`, parses the user's `{id,…} + directives` reply with `parse_selection`. No new tool; grammar is the contract.

## 2. M0 batch bound (serial-atomic without rollback machinery)

- At most **one net-mutating op** per batch (`fire` **or** `claim` **or** `splice-add-proposal-apply`); any number of **directive annotations** (overlay-only, opaque) + any number of **D4 proposals** (drift/unscoped hygiene rendered as proposal text, never auto-applied).
- >1 mutating op in one pick → refuse `multi_mutate_deferred_o4` + re-render + O4 pointer (F7 `agent_attention=1` stays; true parallel is O4 with explicit reversal).
- Atomicity holds trivially: single `_transact` commit (existing `expected_revision` + `command_id` idempotency); annotations are overlay writes inside the same commit; proposals are pure text. No compensating-rollback path needed in M0.

## 3. Module shape (pure core + thin caller)

New `scripts/omt/net/apply_selection.py` (stdlib-only, no net/ledger I/O):

- `parse_selection(text) -> Selection` (§1).
- `plan_selection(sel, *, valid_ids, enabled, coverage_anonymous: bool) -> Plan` — pure ID→op mapping per §4 table; marks at most one `mutate:{kind, args}` + `annotations:{id:directive}` + `proposals:[...]`; multi-mutate → `PlanRefused(multi_mutate_deferred_o4)`.
- `describe_plan(plan) -> str` — one-line human summary for the approval gate + ledger `reasoning` field.
- Caller threading (harness-surface, receipt-disciplined, one edit per file per e2e receipt):
  1. `state.py`: `apply_selection(base, *, selection_text, valid_ids, reasoning, session, expected_revision, command_id)` — parse + plan (pure) → execute single mutate via existing `fire`/`claim_task`/`splice` under `_transact` (reuse, no new lock) → write overlay annotations in same commit → `append_ledger` reuses existing kinds only (§5) → return `(NetState, report)`.
  2. `cli.py`: `apply-selection` subcommand (`--expected-revision` required, session whitelist per 046) printing report JSON + re-render hint (`sync net_to_md` next).
  3. `sync_md.py`: untouched (O1 render already carries `Options:` + rev-stamp the batch validates against).

## 4. ID→op plan table (existing ops only)

| ID | Mutate? | Plan |
|---|---|---|
| `pool:<t>` (enabled) | YES (counts as the one) | `fire(t, expected_revision=R)` |
| `proj:<slug>` (active project, anonymous coverage) | NO (M0) | annotation `selected:<slug>` + proposal text "open project home" (claim handles are O3) |
| `drift:<class>:<key>` | NO (M0) | D4 proposal text only (`splice`/`sync` suggested, never applied) |
| `unscoped:<id>` | NO (M0) | annotation `directive` + proposal text "scope feature first" |
| second mutating ID | — | refuse `multi_mutate_deferred_o4` |

Rationale: live rev 60 has `enabled:[]` + anonymous coverage 7/7, so real M0 batches are `0 mutate + N annotations/proposals` or `1 pool fire + annotations` — always single-commit atomic.

## 5. Ledger / annotations (no new kinds, no overlay change)

- Reuse existing kinds only (replay-safe per `history.py` no-mutation skip branches): the single mutate appends its native record (`net_fire` / `net_claim` / `net_splice`) with extra fields `selection:{ids}`, `directives:{...}`, `batch_id`; a following `net_sync` re-render closes the batch. No `net_apply` kind (avoids feature_044/`net_mine`-class replay breakage).
- **Deviation from Analysis (P10):** directives ride in the ledger record's fields, NOT the overlay — `save()` re-derives the overlay from the net (`derive_overlay`, `state.py:535`), so custom `overlay["selections"]` keys would be silently dropped. Overlay stays byte-identical in shape; Tier-3 holds (no place/transition/overlay-derivation change).
- Annotate-only batches (no mutate) write nothing: report carries annotations + D4 proposals for the agent's next step (durable via session log); the following `sync net_to_md` appends its own `net_sync` audit.

## 6. Stale-rev + error codes (stable strings)

- `bad_syntax | unknown_id:{id} | dup_id:{id} | directive_without_id:{id} | stale_revision (expected R, live R') | multi_mutate_deferred_o4 | task_not_pending | worker_capacity_exhausted | scope_conflict` — all refuse pre-write except the single-mutate path, which reuses `_transact` errors verbatim; every refuse prints fresh-menu re-render hint.

## 7. Goldens (new file, canary-gated)

`tests/scripts/omt/test_net_apply_o2.py` (~12): grammar accept ×3 / refuse ×4 (unknown/dup/bad-syntax/directive-without-id); plan single-mutate + annotations; multi-mutate refuse; stale-rev refuse; annotation round-trip in report; D19 + rev-stamp preserved in describe; no-new-places invariant (Tier-3: assert place set unchanged after apply).

## 8. Receipt + budget plan

- 3 single-edit rounds: (1) `apply_selection.py` pure parse+plan → e2e receipt; (2) `state.py` threading → e2e; (3) `cli.py` subcommand → e2e; goldens after tests/ canary (guardTestsPath: phase-first then re-issue skip).
- Token/runtime: one `probe` (validate at R) + one commit + one `sync net_to_md`; no new places/transitions; `src/agentx/` untouched (D1).
