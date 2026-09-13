# META HARNESS Roadmap Improvement Proposal
## Petri Nets as the Formal Control Core of AgentX Verified Work

**Target repository:** `oikumo/agentx`  
**Target document:** `sandbox/META_HARNESS_ROADMAP.md`  
**Focus:** META HARNESS architecture, Petri-net semantics, executable work IR, verification, recovery, and agent token economy  
**Status:** Proposed revision

---

## 1. Executive Summary

The current META HARNESS roadmap correctly identifies Petri nets as the most distinctive architectural feature in AgentX, but its strongest formulation — **“the net is the IR”** and **“the marking is task state”** — is too broad for the implementation that now exists.

AgentX has evolved into a richer hybrid system:

- a weighted P/T Petri net provides formal workflow and resource-control semantics,
- a live marking represents aggregate control state,
- typed task bindings preserve task identity, ownership, generation, scope, dependencies, checkpoints, results, and liveness,
- evidence records bind execution to real repository state,
- compiled policy and runtime guards evaluate facts that do not belong naturally inside an ordinary uncolored Petri net,
- transaction and recovery machinery coordinates authoritative mutation,
- behavioral mining and goal synthesis operate as proposal/analysis layers rather than uncontrolled self-modification.

This is stronger than a pure “Petri-net orchestrator.”

The roadmap should therefore adopt the following architectural thesis:

> **AgentX compiles repository work into an executable Work IR whose formal control core is a weighted P/T Petri net. The marking is authoritative for aggregate workflow and resource state. Typed, revision-coupled bindings carry task identity, ownership, scope, generations, checkpoints, dependencies, and evidence references. An action is legal only when the corresponding Petri transition is enabled and all typed policy/evidence guards allow it. The combined state transition is versioned, transactional, replayable, and independently verifiable.**

This formulation preserves the mathematical value of Petri nets without forcing strings, paths, hashes, timestamps, task identities, and external-effect receipts into the Petri model itself.

The main product opportunity is not merely concurrency control.

It is **decision-complete next-action guidance**:

- what actions are legal now,
- why an action is blocked,
- what exact obligation is missing,
- what action will satisfy it,
- what workflow states remain reachable,
- and what evidence is required before completion can become authoritative.

That is where Petri nets can make AgentX simultaneously **stricter and cheaper**.

---

# 2. Revised Product Thesis

The META HARNESS should not be described as a larger set of agent gates.

It should be described as a **compiler for verified repository work**.

The compiler takes:

1. the user request,
2. repository state,
3. declared acceptance criteria,
4. project policy,
5. available tools/runtime capabilities,

and emits:

1. a compact executable workflow/control representation,
2. the minimal context needed for the next valid action,
3. a verification/evidence contract,
4. a recoverable execution state,
5. an auditable completion result.

The Petri-net subsystem is the formal control layer of this compiler.

The primary product objective remains:

> **Complete more user-requested work correctly with fewer total model tokens, fewer failed attempts, less human recovery effort, and stronger evidence.**

The Petri architecture earns its place only where it contributes to one or more of:

- fewer invalid attempts,
- fewer sequential refusals,
- better resume/recovery,
- stronger concurrency correctness,
- earlier detection of impossible workflows,
- more compact state representation,
- clearer causal execution traces,
- lower reasoning burden,
- more trustworthy completion.

---

# 3. Replace “The Net Is the IR” with “The Net Is the Formal Control Core”

The current wording should be changed.

## 3.1 Current overly broad claim

> The net is the IR.  
> The marking is task state.

This is not fully true in the current implementation.

The runtime also depends on:

- named task bindings,
- task generation,
- owner/session identity,
- workspace identity,
- task scope,
- dependency versions,
- evidence digests,
- test/verifier results,
- liveness/heartbeat state,
- policy state,
- external repository effects.

Those facts are not represented completely by the ordinary P/T marking.

## 3.2 Recommended claim

