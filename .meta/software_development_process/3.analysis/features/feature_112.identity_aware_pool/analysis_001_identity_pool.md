# Analysis 001 — O3 identity-aware pool (scope for approval)

> Feature: `feature_112.identity_aware_pool` (`minor_feature`, project `meta_harness_11`) · Phase: Analysis · Date: 2026-09-19.
> Resumes: PROJECT.md §Plan O3 + gaps doc G10/G11 + O1 Done (feature_110, rev 60 whole-project menu) + O2 Done (feature_111, `apply_selection` single-mutate bound, `proj:/drift:/unscoped:` annotate-only).

---

## 1. Problem (reproducer)

Cold start on rev 60 has selectable IDs but no identity to reserve:

- Live `probe rev 60`: `enabled:[]`, `observation:drained_complete`, `coverage work_done bindings 0/7 anonymous 7/7`, `menu {next:none, other:[], blocked:[], resources 4/4 free}`, `parallel:[]`, `workers 0/2`. WORK.md overlays O1 `Options:` — 19 `proj:<slug>` + 9 `drift:<class>:<key>` + 2 `unscoped:<id>`, `NEXT: proj:agentx_concurrent_development (recommended)`.
- `claim_task(task_id, owner, session, expected_revision)` exists (sidecar `task_bindings[]`: `id/place/owner/generation/workspace`, gen-fenced, `worker_slots=2` cap, scope-conflict guard) but the menu carries no claim handles and `probe.resources[].holders` is empty live. There is no `task_id→holder` view joining O1 IDs to bindings (G10).
- User picks `pick {proj:rag_v2}` (O2 parses, plans `annotate-only + proposal "open rag_v2 project home (claim handles are O3)"`). Nothing reserves `rag_v2`: two sessions can pick the same `proj:rag_v2` concurrently, both annotate, neither holds a generation fence (G11).
- Adapting "do feature_001 + rag_v2 fix" cannot address net tokens by ID — counts live in net, map lives in overlay+ledger (D20/D16 split), audit in ledger. `fire(work_start)` moves a generic token; the net cannot represent *which* O1 ID was selected (G10).

Reproduce: present WORK.md `Options:` (30 O1 IDs) → `pick {proj:rag_v2, unscoped:001}` → O2 `plan_selection` returns `mutate=annotate-only` → no `claim` handle to hold, `probe.coverage` stays `anonymous 7/7`, second session picks same IDs with no refusal.

## 2. What O3 must prove (oracle)

- **Derived ID map (P10-clean, no new places/transitions):** expose a read-only `task_id→holder` view derived from sidecar `task_bindings[]` + O1 menu IDs (Tier-3 excludes net — overlay file stays derived from net via `derive_overlay`; custom overlay keys would drop on `save()`, same lesson as O2 design §5 ledger-carried directives). Map lives in `probe` output (e.g. `menu.claims` or `coverage.bindings[]` enriched with `menu_id`), not in new net structure. `src/agentx/` untouched (D1).
- **`probe.menu` emits claim handles:** each O1 menu ID maps to a claimable handle:
  - `pool:<transition>` → existing task binding id for that transition if pending, else `fire --expected-revision R` path unchanged (executor refuses authoritatively if disabled).
  - `proj:<slug>` / `drift:<class>:<key>` / `unscoped:<id>` → logical `task_id` (e.g. `proj:rag_v2 → task proj-rag_v2`, stable across revs) with `place` (`pending/active/done`), `owner`, `generation`. Unknown slug → refuse with re-render of valid `Options:` (D19 kept, no invented options).
- **Claim reserves on select (atomic, rev-checked, gen-fenced):** `apply_selection` threading gains a claim step reusing `claim_task`/`release`/`fire --expected-revision` only (closed-enum ops, 046 whitelist): validate all handles at rev R → claim each selected handle at R with `owner/session` + generation bump (first claim 0→1) → single ledger `net_claim` per handle + WORK.md re-render; any handle not-pending / capacity-full (`worker_slots=2`) / scope-overlap / stale-R → refuse + re-render, zero partial holds (all-or-nothing, same atomicity as O2). Still serial (F7 `agent_attention=1` NOT reversed — M0 slice; true parallel dispatch is O4).
- **Coverage de-anonymized:** after claim, `probe.coverage` shows `bindings N/M` with `owner+generation` instead of `anonymous`; `probe.resources[].holders` lists holders (e.g. `pool` + claim owners); `menu.next/other` reflects reserved vs free (reserved IDs show `claimed by <owner>#<gen>`, not re-offered as free).
- **Ordering + stamp preserved:** D19 `NEXT / Other / Blocked / Resources` + `Options:` + `Lanes:` + `<!-- net_rev:R -->` round-trip through claim; stale-R claim refuses with fresh menu (G4 fire-time guard extended to claim scope, same as O2 batch scope).
- Out of scope: worktree dispatch/join/WIP runtime (O4, needs F7 reversal), menu-time freshness/live view (O5), agentx bridge + directive→fragment synthesis (O6, needs D1 revisit), bulk multi-mutate (still `multi_mutate_deferred_o4` — one net-mutating `fire` per batch max, claims are binding moves, not net mutates).

## 3. Resource budget

- Code: pure helper (e.g. `scripts/omt/net/claim_handles.py`: O1-ID→`task_id` mapping + handle view composer, stdlib-only, no net I/O) + thin threading in `state.py` (`probe` handle emission, `apply_selection` claim step via existing `claim_task`, no new `net_*` kind — replay-safe) + CLI `claim` handle display (additive fields only). No new places/transitions; no `src/agentx/` changes.
- Tests: new goldens `tests/scripts/omt/test_net_claim_o3.py` (handle map stable, unknown-ID refuse, claim reserves + second-session `task_not_pending` refuse, capacity-full refuse, scope-conflict refuse, stale-rev refuse + re-render, coverage de-anonymized, D19 + rev-stamp) — needs tests/ canary approval; e2e receipt per harness-surface round discipline (one edit per file per receipt).
- Runtime: one `probe` (handles at R) + N `claim_task` inside one atomic batch + one `sync net_to_md` re-render; no extra live loop (freshness stays fire/claim-time; menu-time is O5).

## 4. Handle sketch (O1 → O3)

| O1 menu ID | Example (rev 60 live) | O3 handle sketch (existing bindings only) |
|---|---|---|
| `pool:<transition>` | (none enabled live) | `task_id` = transition binding if pending else `fire --expected-revision R` single transition |
| `proj:<slug>` | `proj:rag_v2` (active), `proj:agentx_concurrent_development` (draft) | `task proj-<slug>` (`pending` until claimed; `claim_task` reserves `owner/session/gen`; re-pick refuses `task_not_pending`) |
| `drift:<class>:<key>` | `drift:aging-draft:feature_kb_akb`, `drift:iteration-log:meta_harness_3` | `task drift-<class>-<key>` (hygiene claim reserves the fix slot; actual fix stays D4 `splice/sync` proposal) |
| `unscoped:<id>` | `unscoped:001`, `unscoped:002` | `task unscoped-<id>` (claim reserves scoping slot; `fire` still refused until scoped — stays proposal) |

## 5. Next (Design → code)

- `omt_phase{minor_feature, Design}` → handle grammar + `claim_handles` view shape (pure) + `probe`/`apply_selection` threading points + golden list → Programming (map + view + threading, receipt-disciplined) → `omt_complete{advance_to:Testing}` + test report.
