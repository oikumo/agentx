# META HARNESS: evaluation and significant improvement options

Date: 2026-09-12. Status: proposal only; no implementation selected.

Scope refinement: the user's next priority is AgentX development guided by a Petri net managing concurrent work. See [AGENTX_CONCURRENT_WORK.md](AGENTX_CONCURRENT_WORK.md) for the focused proposal; the generic rollout below has not been selected.

## Assessment

META HARNESS has a sound motivation: make coding-agent development more reliable, preserve knowledge across tasks, reduce repeated discovery and token expenditure, and support changes to the development process. Its methodology also explicitly values practicality and adaptation to the task. Those goals justify a harness that supplies context, coordinates work, and verifies results.

The current design has substantial strengths: a canonical DSL, generated projections, mechanically enforced restrictions, phase and TDD state machines, persistent knowledge, architecture checks, and verification against the actual agent runtime. Small-task fast paths, preflight, tiered templates, gate/ceremony budgets, and per-feature consultation improvements already exist or are represented in the current worktree. The next program should build on these investments.

My main concern is alignment between the objective and the evidence: the reviewed policy provides much stronger evidence of process compliance and projection consistency than of improved end-to-end agent performance. Some gates depend on a declaration or consultation event; some verification depends on edit chronology; performance budgets predominantly count bytes. These are useful proxies, but they leave room for compliant work that is unnecessarily expensive or behaviorally weak.

The most promising direction is to automate preparation of the task's obligations and verify evidence tied to its actual changes. Measure the resulting effect on correct completed work before expanding enforcement.

## Evidence and limits

- Motivation: [evolution workflow](../../../.workflows/meta_harness/loops/meta_harness_evolution.md), lines 1–15; [OMT++ guide](../../../.meta/software_development_process/omt_agent_guide.md), principles at lines 8–18.
- Current policy: [META_HARNESS.omt](../../../.meta/META_HARNESS.omt), its compiled IR/navigation index, generated onboarding, and WORK.md.
- `uv run scripts/omt/harnessc.py check --verify-projections` passed: **263 records, zero errors**. The report lists 10 gates and the registry contains 10 tools. This establishes compiler/projection consistency, not live gate correctness or performance improvement.
- Existing user changes include enforcement/navigation/session files and feature 063 artifacts. They were preserved. Recommendations do not assume the uncommitted changes are absent or defective.
- The OMT plugin tools are not exposed in this session. Their compiled navigation index was queried directly. Source reads used to locate a navigation entry point were not a runtime enforcement audit; the substantive evaluation follows the evolution workflow's artifact-based scope. No historical improvement iterations were reviewed.
- No live enforcement probes, performance benchmark, or full test suite was run. Consequences inferred from declared behavior are identified below; they require implementation validation before a fix is designed.

## Prioritized options

### A. Measure cost per correctly completed task

**Priority: first measurement investment. Effort: medium.**

The existing budgets and ceremony meter are useful. However, policy lines 265–276 budget bytes for prompts, descriptions, indexes, and internal IR. These have different relationships to runtime cost: an internal IR byte is not automatically an agent input token. The current nav index is 63,923/64,000 bytes, leaving 77 bytes; that proximity alone does not establish poor agent performance.

Add a small, repeatable benchmark of representative tasks: a local bug fix, a change across layers, a major feature, a harness repair, a resumed task, and conflicting concurrent work. Run multiple trials with pinned starting revisions, model/runtime versions, and test environments. Compare current full policy, an appropriate existing tier, and the proposed change. Include seeded harmful actions to test protection as well as ordinary tasks to expose false blocks.

Record task success against independent behavioral checks, regressions, user interventions, unnecessary blocks, recovery calls, verification time, wall time, and actual input/output token usage. Record cached input separately where the runtime exposes it. Count unsuccessful attempts in cost totals. Add focused removal experiments for expensive gates; do not infer a gate's value merely from how often it fires.

Keep artifact-size limits as maintenance checks. Use task outcomes and measured overhead to decide which rules deserve stronger enforcement, automatic handling, advisory status, or retirement. Do not automatically weaken protective rules based on token savings.

