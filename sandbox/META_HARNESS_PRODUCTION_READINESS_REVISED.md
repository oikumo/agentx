# META HARNESS: effectiveness, efficiency, and production readiness — revised qualification edition

**Date:** 2026-09-12  
**Source document:** `sandbox/META_HARNESS_PRODUCTION_READINESS.md`  
**Revision purpose:** incorporate review edits that turn the assessment into a clearer production-readiness and qualification specification.  
**Implementation status:** **no implementation fix is implied by this document revision.** Findings remain open until the repository contains passing regression evidence and the claimed runtime boundary is qualified.

> **Release verdict: NOT QUALIFIED**
>
> **Current defensible claim:** development assistance / scaffold.
>
> **Target next claim:** restricted verified solo execution.
>
> **Managed concurrent execution:** not qualified.
>
> **Assessment confidence:** high for the reproduced and source-inspected failure modes described below; this document is not itself a release certificate and does not substitute for a current qualification run.

---

## 1. Decision

META HARNESS is a substantial and useful development scaffold with a good foundation for a production tool. It is **not yet ready to provide dependable enforcement, verified completion, or managed concurrent execution guarantees**.

Its strongest demonstrated capabilities are:

- organizing development work;
- generating consistent policy artifacts;
- providing modular policy checks and actionable guidance;
- preserving useful task and knowledge context;
- detecting many known regressions.

Its weakest demonstrated capabilities are:

- reliably enforcing critical policy under internal failures;
- composing independent obligations without control-flow bypass;
- proving that completion corresponds to successful verification of the current candidate;
- mediating all mutation interfaces in the claimed execution boundary;
- durably acknowledging authoritative state changes;
- proving managed concurrency under competing writers and crashes;
- demonstrating that harness overhead improves accepted end-to-end work.

The highest-value next investment is a **reliability, qualification, and measurement program**. Close demonstrated enforcement and completion gaps, retain executable reproductions, establish total cost per independently accepted task, and only then expand preparation, knowledge, or concurrency machinery.

### 1.1 Release scope

The first production target is intentionally narrow:

- one trusted operator;
- one explicitly qualified local runtime profile;
- one explicitly qualified adapter;
- one workspace;
- one active writer;
- explicit mutation mediation boundaries;
- explicit verification boundaries;
- explicit degraded/read-only behavior when authority is unavailable.

Managed concurrency remains a separate capability and requires additional transaction, ownership, generation, isolation, crash-recovery, and integrated-candidate qualification.

### 1.2 What to preserve

Preserve:

- the canonical `.omt` policy and generated projections with reproducibility checks;
- modular gate implementations and actionable refusal messages;
- preflight and bounded context delivery;
- lightweight treatment of routine tasks;
- installation tiers, but do not equate them with qualified guarantees;
- behavioral tests and runtime compatibility canaries;
- feature-scoped TDD and test-state isolation;
- staged changes and content-bound verification as design directions;
- explicit task identity, resource modeling, knowledge retention, and the consolidated project backlog.

### 1.3 What to change first

1. Make critical policy and verification failures refuse the operation reliably.
2. Replace gate-chain short-circuiting with compositional obligation evaluation.
3. Define and qualify the mutation adapter boundary.
4. Separate progress, authorization, consultation, staging, and verification evidence.
5. Make authoritative writes durably acknowledged.
6. Make completion content-bound and verifier-bound.
7. Preserve every reproduced defect as an executable regression.
8. Qualify the restricted solo profile.
9. Only then qualify multi-writer concurrency.
10. Measure accepted outcomes and total task cost before adding process machinery.

---

## 2. Capability profiles and qualification boundaries

Installation tiers describe enabled features. **Capability profiles describe demonstrated guarantees.** Installing a feature set does not confer a production claim.

| Capability | Minimum defensible claim | Qualification boundary |
|---|---|---|
| Development assistance | Prepares relevant context, explains obligations, preserves progress, and surfaces diagnostics. | May operate on an unintegrated host, but must not claim its actions were mediated or verified. |
| Verified solo execution | Supported mutations are mediated; critical policy failures cannot silently permit them; accepted output has current verification evidence bound to the candidate. | One qualified adapter, workspace, runtime profile, filesystem model, and active writer. |
| Managed concurrent execution | Ownership, persistence, integration, and acceptance remain correct under competing workers, retries, stale generations, and enumerated failures. | Adds transaction authority, workspace isolation, idempotency, generation checks, crash recovery, and combined-candidate qualification. |

### 2.1 Threat model

The initial production threat model is **cooperative agents and operators that can make mistakes**.

A malicious process with unrestricted write access to the policy, enforcement code, state, and receipts is outside the reliable enforcement boundary of file-based hooks. Stronger adversarial guarantees require a separately protected execution or verification boundary.

### 2.2 Supported runtime profile

A release qualification record MUST identify all of the following:

| Field | Required qualification value |
|---|---|
| Host / adapter | Exact supported adapter and version/API contract |
| OpenCode | Exact qualified version or bounded compatible range |
| Bun | Exact qualified version or bounded compatible range |
| Python | Exact qualified version or bounded compatible range |
| OS | Qualified operating system(s) |
| Filesystem | Required atomicity, rename, locking, timestamp, and case-sensitivity assumptions |
| Repository mode | Normal checkout/worktree assumptions |
| Workspace identity | How repository/workspace identity is determined and validated |
| Symlink policy | Whether symlinks are followed, refused, or normalized |
| Mutation interfaces | Complete set of mediated operations |
| Shell/process policy | Whether shell mutation is mediated, prohibited, or outside the claim |
| Network policy | Whether network effects are trusted, mediated, or outside the claim |
| Verification toolchain | Exact required verifier/toolchain identity |
| State schema | State and evidence schema versions |
| Policy identity | Active policy/IR digest and compatibility identity |

A qualification is invalid if its adapter or runtime boundary is unknown.

---

## 3. Unit of value: a task contract with verifiable acceptance

The unit of value is **a user-requested change accepted against explicit behavior**, not a completed phase or a satisfied gate.

At preparation, bind the task to a compact contract containing:

- task identity;
- intended outcome;
- declared scope;
- observable acceptance cases;
- required mutation mediation profile;
- required verification profile;
- candidate/input identity rules;
- permitted waivers and their authority.

At acceptance, report:

- which acceptance cases passed;
- which candidate and input identity they apply to;
- verifier and toolchain identity;
- which obligations were evaluated;
- unresolved unknowns;
- waivers;
- whether the candidate is accepted, refused, or not qualified.

A phase declaration remains useful progress metadata. It is **not** the acceptance oracle.

Changes in scope or relevant inputs invalidate affected obligations and verification evidence.

Externally consequential actions such as publication retain their own authority even when implementation is accepted.

---

## 4. Normative decision semantics

### 4.1 Decision vocabulary

Every critical policy obligation evaluates to one of:

```text
ALLOW
DENY
UNKNOWN
ERROR
```

Meaning:

- **ALLOW** — required evidence is available and the obligation permits the action.
- **DENY** — the obligation is applicable and refuses the action.
- **UNKNOWN** — required evidence is unavailable or insufficient.
- **ERROR** — evaluation failed or authoritative state could not be read/validated.

For critical mutation and authority obligations:

```text
DENY, UNKNOWN, or ERROR => operation is refused
```

For non-authoritative hints and optional advice, failure may degrade without blocking unrelated work.

### 4.2 Composition rule

Independent obligations MUST compose. A successful obligation MUST NOT terminate evaluation of unrelated applicable obligations.

Each gate returns structured evidence, not traversal control:

```text
{
  obligation_id,
  applicability,
  decision,
  reason,
  evidence_identity,
  recovery_action
}
```

A single policy combiner produces the final action decision.

Gate ordering may affect diagnostics or cost, but reordering independent obligations MUST NOT change the final permission decision.

### 4.3 Degraded mode

If critical policy authority, state, or verification evidence is unavailable:

- diagnostics remain available;
- read-only inspection remains available where safe;
- protected mutation is refused;
- repair actions are narrowly authorized;
- the system MUST NOT convert missing authority into permission.

The degraded-mode result must be machine-readable. Human prose is not the only place where uncertainty is represented.

---

## 5. Evidence and limits

This assessment is based on source inspection, canonical policy/project documents, compiler/projection verification, historical suite results, and isolated behavioral probes of the real TypeScript modules.

The original isolated probes:

- used temporary roots and synthetic ledgers;
- invoked real hook/evaluator implementations;
- used synthetic tool arguments and a stubbed subprocess interface;
- did not execute unauthorized edits;
- did not modify real authorization records;
- did not prove an exploit through a live production adapter.

That distinction remains important: they demonstrate implementation decisions and failure modes, while live adapter coverage requires qualification.

### 5.1 Evidence lifecycle

Retain stable finding IDs F01–F12.

Each finding has one of these states:

```text
reported
reproduced
fixed
qualified
```

Definitions:

- **reported** — evidence or source inspection identifies a credible defect/risk.
- **reproduced** — a retained executable fixture demonstrates the failure.
- **fixed** — the affected revision passes a regression case that failed before.
- **qualified** — the fix passes through the claimed real runtime/adapter boundary plus all required release checks.

A source edit alone does not establish `fixed`.

A unit test alone does not establish `qualified`.

### 5.2 Required evidence bundle

Each finding closure MUST attach:

- finding ID;
- affected revision/content identity;
- retained fixture or command;
- expected outcome;
- actual outcome;
- runtime/adapter profile;
- policy/state/verifier identities;
- scope of the evidence;
- remaining limitations.

