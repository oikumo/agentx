# PROJECT: meta_harness_8 — Consolidated Meta-Harness Backlog (supersedes mh2/mh3/mh5/mh7/concurrent/net_enforced)

> Status: **active** · **v1.0 (2026-09-12)** — created by `project.py new --slug meta_harness_8`. Consolidation session: closed 6 active meta-harness projects (mh2 --force, mh3, mh5, mh7, concurrent --force for 047 tombstone, net_enforced) per user approval; mh4/mh6 already complete (untouched). Iterate freely (non-gated); spawn features with `new_feature.py "<name>" --type <tt> --project meta_harness_8`; log sessions in CURRENT_STATE.md (newest on top).

---

## New Session Quick Start

> One line: `meta_harness_8` is the **single actionable backlog** for all pending meta-harness work — 5 tracks (T1–T5), ~30 items condensed from 6 closed projects; nothing scheduled, each item ships as its own feature in track order unless reprioritized.

**Next:** T2-2 `tdd-same-node-lint` / T1-2 schema-autolink / T1-5 nav-caps (cheapest unblocked; T2-1 `op:sync` DONE via feature_065, T2-3 batch-consult DONE-zero-carry via mh7 feature_066) — scaffold via `new_feature.py "<name>" --type minor_feature --project meta_harness_8`, overlap-check §Decisions D5 first.

---

## Summary (one line)

**All pending work from meta_harness_2/3/5/7/concurrent/net_enforced, condensed from ~40 scattered Phase-B/C/wave/inbox items into 5 conceptual tracks (observability, ergonomics, token economy, policy integrity, concurrency-next) — deferred items (U15 capability inventory, modified-method body-hash, multi_session_concurrency) DROPPED per user 2026-09-12, concurrent core + 050 gate recorded as done, each track item is a standalone `minor_feature` (P2-1 + T3 digest get a short design note).**

---

## Purpose

### What this project is

- The **sole home** for future meta-harness work. The 6 closed projects remain readable (PROJECT.md/CURRENT_STATE.md + FEATURE.md/test_report.md) but take no new features; mh8 is where new `new_feature.py --project meta_harness_8` scaffolds land.
- A **conceptual condensation**, not a copy-paste: overlapping asks merged (e.g. mh2 U14 + mh7 P1-3 → one schema/autolink story; mh2 U16 + mh7 P2-2 → one delegation story; D-bar + P2-3 → one batch story; F-quickfix + P2-1 → one workflow-index story).
- **Execution-ready**: every item has source pointer, mechanism sketch, and acceptance shape so a fresh session can scaffold without re-reading 6 PROJECT.mds (pointers preserved in §References for audit).

### What this project is **not**

- NOT re-opening shipped work (mh2 Phase-A omt_q, mh3 Phase-A 028, mh5 038, mh7 Wave-0 060–063 + 064 slice-1, concurrent 039–046/048/049 + 042–044 optionals, net 050, mh4 037, mh6 051–059). Shipped verdicts stand (D5).
- NOT carrying the 3 dropped deferreds (D3): mh2 U15 opencode-capability inventory, mh3 P1-3-modified body-hash extension, net Phase-B `multi_session_concurrency`. Do not re-propose without new evidence.
- NOT weakening protections: g.think/g.protect semantics, two-hats + genuine-RED + REFACTOR auto-revert, gates net-zero (10/12), KNOWN empty, Tier-3 excludes net, receipt round-robin — all inherited locks stand.
- NOT scheduling: tracks are grouped by concept, order within/between tracks is proposal (T2/T1 first — cheapest, most unblocked); user reprioritizes at scaffold time.

---

## The 5 tracks — condensed actionable backlog

> Conventions: `Source` = closed-project pointer (proves no invention). `Acceptance` = done-shape (golden/test/report). Sizes default `minor_feature` (§12 decl-only) unless noted. Overlap-check D5 before every scaffold.

### T1 — Interrogative & observability (ask before act; cheapest reads first)

