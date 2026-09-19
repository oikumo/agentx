# Analysis 001 — O2 multi-select + directive protocol (scope for approval)

> Feature: `feature_111.multi_select_directive_protocol` (`minor_feature`, project `meta_harness_11`) · Phase: Analysis · Date: 2026-09-19.
> Resumes: PROJECT.md §Plan O2 + gaps doc G5/G6/G8/G9 + O1 shipped Done (feature_110, rev 60, WORK.md whole-project menu with stable IDs).

---

## 1. Problem (reproducer)

Cold start on rev 60 renders the O1 whole-project menu but the agent cannot consume a multi-pick:

- Live `probe rev 60`: `enabled:[]`, `observation:drained_complete`, `menu.next:none`; WORK.md overlays O1 `Options:` — 19 `proj:<slug>` + 9 `drift:<class>:<key>` + 2 `unscoped:<id>` (e.g. `proj:rag_v2`, `drift:aging-draft:feature_kb_akb`, `unscoped:001`), `NEXT: proj:agentx_concurrent_development (recommended)`.
- User says "do `{proj:rag_v2, unscoped:001}` with directive X on the second". There is no defined syntax/semantics for picking 2+ items, no `question`-tool binding, no `pick {id,…} + per-id directive` grammar (G5). Directives have no slot — no token color / overlay annotation / ledger `net_*` field, and 042 synthesis is deterministic templates, not free-form prose (G6).
- Agent must hand-translate the pick into N sequential `fire`/`splice`/`claim`/`sync` calls with reasoning (G8). No `select → splice/fire/claim` transaction exists: no atomic "apply selection R→R+1 + ledger + re-render" op, no rollback on partial multi-pick.
- Emulating with N fires breaks atomicity: fire #1 bumps rev 60→61, fire #2 is rev-stale or half-applied; `propose_diff` serial-mirror (`sync_md.py:270-279`) keeps the first fire and blocks the rest with `blocked_by: [agent_attention]` (cap 1, F7) — multi-pick silently serializes with no batch refusal/re-render path (G9 + G4 race).

Reproduce: present WORK.md `Options:` (30 IDs) → attempt `pick {proj:rag_v2, unscoped:001}` → no grammar to parse, no single rev-checked apply, N manual fires diverge.

## 2. What O2 must prove (oracle)

- **Selection grammar (parse-only, deterministic, stdlib-only):** `pick {id,…} + per-id directive` where each `id` is an O1 menu ID (`pool:<t> | proj:<slug> | drift:<class>:<key> | unscoped:<id>`); directives are opaque per-ID strings (`pick {proj:rag_v2, unscoped:001} + unscoped:001:"scope to read-only spike"`). Unknown ID → refuse with re-render of valid `Options:` (no invented options, D19 kept).
- **One `apply_selection` transaction (atomic, rev-checked):** resolve each ID to a plan of existing closed-enum ops only (`claim`/`fire --expected-revision`/`splice`/`sync`, per 046 session whitelist) → validate all against `probe` at rev R → apply all-or-nothing at R with single ledger `net_*` record + WORK.md re-render; any step blocked/stale → refuse + re-render, zero partial marks. Serial execution stays (F7 `agent_attention=1` NOT reversed here — M0 slice; batch atomicity first, parallelism is O4).
- **Directive attach as overlay annotation (opaque):** directives ride as overlay annotations keyed by selection ID (no net semantics, no new places/transitions — Tier-3 excludes net; no directive→fragment synthesis — deferred O6/D1). Annotations survive re-render for audit; net behavior unchanged if annotations stripped.
- **Ordering + stamp preserved:** D19 `NEXT / Other / Blocked / Resources` + `Options:` + `Lanes:` + `<!-- net_rev:R -->` round-trip through apply; stale-R batch refuses with fresh menu (G4 fire-time guard extended to batch scope).
- Out of scope: claim handles/reservation (O3), worktree dispatch/join/WIP runtime (O4, needs F7 reversal), menu-time freshness/live view (O5), agentx bridge + directive→fragment (O6, needs D1 revisit).

## 3. Resource budget

- Code: new pure helper (e.g. `scripts/omt/net/apply_selection.py`: grammar parse + ID→op-plan + atomic-apply composer, stdlib-only, no net I/O) + thin caller threading in `state.py`/cli (existing `fire --expected-revision` / `claim` / `splice` / `sync` paths reused, no new net places/transitions). `src/agentx/` untouched (D1).
- Tests: new goldens `tests/scripts/omt/test_net_apply_o2.py` (grammar accept/refuse, unknown-ID refuse, atomic rollback on blocked second item, stale-rev refuse + re-render, directive annotation round-trip, D19 + rev-stamp) — needs tests/ canary approval; e2e receipt per harness-surface round discipline (one edit per file per receipt).
- Runtime: one `probe` (validate at R) + one batch commit + one `sync net_to_md` re-render; no extra live loop (freshness stays fire-time; menu-time is O5).

## 4. ID consumption table (O1 → O2)

| O1 menu ID | Example (rev 60 live) | O2 plan sketch (existing ops only) |
|---|---|---|
| `pool:<transition>` | (none enabled live) | `fire --expected-revision R` single transition |
| `proj:<slug>` | `proj:rag_v2` (active) | `claim`/session-bind logical work + `sync` note (no net identity change — coverage stays anonymous until O3) |
| `drift:<class>:<key>` | `drift:aging-draft:feature_kb_akb`, `drift:iteration-log:meta_harness_3` | hygiene fix as scoped `splice`/`sync` proposal (analyzer-validated, D4 proposal-only) |
| `unscoped:<id>` | `unscoped:001`, `unscoped:002` | scoping note as overlay annotation (no fire until scoped — stays proposal) |

## 5. Next (Design → code)

- `omt_phase{minor_feature, Design}` → grammar spec + `apply_selection` plan/composer shape (pure) + caller threading points + golden list → Programming (parse + composer + threading, receipt-disciplined) → `omt_complete{advance_to:Testing}` + test report.