Temporary one-off probes are not sufficient qualification evidence.

---

## 6. Findings and concrete improvements

### Priority model

Use capability-specific blockers:

- **P0-SOLO** — blocks verified solo execution.
- **P0-CONCURRENT** — blocks managed concurrent execution but does not by itself block the restricted solo profile.
- **P0-QUALIFICATION** — blocks a release claim because evidence/qualification is insufficient.
- **P1** — required for efficient, maintainable, or truthful operation but not necessarily a standalone blocker.
- **P2** — optional expansion after evidence.

A finding may have more than one priority.

---

### F01 — Mutation coverage and path matching are incomplete

**Priority:** P0-SOLO.  
**Evidence:** source inspection and gate-chain probe.

The existing policy recognizes a bounded set of edit tools and extracts a scalar path. Mutation through shell or other host interfaces is not automatically mediated merely because repository policy files exist.

The path matcher also treats a non-wildcard entry without a trailing slash as an exact path, while policy classifications can encode prefixes. That can prevent a downstream obligation from seeing a path that the shared classifier otherwise recognizes as harness-owned.

**Required fix**

Normalize supported actions into an adapter-owned action envelope containing:

- operation type;
- complete affected-path set;
- normalized workspace identity;
- proposed content/diff where available;
- command/call identity;
- adapter identity.

Use one compiled matcher with explicit semantics:

```text
exact
directory
prefix
glob
```

Define behavior for:

- create;
- update;
- delete;
- move/rename;
- multi-file patch;
- directory targets;
- traversal;
- symlinks;
- path aliases;
- unsupported mutation forms.

Unknown mutation forms are refused in the verified profile.

**Acceptance**

A table-driven adapter contract covers every supported mutation form and path form. Every path classified as harness-owned reaches all applicable harness obligations. Unsupported mutation types yield an explicit refusal rather than silent bypass.

---

### F02 — Unexpected errors can convert critical denials into permission

**Priority:** P0-SOLO.  
**Evidence:** reproduced.

Critical enforcement currently includes fail-open behavior for internal exceptions and unknown/unhandled predicates.

**Required fix**

Adopt the normative `ALLOW / DENY / UNKNOWN / ERROR` semantics in §4.

Validate:

- complete IR schema;
- predicate vocabulary;
- required types;
- required variables;
- state compatibility;
- fallback compatibility.

Critical policy evaluation cannot silently default to allow.

If policy authority is unavailable, enter explicit degraded/read-only mode.

**Acceptance**

Inject:

- missing IR;
- invalid JSON;
- invalid types;
- unknown predicates;
- subprocess failure;
- timeout;
- missing authoritative state;
- incompatible schema.

Protected mutation remains refused with a stable machine-readable reason and recovery action. Optional guidance failure does not block unrelated read-only work.

---

### F03 — Passing one gate can skip independent obligations

**Priority:** P0-SOLO.  
**Evidence:** reproduced.

The current specialized test gate can terminate traversal after approval, which can skip later independent obligations.

**Required fix**

Remove success-driven chain termination for independent gates.

All applicable obligations evaluate to structured decisions, and a central combiner decides.

Early exit is permitted only after an irrevocable refusal when remaining evaluation is explicitly unnecessary for authorization; if skipped, diagnostics must record which checks were not evaluated.

**Acceptance**

Test approval permits the edit only after all other applicable obligations pass.

Pairwise and multi-gate cases cover:

- test approval + concurrency;
- test approval + thought consultation;
- test approval + receipt requirement;
- protected-path exception combinations.

Reordering independent gates does not change the permission result.

---

### F04 — Authorization, progress, and consultation have inconsistent scope and lifetime

**Priority:** P0-CONCURRENT; P1-SOLO.  
**Evidence:** reproduced/source-inspected.

Compatibility fallbacks and inconsistent lifetime helpers can allow session scope and authorization lifetime to diverge.

**Required fix**

Represent progress, authorization, consultation, and verification as distinct record types with explicit:

- subject;
- workspace;
- session or task scope;
- feature/task scope;
- issued-at time;
- expiry;
- revocation identity;
- issuing authority;
- policy generation.

No progress event implicitly grants authority.

No consultation event implicitly grants mutation authority.

Managed mode MUST NOT fall back from a missing session grant to another session's recent grant.

**Acceptance**

- Session A's grant cannot authorize session B in managed mode.
- Expired grants are rejected by every consumer.
- Phase advancement neither silently revokes nor broadens authority.
- Progress survives authorization expiry.
- Revocation/abandon events affect only their intended scope.

---

### F05 — Completion can succeed without successful verification

**Priority:** P0-SOLO.  
**Evidence:** reproduced.

Completion must never interpret missing verifier output or failed process status as successful verification.

**Required fix**

Define a versioned verifier response and require all of:

