# META HARNESS V2 Roadmap

## Executive summary

META HARNESS has reached the point where another roadmap of gates, helper tools, and local ergonomics would be the wrong next move. The current system already contains a substantial policy compiler, a data-driven OpenCode enforcement layer, a weighted P/T Petri-net engine, transaction and generation fencing, task bindings, work lanes, recovery machinery, evidence/dependency checks, process mining, task preparation, and a compact resume surface. The remaining V1 work is primarily about proving economics, closing qualification gaps, and packaging a supported workflow—not inventing another coordination substrate.[^1][^2]

V2 should therefore be a **semantic consolidation and platformization roadmap**. Its central objective is to turn the mechanisms built during V1 into a stable, adapter-neutral **executable Work IR** and a compiler/runtime contract that can be qualified, replayed, benchmarked, and eventually executed by more than one coding-agent runtime.

The core architectural decision should be:

> **The weighted P/T Petri net is the formal control core of the Work IR, not the whole Work IR.**

The Petri net should remain responsible for what it models well: workflow legality, synchronization, resource capacity, concurrency, reachability, deadlocks, and causal control provenance. Named task identity, workspace identity, generations, scopes, dependency versions, content digests, verifier results, and external-effect receipts should remain typed state coupled to the same authoritative revision. The present runtime already behaves this way: the live marking is paired with task bindings that carry identity-rich state and evidence-related fields.[^3]

V2 should formalize that design rather than replacing it with colored, timed, or hierarchical Petri nets. The generic Petri library is intentionally small, deterministic, completeness-aware, and easy to conform across implementations.[^4][^5] The existing JSON interchange format is likewise intentionally structural and M0-only.[^6] Those are strengths. V2 should add a **Work IR format above the Petri format**, not overload the Petri format until it becomes a second workflow programming language.

The target end-state is:

```text
User request + repository snapshot + acceptance contract + policy + runtime capabilities
                                      |
                                      v
                              Work IR Compiler
                                      |
                                      v
        +----------------------------------------------------------+
        | Executable Work IR                                       |
        |                                                          |
        | request anchor + acceptance cases                        |
        | weighted P/T control net + marking                       |
        | named task bindings + generations + scopes               |
        | typed policy/evidence guards                             |
        | external-effect contracts + receipts                     |
        | evidence manifests + dependency identities               |
        | semantic/profile/revision identities                     |
        +----------------------------------------------------------+
                       |                         |
                       v                         v
               Legal Action Frontier      Workflow Certificate
                       |
                       v
              Adapter-neutral Runtime
                       |
          +------------+-------------+
          |                          |
          v                          v
     OpenCode adapter           second adapter
          |                          |
          +------------+-------------+
                       |
                       v
          effect receipts + verification
                       |
                       v
             evidence-backed result
                       |
                       v
             replay / mining / optimization
```

The V2 success condition is not “more formalism.” It is that one compiled work description can drive **guidance, enforcement, resume, recovery, verification, replay, and multi-agent coordination** while reducing semantic duplication and preserving or improving accepted-task economics.

---

## 1. Scope and V1 handoff assumption

This roadmap is explicitly a **post-V1 roadmap**. It assumes the V1 roadmap's exit criteria have been implemented and qualified before V2 claims depend on them.

That distinction matters because the repository inspected for this analysis is not yet at that hypothetical handoff. At commit `33c9eaa2a811533902ccb953aad04b43aa397e2b`, the active project records the task-cost benchmark and selective knowledge pilot as still remaining, while the current V1 roadmap itself still labels verified solo and managed concurrent execution as unqualified at its review baseline.[^1][^2] The current tree does record major new implementation slices as shipped—including transaction authority, task generations, worktree metadata, two-worker capacity, verification/integration lanes, recovery, evidence dependencies, budget controls, scaffolding, and a compact resume digest—but “feature shipped” is not equivalent to “product guarantee qualified.”[^2]

Therefore:

- **Current-repository gaps are not silently promoted into V2 assumptions.**
- **V1 qualification defects must be closed before the corresponding V2 guarantee is advertised.**
- V2 can be designed now, but its release gates begin from a frozen, qualified V1 profile.

### V2 entry gate

Before `meta_harness_v2` is allowed to claim a stable Work IR or verified runtime profile, the V1 handoff must contain:

1. a retained task-cost baseline and accepted-task benchmark;
2. a supported clean-install profile on non-AgentX repositories;
3. a normalized action/effect mediation contract for supported mutations;
4. critical authority failures that fail closed in the verified profile;
5. independent gate composition with no early-stop suppression of later obligations;
6. candidate-bound, trusted verification rather than caller-supplied success;
7. durable authoritative writes and tested transaction recovery;
8. real workspace isolation for managed execution, not metadata-only isolation;
9. task/generation/workspace identity propagated through every managed write path;
10. clean upgrade, rollback, resume, and recovery qualification;
11. explicit support boundaries and capability diagnostics;
12. a release report that distinguishes proven guarantees from unsupported paths.

If those conditions are not met, they remain V1 blockers rather than being hidden inside the V2 backlog.

---

## 2. Deep analysis of the existing architecture

### 2.1 META HARNESS already contains several partial “IRs”

A central V2 problem is that AgentX currently has multiple representations that each own part of execution semantics.

The OMT compiler treats `.meta/META_HARNESS.omt` as a single policy source and projects it into `harness.ir.json`, `AGENTS.md`, the navigation index, OpenCode configuration, and a budget report.[^7] This is a real compiler, but its output is primarily a **static policy/configuration IR**: gates, predicates, FSM declarations, budgets, deny rules, and tool metadata.

The Petri runtime has a different executable representation: net structure, live marking, sidecar task bindings, and a supervisor overlay.[^3] This is a **dynamic control-state representation**.

The ledger stores durable-ish execution events and progress facts. The status/resume tool reconstructs user-facing state from the ledger, project metadata, `WORK.md`, and other files.[^8] Task preparation separately combines preflight restrictions, risk heuristics, evidence expectations, and a next action.[^9]

These representations are individually useful, but V1 has accumulated semantic joins between them:

```text
OMT source
  -> harness.ir.json
  -> TypeScript gate driver
  -> specialized gate implementations
  -> Petri shell/runtime
  -> sidecar task bindings
  -> ledger
  -> status/resume projections
  -> evidence/completion logic
```

The biggest V2 opportunity is **not to merge every file into one giant JSON document**. It is to define one logical contract that says which layer is authoritative for each fact and how all layers share one revision/version identity.

### 2.2 Static Policy IR and dynamic Work IR should be separate

V2 should preserve a two-stage compilation model.

**Stage A — Policy compilation**

```text
.meta/META_HARNESS.omt
        |
        v
     Policy IR
```

Policy IR should define:

- supported action kinds,
- typed guards,
- profiles and capabilities,
- resource classes,
- evidence requirements,
- verification policy,
- authorization policy,
- task-type defaults,
- static repository restrictions.

**Stage B — Work compilation**

```text
request + repository snapshot + acceptance cases
+ Policy IR + runtime capability profile
                    |
                    v
                 Work IR
```

Work IR should define:

- the request anchor,
- acceptance cases,
- compact control topology,
- initial marking,
- task bindings,
- dependencies,
- typed guards specialized to the task,
- evidence obligations,
- effect contracts,
- compiler provenance,
- workflow-analysis certificate.

