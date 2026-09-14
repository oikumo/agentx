# PROJECT: meta_harness_9 — Roadmap Execution (Work Contract + Petri Frontier + Measured Economy)

> Status: **active** · **v0.2 (2026-09-14)** — created by `project.py new --slug meta_harness_9`. Iterate freely (non-gated); spawn features with `new_feature.py "<name>" --type <tt> --project meta_harness_9`; log sessions in CURRENT_STATE.md (newest on top).
> Refined per user pick: **stronger file-anchored critique + S0–S4 only** (S5+ parked with re-entry criteria, not scheduled).

---

## New Session Quick Start

> One line: mh9 executes `sandbox/META_HARNESS_ROADMAP.md` rebased onto post-mh8 reality — S0 rebase → S1 measure → S2 correct → S3 project (read-only) → S4 paired frontier experiment with a keep/merge/drop exit. Nothing past S4 is scheduled.

**Next:** S0 rebase (sign the §2 table at HEAD + pin oracle/versions/budgets). Then S1+S2 as the one allowed pair, S3, then S4.

---

## Summary (one line)

**Prove or kill the roadmap's cheapest high-value bet — read-only Petri guidance over a thin work contract — on a truthful, measured base, without touching live AgentX usage; all executable/authority/analysis work stays parked until S4 says keep.**

---

## 1. Critical review (verified at HEAD, file-anchored)

Verdict: **sound direction, honest limits, not executable as written.** The architecture (request-linked WorkSpec→WorkIR, Legal = control ∧ guards ∧ capability with ALLOW-only, candidate-bound evidence, measure-before-expand with stop rules) is the right bet, and the roadmap's self-limiting lines (§8.5 keep/merge/drop; "defensible profile today = development assistance only") are its best feature. But it is stale against mh8-close, it schedules authority work as if guidance value were proven, and it has no isolation plan. Each claim below was re-checked at HEAD (`06175f0`; `check` 265/0, `build` OK).

### Keep

- **Measurement before expansion + stop rules** (§§8–9, §8.5): 093 first, comparators native/static/current/preflight/frontier/analysis, promotion only on repeatable accepted-task benefit. If preflight≈frontier → merge; if runtime<static → ship the smaller product.
- **Honest qualification** (§§2/6.5/10.1): assistance vs verified-solo vs managed-local; per-property PROVEN/DISPROVEN/UNKNOWN; control-only ≠ runtime (over-approximation boundary stated, not footnoted).
- **One decision boundary + evidence discipline** (§§5–7): WorkSpec/WorkState split; obligations compose; candidate-bound receipts + freeze/revalidate; reserve→execute→commit without holding the lock over work.
- **Migration discipline** (§5.3): read-only projection first, one writer per action, no dual-write reconciliation.

### Blocking findings (confirmed at HEAD — these are mh9's work, not quotes)