- process exit success;
- response parse success;
- expected response schema;
- explicit verification outcome;
- required check set present;
- candidate identity match;
- verification-input identity match;
- toolchain identity match;
- persistence acknowledgment before reporting completion.

No fallback such as empty-output => `ok:true` is permitted.

**Acceptance**

None of the following can produce verified Done:

- nonzero verifier exit;
- empty output;
- malformed response;
- timeout;
- no collected tests when tests are required;
- missing required suite;
- wrong toolchain;
- stale candidate;
- failed persistence acknowledgment.

A positive control through the same interface completes successfully.

---

### F06 — Staging lacks an enforced verification boundary

**Priority:** P0-SOLO when staged/batch acceptance is part of the claimed profile; otherwise P1 until that capability is enabled.  
**Evidence:** reproduced/source inspection.

A stage record that only identifies files/snapshots is not itself a verification lifecycle.

**Required fix**

A stage is an owned, versioned candidate state with:

- task/feature identity;
- workspace identity;
- owner/session where relevant;
- candidate digest;
- input manifest;
- active policy digest;
- creation time;
- expiry/lifecycle state;
- verification state;
- terminal consumption state.

A later relevant edit invalidates verification.

Successful acceptance consumes or advances the stage atomically.

**Acceptance**

- Two sessions cannot overwrite each other's stage in a profile that supports multiple sessions.
- Stale, failed, unrelated, or unowned stages cannot authorize acceptance.
- Successful finish consumes the stage.
- Later relevant edits invalidate prior acceptance evidence.
- Recovery does not overwrite user changes.

---

### F07 — Receipt fields do not yet form a complete evidence contract

**Priority:** P0-SOLO.  
**Evidence:** source inspection and reproduced helper behavior.

Receipt presence is not equivalent to valid current verification.

**Required fix**

Define a versioned evidence manifest that includes, at minimum:

- candidate digest;
- relevant input manifest/digests;
- policy identity;
- verifier identity/version;
- toolchain identity;
- required checks;
- actual results;
- timestamps as metadata, not the primary truth;
- scope label such as targeted/full-suite;
- evidence generation;
- raw verifier evidence reference where appropriate.

Missing required fields are invalid, not compatibility-success.

**Acceptance**

- Missing or mismatched required fields refuse acceptance.
- Changed tests, dependencies, policy, toolchain, or relevant configuration invalidate affected evidence.
- Unrelated changes do not trigger unnecessary reruns when dependency closure is proven.
- Targeted evidence is never labeled as a full-suite pass.

---

### F08 — Revision checking and file replacement are not a transaction authority

**Priority:** P0-CONCURRENT.  
**Evidence:** source inspection; race/crash cases require retained reproductions.

Checking revision N and then writing N+1 without an atomic commit boundary does not prevent two writers from both succeeding.

Sequential replacement of multiple authoritative files plus a later ledger append is not a transaction.

**Required fix**

Define one transaction authority for managed concurrency with:

- compare-and-commit semantics;
- command ID;
- idempotency;
- generation/revision identity;
- write-ahead or equivalent recoverable commit protocol;
- atomic visibility of the authoritative state;
- event/state commit relationship;
- crash recovery.

Do not maintain two independent authoritative stores.

**Acceptance**

- Two processes starting from N cannot both commit incompatible N+1 states.
- Same command ID + same payload is idempotent.
- Same command ID + different payload is refused.
- Kill after every persistence step recovers to a complete old or complete new state.
- Disk-full or failed event write cannot be acknowledged as a successful commit.

---

### F09 — Best-effort state writes and whole-file rollback weaken recovery

**Priority:** P0-SOLO for authoritative acknowledgment; P0-CONCURRENT for shared-file ownership/recovery.  
**Evidence:** failed-write behavior reproduced; overwrite risk source-inspected.

An authoritative write helper that swallows write errors cannot support a trustworthy success acknowledgment.

Recovery that replaces whole files can overwrite intervening user/worker changes.

**Required fix**

Authoritative persistence MUST return a durable acknowledgment or an error.

Readers MUST distinguish:

- valid record;
- corrupt record;
- incompatible record;
- missing record.

Recovery must be candidate/ownership aware and preserve newer unrelated changes.

**Normative durability invariant**

> No command that changes authoritative state may report success until its durable state transition and corresponding audit identity share a committed command identity.

**Acceptance**

- Write failure cannot produce success.
- Replay is deterministic and detects gaps/corruption.
- Interrupted rotation loses no acknowledged event.
- Workspace identity cannot redirect another workspace's state.
- Recovery preserves intervening edits unless explicit authority permits replacement.

---

### F10 — Preflight and task preparation need a truthful shared snapshot

**Priority:** P1; P0-SOLO only if preflight is marketed as an authoritative permission answer.  
**Evidence:** source inspection.

Prediction must not label unavailable live evidence as allowed.

**Required fix**

Preflight and live enforcement consume the same normalized action model and policy evaluator.