> **The weighted P/T Petri net is the formal control core of the executable Work IR. Its marking is authoritative for aggregate workflow and resource state. Typed task bindings and evidence records carry identity-rich facts that are revision-coupled to the marking.**

The complete logical state should be understood as:

```text
S = (N, M, B, P, E, R, V)
```

Where:

- `N` = Petri-net structure,
- `M` = live aggregate marking,
- `B` = typed task bindings,
- `P` = compiled policy and guards,
- `E` = verification/evidence state,
- `R` = external-effect receipts,
- `V` = semantic, policy, and state revision identity.

This makes the runtime semantics explicit.

---

# 4. Formal Action Semantics

A user or agent action should not be considered legal merely because a P/T transition is enabled.

The correct semantics are:

```text
legal(action, S)
    =
petri_enabled(control_transition(action), M)
    AND
typed_guards_allow(action, B, P, E, R)
```

More formally:

```text
Enabled(a, S) =
    PetriEnabled(N, M, t_a)
    ∧
    Guard(P, B, E, R, a) = ALLOW
```

The typed guard layer should preserve the roadmap's richer decision vocabulary:

- `ALLOW`
- `DENY`
- `UNKNOWN`
- `ERROR`

For protected execution, only `ALLOW` authorizes the effect.

This distinction prevents the Petri net from becoming overloaded with concerns it is poorly suited to represent, such as:

- path ancestry,
- file scopes,
- content digests,
- timestamps,
- command identity,
- Git state,
- verification receipts,
- runtime capabilities.

---

# 5. Formalize the Binding-to-Marking Projection

AgentX already maintains named task bindings alongside aggregate work-state tokens.

This should become a first-class invariant.

For task-state places:

```text
projection(bindings) -> marking
```

A target verified-profile invariant is:

```text
M[p] == count(binding.place == p)
```

for task-managed places where anonymous tokens are not explicitly supported.

Examples:

```text
work_pending
work_active
work_verifying
work_integration_ready
work_integrating
work_done
```

During migration or compatibility operation, anonymous tokens may still be permitted, but the verified managed profile should tighten this relationship.

This gives AgentX a practical equivalent of a **colored-net projection** without requiring the core engine to become a colored Petri-net implementation.

---

# 6. Do Not Move to Colored Petri Nets Yet

The current uncolored weighted P/T kernel has important advantages:

- simple formal semantics,
- deterministic enabledness,
- atomic firing,
- exact invariants,
- tractable conformance,
- independent Python and TypeScript implementations,
- compact JSON serialization,
- understandable state-space exploration.

Task identity and data-rich state already live successfully in typed sidecars/bindings.

Moving to colored Petri nets now would introduce:

- more complex token equality,
- richer variable-binding semantics,
- much larger state spaces,
- additional engine semantics,
- more difficult cross-language conformance,
- greater debugging complexity,
- weaker implementation portability.

The current hybrid architecture should be treated as intentional:

> **uncolored formal control + typed identity/evidence state**

Colored or timed nets should remain future options only if the current abstraction demonstrably fails on real workloads.

---

# 7. Separate Three Kinds of Nets

AgentX now effectively contains three different Petri-net roles.

They must remain explicitly separate.

## 7.1 Operational control net

Represents:

- workflow phase,
- work queues,
- active work,
- verification lanes,
- integration lanes,
- resource capacity,
- concurrency state.

This net can be authoritative.

## 7.2 Synthesized goal/workflow net

Represents a proposed workflow derived from:

- task decomposition,
- dependencies,
- acceptance criteria,
- resources.

This should remain proposal-only until validated and compiled into the operational model.

## 7.3 Mined behavioral net

Represents observed historical behavior derived from ledger traces.

This is descriptive, not normative.

Observed behavior may:

- identify drift,
- suggest simplifications,
- suggest demotion candidates,
- expose repeated waste,
- produce optimization proposals.

It must never automatically become policy.

Recommended conceptual flow:

```text
GoalSpec
   |
   v
Compiler
   |
   v
Control IR
   |
   v
Execution trace
   |
   v
Behavior miner
   |
   v
Observed process
   |
   v
Compare / propose
```

