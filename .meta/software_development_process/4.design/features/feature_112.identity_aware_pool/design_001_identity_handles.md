# Design 001 — O3 identity-aware pool (derived handles + atomic claim)

> Feature: `feature_112.identity_aware_pool` (`minor_feature`) · Phase: Design · Date: 2026-09-19.
> Consumes: Analysis 001 + O1 IDs (`compose_menu_options`) + O2 `apply_selection.py` (M0 single-mutate bound, annotate-only `proj:/drift:/unscoped:`) + `claim_task`/`release` `_transact` authority + D19/rev-stamp render.

---

## 1. Handle grammar (derived, pure)

```ebnf
menu_id    := pool_id | proj_id | drift_id | unscoped_id ;   (* O1 stable IDs, D19 *)
task_id    := "proj-" slug | "drift-" class "-" key | "unscoped-" digits | pool_transition ;
handle     := { menu_id, task_id, place, owner, generation } ;  (* derived view, read-only *)
```

- `menu_id_to_task_id(menu_id) -> task_id` (pure, stdlib-only): `proj:rag_v2 → proj-rag_v2`, `drift:aging-draft:feature_kb_akb → drift-aging-draft-feature_kb_akb`, `unscoped:001 → unscoped-001`, `pool:<t> → <t>`. Lower-snakes, stable across revs; unknown O1 ID → `unknown_id` refuse (same code as O2, D19 no invented options).
- `handles_for_menu(menu_ids, bindings) -> Handle[]` (pure): left-join O1 `Options:` against sidecar `task_bindings[]` (`id/place/owner/generation`); missing binding = `pending` unclaimed (`owner:none, generation:0`); no net I/O.
- `question`-tool binding (convention, no code): agent presents O1 `Options:` + handle `place/owner/gen` via `question`, parses reply with O2 `parse_selection`, resolves via this map before `apply_selection`.

## 2. M0 claim bound (serial-atomic, gen-fenced)

- At most **one net-mutating `fire`** per batch (O2 `multi_mutate_deferred_o4` kept) + any number of **binding claims** (`claim_task` moves `pending→active`, not net mutates — pool token moves alongside via existing `_fire_pool_move`, no new places) + any number of annotations/proposals.
- >1 `fire` in one pick → refuse `multi_mutate_deferred_o4` + re-render + O4 pointer (F7 `agent_attention=1` stays; true parallel is O4 with explicit reversal).
- Atomicity via existing `_transact` (load-through-commit lock, `expected_revision` + `command_id` idempotency): validate all handles at R → claim each sequentially inside one transaction → any `task_not_pending | worker_capacity_exhausted | scope_conflict | stale_revision` aborts pre-write except the single-fire path which reuses verbatim errors; zero partial holds.
- Generations fence stale owners (D9): first claim 0→1, `recover_task` bumps on handoff, old-gen submits refuse `stale_generation`. `worker_slots=2` cap + scope-overlap guard reused verbatim.

## 3. Module shape (pure core + thin caller)

New `scripts/omt/net/claim_handles.py` (stdlib-only, no net/ledger I/O):

- `menu_id_to_task_id(menu_id) -> str` (§1).
- `handles_for_menu(menu_ids: list[str], bindings: list[dict]) -> list[Handle]` — pure left-join + sort deterministic (D19 order preserved).
- `describe_handles(handles) -> str` — one-line `claimed N/M, free K` for menu `Resources:` tail + ledger `reasoning` field.

Caller threading (harness-surface, receipt-disciplined, one edit per file per e2e receipt):

1. `state.py`: `probe` gains additive `menu.claims: Handle[]` + `coverage.bindings[]` enriched with `menu_id` (additive keys only, exact-shape tests updated in same round); `apply_selection` gains claim step — after O2 `plan_selection`, resolve each non-`pool:` ID via `menu_id_to_task_id` → `claim_task` under same `_transact` (reuse, no new lock) → `append_ledger` reuses `net_claim` with extra `selection/directives/batch_id` (same as O2 §5, no new kind).
2. `cli.py`: `probe` JSON prints `menu.claims`; `claim` subcommand accepts `--expected-revision` + session whitelist (046) + handle display; `apply-selection` report gains `claims:[{task_id,owner,generation}]`.
3. `sync_md.py`: `Resources:` tail appends `claims N/M, free K` (additive text, TA `sync_md.py:138` honored — no hand rows between Pool and ## Projects).

## 4. ID→claim plan table (existing bindings only)

| ID | Claim? | Plan |
|---|---|---|
| `pool:<t>` (enabled) | via `fire` (counts as the one mutate) | `fire(t, expected_revision=R)`; binding move alongside via `_fire_pool_move` |
| `proj:<slug>` | YES (binding) | `claim_task(proj-<slug>, owner/session, expected_revision=R)`; re-pick refuses `task_not_pending`; proposal "open project home" kept as text |
| `drift:<class>:<key>` | YES (binding) | `claim_task(drift-<class>-<key>, …)` reserves hygiene slot; actual fix stays D4 `splice/sync` proposal (never auto-applied) |
| `unscoped:<id>` | YES (binding) | `claim_task(unscoped-<id>, …)` reserves scoping slot; `fire` still refused until scoped |
| second `pool:` fire | — | refuse `multi_mutate_deferred_o4` |
| claimed handle re-pick | — | refuse `task_not_pending` + re-render with `claimed by <owner>#<gen>` |

Rationale: live rev 60 has `enabled:[]` + anonymous 7/7, so real M0 batches are `0 fire + N claims + annotations` — always single-`_transact` atomic, still serial.

## 5. Ledger / overlay (no new kinds, P10-clean)

- Reuse existing kinds only (replay-safe): each claim appends native `net_claim` (`task_id/owner/generation/workspace` + `selection/directives/batch_id`); single `fire` appends `net_fire` same as O2; closing `net_sync` re-render ends batch. No `net_handle` kind.
- **P10:** overlay file stays derived (`derive_overlay`, `state.py:535`) — handles are a `probe`-time derived view over sidecar `task_bindings[]`, never persisted overlay keys. Sidecar `task_bindings[]` is the SSOT map (counts in net, map in sidecar+ledger — D20/D16 split honored). Tier-3 holds (no place/transition/overlay-derivation change).

## 6. Stale-rev + error codes (stable strings)

- `unknown_id:{id} | task_not_pending:{id} | worker_capacity_exhausted | scope_conflict:{id} | stale_revision (expected R, live R') | stale_generation | multi_mutate_deferred_o4` — all refuse pre-write except single-fire path (reuses `_transact` verbatim); every refuse prints fresh-menu re-render hint with `claimed by` annotations.

## 7. Goldens (new file, canary-gated)

`tests/scripts/omt/test_net_claim_o3.py` (~12): map stable ×2 / unknown refuse; handles left-join (missing=pending); claim reserves + second-session `task_not_pending`; capacity-full refuse; scope-conflict refuse; stale-rev refuse + re-render; coverage de-anonymized (`bindings 1/M, anonymous M-1`); D19 + rev-stamp; no-new-places invariant (Tier-3).

## 8. Receipt + budget plan

- 3 single-edit rounds: (1) `claim_handles.py` pure map+view → e2e receipt; (2) `state.py` probe-handles + apply-claim threading → e2e; (3) `cli.py` display → e2e; goldens after tests/ canary.
- Token/runtime: one `probe` (handles at R) + one batch commit + one `sync net_to_md`; no new places/transitions; `src/agentx/` untouched (D1).