| # | Condensed item | Source | Mechanism sketch | Acceptance |
|---|---|---|---|---|
| T1-1 | `op:audit` ordered skip audit + U12 bootstrap fingerprint | mh2 U4 + U12 | `omt_q{op:audit, feature}`: ordered skips w/ scope tallies; per-feature `skip reason LIKE %TDD bootstrap%` template list | Golden: ordered audit matches ledger order; template list returns last-3 bootstrap reasons |
| T1-2 | Design↔testing schema audit + project-autolink | mh2 U14 + mh7 P1-3 | `op:audit` variant joining `4.design/features/<slug>` vs `6.testing/features/<slug>/test_report.md` (5 known gaps); `drift` detail emits exact `project.py link --infer` + `check_projects` fix-it | Golden: flags the 5 known gaps; drift line contains runnable link cmd |
| T1-3 | `op:graph` transitive risk (depth) → HQL gate | mh2 U5 + HQL Phase-C | `omt_q{op:graph, symbol, depth}` over `kb.ir.json refs[]` + thoughts join | Golden: depth-1 vs depth-2 risk sets differ correctly; HQL grammar NOT built until this proves novel asks |
| T1-4 | Historical-temporal replay `as_of` (signature) | mh2 U18 | `as_of:"<commit>"` on state/plan/drift via `git show <commit>:<path>` (IR + ledger tail + thoughts + kb skeleton + KNOWN literal); envelope already carries `as_of_commit` | Gate: `count(q with as_of != HEAD) > 0` k sessions; golden: state-at-C differs from state-at-HEAD on seeded drift |
| T1-5 | Nav-answer caps | mh3 T2 | `omt_nav`/`omt_kb_nav` size cap + truncation marker + narrowing hint (`file:/tag_type:`) | Golden: wide query truncated w/ marker; under-cap byte-identical |
| T1-6 | Workflow index + repair quickfix | mh7 P2-1 + Improvement002 F | `omt_workflow` tool `list(subject?) + plan(workflow)` from subject manifests; machine `gates:` frontmatter (`follow\|override`); FIRST fix canonical-target contradiction (workflow says `./meta/META_HARNESS.md` vs canonical `.meta/META_HARNESS.omt` + rebuild) + header/authority compile check | Acceptance: compiler rejects bad ref/authority contradiction; `list` returns the 6 catalog workflows |

### T2 — Friction & TDD ergonomics (multi-session comfort; message/convention fixes)

| # | Condensed item | Source | Mechanism sketch | Acceptance |
|---|---|---|---|---|
| T2-1 | `omt_tdd{op:sync}` (stranded-red closer) | mh3 P2-4 | New `cli.py cmd_sync`: reuse `gates.py:173-183` dangling-red derivation, write `green` only if test passes else `ok:false` no-write | Golden: 3 stranded REDs now-passing close in 1 call; still-failing node writes nothing |
| T2-2 | TDD same-node lint | mh7 P1-2 | `tdd/state.py` latest-wins check: `green/refactor` warns when `test_node` ≠ latest `red` node | Golden: mismatched node warns pre-toolchain; matched passes silent |
| T2-3 | Think batch consult | mh7 P1-1 | `omt_think{op:list, path:[...]}` or `query:`-scoped consult clears gate for matched files; `risk:` stays per-file | Golden: batch consult clears 3 files; unlisted 4th still blocks |
| T2-4 | Skip-scope alignment | mh3 P2-7 | Coverage-gate override honors `scope:tests` (natural scope) OR error names exact required `omt_skip` call | Golden: `scope:tests` satisfies coverage override (or message states `scope:'all'` verbatim) |
| T2-5 | g.kb per-file Read-recency | mh3 P3-9 | NEW per-file Read-recency record (enforcer after-hook writes `{file,ts}`); `g.kb` predicate consults per-file (NOT think-consult `recent_consults` mirror) | Golden: read-then-edit same turn passes; never-read file still blocks |
| T2-6 | Conventions + lints (structural-pin, date lint) | mh3 P2-5/P2-6 | GOTCHA_ entries (structural-pin-not-count-pin; `now-timedelta` vs absolute-date) + date-literal lint (`ts = "20\d\d-…"`) | Golden: lint flags planted literal; entries nav-queryable |
| T2-7 | Scaffolds + LSP allowlist | mh3 P3-10/P3-11 | `new_feature.py testing/implementation --feature <slug>` correct `.meta/...` paths; known-LSP-error allowlist suppresses pre-existing noise, surfaces planted-new | Golden: scaffold paths correct; pre-existing 4–9 main_controller/tui errors hidden, new one surfaces |