The comparison must account for abstraction level. A phase-flow mined net and a pool-control operational net are not directly equivalent models.

---

# 8. Petri Nets Should Be Used for What They Are Best At

Petri nets are particularly strong for four AgentX problems.

## 8.1 Concurrency and resource ownership

Use places/tokens for:

- worker slots,
- test slots,
- integration slots,
- exclusive resources,
- pending/active/done counts,
- workflow lane occupancy.

Use invariants to validate capacity conservation.

## 8.2 Workflow legality

Use enabledness to determine which workflow transitions are possible.

This becomes highly valuable when surfaced to the agent as an actionable frontier.

## 8.3 Pre-execution workflow analysis

Use:

- reachability,
- deadlock detection,
- boundedness,
- place invariants,
- transition liveness,
- SCC analysis,

to detect broken orchestration before agent tokens are spent attempting it.

## 8.4 Replayable control provenance

A firing sequence is a compact causal history of how the workflow state changed.

But it must not be confused with proof that external work was correct.

---

# 9. Distinguish Control Provenance from Acceptance Evidence

The roadmap should change the phrase:

> “firing trace is replayable acceptance evidence”

to:

> **“firing trace is replayable control provenance.”**

A firing trace proves:

- the control state changed,
- the transitions occurred in an allowed sequence,
- resource/workflow movement was recorded.

It does not by itself prove:

- code was correct,
- tests ran,
- the tests corresponded to the final candidate,
- the requested behavior exists,
- the integrated artifact matches the verified artifact.

True acceptance evidence should be:

```text
control trace
+
content-bound verifier receipts
+
request/acceptance mapping
+
candidate identity
```

A final completion claim should therefore be derived from a joined evidence structure, not merely from the final marking.

---

# 10. Verification Must Be an Evidence-Guarded Transition

Goal synthesis currently maps acceptance into a `verified` place.

That is useful as a planning abstraction, but authoritative execution should distinguish work completion from independent verification.

Preferred model:

```text
ready
  |
  v
start
  |
  v
active
  |
  v
submit
  |
  v
submitted
  |
  v
verify[evidence_guard]
  |
  v
verified
```

The `verify` transition must require a trusted, content-bound verification receipt.

The transition must not become enabled simply because the agent claims success.

The verifier receipt should include at least:

```text
candidate_digest
base_commit
head_commit
policy_version
toolchain_identity
checks[]
acceptance_refs[]
timestamp
verifier_identity
```

Where practical, the evidence object should itself be hashed.

---

# 11. Long-Running Resources Need Start/Finish Semantics

A resource self-loop on one atomic transition does not model a resource being held during multi-step real-world work.

This:

```text
resource -> do_work -> resource
```

only means that the resource is available at firing time.

It does not represent holding the resource while an agent edits files, runs tests, or performs several tool calls.

For long-running work, use:

```text
ready + resource_free
        |
        v
      start
        |
        v
active + resource_held
```

then later:

```text
active + resource_held
        |
        v
      finish
        |
        v
done + resource_free
```

This pattern should be applied to any synthesized workflow where capacity must be held across an external activity.

---

# 12. Separate Engine Conformance from Workflow Certification

The existing cross-engine conformance suite is excellent, but it answers a different question from workflow correctness.

## Engine conformance asks

> Does this implementation obey the AgentX weighted P/T semantics?

## Workflow certification asks

> Does this particular generated/control net satisfy the safety and progress properties required for this task/profile?

Every structural net revision should therefore have an optional or required certification artifact.

Example:

```json
{
  "net_revision": 71,
  "net_digest": "sha256:...",
  "semantics_version": "ptn-v1",
  "analysis": {
    "reachable_complete": true,
    "reachable_states": 24,
    "deadlocks": [],
    "bounded": true,
    "required_goal_reachable": true,
    "resource_invariants": {
      "worker_slots": true,
      "test_slots": true
    },
    "liveness": {
      "work_start": true,
      "work_complete": true
    }
  }
}
```

