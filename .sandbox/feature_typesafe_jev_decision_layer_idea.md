# Feature decision memo: TypeSafe Jev decision layer

- **Status:** refined proposal; implementation not approved
- **Date:** 2026-09-20
- **Feature slug:** `feature_typesafe_jev_decision_layer`
- **Likely task type:** `major_feature`
- **Detailed package:** [`feature_typesafe_jev_decision_layer/README.md`](feature_typesafe_jev_decision_layer/README.md)

## Decision in one paragraph

AgentX should explore Jev as an optional, probabilistic decision provider behind an AgentX-owned decision kernel. It must not become a permissions authority, replace deterministic policy, or leak raw agent state into logs and traces. The first production-shaped slice is an `off`/`shadow` service using the stable TypeSafe SDK and a pinned Jev model. Model-route shadowing is the first evaluation target. Tool-risk classification follows only after AgentX has a real authorization contract and interrupt/resume approval path. RAG decisions remain a separate experiment.

## What changed from the original idea

The deeper review found four boundaries that the initial draft treated too loosely:

1. `PolicyEngine` is used by the domain-agent cycle, but LangChain coding tools currently execute directly. Tool-risk integration therefore needs a shared authorization adapter; it cannot merely “add a signal” to the existing engine.
2. `ModelRegistry` stores one current provider and constructs an LLM before an agent run. Per-request routing needs an AgentX middleware or another explicit run-time model-resolution seam.
3. `langchain-typesafe==0.0.1a2` conflicts with AgentX's exact LangChain pins. The preferred spike is `typesafe-sdk==0.7.0` behind an AgentX-owned adapter, not an early LangChain-family upgrade.
4. A provider answer and AgentX's action are different facts. The design now separates typed classifier evidence from the deterministic disposition that observes, applies, reviews, blocks, skips, or falls back.

## Proposed product boundary

Jev may answer narrow semantic questions:

- Which configured route best matches this request?
- How likely is this proposed mutation to be risky or insufficiently authorized?
- Is this already-retrieved passage relevant?
- Does this passage support this specific claim?

AgentX remains responsible for:

- the closed set of allowed outcomes;
- deterministic path, capability, sandbox, and user-authorization checks;
- threshold policy and human approval;
- provider timeouts, retries, circuit breaking, and fallback;
- redaction, retention, audit telemetry, and kill switches;
- deciding whether an answer is acted on at all.

## Recommended sequence

| Stage | Deliverable | Behavior change |
|---|---|---|
| 0 | Dependency/API spike against `typesafe-sdk==0.7.0`; fake transport; compatibility record | None |
| 1 | Decision kernel, TypeSafe adapter, config, redaction, telemetry, `off` and `shadow` | None |
| 2 | Labeled model-route evaluation and calibration report | None |
| 3 | Optional low-stakes route enforcement with bounded registry mappings | Route only; immediate kill switch |
| 4 | Shared tool authorization and UI interrupt/resume approval | Structural prerequisite |
| 5 | Tool-risk shadowing, then separately approved enforcement | Never overrides a deterministic deny |
| 6 | Independent RAG relevance/citation experiments | Separately evaluated |

The refined design adds a protocol layer beneath these stages: immutable question specifications, kind-specific disclosure tiers, a per-run decision budget, stable decision receipts, closed reason codes, and cohort-aware evaluation. These are provider-neutral controls, not Jev-specific product behavior.

The implementation seam is now explicit: one accepted user turn receives a fresh `run_id`; route preflight runs once; a typed, non-checkpointed context carries the disposition into the compiled graph; and a thin LangChain middleware uses `ModelRequest.override(model=...)` without mutating `ModelRegistry`. The provider port is batch-shaped to match TypeSafe's shared-state/multiple-question API while public AgentX methods remain kind-specific. Tool-risk work additionally requires an inventory of the constructed graph's effective tools so framework-added or delegated mutation paths cannot bypass authorization.

## New ideas worth carrying forward

The deeper pass recommends seven additions to the first implementation boundary:

1. a decision-budget governor so classifier latency and cost cannot amplify with agent loops;
2. immutable decision receipts that bind evidence, telemetry, replay, and future approval without storing raw input;
3. privacy disclosure tiers enforced by state builders;
4. a structural question-spec linter that catches enum/schema/fixture drift;
5. paired-cohort replay for model, prompt, schema, or threshold upgrades;
6. a typed per-invocation route context that separates one user turn from the multi-turn thread;
7. an effective tool/action inventory that closes framework-added and delegated mutation paths.