Snapshot fields explicitly represent unavailable evidence.

Machine-readable status distinguishes:

```text
allowed
refused
unknown
error
not_applicable
```

**Acceptance**

- Same action + same complete snapshot => equivalent obligations and decision across consumers.
- Unknown never renders as "all clear".
- Preparation does not fabricate consultation or approval.
- Routine preparation reduces demonstrably redundant calls while preserving low-level repair tools.

---

### F11 — Context and knowledge budgets should track relevance and delivered size

**Priority:** P1.  
**Evidence:** source inspection/navigation behavior.

A consultation flag proves an access event, not that relevant current knowledge was delivered.

**Required fix**

Bind reusable knowledge to:

- affected surface;
- source/policy version;
- freshness identity;
- retrieval reason;
- delivered content size;
- task relevance.

Track successful retrieval and avoided rediscovery rather than consult counts alone.

**Acceptance**

- Relevant changed knowledge refreshes consultation.
- Unrelated changes do not.
- Representative labeled task queries retrieve expected current lessons.
- Large records remain reachable through bounded continuation.
- Stale operational advice can be retired using evidence.

---

### F12 — Tests and release qualification need stronger behavioral independence

**Priority:** P0-QUALIFICATION; P1 for execution cost.  
**Evidence:** existing tests/configuration and historical suite result.

Source-string pins are useful but cannot establish composed runtime behavior. A syntactically present guard can still be bypassed by ordering, ignored subprocess status, adapter gaps, or persistence failure.

**Required fix**

Create a qualification suite with independent layers:

1. pure evaluator tests;
2. retained F01–F12 regression fixtures;
3. adapter contract tests;
4. real-adapter allow/refuse smoke tests;
5. completion/verifier contract tests;
6. persistence fault injection;
7. clean-install/upgrade/recovery checks;
8. concurrency race/crash checks for managed mode.

Critical seeded defects MUST fail behavioral checks even if source pins remain green.

**Acceptance**

A candidate cannot be labeled production-ready with:

- any failed required qualification check;
- an untested claimed adapter;
- stale evidence;
- an unqualified runtime profile;
- unresolved P0 blockers for the capability being claimed.

---

## 7. Executable invariant register

The production design should preserve these outcome properties.

| ID | Invariant | Minimum failure test | Scope |
|---|---|---|---|
| I01 — Complete mediation | Every supported protected mutation is normalized and evaluated; unsupported mutation is explicit. | Attempt each adapter mutation form, including multi-file and rename/delete. | Solo + concurrent |
| I02 — Critical fail-closed | Missing/invalid authority cannot become permission. | Remove/corrupt policy/state/verifier dependencies. | Solo + concurrent |
| I03 — Independent obligations compose | Passing one obligation cannot suppress another applicable obligation. | Pairwise and multi-gate permutations. | Solo + concurrent |
| I04 — Truthful completion | Done implies required verification succeeded for the accepted candidate. | Failed/empty/malformed/stale verifier cases. | Solo + concurrent |
| I05 — Durable acknowledgment | Success implies the authoritative transition is durably recoverable under the qualified failure model. | Fail/kill after each persistence boundary. | Solo + concurrent |
| I06 — Current evidence | Acceptance evidence matches candidate, required inputs, policy, verifier, and toolchain. | Mutate each relevant input dimension independently. | Solo + concurrent |
| I07 — Truthful prediction | Same action/snapshot yields the same obligations; unavailable evidence stays unknown. | Remove live evidence and compare preflight vs enforcement. | Solo + concurrent |
| I08 — Preserved work | Recovery does not overwrite newer user/worker content without authority. | Insert intervening edit before recovery. | Solo; stronger concurrent cases |
| I09 — Ownership isolation | Authority/staging/locks cannot leak between unrelated tasks/sessions/workspaces. | Competing session/workspace fixtures. | Concurrent; selected solo session cases |
| I10 — Idempotent command handling | Duplicate delivery cannot duplicate or conflict with authoritative transitions. | Same/different payload with repeated command ID. | Concurrent; useful solo robustness |

These are outcome properties, not a request for ten new gates.

---

## 8. Action lifecycle and execution boundary

A correct decision is insufficient if the world changes between check and effect.

Use a bounded lifecycle:

```text
normalize action
  → establish workspace + policy generation
  → read consistent snapshot
  → evaluate all applicable obligations
  → refuse OR obtain execution token/conditional authority
  → apply effect through qualified adapter
  → validate resulting candidate
  → durably acknowledge authoritative state/audit identity
```

For multi-file actions:

- prevent partial application; or
- use a recoverable staged publication with explicit incomplete state.

Do not hold a global state lock while long-running tests execute.

Instead:

```text
freeze candidate
  → verify outside short critical section
  → conditionally accept by rechecking candidate + ownership + evidence
```