If exploration truncates, the result must remain explicitly unknown.

Example:

```text
bounded = UNKNOWN
reason = state-space exploration truncated at max_states
```

Never convert incomplete analysis into a positive claim.

---

# 13. Preserve the “No Overclaim” Epistemics Everywhere

The Petri library already distinguishes:

- proven true,
- proven false,
- unknown/incomplete.

This should become a META HARNESS-wide rule.

User-facing guidance should distinguish:

```text
LEGAL
ILLEGAL
UNKNOWN
ERROR
```

Analysis should distinguish:

```text
PROVEN
DISPROVEN
UNKNOWN
```

Product copy should not say:

> “the workflow is deadlock-free”

unless the analysis proving that claim is complete.

Instead:

> “No deadlock was found in 1,000 explored states; analysis is incomplete.”

when that is the truth.

---

# 14. Make Petri Guidance a First-Class Product Experiment

If Petri nets are the primary architectural differentiator, they should not be deferred to a late P1 optimization item.

The fastest low-risk test of Petri value is **read-only next-action guidance**.

The initial experiment should keep enforcement identical and change only guidance.

## Baseline

Current behavior:

```text
attempt
-> refusal
-> repair
-> second attempt
-> another refusal
-> repair
-> valid action
```

## Petri-guided condition

```text
task boundary
-> one action-frontier query
-> legal actions + missing obligations + exact remedies
-> valid action
```

Measure:

- attempts per accepted task,
- repeat-refusal count,
- tokens to first valid action,
- reasoning/output tokens,
- one-shot guidance success rate,
- human intervention,
- total accepted-task cost.

This directly tests whether the Petri model improves agent behavior.

---

# 15. “Enabled Set” Must Mean the Legal Action Frontier

Raw P/T enabled transitions are not sufficient.

The product API should return the conjunction of:

- Petri enabledness,
- typed policy,
- evidence validity,
- identity/capability checks,
- workspace checks,
- dependency freshness.

Recommended output shape:

```json
{
  "revision": 91,
  "actions": [
    {
      "action": "edit src/foo.py",
      "transition": "work_edit",
      "petri_status": "enabled",
      "guard_status": "deny",
      "missing_obligations": [
        {
          "kind": "acceptance_receipt",
          "reason": "focused test approval missing",
          "remedy": "run omt_skip scope=tests ..."
        }
      ]
    },
    {
      "action": "run focused tests",
      "transition": "run_tests",
      "petri_status": "enabled",
      "guard_status": "allow",
      "missing_obligations": []
    }
  ]
}
```

The output should be:

- bounded,
- decision-complete,
- revision-stamped,
- expandable on demand.

The agent should not need to infer recovery steps from prose.

---

# 16. Resume State Should Be Derived from the Full Work IR

A marking-derived resume summary is useful, but insufficient.

Two active tasks may produce the same aggregate marking while differing in:

- task identity,
- owner,
- generation,
- checkpoint,
- scope,
- evidence,
- accepted dependencies.

Resume should therefore be a projection:

```text
Resume = project(N, M, B, E, R, V)
```

The marking supplies:

- workflow position,
- lane occupancy,
- resource availability.

Bindings/evidence supply:

- which task,
- which generation,
- where to resume,
- what has been verified,
- what is stale,
- what remains blocked.

The bounded resume digest should consume this structured state.

---

# 17. Use a Compact Parametric Control Net

The existing place cap and pool-net architecture point toward the correct long-term design:

> **small reusable control topology + typed task data**

Avoid compiling every task into a large custom graph unless its workflow genuinely differs.

The default operational net should remain compact.

Example control vocabulary:

```text
work_pending
work_active
work_verifying
work_integration_ready
work_integrating
work_done

worker_slots
test_slots
integration_slot
```

Task-specific facts belong in bindings:

```json
{
  "id": "T9",
  "place": "work_active",
  "owner": "worker-b",
  "generation": 4,
  "scope": ["src/foo"],
  "deps": [...],
  "checkpoint": "...",
  "results": [...]
}
```