### T3 — Token & performance economy (pay for signal, not repetition)

| # | Condensed item | Source | Mechanism sketch | Acceptance |
|---|---|---|---|---|
| T3-1 | Escape-replay fold | mh2 U17 | `op:plan` predicted-block `msg` gains `last_escape:{scope,reason,ts}` from most-recent matching `skip` (live-smoke×63/nav precedent); agent still calls `omt_skip` (read-only) | Metric: same-reason replay rate; golden: predicted block carries last live-smoke escape |
| T3-2 | Delegate-advisory fold + fanout recipe | mh2 U16 + mh7 P2-2 | `op:state` resume / `op:plan` research-shaped path returns advisory `delegate_hint:{subagent_type, suggested_prompt}` (never enforced); one loop recipe `explore(read-only) → propose → approval → execute` with ledger-session scoping | Metric: `task(/subagent_type` hits 0 → non-zero; golden: research-heavy resume emits hint |
| T3-3 | Resume digest (duplicate-read mitigation) | mh3 T3 (design-needed) | `omt_status` resume-digest ≤ ~2KB so post-compaction resume costs 1 small read not N full re-reads (read = 66% tool bytes; 29× worst) | Design note first; golden: simulated post-compaction resume = 1 digest read |
| T3-4 | Task-cost benchmark (first measurement) | Improvement002 A | Pinned-rev 6-task sample (bugfix, cross-layer, major, harness repair, resume, concurrent conflict) + seeded harmful actions; record success/regressions/interventions/blocks/recovery/verify-time/real I/O tokens; removal experiments per gate | Acceptance: repeatable script + first numbers, no policy change; target (not promise): −50% harness calls / −20% tokens small-task, all seeded violations caught |
| T3-5 | Task-prep op slice (obligations in one call) | Improvement002 B | Vertical C+B slice for routine bugfixes: one bounded prep response (identity, relevant knowledge, restrictions, evidence, next valid action) + risk model by change characteristics; P0-1 preflight is foundation | Acceptance: 1 prep call covers routine task; block == preflight decision; measure-before-broaden |
| T3-6 | Selective verifiable knowledge pilot | Improvement002 E (+P0-3/P1-1) | Metadata (symbol/contract, test ref, content ver, expiry) on top repeated-discovery lessons only; change-surface retrieval (+dependents); version-triggered refresh; promote hot testable lessons to checks then retire prose | Acceptance: relevant change refreshes, unrelated edits don't re-consult; retrieval-quality check green |
| T3-7 | Budget-diet-bot | mh7 P1-4 | `harnessc.py build` warns `suggest -N bytes: longest @tool describes` within 64B of any byte cap (tool_args/schemas/nav_index tight) | Golden: near-cap build emits suggestion; far-from-cap silent |

### T4 — Policy semantics & batch integrity (one evaluator; validate at boundary)

| # | Condensed item | Source | Mechanism sketch | Acceptance |
|---|---|---|---|---|
| T4-1 | Typed policy semantics (foundation for prep) | Improvement002 C | Typed policy data over small primitives; ONE evaluator for preflight/enforcement/explain; separate durable progress vs temp grants vs consultation evidence (8h expiry vs scope-shadow — verify before treating as defect); reuse ledger + net rev | Acceptance: preflight == enforcement == explain on seeded cases; prose-only exceptions (e.g. `g.net skip_ok=false` vs expiring scope-all) eliminated |
| T4-2 | Receipt batch mode + D-bar (same patch same treatment) | mh7 P2-3 + Improvement002 D + mh3 P3-12 | `harnessc.py stage --feature N` snapshots mtimes, allows N files, single `e2e` at end if `check` green; fail-closed outside stage; adopt D acceptance as done-criteria (same patch same treatment any edit count; input change invalidates receipt w/ digests+policy-ver+tests+deps; broken behavior fails; user edits preserved) + auto-refresh variant | Golden: 2-file logical fix stages once, e2e once; input change invalidates; failing refresh still blocks |
| T4-3 | Completion hardening (content-bound evidence) | Improvement002 D-part | Strengthen completion beyond call-coverage with representative faults (receipt carries digests + policy ver + toolchain + results) | Golden: seeded broken behavior fails completion; temp inconsistency inside batch OK, boundary validation required |

