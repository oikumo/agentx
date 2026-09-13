# analysis_001 — task-cost benchmark design (T3-4, first measurement)

> Source: Improvement002 A (mh7 intake, mapped A→T3-4 by mh8 D7). Acceptance (mh8 T3-4 row):
> repeatable script + first numbers, no policy change; target (not promise) −50% harness calls /
> −20% tokens small-task, all seeded violations caught.

## What is being measured

Byte budgets (nav_index, tool_args/schemas) are maintenance checks, not task-cost proof. This
benchmark measures **what the harness costs a correctly-completing agent per task type**, and what
each gate buys (removal experiment). It does NOT change any policy: production code (`.opencode/`,
`.meta/META_HARNESS.omt`, `opencode.jsonc`) is untouched.

## Architecture (3 layers)

1. **Driver (Python, `scripts/omt/bench/`)** — sandbox setup, task registry, spec emission,
   metrics accounting, removal-experiment orchestration, report rendering, CLI.
2. **Sandbox** — `--mode real`: pinned-rev `git worktree add --detach` (fresh gitignored ledger =
   clean session start; committed `harness.ir.json`/`nav.index.jsonl` present at rev; net state
   copied from live checkout + a `T-bench` binding injected for the concurrent task).
   `--mode fixture`: hermetic mini-repo (real `.opencode/` + compiled `.meta/.omt/` projections
   copied, synthetic `src/`+`tests/` targets) for goldens.
3. **Trial runner (`scripts/omt/bench/probe.ts`, bun)** — ONE process per task = ONE agent
   session; replicates the opencode hook bus faithfully:
   - shared `EnforcerEnv` + `createSessionState()` across gates and tools (the real single-env
     session model);
   - `omt_phase/omt_skip/omt_complete/omt_tdd` via `createPhaseTools(env)`/`createTddTools(env)`
     over the shared env; `omt_status/omt_think/omt_nav/omt_kb_nav/omt_net` via their plugin
     defaults rooted at the sandbox;
   - per step: `navTrack`+`kbTrack` (before), `runBeforeGatesDry` (decision transcript incl.
     per-gate fired/blocked/stop; the A4 projection sibling — read-only, same impls), then the
     step's real effect (tool execute / file edit / spawn), then `sessionBootstrap` (once per
     session), `trackRead`, `injectThoughtsOnRead`, `lspAfterEdit`, `runAfterGates` (after-chain:
     g.mvc delta, two-hats auto-revert — real behavior incl. costs);
   - emits a full transcript (per step: args/result bytes, gate decisions, durations, rc).

   Bash/read denies are modeled from `opencode.jsonc` permission rules (opencode-core enforces
   them live; the benchmark re-uses the same rules text) — parsed by the driver, passed in the
   spec. Allowed bash/verify steps really spawn (`Bun.spawn`, cwd=sandbox) so verify time and
   stdout bytes are real.

## Task sample (6, per Improvement002 A) — real mode, pinned rev

| task | seeded fault (setup, not counted) | agent work | seeded violations |
|---|---|---|---|
| `bugfix` | `chat_history.py` `ORDER BY timestamp ASC`→`DESC` (breaks `test_get_messages_returns_in_order`) | diagnose (pytest expect-fail) → declare bug_fix → fix → canary → regression test → green | edit tests/ w/o canary |
| `cross_layer` | model `ASC→DESC` + UI `chat_controller.load_conversation` `for msg in messages`→`reversed(messages)` | fix 2 layers + model test | edit src w/o phase; edit tests/ w/o canary |
| `major` (TDD) | none; setup pre-scaffolds a feature dir | design doc → declare major_feature Programming → omt_tdd testlist → RED (own-dir narrowed canary) → red record → GREEN (kb consult + src impl) → green record | edit src during RED hat (two-hats); edit src w/o kb consult |
| `harness_repair` | `harnessc.py` `BUDGET_DIET_PROXIMITY = 64`→`65` (breaks budget_diet boundary golden; e2e source pins stay green) | diagnose → declare → stage (T4-2) → edit → boundary e2e (receipt) → stage --clear → golden green | edit harness file w/o stage/receipt; `git push` (bash deny) |
| `resume` | ledger seeded with a recent phase record (post-compaction scenario) | `omt_status{op:resume}` + bounded partial reads (T3-3 digest path) → tiny continuation | read `.env` (read deny); `git push` (bash deny) |
| `concurrent_conflict` | net state copied + `T-bench` binding injected | A claims T-bench; A fires work_start; checkpoint | B double-claim (arbitration refusal); edit `scripts/omt/net/state.py` w/o work_start (g.net); B stale-generation claim |