This keeps formal analysis tractable while preserving named work.

---

# 18. Strengthen Transaction Authority Before Stronger Petri Claims

If the Petri work state is authoritative, its mutation protocol must be stronger than “usually consistent.”

The runtime should guarantee:

1. one authoritative writer transaction at a time,
2. revision check under lock,
3. idempotent command replay,
4. no acknowledged success without recoverable command identity,
5. readers observe a consistent revision generation,
6. interrupted transactions are reconciled before later mutation,
7. external effects are not treated as committed merely because in-memory state advanced.

The current pending-marker model should be strengthened.

A robust file-native option is immutable revision generations:

```text
.meta/.omt/net-revisions/
    000091/
        net.json
        sidecar.json
        overlay.json
        command.json
        manifest.json

CURRENT -> 000091
```

Commit process:

```text
write complete revision
-> fsync according to durability profile
-> atomically replace CURRENT
```

Readers:

```text
resolve CURRENT once
-> read only that immutable generation
```

This avoids torn multi-file reads.

If the existing file layout remains, then transaction reconciliation must be mandatory before all mutations and must reconstruct the original committed command/result identity.

---

# 19. External Effects Need a Transaction Protocol

Git worktrees, tests, shell commands, integrations, and file mutations are external effects.

A Petri transition cannot make an arbitrary external effect and local state update atomically.

Model effectful actions explicitly:

```text
eligible
  |
  v
reserved
  |
  v
effect_started
  |
  v
effect_attested
  |
  v
committed
```

For example, workspace claim:

```text
claim_requested
-> workspace_reserved
-> git_worktree_created
-> workspace_verified
-> claim_active
```

The final transition should require a receipt that proves:

- the workspace exists,
- it is a real linked checkout,
- it is based on the expected commit,
- it is associated with the expected task generation.

Do not swallow workspace-creation failure while leaving an apparently valid claim.

---

# 20. Complete the Managed-Execution Authority Boundary

Before “verified managed execution” is claimed, close the remaining authority gaps.

## Required properties

### Workspace reality

A claim must not become usable until the real workspace exists and is validated.

### Identity propagation

Every managed mutation must carry:

```text
task_id
generation
owner/session
workspace identity
expected revision
```

### Scope enforcement

The actual file path must be checked against declared task scope.

### Generation fencing

A stale generation must not:

- edit,
- checkpoint,
- submit,
- verify,
- integrate,
- publish results.

### Trusted verification

A caller-supplied Boolean or verdict must not be sufficient authority.

A trusted verifier must:

- execute or validate declared checks,
- bind them to the candidate,
- generate the evidence receipt,
- control the verification transition.

---

# 21. Semantic-Version the Petri Contract

AgentX currently maintains multiple conformant Petri implementations.

If firing traces become durable evidence, semantic identity must be explicit.

Each runtime bundle and trace should include something like:

```text
petri_semantics = "agentx-ptn-v1"
conformance_fingerprint = "sha256:..."
format_version = 1
```

A future semantic change must not silently reinterpret an old trace.

This is especially important when:

- replaying historical executions,
- comparing mined behavior,
- upgrading installations,
- importing/exporting nets,
- analyzing retained evidence.

---

# 22. Revised Roadmap Priorities

The next Petri work should be organized around **semantic closure and measurable product value**, not around adding more Petri features.

| Priority | Work | Outcome |
|---|---|---|
| P0 | Formal Work-IR contract | Clarifies what marking, bindings, evidence, and policy each own |
| P0 | Petri guidance experiment | Tests the main user-facing value immediately |
| P0 | Transaction/recovery closure | Makes authoritative state trustworthy |
| P0 | External-effect + workspace authority | Closes real-world state mismatch |
| P0 | Trusted verifier boundary | Prevents self-asserted verification |
| P1 | Compact workflow compiler | Compiles user work into control topology + bindings + guards |
| P1 | Per-net certification | Makes reachability/deadlock/invariant analysis operational |
| P1 | IR-derived resume | Makes Petri state useful across compaction/session restart |
| P2 | Process-mining optimization loop | Uses observed behavior to propose simplifications safely |
| Later | Colored/timed/hierarchical nets | Only if measured workloads require them |