### T5 — Concurrency-next + discovery loop (expanded 2026-09-12 per `.sandbox/meta/META_HARNESS_CONCURRENT_NEXT_STEP.md`; bindings-first, correctness-before-throughput)

| # | Condensed item | Source | Mechanism sketch | Acceptance |
|---|---|---|---|---|
| T5-1 | 2A `net_transaction_authority` (FIRST within T5) | NEXT_STEP §5 + §33 (amends mh7 slice-2) | `CoordinationLock` (flock + abstraction); revision check inside lock on EVERY mutation path (fire/splice/sync/migrations/binding edits/recovery/integration); `command_id` idempotency; stable codes (`stale_revision`, `command_id_conflict`, …) | 2 procs from rev N → exactly 1 commit + 1 `stale_revision`; same-ID retry = same result, no double-fire |
| T5-2 | 2B `task_claim_generation` | NEXT_STEP §6 (claim+generation, rev≠gen) | Task-aware `work_start`/claim txn (rev + readiness + owner + capacity + scope); owner/session/generation capability; release/transfer; no unbound managed start | Same-task race = 1 winner; unrelated rev bump doesn't revoke gen; stale gen cannot checkpoint/submit |
| T5-3 | 2C `worktree_execution_isolation` | NEXT_STEP §7–§9 | Shared `OMT_COORDINATION_ROOT`; 1 branch/worktree per generation (`omt/T17/g3`, `.worktrees/T17-g3/`, base/head/patch_digest); managed gate (owner/gen/workspace/scope); stale cannot publish | Two dirty worktrees, one coordination state; claim can't edit integration tree |
| T5-4 | 2D `two_worker_capacity_scope_arbitration` | NEXT_STEP §10–§11 | `worker_slots=2` migration (splice, ≤15 places); component-aware scope conflicts (ancestor/descendant, not prefix); probe menu parallel choices | A+T1, B+T2 concurrent; T3 refused with `worker_capacity_exhausted` or `scope_conflict(blocking_task)` |
| T5-5 | 3A `verification_integration_lane` | NEXT_STEP §13 | `verifying → integration_ready → integrating` + `test_slots=1, integration_slot=1`; immutable result refs; coordinator-only integrate; combined acceptance | Locally-green pair fails combined → objective stays unsatisfied with evidence |
| T5-6 | 3B `recovery_and_transaction_journal` | NEXT_STEP §14–§15 | Heartbeat/liveness → recovery-candidate; gen-incrementing transfer; preserved checkpoint; `net_txn.pending.json` + startup reconcile | Kill worker mid-work → lossless handoff; stale submit = `stale_generation` |
| T5-7 | 3C `evidence_dependency_completion` | NEXT_STEP §12 | Result/evidence digests; deps on accepted artifact versions; staleness detection (`dependency_stale`); objective acceptance on integrated state only | Downstream verified vs old upstream → `dependency_stale`; no self-report Done |
| T5-8 | Fresh-review loop (recurring discovery) | mh5 D4 mechanism | Produce `_idea.md` at current HEAD when backlog empties (audit @-records/nav-index/gotchas/budgets/records); top genuine DX win → new feature in THIS project | Acceptance: review doc + 0/1 new wins declared; never re-runs shipped/rejected 10 without new evidence |

> T5 order is strict in slice order (2A→2B→2C→2D→3A→3B/3C); T5 as a whole stays after T2/T1 per §Scope wave order unless reprioritized. Program-level Done = NEXT_STEP §32 13-point end-to-end demo. Each slice ships as its own `minor_feature` (2A + 3B get a short design note for lock/journal).

---

## Scope & success criteria

**Scope:** T1–T5 above (≈31 actionable items after 2026-09-12 T5 expansion 3→8). Each ships as its own feature (default `minor_feature`, decl-only; T1-6 P2-1 part + T3-3 digest + T5-1 lock + T5-6 journal get a short design note, not a §12 major gate). Wave/order proposal: T2-1/T1-2/T1-5 (cheapest, unblocked) → T2-2/T2-3 → T3-1/T3-2 → T4-1/T3-5 slice → T4-2 → T1-4/T1-3 → T5 slices in strict 2A→2B→2C→2D→3A→3B/3C order → T3-4 benchmark anytime (no policy change).

