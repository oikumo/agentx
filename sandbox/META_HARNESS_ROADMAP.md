# META HARNESS roadmap: product refinement, verified work and token efficiency

**Reviewed:** 2026-09-13

**Implementation baseline:** `b60ade730cf9d1cdb5d7ff7d612d39d2d81f79f9`, with existing uncommitted policy/compiler/project changes. Current observations are separated from historical results in §3.5 and §11.

**Inputs:** [original readiness assessment](META_HARNESS_PRODUCTION_READINESS.md) and [revised qualification assessment](META_HARNESS_PRODUCTION_READINESS_REVISED.md).

**Priority revision:** 2026-09-13 — agent productivity and optimal token consumption, as requested by the user.

**Product refinement review:** 2026-09-13 — refreshed source inspection, isolated defect probes, repository checks, and comparison with primary documentation for current harnesses (§2.2).

**Guidance-economy refinement:** 2026-09-13 — request-fidelity contract anchoring done to the work the user requested (§4.6), guidance-surface quality and request-fidelity measures (§7.1), a usage-unavailable proxy ladder for token accounting (§7.1), tiered experiments with a fast lane for trivially-safe output bounding (§7.2, §5.1 item 3b).

**Productivity-economy deepening:** 2026-09-13 — fixed-versus-marginal cost structure and task-size break-even (§1); harness-assembled completion outcomes, deviation taxonomy and investigation-task acceptance (§4.6); deliberation-inflation and cache-churn cost rows, context value test, digest-as-compaction-anchor (§6); attempt-cost decomposition plus advisory-precision, review-cost and reasoning-share measures (§7.1); dogfood measurement lane (§7.2); standing economy disciplines — budget ratchet and net-zero ceremony (§7.4), grounded in the shipped feature 054 fast path and feature 057 gate budget.

**Status:** useful internal development harness; product value and verified execution remain unproven. This document proposes implementation work and release criteria; it does not implement fixes, qualify a release, or modify the canonical project backlog.

## 1. Product decision

**Make the coding agent complete more correct work with fewer total tokens, fewer unnecessary interactions, and less recovery effort.** The harness should supply the context and tools needed for the next useful action, perform deterministic bookkeeping itself, and preserve enough verified state that the agent rarely has to rediscover prior work.

The primary optimization objective is **total model tokens per independently accepted task**, including failed attempts, repeated context, reasoning/output, tool-result ingestion, verification diagnosis, retries, and recovery. Track accepted throughput and human intervention alongside it. A shorter prompt that causes another investigation or repair cycle is a regression if total accepted-task cost increases.

“Optimal” means the best measured tradeoff for the supported workload and runtime, subject to correctness and required policy constraints. There is no established universal minimum. Keep the non-dominated choices when one uses fewer tokens but takes longer; state the selected tradeoff. Report monetary cost separately because cached-input pricing and different models can change spend without reducing token volume.

Harness cost has a **fixed component** (instruction surface, tool schemas, startup and guidance context) and a **marginal component** per action and task. Small tasks are the hardest case: where fixed cost dominates, every added mechanism is net-negative. Publish the measured task-size break-even — the smallest task class where total accepted-task cost beats the native runtime — keep the shipped bug_fix/test fast path ([feature 054](../.meta/software_development_process/2.requirements/features/feature_054.small_task_fast_path/FEATURE.md)) as the model for task-type-differentiated light lanes, and treat growth of the fixed surface as a measured recurring cost, never as free capacity (§7.4).

Total accepted-task cost also decomposes as **(tokens per attempt) × (attempts per accepted task)**. Context economy moves the first factor; guidance quality, truthful prediction and first-pass correctness move the second. Report both factors (§7.1): an optimization that cheapens each attempt while inducing more attempts can be a net regression that the aggregate metric alone would hide, and the two factors are optimized by different mechanisms.

**First delivery order:** capture a reproducible baseline and fix misleading success → measure native-runtime versus harness task economy → combine task preparation and resume → test a minimal workflow in other repositories → reduce measured waste → reuse sound verification → qualify and package the proven workflow. Close critical enforcement defects alongside measurement. Broader concurrency follows demonstrated solo value.

Today, the defensible claim remains **development assistance**. The repository has substantial policy, testing, navigation, and coordination machinery, but current completion and enforcement behavior still prevents a verified-solo claim. Managed concurrency has advanced considerably since both assessments; it needs integration and failure qualification of existing components, not a fresh implementation of the entire T5 plan.

The first target user is a developer maintaining an existing repository with runnable acceptance checks, repeatedly resuming agent work and manually checking whether a task is actually finished. This is a customer hypothesis to test, not established demand. The initial execution profile is one trusted operator, one qualified adapter/runtime, one workspace, and one active writer. Cooperative mistakes are in scope. An unrestricted malicious process that can rewrite the harness and its evidence is outside this boundary.

The unit of product value is an accepted user change at lower total agent effort. Verified solo execution remains the first qualified release boundary, while productivity experiments can proceed in disposable fixtures before the entire release program is complete. Qualification is a constraint on advertised guarantees, not a prerequisite to reducing duplicate reads or measuring waste.

"Accepted" must remain traceable to the work the user requested. The task record keeps a bounded verbatim extract of the request, acceptance cases derive from and cite it, and completion reports back in user terms with visible deviations (§4.6). Work beyond the request is waste even when its tokens were spent efficiently, and a completion claim that outruns the requested scope is a fidelity failure, not a success. The agent's paraphrase of a task never becomes the authoritative statement of what was asked; after compaction or a session boundary, the harness re-anchors to the request itself.

| Capability | Current assessment | Next defensible release claim |
|---|---|---|
| Development assistance | Useful existing scaffold; limitations must be visible. | Installable preview with explicit support and evidence boundaries. |
| Verified solo execution | **NOT QUALIFIED.** Current F02, F03, F05, and F09 failures were reproduced locally during this review. | Qualified only for a named runtime/adapter profile after all applicable release gates pass. |
| Managed concurrent execution | **NOT QUALIFIED.** Locking, claims, lanes, and recovery exist; execution and durability gaps remain. | Separately qualified local coordinator plus at most two workers. |

Installation Tiers 1–3 select features. They do not select the strength of a guarantee. Preserve that distinction in onboarding, commands, and release notes.

## 2. How the two assessments are fused

The original is the stronger diagnostic reference: it contains concrete source paths, historical probes, measurement limitations, and backlog mapping. The revision is the stronger acceptance specification: it adds capability-specific blockers, explicit decision semantics, an evidence lifecycle, and release gates. Neither is a current release certificate.

| Topic | Retain | Update in this roadmap |
|---|---|---|
| Findings | Stable F01–F12 identifiers and original failure explanations. | Reassess each against current source and distinguish partial implementation from qualification. |
| Decision semantics | Revised `ALLOW / DENY / UNKNOWN / ERROR` and independent obligations. | Apply first at critical boundaries; avoid making a complete evaluator rewrite prerequisite to fixing false completion. |
| Product boundary | Assistance → verified solo → managed concurrency. | Add distribution, onboarding, support, upgrade, release automation, and adoption validation. |
| Concurrency | Original transaction/isolation design and revised race/crash acceptance. | Credit features 079–085; replace “implement T5” with specific remaining integration and recovery work. |
| Measurement | Original task-cost pilot and revised acceptance/cost metrics. | Make tokens per accepted task and accepted throughput the governing objective; put T3-4, preparation, resume, and verification reuse first. |
| Invariants | Revised I01–I10 register. | Use the revision's numbering; the original assigns different meanings to some I-identifiers. F-identifiers remain stable. |
| Evidence | Original source map and revised evidence lifecycle. | Historical pass counts and temporary probes remain historical/local evidence. They do not close release blockers. |

The recommendation to delay the *managed release claim* still stands. T5-1 through T5-7 are already recorded as shipped; further coordination work must demonstrate a productivity benefit before competing with the solo token-economy work. Their original acceptance scope and broader product qualification scope remain separate.

### 2.1 Critical assessment of the previous roadmap

The roadmap's strengths are its acceptance-based cost metric, explicit evidence limitations, and decision to reuse existing mechanisms. Its weakness is that it still describes a large engineering program more clearly than a product a developer can adopt and judge.

| Problem in the previous plan | Product consequence | Refinement |
|---|---|---|
| The first comparator is the existing harness. | A large improvement can still be worse than the runtime alone. | M0 compares native OpenCode, current Meta Harness, and one proposed refinement under matched conditions (§7.2). |
| Generic productivity is the main promise. | No clear reason to install another layer. | Test one promise: resume a repository task and obtain a reviewable result whose checks are tied to the current change. |
| Packaging and outside users arrive at M5. | Repository coupling and unwanted ceremony can survive every internal experiment. | Add a minimal installation and observed user pilot at M1; reserve release distribution/upgrade guarantees for M5. |
| “Shipped” components sit beside unresolved behavior at their integration boundaries. | Feature count and test count overstate readiness. | Keep shipped records, but require an end-to-end task demonstration and named residual regressions. |
| Tokens dominate the objective. | Token reduction can hide setup effort, slower work, needless approvals, or rejected changes. | Treat acceptance, elapsed time, intervention, activation, and repeat use as constraints; report maintenance/payback separately. |
| Every gate has a rationale, but its marginal value is unmeasured. | The harness can make agents comply with the harness rather than complete user work. | Measure each optional mechanism and remove or demote those without observed benefit. Keep required safeguards fixed during comparisons. |
| A large qualification register lacks small delivery boundaries. | More design can postpone fixing obvious defects. | Use the bounded work packages in §5.1; begin with a reproducible compiler baseline and F05/F02/F03/F09. |

**Verdict:** retain the compiler, policy/evidence concepts and existing OpenCode integration; narrow the default workflow. The candidate differentiator is traceable repository-specific acceptance and recovery. It is not yet a demonstrated competitive advantage. Petri-net coordination remains an optional implementation mechanism until it improves a measured user outcome.

### 2.2 Comparison with current harness practice

Primary documentation accessed **2026-09-13**. This is a capability and design comparison, not a benchmark ranking or certification of the other systems. Hosted products, SDKs, workflow engines and research agents serve different scopes; their documented capabilities do not imply equivalent guarantees. No competing harness was run in this review.

