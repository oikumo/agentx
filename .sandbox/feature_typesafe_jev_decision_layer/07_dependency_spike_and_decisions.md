# Dependency spike and decision record

## Current dependency facts

AgentX currently pins:

| Package | AgentX pin |
|---|---:|
| `langchain` | `1.3.14` |
| `langchain-core` | `1.5.3` |
| `deepagents` | `0.7.5` |
| `langgraph` | `1.2.10` |
| `pydantic` resolved transitively | `2.12.5` |
| `tenacity` resolved transitively | `9.1.4` |

The official packages available on 2026-09-20 have materially different integration costs:

| Option | Current package facts | AgentX impact |
|---|---|---|
| `typesafe-sdk==0.7.0` | Stable-classified Python SDK; depends on `httpx2`, Pydantic, Tenacity, and typing extensions; no LangChain dependency | Adds a provider SDK but does not inherently require a LangChain-family upgrade |
| `langchain-typesafe==0.0.1a2` | Prerelease integration; requires `langchain-core>=1.6.2`; experimental middleware additionally requires `langchain>=1.3.15` | Conflicts with AgentX's exact `langchain-core==1.5.3` and `langchain==1.3.14` pins |
| Direct `/v1/systemone` HTTP | No provider package | AgentX owns authentication, request/response models, retries, backoff, errors, compatibility, and lifecycle |