This separation prevents a common mistake: treating `harness.ir.json` as though it were already the eventual executable Work IR. It is not. It is closer to a compiled policy table.

### 2.3 The OpenCode adapter still owns too much semantics

The current OpenCode plugin is intentionally a thin composition root, but the actual gate semantics still live in TypeScript modules. The gate driver evaluates a closed predicate vocabulary, invokes specialized gate implementations, reads the ledger and Petri state, and handles fallbacks.[^10] The typed-policy slice is an improvement, but it explicitly types only part of the policy surface; today `g.net` is the principal typed case while other gates still defer to existing implementations.[^11]

This creates three long-term risks:

1. **Adapter lock-in.** A second runtime would have to reconstruct the same semantics.
2. **Semantic drift.** Preflight, enforcement, explanation, and runtime state can disagree when they are implemented through different paths.
3. **Qualification explosion.** Every adapter-specific branch becomes another behavior that must be independently proven.

V2 should move authoritative policy evaluation out of the OpenCode adapter. The adapter should normalize runtime events into a small protocol and invoke a shared decision/runtime layer.

The adapter's ideal responsibility is:

```text
host event
  -> normalize action
  -> ask Work IR runtime
  -> enforce ALLOW/DENY/UNKNOWN/ERROR
  -> perform supported effect
  -> return effect receipt
```

It should not be the place where workflow semantics are invented.

### 2.4 Petri nets are the strongest formal substrate, but not a complete task model

The generic Petri implementation is a conventional weighted Place/Transition net with deterministic ordering, atomic firing, pure `fire_marking`, and explicit edge-case semantics.[^4] Its analysis layer deliberately distinguishes proven, disproven, and unknown results and refuses to claim safety properties from truncated search.[^5]

Those properties are exactly what META HARNESS needs from a control kernel.

The runtime, however, already exceeds the information content of a marking. Its task bindings carry fields such as owner, generation, checkpoint, scope, resources, results, submission, liveness, accepted dependencies, and accepted evidence.[^3] That is not accidental complexity. It reflects information that ordinary uncolored tokens cannot represent conveniently.

The correct formalization is therefore:

```text
W_r = (Q, A, N, M_r, B_r, G, E_r, R_r, V_r)
```

where:

- `Q` = bounded authoritative request anchor,
- `A` = acceptance cases and user-visible completion contract,
- `N` = weighted P/T control net,
- `M_r` = live marking at revision `r`,
- `B_r` = typed named task bindings,
- `G` = typed guards and policy predicates,
- `E_r` = verification/evidence state,
- `R_r` = external-effect receipts,
- `V_r` = policy, Petri-semantics, compiler, profile, and state revision identities.

The Petri net is the **formal control core**. It is not required to encode strings, paths, hashes, Git identities, timestamps, or verifier artifacts as tokens.

### 2.5 The current binding model is effectively a deliberate color-erasure architecture

The runtime validates named bindings against aggregate task-state token counts and explicitly allows bindings to be a named subset of live tokens.[^3] That is a pragmatic architecture:

```text
rich named task state
        |
        | projection
        v
aggregate uncolored marking
```

For the verified managed profile, V2 should tighten this relation.

For selected managed task places:

```text
M[p] = | { b in B : b.place = p } |
```

unless the profile explicitly declares anonymous tokens for that place.

This gives AgentX many of the practical benefits associated with colored tokens while keeping the Petri kernel simple and analyzable.

V2 should **not** move to colored Petri nets unless real workload evidence shows that the projection architecture fails. Colored nets would add token-binding semantics, equality rules, state-space growth, cross-language conformance burden, and a larger format surface. None of those costs is justified by the current evidence.

### 2.6 Solo and managed execution currently have different control paths

The current compiled policy describes `g.net` as engaging under real concurrency while solo sessions skip to other gates.[^12] This was a sensible V1 economy optimization: do not pay Petri coordination overhead on every solo edit when concurrency is absent.

For V2, however, the **logical semantics should converge even if the implementation cost does not**.

A V2 work item should always have a control state, including solo work. In the solo profile:

- worker capacity is one,
- many concurrency guards become trivially true,
- Petri transitions may be evaluated in-process,
- no shell round trip should be required for a trivial enabledness result,
- unnecessary coordination mechanisms can compile away.

The distinction should become:

```text
same Work IR semantics
different profile capabilities and optimized execution paths
```

rather than:

```text
Petri semantics for concurrent work
other semantics for solo work
```

This makes resume, replay, action guidance, and evidence behavior consistent across profiles.

### 2.7 “Enabled transitions” are not the user-facing legal-action API

Raw Petri enabledness answers only a control question:

> Does the marking contain enough tokens for this transition?

Actual AgentX legality can also depend on:

- scope,
- task generation,
- owner,
- workspace,
- expected base content,
- request fidelity,
- policy grants,
- dependency freshness,
- verifier evidence,
- runtime capability.

Therefore the V2 runtime should expose a **Legal Action Frontier**, not a raw enabled-set call.

Formally:

```text
Legal(a, W_r) =
    PetriEnabled(N, M_r, transition(a))
    AND Guard(G, B_r, E_r, R_r, a) = ALLOW
    AND Capability(profile, a) = true
```

The decision vocabulary should remain explicit:

```text
ALLOW
DENY
UNKNOWN
ERROR
```

For a verified profile, only `ALLOW` authorizes a protected effect.

A frontier entry should have a shape similar to:

```json
{
  "action": "run_focused_tests",
  "transition": "verify_prepare",
  "petri_status": "enabled",
  "guard_status": "allow",
  "missing_obligations": [],
  "required_evidence": ["focused-test-receipt"],
  "recovery_action": null,
  "authority_revision": 184
}
```

For a blocked action:

```json
{
  "action": "edit src/foo.py",
  "transition": "work_edit",
  "petri_status": "enabled",
  "guard_status": "deny",
  "missing_obligations": [
    {
      "code": "workspace_mismatch",
      "required": "task T17 generation 3 workspace",
      "recovery_action": "switch to the claimed worktree"
    }
  ],
  "authority_revision": 184
}
```

This is the main Petri-facing product API V2 should standardize.

### 2.8 Task preparation is already a prototype of the compiler/frontier idea

The existing task-prep slice assembles identity, risk, knowledge pointers, restrictions, policy notes, evidence expectations, and a next action while deliberately remaining read-only and bounded.[^9] This is valuable because it demonstrates the desired user interaction: one bounded answer before action instead of a chain of trial-and-refusal turns.

But task preparation should not become a second ad hoc policy engine.

V2 should subsume the successful parts into compilation:

```text
task preparation
    ->
compile Work IR
    ->
return frontier + acceptance + evidence obligations
```

Risk heuristics can remain advisory inputs. Authoritative guards should be typed and testable.

### 2.9 The resume digest proves that derived state can be dramatically cheaper than re-reading the repository process surface

Feature 092 records a ≤2 KB resume digest and a dogfood case where a 432-byte digest replaced an approximately 58 KB re-read set.[^13] This is one of the clearest product signals in the current META HARNESS work.

V2 should generalize the principle:

> **Status, resume, completion, and guidance should be projections of authoritative Work IR state, not independent state reconstruction pipelines.**

