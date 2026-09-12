# META HARNESS: effectiveness, efficiency, and production readiness

**Date:** 2026-09-12

**Scope:** the meta harness in this working tree, including its compiler, OpenCode plugins, state, verification, knowledge mechanisms, and consolidated roadmap.

**Original assessment reference:** `d08a0041ab01b5901efb062a87bd35f8f38acfd5`, plus the uncommitted work described in §2.

**Document expansion reference:** `4a95c911e6113f056b00b53b9b546f7fd0697d51`; working tree clean before this update. Original probes and suite results remain historical evidence, not newly reproduced results at this revision. See §10.1 for this update's validation.

**Status:** assessment and proposed improvements; no harness implementation changes made by this review.

## 1. Decision

META HARNESS is a substantial, useful development scaffold, with a good foundation for a production tool. It is **not yet ready to provide dependable enforcement, verified completion, or managed concurrent execution guarantees**. Its strongest demonstrated capabilities are organizing development, generating consistent policy artifacts, and detecting many known regressions. Its weakest demonstrated capabilities are enforcing policy across failure conditions and proving that its process overhead improves completed work.

The highest-value next investment is a reliability and measurement program. Close demonstrated enforcement and completion gaps, establish cost per independently verified task, and then expand the existing preparation and knowledge features. More gates, smaller documentation files, or more completed harness features do not by themselves demonstrate progress toward the user's development goals.

The recommended release scope is initially **one trusted operator, one supported local runtime, one active writer, and explicit verification boundaries**. Managed concurrency should remain a separately qualified capability. The existing `meta_harness_8` T5 plan already has much of the correct concurrency design; it needs implementation and failure testing before its guarantees can be advertised.

### What to preserve

- The canonical `.omt` policy and generated projections, with reproducibility checks.
- Modular gate implementations, actionable refusal messages, and preflight.
- Lightweight treatment of small tasks, existing installation tiers, and bounded context delivery.
- Behavioral tests, the runtime compatibility canary, feature-scoped TDD, and test-state isolation mechanisms.
- The direction of staged changes and content-bound verification receipts.
- Explicit task identity, resource modeling, knowledge retention, and a consolidated project backlog.

### What to change first

1. Make critical policy and verification failures refuse the operation reliably.
2. Make independent gates compose correctly and cover the actual mutation interfaces.
3. Separate task progress, authorization, consultation, and verification evidence.
4. Turn staging and completion into enforced, content-bound lifecycles.
5. Measure outcomes and total task cost before adding more process machinery.

### The next level: a task contract with verifiable acceptance

Make the unit of value **a user-requested change accepted against explicit behavior**, rather than a completed phase or a satisfied gate. At preparation, bind the request to a small task contract: intended outcome, scope, observable acceptance cases, required verification, and supported execution profile. At acceptance, report which cases passed against which candidate, what remains unknown, and any waiver. For a routine bug fix this can be one compact record; it need not introduce a design document or another tool call.

The compiler, gates, ledger and knowledge mechanisms should cooperate around this contract. A phase remains useful progress metadata; it does not become the acceptance oracle. Changes in scope must refresh affected obligations and verification targets. Externally consequential actions such as publication retain their own authority even when implementation is accepted.

This creates three distinct product capabilities, each requiring its own evidence:

| Capability | Minimum defensible claim | Qualification boundary |
|---|---|---|
| Development assistance | Prepares relevant context, explains obligations, preserves progress. | May operate on an unintegrated host, but cannot claim its actions were mediated. |
| Verified solo execution | Supported mutations are mediated and accepted output has current verification evidence. | One qualified adapter, workspace, active writer and runtime combination. |
| Managed concurrent execution | Ownership, persistence and integration remain correct under competing workers and failures. | Adds transaction, generation, isolation and combined-candidate qualification. |

Installation tiers describe enabled features; these capability profiles describe demonstrated guarantees. Installing Tier 3 must not automatically confer the managed-concurrency claim. The near-term objective is verified solo execution. The architecture below makes that useful without requiring the entire concurrent platform first.

## 2. Evidence and limits

This assessment combines source inspection, the current canonical policy and project documents, compiler/projection verification, an existing full-suite run, and isolated behavioral probes of the actual TypeScript modules. External references support specific design recommendations; they are not evidence that this repository conforms to a standard.

The current host does not expose the `omt_*` tools. Navigation was performed by invoking the repository's `omt_nav` plugin directly through Bun. This establishes a host integration limitation for this session, not that the plugins fail to load in OpenCode.

The isolated probes used temporary roots and synthetic ledgers under `/tmp`; they called the real hook/evaluator implementations but used synthetic tool arguments and a stubbed subprocess interface. They **did not execute unauthorized edits, modify real authorization records, or prove an exploit through a live agent runtime**. The distinction matters: these probes demonstrate implementation decisions, while live adapter coverage still requires qualification.

During the original assessment, the working tree was already dirty. Workflow/compiler work for feature 076 was present at review start, and further project/testing artifacts appeared during that review. Those observations are a working-tree assessment, not an immutable release audit. The subsequent document expansion started from the clean revision named above. Historical counts in project logs are treated as historical claims, not new measurements.

### Original verification record

| Check | Result and interpretation |
|---|---|
| `uv run scripts/omt/harnessc.py check` | Passed: 263 records, zero errors; one workflow catalog warning. |
| `uv run scripts/omt/harnessc.py check --verify-projections` | Passed with the same warning; generated projections match the inspected canonical policy. |
| Isolated Bun probes | Reproduced the behaviors in §5 and Appendix A. No production state mutated by the probes. |
| `uv run pytest` | 2,080 passed, 2 failed, 6 warnings in 552.04 seconds; details in §10. |
| Task-level efficiency benchmark | Not run. No new claim of reduced task tokens, latency, or defect rate is made. |
| Multi-process race/crash tests | Not run in this review. Transaction and rollback risks are source-based findings. |

Compiler warning: `.workflows/meta_harness/meta_harness_development_self_evaluation.md` is not listed in its subject manifest. The current workflow changes therefore improve checking without fully closing catalog drift.

**Evidence discipline for follow-up work:** retain stable F01–F12 finding IDs. Each closure should attach the affected revision/content identity, reproducible fixture or command, expected and actual outcome, evidence scope, and remaining limitations. Use explicit states: `reported`, `reproduced`, `fixed`, and `qualified`. A code change can establish `fixed` only with a passing regression case; `qualified` additionally requires the claimed runtime boundary. New design proposals in §§6–8 are recommendations, not additional reproduced defects. The temporary probes described in Appendix A have no retained fixture path in this document, so preserving executable reproductions is itself an outstanding deliverable.

## 3. How effectively the harness serves its goals

The goals below are derived from the policy, methodology, earlier improvement assessment, and consolidated backlog. They should become an explicit, queryable product contract. Navigation queries for `goal`, `production`, and `efficiency` returned no results in the inspected index.

| Goal | Existing mechanism | Assessment | Outcome that should decide success |
|---|---|---|---|
| Deliver correct changes | Phases, artifacts, TDD, architecture checks, completion | Useful discipline; completion can still report success without successful verification. | Independently checked behavior, regression rate, accepted integrated changes. |
| Reduce agent effort | Navigation, budgets, fast paths, preflight, consultation reuse | Good local optimizations; end-to-end benefit remains unmeasured. | Total cost and elapsed time per accepted task, including failures and recovery. |
| Preserve useful knowledge | Inline thoughts, KB indexes, consult records, review | Records access and retains rationale; relevance and freshness are incompletely tied to changed content. | Retrieval usefulness and fewer repeated mistakes, at lower rediscovery cost. |
| Prevent unauthorized or invalid work | Deny rules, protected paths, ordered gates, logged overrides | Effective for many expected calls; coverage, composition, and failure handling have demonstrated gaps. | Forbidden operations consistently refused across supported adapters and fault cases. |
| Make state and recovery understandable | Ledger, status/preflight, projects, task menu | Strong visibility foundation; progress and temporary authority remain partly conflated. | Accurate resume state, bounded recovery effort, no false success after persistence failure. |
| Coordinate concurrent work | Petri net, resources, revisions, named bindings | Useful planning model; current persistence is not a complete transaction authority. | No double claim, lost update, stale publication, or acceptance of incompatible combined work. |
| Evolve and reuse the harness | DSL compiler, tiered initializer, workflow catalog, tests | Substantial capability; production packaging and independent release qualification remain incomplete. | Repeatable clean installation, safe upgrade/recovery, verified compatibility and policy equivalence. |

