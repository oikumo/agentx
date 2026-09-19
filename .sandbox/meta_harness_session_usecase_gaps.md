# Meta-Harness vs Session Use-Case — Gap Evaluation

> Date: 2026-09-19 · Scope: `meta_harness` only (D1) · Method: WORK.md-only startup + `omt_status`/`omt_q{state,drift,plan}` + `omt_net{probe,invariant}` + `PROJECT.md/CURRENT_STATE.md` (meta_harness_concurrent) + `features.md` + `.workflows/META.md` via `omt_nav` first (nav-gate honored; no grep/glob on docs).
> Live evidence rev: net rev 60 / ledger rev 60, commit `d282a4c5eba555f81a6baca90e7d349a88218858`.

## 1. Target use-case (as requested)

1. **Per opencode session:** agent presents the **current state of the whole project + next step(s)**.
2. **User selects one or multiple options** to do, with free directives.
3. **Agent adapts the internal global-state Petri net** to the selection.
4. **Agent does the work concurrently as dictated by the Petri net.**

Success = cold-start → whole-project menu → multi-pick → net splice/fire/claim → parallel execution with capacity/deadlock safety → WORK.md re-render + audit.

## 2. What the harness already does (no gap)

| Use-case step | Existing mechanism | Evidence (2026-09-19 live) |
|---|---|---|
| Present state at session start | `STARTUP`: read WORK.md only, ≤15-line summary + Tasks menu `NEXT / Other enabled / Blocked / Resources` in order, no invented options (D19) | WORK.md `<!-- net_rev:60 -->` block: `NEXT:none / Other:none / Blocked:none / Resources:4/4 free / Pool:pending=0 active=0 done=7 (places 15/15)`; `omt_status` resume digest; `INJECT` STARTUP Tasks-menu line (feature_049) |
| Net as global-state SSOT | ONE flat WIP-pool supervisor net + sidecar + overlay = state; ledger = audit; WORK.md = projection (D16); 3-file atomic splice/sync, revisioned fire, conformance gate | `probe rev60`: marking `work_done=7, work_pending=0, work_active=0, agent_attention=1, worker_slots=2`, `enabled=[]`, `observation:drained_complete`, `bounded:true`; `invariant`: `drifted:false, net_rev=ledger_rev=60`, all capacities ok |
| Deterministic WORK.md projection | `sync_md.py` render/parse/propose + `omt_net{op:sync}` md directions; rev-stamped Tasks block; stale-rev refuse + re-render (D4) | feature_045 DONE (net 98 green); feature_048 pool line `Pool: pending/active/done (places N/15)`; feature_049 `menu_lines` pool-aware + `fire --expected-revision` guard + 6 menu tests |
| Single-option pick → fire | Manual `fire(work_start/work_complete, reasoning, session)` with capacity check; analyzer blocks invalid fires | probe `menu.next:none, other_enabled:[], blocked:[], parallel:[], capacity workers 0/2 free 2, verification 0/1, integration 0/1`; PROJECT D19 non-goal: "no fire-on-pick automation (user picks, agent fires with reasoning)" |
| Approval discipline | `.workflows/` mandatory approval gate (propose in sandbox → user picks → execute → record Result); OMT gates keep enforcement, net never overrides gate (D3) | `.workflows/META.md` §§3.3/4.3: no state-mutating tool past gate without explicit pick; 6 workflows (agentx 2, meta_harness 3, akb 1) |
| Concurrency modeling | Complement-place resources (`agent_attention=1, src_edit_capacity, tests_capacity, harness_surface_round`), `place_invariants()`, `deadlocks()/conflicts[]/holders[]`, 15-place cap (D20) | probe `advice.deadlocks_complete:true`, `place_invariants ×8, transition_invariants ×2`; resource_report + pool `work_start` conflicts (feature_041/048) |
| Audit/resume | Ledger `kind:net_*` + phase/complete records; `invariant` drift check at every `omt_complete` exit → `harness.net.drift.jsonl`; `.projects/.../CURRENT_STATE.md` session log | `omt_q{drift}`: 0 drift records on net↔ledger (only project-link/aging-draft hygiene); CURRENT_STATE meta_harness_concurrent top = 2026-09-05 feature_049 DONE |

