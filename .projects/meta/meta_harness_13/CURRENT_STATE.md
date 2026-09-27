# CURRENT_STATE: meta_harness_13

> Session-by-session log + resume point. Companion to `PROJECT.md` (canonical).
> Newest entry on top. One `## <date>` block per session.

---

## 2026-09-27 (iter 14 — project CLOSED complete; live pilot un-executed per D7)

### Done

- User `close the project properly` → `project.py close meta_harness_13` (active→complete) + `sync` + `workc.py build`: manifest row, WORK.md row, WORK.compiled (16 complete / 6 active) all show complete.
- Ledger hygiene: tombstoned stale phase declarations for shipped features (132 Design×2/Done, 133 Done, 134 Design) — substance already verified via omt_complete + test reports.
- Cleared the pre-existing `work_md` budget drift (this project's 131–134 rows consumed the headroom, 9758→9760 B > 9728): deliberate grow **9728→10240** in the same `.omt` edit + `WORK_BUDGET` pin sync (feature_110 same-round precedent) + `harnessc build` → **check 276/0, work_md 9760/10240 OK**.
- All 5 pre-existing baseline failures cleared (budget_diet, harnessc×2, work_md pin, run_metering): pins battery **59 passed**.
- PROJECT.md updated honestly: status checklist closed out, **D7 closure decision** recorded — AC6 live pilot NOT executed (`executed:false` everywhere); live run = future explicit `p` + 12 claims + budgets + isolation; no promotion/token claims citable from the un-run pilot.
- Zero `src/` edits in the closure round; one `.omt` budget line + one pin line + generated-file rebuilds.

### Next

- Nothing active — project complete. Any live 12-trial pilot is a NEW decision (D7 path: explicit `p`, claims held, budgets, per-trial isolation; launcher core exists at fake fidelity).
- Resume: PROJECT.md header → D7 → feature_134 test_report.md.

---

## 2026-09-27 (auto — feature_134.real_trial_launcher Done)

- shipped: major_feature · test report @ 6.testing/features/feature_134.real_trial_launcher/test_report.md
- fake core: launcher.py NEW (plan 12 → dispatch_fake → enforce_timeout 300s strict-once → collect_fake → run_fake via 132 gate); 4 slice + 2 bridge tests green (72 passed battery); full-minus-inspect 2012 passed, 5 pre-existing baseline failures (zero NEW), work_md 9758>9728 B pre-existing drift flagged (134 allocation, iter 11).
- no launches, no tokens, fakes only; `executed:false` everywhere; service.py/.ts/.omt untouched.
- logged by omt_complete; expand by hand if resume needs more.

---

## 2026-09-27 (iter 13 — 134 fake-executor core SHIPPED; live run pending explicit `p`)

### Done

- `continue` → Programming resumed: stranded RED `test_fake_plans_12_in_order` closed GREEN via `scripts/session_inspect/launcher.py` (stdlib-only) → REFACTOR → SYNC → TDD done, Programming→Testing→Done verified.
- Fake core per `operation_spec_001`: `plan_trials` (12 in-order via `manifest.expand_matrix`, seed 0), `dispatch_fake` (injected executor, once, `/tmp` stub isolation, `trial_incomplete` on exception), `enforce_timeout` (300 s, strict-once → `timeout_failed`, attempt 1), `collect_fake` (usable = independent_n stub), `run_fake` (gate_run budgets/isolation/claims/explicit_p; refusal → `no_safe_launch`; allow → `{allowed, n_trials:12, executed:False, fake_n:12}`).
- Bridge `test_bridge_134.py` (2, unique basename) + impl_notes + test_report written; slice battery 72 passed, 2 skipped.
- Full minus inspect 2012 passed / 5 failed — all 5 pre-existing at baseline (budget_diet, harnessc×2, work_md pin, run_metering); `work_md` 9758 B > 9728 B is pre-existing drift from the 134 allocation (iter 11) — remediation = deliberate `.omt` budget edit + build + re-pins (separate task, flagged in report).
- Harness-surface untouched this slice (no `.ts`/`.omt` edits, no pin churn); `feature_129/130/131/132/133` untouched.

### Next

- Live `executed:true` slice: real executor path + per-trial worktree + 12 held claims + budgets + explicit `p` — needs user go + design for entrypoint/creds questions (iter 11 open questions).
- Repo drift triage (optional, user call): grow `work_md` budget deliberately or diet-bot it.
- Resume: this entry → launcher.py → test_report.md (134).

---


## 2026-09-27 (iter 12 — 134 decisions locked; ready for Programming)

### Done

- User answered §4: existing dispatch only; small pilot (5min/trial, conc 1, overhead separate); strict once; `/tmp` per-run atomic; runner holds 12 claims.
- `design_001` flipped DRAFT → DECIDED; no builds, no launches.

### Next

- Programming (fake-executor TDD: manifest→dispatch→timeout→collect) on `go`; live run only on later explicit `p`.
- Resume: this entry → 134 design_001.

---

## 2026-09-27 (iter 11 — 134 launcher scoped; no builds, no launches)

### Done

- `do it` clarified: real execution not built (gate `allowed` + `executed:false` only). User chose scope launcher build.
- Allocated `feature_134.real_trial_launcher` (major) + Design declared (artifact `design_001_real_trial_launcher.md` DRAFT).
- Open questions logged: execution entrypoint/creds, 12-trial caps, timeout/retry, snapshot dest, `omt_net` claims holder.

### Next

- Answer §4 questions → finalize Design → Programming (fake-executor TDD) → guarded live run on explicit `p`.
- Resume: this entry → 134 design_001 → PLAN.md.

---

## 2026-09-27 (auto — feature_133.dispatcher_gate_wiring Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_133.dispatcher_gate_wiring/test_report.md
- wiring: service run → run_gate, 62 slice + 9 gate, 2015 full-minus-inspect, 276/0, S5/S6 preserved, no launches.
- bridge basename clash fixed (132/133 unique names).
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-27 (iter 10 — 133 wiring programmed; Testing pending)

### Done

- `next` → feature_133 allocated (minor) + Programming + TDD closed: 3 gate tests → RED → GREEN (`service.py` wires `run_gate`) → SYNC (validate-exit ok; `done` hygiene times out on full suite, slice green).
- Wiring: `run` reads gate fields from manifest body (OP_ARGS/`.ts` untouched), `allowed` → ok True 12 trials `executed False`; refusals → `no_safe_launch` + detail (S5/S6 preserved, 62 passed slice).
- `omt_complete` Programming verified (impl_notes + bridge 2 passed).

### Next

- Testing (report + regression + check) on your `test`; real launches still out of scope.
- Resume: this entry → service.py run block → test_dispatcher_gate.py.

---

## 2026-09-27 (auto — feature_132.pilot_launch_path Done)

- shipped: major_feature · test report @ 6.testing/features/feature_132.pilot_launch_path/test_report.md
- run_gate slice: 59 passed slice, 7 gate+bridge, 2013 full-minus-inspect, harnessc 276/0, no launches/tokens.
- `service.py run` still `no_safe_launch`; dispatcher wiring deferred.
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-27 (iter 9 — 132 Programming closed; Testing pending, no launches)

### Done

- `go` → Programming + TDD closed for feature_132: testlist 5 → RED → GREEN (`run_gate.py`) → REFACTOR → SYNC → DONE (batch-N grouped, S3/S4 precedent).
- `run_gate.py` NEW (stdlib-only): manifest/isolation/budgets/claims+explicit_p gates; refusals `manifest_invalid|isolation_unavailable|budget_missing|no_safe_launch`; allow → `{allowed:True, n_trials:12, executed:False}`.
- Tests: slice `59 passed, 2 skipped` (54+5 new); bridge `2 passed` (7 with gate file); `omt_complete` Programming verified.
- Artifacts: `operation_spec_001_run_gate.md`, `design_001`, `impl_notes.md`, bridge tests. `service.py run` still `no_safe_launch` (not wired this slice).

### Next

- Testing (test report + full regression + `harnessc check`) then Done, on your call. Real 12-trial launches still blocked (need dispatcher wiring + isolation/budgets + `p` run invocation).
- Resume: this entry → design_004 → run_gate.py → test_run_gate.py.

### Notes

- No launches, no tokens; synthetic fixtures only; `feature_129/130/131` untouched.

---

## 2026-09-27 (iter 8 — reopened for pilot launch-path build; no launches)

### Done

- User `p` → approved design build (not execution): `project.py reopen meta_harness_13` (complete→active), `new_feature.py pilot launch path` → feature_132 linked.
- `omt_phase` Design declared for feature_132 (artifact `design_001_pilot_launch_path.md` promotes 131/design_004 §§1–8).
- `run` still `no_safe_launch` (verified this session); `dry_run` 12 trials `executed:false` unchanged.

### Next

- Review design_001/004, then Programming + TDD (run + isolation/bounds + collect/validate) on explicit go-ahead. No launches in Design.
- Resume: this entry → design_004 → feature_132 PLAN.md.

### Notes

- No src edits, no tokens, no launches this round; docs + lifecycle only.

---

## 2026-09-27 (iter 7 — Done verified; ready to close)

### Done

- `omt_complete` Done verified for feature_131 (ship already logged); Analysis verified for meta_harness_13.
- Re-verified this session: slice `tests/scripts/session_inspect/ -q` → 54 passed, 2 skipped; full minus inspect → 2011 passed, 2 deselected, no failures.
- `harnessc check` → 276 records, 0 errors (budgets green).
- S6 full Addendum reviewed (AC1–AC12, live 242k corpus, 12-trial dry_run, run gated no_safe_launch).

### In progress / Blocked

- Project close/sync per lifecycle (`project.py close meta_harness_13` + `sync`) — next.
- 12-trial pilot execution still needs explicit `p` approval.

### Next

- `project.py close meta_harness_13` then `sync`, verify manifest/WORK row → complete.
- Resume entry point: this entry → PROJECT.md AC1–AC12 → test_report Addendum S6 full.

### Notes / context

- No code changes this session; docs log only; fixtures synthetic; live DB read-only mode=ro.
- Harness-surface: no `.ts`/`.omt` edits this round.

---

## 2026-09-27 (iter 6 — S6 full closed; Testing verification pending)

### Done

- S6 items 3–6 TDD closed: testlist 4 → RED/GREEN/REFACTOR per node → DONE, validate-exit ok.
- `service.py` dispatcher now delegates profile/inspect/trace/query/export/experiment(dry_run/plan) to real S1–S4 core (selection_json respected, limits/cursors named, run gated).
- Slice suite: `tests/scripts/session_inspect/ -q` → 54 passed, 2 skipped; `MH13_LIVE_DB=1` → 56 passed in 113s (242k corpus ≥100k asserted).
- Full regression minus inspect: 2011 passed, 2 deselected, no failures (matches iter5 baseline).
- Test report Addendum S6 full written; `omt_complete` Programming verified; Testing declared.
- Pilot `dry_run` re-verified: context_strategy/run_001 2×2×3=12 trials, `executed: False`, invalid → `manifest_invalid`, `run` → `no_safe_launch`.

### In progress / Blocked

- Testing→Done verification (`omt_complete`) NOT yet run — needs this CURRENT_STATE entry + Addendum S6 review.
- 12-trial pilot execution still needs explicit `p` approval.

### Next

- `omt_complete` Testing→Done, then project close/sync per lifecycle.
- Resume entry point: this entry → design_003 §6 → PROJECT.md AC1–AC12.

### Notes / context

- No `feature_129/130` edits; fixtures synthetic; live DB read-only `mode=ro`; transcript bodies never dumped.
- Harness-surface: no `.ts`/`.omt` edits this round (service-only, NON-harness); B1/B2 pin still green.

---

## 2026-09-27 (iter 5 — S6 B1/B2 hardening closed; live AC battery pending)

### Done

- S6 B1 stdlib shadow closed: renamed `scripts/session_inspect/inspect.py` → `detail.py` (op string `inspect` unchanged, no file on disk), `__init__` shim keeps legacy `from session_inspect import inspect` green, `service.py` bootstrap supports both script + `python -m` launches, plugin `.ts` switched to `uv run python -m session_inspect.service` with cwd `scripts/` + timeout 30s→120s (B1+B2 in ONE harness-surface edit).
- S6 B2 bounded-directory closed: `service.py` `DIRECTORY_CAP=20`, directory-only without time/ids over cap returns `query_limit_exceeded` + cursor (COUNT pre-check avoids 100s scan), `session_ids` drill-down bypasses cap, time-bounded bypasses cap.
- TDD S6: testlist 6 → RED/B1 (script launch + no-shadow) → GREEN (bootstrap) → REFACTOR → RED/B2 (over-budget + drill-down) → GREEN → REFACTOR, validate-exit ok for cycles, no stranded REDs for B1/B2.
- Slice suite: `tests/scripts/session_inspect/ -q` → 50 passed, 2 skipped (live gated); pin `test_omt_session_plugin_args.py` → 2 passed; `MH13_LIVE_DB=1` → 52 passed in 103s (live scan <120s, would timeout at 30s before B2).
- Pilot `dry_run` re-verified: context_strategy/run_001 2×2×3=12 trials, `executed: False`, no launches/tokens.
- Full regression (minus inspect): `uv run pytest -q --ignore=tests/scripts/session_inspect` → 2011 passed, 2 deselected, no failures.

### In progress / Blocked

- S6 remaining (AC1–AC5 live chain via `omt_session`, AC3 bench latency/memory split, AC9 export/replay bundle, AC11 2KiB + overhead, negative battery, B1/B2 pin re-run) NOT started — needs next REDs (`s6.ac1_ac5_live` → `s6.ac3_bench` → `s6.ac9_replay` → `s6.pilot_dry_run`) + test_report Addendum S6 + `omt_complete` Testing→Done.
- 12-trial pilot execution still needs explicit `p` approval; `run` stays `no_safe_launch`.

### Next

- Declare RED for `s6.ac1_ac5_live` (env-gated live chain), then bench/replay/pilot, then Addendum S6 + regression + `omt_complete`.
- Resume entry point: this entry → design_003 §6 (items 3–6) → PROJECT.md AC1–AC12.

### Notes / context

- No `feature_129/130` edits; fixtures synthetic; live DB read-only `mode=ro`; transcript bodies never dumped.
- Harness-surface: ONE `.ts` edit (launch + timeout) this round, no `.omt` change, pin green; second `.ts` edit needs fresh e2e receipt.

---

## 2026-09-27 (iter 4 — S5 verified; S6 Design drafted, pilot dry_run only)

### Done

- `omt_complete` Testing verified for feature_131 (S5 Tier-2 closed).
- Declared Design for S6 acceptance (AC1–AC12, live A2, 12-trial pilot, overhead).
- Wrote `design_003_s6_acceptance.md` (live baseline, AC verification plan, B1/B2 fixes, pilot plan-only, S6 TDD list).
- Live census read-only: 1857 sessions / 47k messages / 195k parts (agentx 1724/42k/177k, AC3 ok); AC1 shapes `ses_0a85d1b6` / `ses_0eaa78cd4` / 85 child sessions; `MH13_LIVE_DB=1` 50 passed.
- Pilot `dry_run`: context_strategy/run_001 2×2×3 = 12 trials, `executed: False`, no launches/tokens.
- Found AC10 blockers (not fixed): B1 stdlib `inspect` shadow on script launch (argparse crash reproduced) + B2 plugin 30s timeout vs ~100s live scan.

### In progress / Blocked

- S6 implementation (B1 rename+`-m` launch, B2 bounded-directory rule, live AC battery, export/replay, overhead) NOT started — needs Programming declaration + TDD per design_003 §6.
- 12-trial pilot execution needs explicit `p` approval (isolation/budgets); `run` stays `no_safe_launch`.

### Next

- Declare Programming for S6, TDD `s6.b1_no_shadow` → `s6.b2_bounded` → live AC battery → `dry_run` negative set, then test_report Addendum S6 + regression + `omt_complete` Testing→Done.
- Resume entry point: this entry → design_003 → PROJECT.md §acceptance AC1–AC12.

### Notes / context

- No src/plugin/`.omt` edits in iter 4; `feature_129/130` untouched; fixtures synthetic; live DB read-only `mode=ro`; transcript bodies never dumped.

---

## 2026-09-27 (iter 3 — S5 Tier-2 closed; S6 acceptance pending)

### Done

- S5 (Tier-2 integration, design_002) TDD closed: testlist 6 → red (1 node, batch-N grouped) → green (service.py dispatcher + main CLI) → refactor → sync → done, validate-exit ok, no stranded REDs.
- Slice suite: `tests/scripts/session_inspect/ -q` → 48 passed, 2 skipped (live gated); pin `tests/scripts/omt/test_omt_session_plugin_args.py` → 2 passed.
- Registry: `.opencode/plugins/omt_session.ts` NEW (9-op enum, whitelist, run pre-refused) + `@tool omt_session` row; deliberate caps tool_args 2592→2848 / nav_index 66560→67072 / ir_json 21504→22016 (2 receipt-guarded rounds); 3 pins re-pinned (059/058/diet).
- Artifacts: `harnessc build` OK (276 records → 5 projections), `harnessc check` 0 errors, e2e receipt fresh, full regression `uv run pytest -q` → 2059 passed, 2 skipped, 2 deselected.
- Docs: `design_002_tier2_integration.md` + `impl_notes.md` S5 line + `test_report.md` Addendum S5.

### In progress / Blocked

- Feature in Programming (S5 done, TDD green) — NOT Done. S6 acceptance (AC1–AC12, 12-trial pilot, live-DB A2 `MH13_LIVE_DB=1`, overhead disclosure) remains.
- `omt_complete` Programming→Testing for S5 verification is the next gate.

### Next

- `omt_complete` S5 verification (this test report addendum + regression), then Design/Programming for S6 per PROJECT.md §acceptance.
- Resume entry point: this entry → PROJECT.md §Implementation plan M5–M6 → design_002 §8.

### Notes / context

- `feature_129/130` scripts untouched; fixtures synthetic only; adapter read-only `mode=ro`; plugin `run` refuses before dispatch.
- TDD batch-N warning noted (6 tests/file, related behaviors grouped — S3/S4 precedent).

---

## 2026-09-27 (auto — feature_131.opencode_session_inspection_and_experiments Done)

- shipped: major_feature · test report @ 6.testing/features/feature_131.opencode_session_inspection_and_experiments/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-27 (iter 2 — S2 slice closed; S3–S6 pending)

### Done

- S2 (query/inspect/trace/cli) TDD closed: testlist 5 → red/green per node → sync closed orphaned `test_inspect_trace.py` RED (rename to `test_slice2_inspect_trace.py`) via same-node alias → refactor → done, validate-exit ok, no stranded REDs.
- Slice suite: `tests/scripts/session_inspect/ -q` → 32 passed, 2 skipped (live gated); bridge `tests/features/feature_131.../test_slice1_bridge.py` → 3 passed.
- Artifacts: `omt_complete` Programming verified (S2); full TDD `done` green (suite+feature+refactor+naming ok).
- Legacy alias `tests/scripts/session_inspect/test_inspect_trace.py` kept as thin same-node close-out; canonical tests are `test_slice2_*.py`.

### In progress / Blocked

- Feature in Programming (S2 verified) — NOT Done. S3 (profile/compare/exporter) → S4 (manifest/collect/evaluate run-gated) → S5 Tier-2 + 39-byte budget → S6 acceptance remain.
- Live-DB reasoning-bearing reconciliation (A2) still needs `MH13_LIVE_DB=1` verification in S3.

### Next

- Declare Testing for S2 verification (test report S2 addendum + regression), then Programming for S3 per design_001 §Slice plan S3.
- Resume entry point: this entry → PROJECT.md §Implementation plan M2–M3 → design_001 §Slice plan S3.

### Notes / context

- `feature_129/130` scripts untouched; fixtures synthetic only; adapter read-only `mode=ro`.
- TDD same-node lint (GOTCHA_TDD_NODE): rename-induced orphan REDs must be closed with same-path GREEN (sync), never by deleting the path.

---

## 2026-09-27 (iter 1 — S1 slice closed; S2–S6 pending)

### Done

- S1 (schema/adapter/normalize/labels/hierarchy/usage/collect) TDD closed: testlist 18 → 12 cycles → refactor → done, validate-exit ok, no stranded REDs.
- Slice suite: `tests/scripts/session_inspect/ -q` → 25 passed, 2 skipped (live gated); bridge `tests/features/feature_131.../test_slice1_bridge.py` → 3 passed (Programming→Testing gate).
- Artifacts: `5.implementation/.../impl_notes.md` + `6.testing/.../test_report.md`; `omt_complete` Programming→Testing; full regression `uv run pytest -q` → 2031 passed, 2 skipped, 2 deselected in 95.41s; `harnessc check` 275 records 0 errors.
- Project flipped draft→active (ledger project_link), feature_131 linked.

### In progress / Blocked

- Feature stays in Testing (S1 verified) — NOT Done. S2 (query/inspect/trace/cli) → S3 → S4 → S5 Tier-2 + 39-byte budget → S6 acceptance remain.
- Live-DB reasoning-bearing reconciliation (A2) still needs `MH13_LIVE_DB=1` verification in S2.

### Next

- Declare Programming for S2 (Testing→Programming allowed), add design addendum for query/inspect/trace/cli, TDD testlist → red → green → refactor → done per module.

### Notes / context

- Resume entry point: this entry → PROJECT.md §Implementation plan M2 → design_001 §Slice plan S2.
- `feature_129/130` scripts untouched; fixtures synthetic only; adapter read-only `mode=ro`.

---

## 2026-09-26 (iter 0 — project created; inspection and experiments scoped)

### Done

- Created the project mechanically with `uv run scripts/omt/project.py new "Meta Harness 13 — Real OpenCode Session Analysis (Tier 2)" --slug meta_harness_13`; lifecycle state is draft and the generated manifest/WORK project row exist.
- Filled `PROJECT.md` with the canonical proposal for a powerful real-session inspector and labeled experimental workflow, targeting a registered Tier-2 `omt_session` tool.
- Incorporated both user refinements: deep inspection is essential; labeled messages for running experiments are an equally important core feature.
- Defined session trees, full message/part/tool/reasoning drill-down, typed cross-session queries, traces, usage reconciliation, failure diagnosis, live snapshots, comparison, and reproducible exports.
- Defined the proposed message-label protocol and experiment lifecycle: manifest → dry run → explicitly invoked independent trials → capture/validate → quality-aware comparison/replay. Included runs/cases/variants/repetitions/attempts, nested spans, child bindings, contamination checks, and independent sample accounting.
- Reviewed Harness Reason features 129/130 and closure: reuse their capture contracts and explicit unknowns; preserve the negative general-engine promotion result. Legacy labels remain importable without treating repeated ledger replays as independent trials.
- Inspected current toolbox discovery (`list --tier 2`, `query session`): no real-session inspector is registered. Baseline compiler check: 275 records / 0 errors; `tool_args` headroom is 39 bytes and needs a deliberate integration budget plan.
- Declared the project-creation task as `docs`/Analysis, consulted thoughts for both new files (none), and verified project-document edit preflight is clear.
- Validation: `project.py sync` and `project.py status meta_harness_13` confirm the draft; `harnessc.py check` passes (275 records, 0 errors; existing 39-byte tool-argument headroom warning); both project documents have no unresolved template placeholders and all 9 relative Markdown links resolve; `git diff --check` passes.
- `omt_complete` verified the docs/Analysis artifacts. Repository regression: `env PYTHON_DOTENV_DISABLED=1 LLAMA_CPP_MODELS_CACHE_PATH=/tmp uv run pytest -q` → **2006 passed, 2 deselected, 7 deprecation warnings** in 91.52 seconds. Restored the six generated toolbox files changed by the test run to their clean pre-test state; retained the project documents and mechanically synced manifest/WORK row.

### In progress / Blocked

- Project creation/proposal only. No feature ID allocated, implementation begun, real session content harvested, trial launched, or runtime/tool registry changed.
- Option A (dedicated Tier-2 inspector and labeled experiments) is recommended; implementation approval is pending under the project workflow's step 6.
- Project creation and validation are complete. Runtime implementation remains the next, separately approved project step.

### Next

- Review `PROJECT.md` §Implementation plan for approval. Once approved, use `new_feature.py` to allocate/link `opencode_session_inspection_and_experiments` as a `major_feature`, then begin M1 contract/schema verification with a design document and the required TDD process.

### Notes / context

- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.
- Treat Tier 2 as full harness registration/build/budget/e2e integration, not merely the toolbox tier filter. A read-only query and an experiment run have different enforcement requirements.
- Do not mark the project complete or reopen `harness_reason` as a side effect. The draft's core scope includes both inspection and experiments; neither may be dropped silently.