The key effectiveness gap is **evidence quality**. A phase declaration proves that a declaration happened. A consultation receipt proves an access event. A source-string assertion proves that text exists. A net marking represents a modeled state. Each is useful, but none independently proves that the user's requested behavior works in the integrated result.

Sources: [canonical policy](../.meta/META_HARNESS.omt), [earlier assessment](meta/improvement002/IMPROVEMENT_OPTIONS.md), [consolidated project](../.projects/meta/meta_harness_8/PROJECT.md).

## 4. Efficiency: what is measured and what is missing

### 4.1 Current size budget snapshot

| Budget | Measured / cap | Utilization | Remaining |
|---|---:|---:|---:|
| Generated `AGENTS.md` | 2,918 / 2,944 bytes | 99.1% | 26 bytes |
| Tool description payloads, labeled `tool_schemas` | 1,778 / 1,792 bytes | 99.2% | 14 bytes |
| Argument description text, labeled `tool_args` | 2,284 / 2,304 bytes | 99.1% | 20 bytes |
| Navigation index | 63,929 / 64,000 bytes | 99.9% | 71 bytes |
| Runtime policy IR | 20,002 / 20,480 bytes | 97.7% | 478 bytes |
| Startup `WORK.md` | 5,653 / 8,192 bytes | 69.0% | 2,539 bytes |
| Gate count | 10 / 12 | 83.3% | 2 gates |

These limits curb growth, but the units represent different costs. `measure_budgets()` measures tool and argument **description text**, not the complete serialized schemas delivered to the model. The index and IR are internal files; their entire size is not automatically charged to every model request. Startup text, actual tool schemas, selected results, injected context, cached input, and repeated reads should be measured separately.

At this level of headroom, arbitrary byte ceilings can influence architecture: [preflight](../.opencode/lib/enforcer/preflight.ts) explicitly keeps clearing actions in a TypeScript map partly because the nav index lacked room. That duplicates policy explanations to satisfy a representation budget. Prefer limits grounded in actual runtime costs; allow a justified internal-schema expansion when it reduces duplicated logic or false decisions.

### 4.2 The ceremony meter measures a narrow proxy

`ceremony_stats()` counts selected ledger event kinds **before the first phase record in a session**. It excludes later repair loops, most ordinary tool traffic, verification time, and sessions that never reach a phase declaration. Declaring a phase earlier can improve this metric without saving any actual effort. Skip-to-gate attribution is heuristic, and its compiler-side reader reads only the hot ledger, so the seven-day view can omit rotated events.

Likewise, a gate with zero recorded skips is not necessarily useless: it may be effective, unused, or absent from the measured traffic. A frequently skipped gate may be overbroad or simply encountered more often. Neither count alone is an adequate retirement criterion.

Source: [compiler metrics](../scripts/omt/harnessc.py), `measure_budgets`, `ceremony_stats`, `gate_skip_counts`, `_read_repo_ledger_records`.

### 4.3 A capped hot ledger does not bound the read workload

At inspection, the latest archive contained **428,997 bytes / 1,006 records**, and the hot ledger contained **7,506 bytes / 14 records**. `readLedger()` reads both: **436,503 bytes / 1,020 records per call**, before parsing and subsequent scans. The 64 KiB hot-file cap does not bound this combined read because rotations append to the same monthly archive.

`loadIr()` also reads and parses afresh. Several gate helpers load the IR or ledger independently during one operation. The resulting opportunity is to use one consistent snapshot per operation, with measured caching and invalidation, rather than optimizing individual string lengths. These byte counts establish repeated work, **not a measured latency bottleneck**; profile the real hooks before setting a speedup target.

Source: [shared state library](../.opencode/lib/omt_shared.ts), `readLedger`, `rotateLedgerIfNeeded`, `loadIr`.

### 4.4 Define the actual efficiency objective

Use two separate measures rather than an arbitrary blended score:

```text
cost per accepted task = total spend across all attempts / independently accepted tasks
accepted throughput   = independently accepted tasks / elapsed execution time
```

Include failed attempts, retries, verification, and recovery. Report human intervention minutes separately, or use an explicitly agreed conversion if including them in cost. If nothing is accepted, report the denominator as zero rather than hiding the result. Qualify both measures with correctness and forbidden-action detection. A cheap but wrong result is not an efficiency win.

## 5. Findings and concrete improvements

**Priority definitions:** P0 blocks the relevant production guarantee; P1 is needed for efficient, maintainable operation; P2 is optional expansion after evidence. P0 here describes release readiness, not a claim of an observed external security incident.

### F01 — Mutation coverage and path matching are incomplete

**Priority:** P0. **Evidence:** source inspection and a gate-chain probe.

The policy recognizes edit tools by `edit|write|patch|multiedit`, and the hook extracts one scalar path. Shell writes and other host mutation tools do not automatically enter that chain. This session's `apply_patch` and `exec_command` interfaces, for example, are not OpenCode hook integration merely because the repository contains `AGENTS.md`. The documented shell-edit workaround also acknowledges that hooks cover edit tools rather than all filesystem mutations.

There is a narrower defect inside the supported chain: `pathIn()` treats a non-wildcard entry without a trailing slash as an exact path. However, the compiled harness path classification includes prefixes such as `.opencode/plugins/omt_`. A dry-run probe of `.opencode/plugins/omt_review.ts` returned `g.receipt.fired = false`, although `isOmtHarness()` recognizes that class. The correct downstream helper cannot protect a path filtered out upstream.

**Improvement:** normalize operations into an adapter-owned action envelope containing all affected paths, operation type, workspace identity, and proposed content/diff where available. Use one compiled matcher with explicit `exact`, `directory`, and `prefix` semantics. Validate moves, deletions, multi-file patches, directory roots, traversal and symlinks according to a documented workspace policy. Qualify only adapters whose operations are actually mediated. Use an execution sandbox or broker for stronger filesystem guarantees; string-matching shell commands alone is insufficient.

**Acceptance:** a table-driven adapter contract covers every supported mutation operation and path form. Every path classified as harness-owned by the compiler reaches the receipt obligation; unknown mutation forms produce an explicit unsupported decision. No real secret files are needed in these tests.

Sources: [policy variables](../.meta/META_HARNESS.omt), [hook entry point](../.opencode/plugins/omt_enforcer.ts), [gate matcher](../.opencode/lib/enforcer/gate_driver.ts), [harness classifier](../.opencode/lib/omt_shared.ts).

### F02 — Unexpected errors can convert critical denials into permission

**Priority:** P0. **Evidence:** reproduced.

The before-hook rethrows `OmtBlock` but catches every other exception and continues. With concurrent marking and a stubbed net command returning malformed JSON, the actual hook returned normally and logged `before-hook internal error (failing open)`. The generic predicate evaluator also returns true for unknown predicates; a synthetic hard gate with `requires: unknown_requirement()` permitted the operation.

Missing IR has additional consequences: fallback gates still refer to `@var` values that the generic matcher cannot resolve without IR. A `.meta/doc` search blocked with normal IR but passed when the fixture IR was removed. Separately, `.meta` itself did not match the `.meta/` directory-prefix rule.

**Improvement:** distinguish `allow`, `deny`, `unknown`, and `error`. Critical mutation/authority checks must refuse on unavailable or invalid evidence; optional hints may fail open. Validate the complete IR schema and predicate vocabulary at load time. Provide either a fully self-contained verified fallback or an explicit repair/read-only mode. Preserve useful diagnostic access during repair.

**Acceptance:** inject invalid JSON, missing IR, bad types, unknown predicates, subprocess failure, timeout, and unavailable state. Critical operations remain refused with a stable reason and recovery action. Optional advice failure does not block unrelated work.