The digest should therefore be derived from:

```text
request anchor
+ current marking
+ named bindings
+ unresolved obligations
+ evidence state
+ last effect/checkpoint
+ legal next actions
```

A projection can remain small while the underlying evidence is retained off-context.

### 2.10 Engine conformance and workflow correctness are different guarantees

AgentX already has a strong conformance story for Petri semantics. Petri Net Studio is independent at runtime, shares the JSON format, and uses Python-generated conformance vectors to check the TypeScript implementation.[^14] That proves implementations agree on semantics.

It does **not** prove that a particular generated workflow is useful or safe.

V2 should introduce a per-Work-IR **Workflow Certificate** containing:

- Petri semantics version,
- control-net digest,
- compiler version,
- policy version,
- reachability analysis completeness,
- known reachable deadlocks,
- required-goal reachability,
- capacity/resource invariants,
- selected liveness checks,
- projection invariants between bindings and task places,
- explicit unknown results where exploration was truncated.

Example:

```json
{
  "control_digest": "sha256:...",
  "petri_semantics": "agentx-ptn-v1",
  "analysis": {
    "complete": true,
    "reachable_states": 31,
    "deadlocks": [],
    "goal_reachable": true,
    "resource_invariants": {
      "worker_slots": "proven",
      "integration_slot": "proven"
    }
  }
}
```

A conformance vector says, “the engine computes the agreed semantics.”

A workflow certificate says, “this compiled control model satisfies the checked properties.”

They are complementary, not interchangeable.

### 2.11 Firing traces are control provenance, not acceptance evidence

A Petri firing trace proves that the control system recorded a sequence of state changes. It does not prove that the source code changed correctly or that the verified artifact is the one eventually integrated.

V2 should use the following hierarchy:

```text
control trace
    = workflow/control provenance

effect receipt
    = attestation that an external operation happened to a named candidate

verification receipt
    = attestation that a declared check ran against a named candidate

acceptance record
    = request acceptance case
      + exact candidate identity
      + applicable control provenance
      + valid verification receipts
      + dependency identity
      + waivers/deviations
```

This distinction is especially important because current verification/integration tests can exercise state movement with supplied verdicts, while the V1 roadmap itself notes that trusted verifier execution remains a qualification boundary.[^1][^15]

### 2.12 External effects are the hardest transactional boundary

No file-based Petri state update can be atomically committed with arbitrary Git, filesystem, shell, test, or remote effects.

The correct runtime model is a receipt protocol:

```text
eligible
   |
   v
reserved
   |
   v
effect_performed
   |
   v
effect_attested
   |
   v
logical_commit
```

The current workspace implementation illustrates why this matters. It can create workspace metadata and perform best-effort directory/branch setup, but it explicitly treats failures as non-blocking convenience behavior rather than proof of a linked checkout.[^16] That is acceptable as an intermediate V1 implementation, but it cannot be the basis of a V2 verified workspace claim.

V2 should define effect contracts explicitly. A workspace activation receipt, for example, should bind:

```text
task_id
generation
workspace_id
path
branch
base_commit
actual_head
repository_identity
profile
receipt_digest
```

The control transition to “active” should consume the receipt required by the profile.

### 2.13 Storage should move from multi-file mutable state to revision generations

The current runtime made meaningful progress on locking, in-lock revision checks, and command idempotency; tests prove same-revision races produce one commit and one stale revision, and same-command retries do not double-fire.[^17] Recovery tests also cover heartbeat transfer, stale generations, and several planted journal-marker states.[^18]

But a durable platform contract needs a stronger read model than several mutable files with coupled revision fields.

The recommended V2 storage shape is immutable state generations:

```text
.meta/.omt/work-ir/
    revisions/
        00000184/
            manifest.json
            control.json
            bindings.json
            evidence-index.json
            receipts-index.json
            command.json
            certificate.json
        00000185/
            ...
    CURRENT
```

Commit protocol:

```text
1. validate expected revision
2. write complete next generation
3. fsync according to the declared durability profile
4. atomically publish CURRENT
5. append/confirm replay index
6. acknowledge success
```

Reader protocol:

```text
1. resolve CURRENT once
2. read only that immutable generation
```

This solves a deeper V2 problem: reproducible replay and cross-adapter state transfer require **revision identity**, not merely “files that should agree.”

V2 does not have to use this exact directory layout, but it should adopt the invariant: **a reader observes one complete authoritative revision**.

### 2.14 Process mining should remain descriptive and proposal-only

The behavioral miner explicitly states that mined behavior is observed, never normative, and surfaces heuristic attribution and pruned data rather than hiding them.[^19] That is the correct safety boundary.

V2 should maintain three semantic classes:

| Net class | Purpose | Authority |
|---|---|---|
| Operational control net | Runtime workflow/resource control | May be authoritative after certification |
| Synthesized workflow proposal | Compiler/planner candidate | Proposal until compiled/certified |
| Mined behavioral net | Description of observed traces | Never normative by observation alone |

The adaptive loop should be:

```text
execution traces
    -> observed-process model
    -> compare with intended abstraction
    -> propose optimization
    -> replay/simulate
    -> benchmark
    -> certify
    -> shadow
    -> explicit promotion
```

Never:

```text
observed behavior -> automatic authority rewrite
```

### 2.15 Packaging is still coupled to the AgentX application

The Python package currently builds `src/agentx` and includes a broad application dependency set spanning LangChain, Chroma, Textual, OpenAI, and other runtime libraries.[^20] META HARNESS itself also depends on repository-local scripts, `.opencode` plugins, `.meta` state, and generated artifacts.

V2 should not immediately create a large public SDK. First define the contract, then extract the minimal package boundary.

A likely eventual split is conceptual rather than necessarily repository-level at first:

```text
agentx-work-ir
    schemas, canonicalization, semantic versions

agentx-work-runtime
    decisions, transactions, projections, replay

agentx-work-compiler
    request/repo/policy -> Work IR

agentx-adapter-opencode
    host normalization + enforcement

agentx-petri
    generic weighted P/T semantics and analysis
```

The names are placeholders. The architectural separation is the important part.

---

## 3. V2 architectural thesis

META HARNESS V2 should be defined by one sentence:

> **Compile user-requested repository work into a versioned, analyzable, evidence-bound Work IR whose formal control core is a weighted P/T Petri net and whose runtime can be executed consistently by multiple agent adapters.**

This yields six principles.

### Principle 1 — Work IR is a contract, not a storage file

The logical state may be sharded across files or a database, but every authoritative field has:

- one owner,
- one schema,
- one revision,
- one versioning rule,
- one replay meaning.

### Principle 2 — Petri marking owns aggregate control state

The marking is authoritative for the workflow/resource facts represented by the control net.

It is not automatically authoritative for:

- task identity,
- content identity,
- workspace reality,
- verifier truth,
- filesystem state,
- external authorization.

### Principle 3 — Typed bindings and guards preserve identity-rich semantics

Identity, generation, scope, capability, evidence, and dependency facts remain typed.

For protected execution:

```text
Legal = Petri enabledness ∧ typed guards ALLOW ∧ supported capability
```

### Principle 4 — External reality enters through receipts

Git, filesystem, tests, integration, and remote effects become authoritative only through receipts that are bound to the expected work revision/candidate.