Two promising ideas remain experiments: an independent route-promotion Noul beside the route Choice to improve abstention, and deterministic fast-path bypasses for explicit local-only or fixed-provider cases. Neither should replace the simpler route-v1 baseline before comparative evidence exists.

## Non-negotiable invariants

- `off` constructs no TypeSafe client and requires no `TYPESAFE_API_KEY`.
- First enablement always starts in `shadow`.
- A Jev answer is untrusted evidence, never authority.
- Provider output can only select an AgentX-owned enum or configured registry entry.
- A deterministic deny always wins.
- Provider failure never broadens authority.
- Tool-risk enforcement is unavailable until approval can pause and resume safely.
- Raw prompts, source text, tool arguments, secrets, and retrieved chunks are excluded from decision telemetry.
- Model aliases are not used for enforced decisions; `jev-1.13.0` is pinned and re-evaluated before change.
- Every decision kind has its own state schema, thresholds, evaluation report, and rollout gate.

## Recommendation

Approve only the dependency/API spike and shadow model-routing slice as the first implementation package. Do not approve tool-risk enforcement, RAG enforcement, direct adoption of experimental TypeSafe middleware, or a broad LangChain dependency upgrade as part of that slice.

## Detailed documents

- [`README.md`](feature_typesafe_jev_decision_layer/README.md) — package map and status
- [`01_intent_and_scope.md`](feature_typesafe_jev_decision_layer/01_intent_and_scope.md) — purpose, users, use cases, non-goals, invariants
- [`02_architecture_and_contracts.md`](feature_typesafe_jev_decision_layer/02_architecture_and_contracts.md) — components, typed contracts, flows, authority model
- [`03_implementation_plan.md`](feature_typesafe_jev_decision_layer/03_implementation_plan.md) — exact code layout, integration seams, phases, pseudocode
- [`04_security_privacy_operations.md`](feature_typesafe_jev_decision_layer/04_security_privacy_operations.md) — threat model, minimization, failures, telemetry, operations
- [`05_evaluation_and_rollout.md`](feature_typesafe_jev_decision_layer/05_evaluation_and_rollout.md) — datasets, metrics, thresholds, experiment and rollout gates
- [`06_testing_and_acceptance.md`](feature_typesafe_jev_decision_layer/06_testing_and_acceptance.md) — test plan and acceptance matrix
- [`07_dependency_spike_and_decisions.md`](feature_typesafe_jev_decision_layer/07_dependency_spike_and_decisions.md) — dependency options, recommendation, open decisions
- [`08_normative_decision_protocol.md`](feature_typesafe_jev_decision_layer/08_normative_decision_protocol.md) — normative execution, mode, failure, concurrency, receipt, and version contracts
- [`09_question_catalog_and_state_schemas.md`](feature_typesafe_jev_decision_layer/09_question_catalog_and_state_schemas.md) — candidate question wording, criteria, disclosure tiers, and state budgets
- [`10_new_ideas_and_experiments.md`](feature_typesafe_jev_decision_layer/10_new_ideas_and_experiments.md) — ranked extensions, experiments, and rejected directions
- [`11_delivery_backlog_and_traceability.md`](feature_typesafe_jev_decision_layer/11_delivery_backlog_and_traceability.md) — dependency graph, change packages, PR order, and requirement-to-test traceability
- [`12_runtime_integration_blueprint.md`](feature_typesafe_jev_decision_layer/12_runtime_integration_blueprint.md) — exact AgentX/LangChain run context, provider batch, middleware, cancellation, ownership, and approval seams

## Source basis

The external facts were rechecked on 2026-09-20 against the official [LangChain TypeSafe integration guide](https://docs.langchain.com/oss/python/integrations/providers/typesafe), [`langchain-typesafe` package metadata](https://github.com/langchain-ai/langchain/blob/master/libs/partners/typesafe/pyproject.toml), [TypeSafe Python SDK metadata](https://github.com/typesafe-ai/typesafe-sdk-python/blob/main/pyproject.toml), [Jev model documentation](https://docs.typesafe.ai/models), [Jev 1.13 limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13), and [TypeSafe data-handling information](https://docs.typesafe.ai/legal). The new selective-routing idea follows the provider's documented distinction between relative `Choice` answers and absolute `Noul` probabilities; the two signals must be calibrated independently rather than combined arithmetically.

## Approval boundary

This package is a proposal artifact only. No dependency, source, test, configuration, or persistence change has been applied. The next approval choice is recorded in [`07_dependency_spike_and_decisions.md`](feature_typesafe_jev_decision_layer/07_dependency_spike_and_decisions.md).