Sources: [before-hook catch](../.opencode/plugins/omt_enforcer.ts), [predicate evaluator and net implementation](../.opencode/lib/enforcer/gate_driver.ts).

### F03 — Passing the test gate skips independent obligations

**Priority:** P0. **Evidence:** reproduced.

`g.tests` returns `stop` after test approval succeeds. Both live and dry chains then terminate. A fixture with an approved test edit, concurrent marking, and an inline risk thought was permitted; the chain stopped at `g.tests`, with **zero net calls and no thought gate evaluation**. This conflicts with the intended independent net and thought obligations for covered files.

**Improvement:** distinguish “this gate is satisfied” from “no more gates apply.” Continue evaluating independent obligations after approval; express intentional subsumption explicitly in policy. Keep the TDD test-hat decision as the authority for test editing without allowing it to silently waive unrelated checks.

**Acceptance:** test approval permits the edit only after all other applicable obligations pass. Pairwise and multi-gate cases cover test approval plus concurrency, thoughts, receipts, and protected-path exceptions. Reordering unrelated gates cannot change the final permission decision.

Sources: [gate implementations and iteration](../.opencode/lib/enforcer/gate_driver.ts), [test approval guard](../.opencode/lib/enforcer/receipt_guard.ts).

### F04 — Authorization, progress, and consultation have inconsistent scope and lifetime

**Priority:** P0 for managed/multiple sessions; P1 for the restricted solo profile. **Evidence:** reproduced, with legacy fallback intentional in source.

`findBreakGlass()` can return session A's recent grant when session B has no matching grant. This is an explicit compatibility fallback, but it cannot support session isolation. A 48-hour-old fixture returned `getActiveUnlock() = null` while `hasNavUnlock() = true` and `hasFastPathUnlock() = true` for the same session. Thus the eight-hour lifetime is not applied consistently across helpers.

The new `hasDurableProgress()` helper also expires phase records, despite the module's stated distinction between durable progress and temporary grants. It is not currently called by other production modules found in this review, so this is an incomplete API contract rather than proof that all progress disappears after eight hours. The ledger retains history.

**Improvement:** define separate typed records for durable task progress, temporary grants, consultation evidence, and verification. Bind grants to explicit principal/session, feature, workspace, scope, reason, and revocation/expiry. Keep any legacy single-user fallback inside an explicit compatibility profile. Use one reducer and one clock policy; reject implausible future timestamps. Consultation freshness should follow relevant content changes, separately from edit authority.

**Acceptance:** A's grant cannot authorize B in managed mode; expired grants are rejected by every consumer; unrelated phase advancement neither revokes nor broadens a grant; progress survives grant expiry; revocation and abandon events affect only their intended scope.

Sources: [session selectors](../.opencode/lib/enforcer/session_state.ts), [typed policy slice](../.opencode/lib/enforcer/policy_decision.ts).

### F05 — Completion can succeed without successful verification

**Priority:** P0. **Evidence:** subprocess-boundary defect reproduced; coverage limitations inspected.

`omt_complete` ignores the verifier subprocess's exit code and substitutes `{"ok":true}` when stdout is empty. In a temporary fixture, a command result with `exitCode: 1` and empty stdout produced a successful Testing completion, wrote a `complete` record, and advanced the feature to Done.

The new behavioral completion check is valuable but searches only `tests/features/<full-feature>/test_*.py`. Tests under `tests/scripts/omt`, alternate layouts, and TypeScript suites are not automatically included by that search. With no discovered tests, `behavioral.ran` is false and completion may still be okay. An active global `scope:all` override can also transform failing validation into `ok:true`; the failure is then no longer represented as a failed outcome in the returned arrays.

**Improvement:** require zero exit status, a valid versioned response, the expected verification identity, and a passing outcome before recording verified completion. Declare verification targets explicitly by feature/change surface and toolchain; missing expected tests or zero collection must be incomplete evidence. Preserve intentional docs-only/no-test cases as a distinct policy outcome. Overrides should yield `waived` with the original failure and authority recorded, never an ordinary verified pass.

Run expensive behavioral verification at meaningful acceptance boundaries. Reuse an unchanged, valid result where policy allows, rather than rerunning the same suite at every declaration or intermediate phase.

**Acceptance:** nonzero exit, empty output, malformed response, timeout, no collected tests, missing suite, and wrong toolchain cannot produce verified Done. Failing tests outside the conventional feature folder still block the relevant change. A waiver remains visible to the integration decision.

Sources: [completion tool](../.opencode/lib/enforcer/phase_gate.ts), [behavioral validation](../scripts/omt/tdd/gates.py), [toolchain-aware test runner](../scripts/omt/tdd/state.py).

### F06 — Staging lacks an enforced verification boundary

**Priority:** P0 for the batch guarantee. **Evidence:** reproduced and source inspection.

The stage record contains feature, files, snapshots, creation time, and policy digest. `isStagedHarnessFile()` checks membership and an optional policy digest, but not ownership, age, feature authority, terminal state, or whether verification occurred. A 48-hour-old fixture with an unrelated feature and empty policy version was accepted. Even well-formed stages have no enforced end-of-batch lifecycle in the inspected path.

The CLI supports create/status/clear; it does not supply a transactional finish-and-verify operation. The receipt writer does not consume a stage, and `omt_complete` does not check that the stage has closed. Staging therefore reduces per-edit friction, but currently depends on the agent to honor the promised boundary.

**Improvement:** make stage states explicit: open, verifying, verified, failed, abandoned. Bind each batch to owner, task, workspace, permitted paths, base snapshot and policy version. Finish should freeze the candidate, run the required checks, write evidence, and consume the authorization atomically. A crashed or abandoned batch must remain visible and cannot count as completed work.

**Acceptance:** two sessions cannot overwrite each other's stage; unfinished or failed stages block acceptance; a successful finish consumes the stage; a later edit invalidates the result; recovery preserves user changes. Policy-source edits have a defined batch transition instead of silently losing their own stage permission.

Sources: [stage CLI](../scripts/omt/harnessc.py), `cmd_stage`; [stage validation](../.opencode/lib/omt_shared.ts); [receipt writer](../tests/scripts/omt/test_omt_harness_e2e.py).

### F07 — Receipt fields do not yet form a complete evidence contract

**Priority:** P0 for content-bound verification claims. **Evidence:** reproduced helper behavior and source inspection.

New receipts contain hashes, policy version, toolchain, and results. However, absent results are accepted for compatibility; absent per-file digests are not rejected. Toolchain data is written but not validated by the receipt guard. Freshness can use receipt filesystem mtime. Checking the current target and policy does not establish that all relevant tests, dependencies, configuration and sibling inputs remain the ones that passed.

The writer's manually maintained `HARNESS_FILES` list omits inspected modules such as `policy_decision.ts` and `task_prep.ts`. Also, its `results.status = passed` describes that specific contract test's checks, not necessarily the entire repository suite. These are different evidence scopes.

**Improvement:** introduce a versioned verification manifest with required fields: exact candidate identity, input/dependency digests, policy/IR version, runtime/toolchain identity, verification command and selected nodes, exit status, result summary, and output digest. Validate the complete relevant input closure and distinguish targeted-contract pass from full-suite pass. Migrate old receipts to explicitly legacy/unverified status; do not silently treat missing fields as current-format evidence.

The receipt issuer must also be appropriate to the threat model. Content hashes detect stale content, but do not authenticate a record that an equally privileged process can rewrite. A release verifier or protected execution service should issue production acceptance evidence. SLSA's artifact verification guidance provides a useful model for checking artifact digest and expected builder identity; this recommendation is an analogy, not a claim of SLSA compliance. [SLSA artifact verification](https://slsa.dev/spec/v1.2/verifying-artifacts).

**Acceptance:** missing or mismatched required fields refuse acceptance; changed tests, dependencies, policy or toolchain invalidate the affected evidence; changes to unrelated inputs do not cause unnecessary reruns; targeted evidence is never labeled a full-suite pass.