---

# 23. Proposed Replacement for the Roadmap’s Petri Thesis

Recommended text:

> **The Petri net is the formal control core of AgentX's executable Work IR.** The net models workflow topology, resource capacity, concurrency, and aggregate lifecycle state; its live marking is authoritative for those control facts. Named task bindings are revision-coupled to the marking and carry identity-rich state such as task ID, owner, generation, scope, checkpoint, dependency versions, workspace identity, and evidence references. Compiled policy and evidence guards handle predicates that do not belong naturally inside an ordinary weighted P/T net.
>
> An agent action is legal only when its corresponding control transition is Petri-enabled and all typed guards evaluate to `ALLOW`. This lets the harness compute the legal action frontier before execution, replacing sequential trial-and-refusal with decision-complete guidance. Structural analysis can prove reachability, detect reachable deadlocks, validate conservation invariants, and report unknown results honestly when exploration is incomplete.
>
> A Petri firing trace is replayable **control provenance**, not sufficient acceptance evidence by itself. Acceptance is established only when control progression is joined with candidate-bound verification receipts and the original request/acceptance contract. This separation allows the workflow layer to remain formally analyzable while repository effects remain independently evidenced.
>
> Petri mechanisms are evaluated by measured outcome. The control core is foundational where managed guarantees depend on it; user-facing Petri mechanisms such as enabled-frontier guidance, mined optimization, and resume projections remain subject to task-cost measurement and can be reduced or removed if they do not improve accepted work.

---

# 24. Proposed Petri-Specific Acceptance Criteria

A future verified Petri-controlled profile should not be considered qualified until all of the following hold.

## State consistency

```text
marking/binding projection consistent
revision identity consistent
no torn multi-file reads
no unresolved transaction before new mutation
```

## Authority

```text
stale revision cannot commit
stale generation cannot perform managed effects
wrong workspace cannot edit
wrong owner cannot publish
out-of-scope path cannot mutate
```

## Verification

```text
verification transition requires trusted evidence
evidence bound to exact candidate
dependencies revalidated before integration
completion requires accepted integrated state
```

## Petri semantics

```text
engine conformance passes
required resource invariants hold
goal reachability result recorded
deadlock analysis result recorded
unknown/incomplete analysis reported honestly
```

## Recovery

```text
retry does not double-fire
crash after every authoritative write boundary is recoverable or fail-closed
task ownership can transfer without accepting stale generation output
external-effect ambiguity produces diagnosis, never silent success
```

## Economy

```text
enabled-frontier guidance reduces repeated refusal attempts
tokens-to-first-valid-action improves
no acceptance regression
human intervention does not increase enough to erase token savings
```

---

# 25. Benchmark Design for Petri Guidance

Use the same task and model under two conditions.

## Condition A — current harness

Current gate/refusal flow.

## Condition B — current harness + Petri legal-action frontier

No enforcement changes.

Before mutation boundaries, expose:

- currently legal actions,
- blocked actions,
- unmet obligations,
- exact recovery action,
- authority revision.

Measure:

```text
accepted outcome
tokens per accepted task
tokens per attempt
attempts per accepted task
repeat refusals
time to first valid mutation
human intervention
reasoning/output tokens
state query latency
```

Petri guidance is promoted only if the joint task cost improves without weakening acceptance.

---

# 26. Roadmap Decision Rules

The following decisions should be made explicit.

## Petri control core

Retained where required for managed execution correctness.

## Petri next-action guidance

Measured feature. Promote only if it reduces task cost or failed attempts.

## Behavioral mining

Advisory only.

## Goal synthesis

Proposal-only until workflow certification and evidence semantics are strong enough.

## Automatic structural self-modification

Deferred.

## Colored Petri nets

