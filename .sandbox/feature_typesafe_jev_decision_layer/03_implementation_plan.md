# Implementation plan

## Delivery principle

Implement the feature as independently releasable slices. A later slice may depend on evidence from an earlier one, but no slice is allowed to smuggle in enforcement merely because the supporting types exist.

Because this is a `major_feature`, implementation should begin only after a formal feature/design artifact is created in the repository's normal design location and the OMT TDD sequence is declared. This sandbox package is the proposal, not that approval.

## Proposed code layout

### First milestone

```text
src/agentx/model/decision/
├── __init__.py
├── config.py                 # typed modes, per-kind config, validation
├── types.py                  # inputs, evidence, disposition, errors
├── specs.py                  # immutable versioned question specifications
├── provider.py               # DecisionProvider protocol + fake-friendly port
├── service.py                # off/shadow/enforce orchestration
├── state_builders.py         # minimization, budgets, redaction
├── disposition.py            # deterministic evidence-to-action policy
├── budget.py                 # per-run call/byte/time budget + circuit interface
├── receipts.py               # cohort IDs, keyed fingerprints, decision receipts
├── telemetry.py              # sanitized event schema and sink protocol
├── typesafe_provider.py      # optional SDK adapter
├── run_context.py            # per-invocation route context; never checkpointed
└── langchain_middleware.py   # model-route shadow/enforcement adapter
```

The first milestone should not create `tool_risk_middleware.py` or RAG adapters. Their contracts belong in the feature design; their runtime files land only in their approved slices.

### Test layout

```text
tests/features/feature_<NNN>.typesafe_jev_decision_layer/
├── test_config.py
├── test_state_builders.py
├── test_disposition.py
├── test_decision_service.py
├── test_typesafe_provider.py
├── test_model_route_middleware.py
├── test_model_registry_route_resolution.py
├── test_service_integration.py
├── fixtures/
│   └── model_route_cases.jsonl
└── README.md                 # feature test map and opt-in live-test policy
```

## Existing files likely to change in the first milestone

| File | Intended change | Why |
|---|---|---|
| `pyproject.toml` | Add a pinned optional extra such as `typesafe = ["typesafe-sdk==0.7.0"]` | Keep AgentX runnable without the provider package |
| `uv.lock` | Regenerate through the repository-approved protected-file path | Reproducible optional dependency resolution |
| `src/agentx/model/ai/model_registry.py` | Add non-persisting `create_llm(provider_id)` and route-validation helpers | Routing must not mutate the user's current selection |
| `src/agentx/model/ai/service.py` | Expose bounded provider-ID construction through the registry | One application facade for model construction |
| `src/agentx/model/coding/coding_agent_service.py` | Accept/inject decision middleware and preserve middleware order | Coding route shadowing and later enforcement |
| `src/agentx/model/react/react_agent_service.py` | Accept/inject middleware | ReAct parity |
| `src/agentx/model/rag_v2/rag_v2_agent_service.py` | Accept/inject middleware and preserve summarization order | RAG v2 parity |
| UI/controller composition points | Construct or inject a shared `DecisionService` | Avoid one provider client per screen or request |

The exact UI composition change should be selected after tracing application startup. Constructors already support service injection in controllers, so tests should continue injecting fakes rather than reaching a global network client.

## Slice 0 — dependency and API spike

### Goal

Prove that the stable TypeSafe SDK can satisfy AgentX's transport needs without changing the LangChain dependency family.

### Work

1. Resolve `typesafe-sdk==0.7.0` with the current lock in an isolated spike.
2. Verify sync and async client construction on Python 3.14.
3. Verify explicit model pinning, base URL injection, total timeouts, retry configuration, and clean close.
4. Inspect whether an injectable transport or test server is the best seam for provider-adapter tests.
5. Map SDK `Choice`, `Noul`, and `Score` response objects to AgentX types.
6. Confirm how request IDs, returned model IDs, token usage, cancellation, and error types surface.
7. Confirm that provider traces are not automatically exported by the SDK path.
8. Record the resolved dependency diff and run the full AgentX suite.

### Exit criteria

- no LangChain version changes;
- no live network in ordinary tests;
- deterministic fake response path exists;
- timeout and rate-limit errors map cleanly;
- no raw state appears in default logs;
- written go/no-go result.