- **F09 confirmed — durable ack is best-effort.** `.opencode/lib/omt_shared.ts:154-159`: `appendJsonl` wraps mkdir+append in `try { … } catch { /* best-effort */ }`. Any authoritative write (ledger, thoughts index via `omt_think.ts:100`, phase/complete records) can silently fail while the caller proceeds as if recorded. S2 fixes first: return/report write failure at authority boundaries; keep best-effort only for advisory paths.
- **F02 confirmed — critical errors fail open.** `.opencode/plugins/omt_enforcer.ts:100-103`: the `tool.execute.before` wrapper rethrows only `OmtBlock`; every other internal error warns and **allows the edit through**. Correct for optional advice (nav track, bootstrap), wrong for missing/invalid authority. S2 must separate the two: advice may fail open, authority resolution may not.
- **F05-caller residual — empty verifier output means success.** `.opencode/lib/enforcer/phase_gate.ts:455`: `JSON.parse(tddRes.stdout.toString() || '{"ok":true}')`. Feature 075 added real failing-test/dangling/coverage blocking (lines 456–473), but the **default on empty/missing output is still `ok:true`**. Contrast line 512, where the net-drift check defaults to `'{"ok":false}'` (fail-closed) — that is the pattern to copy. S2 changes the 455 default and adds empty/malformed/nonzero goldens.
- **F03 confirmed shape — one gate stops the chain.** `.opencode/lib/enforcer/gate_driver.ts:219-221`: `g.tests` unconditionally returns `"stop"` after its guard; the chain contract (`:366-367`, dry path `:398`) is `stop → later gates never evaluated`. Passing the tests-canary therefore suppresses unrelated later obligations on the live path. Note the dry/live divergence the roadmap's F10 predicts: `runBeforeGatesDry` **continues** after a block (`:408-410`, so `op:plan` sees all firings) while the live chain **breaks** on `stop` — prediction and enforcement structurally disagree. S2 makes obligations compose; S3 records the parity gap as UNKNOWN rather than papering over it.
- **C6 confirmed — lifecycle ops bypass the net transition relation.** `scripts/omt/net/state.py`: `fire()` (lines 763–768) correctly goes through `st.net.fire_marking`, but `claim_task` (line 896), recovery, lane and integration moves go through `_move_pool_token` (`:819-834`, direct counter `+=1/-=1`, guarded but not a fired transition). `validate_task_bindings` (`:296-300`) treats absent lane places as binding-only occupancy (`tokens = bindings`, never an error). So counts can agree while no transition fired — exactly the roadmap's C6. Consequence: **no Petri execution guarantee may be claimed** until one template's every managed op maps to a checked transition (parked S5, gated on S4-keep + S2-green).
- **C1 residual — clear-before-record crash window.** `state.py:730-742` (`_transact`): on success the pending WAL marker is **cleared (730–734) before the command replay record is written (735–742)**. Feature 084's WAL bracketing is real progress (marker written inside the held lock `:672-675`, reconcile on crash `:660-666`), but a crash between clear and `record_command` still loses idempotent-replay info while the state advance survives. Parked S6a must reorder to record-before-clear (or clear-after-record-ack) with a crash test; S0–S4 must not depend on replay surviving that window.
- **C2/C3/C4/C5 + F07/F10/F11 stand as scoped.** Multi-file `save` vs split `load`, workspace-metadata vs real worktree proof, path/session vs task/generation/owner identity on every write path, caller-supplied lane verdicts, guard-free model vs guarded runtime, byte-counts vs tokens — none are closed by 079–085's (genuine) lane/lock/worktree progress. The roadmap is right to keep the solo/managed profiles unqualified; mh9's error would be building guidance that assumes them closed.

### Roadmap-prose critiques (no new source needed)