### Principle 5 — Every user-facing surface is a projection

The following should be derived from Work IR:

- prepare,
- legal action frontier,
- status,
- resume,
- refusal/recovery explanation,
- completion report,
- audit/replay view.

They are not separate truth stores.

### Principle 6 — Optimization cannot silently rewrite authority

Mining, heuristics, and model-generated proposals can recommend changes. Promotion requires measurement and qualification.

---

## 4. Work IR v1 contract

### 4.1 Immutable specification versus mutable execution state

A Work IR instance should distinguish an immutable or versioned **specification** from mutable execution state.

```text
WorkSpec =
    RequestAnchor
    AcceptanceContract
    ControlNet
    GuardProgram
    EffectContracts
    RuntimeProfile
    SemanticVersions

WorkState_r =
    Marking_r
    Bindings_r
    Evidence_r
    Receipts_r
    Revision_r
```

The complete runtime object is:

```text
WorkIR_r = (WorkSpec, WorkState_r)
```

Changes to the specification create a new spec version and invalidate the analyses/evidence that depend on changed fields.

### 4.2 Request anchor

The request anchor contains:

- bounded verbatim request extract or durable conversation reference,
- deictic/referent snapshot where needed,
- task decomposition,
- scope,
- accepted clarification/amendment history.

The model's paraphrase must never replace the authoritative request.

### 4.3 Acceptance contract

Each acceptance case should include:

```text
id
request_ref
observable_outcome
verification_method
required_evidence_type
waiver_policy
status
```

The completion report should be assembled from these cases.

### 4.4 Control net

Use the existing Petri format as the nested structural control-net representation where possible.[^6]

Do not extend `petri-net-json-v1` with task bindings, evidence, or mutable state. Work IR should reference or embed a Petri document and separately carry live state.

### 4.5 Task bindings

Minimum binding contract:

```text
task_id
control_place
generation
owner
workspace
scope
dependencies
checkpoint
resources
submission
accepted_evidence_refs
```

For verified managed profiles, the binding-to-marking projection must be checked at every commit.

### 4.6 Guard program

Guards should use a closed, versioned vocabulary.

Examples:

```text
path_within_scope
generation_matches
owner_matches
workspace_matches
base_content_matches
dependency_current
evidence_present
evidence_candidate_matches
approval_present
policy_grant_alive
runtime_capability_present
```

Each guard returns:

```text
ALLOW | DENY | UNKNOWN | ERROR
```

A guard failure includes a stable reason code and recovery action.

### 4.7 Effect contracts

An effect contract declares:

- action kind,
- inputs,
- supported adapter capabilities,
- reversibility class,
- required preconditions,
- expected receipt fields,
- commit semantics.

Examples:

```text
edit_file
run_tests
create_worktree
commit_git
integrate_candidate
publish_remote
```

V2 should distinguish reversible local effects from externally irreversible effects without encoding that distinction as a tool-name heuristic.

### 4.8 Evidence manifest

An evidence item should bind at least:

```text
evidence_id
candidate_digest
repository/base/head identity
input manifest digest
policy version
verifier identity
toolchain identity
check identity
result
raw result reference
timestamp
```

Evidence reuse is valid only when the declared invalidation contract remains satisfied.

### 4.9 Version tuple

Every Work IR revision should carry a version tuple such as:

```text
work_ir_schema
petri_semantics
policy_ir_version
compiler_version
runtime_profile
adapter_contract
state_revision
```

This prevents old traces from being silently reinterpreted under new semantics.

---

## 5. Petri strategy for V2

### 5.1 Keep weighted P/T as the default formal kernel

The existing kernel should remain the baseline because it is:

- deterministic,
- easy to serialize,
- easy to port,
- easy to test,
- analyzable with exact invariants,
- explicit about incomplete analysis,
- already supported by independent Python and TypeScript implementations.[^4][^5][^14]

### 5.2 Prefer compact parametric control nets

The existing runtime's WIP-pool design and 15-place cap already point toward the scalable approach: use a small reusable control topology and keep task-specific identity in bindings.[^3]

Avoid generating:

```text
task_1_pending
task_1_active
task_1_verified
task_2_pending
task_2_active
...
```

for every task unless the tasks genuinely have different control structure.

Prefer:

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

with task identity in `B`.

### 5.3 Model long-running resources with start/finish transitions

A single atomic transition with a resource self-loop does not model a resource being held while an external agent performs work.

Preferred pattern:

```text
ready + resource_free
        |
        v
      start
        |
        v
active + resource_held

active + resource_held
        |
        v
      finish
        |
        v
done + resource_free
```

The compiler should use this pattern whenever a resource spans external work.

### 5.4 Verification is an evidence-guarded transition

Preferred pattern:

```text
active
  |
submit
  v
submitted
  |
verify[trusted evidence]
  v
verified
```

The transition to `verified` is not caused by the same action that produced the work.

### 5.5 Add per-net certification before adding richer net semantics

The next formal feature should be workflow certification, not colored tokens.

Certification should include:

- invariant checks,
- reachability completeness,
- goal reachability,
- deadlock result,
- relevant liveness,
- resource-bound checks,
- projection invariants.

Where the state space is too large, report unknown.

### 5.6 Advanced Petri features are demand-gated

Use a workload-triggered decision rule.

Investigate **coverability or state-space reduction** when unbounded or large control models become a demonstrated analysis problem.

Investigate **colored nets** only when identity-dependent synchronization cannot be expressed cleanly through binding projection and guards.

Investigate **timed nets** only when deadlines, leases, temporal SLAs, or scheduling proofs become central rather than ordinary typed runtime facts.

Investigate **hierarchical nets** only when independently reusable workflow components require formal composition at a scale the compact control-net model cannot manage.

Until then, those features are deferred.

---

## 6. V2 release profiles

V2 should separate **feature installation** from **guarantee profiles**.

### Assistance profile

Purpose:

- compile/read Work IR,
- return action frontier,
- resume/status,
- produce diagnostics,
- no strong effect-mediation guarantee.

Failure policy may degrade to advice when authority is unavailable.

### Verified Solo profile

Boundary:

- one trusted operator,
- one active writer,
- one supported adapter/runtime,
- supported effect types only,
- trusted verifier,
- content-bound evidence,
- atomic Work IR revision semantics.

Unknown/error on a critical authority check fails closed.

### Managed Local profile

Adds:

- multiple enrolled workers,
- task generations,
- real isolated workspaces,
- scope arbitration,
- resource capacity,
- serialized verification/integration where required,
- stale-worker fencing,
- recovery/handoff.

This profile must demonstrate a throughput or cost advantage over verified solo before being the default.

### Distributed Preview profile

Adds remote workers and network failure modes.

It should remain explicitly experimental until V2's local semantics are stable and economically justified.

---

## 7. V2 roadmap

The project should be created as a new home rather than extending `meta_harness_8` indefinitely:

```text
.projects/meta/meta_harness_v2/
```

Numeric feature IDs should continue to be assigned mechanically by `new_feature.py`; the roadmap should refer to stable slug names rather than predicting IDs.

### Milestone V2-M0 — Freeze the V1 semantic baseline

**Goal:** convert the successfully qualified V1 release into a stable semantic reference before V2 changes architecture.