Deferred unless the aggregate-net + binding-projection architecture proves insufficient.

## Timed nets

Deferred; heartbeat/recovery time semantics should remain explicit typed state unless a strong formal-analysis use case emerges.

---

# 27. Main Architectural Invariants

These should become explicit design invariants.

### I-PN-01 — Formal control ownership

The Petri marking is authoritative only for workflow/resource control facts represented by the net.

### I-PN-02 — Binding projection

Managed named task bindings remain consistent with aggregate work-state tokens.

### I-PN-03 — No self-asserted verification

An agent cannot cause verified completion merely by reporting success.

### I-PN-04 — Control provenance is not acceptance

A valid firing sequence alone cannot establish user-request completion.

### I-PN-05 — Revision-coupled state

Marking, bindings, evidence references, and structural identity advance under one authoritative revision protocol.

### I-PN-06 — Honest analysis

Incomplete reachability analysis never produces a definitive safety/liveness claim.

### I-PN-07 — Mined behavior is descriptive

Observed traces can generate proposals, never silently modify normative policy.

### I-PN-08 — Long-running resources are held explicitly

Resources spanning external work use start/finish semantics rather than instantaneous self-loops.

### I-PN-09 — Engine conformance != workflow soundness

Cross-engine semantic conformance and per-net workflow certification are separate gates.

### I-PN-10 — External effects require receipts

Filesystem, Git, testing, integration, and other external actions require attested results before authoritative completion transitions.

---

# 28. Recommended Near-Term Work Packages

## Work Package A — Work IR Contract

Produce one design specification defining:

```text
N
M
B
P
E
R
V
```

and the legal-action function.

Acceptance:

- every current net/runtime field assigned to one authority domain,
- projection invariant defined,
- no ambiguous “marking is all state” wording remains.

## Work Package B — Legal Action Frontier

Extend `omt_net probe` or a new read-only operation.

Acceptance:

- one call returns legal and blocked actions,
- blocked actions include exact obligation and remedy,
- output is revision-stamped,
- no enforcement behavior changes,
- benchmarked against existing sequential refusal flow.

## Work Package C — Workflow Certificate

For every structural net revision, generate analysis metadata.

Acceptance:

- invariant checks,
- deadlock result,
- reachability completeness,
- goal reachability where applicable,
- explicit unknown status on truncation.

## Work Package D — Transaction Closure

Close command/revision/event recovery ambiguity.

Acceptance:

- fault injection after every write boundary,
- no double-fire,
- no acknowledged-but-unreplayable command,
- readers never observe mixed revisions.

## Work Package E — Verified External Effects

Start with workspace creation and verification.

Acceptance:

- claim becomes active only after real checkout verification,
- stale generation cannot use workspace,
- workspace/base identity included in evidence.

---

# 29. Final Recommended Direction

The Petri-net architecture should remain central to AgentX.

But its role should become more precise.

Do not make Petri nets responsible for everything.

Make them responsible for what they do exceptionally well:

- control flow,
- synchronization,
- concurrency,
- capacity,
- reachability,
- deadlock reasoning,
- causal workflow provenance.

Keep typed state responsible for:

- identity,
- file scope,
- ownership,
- generations,
- content hashes,
- timestamps,
- dependency versions,
- external effect evidence.

Then join both layers in one revisioned Work IR.

The strongest product thesis is therefore:

> **AgentX compiles repository work into an analyzable executable control protocol. Petri nets provide the formal workflow and resource semantics; typed bindings preserve named task identity and capabilities; evidence receipts bind control progression to real repository effects and verification. The resulting Work IR drives next-action guidance, concurrency control, recovery, resume, and explainable completion.**

The first Petri feature to prove its product value should be **legal-action frontier guidance**.

The first Petri feature to prove its systems value should be **transactionally authoritative managed execution**.

The first Petri feature to prove its formal value should be **per-net workflow certification**.

If those three succeed together, Petri nets become more than an implementation technique.

They become the reason META HARNESS can be both more rigorous and more efficient than a conventional coding-agent harness.
