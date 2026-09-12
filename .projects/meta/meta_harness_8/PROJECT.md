# PROJECT: meta_harness_8 — Consolidated Meta-Harness Backlog (supersedes mh2/mh3/mh5/mh7/concurrent/net_enforced)

> Status: **draft** · **v1.0 (2026-09-12)** — created by `project.py new --slug meta_harness_8`. Consolidation session: closed 6 active meta-harness projects (mh2 --force, mh3, mh5, mh7, concurrent --force for 047 tombstone, net_enforced) per user approval; mh4/mh6 already complete (untouched). Iterate freely (non-gated); spawn features with `new_feature.py "<name>" --type <tt> --project meta_harness_8`; log sessions in CURRENT_STATE.md (newest on top).

---

## New Session Quick Start

> One line: `meta_harness_8` is the **single actionable backlog** for all pending meta-harness work — 5 tracks (T1–T5), ~30 items condensed from 6 closed projects; nothing scheduled, each item ships as its own feature in track order unless reprioritized.

**Next:** pick the next track/item with the user (default: T2 P2-4 `op:sync` or T1 U4/U14 audit — cheapest unblocked), scaffold via `new_feature.py "<name>" --type minor_feature --project meta_harness_8`, overlap-check §Decisions D5 first.

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

### T5 — Concurrency-next + discovery loop (new scope; bindings-first)

| # | Condensed item | Source | Mechanism sketch | Acceptance |
|---|---|---|---|---|
| T5-1 | Atomic claims (slice 2) | mh7 intake slice 2 (AGENTX_CONCURRENT_WORK) | Atomic claim: rev + readiness + owner + capacity + scope-conflict check; one local transaction authority; stale-owner blocked; ≤15 places; bindings==tokens | Demo: 2 tasks together, 3rd waits with reason; stale owner blocked |
| T5-2 | Integration + recovery (slice 3) | mh7 intake slice 3 | Isolated workspaces + coordinator-owned serialized integration + objective-level acceptance; checkpoints/transfer/recovery; combined-failure blocks goal; fresh agent recovers from shared state alone | Demo: interrupt/resume lossless; fresh-agent recovery from shared state |
| T5-3 | Fresh-review loop (recurring discovery) | mh5 D4 mechanism | Produce `_idea.md` at current HEAD when backlog empties (audit @-records/nav-index/gotchas/budgets/records); top genuine DX win → new feature in THIS project | Acceptance: review doc + 0/1 new wins declared; never re-runs shipped/rejected 10 without new evidence |

---

## Scope & success criteria

**Scope:** T1–T5 above (≈26 actionable items). Each ships as its own feature (default `minor_feature`, decl-only; T1-6 P2-1 part + T3-3 digest get a short design note, not a §12 major gate). Wave/order proposal: T2-1/T1-2/T1-5 (cheapest, unblocked) → T2-2/T2-3 → T3-1/T3-2 → T4-1/T3-5 slice → T4-2 → T1-4/T1-3 → T5 slices → T3-4 benchmark anytime (no policy change).

**Success (project-level):**
1. Every item shipped OR closed-with-verdict in Decisions log (no silent drops).
2. Suite stays green with KNOWN empty (shape-pinned; current 2015+17 baseline at mh8 birth); `harnessc check` 0 errors + `build` OK after every feature; byte budgets green (P1-4 owns the warning).
3. Friction deltas vs mh7 §Baseline + mh6 close + mh3 token evidence: `nav-escapes 53 → <20/7d`; `block_count/edited_files` down; `tools_called_pre_task/1` down; `op:plan` pre-flight hit-rate up; post-compaction resume = 1 digest.
4. No new gate without retirement (10/12 net-zero holds); think/protect untouched; no auto-`omt_skip`; Tier-3 still excludes net.
5. End-of-program re-evaluation vs baselines shows consults/session + denials/session down; `task(/subagent_type` non-zero; `as_of != HEAD` asked (else U18/HQL stay parked).