## 3. Gaps vs the use-case

### A. "Whole project + next step" presentation

- **G1 — Menu is pool-counts, not whole-project state (HIGH).** After D20 the net holds only counts (`pending=0/active=0/done=7`), identity moved to overlay+ledger. Today's render cannot say *which* project/feature is next, only that *a* slot is free. Live proof: 3 projects `active` (petri_net_studio, project_lifecycle, rag_v2) + 3 `draft` but pool shows `pending=0` → menu `NEXT:none`. The user sees "nothing to do" while active projects exist. Whole-project needs: Projects table + per-project next-feature + pool capacity + verification/integration lanes in one view; currently three sources (net counts / WORK.md Projects synced by `project.py sync` / CURRENT_STATE logs) with no single composer.
- **G2 — Empty-menu path has no "next step" generator (HIGH).** `drained_complete` (done=7, enabled=[]) is a terminal observation with no recommendation. PENDING FEATURES (`feature_001 session_user_objectives… scope unset`, `feature_002 rag… scope unset`) and `aging-draft` projects (feature_kb_akb, workflows, 27d) are invisible to `probe.menu`. `omt_q{drift}` also reports `unlinked-project-backed ×10` + `iteration-log ×5` hygiene issues that never surface in the menu. Result: cold start on rev 60 presents an empty menu and stops — the opposite of "all options presented".
- **G3 — No cross-lane next-step synthesis (MEDIUM).** probe exposes `verification {used 0/1 free 1}`, `integration {ready 0/1}`, `worker_slots`, `deadlocks`, `bindings_valid`, but `sync_md` render uses only `enabled[]/holders/conflicts`. Verification/integration capacity, deadlock explanation, and `task_claim_generation / worktree_isolation / capacity_arbitration` (features 080–082) do not flow into NEXT/Other/Blocked text. User cannot tell *why* nothing is enabled or what would unblock it.
- **G4 — Staleness UX is fire-time, not menu-time (MEDIUM).** Rev-stamp + `--expected-revision` refuse stale `fire` (good), but the menu itself carries no freshness guarantee at render time (no auto re-`probe`/`sync` before present). Two sessions can present the same rev 60 menu and race; loser discovers staleness only at fire.

### B. "User selects one or multiple options + directives"

- **G5 — No multi-select protocol (HIGH — core use-case miss).** D19 contract is singular: `NEXT:<fN_start> (recommended)` + ordered list, "no invented options". There is no defined syntax/semantics for picking 2+ items, no `question`-tool binding, no `Other enabled: a, b, c → pick {a,c}` grammar, no handling of "do a+b with directive X on b". `.workflows` approval gate assumes *one* alternative picked. `omt_net fire` fires *one* transition per call. Multi-pick → multi-claim → parallel dispatch is unmodeled.
- **G6 — No directive capture/binding (MEDIUM).** "Following the user directives" has no slot: no place to attach per-selection directives/constraints to the net (as token color, overlay annotation, or ledger `net_*` field), and no `synthesize(template→splice)` path from directive text → net fragment. feature_042 synthesis is deterministic templates (task→chain, dependency→arc) and explicitly *not* free-form; user prose directives fall outside it (D4: agent never edits goals unilaterally, but also provides no directive→net bridge).
- **G7 — No whole-project option enumeration (MEDIUM).** "Current state of the whole project" implies options across all active/draft projects + unscoped features (001/002) + hygiene (drift fixes, unlinked links). Today `Other enabled` = enabled pool transitions only (currently `[]`). There is no `Other` that lists "scope feature_001 / link feature_kb_akb / close aging draft / resume petri_net_studio" as selectable work items with uniform IDs.