**Success (project-level):**
1. Every item shipped OR closed-with-verdict in Decisions log (no silent drops).
2. Suite stays green with KNOWN empty (shape-pinned; current 2015+17 baseline at mh8 birth); `harnessc check` 0 errors + `build` OK after every feature; byte budgets green (P1-4 owns the warning).
3. Friction deltas vs mh7 §Baseline + mh6 close + mh3 token evidence: `nav-escapes 53 → <20/7d`; `block_count/edited_files` down; `tools_called_pre_task/1` down; `op:plan` pre-flight hit-rate up; post-compaction resume = 1 digest.
4. No new gate without retirement (10/12 net-zero holds); think/protect untouched; no auto-`omt_skip`; Tier-3 still excludes net.
5. End-of-program re-evaluation vs baselines shows consults/session + denials/session down; `task(/subagent_type` non-zero; `as_of != HEAD` asked (else U18/HQL stay parked).

**Out of scope / guardrails:** D3 dropped trio (U15, modified-hash, multi_session_concurrency — the last PARTIALLY re-admitted as managed-local 1+2 by D8 with new evidence); no gate removals; no `src/agentx/` work (agentx features 001/002 stay unscoped elsewhere); no free-form goal synthesis; no distributed execution (legacy solo keeps `agent_attention`=1; managed T5-4 migrates to `worker_slots=2` one-machine only); receipt round-robin until T4-2 ships (ONE edit/file/round + e2e refresh; e2e file receipt-EXEMPT).

---

## Status

- [x] Consolidation DONE 2026-09-12: 6 projects closed (mh2 --force for 020/022/023 short-slug completes + concurrent --force for 047 tombstone; mh3/mh5/mh7/net clean-close); mh8 home created; this PROJECT.md v1.0 written (5 tracks, deferred trio dropped per approval).
- [x] T2-1 `op:sync` DONE 2026-09-12 (feature_065.tdd_sync_stranded_red_closer, minor_feature) — first linked feature, header draft→active.
- [x] mh7 Wave-0 + slice-1 + P1-1 absorbed DONE-zero-carry 2026-09-12: feature_060/061/062/063 (Wave-0) + feature_064 slice-1 + feature_066 think-batch-consult (== mh8 T2-3) all `complete` under closed mh7; no re-implementation in mh8 (D7).
- [x] meta_harness_7 CLOSED 2026-09-12 (re-close after Wave-1 execution; 6/6 linked features complete, clean-close no --force) — mh8 sole home for remaining mh7 waves (D7).
- [x] T5 expanded 3→8 (2026-09-12, user-approved): NEXT_STEP 2A–2D/3A–3C replace coarse slice-2/slice-3 rows; D8–D14 locked; strict slice order; 13-point demo is T5 Done-bar.
- [x] T4-2 `receipt-batch-mode` DONE 2026-09-12 (feature_074.receipt_batch_mode, minor_feature) — `harnessc.py stage` + staged bypass + content-bound receipt (digests + policy_ver + toolchain); 5 goldens + boundary e2e green, `harnessc check` 0 errors, omt-suite 458 green (1 pre-existing budget-pin failure from uncommitted 071–073 WORK.md drift, untouched by T4-2).
- [x] T4-3 `completion-hardening` DONE 2026-09-12 (feature_075.completion_hardening_content_bound_evidence, minor_feature) — validate-exit runs the feature's own tests (seeded broken behavior fails completion; golden in `tests/scripts/omt/test_completion_hardening.py`); receipt gains `results` (guard: `receiptResultsPassed`); 5 goldens + boundary e2e green, `harnessc check` 0 errors, suite 2063/2064 (pre-existing budget-pin failure unrelated).
- [x] T1-6 `workflow index + repair quickfix` DONE 2026-09-12 (feature_076.workflow_index_and_repair_quickfix, minor_feature) — evolution.md canonical-target contradiction fixed (step 6 → `.meta/META_HARNESS.omt` + `harnessc.py build`); `<!-- authority: follow|override -->` markers on all 6 catalog workflows; `harnessc check_workflows` (missing-marker/missing-file/projection-edit → error; unlisted-on-disk → drift warning, 1 live flag on `meta_harness_development_self_evaluation.md`); `harnessc workflows [--subject X] [--plan W]` subcommand (list = exactly the 6 catalog workflows). 16 goldens + boundary e2e green; suite 2079/2080 (pre-existing budget-pin only). Impl diverged from the T variance column per user pick: harnessc CLI subcommand instead of an `omt_workflow` tool (tool budgets ~99% full).
- [x] T1-4 `as_of` historical-temporal replay DONE 2026-09-12 (feature_077.as_of_historical_temporal_replay, minor_feature) — `omt_q{state|plan|drift, as_of:"<commit>"}` replays ledger(+archives)/ir/kb.ir/thoughts/state.py via `git show`; historical `featurePhaseAt` (tombstone-aware, no liveness window); `as_of_scope` marks live leftovers (plan session-state/receipt, drift project_drift); q-ledger `as_of` now records the resolved sha (U18 adoption-gate measurable). Incidental: feature_059 tight-budget pin re-pinned post-measure (KNOWN stays empty). 3 goldens (state-at-C≠HEAD on seeded drift) + boundary e2e green; suite 2084/2085 (only pre-existing environmental live-opencode timeout, stash-verified at clean HEAD).
- [x] T1-3 `op:graph` transitive risk DONE 2026-09-13 (feature_078.op_graph_transitive_risk, minor_feature) — `omt_q{op:graph, symbol, depth}` BFS 1..3 over `kb.ir.json` refs[] + thoughts join (mention-match, cap 5); `as_of` replays kb+thoughts; unknown-symbol fail-open; HQL grammar explicitly NOT built (op:hql stays unknown, pinned). 3 goldens (depth-1 vs depth-2 differ on seeded `g.a→{g.b,g.d}, g.b→g.c` + live `doc.mvcpp` smoke) + boundary e2e green; `harnessc check` 0 errors, `build` OK (tool_args budget deliberately 2304→2400, tool_schemas fits at 1780/1792); suite 2088/2088 (feature_059 pins re-measured: NAV_INDEX 63931, TOOL_ARGS 2367, TOOL_SCHEMAS 1780). Incidental discipline notes in test report (skip-latest-wins, stage-vs-policy_ver, raw-stdout unknown-op asserts).
- [ ] Next: T5-1 2A (`net transaction authority`, design note; strict T5 slice order); T3-4 benchmark anytime (no policy change); T5-8 loop when backlog empties. Open repair flag: `meta_harness_development_self_evaluation.md` unindexed (warning) — index into meta_harness META.md or remove, when convenient.