**Proposed acceptance target, not a predicted result:** reduce median harness-specific calls by 50% and total task tokens by 20% on the small-task sample, while maintaining observed behavioral success and detecting every seeded protected-action violation. Report tail cases and uncertainty; these samples cannot prove universal safety or performance.

### B. Prepare task obligations in one operation

**Priority: largest agent-facing improvement after baseline. Effort: medium–large.**

The current surface includes phase, status/preflight, navigation, thought, KB, TDD, and completion operations (policy lines 281–290). Preflight already lists gates and clearing actions. Extend that capability so a task preparation operation can assemble the applicable obligations and relevant context in one bounded response.

For example, a request describing a bug and its likely files would return the task identity, relevant knowledge, applicable restrictions, required behavioral evidence, and the next valid action. Automatically perform mechanical registration and retrieval already authorized by the task. Preserve decisions that require actual user authorization, and never manufacture approval or claim the agent understood material merely because it was retrieved.

Select obligations using change characteristics: affected contracts, data handling, reversibility, architecture boundaries, shared resources, and uncertainty. Task labels remain useful defaults, but a small bug fix can affect a critical permission check. Existing installation tiers and bug-fix fast paths are a foundation, not a complete task-risk model.

Use the existing tool surface where practical, such as extending preflight and completion. Keep low-level operations for recovery and diagnostics rather than adding another competing workflow vocabulary.

**Acceptance:** representative routine tasks receive complete relevant context and obligations through one preparation call; every actual block is explained by the same decision used by preflight; changed scope refreshes only affected obligations; no consultation or approval is silently fabricated. Measure the effect with option A.

### C. Make policy decisions and state semantics unambiguous

**Priority: architectural foundation for B. Effort: large, incremental migration.**

The DSL intentionally leaves gate logic in TypeScript (policy lines 105 and 118). That is reasonable for implementation primitives, but several policy exceptions are only expressed in prose. For example, `g.net` has `skip_ok=false` while its text permits a special expiring scope-all override and describes concurrency activation as implementation-owned (line 124). The IR's `requires` is empty for that gate. This does not prove a runtime bug; it shows that those fields alone do not encode the complete decision.

Represent activation, requirements, exception classes, authorization scope, evidence freshness, and recovery actions as typed policy data over a small set of implementation primitives. Use one evaluator for preflight, actual enforcement, and explanations. Avoid turning the DSL into an unrestricted programming language or attempting a wholesale rewrite.

Separately model durable task progress, temporary authorization grants, and consultation evidence. The current state description expires phase and skip records after eight hours (line 162), while a current gotcha describes a later phase declaration shadowing test approval (line 253). That gotcha may be stale; verify it before treating it as a defect. Either way, the desired contract should make unrelated state independent: progressing a phase should not silently revoke a valid, separately scoped grant.

Reuse the existing ledger and net revision mechanisms. Define their ownership and derived views rather than introducing another state engine.

**Acceptance:** preflight and enforcement return identical decisions for the same snapshot; phase/approval order does not change unrelated effective permissions; expiry removes authority without losing task progress; feature A cannot alter feature B's grants; exceptional overrides are explicit in compiled data and explanations.

### D. Validate coherent changes and bind evidence to content

**Priority: high for harness development and refactoring. Effort: medium–large.**

Receipt freshness currently compares a timestamp with target mtime, and the harness guard is explicitly a per-file second-edit guard (policy lines 112, 122, 164, and 243). The documented round-robin recipe consequently organizes editing around receipt refreshes (line 247). The large-write workaround even prescribes deletion and reconstruction of a file (line 246). These are signs that tool mechanics influence the engineering workflow; they are not evidence of an independently reproduced exploit.

Permit a bounded, authorized edit batch, then validate the resulting change. Record a receipt containing content digests, policy version, selected tests, relevant dependency/configuration inputs, toolchain identity, and results. Permit temporary internal inconsistency inside the batch; require successful validation before accepting or extending beyond its boundary. Run cheap checks during editing and risk-appropriate integration checks at that boundary.

Invalidate evidence when its inputs change. A receipt should not be presented as covering content or dependencies it did not test. Preserve unrelated user edits and offer a reviewable recovery patch when validation fails; any rollback must have explicit ownership of the changes it reverses.

