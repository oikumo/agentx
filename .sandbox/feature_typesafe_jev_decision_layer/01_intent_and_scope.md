# Intent and scope

## Problem statement

AgentX increasingly has decisions that are semantic but not generative: pick a bounded model route, estimate whether an action needs review, or assess whether retrieved evidence is relevant. General chat models can make these judgments, but they add latency, cost, free-form parsing, and another opportunity for unbounded output. Hard-coded rules are cheaper and safer when the condition is explicit, but become brittle when the condition depends on natural-language intent.

The proposed layer fills that narrow gap. It asks a typed classifier an atomic question, receives a closed-set answer with probabilities, and lets ordinary AgentX code decide what that evidence means.

## Intended outcomes

The feature intends to:

1. make repeated semantic decisions explicit, typed, observable, and testable;
2. reduce unnecessary general-model calls for bounded classifications;
3. expose uncertainty instead of hiding it behind a free-form answer;
4. preserve deterministic policy and user authorization as the authority boundary;
5. let AgentX compare providers or remove Jev without rewriting product policy;
6. introduce behavior only after repository-owned, per-decision evaluation.

## Users and operators

| Actor | Need | Feature response |
|---|---|---|
| AgentX user | Predictable behavior and no surprise external disclosure | Off by default, explicit enablement, shadow first, documented external processing |
| Coding/RAG user | Fast model selection without losing manual choice | `current` route remains the fallback; route options are configured and bounded |
| Security-conscious user | Mutations must not gain authority from a model | Deterministic deny wins; classifier evidence can only maintain or reduce authority |
| Maintainer | Provider changes must not infect application code | AgentX-owned contracts and provider adapter |
| Evaluator | Reproducible quality and calibration evidence | Versioned datasets, schema versions, pinned model, holdout reports |
| Operator | Quick containment during incidents | Global kill switch, per-kind switches, timeouts, circuit breaker, no client in `off` |

## Decision classes

### Model route

Question: which semantic route best matches the current user request?

Initial outcomes:

| Outcome | Meaning | Constraint |
|---|---|---|
| `current` | Preserve the user's selected provider | Always available |
| `fast` | Direct lookup, extraction, or localized work | Maps to one configured `ModelRegistry` provider ID |
| `powerful` | Architecture, ambiguity, or difficult reasoning | Maps to one configured provider ID |
| `local` | Work intended to remain on-device | May map only to a provider whose registry `kind` is `local` |

The route is not a provider name. Configuration resolves the route to an existing registry entry, and validation rejects missing or invalid mappings before enforcement can start.

### Tool risk

Question: how likely is this proposed mutation to be risky or insufficiently authorized given a minimal, structured context?

Initial outcomes should be a probability plus a deterministic action band:

- below `review_threshold`: classifier does not add a restriction;
- at or above `review_threshold`: require human review;
- at or above `block_threshold`: deny according to the configured action class;
- any deterministic deny: deny regardless of classifier result;
- classifier unavailable: follow the configured fail policy, never silently convert an intended review into execution.

The first host-filesystem candidates are `file_edit` and `file_create`, but only after AgentX has a common authorization result and resumable approval flow. The implementation must inventory every mutation-capable tool that the compiled graph exposes. Deep Agents also adds backend filesystem tools such as `edit_file` and `write_file`, and may expose `execute` for sandbox-capable backends. Those are different action classes, but they cannot be left as an undocumented bypass: each must be guarded, proven unable to mutate the protected host resource, or disabled for the enforcing cohort.

### RAG relevance and citation support

These are two different questions and must not share a threshold:

- relevance: whether an already-retrieved chunk helps answer one query;
- citation support: whether one cited chunk supports one concrete answer claim.

Prompt-injection likelihood is a third decision, not an extra label on relevance. Each needs its own dataset, question primitive, threshold, and error policy.

## Non-goals

The first feature is not intended to:

- replace chat or reasoning models;
- let Jev generate plans, text, code, commands, or policy rules;
- make Jev the source of truth for permissions;
- infer arbitrary provider or model identifiers;
- auto-tune thresholds in production;
- send whole repositories, complete conversations, or session snapshots for classification;
- classify every read-only tool call;
- add tool-risk enforcement before user approval can suspend and resume a run;
- upgrade the whole LangChain family merely to reuse experimental middleware;
- promise correctness from a typed response shape;
- combine model routing, tool authorization, and RAG into one release gate.

## Core invariants

### Authority invariant

For any action, effective authority after the decision layer must be less than or equal to authority granted by deterministic AgentX checks and explicit user approval.

Informally:

`effective_authority = min(deterministic_authority, approval_authority, probabilistic_restriction)`

The classifier can add a restriction; it cannot remove one.

### Closed-world invariant

Every provider answer is parsed into an AgentX enum. Unknown labels, missing answers, invalid distributions, non-finite probabilities, or model-version mismatches are provider errors, not new outcomes.

### Off-mode invariant

When mode is `off`:

- no provider client is constructed;
- no API key is read or required;
- no decision network request occurs;
- no decision middleware affects ordering;
- current behavior and performance remain unchanged apart from negligible configuration branching.

### Shadow invariant

When mode is `shadow`, the counterfactual disposition may be recorded, but the actual route, approval, policy, model invocation, and tool execution result remain semantically equivalent at their public boundaries. Shadow classification can still add time-to-first-token, external traffic, and failure telemetry; those observable costs must be measured rather than hidden behind a “no behavior change” claim. Provider or telemetry failure may not change the baseline result.

### Version invariant

The following identifiers travel together in every evaluation event:

- AgentX decision schema version;
- question/instruction version;
- redaction schema version;
- threshold policy version;
- provider adapter version;
- exact returned Jev model ID.

Changing any of them starts a new evaluation cohort.

## Success definition

The layer succeeds only if it offers measurable benefit over the current baseline without weakening control:

- model routing reduces cost or latency while keeping task success within an approved bound;
- risk classification catches meaningful review cases with a false-allow rate below the separately approved ceiling;
- decision latency remains inside the budget for the affected flow;
- privacy inspection finds no prohibited content in telemetry or traces;
- provider outages degrade predictably;
- users can disable the layer immediately;
- maintainers can replace the provider behind the same contracts.

If these conditions are not demonstrated, remaining in `off` or deleting the experiment is a valid outcome.