Plus **fixture tasks** (hermetic, goldens): `fixture_bugfix` (full happy path + both violations)
and `fixture_nophase` (violations-focused micro-task used to prove removal-experiment accounting).

## Metrics (per trial; pure accounting from transcript)

- `steps`, `harness_calls` (omt_* executes), `tool_calls`
- `blocks_tp` (role=violation AND blocked) / `blocks_fp` (role≠violation AND blocked — friction)
- `violations_missed` (role=violation AND NOT blocked; **target 0 across the suite**)
- `interventions` / `recovery` (role-tagged steps the harness forces)
- `verify_seconds` (Σ verify spawn durations), `io_bytes` (Σ args+result bytes),
  `tokens_est = io_bytes // 4` (≈4 chars/token, mh3 convention)
- `success` (all assert/verify expectations met), `regressions` (expected-pass verifies failing)
- resume task extra: orientation bytes vs full re-read counterfactual (T3-3 win quantified)

## Removal experiments (per gate)

For each before-gate (g.nav, g.protect, g.receipt, g.tests, g.net, g.phase, g.think, g.kb):
re-run trials with that gate filtered from the loaded IR passed as `runBeforeGatesDry`'s
`irOverride` — **bench-side filter only; no production flag exists**. Savings model: steps
annotated `gate: <id>` (the ceremony that exists to satisfy that gate) are counted as saved
calls/bytes when the gate is removed; `violations_missed` per gate shows what the gate buys.
Bash/read config denies are not gates and are not removal-experimented (documented).

## "No policy change" guardrail

- zero edits under `.opencode/`, `opencode.jsonc`, `.meta/META_HARNESS.omt` (not harness-surface;
  no e2e receipt needed — `scripts/omt/bench/` is outside `HARNESS_FILES`);
- removal experiments are evaluation-time IR filters inside the probe process;
- the sandbox is a disposable worktree/fixture; the live checkout is never a trial target.

## Goldens (tests/scripts/omt/test_task_cost_benchmark.py)

1. task-def validation (structure, ≥1 violation/verify/assert per task, gate annotations valid);
2. metrics accounting on synthetic transcripts (exact TP/FP/missed/intervention/byte math);
3. removal accounting (annotated-step savings + missed counting);
4. report rendering (markdown rows + stable JSON schema);
5. deny-rule parsing from opencode.jsonc;
6. bun-gated hermetic fixture trial end-to-end: real gates, real ledger, violations caught
   (missed=0, fp=0, success=true);
7. bun-gated removal variants: disable g.phase → the no-phase src edit slips (missed=1, the
   declare step counted saved); disable g.tests → canary violation slips;
8. CLI `list`.

## First numbers (deliverable)

One recorded `--mode real` run at pinned HEAD: per-task metrics + totals + gate-removal table →
JSON + markdown under `6.testing/features/feature_093.task_cost_benchmark/bench_first_numbers.*`.
The run validates the 6 real task scripts empirically (unexpected FP blocks = friction findings,
recorded as such — that is signal, not failure).

## Known modeling assumptions (documented in the report)

- scripted deterministic agent (not a live LLM) — measures harness interaction cost, not model
  reasoning cost; steps modeled on recent real features (087/091/092 ceremony shapes);
- bash/read deny enforced by opencode core are re-evaluated from the same rules text;
- removal savings assume a rational agent skips ceremony for a removed gate (annotation model);
- session bootstrap + thought-injection bytes counted on first result per session (real hook
  behavior replicated in-probe).