This is a short freeze, not a reimplementation program.

Deliverables:

- a V1 qualification manifest;
- exact policy/compiler/Petri/adapter versions;
- retained benchmark corpus and raw result references;
- supported runtime/effect matrix;
- Petri conformance fingerprint;
- evidence schema snapshot;
- explicit list of unsupported actions;
- migration fixtures built from real V1 task states.

Acceptance:

- a V1 state can be replayed and inspected without current working-tree assumptions;
- all V1 release claims are linked to retained evidence;
- V2 tests can load frozen V1 fixtures for migration compatibility.

**Exit:** V2 has a stable source semantics to preserve or deliberately break.

---

### Milestone V2-M1 — Work IR v1

**Goal:** define the adapter-neutral executable contract.

#### Feature: `work_ir_contract`

Deliver:

- `shared/work-ir/FORMAT.md`,
- JSON Schema or equivalent typed schema,
- canonical serialization,
- `WorkSpec` / `WorkState` separation,
- nested/reference Petri control-net contract,
- typed bindings,
- guard result vocabulary,
- semantic version tuple.

Acceptance:

- canonical round trip;
- same logical state produces identical canonical bytes across reference implementations;
- unknown fields/version mismatch rejected rather than silently interpreted;
- migration fixtures from V1 load into a semantically equivalent V2 representation.

#### Feature: `work_ir_revision_store`

Deliver:

- immutable revision-generation store or equivalent atomic snapshot model;
- one-revision reader rule;
- expected-revision transaction API;
- command idempotency integrated with revision commit;
- recovery before new mutation.

Acceptance:

- fault injection after every authoritative write boundary;
- no reader sees a mixed generation;
- acknowledged command is replayable;
- retry never double-applies;
- incomplete commit is either deterministically finished or explicitly rejected.

#### Feature: `typed_guard_program`

Deliver:

- closed guard vocabulary;
- migrate critical gate semantics from adapter modules;
- one evaluator for prediction, enforcement, explanation, and replay.

Acceptance:

- same snapshot/action gets the same decision across all four surfaces;
- `UNKNOWN` and `ERROR` are distinct;
- verified profile fails closed on critical unknown/error;
- assistance profile can expose bounded diagnostics without claiming authority.

#### Feature: `effect_receipt_contract`

Deliver:

- normalized action/effect schema;
- reversible/irreversible classification;
- receipt types for edit, Git workspace, tests, integration, and publication boundaries.

Acceptance:

- logical state cannot reach an effect-complete state without the required receipt;
- receipt is bound to expected Work IR revision and candidate identity;
- seeded mismatched receipt is rejected.

#### Feature: `work_ir_projections`

Deliver derived APIs:

```text
prepare
frontier
status
resume
completion
audit
```

Acceptance:

- projections are read-only;
- no projection creates independent authority state;
- resume and completion are reproducible from retained Work IR/evidence state;
- bounded default output with expansion references.

**V2-M1 exit:** one qualified V1 task can be represented, resumed, decided, and completed entirely through Work IR semantics while the legacy surfaces remain compatibility projections.

---

### Milestone V2-M2 — Work Compiler v1

**Goal:** compile repository work rather than manually assembling runtime state.

The compiler input is:

```text
request anchor
repository snapshot/index
declared or confirmed acceptance cases
Policy IR
runtime capability profile
```

The compiler output is:

```text
WorkSpec
initial WorkState
Workflow Certificate
initial Legal Action Frontier
```

#### Feature: `request_acceptance_compiler`

Deliver:

- bounded request anchoring;
- acceptance-case derivation with request references;
- amendment/version semantics;
- task decomposition only where outcomes are independently acceptable.

Acceptance:

- every acceptance case traces to request text/reference;
- seeded omitted requested behavior is detectable;
- scope amendments invalidate affected compilation/evidence;
- compiler never silently replaces user request with model paraphrase.

#### Feature: `control_template_compiler`

Deliver:

- compact workflow templates;
- lifecycle/resource mappings;
- start/finish resource semantics;
- task binding generation;
- dependency edges as typed state/guards rather than per-task place explosion.

Acceptance:

- deterministic compile;
- place count remains bounded for increasing task count under pool mode;
- same control structure is reusable across tasks;
- generated nets pass structural validation.

#### Feature: `workflow_certificate`

Deliver:

- automatic Petri analysis at compile time;
- resource invariants;
- reachable deadlocks;
- goal reachability;
- completeness status;
- binding-projection checks;
- certificate bound to control digest/compiler version.

Acceptance:

- planted deadlock is rejected or explicitly surfaced;
- truncated analysis returns unknown rather than safe;
- changed control structure invalidates the certificate.

#### Feature: `legal_action_frontier`

Deliver the primary runtime decision API.

Acceptance:

- one query returns legal actions plus blocked actions that matter;
- every block has stable reason code, missing obligation, and recovery action;
- result is revision-stamped;
- raw Petri enabledness and typed guard status are separately inspectable;
- frontier can be consumed without knowledge of internal feature IDs.

#### Feature: `compiler_corpus`

Deliver:

- retained tasks across bug fix, cross-layer change, feature, investigation, resume, and managed conflict;
- expected Work IR characteristics;
- seeded invalid workflows;
- deterministic golden compilation.

Acceptance:

- compiler regressions are mechanically attributable;
- request fidelity and workflow certification are part of corpus grading;
- compilation cost is measured.

**V2-M2 exit:** for supported task classes, a user request can be compiled into a certified executable Work IR without manually authoring Petri topology.

---

### Milestone V2-M3 — Economic proof of compiled guidance

**Goal:** prove that Work IR and Petri-fronted guidance are economically useful, not merely elegant.

V1 should already provide the accepted-task baseline. V2-M3 evaluates the architectural change against that frozen baseline.

Comparisons:

```text
A — qualified V1 runtime
B — V2 runtime with same enforcement but Work IR projections
C — V2 runtime with compiled Legal Action Frontier
```

Primary measures:

```text
joint accepted-task cost
tokens per accepted task
tokens per attempt
attempts per accepted task
tokens to first valid action
repeat refusal rate
accepted throughput
human intervention minutes
completion review minutes
```

Petri-specific measures:

```text
frontier one-shot success
frontier query cost
blocked-action recovery success
workflow compile/certification cost
dead workflow detections before execution
```

Promotion rule:

- V2 mechanisms must not rely on lower correctness standards than V1;
- fixed compile cost must be included;
- improvements must hold by task class, not just in aggregate;
- mechanisms that consistently cost more than they save are demoted or removed from the default profile.

**V2-M3 exit:** Work IR/frontier architecture has a measured user-work advantage or a clearly justified correctness guarantee that offsets its cost.

---

### Milestone V2-M4 — Adapter SDK and cross-runtime conformance

**Goal:** prove that Work IR semantics are not OpenCode semantics.

#### Feature: `adapter_contract`

Define a small host interface:

```text
capabilities()
observe_repository()
propose_action()
perform_effect()
return_receipt()
emit_context_projection()
```

The adapter must not own normative workflow state.

#### Feature: `opencode_adapter_v2`

Re-implement the supported OpenCode path against the adapter contract.

Acceptance:

- behavior matches the qualified V2 reference;
- legacy adapter-specific policy branches are removed or compatibility-only;
- normalized actions include complete path sets and identity.