### C. "Agent adapts the global-state net"

- **G8 — Adaptation is manual, not selection-driven (HIGH).** No `select → splice/fire/claim` transaction exists. Agent must hand-translate a user pick into `fire`/`splice`/`sync`/`claim` calls with reasoning. PROJECT.md declares this a non-goal ("no fire-on-pick automation"). Consequence: step 3 of the use-case is procedure, not mechanism — no atomic "apply selection R→R+1 + ledger `net_*` + WORK.md re-render" op, no rollback on partial multi-pick.
- **G9 — Closed op enum blocks needed mutations (MEDIUM).** `omt_net` ops are closed (`probe|fire|splice|sync|synthesize|invariant|mine|gate|claim|release|transfer|checkpoint` per TOOL spec; IDEA-002 v4). Multi-select needs: bulk-claim, selection-scoped splice proposal, directive attach, rev-checked batch fire. None exists as a single transaction; emulating with N sequential fires breaks atomicity and risks rev races (G4).
- **G10 — Identity loss blocks targeted adaptation (MEDIUM).** D20 deliberately moved feature identity out of the net (counts in net, map in overlay, audit in ledger). `probe.coverage` confirms: `work_done bindings 0/7 anonymous 7`. Adapting "do feature_001 + rag_v2 fix" cannot address net tokens by ID — must resolve via overlay/ledger first, then fire a generic `work_start`. The net cannot represent *which* work was selected.
- **G11 — No session-scoped claim→menu binding (LOW/MEDIUM).** `claim(task,owner,gen-fenced)`, `gate(path,session?)`, `session` arg whitelist (feature_046) exist, but the menu carries no `claim` handles and `probe.resources[].holders` is empty live. Selecting an option does not reserve it; two sessions can claim the same logical work.

### D. "Do the work concurrently given the net"

- **G12 — Modeled concurrency, serial execution (HIGH — by design, but use-case opposite).** `agent_attention=1` (F7) + `src_edit_capacity=1` + `tests_capacity=1` serialize starts/edits/tests. PROJECT.md Feasibility is explicit: "NOT distributed execution… the agent still executes serially… deliverable is concurrency *modeling*, not *concurrent execution*." `worker_slots=2` is capacity display, not dispatch. The use-case asks for concurrent doing; the harness by design only models it. Features 080–083 (claim generation, worktree isolation, 2-worker arbitration, verification lane) exist per ledger but are not wired into a `menu → dispatch N workers → join` runtime.
- **G13 — No parallel-dispatch / join / WIP enforcement runtime (HIGH).** No component maps `enabled[]/parallel[]` → concurrent tool/sub-agent fan-out with `agent_attention`/`src_edit_capacity` acquisition, per-task worktrees (feature_081), progress `fire`s, and completion join that `fire(work_complete)` + re-render. `parallel:[]` has been empty in every observed probe; `sync`/`splice` never emit a dispatch plan.
- **G14 — No live dashboard / progress projection during concurrent work (LOW).** feature_043 dashboard is static-build only (explicit non-goal: no live view). During multi-task execution the user has no revision slider / deadlock highlight / marking view — only the next cold-start WORK.md render.

### E. Cross-cutting

- **G15 — feature_001 (agentx adaptive net) out of scope severs the loop (MEDIUM).** D1 forbids `src/agentx/`, `internal_state`, `USER_OBJECTIVES.md`, feature_001 work under meta_harness_concurrent. But the use-case's "internal global state petri nets" for *doing user-selected work* is arguably the agentx-side adaptive net (feature_001 ⏳, scope unset), not the harness-development WIP pool. Today neither side owns it: harness models harness projects; agentx `IGoalManager` swap (features.md F001) is pending. A selection like "do rag_v2 + studio fix concurrently" has no net that spans harness state *and* agent execution state.
- **G16 — Measurement/benchmark for "concurrent doing" missing (LOW).** feature_093 task_cost_benchmark + feature_098 honest-cost exist, but no metric proves multi-pick concurrency pays back (wild sessions N≥10 residual noted in WORK.md Paused). Cannot tell if G12/G13 fixes are worth it.