Keep TDD available and enforce it where selected. Strengthen completion evidence around declared behavior and observable assertions. The current public-method-call coverage criterion (line 185) is useful for finding gaps, but a call alone does not establish that a test detects incorrect behavior. Use a small set of representative faults to validate critical checks, rather than adding exhaustive testing ceremony to every small task.

**Acceptance:** the same final patch receives equivalent verification treatment whether entered in one edit or several; changed inputs invalidate the appropriate receipt; representative broken behavior fails validation; failing validation preserves pre-existing user changes.

### E. Make accumulated knowledge selective and verifiable

**Priority: medium. Effort: medium.**

Inline TA knowledge, consultation receipts, KB navigation, and stale-review support are valuable existing mechanisms. However, the declared gates largely establish that consultation happened (policy lines 126, 129, 170, and 214–217). A consultation event proves neither relevance nor correctness.

Attach lightweight metadata to important lessons: affected symbol or contract, evidence/test reference, relevant content version, and the condition under which the lesson stops applying. Retrieve knowledge based on the change surface, including affected dependents where relevant. A preparation response should deliver that material once and refresh it when the relevant version changes.

Track repeated failures and whether a lesson prevented them. Promote frequently needed, testable lessons into executable checks, then remove redundant warning text after the check is verified. Keep design rationale as prose when it cannot usefully become a rule. Retire obsolete recovery instructions after checking their current validity.

**Acceptance:** changed relevant knowledge causes a refresh; unrelated edits do not require another consultation; retrieval quality is checked against representative tasks; removed lessons have a documented reason and, where appropriate, a replacement check. No automatic learning path may silently grant authority or alter protective policy.

### F. Repair and validate the harness's own evolution procedure

**Priority: immediate, bounded improvement. Effort: small–medium.**

The selected evolution workflow says to update only `./meta/META_HARNESS.md` (line 23). The canonical policy explicitly requires editing `.meta/META_HARNESS.omt` and rebuilding projections (lines 6–8). The successful compiler check does not catch this workflow contradiction.

The workflow also requires a fresh start without previous-iteration history and prohibits source-code searches (lines 9 and 18). These constraints reduce exploratory cost, but for improvement decisions they can prevent reuse of relevant experiment results and verification of a suspected implementation cause. This evaluation respected that artifact scope; a follow-on implementation investigation should be allowed to examine the relevant code and evidence.

Give workflows a minimal validated header declaring their authority, canonical targets, required capabilities, output location, and approval boundary. Check references and generated-file restrictions during compilation. Provide a documented artifact-only mode when plugin tools are unavailable, with an explicit limit on claims about enforcement. Do not infer a live plugin defect simply because this host lacks those tools.

Allow targeted reading of prior measured outcomes, not automatic loading of entire histories. Require each proposed policy change to state the observed problem, intended measurable benefit, affected safety conditions, evaluation method, and rollback condition.

**Acceptance:** the compiler rejects a workflow that instructs an edit to a generated policy projection, references a nonexistent target, or contradicts its declared authority; the evolution workflow points to the canonical source; an unavailable capability yields a useful bounded mode with no false claim of enforcement.

## Suggested sequence

1. Select **F + A** first: repair the improvement contract and establish an outcome baseline. This makes later decisions testable and prevents repeating stale instructions.
2. Deliver one vertical slice of **C + B** for ordinary bug fixes: shared decision semantics plus automatic task preparation. Measure before broadening it.
3. Apply **D** to harness changes, where receipt-related friction is directly documented. Verify ownership and invalidation behavior before extending it.
4. Add **E** using observed repeated discovery and stale-knowledge cases. Expand risk-sensitive methodology and concurrency features only where the benchmark shows value.

The successful outcome is a harness that improves verified task completion while lowering agent effort, with a clear explanation of which checks earn their cost. More rules, a larger DSL, or fewer bytes alone are insufficient success criteria.

## Result

Evaluation and alternatives recorded. Compiler/projection verification passed. No harness, source, test, workflow, or user worktree changes were applied by this evaluation. Only this proposal was added. Selection and implementation remain a separate user decision.