#### Feature: `reference_second_adapter`

Implement one materially different execution environment.

It does not need every feature. It must support a small verified-solo corpus.

Acceptance:

- same Work IR can be loaded;
- same normalized action gets equivalent decision semantics;
- same Petri transition sequence is interpreted under the same semantics version;
- evidence manifests have the same meaning.

#### Feature: `cross_adapter_conformance`

Golden vectors should cover:

- action normalization,
- guard decisions,
- Petri control progression,
- effect receipts,
- resume projection,
- completion assembly,
- error/unknown behavior.

**V2-M4 exit:** Work IR is demonstrably a runtime-independent protocol, not an internal representation renamed as a standard.

---

### Milestone V2-M5 — Managed multi-agent runtime 1.0

**Goal:** turn the existing concurrency mechanisms into an economically justified execution profile.

V1 already supplies many primitives: revision fencing, task generations, capacity checks, lanes, recovery, and dependency freshness.[^2][^17][^18] V2 should not rebuild them. It should bind them to the Work IR and qualified effect contracts.

Deliverables:

- explicit worker enrollment/capabilities;
- task/generation capability tokens or equivalent identity;
- real workspace effect receipts;
- scope/resource arbitration from Work IR;
- verification and integration receipts;
- deterministic recovery/handoff;
- dependency version recheck at integration;
- merged-candidate verification where required.

Benchmark against verified solo:

```text
accepted throughput
total tokens across workers + coordinator
human intervention
merge/integration failures
recovery cost
idle capacity
```

Release criterion:

> Managed multi-agent execution is promoted only when it provides a measured advantage for task classes with real parallelism.

Concurrency is not a product success when two agents consume twice the tokens to finish at the same accepted throughput.

**V2-M5 exit:** at least one supported task class demonstrates useful parallel execution with preserved verification guarantees and positive joint economics.

---

### Milestone V2-M6 — Adaptive optimization with a hard authority boundary

**Goal:** use execution history to make the compiler/runtime cheaper and more effective without allowing observations to rewrite policy directly.

#### Feature: `trace_replay_simulator`

Replay retained Work IR traces against candidate policy/compiler versions.

Acceptance:

- candidate change can be evaluated without authorizing real effects;
- semantic-version incompatibility is explicit;
- replay distinguishes control differences from adapter differences.

#### Feature: `optimizer_proposals`

Inputs:

- mined behavior,
- refusal frequency,
- action-frontier usage,
- context reuse,
- mechanism cost,
- failed attempts.

Outputs:

- ranked proposal,
- expected effect,
- affected profiles/task classes,
- evidence supporting proposal,
- rollback plan.

#### Feature: `shadow_policy_evaluation`

Run current and candidate policies on the same normalized action stream.

Acceptance:

- newly allowed and newly denied cases are separately reported;
- no shadow result authorizes effects;
- critical differential requires explicit review.

#### Promotion pipeline

```text
telemetry
 -> proposal
 -> replay/simulation
 -> workflow/property checks
 -> controlled benchmark
 -> shadow run
 -> explicit promotion
```

The improvement loop must itself report maintenance and evaluation cost.

**V2-M6 exit:** at least one optimization moves through the complete pipeline and demonstrates a retained accepted-task benefit without an authority regression.

---

### Milestone V2-M7 — Distributed verified execution, optional

**Goal:** extend the same semantics across machines only after local multi-agent execution is proven.

This milestone is optional and should not begin merely because the architecture could support it.

Required new concerns:

- remote worker identity and capability attestation,
- network partitions,
- lease/leadership semantics,
- artifact transport integrity,
- remote effect receipts,
- evidence transport and storage,
- clock assumptions,
- retry semantics across network failures,
- secret boundary,
- coordinator failover.

The Petri model does not solve distributed consensus. Do not encode network-consensus problems as Petri places and call them solved.

A reasonable first distributed profile is:

```text
single authoritative coordinator
+
remote disposable workers
+
content-addressed artifacts
+
signed or authenticated receipts
```

before attempting multi-leader coordination.

**V2-M7 exit:** remote execution preserves the same Work IR decision/evidence semantics under a documented failure model and shows a workload advantage over local execution.

---

## 8. Immediate V2 implementation queue

Assuming the V1 handoff gate is green, the initial queue should be deliberately short.

| Order | Slug | Purpose | Dependency | Concrete acceptance |
|---|---|---|---|---|
| 1 | `v1_semantic_freeze` | Freeze qualification, schemas, semantics fingerprints, migration fixtures | V1 release | One immutable V1 reference bundle and replay corpus |
| 2 | `work_ir_contract` | Define `WorkSpec` / `WorkState`, versions, bindings, guards | 1 | Canonical format + migration golden |
| 3 | `work_ir_revision_store` | Atomic authoritative revision semantics | 2 | Crash campaign across every write boundary |
| 4 | `typed_guard_program` | One decision engine independent of adapter | 2–3 | Preflight=enforcement=explain=replay |
| 5 | `effect_receipt_contract` | Bind external effects to state/candidate | 2–4 | Seeded wrong/stale receipt refused |
| 6 | `work_ir_projections` | Frontier/resume/completion from one state | 2–5 | No projection-owned authority |
| 7 | `workflow_certificate` | Compile-time Petri properties | 2 | Deadlock/unknown/invariant goldens |
| 8 | `request_acceptance_compiler` | Request → acceptance contract | 2 | Full request traceability |
| 9 | `control_template_compiler` | Acceptance/tasks → compact control IR | 7–8 | Deterministic bounded topology |
| 10 | `legal_action_frontier` | Decision-complete next-action API | 4, 6, 9 | One-query blocked/allowed/recovery contract |
| 11 | `compiled_guidance_benchmark` | Prove economics | 10 | V1/B/C comparison with fixed oracle |
| 12 | `adapter_contract` | Runtime-independent execution interface | M1/M2 semantics stable | Reference contract + conformance vectors |
| 13 | `opencode_adapter_v2` | Move OpenCode onto shared runtime | 12 | Qualified corpus parity |
| 14 | `reference_second_adapter` | Prove portability | 12 | Same Work IR semantics on second host |
| 15 | `managed_profile_v2` | Bind concurrency primitives to Work IR | 3–14 | Parallel benchmark + stale-worker/evidence tests |
| 16 | `adaptive_optimizer_pipeline` | Proposal/replay/shadow/benchmark | Stable traces | One safe measured promotion |

The queue intentionally avoids advanced Petri features.

---

## 9. V2 invariants

### V2-I01 — One logical authority revision

Every authoritative decision is tied to exactly one Work IR revision.

### V2-I02 — Control ownership is explicit

The Petri marking is authoritative only for control/resource facts represented by the net.

### V2-I03 — Binding projection is checked

Managed task bindings and task-state marking agree according to the active profile's projection rule.

### V2-I04 — No self-asserted verification

The actor that produced work cannot establish trusted verification merely by supplying `pass`.

### V2-I05 — Control provenance is not acceptance

A valid firing trace alone never establishes completion.

### V2-I06 — External effects require attestation

Logical state cannot claim an effect occurred without a valid receipt required by the profile.

### V2-I07 — Stale identity cannot publish

Stale revision, stale generation, wrong owner, or wrong workspace cannot publish managed output.