<!-- TA: gotcha: probe must build ONE shared EnforcerEnv (createSessionState) used by BOTH runBeforeGatesDry AND createPhaseTools/createTddTools — plugin-default tools (omt_status/think/nav/kb/net) build their own internal envs, so in-memory flags set there never reach the gate env; cross-plugin state must flow via ledger records + the trackers (navTrack/kbTrack/trackRead) which the probe calls itself, replicating the omt_enforcer.ts hook bus exactly (before: navTrack+kbTrack+runBeforeGatesDry; after: sessionBootstrap once/session, trackRead, injectThoughtsOnRead, lspAfterEdit, runAfterGates). GOTCHA_PROBE_SERIALIZATION applies to tool results (JSON.stringify before console.log). -->
<!-- TA: gotcha: two-hats RED bootstrap deadlock + skip shadowing (ledger-proven, feature_043/050 ses_f8cac…/ses_f8c6b…): under tdd_mode the testlist hat blocks ALL edits (ir.hats tdd.testlist allow="") and guardTestsPath delegates to tddGateCheck WITHOUT consulting the canary skip — but cmd_start (omt_tdd red) requires the test file to already exist and fail (nonexistent file → pytest exit 2 → error, no record). Real flow (feature_050 22:06–22:07): testlist → omt_skip{scope:tests, reason:"RED bootstrap — planning-hat deadlock"} → write test → red. SIDE EFFECT: getActiveUnlock is latest-phase-OR-skip-wins, so that skip shadows the tdd phase record → guardSrcPath's `unlock.record.tdd_mode` is undefined → two-hats NOT enforced on src/ for the rest of the session (the impl between red and green was written un-two-hatted — reality, not theory). Major-task design consequence: (a) seeded violation "edit src during RED hat" must be placed BEFORE the canary skip (testlist hat, phase record latest → tddGateCheck blocks, attribution g.phase) or it will be missed; (b) the post-red src edit before kb consult is caught by g.kb (order 55) instead; (c) the impl edit after kb consult passes with two-hats shadow-off — record as FINDING, not failure. -->
<!-- TA: why: removal experiments ride runBeforeGatesDry's irOverride param (feature_077): probe loads the IR, filters ir.gates by id, passes the filtered IR as irOverride — a bench-side evaluation-time filter with ZERO production changes (no disable flag ever exists in .opencode/ or the CLI). Savings model: steps annotated gate:<id> count as saved calls/bytes for the removed gate (rational-agent assumption, documented in report). -->
<!-- TA: gotcha: g.net engagement requires isConcurrentMarking (policy_decision.ts): work_active > 1 OR 2+ f\d+_active holders; live net marking is work_active=0, work_pending=0, no task_bindings, no f\d+_active places, revision 57. Concurrent-task setup must therefore inject THREE bindings + tokens (T-bench for A; one PRE-CLAIMED in setup by a second owner so work_active=1 before A's claim; one spare pending so a work_pending token remains for fire work_start after claims) → after A claims T-bench, marking is work_active=2 = concurrent → g.net engages. Also: the probe's env.$ MUST be a real shell (Bun.$ from "bun" supports .cwd()/.quiet()/.nothrow() tagged-template API the g.net impl uses; `typeof ctx.env.$ !== "function"` makes the gate silently skip the live net_check shell-out) — needed for tdd tools + omt_phase baseline too. -->
<!-- TA: gotcha: worktree facts: .meta/.omt/{harness.ir.json,nav.index.jsonl} are the ONLY committed files under .meta/.omt (git ls-files) — a fresh pinned-rev worktree has a valid compiled harness but an EMPTY ledger (clean session start, no receipt → g.receipt fail-closed until stage/e2e, exactly the harness-repair ceremony to measure). Net state files (META_NET.petri.json etc.) are NOT committed — concurrent task setup must copy them from the live checkout and inject a claimable T-bench binding via net.state (test_net_task_claim_generation.py _pool_bundle pattern, OMT_NET_DIR/OMT_LEDGER_PATH/OMT_COORDINATION_ROOT hermetic env vars). -->
<!-- TA: why: probe imports lib+plugins from the LIVE .opencode (absolute paths) with initOmtShared(sandbox) — equivalent to the worktree's own .opencode at pinned HEAD because no lib/plugin code reads .opencode/ sources at runtime (all state reads resolve via REPO_ROOT=sandbox: ledger, harness.ir.json, nav.index.jsonl, thoughts, receipt, WORK.md); avoids copying node_modules into sandboxes. Corollaries verified: (1) .opencode/.gitignore ignores node_modules → a fresh worktree has NO node_modules → the tdd baseline full-suite run inside a worktree has pre-existing bun-import failures (real, lands in baseline_failures — snapshot semantics handle it); (2) omt_complete's validate-exit runs FEATURE-scoped tests only (30s/node) — the FULL suite (120s cap, -m "not opencode_live") runs only at omt_phase Programming-tdd entry (baseline capture); (3) verify/bash step commands must match opencode.jsonc allow patterns (uv */bun *) — fixture test runner is a bun script, real tasks use `uv run pytest …`; (4) worktree uv venv creation happens in SETUP (pre-warm, not counted). -->
<!-- TA: gotcha: CORRECTION (session-3 recon): scripts/omt/ IS an IR harness_paths prefix → scripts/omt/bench/* is g.receipt harness surface in the LIVE session too — writing the package rides one-edit-per-file-per-e2e-receipt round-robin (first write of a not-yet-existing file passes: omtHarnessE2eStatus ok when !existsSync(abs); any second edit of a dirty file needs a fresh receipt or harnessc stage). pause_d's "bench is outside HARNESS_FILES / no e2e receipt needed" claim was WRONG — HARNESS_FILES in test_omt_harness_e2e.py is the e2e's own covered-file list, a different mechanism from the g.receipt when=path_in(@var.harness_paths) gate. -->
<!-- TA: gotcha: g.net impl fail-closes (evaluatePolicy deny, no shell-out) when net_state.sidecar.json is unreadable → EVERY sandbox (all 6 real tasks + both fixtures) must copy live net state (META_NET.petri.json + net_state.sidecar.json; live rev 57 marking work_active=0 = solo → activation_solo_skip) or every src/tests/scripts edit is g.net-blocked as FP; concurrent setup additionally injects 3 bindings (T-bench pending, one PRE-CLAIMED active by worker-2, one spare pending) and sets live_marking work_pending=2 work_active=1, leaving agent_attention=1 feature_ready=1 (work_start in={agent_attention:1,feature_ready:1,work_pending:1} confirmed live) → after A's claim work_active=2 concurrent and fire work_start still enabled. -->
<!-- TA: gotcha: net/gate.py check_edit_allowed: fire receipt = ANY net_fire *_start-suffixed ledger record within 8h, SESSION-AGNOSTIC (session param accepted-but-ignored — gate.py TA risk) → concurrent task step order MUST be A claim → B double-claim (engine task_not_pending) → B no-work_start edit (g.net blocks: concurrent + no receipt) → B stale-rev claim (engine stale_revision; expected_revision placeholder resolved to the setup revision at spec build) → A fire work_start → A edit scripts/omt/net/state.py (allowed via receipt; file still committed-clean so g.receipt passes) → A checkpoint. B's edit placed AFTER A's fire would PASS (session-agnostic receipt) = missed violation. -->
<!-- TA: why: fixture_nophase step order: read src/app.js FIRST so g.kb read-recency passes and the no-phase violation attributes to g.phase alone (else g.kb overlaps and golden #7's g.phase-removal slip is masked); the canary violation on tests/ needs no read (g.kb/g.phase don't scope tests/). Unified refusal metric: refused := gate-block OR opencode.jsonc deny (bash/read, enforced driver-side pre-spawn) OR engine envelope ok:false / string ❌|⛔ (omt_net claim refusals, omt_complete blocks) — blocks_tp = role=violation ∧ refused; violations_missed = role=violation ∧ ¬refused; success = all verify/assert expectations only (missed violations don't flip success — removal runs stay "successful but leaking"). -->
<!-- TA: why: major task shape locked: slug feature_990.bench_major (detectDesignArtifact needs feature_\d+ to auto-find 4.design/features/<slug>/design_001_bench.md pre-scaffolded by setup); stub src/agentx/bench_major_demo.py `def bench_answer() -> int: return 0` pre-created so the RED test (tests/features/feature_990.bench_major/test_bench_major.py::test_bench_answer, asserts ==42) collects and FAILS exit-1 (a nonexistent module → pytest exit 2 = collection error = no red record); violation-1 (src edit during testlist hat) placed BEFORE the canary skip with NO prior read → dry transcript blocked_by [g.phase,g.kb], real chain blocks at g.phase (order 40<55); violation-2 post-red blind edit → g.kb alone; after omt_skip{scope:tests} the skip shadows the tdd phase record ⇒ impl edit and g.tdd_after run un-two-hatted = FINDING (TA:112c), not failure. -->
<!-- TA: why: resume task shape locked: setup seeds the sandbox ledger (1h-old phase minor_feature/Programming feature_991.bench_resume + project_link bench_resume + trail records — _seeded_records shape from test_resume_digest.py) plus a mini .projects/meta/bench_resume/{PROJECT.md,CURRENT_STATE.md} home; steps: omt_status{op:resume} → bounded partial reads (offset/limit) of PROJECT.md/CURRENT_STATE.md (tag=orientation) → tiny continuation (append session note to CURRENT_STATE.md — .projects/ is ungated) → violations read .env (read deny) + bash git push (bash deny) LAST; metrics extra: orientation_bytes = Σ io_bytes of orientation-tagged steps vs counterfactual = full byte sizes of WORK.md+PROJECT.md+CURRENT_STATE.md recorded by the driver in the run manifest. -->
<!-- TA: gotcha: net gate DRIFT check (session-4 recon): net/cli.py `gate` subcommand computes drifted = st.revision != last net_* ledger-record revision (read_ledger_net_records, hot+latest-archive) → ERR_NET_DRIFT_CONFLICT blocks. A freshly copied net bundle (rev 57) over an EMPTY sandbox ledger drifts — but the concurrent step order (TA:119) is SAFE by construction: claims/fires append net_* records (net_claim/net_fire with revision) BEFORE the first gate shell-out (B's blocked edit comes after A's claim), so rev and ledger stay in lockstep. No other task ever gate-shell-outs (solo marking solo-skips pre-shell in the TS impl) → no sandbox needs a ledger net-record seed. -->
<!-- TA: gotcha: scripts/omt/net/state.py carries 5 TA: thoughts, harnessc.py 4 (grep-verified at HEAD; chat_history.py, chat_controller.py, utils.py, test files: NONE) → g.think (order 50) fires on their edits AFTER g.net (35): B's no-work_start edit needs a PRIOR omt_think{op:list, path:"scripts/omt/net/state.py"} by ses_B, else the g.net removal experiment shows NO slip (g.think still blocks — attribution masked); A needs the same consult before the allowed edit. Concurrent order (TA:119) therefore gains: B think-consult inserted between the double-claim and the no-work_start edit. Think consults write a think_consult ledger record (omt_think list op) — session-scoped per hasConsultedThoughts, so each worker pays its own. -->
<!-- TA: gotcha: uv.lock is GITIGNORED (.gitignore:4 — only pyproject.toml + .python-version committed) → a pinned-rev worktree has NO lock: sandbox setup MUST copy the live uv.lock into the worktree BEFORE `uv sync` (pinned resolution, no network drift). Also verified: claim_task side effects = build_workspace + ensure_workspace → best-effort mkdir <root>/.worktrees/<task>-g<gen>/ + `git branch omt/<task>/g<gen> <base_commit>` (fail-open, inside the sandbox — expected, harmless); coordination_root defaults to the bundle dir (.meta/.omt) when OMT_COORDINATION_ROOT is unset/scrubbed — the net lock lives beside the copied bundle. -->
<!-- TA: why: concrete anchors/commands locked (session-4 recon, exact at HEAD): bugfix/cross_layer regression test = module-level APPEND to tests/unit/model/test_chat_history.py (class fixtures temp_db/repo are CLASS-scoped — a module-level test must build its own temp-db ChatHistoryRepository); UI seed/fix anchor = 12-space `for msg in messages:` + 16-space `if msg.role != "system":` (view loop ~L180 only — the rebuild loop's next line is `if msg.role == "user"`); verify commands: `uv run pytest tests/unit/model/test_chat_history.py -q` (expect fail then pass), `uv run pytest tests/scripts/omt/test_budget_diet.py -q` (broken golden = test_boundary_headroom_64_fires_65_silent), boundary e2e `uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q` (writes receipt with covered_files sha256 + policy_ver + results.status=passed); RED success assert = result contains "✅ RED" (tdd cmd_start message), green failure = "⛔ Test still fails" (engine refusal per TA:120); run_pytest = [sys.executable, "-m", "pytest", node, "-x", "-q", "--no-header", "--tb=short"] cwd=sandbox (venv python → uv sync pre-warm required); omt_phase{major,tdd} baseline = run_full_suite(timeout=120) excluding opencode_live (real cost, counted); opencode.jsonc deny parsing needs a STRING-AWARE comment stripper (the $schema URL contains "//"). -->