If the SDK fails the spike, compare the LangChain integration and raw HTTP paths using the matrix in `07_dependency_spike_and_decisions.md`; do not silently switch.

## Slice 1 — provider-neutral kernel

### Goal

Land the decision semantics without any external provider dependency.

### Work

- Implement enums and frozen dataclasses.
- Implement `DecisionConfig.validate()`.
- Define a narrow, batched provider protocol. The TypeSafe API evaluates multiple typed questions over one state; the port must preserve that ability even though AgentX exposes kind-specific service methods:

```python
class DecisionProvider(Protocol):
    def evaluate(
        self,
        *,
        state: Mapping[str, object],
        questions: tuple[ProviderQuestion, ...],
        model_id: str,
        deadline_seconds: float,
        cancel: CancellationToken,
    ) -> ProviderBatchResult: ...

    def close(self) -> None: ...
```

- Keep question definitions in AgentX code with explicit version constants.
- Register each definition as an immutable spec linked to one state builder, fallback policy, fixture family, and disclosure tier.
- Add structural tests that require exact answer-enum coverage and exact model pins.
- Implement mode behavior with a fake provider.
- Validate the batch: expected question IDs appear exactly once; no unexpected ID is accepted; result primitive matches each question; Choice labels exactly match; values are finite and in `[0, 1]`; Choice probabilities sum within tolerance; returned model equals the allowed pin.
- Emit only sanitized `DecisionEvent` objects.

### Important construction rule

`DecisionService` accepts `provider_factory: Callable[[], DecisionProvider]`. It must not invoke the factory in `off` mode or during import. A missing optional package is therefore harmless until an enabled TypeSafe configuration is actually used.

## Slice 2 — TypeSafe adapter and shadow model routing

### Provider adapter

`TypeSafeDecisionProvider` should:

- import `typesafe_sdk` inside construction, not module import;
- receive the API key through the SDK/environment boundary without storing it on serializable config;
- use `jev-1.13.0` explicitly;
- own one long-lived client;
- set a bounded timeout and no interactive-path retry beyond the agreed total deadline;
- map SDK errors to the AgentX error taxonomy;
- translate provider response models immediately and discard them;
- never log request state or full exceptions that may contain payloads.

### Model registry extension

Add a non-mutating API rather than calling `select`:

```python
def create_llm(self, provider_id: str) -> BaseChatModel:
    info = self.get_provider(provider_id)
    if info is None:
        raise UnknownProviderError(provider_id)
    return info.factory().create_llm()
```

The persisted `_selected_id` remains unchanged. A unit test must prove route resolution does not write `model_selection.json`.

### Run preflight and middleware behavior

The agent service should create a fresh `run_id`, classify the accepted top-level user request exactly once, and pass a typed `DecisionRunContext` through LangGraph's non-checkpointed run context. The middleware reads that context for every model call and uses `ModelRequest.override(model=...)` only for an accepted enforcing disposition. Do not store `BaseChatModel`, provider clients, or decision state in the conversation checkpoint.

The concrete call path is specified in `12_runtime_integration_blueprint.md`. This split avoids three bugs: reclassification after every tool call, confusing a multi-turn `thread_id` with a run, and placing non-serializable models in graph state.

In `shadow`:

- actual model is always the model already supplied to the agent;
- recommended route and counterfactual provider ID are recorded;
- no alternate LLM is constructed;
- provider failure is recorded and otherwise invisible to the run.
- decision latency may delay the first model token and is measured explicitly; semantic output and selected model remain baseline-equivalent.

In later `enforce`:

- confidence below the route threshold selects `current`;
- unknown/missing route mapping selects `current`;
- `local` is rejected unless the registry entry is local;
- alternate LLM construction occurs lazily after a valid disposition;
- the same selected model is used throughout the top-level run;
- the persisted current provider remains unchanged.

### Middleware ordering

Do not assume hook order. Add tests that pin both the effective middleware names and the request model observed before and after the AgentX route wrapper for:

1. Coding `create_deep_agent` with existing summarization tool middleware;
2. Coding fallback `create_agent`;
3. RAG v2 `create_deep_agent` with subagents and summarization;
4. RAG v2 fallback `create_agent`;
5. ReAct `create_agent`.