Sources: [receipt reader](../.opencode/lib/omt_shared.ts), `omtHarnessE2eStatus`, `receiptResultsPassed`; [receipt producer](../tests/scripts/omt/test_omt_harness_e2e.py), `HARNESS_FILES`, `_write_receipt`.

### F08 — Revision checking and file replacement are not a transaction authority

**Priority:** P0 before managed concurrency. **Evidence:** source inspection; races and process crashes not reproduced here.

`state.fire()` loads state, checks an optional revision, computes a successor, saves, then appends an event. No lock encloses that read/check/write sequence. Two writers can both observe revision N and proceed. `save()` replaces three files sequentially, using fixed `.tmp` names and in-process rollback. This helps with ordinary exceptions but does not make the bundle atomically visible to another process, guarantee recovery after process death, or bind the later ledger append to the state update.

This is already recognized in T5-1/T5-6. Keep those items as foundational prerequisites rather than presenting capacity tokens as sufficient concurrent ownership.

**Improvement:** implement one authoritative local mutation boundary over all state-changing commands, with revision checking inside the lock, command idempotency, recoverable persistence, and an atomic event/state commit. Readers need a consistent generation too. Preserve the Petri net as the workflow/resource model; use a durable transaction mechanism for authoritative storage.

For the existing file design, that means the planned lock plus journal/generation publication and startup reconciliation. An alternative is a single local SQLite database for authoritative records, with JSON/Markdown as exports. SQLite provides atomic transaction and writer-isolation mechanisms, but its documented filesystem/durability assumptions still matter. Choosing SQLite would be an architectural decision, not an unapproved replacement for the current T5 plan. [SQLite atomic commit](https://www.sqlite.org/atomiccommit.html), [SQLite isolation](https://www.sqlite.org/isolation.html).

**Acceptance:** two processes starting from N cannot both commit incompatible N+1 results; same command ID plus same payload is idempotent; same ID plus different payload is refused. Kill the process after every persistence step and recover to a complete old or new state. Disk-full and failed event writes cannot be reported as successful commits.

Source: [net state](../scripts/omt/net/state.py), `save`, `fire`; [approved T5 design direction](../.projects/meta/meta_harness_8/PROJECT.md), T5-1 through T5-7 and D8–D14.

### F09 — Best-effort state writes and whole-file rollback weaken recovery

**Priority:** P0 for authoritative audit/progress; P0 before shared-file concurrency. **Evidence:** failed-write behavior reproduced; overwrite risk inferred from source.

`appendJsonl()` swallows write errors. A fixture whose ledger parent was a regular file returned from `appendLedger()` without an exception and persisted zero records. A caller therefore cannot use return from this function as evidence that a phase, authorization, or completion event is durable. JSONL readers also silently skip corrupt lines.

The shared library holds a mutable module-global repository root. It is safe only under the assumption that every consumer in that process uses the same root. REFACTOR recovery stores snapshots keyed by absolute path and writes the old whole-file content back on failure. No comparison against intervening user/worker edits precedes that write in the inspected function.

**Improvement:** keep optional diagnostics best-effort, but require acknowledged writes for authoritative state. Preserve and surface corrupt records with sequence/checksum diagnostics instead of silently treating missing authority as normal history. Inject an immutable workspace/state context rather than changing global roots. Rollback must be task-owned and conditional on the expected current content; otherwise produce a recovery patch and preserve concurrent changes. Per-generation worktrees are the preferred isolation boundary for managed workers.

**Acceptance:** write failure cannot produce a success acknowledgment; replay is deterministic and detects gaps; interrupted rotation loses no accepted event; separate workspaces cannot redirect each other's state; failed refactoring preserves a user's intervening edit.

Sources: [state IO](../.opencode/lib/omt_shared.ts), `appendJsonl`, `readJsonl`, `initOmtShared`; [REFACTOR restore](../.opencode/lib/enforcer/tdd_hats.ts), `tddAfterEdit`; [snapshot containers](../.opencode/lib/enforcer/session_state.ts).

### F10 — Preflight and task preparation need a truthful shared snapshot

**Priority:** P1, with correctness fixes required before broader wiring. **Evidence:** source inspection.

Reusing the dry chain is a strong design choice, but the net implementation returns without its live permission verdict when the synthetic environment has no shell function. The projection may consequently report `blocked:false` and an “all clear” summary while its human-readable text adds a concurrency caveat. Machine consumers should not need to interpret that prose to distinguish checked permission from unknown permission.

The typed evaluator currently covers only `g.net` activation/override. `task_prep.ts` is deliberately a standalone slice without tool wiring; its policy note defaults to a solo marking if one is not supplied and passes an empty record list to the evaluator. Its risk model uses path/description keywords. Those are useful provisional heuristics, not authoritative classification of a patch.

**Improvement:** read one versioned snapshot, evaluate typed obligations without side effects, and use the result for enforcement, preflight and explanation. Represent unavailable live evidence as `unknown`, with an explicit required check. Extend the existing status/preparation surface only after measuring its value; include observed change scope, relevant context, obligations, and verification plan. Re-evaluate on changed scope. Use deterministic path/operation facts and conservative uncertainty handling for risk, with descriptions as supplementary evidence.

**Acceptance:** the same action and snapshot produce equivalent decisions across consumers; prediction never labels unknown as allowed; preparation does not fabricate consultation or approval; one routine preparation response replaces demonstrably redundant calls. Keep low-level recovery tools available.

Sources: [preflight](../.opencode/lib/enforcer/preflight.ts), [typed policy](../.opencode/lib/enforcer/policy_decision.ts), [preparation slice](../.opencode/lib/enforcer/task_prep.ts).

### F11 — Context and knowledge budgets should track relevance and delivered size

**Priority:** P1. **Evidence:** source inspection and navigation queries.

Thought/KB consultation and batch reuse reduce rediscovery, but consultation is often represented as a session flag or time-window event. It is not a proof that relevant current knowledge was delivered. Some inline comments still describe earlier known defects, so duplicated operational advice needs evidence-driven retirement.

`capNavLines()` caps **25 records**, not actual output bytes or tokens. One long record or contextual expansion can still be expensive. Knowledge index size, returned context size, and retrieval usefulness require separate measurements. Queries central to this assessment, including `goal` and `efficiency`, returned no indexed answer, despite related project documents existing.

**Improvement:** attach stable IDs, affected symbols/contracts, source version, evidence references, and invalidation conditions to important knowledge. Retrieve by change surface; deliver it once per relevant version. Give navigation a returned-byte/token budget, deterministic truncation, and a continuation mechanism. Keep accessible explanations even when internal records grow. Promote repeatedly useful, testable lessons into checks and retire redundant prose through review.

**Acceptance:** changed relevant knowledge refreshes the consult; unrelated changes do not. Representative task queries retrieve the expected current lessons. Large individual records respect output limits and remain reachable through continuation. Track successful retrieval and avoided rediscovery rather than only consult counts.

Sources: [knowledge/session selectors](../.opencode/lib/enforcer/session_state.ts), [navigation implementation](../.opencode/plugins/omt_nav.ts), [output cap](../.opencode/lib/omt_shared.ts), `capNavLines`.

### F12 — Tests and release qualification need stronger behavioral independence

**Priority:** P0 for release qualification; P1 for execution cost. **Evidence:** existing tests and configuration inspected; suite result in §10.

The repository has extensive behavioral tests, so describing it as “only source pins” would be wrong. Nevertheless, the receipt-producing contract test contains many source-string assertions, and the live suite documents a reduction from guard-behavior probes to two load/injection smoke tests. A syntactically present guard can still be bypassed by chain order, ignored subprocess status, or a path prefilter—the reproduced findings demonstrate why those layers are distinct.

The policy's audited OpenCode range is `>=1.18.29,<1.19`, while `.opencode/package.json` pins `@opencode-ai/plugin` to `1.17.11`. This is not proof of incompatibility; it is a runtime/SDK pair that needs an explicit tested compatibility record. No in-repository YAML CI configuration or `.github` directory was found in the inspected tree. External CI may exist, but this review has no evidence of an independent release pipeline.

**Improvement:** define three test layers: fast deterministic policy/reducer tests, adapter contract/fault tests, and a smaller real-runtime qualification lane. Add independent acceptance cases for critical workflows and representative fault injection. Keep source pins only where representation itself is the contract. Release from a pinned candidate in a clean environment; record runtime/SDK/compiler/dependency identities, projection checks, behavioral results, and installation/upgrade/rollback evidence. Separate hermetic checks from network/model-dependent smoke so one slow external dependency does not obscure deterministic failures.

A missing runtime should be an explicit unsupported/not-qualified result for a release that claims support, even if developer tests may skip it. Publish migration and repair procedures alongside release artifacts. NIST SSDF provides a useful external framework for protecting software and retaining release verification/provenance, without requiring this project to claim certification. [NIST SSDF](https://csrc.nist.gov/projects/ssdf).

**Acceptance:** a candidate cannot be labeled production-ready with a failed required check, an untested claimed adapter, or stale evidence. Install into a clean temporary repository, exercise an accepted and refused workflow through the real adapter, upgrade, and recover without affecting user content. Critical seeded defects must fail behavioral checks even when source pins remain green.

Sources: [receipt-producing test](../tests/scripts/omt/test_omt_harness_e2e.py), [live smoke contract](../tests/scripts/omt/test_omt_live_opencode_guards.py), [SDK dependency](../.opencode/package.json), [pytest configuration](../pyproject.toml).

## 6. Production architecture: evolve the existing components

### 6.1 Authority boundaries

Keep the compiler, gate modules, knowledge tools, and net. Give each a clear authority boundary:

| Layer | Responsibility | Must not claim |
|---|---|---|
| Canonical policy/compiler | Validate and compile typed policy, matcher semantics, schemas and explanatory text. | That a successful build proves runtime behavior. |
| Runtime adapter | Normalize supported actions and mediate execution inside the declared workspace. | Coverage of unintegrated tools or arbitrary external writers. |
| Policy evaluator | Compute allow/deny/unknown/error from one immutable snapshot. | Successful verification or persisted state merely from a prediction. |
| State authority | Atomically manage progress, grants, claims, revisions and events. | That task ownership alone proves correct output. |
| Verifier | Execute the declared tests against the frozen candidate and issue scoped evidence. | A broader pass than the suites and inputs actually checked. |
| Integration authority | Accept the candidate against current dependencies and integrated state. | Completion based on a worker's self-report or an expired receipt. |
| Agent-facing context | Prepare tasks, retrieve knowledge, explain obligations and resume state. | Authority or understanding from a retrieval event alone. |

A minimum decision envelope should include `decision`, `reason_code`, `action_id`, `workspace_id`, `task_id`, `policy_digest`, `state_revision`, `obligations`, and `evidence_refs`. A grant or worker claim additionally carries its own ownership/generation identity. **Global revision and task generation solve different problems:** revision protects a transaction against stale reads; generation prevents a former owner from publishing after transfer.

Avoid distributing another independently maintained policy copy across Python, TypeScript, prose and tests. Typed data plus a small primitive implementation registry is enough; an unrestricted policy language is unnecessary. Migrate one obligation at a time, replay old/new decisions in shadow mode, inspect differences, and keep the previous verified policy available for recovery.

The initial threat model should be explicit. Cooperative agents making mistakes are a reasonable first target. A malicious process with the same write access to policy, code, state and receipts is outside a file-based hook's reliable enforcement boundary. Stronger adversarial guarantees need a separately protected execution/verifier boundary, not more self-authored approval records.

### 6.2 Make the guarantees executable invariants

The findings share a structural cause: several local indicators are treated as stronger evidence than they provide. A successful gate terminates other checks; process output substitutes for process success; a receipt's presence substitutes for current verification; a revision comparison substitutes for a transaction. Fix each defect, then preserve the intended guarantee at the composed boundary.

Use this invariant register to connect design, regression cases and release decisions. It can initially live alongside the proposed F07 verification manifest; a new registry service is unnecessary.

| ID | Required invariant | Decisive negative case and positive control | Related findings |
|---|---|---|---|
| I01 — Complete mediation | Every supported mutation is normalized and every affected path evaluated before execution. | A multi-file patch with one forbidden target is refused in full; the same patch restricted to permitted paths succeeds. | F01 |
| I02 — Independent obligations | Permission requires every applicable critical obligation to be satisfied or specifically waived where policy permits. | Test approval plus missing net authority is refused; granting the net authority still leaves any thought obligation intact. | F02–F03 |
| I03 — Scoped authority | Grants cannot grow through actor fallback, expiry, unrelated progress or replay. | A grant for A does not authorize B; A succeeds inside its scope and lifetime. | F04 |
| I04 — Truthful verification | Verified acceptance requires successful declared checks against the exact candidate and relevant inputs. | A nonzero exit with empty or even positive-looking output refuses acceptance; a valid passing response with matching identity succeeds. | F05–F07 |
| I05 — Durable acknowledgment | Acknowledged authoritative commands survive the claimed crash model without partial state. | Interrupt each persistence step and retry the command; after successful retry, exactly one complete effect is visible. Include a successful uncontended command. | F08–F09 |
| I06 — Safe invalidation | A relevant change invalidates dependent evidence; an unrelated change does not. | Change a required test/config input and refuse stale evidence; change an unrelated document and retain valid reuse. | F06–F07, F11 |
| I07 — Truthful prediction | The same action and snapshot have the same evaluated obligations; unavailable evidence stays unknown. | Remove the live net observation and require `unknown`, not “all clear”; a complete snapshot agrees with enforcement. | F10 |
| I08 — Preserved work | Recovery never overwrites a newer user/worker version without explicit authority. | Insert an intervening edit before rollback and retain it; restore an exclusively owned unchanged candidate normally. | F08–F09 |

I01–I04 and I06–I07 apply to the claimed solo boundary. I05's durability and I08's user-edit preservation matter even for a single agent; competing-owner cases additionally qualify managed mode. These are outcome properties, not a proposal for eight new gates.

### 6.3 Close the gap between checking and executing

A correct decision is insufficient if the state changes before the effect. Define a bounded action lifecycle:

```text
normalize action → read snapshot → evaluate obligations
                 → conditionally execute → acknowledge effect
freeze candidate → verify declared inputs → conditionally accept
```

Preflight is a prediction and grants no authority. An execution decision binds the action payload, all target paths and expected base digests, workspace, policy digest, state revision, applicable grants and their validity. Immediately before mutation, the executing adapter checks those preconditions and any revocation/expiry; a mismatch requires a fresh decision. An `action_id` provides retry correlation, not permission. The authority must store idempotency decisions; replaying the same ID with a different payload is an error.

For multi-file actions, prevent partial application or use a recoverable staged publication with explicit incomplete status. Do not hold a global state lock while tests run: freeze an isolated candidate, verify outside the lock, then accept through a short conditional transaction that rechecks candidate, ownership and evidence. If the host cannot mediate the check-to-write boundary, document that limitation and restrict the claim; an after-write hash can detect drift but cannot retroactively prevent the write.

This applies to self-modification too. A proposed policy must not authorize its own activation. The currently trusted policy controls editing and qualification; a verified successor is activated at a defined boundary. In-flight work either finishes under its explicitly pinned policy where permitted or is re-evaluated. No operation may silently combine obligations from two versions.

### 6.4 Specify evidence before building another abstraction

Extend existing records with a small, versioned contract. Names below are proposed fields, not an already supported API.

| Record | Required information | Validation rule |
|---|---|---|
| Task contract | Task ID, requested outcome, scope, acceptance-case IDs, verification targets, capability profile, contract revision. | Scope/acceptance changes create a new revision and invalidate affected decisions. |
| Decision | Action/payload identity, task-contract revision, workspace, policy and state identities, per-obligation outcomes and evidence references. | Only satisfied applicable obligations permit execution; any explicit waiver names the exact waivable obligation and authority. |
| Verification | Candidate digest, input manifest, command/node selection, runtime/config identities, timestamps, timeout/exit/collection data, result and log digest, issuer. | Mandatory fields and input coverage validated before reuse; a log digest alone cannot establish a pass. |
| Acceptance | Task-contract revision, candidate and integration-base identities, verification references, outcome, unresolved items and waivers. | Distinguish `verified`, `failed`, `waived`, and `unverified`; only eligible current evidence supports `verified`. |

Keep execution status separate from verification status: `finished` means the process stopped, not that verification passed. A docs-only case can satisfy its explicitly declared document checks without inventing a behavioral test pass. A skipped required check remains unverified. Cancellation, timeout, infrastructure failure and zero collection should remain distinguishable for diagnosis, even though none supplies positive behavioral evidence.

Candidate identity must cover relevant uncommitted and untracked inputs, not just `HEAD` or the edited target. Include file mode, symlink target and deletion semantics where relevant. Start with a conservative declared input manifest; if dependency coverage is unknown, broaden verification or refuse reuse. Optimize toward dependency-aware invalidation only after tests show the narrower closure is sound. Preserve raw verifier evidence outside the candidate's self-authored acceptance record to the extent required by the threat model.

Separate verification inputs from generated outputs: logs, receipts and runtime ledger updates must not recursively change the candidate identity they describe. Declare those exclusions narrowly. If a verifier unexpectedly modifies a source, test or configuration input, invalidate the run rather than issuing evidence for the pre-run digest.

### 6.5 Degraded operation and recovery are product behavior

Failing closed should prevent unsupported authority without turning optional knowledge failures into a dead end. Define the behavior by failed component rather than using one global bypass:

| Failure | Continued capability | Required restriction / recovery |
|---|---|---|
| Missing/corrupt policy or authoritative state | Protected, sanitized diagnostics and read-only inspection within host permissions. | Refuse affected writes and acceptance; validate and restore a compatible policy/state pair. |
| Optional navigation/KB index unavailable | Source-based inspection and a clearly labeled degraded preparation response. | Do not invent a consult receipt. If policy mandates a consult, satisfy it through a defined equivalent path or leave that obligation unresolved. |
| Verifier timeout/unavailable runtime | Preserve the candidate and diagnostic output; allow a bounded retry. | No verified acceptance; report the failed execution separately from a tested behavioral failure. |
| Receipt stale after an edit | Continue authorized development with stale status visible. | Reverify affected inputs before acceptance; do not discard good work merely because evidence expired. |
| Failed state acknowledgment | Read-only diagnosis and command-status lookup. | Do not blindly retry a non-idempotent action or report success. Reconcile the original command ID first. |

Recovery starts by identifying the workspace, last valid state/policy generation, unfinished commands and current user changes. Export diagnostics, reconcile or restore into a disposable location, validate it, then activate the repaired state conditionally. A repair path must not grant itself unlimited authority. Keep a last-known-good implementation and compatible state backup; a compiler check is necessary but cannot establish safe rollback across an incompatible state migration.

### 6.6 Evolve policy with a decision-difference report

For each typed-policy migration, replay a fixed labeled action corpus against old and proposed evaluators. Classify differences as stricter, more permissive, unknown/error, or explanation-only. The old evaluator is a comparison baseline, not the correctness oracle: reviewed expected outcomes decide which behavior is right.

Promotion requires every newly permitted operation to have an explicit rationale and acceptance case, every newly refused valid operation to have a resolution, and every required fault case to pass. Shadow evaluation observes; it never authorizes. Keep policy, compiler, adapter and state-schema compatibility identities in the activation record. Demonstrate both forward migration and recovery before promoting a version that changes persisted authority semantics.

For bounded policy/net models, add generated event sequences and property checks for expiry, revocation, duplicate delivery and independent-gate order. The existing net analysis can check modeled invariants, but adapter mediation and storage atomicity still require execution tests. A Petri-net proof cannot establish that an implementation's three-file save is atomic.

### 6.7 Learn from failures without automatically expanding policy

Turn repeated repair into reusable evidence. When a gate or verifier blocks work, produce a bounded diagnostic record through the existing status/preflight surface: stable reason, affected task/action, observed versus required state, missing evidence, and the smallest valid recovery action. Distinguish a missing authorization from a stale index or unavailable verifier; suggesting a broad override for all three obscures the cause and increases intervention cost.

Link a resolved incident to its counterexample, repair and verified outcome. Promote it through three explicit stages: observation, validated lesson, and candidate regression check or policy change. Promotion is reviewed; a retrieved lesson or agent-authored failure report cannot grant authority or rewrite the active policy. Deliver a lesson only when its affected surface and source version are relevant, and measure whether it reduces recurrence and recovery effort.

Use an unchanged failure signature to detect unproductive loops. After a small configurable retry budget, preserve the candidate and return the unresolved cause and next required input instead of repeating the same expensive checks. Retry when relevant state changes or an explicitly transient failure warrants it. This makes knowledge retention improve completed work and provides evidence for retiring redundant instructions, rather than accumulating more mandatory consultation.

## 7. Measurement program and proposed service objectives

### 7.1 Establish a baseline before broadening policy

Use the existing T3-4 six-task plan: local bug fix, change across layers, major feature, harness repair, resumed task, and conflicting concurrent work. Treat concurrency as a separate capability cohort until T5 is ready. Pin candidate revision plus working-tree content, model/runtime versions, dependencies, machine profile, task definition and hidden acceptance checks.

For an initial feasibility sample, run at least five independent attempts per task and condition. Compare current policy with an appropriate existing tier and one proposed improvement. Randomize order and separate warm/cold runs. Do not copy observations from one attempt into the next agent's context. Report distributions and confidence limits where meaningful; thirty attempts is a pilot, not proof of universal reliability. Use larger samples for close comparisons or rare failures.

Seed forbidden operations and representative broken implementations in disposable fixtures. Evaluate both valid work wrongly refused and invalid work wrongly permitted. Run targeted removal/simplification experiments before retiring a gate; never automatically weaken a protection based on cost alone. Keep evaluator acceptance checks independent of the agent-authored implementation tests.

Predeclare the primary comparison, acceptable correctness margin and stopping rule. “No observed loss” in a small pilot is not evidence of equivalence. Report per-task and per-profile results so a cheap routine edit cannot hide failed complex work. Count infrastructure failures in the operational result and also report them separately for diagnosis; replacing only failed runs would bias the comparison. Keep acceptance checks stable across conditions, with access separated from the implementing agent where practical.

### 7.2 Metrics that should guide decisions

| Measure | Definition / reason |
|---|---|
| Behavioral acceptance rate | Accepted attempts / all attempts, with independent checks and no hidden exclusions. |
| Total cost per accepted task | Actual runtime usage/spend across successes and failures / accepted tasks. |
| End-to-end p50/p95 duration | Includes preparation, edits, verification, retries and recovery. |
| Gate false refusal / false permission | Labeled valid and invalid cases, reported separately by gate and adapter. |
| Recovery cost | Extra calls, tokens and human minutes after a block, crash, stale receipt or failed check. |
| Preparation and resume cost | Actual calls and input/output tokens, including repeated document reads. |
| Verification cost and reuse | Time spent validating, proportion of safely reusable results, invalidation accuracy. |
| Knowledge usefulness | Relevant results retrieved, stale results delivered, repeated mistakes and rediscovery. |
| State reliability | Acknowledged events lost, conflicting claims, stale publications, incomplete recoveries. |
| Harness maintenance burden | Time spent repairing harness mechanics per time spent delivering accepted application work. |
| Evidence invalidation quality | Stale results wrongly reused and valid results unnecessarily rerun, measured with labeled dependency changes. |
| User-intervention burden | Number and minutes of required clarifications, approvals and manual recoveries per accepted task. |

Capture tool start/end, decision reason, state/policy identity, cache hit, subprocess time, output bytes, and observed usage. Keep content and secrets out of routine telemetry. Read metrics across the retention window rather than only the current hot ledger. Do not interpret fewer refusals as safer behavior without labeled cases.

### 7.3 Initial acceptance targets — proposals, not achieved results

- **Correctness:** all enumerated critical fault and forbidden-action cases refused; every positive control still succeeds. Any missed critical case blocks the affected release claim. Passing a finite corpus is not a universal security guarantee.
- **Efficiency experiment:** test the existing proposal of 50% fewer harness-specific calls and 20% fewer total tokens on routine tasks, with no observed loss of behavioral acceptance. Revise these targets from baseline evidence rather than promising them.
- **Local decision overhead:** propose p95 under 100 ms for pure/local preflight and policy decisions on a documented reference machine, excluding actual test execution. Benchmark current behavior first and report state size.
- **State scaling:** at 1×, 10× and 100× retained history, current-task decision work should depend on the active snapshot and relevant indexes, not a full monthly-history parse per helper.
- **Recovery:** zero acknowledged authoritative events lost in the enumerated process-kill tests; abandoned work recovered without deleting another actor's changes. Separate process-crash qualification from filesystem/power-loss guarantees.
- **Preparation/resume:** one bounded response contains the task identity, verified current state, applicable obligations and next step for routine cases; refresh only on relevant changes.

## 8. Prioritized implementation sequence and backlog mapping

This is a proposed ordering, not a modification of the locked roadmap or authorization to execute it. Keep `meta_harness_8` as the existing actionable home. The reproduced findings supply new evidence for follow-up work; they do not erase previous features' shipped status.

| Order | Work package | Priority / indicative size | Existing home | Completion criterion |
|---|---|---|---|---|
| 1 | Enforcement/completion defect closure: exit-status validation, fail behavior, matcher parity, independent gate composition | P0 / medium | Follow-ups to T4-1 and T4-3 | F01–F05 fault corpus green through supported adapters. |
| 2 | Baseline instrumentation and six-task pilot | P1 / medium | T3-4 | Reproducible first outcome/cost report; no unmeasured efficiency claims. |
| 3 | Explicit grants and typed snapshot semantics | P0 managed, P1 solo / medium–large | Extend T4-1 | Scope, expiry, revocation, prediction and durable-progress contracts pass. |
| 4 | Stage finish lifecycle and complete verification manifest | P0 / medium–large | Follow-ups to T4-2/T4-3 | F06–F07 acceptance, including interrupted batches and stale dependencies. |
| 5 | Production solo release lane, clean install, migration/repair and compatibility record | P0 release / medium | Feature 052/059 foundation; new release-quality work | All required checks green for a pinned candidate, with rollback/repair evidence. |
| 6 | One preparation snapshot, useful bounded context, indexed state reads | P1 / medium | T3-5, T3-3, T3-6 | Measured cost improvement with no missed obligations or invalidations. |
| 7 | Transaction authority, claims/generations, worktree isolation, capacity, integration and recovery | P0 managed / large across existing slices | T5-1 → T5-7 | Existing T5 end-to-end demo plus race/crash and gate-composition cases. |
| 8 | Graph queries, temporal replay, further advice and retrieval sophistication | P2 / evidence-dependent | T1-3/T1-4 and remaining discovery work | Real user tasks show benefits exceeding maintenance and context cost. |

Sizes are relative planning estimates, not time commitments. Work package 2 can be designed alongside correctness fixes without blocking an urgent demonstrated defect. Do not tune performance on known-invalid permission behavior and then report the result as an improvement.

Feature 076's current compiler/workflow changes should be assessed as existing work, not proposed from scratch. Finish its normal validation and close the catalog warning. The important production reorder is to advance correctness and baseline measurement ahead of optional graph, replay or advisory expansion.

Replace activity-based success criteria such as “delegation calls become nonzero” or “historical queries are used” with outcome measures. A feature should earn its place by improving work, not by inducing calls to itself. Similarly, reserve new gates for a demonstrated invariant; first fix or combine the current obligations where their semantics are wrong.

### 8.1 First implementation slice: make completion truthful

Start with F05 rather than a wholesale architecture rewrite. It has a narrow implementation boundary and a decisive observed failure: a failed verifier can record success. Deliver the following as one reviewable slice:

1. Preserve a runnable temporary-root reproduction of nonzero exit plus empty stdout at `omt_complete`, asserting that no `complete` or Done event is written. Add a valid passing positive control through the same interface.
2. Define a versioned verifier response and explicit outcomes. Check process status, parsing, required fields and selected verification identity. Cover nonzero exit with `ok:true`, empty/malformed output, timeout and missing required checks.
3. Preserve docs-only handling and waivers as explicit outcomes. Keep the original failure details when authority permits a waiver; do not relabel it verified.
4. Require an acknowledged completion write. If persistence fails, return an error and a recoverable command identity; never a successful completion message. This requires a narrow authoritative-write path from F09 before claiming end-to-end completion reliability.
5. Qualify through the supported runtime adapter. Record test node IDs, candidate identity and actual results in the F05 closure. Run affected compiler/projection and behavioral checks, then the required release lane.

**Exit:** the original false-success case is impossible in the enumerated subprocess/persistence failures and the positive case still works. **Limit:** this closes truthful completion signaling; content/input binding in F07 and the wider adapter coverage in F01 remain separate release blockers. The first slice must not be marketed as full verified execution.

Follow with F02/F03 gate failure/composition and F01 matcher/adapter coverage. Instrument these repaired boundaries while establishing the baseline. Then implement the shared snapshot and evidence contract incrementally, using the invariant register to decide when the solo profile is qualified.

### 8.2 Alternatives and decision checkpoints

| Decision | Recommended first choice | Escalate when evidence justifies it |
|---|---|---|
| Policy representation | Extend the existing typed IR and primitive registry, one obligation at a time. | Introduce a richer policy language only if concrete rules cannot be expressed clearly and safely. |
| State persistence | First require durable acknowledgments and an explicit transaction contract; compare the existing file/journal plan with local SQLite in disposable fixtures. | Select the storage design using crash/race results, migration effort and operational assumptions; do not maintain two authoritative stores. |
| Verification reuse | Conservative declared inputs and exact candidate identity. | Add finer dependency indexing when unnecessary reruns are a measured material cost. |
| Context preparation | One bounded response on existing tool surfaces, with current obligations and targeted knowledge. | Add graph/retrieval machinery only after labeled task queries expose a repeatable deficiency. |
| Concurrent workers | Isolated workspaces plus a single acceptance authority after the solo boundary is qualified. | Expand worker capacity only when integrated accepted throughput improves and recovery cases stay green. |

At each checkpoint, attach the smallest evidence bundle that decides the next investment. If the six-task pilot shows no useful end-to-end gain, simplify or retire redundant preparation and consultation work before adding more. Critical protections are retained unless an equally effective replacement is demonstrated. No new gate, service or document is justified solely by satisfying this assessment's terminology.

## 9. Release acceptance checklist

### Restricted production solo release

- [ ] Supported runtime, adapter, operating system, filesystem and threat model documented.
- [ ] F01–F07 relevant critical behaviors corrected and verified through the supported adapter.
- [ ] Authoritative writes acknowledged; invalid/corrupt state produces explicit recovery behavior.
- [ ] Accepted output is bound to the candidate and its relevant inputs; failure/waiver/unverified remain distinguishable.
- [ ] Required compiler, behavioral, adapter and clean-install checks pass on the same pinned candidate.
- [ ] No unresolved required-suite failures hidden behind historical success counts.
- [ ] Upgrade, recovery and user-edit preservation demonstrated in disposable repositories.
- [ ] Baseline task-outcome and cost report published, with limitations and failed attempts included.
- [ ] No concurrency, tamper resistance, or unsupported-host guarantee implied by the release description.
- [ ] I01–I08 have applicable executable cases with positive controls, candidate identities and retained results; unsupported cases limit the release claim explicitly.
- [ ] Task scope and acceptance contract are current; preflight does not confer edit or publication authority.
- [ ] Check-to-execution preconditions, self-policy activation and degraded recovery behavior demonstrated for the supported adapter.
- [ ] Compatibility profile and installation tier distinguished; historical results cannot satisfy current release checks.

### Managed concurrent release, additional requirements

- [ ] Every mutation path uses the transaction authority, including repair and migration paths.
- [ ] Claims bind task, owner, generation, scope and workspace from the first managed worker.
- [ ] Isolation and conditional rollback preserve other actors' work.
- [ ] Revision races, duplicate commands, process death and stale-generation publication cases pass.
- [ ] Verification and integration capacity are explicit; combined acceptance runs on the integrated candidate.
- [ ] Changed upstream artifacts invalidate dependent acceptance evidence.
- [ ] Existing T5 demo and the new independent-gate cases pass with two workers.

## 10. Original review validation outcome

The compiler and projection checks passed with one catalog warning. The existing full suite collected **2,082 tests** and completed with **2,080 passed, 2 failed, 6 warnings in 552.04 seconds (9 minutes 12 seconds)**.

| Failure | Evidence | Interpretation / action |
|---|---|---|
| `test_tight_budgets_unchanged` | Navigation index was 63,929 bytes; the feature-specific historical ceiling is 63,923. The compiler's current 64,000-byte budget still passes. | Reproduces the failure already recorded in the pause/project history. The observed failure is a six-byte historical-ceiling discrepancy, not a compiler-cap violation. Reconcile the test's intended contract with the current policy; do not simply hide the failure or assume increasing a ceiling is the right fix. |
| `test_plugins_load_and_tools_execute` | `opencode run --format json` exceeded the test's 240-second subprocess timeout. | This run did not establish successful completion of that live smoke. The other live smoke passed. Investigate runtime/provider/process progress in a controlled qualification lane; a timeout alone does not establish that the plugin failed to load. |

The six warnings concern application/dependency behavior and are not used as evidence for the harness-specific findings. No blanket rerun or source repair was performed: this task is an assessment, and the failed checks are reported rather than silently changing the evaluated system. The production assessment depends on the reproduced implementation behaviors, not on an assumption that a green existing suite would prove their absence.

No source, policy, test, workflow or project implementation changes were made by this review. The delivered change is this assessment. Existing tests may refresh their normal ignored runtime artifacts; existing and concurrently appearing working-tree changes were preserved.

### 10.1 Document expansion validation — 2026-09-12

This update expands the same assessment with capability profiles, a task/acceptance contract, an invariant register, execution preconditions, evidence schemas, degraded operation, policy migration controls, evidence-driven learning, and a concrete first implementation slice. It does not implement these proposals or close F01–F12.

The starting checkout was clean at `4a95c911e6113f056b00b53b9b546f7fd0697d51`. The completion, typed-policy and preflight sources were inspected to ground the proposed boundaries. Appendix A's probes were not rerun. A fresh `uv run scripts/omt/harnessc.py check --verify-projections` passed: 263 records, zero errors, with the same catalog warning. Current `WORK.md` is 5,850 bytes; §4.1 retains the original assessment's size snapshot.

Document checks passed: all 64 local Markdown links resolve, code fences are balanced, no duplicate headings were found, and `git diff --check` reported no whitespace errors. This update edits only this assessment. Other work appeared in `WORK.md`, the project manifest and feature 077 requirements during finalization and was left untouched.

**Tests:** the user confirmed that the tests pass. This is user-reported validation; no command output or candidate identity was supplied for that passing run. The assistant-started `uv run pytest` collected 2,082 tests and showed the previously documented budget-pin failure before reaching the live OpenCode checks. Observation of that run was interrupted, and the user requested that further testing be skipped. No final result from that run is claimed here, and no additional tests are required for this document update. The original results in §10 remain historical records; the user confirmation does not by itself close the implementation findings or qualify a production release.

## Appendix A. Reproduced behavior matrix

The temporary probe imported `omt_enforcer`, `gate_driver`, `session_state`, `policy_decision` and `omt_shared` from this checkout. It initialized a temporary root, copied the current IR where specified, and explicitly redirected `OMT_LEDGER_PATH` and `OMT_NET_DIR` to the fixture. Inputs below are synthetic. Results describe hook/helper behavior, not actual filesystem edits.

| Probe | Essential input | Observed output |
|---|---|---|
| Test-chain composition | Approved test edit, marking with two active works, test file with a risk thought | Allowed; dry chain ended at `g.tests` with `stop:true`; zero net subprocess calls. |
| Net error boundary | Concurrent marking; stub command returns exit 1 and malformed JSON | Hook returned normally; logged failing-open JSON parse error. |
| Normal nav control | No grant/consult, normal IR, grep path `.meta/doc` | Blocked by navigation gate. |
| Missing-IR nav | Same search with IR removed | Allowed. |
| Directory-root nav | Normal IR, grep path `.meta` | Allowed; directory root does not match `.meta/` prefix. |
| Unknown predicate | Synthetic hard generic gate requiring `unknown_requirement()` | Allowed with warning about unknown predicate. |
| Receipt prefix | Normal IR, edit target `.opencode/plugins/omt_review.ts` | `g.receipt.fired:false` in dry chain. |
| Failed completion command | Active Testing phase; stub verifier returns exit 1 and empty stdout | Success message; `complete` record and Done phase persisted in fixture. |
| Cross-session grant | Recent scope-all record for A, lookup for B | Returned A's record. |
| Expiry consistency | Same-session bug-fix phase and nav grant 48 hours old | Active unlock null; nav true; fast path true. |
| Durable helper | Same-feature phase 48 hours old | `hasDurableProgress:false`; history was not deleted. |
| Stale/unbound stage | Stage 48 hours old, unrelated feature, listed target, empty policy version | `isStagedHarnessFile:true`. |
| Legacy result field | Receipt JSON `{}` | `receiptResultsPassed:true`; this probes that helper, not every receipt condition. |
| Failed event append | Ledger path nested under a regular file | Append did not throw; zero records persisted. |

To turn these into regression tests, keep the temporary-root setup, invoke the same production interfaces, assert the intended refusal/success outcomes, and add positive controls. For subprocess cases, assert both the tool's returned status and the absence of a completion event. Avoid replacing these behavioral checks with assertions that a particular source string exists.

## Appendix B. Source map

| Area | Primary local sources |
|---|---|
| Goals, policy and backlog | [META_HARNESS.omt](../.meta/META_HARNESS.omt), [meta_harness_8 project](../.projects/meta/meta_harness_8/PROJECT.md), [earlier improvement options](meta/improvement002/IMPROVEMENT_OPTIONS.md), [WORK.md](../WORK.md) |
| Compiler, budgets, stages, tiers and workflow checking | [harnessc.py](../scripts/omt/harnessc.py) |
| Runtime boundary | [omt_enforcer.ts](../.opencode/plugins/omt_enforcer.ts), [gate_driver.ts](../.opencode/lib/enforcer/gate_driver.ts), [receipt_guard.ts](../.opencode/lib/enforcer/receipt_guard.ts) |
| State, grants and evidence | [omt_shared.ts](../.opencode/lib/omt_shared.ts), [session_state.ts](../.opencode/lib/enforcer/session_state.ts), [policy_decision.ts](../.opencode/lib/enforcer/policy_decision.ts) |
| Completion and TDD | [phase_gate.ts](../.opencode/lib/enforcer/phase_gate.ts), [gates.py](../scripts/omt/tdd/gates.py), [state.py](../scripts/omt/tdd/state.py), [tdd_hats.ts](../.opencode/lib/enforcer/tdd_hats.ts) |
| Preparation and navigation | [preflight.ts](../.opencode/lib/enforcer/preflight.ts), [task_prep.ts](../.opencode/lib/enforcer/task_prep.ts), [omt_nav.ts](../.opencode/plugins/omt_nav.ts), [nav_gate.ts](../.opencode/lib/enforcer/nav_gate.ts) |
| Coordination | [net/state.py](../scripts/omt/net/state.py), [net/cli.py](../scripts/omt/net/cli.py) |
| Verification scope | [contract/receipt test](../tests/scripts/omt/test_omt_harness_e2e.py), [live smoke](../tests/scripts/omt/test_omt_live_opencode_guards.py), [completion tests](../tests/scripts/omt/test_completion_hardening.py), [budget pins](../tests/features/feature_059.harness_tiered_template/test_budget_pins.py) |

External design references were checked on 2026-09-12 and cited at the relevant recommendations. They complement the local evidence; they do not replace testing this implementation.