## 4. Recommended next options (for user multi-pick)

| Opt | Title | Closes | Sketch |
|---|---|---|---|
| O1 | Whole-project menu composer (net counts + Projects + drift/hygiene + unscoped 001/002 → single NEXT/Other/Blocked/Resources with IDs) | G1, G2, G3, G7 | Extend `sync_md` render: pool counts + `project.py sync` rows + `omt_q{drift}` hygiene + PENDING FEATURES as selectable proposals; stable IDs; keep D19 ordering + rev-stamp |
| O2 | Multi-select + directive protocol (`pick {id,…} + per-id directive` grammar, `question`-tool binding, batch rev-checked apply/rollback) | G5, G6, G8, G9 | Define selection grammar; one `apply_selection` transaction (claims+fires+splices, atomic, ledger `net_*`, re-render); directive attach as overlay annotation |
| O3 | Identity-aware pool (overlay ID map → claimable menu handles, de-anonymize coverage) | G10, G11 | Overlay `task_id→holder` map; `probe.menu` emits claim handles; `claim` reserves on select; `fire --expected-revision` per handle |
| O4 | Concurrent dispatch runtime (enabled[] → N worktrees/sub-agents → join → work_complete; WIP/capacity enforced) | G12, G13 | Wire 080–083: worktree per claim, 2-worker arbitration, verification/integration lanes, progress fires; explicit reversal of F7 for this lane with new decision |
| O5 | Live progress projection (probe→menu re-render on fire/claim; optional live dashboard slice) | G4, G14 | Menu-time freshness (`probe` before present); re-render push after each fire; minimal live view reusing studio projection |
| O6 | Bridge harness-pool ↔ agentx adaptive net (scope feature_001; USER_OBJECTIVES ↔ net fragment contract) | G15 | Requires revisiting D1; define which net owns execution state vs harness state; directive→fragment via 042 templates |

Suggested minimal use-case slice: **O1 + O2 + O3** (selectable whole-project menu with atomic apply, still serial execution) before **O4** (true concurrency, needs F7/D1 decisions).

## 5. Appendix — live snapshot (rev 60)

- `omt_net{probe}`: `rev 60, marking {agent_attention:1, resource_token:1, src_edit_capacity:1, tests_capacity:1, harness_surface_round:1, work_done:7, others 0}, enabled:[], observation drained_complete, bounded:true, deadlocks_complete:true, menu {next:none, other:[], blocked:[], resources 4/4 free, parallel:[], workers 0/2, verification 0/1, integration 0/1}, coverage work_done anonymous 7/7`.
- `omt_net{invariant}`: `live_marking_invariants_hold:false (structural, not drift), drifted:false net_rev=ledger_rev=60, all capacities ok, conflicts:[]`.
- `omt_q{state}`: phase Unknown, 505 ledger records, 120 risky thoughts, 27 recent consults; `omt_q{drift}`: 0 net↔ledger drifts; hygiene only (unlinked-project-backed, aging-draft 27d, iteration-log).
- `omt_q{plan}` on feature_001 path: all gates unblocked (no think/kb/receipt/net blockers) — scoping is process-free, just unstarted.
- WORK.md: `meta_harness_10 P2 CLOSED 2026-09-19 (rev 60 drained_complete)`; 3 projects active / 3 draft; PENDING `feature_001/002` scope unset; `Pool: pending=0 active=0 done=7 (places 15/15)`.

---
*Proposal doc, no source mutation — written to `.sandbox/` per request (copy of `/tmp/opencode/meta_harness_session_usecase_gaps.md`); no `src/`/`tests/` edits, no phase claim, no commits.*