The decision preflight receives the raw accepted `user_message` directly from `stream_agent()` before summarization can rewrite graph messages. The middleware receives only the disposition in run context, so raw classifier state cannot leak into later middleware traces.

## Slice 3 — evaluation harness

Create an offline runner that reads a JSONL fixture, invokes an injected provider, and produces a report with:

- exact dataset and question schema hashes;
- complete cohort identifier and paired-cohort comparison when evaluating an upgrade;
- exact Jev model ID;
- confusion matrix and per-class precision/recall;
- coverage after abstention/fallback;
- expected calibration error and Brier score;
- latency percentiles and error rates;
- input-token distribution and estimated cost;
- disagreement examples referenced by case ID, with sensitive text excluded from the report.

The detailed execution contract is in `08_normative_decision_protocol.md`; candidate question text and initial state budgets are in `09_question_catalog_and_state_schemas.md`. Implementations should not invent different semantics inside middleware.

Live evaluation must be opt-in and separately marked. Default `uv run pytest` remains network-free.

## Slice 4 — optional route enforcement

This slice is proposed only after the route holdout gate passes.

Work:

- accept an evaluation receipt in configuration or release metadata;
- add the global and per-kind kill switches;
- enable a small cohort or explicit opt-in;
- expose the selected route and fallback reason in sanitized diagnostics;
- monitor task outcome, latency, and cost against the current-provider control;
- keep `current` as the immediate fallback.

Enforcement rollout should start with `fast` versus `current`. The `powerful` and `local` routes have different failure costs and should be unlocked separately.

## Slice 5 — authorization and approval prerequisite

Before tool risk can influence execution:

1. inventory the effective compiled tool set, including Deep Agents backend tools, and classify each resource plane and mutation capability;
2. define `AuthorizationResult` and an adapter that runs before LangChain tool execution;
3. preserve `_resolve_safe_path` and tool-internal checks as defense in depth;
4. introduce an `ApprovalRequest` containing sanitized preview, reason codes, decision ID, and expiry;
5. use the pinned graph's human-in-the-loop/interrupt capability, but adapt interrupt events and `Command(resume=...)` into AgentX service and controller APIs;
6. render approval in the UI;
7. resume or reject the exact same tool call once;
8. persist enough state for crash-safe handling or explicitly expire on restart;
9. test duplicate resume, cancellation, reset, and stale approval behavior.

An error `ToolMessage` is acceptable for a deny, but not a substitute for approval.

## Slice 6 — tool-risk shadow and enforcement

### Shadow first

- Classify `file_edit` and `file_create` as the first host-workspace action class, not as the complete graph tool inventory.
- Alternate host mutation paths must be equivalently guarded or unavailable; state-backend mutations are recorded as a separate class.
- Run deterministic authorization first.
- Skip the provider on deterministic deny.
- Build the minimal state defined in the security document.
- Record actual deterministic action and counterfactual Jev-composed action.
- Label disagreements for evaluation.

### Enforcement later

- Require separately approved false-allow and false-block ceilings.
- Default provider error to `review`.
- Keep deterministic deny dominant.
- Do not cache a risk answer across distinct tool arguments.
- Bind approvals to decision ID, tool-call ID, normalized argument hash, thread ID, and expiry.

## Slice 7 — independent RAG experiments

RAG work begins only after routing is stable. Implement relevance, prompt-injection likelihood, and citation support as separate methods and reports.

- Classify one retrieved chunk or one claim/chunk pair at a time.
- Retrieve and deterministically filter first.
- Preserve source IDs and offsets locally; send only bounded text.
- Never treat “relevant” as “safe” or “supports citation.”
- Do not remove all context on provider failure; fall back to the current RAG pipeline.

## Rollback plan

At every slice:

- set global mode to `off`;
- avoid constructing the provider;
- omit decision middleware from agent construction;
- use `get_current_llm()` and current deterministic tool behavior;
- retain sanitized events only for the configured retention window;
- remove the optional dependency after the experiment if the value hypothesis fails.

No schema migration should be required to disable the first milestone. If later telemetry moves into SQLite, its tables must be additive and safe to leave unused.