**Out of scope / guardrails:** D3 dropped trio (U15, modified-hash, multi_session_concurrency); no gate removals; no `src/agentx/` work (agentx features 001/002 stay unscoped elsewhere); no free-form goal synthesis; no distributed execution (`agent_attention`=1 mental model for harness concurrency); receipt round-robin until T4-2 ships (ONE edit/file/round + e2e refresh; e2e file receipt-EXEMPT).

---

## Status

- [x] Consolidation DONE 2026-09-12: 6 projects closed (mh2 --force for 020/022/023 short-slug completes + concurrent --force for 047 tombstone; mh3/mh5/mh7/net clean-close); mh8 home created; this PROJECT.md v1.0 written (5 tracks, deferred trio dropped per approval).
- [ ] First linked feature (header flips draft → active mechanically) — pick from §Next.

---

## Decisions log (locked — do not re-litigate without new evidence)

- **D1 — close 6 active only (2026-09-12, user-approved):** `meta_harness_2, meta_harness_3, meta_harness_5, meta_harness_7, meta_harness_concurrent, net_enforced_harness` → complete. mh4/mh6 already complete (untouched). mh2 --force rationale: 020/022/023 lack `complete` records under full slugs (old short-slug era: `feature_021/022/023` completes exist); concurrent --force rationale: `feature_047.wip_limited_pool` tombstone (renamed to 048 per D20) has no complete.
- **D2 — 5-track condensation approved (2026-09-12):** T1 observability / T2 ergonomics / T3 economy / T4 integrity / T5 concurrency-next as defined above. Merges recorded inline (U14+P1-3, U16+P2-2, D+P2-3, F+P2-1).
- **D3 — deferred trio DROPPED (2026-09-12, user-selected "Drop deferred"):** mh2 U15 capability inventory, mh3 modified-method body-hash, net Phase-B `multi_session_concurrency` (was deferred 2026-09-05) are NOT carried into mh8. Re-proposal needs new evidence.
- **D4 — concurrent core recorded DONE, zero carry:** 039/040/041/045/046/048/049 + 042/043/044 optionals all have `complete` records; pool net rev 57 (12/15 places) + Tasks-menu render stand as built. T5 slices build ON them, not re-litigate D1/D16–D20.
- **D5 — inherited locks stand:** mh6 D1–D6/DG1–DG3 (net solo-only, Tier-3 excludes net, KNOWN empty, gates net-zero) + mh7 DG1–DG3/D1–D4 + mh3 D1–D9 + mh2 v1 lock (read-only above mechanics) + mh5 D1–D4 (shipped/reject verdicts). Overlap-check before every scaffold (no re-implementation).
- **D6 — execution discipline:** receipt round-robin + canary ordering (phase→skip→tests) + `harnessc check && build` + e2e receipt per harness-surface round; `uv` only; `src/` edits need `omt_phase` first (this doc is `.projects/`, non-gated).

---

## References

- Closed homes (read-only): `.projects/meta/meta_harness_2/PROJECT.md` (U-set U1–U18, token-lever map, Phase-B/C table) + `CURRENT_STATE.md` · `meta_harness_3/PROJECT.md` (P1/P2/P3+T1–T3, R1–R11, D1–D9) · `meta_harness_5/PROJECT.md` (10-item backlog verdicts + 038) · `meta_harness_7/PROJECT.md` (11-item program Waves 0–2 + Improvement002 A–F intake + concurrent slice-1 + baselines) · `meta_harness_concurrent/PROJECT.md` (D1–D20, core 039–041/045 + 046/048/049 + 042–044) · `net_enforced_harness/PROJECT.md` (050 Alt-A + deferred Phase-B note).
- Evidence: `sandbox/meta/improvement002/IMPROVEMENT_OPTIONS.md` (A–F) + `AGENTX_CONCURRENT_WORK.md` (slices, bindings, demo) · `.sandbox/session_2026-08-15_feature_027_completion.md` (mh3 evidence) · `.sandbox/meta_harness_5_idea.md` (038 origin) · opencode.db token analysis (mh3 §Token evidence: 1009 sessions, 68.8MB tool bytes).
- SSOT: `.meta/META_HARNESS.omt` (gates/budgets/tools) · live net rev 57 · WORK.md Tasks (net render).
- Approvals this session: close-6-only + 5-tracks + drop-deferred (question-gate 2026-09-12).