| Reference | Documented practice | Meta Harness assessment and next step |
|---|---|---|
| **OpenAI Codex** | Filesystem/network sandboxing and approval policy are distinct controls. App Server exposes task activity through thread/turn/item events, approval requests, command results and token-usage notifications. [Sandbox](https://learn.chatgpt.com/docs/sandboxing), [App Server](https://learn.chatgpt.com/docs/app-server). | OpenCode-specific hooks and policy files are not a portable enforcement boundary. Specify required adapter capabilities and normalize observed events into the task/evidence contract. Use host usage reporting where available; do not infer a Codex adapter exists. |
| **Claude Code** | Hooks have explicit event-specific decision/error behavior; ordinary command-hook failures and timeouts can be non-blocking. Its Bash sandbox enforces filesystem/network limits on processes and children. [Hooks](https://code.claude.com/docs/en/hooks), [sandboxing](https://code.claude.com/docs/en/sandboxing). | “Uses hooks” is insufficient assurance, even in a mature product. Test missing plugins, malformed results, timeouts and supported effect paths on the real host. Fix F02/F03 and distinguish process containment from repository workflow policy. |
| **Anthropic long-running-agent harness** | Initial setup, explicit feature acceptance, incremental work, progress artifacts and end-to-end checks help subsequent sessions resume and avoid premature completion. This is a documented experimental pattern, not a universal architecture. [Engineering report](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents). | WORK/project/ledger machinery already covers parts of this pattern, yet entry points are stale and resume remains backlog. Finish one trustworthy task digest and acceptance flow before adding more orchestration. |
| **OpenCode** | Native allow/ask/deny permissions, local or packaged plugins, tool hooks, and an experimental compaction hook are documented extension points. [Permissions](https://opencode.ai/docs/permissions/), [plugins](https://opencode.ai/docs/plugins/). | This is both the first integration target and the essential baseline. Reuse its loop, permissions and compaction facilities where compatible. Qualify the installed runtime/plugin versions; an experimental hook requires a fallback and compatibility test. |
| **OpenHands Software Agent SDK** | Separates SDK, tools, workspace implementations and agent server; exposes typed events, context condensation and local/remote execution models. [Architecture](https://docs.openhands.dev/sdk/arch/overview). | AgentX's wheel packages the application, not an independent Meta Harness product. Establish a minimal dependency boundary and event contract without rebuilding a general agent SDK or remote server. |
| **LangGraph** | Checkpointers persist thread-scoped graph state; stores hold cross-thread data. Persistence backends and checkpoint inspection support continuation and recovery. [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers). | Separate progress, knowledge, permission and accepted evidence. Existing JSONL/journal machinery needs a defined commit/recovery protocol. Checkpoint presence alone does not prove that external effects or verification are valid; importing LangGraph would not close C1–C5 by itself. |
| **mini-SWE-agent** | A deliberately small Bash-based loop, linear history and replaceable execution environment make it useful as a baseline. [Project documentation](https://mini-swe-agent.com/latest/). | Complexity must earn its cost. Include a minimal-loop comparison only if the same model/task configuration is feasible; classify it separately where policy guarantees differ. Published benchmark scores do not establish Meta Harness's relative performance. |

**Implication inferred from these sources and the repository review:** task continuity, runtime extension, permissions, tracing and context management are already available in several forms. Invest in the integration that makes a repository task's state, verification and recovery understandable and dependable. Adopt existing runtime capabilities; retain custom mechanisms only where they add measurable value. A standard protocol can transport a tool call without ensuring it mediates every write.

## 3. Implementation evidence and current-state reconciliation

### 3.1 Evidence boundary

The checkout was clean at the start of the original review. That review inspected the actual compiler, TypeScript hook/gates, completion path, state helpers, net transaction and workspace implementation, CLI, initializer, and relevant tests. Navigation used the repository's `omt_nav` plugin through Bun because this host does not register the `omt_*` tools. That is a limitation of this session's integration, not evidence that OpenCode cannot load the plugins. The earlier productivity revision preserved those observations. This product review refreshes selected findings in §3.5; it does not recertify the entire implementation.

Other work appeared during the review in `WORK.md`, the project manifest, and feature 089 scaffolding. Those changes were preserved. This is a working-tree assessment, not an immutable release audit; the final validation record states its limits.

| Check | Observation from the baseline review |
|---|---|
| Compiler and projection verification | `uv run scripts/omt/harnessc.py check --verify-projections`: 263 records, zero errors; the existing unindexed self-evaluation workflow warning remains. |
| Runtime discovery | Installed OpenCode `1.18.30`, Bun `1.3.14`; plugin dependency remains `@opencode-ai/plugin` `1.17.11`. These identifiers do not by themselves establish compatibility. |
| Existing behavioral tests | Current suite run recorded in §11. New net transaction, claim, workspace, capacity, verification, recovery, and dependency test modules are present. |
| Fresh isolated probes | F02, F03, F05, and F09 reproduced through real TypeScript modules with temporary state and stubbed subprocess responses. No actual guarded file edit was executed. |
| Product qualification | No complete retained clean-install → real-adapter allow/refuse → verification → upgrade/recovery qualification report was established. |
| Outcome efficiency | No new task-cost benchmark was run. |

Recorded compiler size snapshot: `AGENTS.md` 2,918/2,944 bytes; tool descriptions 1,812/1,856; argument descriptions 2,454/2,464; nav index 63,963/64,000; IR 20,079/20,480; gates 10/12. At that snapshot, 37 nav bytes and 10 argument-description bytes remained. These are representation budgets, not measurements of complete model schemas or end-to-end task cost. Do not automatically raise or tighten them without examining actual delivered context and maintenance cost. Source: [compiler](../scripts/omt/harnessc.py), `measure_budgets`.

### 3.2 Material progress since the original assessment

The [meta_harness_8 project](../.projects/meta/meta_harness_8/PROJECT.md) now records the following work, corroborated by source and test files:

| Shipped slice | What exists now | What it does not yet establish |
|---|---|---|
| 077 / T1-4 | Historical reads of policy, ledger, thoughts and KB through `git show`; historical-state tests. | Complete historical authority: some live observations remain explicitly outside replay. |
| 078 / T1-3 | Bounded graph traversal and risk/thought joins. | An authoritative risk classifier or a reason to introduce HQL now. |
| 079 / T5-1 | `CoordinationLock`, in-lock revision checks, command ID index, and a multiprocess same-revision race test. | Atomic multi-file publication, crash-safe idempotency, or consistent unlocked readers. |
| 080 / T5-2 | Claim/release/transfer/checkpoint operations with ownership generations. | End-to-end actor authorization through every adapter entry point. |
| 081 / T5-3 | Workspace metadata, directory/branch bootstrap, path containment helper and CLI gate parameters. | A populated linked Git worktree or automatic use of managed identity by the live hook. |
| 082 / T5-4 | Two-worker capacity and component-aware scope arbitration. | Protection of every actual write or useful parallel throughput. |
| 083 / T5-5 | Submit/verify/integrate state transitions, serialized lanes, immutable submission references. | Actual verifier execution or verification of the combined integration candidate. |
| 084 / T5-6 | Heartbeats, recovery candidates, generation transfer, pending transaction marker and reconciliation. | Recovery after every real process-kill boundary or atomic state/event/idempotency completion. |
| 085 / T5-7 | Pinned upstream dependencies, staleness checks and objective-status evaluation. | Proof that the supplied evidence describes passing checks against real current content. |
| 086–088 | Ordered skip audit, scope alignment, and per-file recent-read consultation exemption. | Consistent authority lifetimes or content-versioned knowledge relevance. |

The project records six remaining backlog items: T2-6, T2-7, T3-3, T3-4, T3-6, T3-7, plus the recurring T5-8 review loop. Feature 089 scaffolding appeared for T2-6 during this review. The older Quick Start and WORK pause text still point to already-shipped T1/T5 slices. Reconcile those entry points in a separate project-maintenance change; do not treat the stale startup summary as implementation truth.

### 3.3 Finding reconciliation

“Open” below means the product requirement remains unresolved at the inspected baseline. “Partial” credits implemented mechanisms without claiming that the whole finding is fixed. Local reproductions still need retained repository regressions and real-adapter qualification. The priority column describes release-blocker severity, not the new implementation order: F10/F11 and the T3 productivity work now lead the optimization sequence in §5.

| ID | Current disposition and evidence | Required next outcome | Priority |
|---|---|---|---|
| **F01** Mutation coverage/matching | **Open.** Before-hook still extracts one scalar path; edit-tool names remain bounded. `pathIn()` uses exact matching for entries without trailing `/`, while harness classification includes prefixes. | One normalized action/path contract covering supported mutation forms; unsupported mutation refused in the verified profile. | P0 solo |
| **F02** Critical fail-open | **Open; reproduced locally.** Malformed net JSON caused the actual before-hook to return normally and log “failing open.” Unknown predicate fallback remains permissive. | Critical missing/invalid authority refuses; optional advice degrades independently. | P0 solo |
| **F03** Independent gates | **Open; reproduced locally.** Approved test edit stopped at `g.tests`; zero net calls and no later thought evaluation. | Successful test approval satisfies that obligation and continues through all others. Audit protected-path success exits too. | P0 solo |
| **F04** Scope/lifetime | **Partial.** Generation-fenced net claims are new. Legacy cross-session grants and differing progress/consult lifetimes remain; feature 088 also intentionally reuses recent reads across sessions. | Explicit per-record scope/lifetime; no cross-session authority fallback in a profile promising isolation. Consultation reuse must remain distinct from permission. | P0 managed; solo blocker wherever session isolation is claimed |
| **F05** Truthful completion | **Open; reproduced locally.** `exitCode:1` plus empty output wrote completion and advanced Done. Explicit `ok:false` correctly blocked. Feature 075 tests behavior, but `omt_complete` still defaults empty stdout to `ok:true`. | Require process success, valid response, declared checks and matching candidate before verified completion. Docs/no-test and waived outcomes remain explicit. | P0 solo |
| **F06** Stage lifecycle | **Open.** Stage helper checks file membership and optional policy digest; CLI remains create/status/clear. | Owned stage with finish/verify/consume lifecycle, or disable staged acceptance in the first verified profile. | P0 if enabled; otherwise P1 |
| **F07** Evidence contract | **Partial.** Receipts have content/policy/results fields; net submissions and dependencies now carry digests. Missing receipt results still pass compatibility handling; toolchain and complete input closure are not enforced. | One versioned acceptance manifest with mandatory fields, actual verifier evidence, and explicit scope. | P0 solo and managed |
| **F08** Transaction authority | **Substantially implemented, incomplete.** Original “no lock” finding is obsolete for `_transact` paths. Multi-file save, marker ordering, idempotency recovery and unlocked reads still leave gaps (§3.4). | Qualify one commit/recovery protocol across authoritative files, events and command results. | P0 managed |
| **F09** Durable writes/recovery | **Partial overall; TS append failure reproduced locally.** Net recovery machinery is new, but `appendJsonl()` still swallows errors and TDD rollback still restores whole-file snapshots without checking intervening edits. | Failed authoritative writes cannot acknowledge success; recovery preserves newer content. | P0 solo and managed |
| **F10** Truthful prediction/prep | **Partial.** Historical replay and graph inspection improved; dry net evaluation still skips the live permission call while projections can say “all clear.” Task prep remains a standalone slice. | Same action/snapshot semantics; unavailable evidence is machine-readable `unknown`; measure preparation before wider wiring. | P1; P0 if permission certainty is claimed |
| **F11** Knowledge/context value | **Partial.** Recent-read reuse reduces some friction; nav still caps records, not returned bytes/tokens; ceremony metrics remain narrow proxies. | Bounded delivered context, relevant versioned retrieval, and measured avoided rediscovery. | P1 |
| **F12** Independent qualification | **Open at product boundary.** More behavioral and multiprocess tests exist. Recovery tests manually construct markers; lane tests supply verdicts; template tests include static pins. No tracked CI configuration found in the inspected standard paths. | Retained faults, actual adapter workflows, clean-install/upgrade/recovery and required-check release automation. External CI remains unknown. | P0 qualification |

Source locations: [hook](../.opencode/plugins/omt_enforcer.ts), [gate driver](../.opencode/lib/enforcer/gate_driver.ts), [phase/completion](../.opencode/lib/enforcer/phase_gate.ts), [shared IO/evidence](../.opencode/lib/omt_shared.ts), [scope helpers](../.opencode/lib/enforcer/session_state.ts), [typed policy](../.opencode/lib/enforcer/policy_decision.ts), [TDD rollback](../.opencode/lib/enforcer/tdd_hats.ts), [preflight](../.opencode/lib/enforcer/preflight.ts), [task prep](../.opencode/lib/enforcer/task_prep.ts), [net state](../scripts/omt/net/state.py).

### 3.4 Specific remaining concurrency gaps

These are current source-based findings. They extend F01/F04/F07/F08/F09/F12 without renumbering the original register. They have not been demonstrated as live-runtime exploits or as a complete crash campaign.

| Gap | Current evidence | Required implementation/qualification |
|---|---|---|
| **C1: commit, event and retry can diverge** | `_transact()` clears the pending marker before `record_command()`. Reconciliation compares revisions and appends a generic event; it does not reconstruct the original command result/index entry. A later transaction does not first require the pending marker to be resolved. | Preserve enough intent/result identity to finish or reject interrupted commands deterministically; reconcile before new mutation; acknowledge only a recoverable committed command. Test retry after every write boundary. |
| **C2: storage visibility/durability remains partial** | `save()` replaces three files sequentially; readers call `load()` without the mutation lock. Marker fsync failures are swallowed, and bundle/event/index writes do not together form a durable commit. The command index prunes after 500 entries. | Consistent reader generation, explicit process-crash versus power-loss scope, propagated required durability errors, and a documented retry-retention contract that prevents expired IDs from silently replaying effects. |
| **C3: workspace metadata exceeds actual bootstrap** | `ensure_workspace()` performs mkdir and best-effort `git branch`; there is no `git worktree add` in that implementation. Git failure can leave an apparently valid claim. | Create and verify the linked checkout at the expected base; refuse managed activation if bootstrap is incomplete; inspect branch/base/working tree through a real repository fixture. |
| **C4: managed checks are not fully connected to execution** | CLI exposes task/generation/owner, but the live `g.net` shell call passes path/session only. Activation still uses concurrency marking; `check_workspace_edit()` has an optional owner and ignores session. | An explicit managed profile activates claim/workspace checks even with one enrolled worker, threads identity through every write entry point, and enforces declared scope and expected base content. |
| **C5: lane verdicts are supplied assertions** | `verify_result()` and `integrate_finish()` accept `verdict` plus a `coordinator` Boolean; CLI exposes `--coordinator`. These functions move state without running verification or constructing/checking the combined candidate. | A trusted coordinator/verifier boundary executes declared checks, validates results/content identity, and conditionally accepts the actual integrated candidate. A caller-set role flag must not be the full authority contract. |

Sources: [transaction and lane implementation](../scripts/omt/net/state.py), [lock/index/journal](../scripts/omt/net/lock.py), [workspace bootstrap](../scripts/omt/net/workspace.py), [net CLI](../scripts/omt/net/cli.py), [live gate](../.opencode/lib/enforcer/gate_driver.ts). Retain the existing locking, generation and lane design; close these seams before claiming managed execution.

### 3.5 Fresh product-review observations — 2026-09-13

HEAD remains `b60ade730cf9d1cdb5d7ff7d612d39d2d81f79f9`. At review start, `.meta/META_HARNESS.omt`, `scripts/omt/harnessc.py`, `WORK.md` and the project manifest were modified; feature 089 and this roadmap were untracked. These pre-existing changes were preserved. The following observations supersede historical status only for the checks named:

| Check | Fresh observation | Consequence |
|---|---|---|
| Compiler/projection check | Initial check exited 1: nav index **64,956 > 64,000 bytes**, with a stale projection. Concurrent feature-089 work then raised the cap to **65,536** and refreshed projections. Recheck **passed: 265 records, zero errors**; the workflow-index warning remains. | Initial drift is resolved in the observed working tree, not by this roadmap edit. Freeze that identity before benchmarking. The budget increase establishes neither token savings nor runtime qualification. |
| F05 completion probe | Real completion module, stubbed verifier: exit 1 + empty stdout still records completion and Done. Explicit `ok:false` refuses; exit 0 + `ok:true` is the positive control. | “Done” cannot be the acceptance oracle. Fix this small boundary before promoting verification reuse. |
| F02/F03/F09 probes | Malformed net response returns from the real before-hook without refusal; an approved test path stops the dry gate chain before net/thought checks; unwritable ledger append returns without a record. | All four previously reproduced defects remain reproducible. Tests must retain refusal and positive controls, then exercise actual host effects. |
| Concurrency source recheck | `_transact()` still clears the pending marker before storing command replay data; workspace bootstrap still creates a directory/branch rather than a linked checkout; the live net call still supplies path/session only. | C1/C3/C4 remain source-supported gaps. Existing helper tests and shipped feature names do not close execution qualification. |
| Context delivery | `capNavLines()` still limits **25 records**, with no bound on an individual record. Startup points to shipped work; project status still lists six unfinished items. | Measure real delivered payloads and implement a provenance-aware resume digest. A smaller index is not itself evidence of lower task tokens. |
| Distribution/automation | `pyproject.toml` builds `src/agentx`, with application dependencies; plugin SDK remains pinned to `1.17.11`. No tracked CI files found in `.github`, `.circleci`, or the checked standard root paths. | Test a minimal non-AgentX install early. CI outside those paths is unknown; require retained release automation rather than assuming it exists. |
| Host portability | This session does not expose `omt_*` as tools; the nav plugin was invoked through Bun. | Add a capability/health report that distinguishes installed instructions, registered tools, active hooks and enforced effects. A readable AGENTS.md is not proof of mechanical enforcement. |

Probe output: `/tmp/meta-harness-product-review-probes.json`, from the inspected `/tmp/meta-harness-roadmap-probes.ts`. Each probe uses a disposable state root; subprocess results are synthetic and no actual guarded edit occurs. The compiler and suite results are working-tree observations, not immutable release evidence. Fresh suite and document validation are recorded in §11.

## 4. Target product contract

### 4.1 User journey

The supported path should minimize the agent's repeated decisions and context acquisition during a normal task. Deterministic checks and bookkeeping run in code; the agent receives their concise results:

1. **Install and diagnose.** Identify runtime/adapter, verify policy/state compatibility, explain available capability and any missing prerequisite.
2. **Prepare.** Capture a bounded verbatim extract of the user's request, then derive intended behavior, scope, acceptance cases and verification targets from it in one bounded task response. Resolve ambiguity with one bounded clarification, not an interview and not a guess.
3. **Work.** Evaluate every applicable obligation for each supported action; preserve useful progress with clear refusal reasons; surface a drift signal when proposed work falls outside the requested scope.
4. **Verify.** Freeze the candidate and relevant inputs; execute the declared checks outside long-held state locks.
5. **Accept.** Recheck candidate/authority/evidence, acknowledge durable state, and report `verified`, `failed`, `waived`, or `not_verified` explicitly for each acceptance case, in user terms, with visible deviations from the request.
6. **Resume or recover.** Explain the last valid state, outstanding checks and safe next action without repeating all context or overwriting newer work.

These are proposed product operations, not six mandatory model round trips or claims that matching public commands exist today. Combine preparation/resume facts in one bounded response and reuse unchanged evidence when valid. Evolve the existing CLI/tools rather than adding a separate command for every internal mechanism. Acceptance does not itself authorize publication or another external effect.

### 4.2 Small explicit contracts

| Contract | Required information |
|---|---|
| Task | ID, bounded verbatim request extract (or durable reference to it), requested outcome, scope, observable acceptance cases each citing the request, execution profile, verification targets, waiver policy, scope-change history. |
| Action | ID and payload identity, complete normalized path set, operation, workspace, expected base content, task/actor/claim where applicable. |
| Decision | `ALLOW/DENY/UNKNOWN/ERROR`, applicable obligations, reason codes, evidence identities, unresolved checks and recovery action. |
| Progress | Task phase/checkpoint and provenance; no implicit permission. |
| Grant | Subject, scope, issuer, workspace, task/session, policy generation, expiry and revocation. |
| Evidence | Candidate and input digests, policy/verifier/toolchain identities, required/actual checks, process status, result scope, raw evidence reference. |
| Accepted result | Current candidate/evidence references, outcome, visible waivers, durable command identity; integrated candidate/dependency versions in managed mode. |
| Completion report | Outcome per acceptance case with evidence references, the request extract, visible deviations and waivers, remaining work — phrased in user terms, not internal mechanism names. |

Candidate identity includes relevant uncommitted/untracked inputs, deletions, modes, symlink targets, tests and configuration. Exclude generated logs/state/receipts narrowly to avoid recursive digests. A verifier that changes an input invalidates the run. Start with a conservative input manifest; narrower reuse must earn its validity through invalidation tests.

### 4.3 Architecture boundaries

Keep `.omt` as canonical policy and the compiler as its validator/projector. Keep the adapter responsible for normalizing and mediating effects. The evaluator computes decisions from one consistent snapshot; it neither executes verification nor pretends a read-only prediction grants authority. Authoritative persistence records commands and evidence. The verifier executes acceptance. Agent-facing context explains those results and retrieves knowledge.

Migrate typed obligations incrementally using labeled old/new decision comparisons. Newly permitted cases need an explicit rationale and regression. The currently trusted policy must govern activation of its successor; record old/new policy, compiler, adapter and state compatibility, and keep a tested recovery target. Shadow evaluation must never authorize writes.

### 4.4 Minimum useful product and integration boundary

The first demonstrable workflow is: **install in an existing repository → define one change and its checks → interrupt and resume → review the current patch and its evidence**. The developer should understand the result without learning feature IDs, Petri-net transitions or internal consultation sequences. Existing advanced diagnostics remain available on demand.

Expose this through existing status/preparation/completion surfaces wherever possible. The default response gives the intended outcome, candidate identity, checks passed/failed/not run, outstanding action, and evidence location. A refusal names the unmet obligation and a bounded recovery action. “Verified” means the declared checks passed for the named inputs; it never means all possible defects were excluded. Keep workflow completion, verification outcome and user acceptance distinct.

Publish one support profile initially: exact OpenCode/plugin versions, OS/toolchain, observable usage fields, supported file/shell operations, compaction/resume behavior and disabled capabilities. A diagnostic must positively establish tools and hooks are active. Missing or incompatible integration yields assistance-only or unavailable status, never a silent verified-mode downgrade.

Native sandboxing limits effects to its configured boundary; it does not automatically enforce every OMT phase or protected-path rule inside that boundary. For verified operation mediation, either qualify a broker that validates the complete permitted action or constrain the process's write access so it cannot bypass that broker. Include shell children, scripts, multi-file patches, moves/deletions and symlink behavior in the support matrix. Unsupported paths cannot inherit a verified guarantee from a tool name.

Reuse host permissions and existing session authorization. Avoid a second prompt when the same action is already authorized. Deterministic obligations can still fail and explain why, but routine bookkeeping should not require user confirmation. Measure unnecessary prompts separately from necessary boundary approvals.

### 4.5 Early adoption experiment

At M1, prepare a minimal local installation artifact for **two non-AgentX repositories** with different layouts, and observe **three developers other than the maintainer** using disposable copies. Recruitment and repository access are future execution dependencies; no external contact is authorized by this document edit. Start with assistance-only claims until the applicable qualification gates pass.

Proposed pilot criteria, to revise after the baseline: at least two participants complete setup and a first independently accepted task within 30 minutes without maintainer repair; at least two voluntarily use it for three further eligible tasks within two weeks. Record setup time, time to first useful result, confusing refusals, override requests, support minutes, failed tasks and reasons for abandonment. These small numbers test usability and interest, not market fit or statistical reliability.

Compare native-runtime and harness-assisted sessions. If benefit depends on the maintainer interpreting state or editing policy for every task, simplify the product before packaging more features. If usage telemetry is unavailable, label token measures incomplete and report the observable outcomes without inventing usage. Store pilot traces locally by default, redact secrets, set retention/deletion controls, and obtain separate authorization before exporting repository content.

### 4.6 Done definition, request fidelity and drift control

The harness exists to complete work the user requested, and "done" must stay anchored to that request rather than to the agent's evolving interpretation of it. Three anchoring mechanisms keep the request authoritative, and three reporting rules keep the completion honest:

- **Request capture.** Task preparation stores a bounded verbatim extract of the user's request, or a durable reference when the request is a longer conversation. The extract is part of the resume digest, so a fresh session, post-compaction recovery or worker handoff re-anchors to the request itself, never to a paraphrase. Acceptance cases cite the request. An ambiguous request gets one bounded clarification at preparation time — not a guess, and not an interview loop.
- **Drift signals.** Actions or proposed edits outside the declared scope produce a visible advisory: non-blocking in assistance mode, always recorded. Scope additions require an explicit re-anchor — either the user amends the request (logged, with acceptance cases re-derived) or the addition is reported as a deviation at completion. The digest carries the request extract forward unchanged, so the agent cannot silently rewrite what was asked.
- **Truthful completion in user terms.** The completion report names the outcome for each acceptance case (`verified`, `failed`, `waived`, `not_verified`), quotes or references the request, lists deviations and waivers, and states what remains. It uses the user's vocabulary, not feature IDs, transitions or internal obligation names. "Done" never claims more than the declared checks against the named candidate (§4.4); when the user's real acceptance differs from the declared checks, that gap is itself reported rather than papered over.

Completion reporting adds three rules:

- **Harness-assembled outcomes.** The outcome table of a completion report is assembled from recorded evidence — check results, digests, ledger events — with the agent contributing the user-terms phrasing, not the facts. A completion narrative that outruns recorded evidence is the same class of defect as F05: the report can be no more truthful than the state it cites.
- **Deviation taxonomy.** Deviations are classified, not narrated: **scope additions** (delivered beyond the request), **omissions** (requested, not delivered), **quality gaps** (delivered with failed or waived checks) and **interpretation choices** (ambiguity the agent resolved without asking). Each class is counted separately in the fidelity measures (§7.1); an unclassified deviation does not count as reported.
- **Investigation tasks.** Where the request asks a question rather than a change ("why does X fail"), acceptance is an evidenced answer to that question. The completion report answers it directly; "I fixed X instead" is a scope deviation, not a success.

The report itself is bounded — request extract, outcome per acceptance case, classified deviations, waivers, remaining work, with expansion on demand — because review cost is part of the product promise: the user must be able to trust the done claim for less effort than re-doing the work, and that review effort is measured (§7.1).

These are product semantics for the first workflow (§4.4), implemented on the existing task-preparation and digest surfaces (§5.1 item 4); they add no mandatory model round trip. Fidelity is measured, not assumed: scope-drift events, request-traced acceptance cases, completion deviations and user amendments belong to the measurement record from M0 onward (§7.1).

## 5. Delivery roadmap: productivity first

The roadmap now has a productivity sequence and a supporting reliability lane. Measurement and low-impact context improvements can start immediately. An optimization that reuses authority or verification must first satisfy the relevant reliability contract. M-identifiers below replace the earlier qualification-first milestone ordering.

| Milestone | Agent productivity deliverable | Dependencies | Exit criterion |
|---|---|---|---|
| **M0 — Establish truth and task cost** | Reproducible compiler/runtime baseline, F05/F02/F03/F09 fixes, task-level usage trace with a defined usage-unavailable proxy variant (§7.1), independent acceptance oracle and native-runtime comparator. | Instrumentation can start now; do not rely on current Done records. Fixes and the benchmark can proceed independently. | Baseline includes failed attempts, repeated inputs, retries, verification and recovery; missing usage is explicit, and the proxy variant is labeled when request-level usage is unavailable. Critical boundary regressions and positive controls pass before qualification. |
| **M1 — Prepare, resume and test adoption** | Compose existing status, task prep, nav/KB and progress into a bounded response; persist a compact resume digest; minimal install pilot (§4.5). | M0 measurements; truthful handling of unknown state. Prototype/pilot may use assistance-only claims. | Routine prep/resume needs one bounded response, retains critical facts and lowers total task effort; non-maintainers demonstrate activation and repeat use or trigger simplification. |
| **M2 — Eliminate repeated context and ceremony** | Selective context delivery, compact tool outputs, stable tool/schema exposure where supported, batched independent reads and a consistent per-operation snapshot. | M0/M1 measurements identify the main costs. | Lower input tokens per accepted task and fewer redundant calls without increased repair, stale decisions or missing obligations. |
| **M3 — Reuse valid verification and knowledge** | Candidate-bound verification reuse, bounded batch completion where enabled, versioned relevant lessons and precise failure diagnostics. | Evidence/ownership fixes for every reused result. | Unchanged relevant inputs reuse valid evidence; changed inputs reverify; repeated failure diagnosis declines; accepted-task cost improves. |
| **M4 — Prove and tune the improvement** | Controlled comparisons, one-change-at-a-time removal experiments, task-class policies and small external-repository pilot. | M0 baseline plus each candidate optimization. | Accepted-task tokens improve beyond benchmark noise; correctness/critical refusal controls hold; latency and intervention tradeoffs are reported. |
| **M5 — Release the proven workflow** | Versioned independent artifact, concise onboarding, support profile, upgrade/rollback, diagnostic export and qualification report. | Demonstrated M4 value; early pilot evidence; required solo release gates pass. | Clean artifact install, upgrade and rollback pass in non-AgentX repositories; accepted-task benefit survives onboarding/support cost. |

**Execution order:** M0 → M1 → M2 → M3 → M4 → M5, with M4 comparisons after each slice rather than one final benchmark. M1 includes early installation and user feedback; M5 adds supported release lifecycle. Reliability fixes run alongside the affected slices. Managed concurrency is an optional later experiment; it must beat a solo baseline on accepted throughput while accounting for all worker, coordinator and integration tokens.

### 5.1 Immediate implementation queue

Use the existing meta_harness_8 home. Create follow-up feature records when implementation starts, keeping shipped features intact.

| Order / priority | Bounded deliverable | Existing home / dependency | Concrete acceptance |
|---|---|---|---|
| **0 / P0 baseline** | Capture source/runtime identities and confirm the feature-089 compiler/projection repair. | Existing feature **089** work; recheck now passes (§3.5). | Freeze the passing compiler state and dirty/untracked input manifest for the benchmark. Do not reopen the resolved budget error or count its larger cap as token savings. |
| **1 / P0 truth** | Fix the completion subprocess contract, then authoritative append failure. | **F05/F09**, feature 075 residual; `phase_gate.ts`, `omt_shared.ts`. Two small changes. | Nonzero/empty/malformed/missing-result verifier responses never write complete/Done; failed append never acknowledges success; explicit valid success still works. Retain the current reproductions as behavioral regressions. |
| **2 / P0 mediation** | Fix critical error handling and independent gate composition; publish the first operation coverage matrix. | **F02/F03/F01**, gate driver/hook and live adapter tests. | Approved test/protected-path obligation does not suppress net/thought obligations; critical authority error refuses; optional advice failure remains separate; real allowed and refused edits corroborate the matrix. Unsupported shell effects prevent a verified mediation claim. |
| **3 / P0 measurement** | Instrument bug-fix and resume tasks, then the complete solo corpus. | **T3-4**; can proceed alongside 1–2, using an independent oracle. Extends the shipped ceremony meter and ledger medians ([feature 057](../.meta/software_development_process/2.requirements/features/feature_057.gate_budget_ceremony_meter/FEATURE.md)) rather than building a parallel instrument; the bug_fix/test fast path ([feature 054](../.meta/software_development_process/2.requirements/features/feature_054.small_task_fast_path/FEATURE.md)) is the first task-type lane to measure; the dogfood lane (§7.2) starts logging at M0. | Repeatable report compares native runtime/current harness/one refinement, records acceptance and full available usage, and labels missing usage. Pin all configurations and retain raw result references. |
| **3b / P0 safe economy** | Bound the largest single responses: per-record byte cap with explicit continuation, deduplication of identical consecutive reads, summary-first tool outputs. | **F11**, features 069/088 surfaces; runs in parallel with item 3. | Restricted to the trivially-safe class (§7.2): changes that provably preserve information. Required facts remain reachable through continuation; smoke-pair total task tokens do not worsen; full-pilot confirmation follows when the M0 baseline exists. |
| **4 / P1 first workflow** | One-response preparation/resume plus runtime health status, request capture and user-terms completion reporting (§4.6). | **T3-3 + T3-5 / feature 073**, preflight foundations; M0. | Fresh session and post-compaction fixture recover the request extract, scope, acceptance, candidate and outstanding checks; the digest re-anchors to the request rather than a paraphrase; changed inputs invalidate stale facts; health report distinguishes tools, hooks and actual mediation; the completion report maps acceptance cases to evidence in user terms, with outcomes assembled from recorded evidence and deviations classified (§4.6). No additional mandatory agent tool. |
| **5 / P1 adoption** | Minimal install artifact and observed pilot in other repositories. | Feature **059** foundation; item 4; assistance-only until qualified. | §4.5 activation/repeat-use results and support burden recorded; works without AgentX application dependencies or maintainer policy repair. Failure returns work to simplifying the workflow. |
| **6 / P1 measured economy** | Bound/deduplicate the highest-cost output; remove the largest avoidable round trip. | **F10/F11**, features 069/073, T3-7 when justified; item 3 measurements. | Single oversized records have usable continuation; compaction/handoff restores needed content; independent reads share a valid snapshot. Total task cost improves after expansion/recovery costs. |
| **7 / P1 evidence reuse** | Candidate-bound verifier manifest, conservative invalidation and bounded completion reuse. | **F04/F06/F07/F09**, features 074/075; item 1 and declared input closure. | Changed source/tests/config/policy/toolchain invalidate evidence; unchanged inputs reuse it; verifier-mutated inputs fail acceptance; waivers and no-test tasks are explicit. Disable stage acceptance until its lifecycle qualifies. |
| **8 / P1 retention of value** | Pilot selective lessons; run gate-removal and task-class comparisons. | **T3-6 + T3-4**, resume foundation. | Lower rediscovery/retry cost on held-out tasks; unused/stale lessons retire; optional mechanisms with no net benefit are removed or demoted. Required safeguards retain all controls. |
| **9 / P2 release** | Versioned standalone artifact, qualification runner and upgrade/rollback support. | M4/pilot value; all applicable §8 gates, including F01/F12. | Clean install→task→resume→verify→upgrade→rollback succeeds for the named profile; retained CI evidence and a concise diagnostic bundle explain support failures. |

Items 1–3 form the first implementation batch, with separate reviewable changes. The maintainer selects scope and support claims; the adapter work owns effect normalization and compatibility, compiler/state work owns policy/evidence validity, and evaluation work owns the independent oracle. These are responsibilities, not a requirement for separate agents or a larger team. Do not start a second coordination program while this batch lacks retained results.

F01 mediation remains a verified-release blocker; F04/F06/F07 must be resolved before relying on scoped grants, staged acceptance or evidence reuse. Preserve independent regression cases and positive controls. No broad policy rewrite or concurrency platform is a dependency of measuring and eliminating duplicated context.

Apply the repository's implementation gates when executing these items. This document update changes the proposed work order; it does not authorize source fixes, test modifications, relaxed policy, or alterations to the source assessments.

### 5.2 First slice: exact done definition

Deliver the small truth fixes and a T3-4 baseline report before choosing compression ratios or adding another tool. The measurement slice is:

1. Pin task definitions, source candidate, model/runtime configuration and independent acceptance cases. Record each task's request extract so acceptance stays traceable to the requested work (§4.6).
2. Record request-level token usage and task-level outcome, including all retries and helper agents if used.
3. Attribute avoidable work to startup/schema exposure, retrieval, repeated content, orchestration, verification diagnosis, resume and repair.
4. Run matched native-runtime/current-harness attempts for a routine bug fix and an interrupted/resumed task first; expand to the full corpus before generalizing.
5. Identify the largest repeatable source of waste, select one bounded optimization, and replay the same acceptance cases.

A baseline can be collected despite known harness defects because acceptance is assessed independently. In the supporting lane, retain the F05 reproduction at the TypeScript completion boundary and require process success plus an explicit valid result before completion. Assert no completion/Done ledger event on failure. This prevents future internal metrics from rewarding a false success.

## 6. Where the token savings should come from

These are hypotheses grounded in the inspected mechanisms, not measured savings. Optimize in the order demonstrated by M0, considering how often a cost occurs across future tasks.

| Cost source | Current evidence or uncertainty | Proposed optimization | Proof that it helps |
|---|---|---|---|
| Repeated startup and policy/tool descriptions | Byte budgets exist; complete request payload cost is not measured. | Minimal stable core; load task-relevant context and optional schemas only when supported and needed. | Actual request input tokens and cache use improve; required tools/rules stay discoverable. |
| Fragmented preparation | Status, preflight, nav/KB and standalone task prep contain useful pieces. | One bounded task response assembled from shared state and relevant retrieval. | Lower total preparation tokens and round trips with the same obligations and acceptance. |
| Request drift and rework | Unmeasured. Resume is still backlog (T3-3) and the request itself is not pinned, so silent scope expansion and post-compaction reinterpretation are plausible. | Pinned verbatim request extract, drift advisories, explicit re-anchoring and user-terms completion (§4.6). | Fewer out-of-scope actions and less rework; deviations surface at completion instead of in review; clarification round trips stay bounded at one. |
| Post-interruption rediscovery | T3-3 resume digest is still backlog; startup pointers can be stale. | Persist a compact task digest with source/evidence references and invalidation rules. | Resume reaches the next correct action without replaying whole documents; fresh-session control retains all critical facts. |
| Oversized or repeated tool results | Nav caps record count, so a single record can still be large. | Returned-token budget or labeled byte fallback, summary-first output, stable IDs, continuation and requestable detail. | End-to-end tokens fall; additional expansion calls do not erase savings or hide needed facts. |
| Serial discovery and bookkeeping | Redundant calls are plausible; frequency needs measurement. | Batch independent reads; join facts, classify paths and compute obligations in code. | Fewer model round trips and lower total tokens; authorization/mutations remain explicit and ordered. |
| Repeated local state parsing | Helpers read IR/ledger independently; disk bytes are not automatically model tokens. | One immutable snapshot per operation, then measured indexing/caching with correct invalidation. | Lower measured latency/IO; token savings claimed only when model turns or delivered context also decline. |
| Redundant verification | Current phase/batch/evidence mechanisms do not establish reliable reusable acceptance. | Run required checks at meaningful boundaries; reuse only a valid candidate/input/toolchain-bound result. | Fewer redundant runs and diagnostic tokens; seeded relevant changes still invalidate evidence. |
| Repeated failed repair | Diagnostics and knowledge exist, but avoided recurrence is unmeasured. | Stable failure signature, changed-state check, bounded diagnostic output and validated reusable lesson. | Fewer repeat attempts and intervention minutes per accepted task. |
| Deliberation inflation | Pre-unlock ceremony is metered (feature 057), but guidance quality is not yet measured for decision-completeness; reasoning usage is counted without per-decision attribution. | Decision-complete guidance: every refusal names the unmet obligation, the exact recovery action and the authoritative fact reference; no advisory fires without a next action. | Reasoning tokens per accepted task and the repeat-refusal rate fall together; advisory precision (§7.1) rises. |
| Cache-breaking churn | Stable-prefix caching exists host-side; which harness outputs invalidate the prompt cache is unmeasured. | Order session context stable-first (instructions, schemas) and volatile-last (task digest, live state); count cache-invalidation events per session. | Cached-input share rises and re-sent history falls at equal or better outcomes, verified through host usage reporting. |
| Coordination overhead | Existing worker/claim/lane machinery is substantial; productivity gain is unmeasured. | Prefer solo execution for dependent/small tasks; evaluate parallel work only for independent substantial subtasks. | Combined worker/coordinator/merge usage pays for itself through accepted throughput or lower total cost. |

### 6.1 Context delivery and resume

Build context around the next unresolved decision. Return task identity, intended outcome, active scope, changed/relevant files or symbols, applicable obligations, verification status, unresolved blockers and the next valid action. Include provenance/version references so facts can be checked without reopening whole documents.

Use progressive detail: concise result first, a bounded relevant excerpt next, full supporting evidence on demand. Budgets are configurable by task class and calibrated from total task cost; neither a fixed record count nor an arbitrary small token ceiling establishes optimality. Mandatory constraints and decisive error details must survive compression. If required evidence does not fit, expose an explicit continuation requirement rather than silently dropping it.

A fact earns its delivered tokens when it is **project-specific**, **expensive to guess wrong** and **used by the current task**. Generic knowledge the model can infer cheaply is the first content to drop; project-specific constraints with costly wrong guesses are the last. This value test ranks content for selection before any byte budget is applied, so selection is driven by value rather than by size alone.

Deduplication must account for what the current agent actually has. A reference can replace content already present in the usable context; after compaction, a fresh session, or a model/worker handoff, restore the necessary excerpt or digest. Do not treat a past consultation event as proof of current understanding. Summaries retain acceptance criteria, decisions and rationale, unsuccessful approaches, current candidate identity and outstanding work; stale summaries must not authorize actions.

The resume digest doubles as the **compaction anchor**. When the host compacts the conversation or a session boundary occurs, re-anchoring reads the digest rather than re-deriving facts from history, so recovery cost is bounded by digest size instead of session length. A digest that cannot serve this role is incomplete regardless of how small it is.

Keep full traces and verbose reports on disk with selective retrieval. This roadmap is a planning reference, not a new startup payload. Future implementation should not inject the entire roadmap or assessment into routine sessions.

### 6.2 Tools, prompts and deterministic work

Keep tool contracts concise, stable and unambiguous. Measure the entire serialized schema and actual request payload, not only description strings. If the host supports optional tool exposure, test whether task-scoped schemas save tokens without causing rediscovery or unavailable-tool failures. Avoid changing the schema set every turn if that increases churn or loses useful cache reuse.

Preserve stable instruction/schema prefixes where supported and isolate changing task facts. Verify cache behavior through observed usage; a hoped-for cache hit is not a saving. Caching may reduce billed cost and latency while leaving total logical input tokens unchanged.

Let code perform joins, state folds, path matching, repeated formatting and bounded log extraction. Combine independent reads where their results are needed together. Batch mutations only inside an authorized, recoverable lifecycle; fewer tool calls do not justify bypassing approval, freshness checks or verification.

Default output should name the result, reason and next action. Successful deterministic checks usually need a compact summary and an evidence reference. Failures need the first actionable cause, relevant context and a bounded log excerpt; retain the complete log for expansion. Removing detail that causes another troubleshooting turn can cost more than including it initially.

### 6.3 Verification, knowledge and recovery

Verification economy depends on sound evidence identity. An unchanged candidate with unchanged declared inputs and toolchain can reuse a valid result where policy permits. A changed relevant source/test/configuration/policy input invalidates affected evidence. Use conservative scope until selective invalidation is proven. Targeted checks can guide development, while required integration/release checks still run at their defined boundary.

Store evidence and machine state outside the changing input set to avoid invalidating every result with its own log. A test-process timeout must be distinguished from a behavioral failure; repeated retries require a relevant state change or a justified transient-error policy. Preserve the candidate when stopping an unproductive retry sequence.

Retrieve lessons by changed surface, contract and source version. Store concise, validated explanations with supporting tests or incident references. Promote frequently useful deterministic lessons into checks, then retire redundant prose through review. Measure avoided rediscovery and reduced repair cost; a growing knowledge index is not itself success.

### 6.4 Minimal product delivery

Package the demonstrated workflow after proving its economics. The current [AgentX package](../pyproject.toml) carries application dependencies; the [initializer](../scripts/omt/harnessc.py) provides a useful tier/template foundation. Define a minimal harness runtime/dependency manifest, install it in a non-AgentX repository, and make product-owned files, repository policy and user state explicit.

Use one short install → prepare → act → verify → resume guide and machine-readable diagnostics. Include onboarding tokens and maintainer intervention in the pilot cost. Ship only the compatibility, upgrade, recovery and support material needed for the first supported local profile. Broader packaging, hosted services, pricing and enterprise features remain secondary until the productivity benefit is repeatable.

## 7. Measurement and optimization protocol

### 7.1 Count the whole task

Use T3-4 as the measurement home. For a fixed corpus, let A be the number of independently accepted task outcomes, counted once per task run. Failed attempts and retries contribute usage but never inflate A.

```text
tokens per accepted task = sum(all request input + all generated tokens) / A
accepted throughput     = A / elapsed execution time
money per accepted task = sum(actual cost across all attempts) / A
```

Request input includes instructions, schemas, conversation replay and tool results as actually delivered on each model call. Repeated text counts each time it is supplied. Report cached and uncached input separately; do not add cached input a second time to a total that already includes it. Count generated/reasoning usage according to the runtime's reporting contract without double-counting reasoning already included in output totals. Missing usage is unknown, not zero.

Decompose the primary metric for diagnosis: **tokens per accepted task = (tokens per attempt) × (attempts per accepted task)**. Context economy moves the first factor; guidance quality, truthful prediction and first-pass correctness move the second. Report both factors beside the aggregate. An optimization that cheapens each attempt while inducing more attempts can be a net regression the aggregate alone would hide, and the two factors are optimized by different mechanisms (§6).

When the runtime does not expose request-level usage, run the defined proxy variant instead of stalling the program. Instrument delivered-payload bytes (serialized instructions and schemas, tool results, guidance responses), model turn counts and tool-call counts, and report them as labeled proxies, never as tokens. Calibrate the proxies against real usage on any run where both are available, and state the observed calibration gap. The proxy variant is sufficient for M0 baselines and for the trivially-safe fast lane (§7.2); promoting a mechanism that can remove information still requires request-level usage or an explicit, recorded justification for the exception.

Include coordinator/helper-agent requests, summary/compaction calls where observable, unsuccessful branches, verification diagnosis and recovery. A tool log stored on disk consumes no model tokens until retrieved; its repeated inclusion in later requests can consume tokens repeatedly. Local subprocess time and disk reads are measured separately. If A is zero, report no finite accepted-task unit cost.

| Measure | What to report |
|---|---|
| **Primary: tokens per accepted task** | Full input/output usage, task-class breakdown, workload-weighted aggregate, and p50/p95 where sample size permits. |
| **Accepted throughput** | Correct tasks per elapsed time; report total latency distribution as well. |
| **Quality constraints** | Independent acceptance rate, regressions, all enumerated critical refusal cases, and valid positive controls. |
| **Request fidelity** | Scope-drift advisories triggered; acceptance cases traced to the request extract; deviations and user amendments visible at completion; clarification round trips per task. |
| **Guidance sufficiency** | Refusals resolved without a repeat refusal for the same cause; rediscovery events (the same artifact re-read within a short window); next-action validity — whether the agent's first action after a guidance response makes progress. |
| **Advisory precision** | Advisories fired, advisories acted upon, and precision (acted-upon ÷ fired) by advisory class. Low-precision advisories train agents to ignore signals and are demotion candidates under the same ablation rule as optional mechanisms (§7.4). |
| **Completion review cost** | Human time to accept or reject a completion report, and report length in tokens. The done-promise is only delivered if review is cheaper than re-doing the work. |
| **Reasoning share** | Reasoning/thinking usage per accepted task where the runtime reports it, read next to guidance-sufficiency events to expose deliberation inflation (§6). |
| **Human burden** | Intervention minutes, unnecessary clarifications/overrides, and recovery effort. |
| **Input composition** | Actual schema/startup, history, retrieved evidence, repeated context and failure-diagnostic contributions; label attribution estimates. |
| **Waste indicators** | Duplicate delivered content, unnecessary round trips, verification reruns without relevant change, unchanged-failure retries and resume rereads. |
| **Cache and spend** | Cached/uncached input, cache-invalidation events per session, cache behavior and actual billed cost using the run's recorded prices; distinguish savings from token-volume reduction. |
| **Maintenance cost** | Tokens spent implementing, testing and maintaining the optimization; human effort separately. |
| **State/runtime overhead** | Local decision latency, subprocess time, bytes parsed and snapshot/index behavior; not a substitute for model-token accounting. |

### 7.2 Controlled experiments

Start with local bug fix and interrupted/resumed task for instrumentation. Expand to five solo task classes: local bug fix, cross-layer change, major feature, harness repair and resume. Treat concurrent conflict as a separate sixth cohort after its execution boundary is ready.

The harness's own development is the **always-on dogfood lane**. From M0 onward, every real harness task — features, fixes, repairs and resumes — is instrumented as continuous, zero-recruitment data, dominated by the harness-repair class. Dogfood records never replace controlled comparisons: the maintainer is not an independent user, and policy evolves mid-corpus. They supply what curated benchmarks lack — real frequency data on which guidance is actually consulted, which refusals repeat, and which context is re-read — and those frequencies feed the ranking in §7.3.

Tier the experiments so the cost of a decision matches its risk. **Tier 0 (smoke):** two tasks × two conditions × two or three attempts, hours of work — sufficient for instrumentation sanity checks and for the trivially-safe fast lane: changes that provably preserve information (a byte cap with explicit continuation, deduplication of identical consecutive reads, summary-first output with the full result retained on disk). **Tier 1 (pilot):** the sizes specified below — required for any mechanism that can hide facts or change obligations (schema reduction, context selection, tier changes, guidance rewrites). **Tier 2 (expanded):** multiple independent tasks per class plus held-out non-AgentX tasks — required before any general benefit claim. Count the experiments' own token and effort cost inside the maintenance-cost measure and cap it; an experiment program that consumes the savings it exists to find is itself a regression.

For an initial pilot, use at least five independent attempts per task and condition: 25 attempts per five-task solo condition, or 30 including the separate concurrent cohort. This is a pilot size, not proof of rare-failure reliability. Pin candidate/content, task definitions, model/runtime/toolchain, machine and independent acceptance cases. Randomize matched task order, separate cold/warm context and cache cases, and prevent earlier solutions leaking into later attempts.

Compare current behavior with one optimization, then the combined configuration. Change one mechanism at a time to identify its contribution. Hold the model configuration fixed initially; any later model/effort-routing comparison is a separate experiment with the same acceptance criteria and all retry costs included.

**Required conditions:** A = native OpenCode with normal repository instructions and host permissions; B = current Meta Harness; C = B plus one refinement; D = combined retained refinements after individual comparisons. Use disposable copies, equivalent task information and the same model/effort/toolchain where supported. Report capability differences explicitly: native task completion is an economic baseline, not proof that native OpenCode enforces every OMT obligation. Keep a separate refusal/control matrix for each claimed profile. Other harnesses are optional secondary comparators and cannot support causal claims about OMT if model/runtime configuration also changes.

Five repeats of one task per class mostly measure run variability, not workload diversity. Expand to multiple independent tasks per class and reserve held-out tasks from non-AgentX repositories before claiming general benefit. Freeze acceptance cases before execution, retain failures/timeouts in denominators, specify a retry/cost cap, and report uncertainty rather than treating an arbitrary percentage as significant. Log any human amendment of the acceptance criteria. A passing test suite and a maintainer's satisfaction are related observations, not interchangeable acceptance measures.

Ablation means disabling one optional advisory/formatting behavior in a disposable benchmark or comparing existing supported tiers. Keep the expected correctness and policy constraints fixed; a tier with fewer guarantees is labeled as a different capability and cannot establish an equivalent cheaper verified result. Do not silently disable live mandatory gates to improve numbers.

### 7.3 Promotion and stopping rules

Promote an optimization only when accepted-task token cost improves reproducibly, critical seeded cases and positive controls still pass, and acceptance/regression outcomes show no unexplained deterioration. Report latency and human-burden changes; fewer tokens with materially worse throughput is an explicit tradeoff. If uncertainty overlaps no improvement, gather a larger sample or leave the optimization experimental.

**Initial stretch targets, to recalibrate after M0:** at least 20% lower total tokens per accepted routine/resumed task, 40% less duplicated delivered context, and 30% fewer harness-only model round trips. These are proposed targets, not measured results or automatic reasons to compress necessary context. Total task tokens and accepted outcomes decide; proxy targets alone cannot qualify an optimization.

Rank work using measured frequency and net token savings per task, confidence in preserving quality, implementation effort, and recurring maintenance cost. For positive per-task savings, estimate token payback as implementation/validation token cost divided by saved tokens per future task; report the assumed task volume and human effort separately. Prefer removing a frequently repeated cost over adding a complex subsystem for an occasional small saving.

Set a bounded experiment budget and retry policy, stated in tokens and human hours before Tier 1 begins; a matrix whose own cost approaches the savings it can plausibly find is reshaped — fewer conditions or cheaper task instances — not funded. Stop tuning when further savings are within measurement noise, required evidence is lost, recovery cost rises, or likely future usage cannot repay the added complexity. Preserve the best measured configuration and its limitations; avoid an endless optimization loop.

### 7.4 Standing economy disciplines

Two ratchets erode token economy silently; each gets a standing rule rather than a one-time fix.

- **Budget ratchet.** A delivered-context budget (nav records, index bytes, tool or argument descriptions) may be raised only with a recorded, measured justification: the observed delivered payloads that needed the room and the task classes that consume it. The 64,000 → 65,536 nav-index raise during feature 089 (§3.5) is the template case — correct as the repair of an exceeded budget, wrong as a trend. Index growth is a recurring cost even when no single record is large; stale records retire rather than accumulate, and every raise is logged with its justification.
- **Net-zero ceremony.** A new mandatory or advisory mechanism must retire, absorb or demote an equivalent existing one. The compile-enforced gate budget (`@budget gates max=12` with skip-frequency retirement candidates, [feature 057](../.meta/software_development_process/2.requirements/features/feature_057.gate_budget_ceremony_meter/FEATURE.md)) is both the precedent and the enforcement point. The same discipline extends to nav records (per-record byte caps with explicit continuation, stale-record retirement) and to advisories (precision-based demotion, §7.1). The ceremony meter's existing medians are the baseline a new mechanism must not worsen.

## 8. Release gates and evidence lifecycle

These gates constrain production claims and unsafe reuse. They do not replace the productivity promotion criteria in §7 or require every qualification task to finish before a read-only context optimization can be benchmarked. A product release must demonstrate both the claimed guarantees and useful accepted-task economics.

Use `reported → reproduced → fixed → qualified` with explicit scope. A checked-in reproducer demonstrates the defect; a passing regression at a named revision establishes a fix for that case; qualification adds the claimed runtime boundary and complete release matrix. Local temporary probes below are not retained product qualification tests.

| Required gate | Verified solo | Managed addition | Decisive evidence |
|---|---|---|---|
| Named support profile | Required | Coordinator/worker topology and shared storage added. | Runtime/adapter/toolchain/OS/filesystem/policy/state identity. |
| I01 mutation mediation | Required | Claim, generation, scope and worktree identity on every managed effect. | Real-adapter operation/path matrix including multi-file refusal. |
| I02 critical fail-closed | Required | Coordination/journal failure included. | Missing/malformed/incompatible authority and subprocess fault cases. |
| I03 obligation composition | Required | Managed gate remains independent of test/phase approvals. | Pairwise and reordered gate cases plus positive controls. |
| I04 truthful completion | Required | Coordinator verifies real combined candidate. | Failed/empty/stale/missing-check verifier cases never produce verified Done. |
| I05 durable acknowledgment | Required for authoritative state | Atomic competing-writer commit/event/idempotency recovery. | Actual process interruption and failed-write tests at each persistence boundary. |
| I06 current evidence | Required | Upstream and integration-base changes invalidate dependent acceptance. | Candidate/input/policy/toolchain mutation tests and appropriate reuse controls. |
| I07 truthful prediction | Unknown remains unknown | Managed observation uses a consistent generation. | Preflight/enforcement equivalence for the same available facts. |
| I08 preserved work | Required | Other workers' candidates preserved too. | Intervening user edit survives failed refactor/recovery. |
| I09 ownership isolation | Claimed session/workspace semantics required | Full task/actor/claim/coordination isolation. | Cross-session/cross-workspace/stale-owner refusal. |
| I10 idempotency | Required where retries promise it | Required for every authoritative managed mutation. | Same-ID same-payload replay, conflicting payload refusal, crash retry and retention-boundary cases. |
| Product lifecycle | Required | Shared-state/worktree migration covered. | Artifact-based install, upgrade, recovery and support diagnostics in a disposable repository. |
| Required test suite | No required failure | Same plus managed stress/integration demo. | Immutable candidate-specific result report. |

Each release report must name capability, candidate revision plus dirty/untracked input identity, support profile, policy/state/evidence schema, required findings/checks, actual results, evidence locations and limitations. Missing, stale or failed required evidence yields `not_qualified`. A waiver is reported as a waiver and does not silently count as a verified pass.

Degraded behavior is part of this contract: missing policy/state permits bounded read-only diagnosis but refuses affected authority; optional KB failure is labeled and handled independently; verifier failure preserves the candidate but prevents acceptance; stale evidence requires re-verification; failed acknowledgment requires command reconciliation before retry.

## 9. Backlog reconciliation and deferrals

Keep [meta_harness_8](../.projects/meta/meta_harness_8/PROJECT.md) as the existing implementation home. This user-requested roadmap revision proposes productivity-first sequencing; update the canonical execution plan explicitly when scheduling work. Do not infer that the project file or its shipped feature records have already changed.

- Preserve T4-1/T4-2/T4-3 and T5-1…T5-7 shipped records. Add residual acceptance work tied to F/C identifiers and exact reproductions.
- **Lead with the compiler baseline, small truth fixes and T3-4 measurement; then T3-3 resume and the T3-5 preparation slice.** Use F10/F11 to make responses truthful, relevant and bounded. Pilot installation early, then prioritize verified reuse and T3-6 knowledge by measured savings. Instrument the harness's own tasks as the dogfood lane from the first slice (§7.2) and extend feature 057's ceremony meter rather than building a second instrument.
- T2-6 conventions/lints and T2-7 scaffolds remain useful maintenance; coordinate with the already-started feature 089 work. They do not close the current release blockers.
- T3-7 budget suggestions should target actual repeated model payloads. Internal file-byte reductions alone do not establish token savings.
- Keep task prep's existing vertical slice; finish truthful snapshot semantics before broad tool exposure.
- Repair the unindexed workflow warning and stale Quick Start/resume pointers as small, separate changes.
- Use the bounded experiment loop in §7; avoid repeated broad reviews that produce no implemented, measured productivity gain.

Defer broad release packaging until the smallest workflow demonstrates value; a minimal pilot artifact belongs at M1. Defer additional adapters, expanded managed concurrency, distributed execution, an unrestricted policy/query language, mandatory new consultation gates, automatic policy self-modification, a hosted control plane and speculative commercial features. Reconsider each only when observed customer need and expected accepted-task savings or throughput justify its overhead and the relevant capability can be qualified.

## 10. Risks and decisions still to make

| Decision | Recommended starting position | Evidence needed before expanding |
|---|---|---|
| Context budget | Task-scoped summary with relevant excerpts and explicit continuation. | Lower total accepted-task tokens, with critical facts retained and expansion cost included. |
| Done authority and drift policy | Request-provenance acceptance with advisory drift signals and user-terms completion (§4.6). | Measured drift and rework reduction without added clarification round trips; user amendments logged and rare. |
| Tool/schema exposure | Concise stable core; optional task-specific exposure only where supported. | Actual request token/cache measurements plus successful tool discovery. |
| Optimization granularity | One measured mechanism at a time; combine only after individual comparison. | Reproducible benefit beyond noise and no hidden quality/repair regression. |
| Agent parallelism | Solo for routine or dependent work; bounded independent subtasks only when justified. | All-worker/coordinator token totals, integration cost, and accepted-throughput comparison. |
| First supported adapter/profile | Existing OpenCode integration, one local profile and one writer. | Real operation coverage and exact runtime/SDK compatibility. |
| Arbitrary shell mutation | Do not claim verified mediation without a qualified execution boundary. | Broker/sandbox or demonstrably complete mediation of the permitted shell/process behavior. |
| Staging in first solo release | Enable only with owned finish/verify/consume semantics; otherwise exclude from the verified profile. | Interrupted, stale, cross-task and failed-stage cases. |
| State persistence design | Extend the existing local design first against a concrete commit/recovery contract. | Full fault campaign; choose a different store only if it simplifies satisfying the contract, through an explicit design decision. |
| Evidence reuse | Conservative declared input closure. | Dependency invalidation tests proving narrower reuse sound. |
| Product packaging | Minimal pilot artifact at M1; supported release artifact at M5. | Non-maintainer activation/repeat use, clean non-AgentX install/upgrade/rollback, and onboarding/support cost. |
| Small-task lane and break-even | Task-type-differentiated light lanes modeled on the bug_fix/test fast path (feature 054); publish the measured break-even task size. | Fixed-cost decomposition per task class (§1); break-even confirmed on non-AgentX tasks before any "cheaper for everything" claim. |
| Advisory precision policy | Advisory-only signals, precision-metered; low-precision advisories are demoted or retired under the net-zero rule (§7.4). | Acted-upon rate and true-drift catch rate on seeded out-of-scope work; no rise in missed real drift after demotion. |
| Claims and business model | Useful local preview, then qualified solo capability. | Repeat external usage and measured value before pricing/hosted expansion. |

No calendar estimate is asserted. The milestone exits above are the scheduling units; estimate each implementation slice after its reproducer and adapter/storage scope are concrete.

## 11. Validation history

### Original roadmap review: compiler and source inspection

`uv run scripts/omt/harnessc.py check --verify-projections` passed with 263 records and zero errors. Warning: `.workflows/meta_harness/meta_harness_development_self_evaluation.md` is still absent from its subject manifest. It remains a small catalog repair, not evidence that generated projections failed.

Source comparison against the original expansion baseline `4a95c911e6113f056b00b53b9b546f7fd0697d51` found substantial additions to net state/CLI, locking/workspace helpers, and tests. The old no-lock conclusion was therefore not carried forward. Current source checks confirmed the original completion default, before-hook catch, test-gate stop, stage/receipt compatibility behavior and best-effort TS IO remain.

### Original roadmap review: local reproductions

Command: `bun /tmp/meta-harness-roadmap-probes.ts`. Temporary output: `/tmp/meta-harness-roadmap-probes.json`. The script invokes real repository modules, copies policy IR into temporary roots, redirects ledger/net paths, and substitutes subprocess responses. It does not execute an unauthorized edit, run a malicious process, or modify real authorization records.

| Case | Observed result |
|---|---|
| F05: failed verifier, exit 1, empty stdout | Successful completion message, completion record, and Done phase. |
| F05 control: explicit `ok:false` and failing test | Refusal; no completion or Done. |
| F05 control: exit 0 and explicit `ok:true` | Completion and Done under the current contract. This is a control, not proof of the proposed richer evidence contract. |
| F03: approved test edit with thought-bearing fixture | Chain ends at `g.tests`, `stop:true`, zero net subprocess calls. |
| F02: malformed net subprocess output | Before-hook returns normally and logs a failing-open JSON error. |
| F09: ledger parent is a regular file | Append returns without error; no record persisted. |

These files are temporary review artifacts, not a shipped regression suite. Retaining their scenarios as repository tests with positive controls belongs to the supporting reliability lane in §5. New concurrency gaps C1–C5 are source-based observations; no exhaustive race/crash or real-adapter campaign was performed in the original review.

### Original roadmap review: suite and document checks

`uv run pytest` completed with **2,167 passed, 1 failed, 10 warnings in 580.12 seconds** (2,168 collected). The failure was `tests/scripts/omt/test_omt_live_opencode_guards.py::test_plugins_load_and_tools_execute`: the `opencode run --format json` subprocess exceeded its 240-second timeout. The other live smoke passed. Log: `/tmp/meta-harness-roadmap-pytest.log`.

The historical feature-059 budget-pin failure did not recur. The live timeout also appears in earlier assessments, but this run does not establish its root cause or prove a plugin-load defect. It does leave that runtime qualification check unsuccessful. Existing net transaction/claim/workspace/capacity/lane/recovery/dependency tests passed; their scope limits in §§3.2–3.4 still apply.

The suite ran in the shared working tree while unrelated project/scaffold edits appeared, not in a frozen release checkout. No implementation files were changed by this review, and no failing check was repaired or excluded to improve the result. Temporary runtime artifacts may be refreshed by the normal tests. Historical suite counts in the input reports are not substituted for this result.

Document validation: local Markdown links resolve, fenced code blocks are balanced, headings are unique, and whitespace checks pass. The sole authored workspace deliverable is this roadmap; both source assessments and unrelated changes are preserved.

### Productivity priority revision — 2026-09-13

Updated the objective, milestone order, immediate queue, optimization mechanisms, request-level token accounting, controlled experiments, promotion/payback rules and product deferrals. Added explicit separation of total tokens, cached-input spend and local runtime overhead. Numerical savings targets are proposed experiments, not achieved results.

This update changes only the roadmap. Concurrent policy/compiler/project edits visible at revision start were left untouched. The previous compiler/probe/suite results above are historical validation of the earlier review, not fresh checks of that evolving source. No application suite or live-runtime probe was repeated for this prose-only change. Local-link, heading, code-fence and whitespace checks validate the updated document.

### Product refinement review — 2026-09-13

Added a critical assessment of the plan itself, seven sourced reference comparisons, a narrow first workflow, explicit adapter boundaries, an early adoption experiment, native-runtime benchmark controls, held-out task requirements and prioritized implementation packages. Historical records remain labeled; no shipped feature was reopened or declared fixed by this edit.

Fresh checks: the compiler initially failed on nav budget/projection drift, then passed after concurrent feature-089 changes (**265 records, zero errors**, one existing workflow-index warning). Isolated probes reproduced F02/F03/F05/F09 with the controls described in §3.5. Their subprocess responses were synthetic; no live guarded edit or crash campaign was performed by those probes.

The repository suite and final document checks are recorded below after completion. Only this roadmap is authored by the review; concurrent implementation, test, policy and projection changes are preserved. This shared checkout cannot serve as a frozen release candidate.

### Guidance-economy refinement — 2026-09-13

Added the request-fidelity contract (§4.6): verbatim request capture in the task digest, drift signals with explicit re-anchoring, and completion reporting in user terms. Extended the Task contract with request provenance and a Completion report contract (§4.2), and the user journey accordingly (§4.1). Added a usage-unavailable proxy ladder so the token-economy program does not stall when request-level usage is unavailable (§7.1), request-fidelity and guidance-sufficiency measures, tiered experiments (smoke/pilot/expanded) with a trivially-safe fast lane (§7.2, §5.1 item 3b), a request-drift cost row (§6), a done-authority decision row (§10), and request-extract pinning in the first measurement slice (§5.2). These are proposals grounded in the inspected mechanisms; none is implemented or measured by this edit.

Verification for this edit: source spot-checks confirmed the F05 completion default (`.nothrow()` with an empty-stdout `{"ok":true}` fallback in `phase_gate.ts`), the F09 best-effort append (`appendJsonl` in `omt_shared.ts`), the F02 fail-open before-hook (`omt_enforcer.ts`), and the F11 record-count-only nav cap (`NAV_MAX_RECORDS = 25`). Document checks pass on the updated file: local links resolve, code fences balanced, all 40 headings unique, no trailing whitespace or tabs. `harnessc check --verify-projections` passes at 265 records with zero errors in the observed working tree. Following the precedent of the prose-only productivity revision, the application suite was not rerun for this markdown-only change; no source, test, policy or projection file was modified, and concurrent working-tree changes are preserved.

### Productivity-economy deepening — 2026-09-13

Added the fixed-versus-marginal cost structure, task-size break-even and attempt-cost decomposition (§1, §7.1); harness-assembled completion outcomes, a deviation taxonomy, investigation-task acceptance and bounded review cost (§4.6); deliberation-inflation and cache-churn cost rows, the context value test and the digest-as-compaction-anchor rule (§6, §6.1); advisory-precision, completion-review-cost and reasoning-share measures, plus cache-invalidation events (§7.1); the always-on dogfood measurement lane (§7.2, §5.1 item 3, §9); a pre-Tier-1 experiment-budget statement (§7.3); standing economy disciplines — the budget ratchet and net-zero ceremony (§7.4) — and two decision rows (§10). The new disciplines are grounded in the shipped feature 054 fast path and feature 057 gate budget/ceremony meter rather than proposing new mechanisms; their FEATURE.md records were read for this edit. This is a markdown-only planning change: no source, test, policy or projection file was modified, and no benchmark, probe or suite run was performed. Document checks pass on the updated file: local links resolve, code fences balanced, all 42 headings unique, no trailing whitespace or tabs. Concurrent working-tree changes are preserved.

## 12. Source and test map

| Area | Primary evidence |
|---|---|
| Original diagnosis and revised acceptance | [Original](META_HARNESS_PRODUCTION_READINESS.md), [revision](META_HARNESS_PRODUCTION_READINESS_REVISED.md) |
| Canonical policy and compiler/initializer | [Policy](../.meta/META_HARNESS.omt), [compiler](../scripts/omt/harnessc.py) |
| Approved backlog and session history | [Project](../.projects/meta/meta_harness_8/PROJECT.md), [state log](../.projects/meta/meta_harness_8/CURRENT_STATE.md) |
| Completion behavior | [TypeScript completion](../.opencode/lib/enforcer/phase_gate.ts), [Python verifier](../scripts/omt/tdd/gates.py), [behavioral tests](../tests/scripts/omt/test_completion_hardening.py) |
| Transaction and idempotency | [State](../scripts/omt/net/state.py), [lock/index](../scripts/omt/net/lock.py), [transaction tests](../tests/scripts/omt/test_net_transaction_authority.py) |
| Claims/workspaces/capacity | [Claim tests](../tests/scripts/omt/test_net_task_claim_generation.py), [workspace helper](../scripts/omt/net/workspace.py), [workspace tests](../tests/scripts/omt/test_net_worktree_isolation.py), [capacity tests](../tests/scripts/omt/test_net_two_worker_capacity_scope.py) |
| Verification/integration/dependencies | [Lane tests](../tests/scripts/omt/test_net_verification_integration_lane.py), [dependency tests](../tests/scripts/omt/test_net_evidence_dependency.py) |
| Recovery evidence and its limits | [Journal/recovery tests](../tests/scripts/omt/test_net_recovery_journal.py), especially manually constructed marker cases and direct generation handoff |
| Receipt/live-runtime scope | [Contract receipt test](../tests/scripts/omt/test_omt_harness_e2e.py), [live OpenCode tests](../tests/scripts/omt/test_omt_live_opencode_guards.py) |
| Packaging/runtime identities | [AgentX package](../pyproject.toml), [plugin dependencies](../.opencode/package.json) |
| Current harness comparison | Primary documentation linked alongside each claim in §2.2; documentation accessed 2026-09-13, with no comparative runtime benchmark performed. |

The roadmap is grounded in this repository, the two supplied assessments and the cited primary documentation. Product recommendations are inferences and testable hypotheses; no external certification, market demand or comparative performance advantage is established.