Sources: [TypeSafe SDK metadata](https://github.com/typesafe-ai/typesafe-sdk-python/blob/main/pyproject.toml), [`langchain-typesafe` metadata](https://github.com/langchain-ai/langchain/blob/master/libs/partners/typesafe/pyproject.toml), and the [TypeSafe model/API overview](https://docs.typesafe.ai/models).

The SDK option is only *likely* to be compatible from metadata. The spike must prove the full lock resolution and runtime behavior before adoption.

## Alternatives

### Alternative A — stable TypeSafe SDK behind AgentX adapters

**Recommendation:** choose for the first spike.

Shape:

- optional dependency `typesafe-sdk==0.7.0`;
- AgentX-owned `DecisionProvider` protocol;
- `TypeSafeDecisionProvider` maps SDK types to AgentX types;
- AgentX-owned LangChain middleware for routing and, later, tool risk;
- AgentX-owned telemetry, privacy, thresholds, and failure policy.

Advantages:

- avoids the known LangChain pin conflict;
- uses the official typed client instead of owning raw HTTP;
- keeps experimental middleware semantics out of the authorization boundary;
- avoids automatic LangSmith classifier traces described by the LangChain integration;
- lets the provider be tested or replaced behind a narrow port.

Costs:

- AgentX must write and test its own middleware adapters;
- Runnable composition is not supplied by the package;
- transport injection and cancellation behavior still need verification;
- a new HTTP stack dependency, `httpx2`, must be reviewed.

### Alternative B — first-party LangChain integration

Use `langchain-typesafe==0.0.1a2` and upgrade the LangChain family coherently.

Advantages:

- `TypeSafeClassifier` is a LangChain `Runnable`;
- ready-made model-routing and tool-risk middleware can accelerate a prototype;
- LangChain message conversion and tracing are built in.

Costs and risks:

- requires at least `langchain-core>=1.6.2` while AgentX pins `1.5.3`;
- experimental middleware requires at least `langchain>=1.3.15` while AgentX pins `1.3.14`;
- the integration package is `0.0.1a2` and its experimental APIs may change;
- the documented tool middleware blocks at a fixed `0.5` threshold, sends up to 30 recent messages, and returns an error rather than requesting approval;
- built-in tracing is a privacy surface that needs explicit payload controls;
- every LangChain provider, Deep Agents, streaming, subagent, and fallback path must be requalified.

This is a valid later choice if AgentX already plans the required dependency upgrade. It is disproportionate for proving the decision-layer hypothesis now.

Official behavior references: [LangChain integration guide](https://docs.langchain.com/oss/python/integrations/providers/typesafe) and [Auto Mode source](https://github.com/langchain-ai/langchain/blob/master/libs/partners/typesafe/langchain_typesafe/experimental/middleware/auto_mode.py).

### Alternative C — direct HTTP adapter

Implement `POST /v1/systemone` directly behind the same `DecisionProvider` port.

Advantages:

- smallest dependency surface;
- full control over HTTP client, logging, retry, and tracing behavior;
- no LangChain coupling.

Costs and risks:

- AgentX owns wire compatibility and typed validation;
- retry/backoff/rate-limit behavior must be maintained;
- easy to mishandle error bodies, secrets, connection pooling, or future API changes;
- duplicates work already maintained by the official SDK.

Choose only if the stable SDK fails the spike for a concrete reason that a small HTTP adapter actually solves.

### Alternative D — do not integrate Jev

Keep deterministic decisions and existing chat models.

Advantages:

- no external processor, dependency, latency, or operational surface;
- no new privacy or model-quality risk.

Cost:

- no opportunity to test whether typed, lower-cost classification improves AgentX.

This remains the correct outcome if the spike or shadow evaluation does not demonstrate value.

## Recommended spike protocol

### 1. Resolution

- Add only the candidate optional SDK pin in the spike.
- Resolve without upgrading unrelated packages.
- Review the full lock diff, licenses, and new transitive packages.
- Confirm Python 3.14 wheels/source behavior.
- Reject the spike if it forces a LangChain-family change.

### 2. API characterization

Build a disposable adapter proof covering:

- one `Choice` route question;
- one `Noul` risk question;
- exact `jev-1.13.0` model selection;
- returned model ID, request ID, and usage;
- synchronous and asynchronous calls;
- explicit base URL and test transport/server;
- timeout, cancellation, rate limit, invalid response, authentication failure, and close;
- client reuse across decisions.

### 3. Privacy characterization

- Verify default SDK logging at all log levels used by AgentX.
- Verify exceptions do not expose request state or authorization headers.
- Confirm no automatic LangSmith or OpenTelemetry payload export occurs.
- Run the leak-sentinel tests.
- Document every environment variable the SDK reads.

### 4. Compatibility

Exercise current AgentX behavior after adding the optional extra:

- import and startup without the extra installed;
- startup with the extra but no API key while mode is off;
- Coding and RAG v2 Deep Agents paths;
- `create_agent` fallbacks;
- streaming and cancellation;
- full test suite.

### 5. Written result

The spike report records:

- exact resolved packages;
- API/error mapping;
- lifecycle and test seam;
- privacy observations;
- test results;
- known gaps;
- proceed with A, reconsider B/C, or stop.

## Recorded design decisions

| ID | Decision | Status | Reason |
|---|---|---|---|
| D1 | AgentX owns decision types and disposition policy | Proposed recommendation | Prevent provider/framework types from becoming product policy |
| D2 | Use `typesafe-sdk==0.7.0` for the first spike | Proposed recommendation | Lowest known compatibility risk |
| D3 | Pin `jev-1.13.0` for evaluation and enforcement | Proposed recommendation | Aliases can move and invalidate calibration |
| D4 | First runtime slice is `off` plus shadow model routing | Proposed recommendation | Lowest-stakes place to validate the system |
| D5 | Keep deterministic denies authoritative | Required invariant | Probabilistic evidence cannot grant authority |
| D6 | Separate evidence from disposition | Required invariant | Provider answer and AgentX action are different facts |
| D7 | Tool-risk enforcement waits for interrupt/resume approval | Required prerequisite | Blocking is not equivalent to human review |
| D8 | RAG relevance, injection risk, and citation support are separate decisions | Required scope rule | Different semantics and failure costs |
| D9 | Every decision uses an immutable versioned spec and cohort ID | Proposed recommendation | Prevent question, state, model, and threshold drift from being pooled |
| D10 | Enforce explicit privacy disclosure tiers in state builders | Proposed recommendation | Prevent gradual expansion from bounded text to history or raw content |
| D11 | Add per-run decision budgets and stable receipts to the kernel | Proposed recommendation | Bound amplification and join audit/approval/replay without raw state |
| D12 | Treat paired route Choice plus promotion Noul as an experiment, not v1 | Proposed recommendation | It may improve abstention but requires separate calibration |
| D13 | Carry the route through an immutable, non-checkpointed per-invocation context | Proposed recommendation | Prevent cross-run leakage and avoid serializing model objects into graph state |
| D14 | Make the provider port batch-shaped while keeping public methods kind-specific | Proposed recommendation | Match System One's shared-state/multiple-question contract without exposing provider types |
| D15 | Require an effective-tool/resource inventory before tool-risk work | Required prerequisite | Guarding one alias is insufficient if another tool reaches the same protected resource |

## Open decisions before implementation

| ID | Decision needed | Blocks |
|---|---|---|
| O1 | Approve Alternative A spike, choose B/C, or stop | Any dependency work |
| O2 | Choose the formal feature number/project and design artifact location | Major-feature implementation |
| O3 | Decide how users enable external processing and acknowledge privacy implications | Shadow runtime |
| O4 | Choose decision-event storage path, permissions, size, and retention | Persistent shadow evaluation |
| O5 | Approve initial route mappings from semantic route to provider ID | Route enforcement only |
| O6 | Approve route acceptance thresholds after calibration | Route enforcement only |
| O7 | Define shared tool authorization semantics and approval UX | Tool-risk shadow/enforce integration |
| O8 | Approve false-allow and false-block ceilings | Tool-risk enforcement |
| O9 | Approve route-v1 question wording, disclosure tier, and state budget | Route calibration |
| O10 | Decide whether keyed input fingerprints are available or omitted | Receipt correlation |
| O11 | Approve per-run call/byte/time budgets and circuit-breaker defaults | External shadow runtime |
| O12 | Choose the application composition owner for one shared `DecisionRuntime` and its shutdown | Any production shadow traffic |
| O13 | Approve the effective tool/action/resource registry and handling of Deep Agents built-ins | Tool-risk shadow/enforcement |

## Approval gate

The proposed next action is **Alternative A: a dependency/API spike only**, followed by a written compatibility result. It does not authorize production integration or enforcement.

No alternative has been executed in this documentation pass.