---

## Decisions log (locked — do not re-litigate without new evidence)

- **D1 — close 6 active only (2026-09-12, user-approved):** `meta_harness_2, meta_harness_3, meta_harness_5, meta_harness_7, meta_harness_concurrent, net_enforced_harness` → complete. mh4/mh6 already complete (untouched). mh2 --force rationale: 020/022/023 lack `complete` records under full slugs (old short-slug era: `feature_021/022/023` completes exist); concurrent --force rationale: `feature_047.wip_limited_pool` tombstone (renamed to 048 per D20) has no complete.
- **D2 — 5-track condensation approved (2026-09-12):** T1 observability / T2 ergonomics / T3 economy / T4 integrity / T5 concurrency-next as defined above. Merges recorded inline (U14+P1-3, U16+P2-2, D+P2-3, F+P2-1).
- **D3 — deferred trio DROPPED (2026-09-12, user-selected "Drop deferred"):** mh2 U15 capability inventory, mh3 modified-method body-hash, net Phase-B `multi_session_concurrency` (was deferred 2026-09-05) are NOT carried into mh8. Re-proposal needs new evidence.
- **D4 — concurrent core recorded DONE, zero carry:** 039/040/041/045/046/048/049 + 042/043/044 optionals all have `complete` records; pool net rev 57 (12/15 places) + Tasks-menu render stand as built. T5 slices build ON them, not re-litigate D1/D16–D20.
- **D5 — inherited locks stand:** mh6 D1–D6/DG1–DG3 (net solo-only, Tier-3 excludes net, KNOWN empty, gates net-zero) + mh7 DG1–DG3/D1–D4 + mh3 D1–D9 + mh2 v1 lock (read-only above mechanics) + mh5 D1–D4 (shipped/reject verdicts). Overlap-check before every scaffold (no re-implementation).
- **D6 — execution discipline:** receipt round-robin + canary ordering (phase→skip→tests) + `harnessc check && build` + e2e receipt per harness-surface round; `uv` only; `src/` edits need `omt_phase` first (this doc is `.projects/`, non-gated).
- **D7 — mh7 closed, residual absorbed (2026-09-12, user-directed):** `meta_harness_7` → complete (clean-close, 060/061/062/063/064/066 all `complete`, no --force). Pending→mh8 mapping verified, zero new rows needed: P1-2→T2-2, P1-3→T1-2, P1-4→T3-7, P2-1+F→T1-6, P2-2→T3-2, P2-3+D→T4-2, A→T3-4, B→T3-5, C→T4-1, E→T3-6, slices 2–3→T5-1/T5-2. T2-3 DONE-zero-carry via mh7 feature_066; slice-1 DONE-zero-carry via mh7 feature_064; Wave-0 DONE-zero-carry via 060–063. Shipped verdicts stand (D5).
- **D8 — managed local concurrency re-admitted (2026-09-12, amends D3 + `agent_attention=1` guardrail):** new evidence = 064 slice-1 DONE + TOCTOU race analysis + 1-coordinator/≤2-workers/one-machine scope in NEXT_STEP. Solo behavior frozen; managed mode is explicit enrollment only. `agentx_concurrent_development` draft stays untouched — mh8 is the sole home, no program split.
- **D9 — claim + generation, revision ≠ generation (NEXT_STEP D4/D5):** ownership is a durable claim with monotonic generation (no auto-expiring lease); heartbeat is observation only. Global revision = short CAS token; task generation = long ownership fence.
- **D10 — transaction authority first:** every authoritative mutation (fire/splice/sync/migrations/binding edits/recovery/integration) under one local `CoordinationLock`; revision check inside the lock. T5-1 gates all later T5 slices.
- **D11 — one coordination root + per-generation worktree/branch:** `OMT_COORDINATION_ROOT` shared by all workers; `omt/T17/g3` + `.worktrees/T17-g3/` + base/head/patch_digest in binding; stale workspace survives but cannot publish.
- **D12 — managed gates task/owner/gen/workspace/scope-aware:** from the first worker (not `active>1`); no ambient recent-start receipt in managed mode; break-glass explicit + audited; legacy solo verdicts untouched.
- **D13 — topology migration last within T5; ≤15 cap holds:** 6 lifecycle + 3 resources + optional goals (9–11 places); blocked stays binding metadata; task identity never becomes one-place-per-task.
- **D14 — `command_id` idempotency on all mutations:** same ID + same payload = same result; same ID + different payload = `command_id_conflict`; stable refusal codes throughout.