If the host cannot mediate the check-to-write boundary, document that limitation and restrict the claim. An after-write hash can detect drift but cannot retroactively prevent a write.

### 8.1 Self-modification

A proposed policy or enforcement implementation MUST NOT authorize its own activation.

The currently trusted generation controls editing and qualification of its successor.

Activation records include:

- old policy identity;
- proposed policy identity;
- compiler identity;
- adapter compatibility identity;
- state-schema compatibility;
- qualification evidence;
- recovery target.

In-flight work is explicitly pinned or re-evaluated. No operation silently mixes two policy generations.

---

## 9. Evidence contract

Candidate identity must cover relevant uncommitted and untracked inputs, not just `HEAD` or the edited target.

Where relevant, identity includes:

- content digest;
- file mode;
- deletion;
- symlink target;
- generated/input distinction;
- dependency/configuration inputs.

Verification inputs and generated runtime outputs must be separated so that receipts/logs do not recursively change the candidate they describe.

If a verifier unexpectedly modifies a source, test, dependency, or configuration input, invalidate the run rather than issuing evidence for the pre-run digest.

A conservative declared input manifest is preferred initially. Narrow dependency-aware invalidation only after tests demonstrate that it is sound.

---

## 10. Degraded operation and recovery

Failing closed should prevent unsupported authority without making diagnosis impossible.

| Failure | Continued capability | Required restriction / recovery |
|---|---|---|
| Policy/IR unavailable or invalid | Read-only diagnosis, policy inspection, repair tooling | Protected mutation refused; activate only a verified compatible policy |
| Ledger/state unavailable or corrupt | Read-only diagnosis, export, reconciliation | No authoritative mutation or false progress acknowledgment |
| Verifier unavailable | Authorized development may continue where policy permits | Candidate cannot be accepted/Done |
| Receipt stale | Development continues with stale status visible | Reverify before acceptance |
| Optional KB/navigation unavailable | Core policy may continue if independent | Mark advice unavailable; do not invent consultation |
| Failed state acknowledgment | Diagnosis + command-status reconciliation | Do not blindly retry non-idempotent command or report success |
| Adapter capability unknown | Inspection only | Refuse protected mutation in verified profile |
| Incompatible state generation | Recovery/migration path | No implicit downgrade/upgrade authorization |

Recovery begins by identifying:

- workspace;
- last valid policy generation;
- last valid state generation;
- unfinished command IDs;
- current user changes;
- current candidate/evidence status.

Restore or reconcile in a disposable location where possible, validate it, then conditionally activate.

A repair path MUST NOT grant itself unlimited authority.

---

## 11. Policy evolution

Avoid another independently maintained policy copy across Python, TypeScript, prose, and tests.

Prefer typed policy data plus a small primitive implementation registry.

Migrate one obligation at a time.

For each migration, replay a fixed labeled action corpus against old and proposed evaluators and classify differences as:

```text
stricter
more_permissive
unknown_or_error
explanation_only
```

The old evaluator is a comparison baseline, not the correctness oracle.

Promotion requires:

- every newly permitted operation has explicit rationale and acceptance coverage;
- every newly refused valid operation has a resolution;
- required fault cases pass;
- adapter/state schema compatibility is recorded;
- forward migration and recovery are both demonstrated.

Shadow evaluation observes; it never authorizes.

---

## 12. Measurement and service objectives

### 12.1 Primary outcome metrics

Use at least:

| Measure | Definition |
|---|---|
| Behavioral acceptance rate | Independently accepted attempts / all attempts |
| Total cost per accepted task | Total runtime usage/spend across successes, failures, retries, verification, and recovery / accepted tasks |
| Accepted throughput | Independently accepted tasks / elapsed execution time |
| Forbidden-action detection | Critical seeded invalid actions correctly refused |
| False-refusal rate | Valid labeled actions wrongly refused |
| Recovery burden | Recovery time and user intervention per accepted task |
| Evidence invalidation quality | Stale evidence wrongly reused vs valid evidence unnecessarily rerun |
| Adapter coverage | Supported mutation forms exercised through the real adapter |
| Decision latency | Pure/local policy decision distribution on a documented machine/profile |

Human intervention minutes should be reported separately unless an explicit conversion is agreed.

If nothing is accepted, report the denominator as zero rather than hiding the result.

### 12.2 Telemetry

Capture:

- action/tool start/end;
- normalized action type;
- decision status/reason;
- policy/state/evidence generation;
- cache hit/miss;
- subprocess time/result;
- persistence acknowledgment;
- output bytes;
- usage/cost where available.

Do not capture secrets or unnecessary content in routine telemetry.

### 12.3 Proposed initial targets

These are **proposals, not achieved results**:

- All enumerated critical fault/forbidden-action cases are refused.
- Every positive control succeeds.
- Any missed critical case blocks the affected capability claim.
- Benchmark current local decision overhead before setting a hard SLO; p95 under 100 ms may be tested for pure/local decisions on a documented machine, excluding verification execution.
- At increasing retained-history sizes, current-task decisions depend on active snapshot/indexes rather than repeated full-history scans.
- Zero acknowledged authoritative events are lost in the enumerated process-kill tests for the qualified storage profile.
- Routine preparation returns task identity, current state, obligations, and next action in one bounded response when the evidence is available.

---

## 13. Executable release-gate matrix

The release decision is made from this table, not from feature count or installation tier.

| Requirement | Development assistance | Verified solo | Managed concurrent | Evidence required | Blocker class |
|---|---:|---:|---:|---|---|
| Explicit supported runtime profile | Recommended | Required | Required | Versioned qualification record | P0-QUALIFICATION |
| Complete qualified mutation adapter | No guarantee | Required | Required | Real-adapter contract suite | P0-SOLO |
| Critical failures fail closed | No guarantee | Required | Required | Fault-injection suite | P0-SOLO |
| Independent obligations compose | No guarantee | Required | Required | Gate permutation/regression suite | P0-SOLO |
| Completion requires successful verifier | No guarantee | Required | Required | Completion contract suite | P0-SOLO |
| Candidate/input-bound evidence | No guarantee | Required | Required | Evidence invalidation suite | P0-SOLO |
| Durable authoritative acknowledgment | Best effort allowed if not marketed as authority | Required | Required | Persistence fault suite | P0-SOLO |
| Session/workspace authorization isolation | Best effort | Required for claimed session semantics | Required | Scope/lifetime tests | P0-SOLO/P0-CONCURRENT |
| Atomic competing-writer commit | Not required | Not required for one-writer profile | Required | Multi-process race/crash suite | P0-CONCURRENT |
| Idempotent command handling | Recommended | Recommended | Required | Duplicate-delivery suite | P0-CONCURRENT |
| Combined-candidate verification | Not required | N/A | Required | Integration acceptance suite | P0-CONCURRENT |
| Clean install/upgrade/recovery | Recommended | Required | Required | Disposable-repo qualification | P0-QUALIFICATION |
| Retained F01–F12 regressions | Recommended | Required for applicable blockers | Required | Checked-in fixtures | P0-QUALIFICATION |
| No failed required checks | N/A | Required | Required | Qualification summary | P0-QUALIFICATION |
| Efficiency baseline | Recommended | Required before process expansion | Required | Controlled benchmark | P1 |

---

## 14. Prioritized implementation sequence

This sequence is deliberately narrower than a broad architecture rewrite.

### Slice 1 — Make completion truthful

Close F05 first.

Deliver:

1. retained reproduction for nonzero verifier exit + empty output;
2. positive control through the same interface;
3. versioned verifier response;
4. explicit process-status handling;
5. malformed/empty/timeout/missing-check coverage;
6. candidate/toolchain identity validation;
7. persistence acknowledgment before Done.

**Exit:** false-success completion is impossible in the enumerated verifier/persistence failures.

**Limit:** this does not yet qualify verified solo execution.

### Slice 2 — Fix critical decision semantics

Close F02 and F03:

- structured `ALLOW/DENY/UNKNOWN/ERROR`;
- fail closed for critical authority;
- compositional independent obligations;
- retained fault-injection and gate-permutation cases.

### Slice 3 — Define the adapter boundary

Close F01:

- normalized action envelope;
- exact/directory/prefix/glob semantics;
- full affected-path set;
- unsupported mutation refusal;
- real-adapter contract tests.

### Slice 4 — Make state acknowledgment truthful

Close the solo-relevant part of F09:

- authoritative write errors propagate;
- command/result acknowledgment is explicit;
- corruption is visible;
- recovery preserves current user work.

### Slice 5 — Bind acceptance evidence

Close F06/F07 as required by the selected solo lifecycle:

- stage ownership/lifecycle;
- candidate/input manifest;
- verifier/toolchain identity;
- evidence invalidation;
- consumed terminal state.

### Slice 6 — Retain the qualification suite

Close F12 for the solo profile:

- every reproduced defect becomes a checked-in fixture;
- clean install;
- real-adapter allow/refuse path;
- upgrade;
- recovery;
- seeded critical-defect detection.

### Slice 7 — Qualify restricted solo execution

Run the complete release-gate matrix for the exact runtime profile.

Only after all required solo blockers are `qualified` may the release claim say:

> Verified solo execution qualified for profile `<profile-id>`.

### Slice 8 — Establish baseline efficiency

Run representative tasks and record behavioral acceptance, total cost per accepted task, throughput, false refusals, and recovery burden.

Do not optimize byte budgets or add mandatory consultation solely because a representation ceiling is close.

### Slice 9 — Implement managed concurrency

Then address:

- F04 managed scope;
- F08 transaction authority;
- F09 competing-owner recovery;
- idempotency;
- generation checks;
- isolated workspaces;
- combined-candidate verification;
- race/crash qualification.

Only then may managed concurrency be claimed.

---

## 15. Release acceptance checklist

### 15.1 Restricted verified solo release

- [ ] Exact runtime/adapter/OS/filesystem/threat-model profile documented.
- [ ] Real adapter mediates every mutation type included in the claim.
- [ ] Unsupported mutation types are explicitly refused.
- [ ] F01 applicable solo cases are fixed and qualified.
- [ ] F02 is fixed and qualified: critical errors/unknowns cannot permit protected mutation.
- [ ] F03 is fixed and qualified: independent obligations compose.
- [ ] F04 solo-relevant scope/lifetime behavior is qualified.
- [ ] F05 is fixed and qualified: failed verification cannot produce Done.
- [ ] F06 is fixed/qualified if staged acceptance is part of the profile.
- [ ] F07 is fixed and qualified: acceptance evidence is content/input/toolchain bound.
- [ ] F09 solo durability and preserved-work cases are qualified.
- [ ] F10 cannot label unknown permission as allowed if preflight is part of the claim.
- [ ] F12 qualification suite is independent enough to catch seeded critical defects.
- [ ] Every reproduced blocker has a retained fixture.
- [ ] Clean install succeeds in a disposable repository.
- [ ] One valid workflow succeeds through the real adapter.
- [ ] Representative forbidden workflows are refused through the real adapter.
- [ ] Upgrade and recovery are exercised without losing user content.
- [ ] Required compiler/projection checks pass.
- [ ] Required behavioral suite passes.
- [ ] No required release check is red.
- [ ] Evidence references the exact candidate/runtime/policy profile being released.
- [ ] Release notes clearly state the one-writer boundary and out-of-scope guarantees.

### 15.2 Managed concurrent release

All restricted solo items above, plus:

- [ ] Session/task/workspace authority isolation is qualified.
- [ ] One transaction authority governs concurrent authoritative state.
- [ ] Two writers cannot both commit incompatible successors.
- [ ] Duplicate command delivery is idempotent.
- [ ] Same command ID with a different payload is refused.
- [ ] Crash after every persistence boundary recovers to a valid old/new state.
- [ ] Competing workers use isolated candidates/workspaces where required.
- [ ] Ownership cannot leak or be silently stolen.
- [ ] Stale generation publication is refused.
- [ ] Integrated candidate is independently verified before acceptance.
- [ ] Recovery preserves other workers' and user changes.
- [ ] Concurrency stress/race suite passes through the claimed runtime boundary.
- [ ] Capacity limits for verification and integration are documented.

---

## 16. Qualification report template

Every production release should generate a compact immutable report:

```yaml
qualification:
  capability: verified_solo | managed_concurrent
  result: qualified | not_qualified
  candidate:
    revision: ...
    content_digest: ...
  profile:
    adapter: ...
    host_version: ...
    bun: ...
    python: ...
    os: ...
    filesystem: ...
    state_schema: ...
    policy_digest: ...
    verifier: ...
    toolchain: ...
  required_findings:
    F01: qualified
    F02: qualified
    ...
  checks:
    adapter_contract: pass
    fault_injection: pass
    completion_contract: pass
    persistence_faults: pass
    clean_install: pass
    upgrade_recovery: pass
    full_required_suite: pass
  limitations:
    - ...
  evidence_refs:
    - ...
```

If any required field is absent, stale, or failed, the result is `not_qualified`.

---

## 17. Current release decision

At the time of this revised assessment, the appropriate release decision remains:

### Development assistance

**Usable with explicit limitations.**

The harness provides meaningful organization, policy projection, guidance, testing infrastructure, and state visibility.

### Verified solo execution

**NO-GO until the P0-SOLO and P0-QUALIFICATION requirements in the release matrix are qualified.**

The first target is realistic and does not require the entire concurrent platform.

### Managed concurrent execution

**NO-GO.**

It additionally requires transaction authority, ownership isolation, idempotency, crash recovery, generation control, and integrated-candidate verification.

---

## 18. Review conclusion

The central architecture direction remains sound: evolve the existing compiler, gates, state, verification, knowledge mechanisms, and project backlog rather than replacing them wholesale.

The production-readiness program should now be judged by **executable invariants and accepted outcomes**, not by:

- gate count;
- phase count;
- installed tier;
- consultation count;
- source-string presence;
- byte-budget utilization;
- existence of a receipt;
- existence of a state revision;
- feature completion status.

The next meaningful milestone is not "more harness."

It is:

> **A narrowly defined verified-solo profile in which every supported protected mutation is mediated, critical uncertainty fails closed, independent obligations compose, accepted output is bound to successful current verification, and authoritative state changes are durably acknowledged.**

Only after that profile is independently qualified should managed concurrency become a release claim.