### V2-I08 — Prediction equals enforcement semantics

Read-only prediction and live enforcement use the same evaluator over equivalent snapshots.

### V2-I09 — Incomplete formal analysis stays unknown

Truncation never becomes a positive safety/liveness claim.

### V2-I10 — Mined behavior is descriptive

Observed traces may propose policy/compiler changes but never authorize them.

### V2-I11 — Adapters are not policy authorities

An adapter may normalize and enforce decisions; it may not redefine normative Work IR semantics.

### V2-I12 — Request fidelity survives resume and handoff

The authoritative request and accepted amendments remain traceable through compaction, resume, worker transfer, and completion.

### V2-I13 — Semantic versions are durable evidence fields

A retained trace always identifies the Work IR, Petri, policy, compiler, and adapter-contract semantics under which it was produced.

### V2-I14 — Mechanisms pay rent

Optional runtime mechanisms are measured against accepted-task value and are removable when their marginal value is negative.

---

## 10. Qualification matrix

### Work IR correctness

Required:

- canonical serialization;
- migration from frozen V1 fixtures;
- revision atomicity;
- command replay;
- schema/version refusal;
- request/acceptance traceability;
- binding projection.

### Petri correctness

Required:

- engine conformance;
- workflow certificate;
- resource invariants;
- deadlock result;
- goal reachability where applicable;
- explicit unknown on incomplete exploration.

### Effect authority

Required:

- normalized path/action coverage;
- workspace receipt;
- file-edit receipt/identity where applicable;
- test/verifier receipt;
- integration candidate identity;
- publication approval for irreversible external effects.

### Recovery

Required:

- crash after each transaction boundary;
- crash before/after effect;
- duplicate command;
- stale revision;
- stale generation;
- coordinator restart;
- interrupted verification;
- interrupted integration;
- dependency changes between verify and integrate.

### Adapter portability

Required:

- same decision vectors;
- same guard semantics;
- same Petri semantics;
- same evidence interpretation;
- equivalent completion outcomes for supported corpus.

### Economy

Required:

- full accepted-task cost;
- fixed compile/frontier cost;
- attempts per accepted task;
- repeat refusal rate;
- tokens to first valid action;
- human intervention;
- completion review time;
- concurrency throughput where applicable.

---

## 11. What V2 should explicitly not do

V2 should reject the following attractive but premature directions.

### Do not turn every rule into a Petri place

Path checks, content hashes, timestamps, user approvals, and workspace identities are better typed guards/evidence.

### Do not introduce colored nets because task bindings look like colors

The existing projection architecture is simpler and already works with independent engine conformance.

### Do not make timed nets the heartbeat implementation

Heartbeat and lease data can remain ordinary typed state until formal temporal reasoning is a demonstrated requirement.

### Do not freeze the current OpenCode hook API as the Work IR API

OpenCode is the first adapter, not the protocol definition.

### Do not make the ledger the only source of truth

Events are valuable for audit/mining. Authoritative current state should be a revisioned snapshot with replayable provenance.

### Do not make process mining self-governing

Observed behavior is not evidence of desired behavior.

### Do not equate more workers with higher throughput

Multi-agent work ships only when accepted throughput and joint task cost improve.

### Do not create a cloud/distributed service before local semantics are stable

Network distribution multiplies ambiguity in identity, retries, effects, and recovery.

### Do not standardize accidental file names as public semantics

`net_state.sidecar.json`, the overlay, ledger layout, and plugin files are current implementation details. V2 standardizes their meanings, not their paths.

---

## 12. Decision gates for advanced Petri work

At the end of each V2 milestone, collect workload evidence.

### Trigger A — state-space explosion

If certified workflows frequently hit incomplete reachability because the compact net state space is too large:

1. profile sources of explosion;
2. investigate partial-order reduction/symmetry;
3. investigate coverability where unboundedness is relevant;
4. only then expand the formal engine.

### Trigger B — identity-dependent transition logic becomes dominant

If typed guard/binding logic repeatedly reconstructs complex token matching and makes certification opaque:

1. document at least three real workload cases;
2. compare colored-net formulation against current projection architecture;
3. measure analysis/conformance cost;
4. only then decide on colored nets.

### Trigger C — temporal properties become release-critical

If leases/deadlines/timeouts need formal proofs rather than runtime checks:

1. define the temporal properties;
2. test whether ordinary state + clocks suffice;
3. evaluate timed-net semantics only if they materially improve proof or execution quality.

### Trigger D — workflow composition becomes unwieldy

If independently authored workflows need reusable formal interfaces:

1. define composition ports/contracts;
2. validate flattened-net behavior;
3. evaluate hierarchical nets only when composition complexity is measurable.

The default outcome of each gate may legitimately be “remain on weighted P/T.”

---

## 13. Product and research questions V2 must answer

V2 should be falsifiable.

### Product question

> Does a compiled Work IR help agents complete accepted repository work more cheaply and reliably than the qualified V1 harness?

### Petri question

> Does the Petri control core reduce failed action discovery, improve recovery/concurrency, or detect invalid workflows early enough to justify its fixed and marginal cost?

### Compiler question

> Can user requests and acceptance contracts be compiled into sufficiently compact, correct workflow models without creating a brittle planning language?

### Portability question

> Does the same Work IR preserve meaning across multiple agent runtimes, or are important semantics still host-specific?

### Multi-agent question

> For which task classes does managed parallelism increase accepted throughput after coordinator, verification, and integration cost?

### Adaptive question

> Can historical traces reliably identify mechanisms to simplify or improve without creating policy drift?

A negative answer should change scope. V2 is not successful merely because every planned component is implemented.

---

## 14. Recommended project structure

A clean project home can organize V2 into six tracks.

### T1 — Semantic core

- V1 semantic freeze
- Work IR format
- revision store
- semantic versions
- migration

### T2 — Authority and evidence

- typed guards
- effect contracts
- evidence manifests
- projections
- trusted verifier interface

### T3 — Compiler and Petri certification

- request/acceptance compiler
- compact control templates
- workflow certificate
- legal action frontier
- compiler corpus

### T4 — Runtime portability

- adapter contract
- OpenCode adapter v2
- second adapter
- cross-adapter conformance

### T5 — Managed execution

- managed local profile
- capability enrollment
- workspace/effect attestation
- integration verifier
- parallel benchmark

### T6 — Adaptive and distributed

- replay simulator
- optimizer proposals
- shadow evaluation
- optional distributed preview
- advanced-Petri decision gates

This preserves the existing project discipline while shifting the center of gravity from feature accumulation to stable semantics.

---

## 15. Definition of done for META HARNESS V2

V2 is complete when all of the following are true.