---

## References

- Closed homes (read-only): `.projects/meta/meta_harness_2/PROJECT.md` (U-set U1–U18, token-lever map, Phase-B/C table) + `CURRENT_STATE.md` · `meta_harness_3/PROJECT.md` (P1/P2/P3+T1–T3, R1–R11, D1–D9) · `meta_harness_5/PROJECT.md` (10-item backlog verdicts + 038) · `meta_harness_7/PROJECT.md` (11-item program Waves 0–2 + Improvement002 A–F intake + concurrent slice-1 + baselines) · `meta_harness_concurrent/PROJECT.md` (D1–D20, core 039–041/045 + 046/048/049 + 042–044) · `net_enforced_harness/PROJECT.md` (050 Alt-A + deferred Phase-B note).
- Evidence: `sandbox/meta/improvement002/IMPROVEMENT_OPTIONS.md` (A–F) + `AGENTX_CONCURRENT_WORK.md` (slices, bindings, demo) · `.sandbox/session_2026-08-15_feature_027_completion.md` (mh3 evidence) · `.sandbox/meta_harness_5_idea.md` (038 origin) · opencode.db token analysis (mh3 §Token evidence: 1009 sessions, 68.8MB tool bytes).
- T5 design basis: `.sandbox/meta/META_HARNESS_CONCURRENT_NEXT_STEP.md` (2026-09-12, 2150 lines — claim+generation, transaction authority, worktrees, managed gates, 2A–2D/3A–3C slices, 13-point demo; §23 home recommendation SUPERSEDED by D8 — mh8 is the home).
- SSOT: `.meta/META_HARNESS.omt` (gates/budgets/tools) · live net rev 57 · WORK.md Tasks (net render).
- Approvals this session: close-6-only + 5-tracks + drop-deferred (question-gate 2026-09-12).