- **C1-doc — stale baseline.** Anchored to `81b3aa1` (09-13). Since then: 093 SHIPPED (17/17 goldens, 6/6 first-numbers TP=13/FP=0/missed=0, suite 2231), 094 SHIPPED (10/10, suite 2241), 095/096 0-win reviews, repair flag CLOSED, mh8 CLOSED 31/31. "093 paused, T3-6 pending" (§§2.1/9.1) is obsolete → S0 re-signs the table before any build.
- **C2-doc — shipped overlap.** 070–075, 092/093/094 are complete under mh8 (manifest-verified) but scheduled as new work in §9.1 → every mh9 scaffold cites its §2 row; re-implementation without new evidence is refused at plan time.
- **C4-doc — value assumed, not gated.** §6.7+§9 pipeline closure/authority/analysis while §8.5 demands frontier-beats-preflight first → S4 is a decision gate, S5+ parked.
- **C5-doc — instrumentation gap.** No host per-call token usage (093's `io_bytes`/`tokens_est`/delivered-bytes are correctly labeled proxies); oracle unqualified ("Done cannot judge its own success"); 6-task/2–3-repeat smoke measures variability, not diversity; 20%/30% targets (§1.2) ungrounded → S1 qualifies the oracle and freezes corpus/rules before any economy sentence.
- **C6-doc — scope vs capacity.** Generations-vs-SQLite, second adapter, SDK, remote/distributed, full WorkIR + shared evaluator + template analysis vs solo maintainer + near-cap budgets (live: tool_args 2455/2464 = 9B, schemas 1840/1856 = 16B, agents_md 2918/2944 = 26B headroom; nav 64990/65536 = 546B free; gates 10/12 net-zero). Every new tool/gate/nav record needs diet+retirement math in the same edit → S0 sheets it; S5+ parks it.

---

## 2. Reconciliation (roadmap §9.1 → mh8-close reality; S0 signs this at HEAD)

Live pins (2026-09-14): `check` 265/0 + `build` OK; budgets as above; suites 2231 (093) → 2241 (094); pool 0/0/7, resources 5/5 free; mh8 CLOSED 31/31 read-only.

| Roadmap slice | Assumed | Reality | mh9 |
|---|---|---|---|
| 1 Task-cost 093 | paused | **SHIPPED** 17/17 + first-numbers v1 | S1 extends (oracle/proxies/corpus/waste rank). No redo. |
| 2 Truthful F05/F09→F02/F03 | open | 074/075 shipped; **F09/F02/F05-caller/F03 still confirmed** (files above) | S2 residual only, ordered F09→F05-caller→F02→F03. |
| 3 Thin contract | proposed | 072 + 073 + 092 shipped as parts; no single WorkIR | S3 read-only projection; duplicate store forbidden. |
| 4 Read-only frontier | proposed | **not done** — highest decision value | S4 paired experiment; keep/merge/drop. Gates everything parked. |
| 5–7 Authority/analysis/install | proposed | lanes/locks shipped; **C1/C6 + C2–C5 + qual gaps open**; 094 advisory shipped; minimal install not done | **PARKED** (§4) with re-entry criteria. |

---

## Purpose

### What this project is

- The **sole execution home** for the roadmap after mh8-close (mh8 read-only; nothing lands there).
- An **S0–S4 program**: rebase → measure → correct → project → paired experiment. Each slice revertible, read-only before authoritative, sidecar before live.
- The **non-interference guarantor**: live harness pinned/green throughout; experiments pay their own budget/maintenance cost.

### What this project is **not**

- NOT scheduled beyond S4. S5+ (executable closure, storage/workspace/verifier, analysis, solo qual, minimal install, managed/M4, second adapter, SDK, remote/distributed, timed/colored nets, self-modification) are parked with re-entry criteria — not dates, not backlog.
- NOT re-shipping mh8 (070–075/079–096 stand) or weakening locks (think/protect, two-hats + genuine-RED + auto-revert, net-zero 10/12, KNOWN empty, Tier-3 excludes net, stage discipline).
- NOT a date plan: each slice estimated only after reproducer + support boundary + oracle + resource budget are concrete.

---

## 3. Plan — S0–S4 (one bounded queue; max 1 active, 2 only as 1 correctness + 1 measurement on disjoint files)

### S0 — Rebase + isolation pins (hygiene; no src/authority change)

- Goal: make §2 signable at HEAD.
- Steps: (1) re-verify each §1 finding at HEAD, record file:line + open/mitigated/closed; (2) budget/retirement sheet (headroom above + longest-contributor diet targets + which record retires for any addition); (3) pin oracle/toolchain/policy/compiler/net-bundle versions; (4) freeze bench corpus + retry/order/randomization rules; (5) declare sidecar-only experiment surface (`bench/` + `kb_pilot/` pattern; fresh worktrees for runs).
- Exit: signed §2 table + pins + sheet; `check`/`build`/suite re-baselined green. Size: `minor_feature`.

### S1 — Benchmark follow-up (evaluation; extend 093, no policy change)

- Goal: first honest cost picture.
- Non-goals: no economy claim beyond labeled proxies; no corpus expansion past 6 tasks + 2–3 repeats (smoke) without a written expansion rule + budget.
- Steps: qualify oracle with 4 seeded classes (valid accept, omitted behavior, stale evidence/missing check, false-success rejection); label `tokens_est`/`io_bytes`/delivered-bytes/byte-digest (092: 432B vs ~58KB reread) as proxies in every artifact; freeze 6-task corpus + attempt boundaries + paired order + cold/warm separation; publish waste ranking + per-gate removal deltas.
- Exit: repeatable native/static/current traces with honest usage fields; waste ranking; expansion rule + resource budget. Size: `minor_feature`. Depends: S0.

### S2 — Truthful-boundary residual (runtime; ordered F09 → F05-caller → F02 → F03)

- Goal: invalid results cannot claim success; critical unknowns refuse; obligations compose — on real supported edits, with positive controls.
- Steps (smallest diff each, copy the line-512 fail-closed pattern): F09 — authority writes report failure (keep best-effort for advisory only) + goldens for failed-write refusal; F05-caller — change the `:455` empty-default to fail-closed + empty/malformed/nonzero goldens (Python verifier behavior unchanged, caller contract fixed); F02 — split advice (may fail open: nav/kb/bootstrap tracks) from authority resolution (must refuse on unknown/error) in the `:100-103` handler; F03 — compose obligations on the live path (no `stop` suppression of unrelated gates; dry-path continue-all behavior becomes the live contract or the divergence is documented as UNKNOWN in S3).
- Exit: allow/deny matrix on real edits (protected, harness-surface, tests-canary, src/phase) incl. all four seeded invalid classes rejected + valid controls accepted. Host-qualification limits documented. Size: `minor_feature` ×1–2 (split only if file sets disjoint). Depends: S0. May pair with S1.

### S3 — Thin work contract, read-only (projection over 072/073/092)

- Goal: one bounded task view with no new authority.
- Shape: `request + acceptance refs / task-candidate-scope / completed vs unresolved obligations / next action + reason + required evidence / stale-or-unknown facts / detail refs`, ≤2KB default with required-continuation (never mid-sentence cuts). Missing/inconsistent fields labeled; unknown stays unknown (incl. the F10 dry/live and proxy gaps from S1/S2).
- Steps: reuse 072 typed evaluator + 073 prep + 092 digest as the substrate; write the Q/A/candidate-identity/normalized-action/decision-result schema as a projection (no store, no writer migration yet — designate the future one-writer per action in a migration log instead).
- Exit: one real task (routine fix + one interrupted/resumed) orients and resumes from the projection alone; dry/live parity note shipped. Size: `minor_feature`. Depends: S0 (+S1 proxies, +S2 parity inputs).

### S4 — Read-only frontier experiment (the decision gate)

- Goal: does joint Petri guidance beat consolidated preflight given identical facts and presentation budget?
- Frozen profile: enforcement untouched; frontier is advisory (never grants/authorizes); candidate-action domain + revision + omitted-count/continuation contract honored; stale revision/generation cannot commit (recheck at dispatch even though S4 never dispatches).
- Arms: (a) consolidated preflight with explicit task/dependency/resource facts; (b) Petri frontier on the same facts + budget; (c) frontier + bounded analysis (cost included). Two task classes: routine fix + interrupted/resumed (paired order, frozen criteria/model/policy pins). Seeded defects used only for detection checks; economic return needs naturally occurring avoided failures too.
- Exit: paired results (first-useful-action, avoided attempts, recovery accuracy, acceptance, all-agent tokens + analysis/query cost) + **keep / merge / drop verdict**: keep → S5 re-entry proposal; merge → fold remedies into preflight, keep Petri as analysis-only; drop → retire frontier, keep the smaller compiler/resume/evidence product. C6/authority explicitly not claimed. Size: `minor_feature` (+ short design note for the frontier schema). Depends: S1 + S3 (+S2 parity note).

---

## 4. Parked (not scheduled; re-entry needs all listed evidence)

- **S5 executable closure (C6):** needs S4-keep + S2-green + one-template transition map with differential conformance (every managed op = checked transition; projection(B)=M; invariants across pass/fail/cancel/recovery; identity-sensitive resume). Without it, the net stays a partial control abstraction with omitted behavior named.
- **S6a storage (C1/C2/F08/F09):** needs record-before-clear reorder + crash-injection suite + stated crash vs power-loss guarantees; generations-vs-SQLite comparison on that suite, not on aesthetics.
- **S6b workspace/identity (C3/C4), S6c verifier/evidence (C5/F05/F07):** need per-write-path identity checks + real-checkout receipts + enrolled-verifier + freeze/revalidate + combined-candidate recheck, each on its fault matrix.
- **S7a analysis + solo qual, S7b minimal install + knowledge value, M4 managed:** need M0 (S1+S2) + M1 (S3+S4-keep) + relevant S5/S6 closures + install/recovery evidence + cost report surviving setup/support. Second adapter/SDK/remote/distributed/timed/colored/self-modification: real user need + measured local limitation first.

Milestones: **M0** (S1+S2: truth + cost) → **M1** (S3+S4: guide one real task + verdict). M2/M3 parked with the slices above.

---

## 5. Non-interference contract (violation reverts the slice, never the harness)

1. **Surfaces:** default `.projects/meta/meta_harness_9/`, `.sandbox/`, declared sidecars. Live surfaces (`.meta/*.omt`, `.opencode/**`, `scripts/omt/net/**`, `tests/`) change only inside a declared slice with approval, via stage (snapshot → allow → single e2e → clear) + `check`/`build` + suite green before AND after.
2. **Read-only first:** projections/advisories/digests never grant/authorize/mutate policy. No new gates/tools/budgets without net-zero retirement + diet math in the same edit (10/12 holds; Tier-3 excludes net).
3. **One queue:** §3 order; S1+S2 may pair (disjoint files); S3, S4 strictly serial. Every slice independently shippable and revertible.
4. **Live freeze:** mh8-close behavior is the floor. Red `check`/`build`/e2e/suite or un-dieted budget regression → revert before further work. Runs happen in fresh worktrees/sidecar bundles, never the live checkout.
5. **Authority quarantine (S0–S4):** nothing authorizes effects, certifies lifecycle movement, or claims verified/managed execution. Stale/duplicated/ambiguous cases refuse + preserve + diagnose.
6. **Telemetry on disk; replies brief.** Roadmap out of startup context (section retrieval + stable refs).
7. **Payback gate:** each slice states expected benefit, minimum meaningful effect, expansion rule, resource budget up front. Stop when realistic use cannot repay build + eval + maintenance.

---

## Scope & success criteria

**Scope:** S0–S4. Each ships as its own feature (default `minor_feature` decl-only; S4 gets a short design note for the frontier schema only).

**Success:**

1. S0 signs §2 at HEAD; S1 publishes the honest cost picture (pinned oracle + labeled proxies + waste ranking); S2 closes F09/F05-caller/F02/F03 residual on the allow/deny matrix; S3 resumes a real task from the projection; S4 ends in a written keep/merge/drop verdict. No silent drops.
2. Live harness green throughout (`check` 0 + `build` OK + e2e + suite + KNOWN empty; budgets never regress without diet; net-zero holds).
3. Docs section-retrievable: snapshot + queue here; narrative in CURRENT_STATE.md + history.

**Out of scope:** §4 parked items; mh8 re-implementation; gate removals; `src/agentx/` product work; goal synthesis; any Git/publication allowance (each policy change ships separately under current authority).

---

## Status

- [x] v0.1 (2026-09-14): created + full-roadmap review + S0–S7b plan.
- [x] v0.2 (2026-09-14): refined per user pick — file-anchored critique (F09 `:154-159`, F02 `:100-103`, F05-caller `:455` vs `:512`, F03 `:219-221/:366-398`, C6 `:296-300/:819-834/896` vs `:763-768`, C1 `:730-742` vs `:672-675`) + scope cut to S0–S4 with §4 parked + re-entry criteria.
- [x] S0 rebase (signed §2 at HEAD `f1be918` + pins + budget sheet — `feature_097` `analysis_001_s0_rebase.md`; `check` 265/0 + `build` OK; net rev 57 drained_complete).
- [x] S1 benchmark follow-up (fixture re-baseline green at HEAD + g.phase/g.tests removal deltas + proxies labeled — `feature_098` Done; real 6-task re-run + 8-gate matrix deferred to S1-full).
- [x] S2 truthful-boundary residual (F09→F05-caller→F02→F03, 4 files one round, pins 32/32 + e2e 1/1 + bench unchanged — `feature_099` Done).
- [x] S3 thin work contract (read-only projection over 072/073/092 + 055/062, ≤2KB cap + continuation, 2-task demo orients from projection alone + parity note — `feature_100` Done; sidecar `.sandbox/work_contract/`, suite 2241/2241).

---

## Decisions log (locked — do not re-litigate without new evidence)

- **D1 — mh9 is the sole roadmap-execution home (2026-09-14):** mh8 CLOSED 31/31 read-only; roadmap work lands here. Forced closes reserved for tombstones/short-slug gaps.
- **D2 — rebase before build:** baseline `81b3aa1`/093-paused/T3-6-pending stale; no scaffold before §2 signed at HEAD.
- **D3 — overlap-check is a scaffold gate:** §2 row + mh8 verdict cited per feature; re-implementation refused at plan time.
- **D4 — S4 gates everything parked:** executable/authority/analysis/install need the keep-signal AND S2-green AND payback. A frontier reproducing preflight text earns no runtime (§6.6).
- **D5 — inherited locks stand:** net solo-only, Tier-3 excludes net, KNOWN empty, gates net-zero, clean-close-over-force, stage discipline + `uv` only + `src/` needs `omt_phase` (this doc non-gated).
- **D6 — non-interference is mechanical (§5).** Slice violation → slice reverts.
- **D7 — refine to S0–S4 + file-anchored critique (2026-09-14, user-picked):** S5+ parked with re-entry criteria; critique must cite HEAD file:line and separate confirmed-residual from mitigated/closed.

---

## References

- Roadmap: `sandbox/META_HARNESS_ROADMAP.md` (665 lines, assessment 2026-09-13, baseline `81b3aa1`).
- Prior home (read-only): `.projects/meta/meta_harness_8/PROJECT.md` + `CURRENT_STATE.md` (close 2026-09-14; first-numbers v1 6/6 TP=13/FP=0/missed=0; suite 2231→2241).
- Head-verified files: `.opencode/lib/omt_shared.ts:154-159` (F09) · `.opencode/plugins/omt_enforcer.ts:100-103` (F02) · `.opencode/lib/enforcer/phase_gate.ts:455` vs `:512` (F05-caller) · `.opencode/lib/enforcer/gate_driver.ts:219-221, :366-398, :408-410` (F03 + dry/live divergence) · `scripts/omt/net/state.py:228-314, :650-743, :763-768, :819-899` (C6/C1 + WAL).
- Live pins: `check` 265/0 + `build` OK (tool_args 2455/2464, schemas 1840/1856, agents_md 2918/2944, nav 64990/65536, IR 20113/20480, gates 10/12).
- SSOT: `.meta/META_HARNESS.omt` · net rev 57 · WORK.md Tasks.