1. **A versioned Work IR exists.** It has canonical semantics independent of repository-local file layout.
2. **The weighted P/T net is formally scoped.** It owns workflow/resource control state and is not falsely presented as all task state.
3. **All protected actions use a common decision model.** Petri enabledness and typed guards are jointly evaluated.
4. **Current state is revision-atomic.** Readers cannot observe mixed authoritative generations.
5. **External effects are attested.** Workspace, verification, integration, and publication state cannot be invented by local metadata.
6. **Completion is evidence assembled.** The final report is grounded in acceptance cases and candidate-bound evidence.
7. **Workflow certification exists.** Generated control models carry explicit reachable/deadlock/invariant results with honest unknown states.
8. **The primary agent-facing API is the legal action frontier.** It tells the agent what is legal, what is blocked, why, and how to recover.
9. **Resume is a projection.** It is derived from Work IR and does not require reconstructing truth from unrelated documents.
10. **At least two adapters demonstrate the same semantics.** OpenCode is no longer the definition of META HARNESS behavior.
11. **Managed parallelism is economically justified for at least one real task class.**
12. **The adaptive loop is proposal-only until qualified.** At least one optimization has passed replay, benchmark, shadow, and explicit promotion.
13. **Advanced Petri semantics remain evidence-driven.** No colored/timed/hierarchical extension is added without a documented workload trigger.
14. **V2 beats or meaningfully extends V1.** Accepted-task economics are non-regressive and the new guarantees are independently demonstrated.

---

## 16. Final recommendation

The deepest shift after V1 should be from:

```text
repository-specific harness
+ many useful mechanisms
+ Petri coordination
```

to:

```text
compiler
+ executable Work IR
+ verified runtime protocol
+ adapter ecosystem
```

Petri nets remain central, but their role becomes more disciplined and therefore more powerful.

They provide:

- formal control state,
- legal workflow progression,
- capacity and synchronization,
- pre-execution reachability/deadlock reasoning,
- replayable control provenance.

Typed Work IR state provides:

- task identity,
- ownership,
- generations,
- scopes,
- workspaces,
- dependencies,
- content identity,
- evidence,
- external-effect attestations.

The compiler connects user intent to both.

The runtime executes the result consistently.

The evidence layer proves what actually happened.

The optimizer learns from traces without gaining unilateral authority.

That architecture gives META HARNESS a credible path from an advanced repository-local development harness to a **portable verified-agent execution protocol**.

The most important V2 rule is consequently simple:

> **Do not add more mechanism until the existing semantics have a stable contract. Once the contract exists, make every new mechanism prove that it improves accepted work, strengthens a named guarantee, or both.**

---

## Sources

[^1]: AgentX repository, “[META HARNESS roadmap: product refinement, verified work and token efficiency](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/sandbox/META_HARNESS_ROADMAP.md),” reviewed 2026-09-13. Used for current product claims, V1 milestones, open findings, qualification boundary, and concurrency-gap analysis.
[^2]: AgentX repository, “[meta_harness_8 CURRENT_STATE.md](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/.projects/meta/meta_harness_8/CURRENT_STATE.md)” and “[PROJECT.md](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/.projects/meta/meta_harness_8/PROJECT.md),” commit `33c9eaa…`. Used for shipped slices, remaining backlog, track structure, and recorded suite state.
[^3]: AgentX repository, “[scripts/omt/net/state.py](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/scripts/omt/net/state.py),” commit `33c9eaa…`. Used for the three-file runtime bundle, WIP pool, capacities, task bindings, projection behavior, and runtime architecture.
[^4]: AgentX repository, “[src/agentx/model/petri_net/model.py](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/src/agentx/model/petri_net/model.py),” commit `33c9eaa…`. Used for weighted P/T semantics, deterministic markings, and firing behavior.
[^5]: AgentX repository, “[src/agentx/model/petri_net/analysis.py](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/src/agentx/model/petri_net/analysis.py),” commit `33c9eaa…`. Used for reachability, deadlock/boundedness/liveness analysis, and explicit incomplete/unknown semantics.
[^6]: AgentX repository, “[shared/petri-net/FORMAT.md](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/shared/petri-net/FORMAT.md),” format v1. Used for the structural/M0-only interchange boundary and versioning strategy.
[^7]: AgentX repository, “[scripts/omt/harnessc.py](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/scripts/omt/harnessc.py)” and “[.meta/.omt/harness.ir.json](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/.meta/.omt/harness.ir.json),” commit `33c9eaa…`. Used for OMT policy compilation and current compiled gate/policy representation.
[^8]: AgentX repository, “[.opencode/plugins/omt_status.ts](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/.opencode/plugins/omt_status.ts),” commit `33c9eaa…`. Used for current status/preflight/resume aggregation responsibilities.
[^9]: AgentX repository, “[.opencode/lib/enforcer/task_prep.ts](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/.opencode/lib/enforcer/task_prep.ts),” commit `33c9eaa…`. Used for the bounded task-preparation prototype and its relationship to preflight/policy.
[^10]: AgentX repository, “[.opencode/plugins/omt_enforcer.ts](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/.opencode/plugins/omt_enforcer.ts)” and “[gate_driver.ts](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/.opencode/lib/enforcer/gate_driver.ts),” commit `33c9eaa…`. Used for adapter-specific hook and gate-evaluation architecture.
[^11]: AgentX repository, “[.opencode/lib/enforcer/policy_decision.ts](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/.opencode/lib/enforcer/policy_decision.ts),” commit `33c9eaa…`. Used for typed policy semantics, durable-progress/temp-grant separation, and the incremental `g.net` typed slice.
[^12]: AgentX repository, “[.meta/.omt/harness.ir.json](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/.meta/.omt/harness.ir.json),” `g.net` compiled record at commit `33c9eaa…`. Used for current concurrent-only net-gate activation.
[^13]: AgentX repository, “[feature_092 resume-digest test report](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/.meta/software_development_process/6.testing/features/feature_092.resume_digest/test_report.md),” 2026-09-13. Used for the ≤2 KB contract, 432-byte dogfood digest, and recorded 2214-test run.
[^14]: AgentX repository, “[petri_net_studio PROJECT.md](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/.projects/meta/petri_net_studio/PROJECT.md),” commit `33c9eaa…`. Used for independent TypeScript/Python semantics, shared format, and conformance-vector design.
[^15]: AgentX repository, “[tests/scripts/omt/test_net_evidence_dependency.py](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/tests/scripts/omt/test_net_evidence_dependency.py),” commit `33c9eaa…`. Used for current dependency/evidence fencing behavior and supplied verification/integration verdict test shape.
[^16]: AgentX repository, “[scripts/omt/net/workspace.py](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/scripts/omt/net/workspace.py),” commit `33c9eaa…`. Used for current workspace metadata/bootstrap semantics and fail-open best-effort Git behavior.
[^17]: AgentX repository, “[tests/scripts/omt/test_net_transaction_authority.py](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/tests/scripts/omt/test_net_transaction_authority.py),” commit `33c9eaa…`. Used for same-revision race, stale-revision, and command-idempotency evidence.
[^18]: AgentX repository, “[tests/scripts/omt/test_net_recovery_journal.py](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/tests/scripts/omt/test_net_recovery_journal.py),” commit `33c9eaa…`. Used for heartbeat, recovery handoff, stale generation, and journal-marker reconciliation evidence.
[^19]: AgentX repository, “[scripts/omt/net/miner.py](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/scripts/omt/net/miner.py),” commit `33c9eaa…`. Used for the “observed, never normative” process-mining boundary.
[^20]: AgentX repository, “[pyproject.toml](https://github.com/oikumo/agentx/blob/33c9eaa2a811533902ccb953aad04b43aa397e2b/pyproject.toml),” commit `33c9eaa…`. Used for current AgentX package boundary and application dependency footprint.
