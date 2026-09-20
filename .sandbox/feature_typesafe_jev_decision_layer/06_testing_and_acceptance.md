# Testing and acceptance

## Test strategy

The default suite is deterministic, offline, and provider-independent. Live TypeSafe checks are opt-in smoke tests, never a prerequisite for ordinary development or `uv run pytest`.

Tests are organized around contracts and failure boundaries rather than the happy path alone.

## Test layers

| Layer | What it proves | Network |
|---|---|---|
| Pure unit | Config, validation, redaction, distributions, dispositions | Never |
| Provider adapter | SDK translation and error mapping via fake transport/server | Never |
| Middleware contract | Hook ordering, state propagation, model selection, fallback | Never |
| Service integration | Coding/ReAct/RAG v2 construction and streaming compatibility | Never |
| Persistence/telemetry | Sanitization, rotation, retention, concurrency | Never |
| Offline evaluation | Metrics and report reproducibility from fixtures | Never |
| Live smoke | Credentials, endpoint, pinned model, minimal real response | Opt-in only |

## Kernel test matrix

### Configuration

- `off` validates with no API key or provider package.
- `shadow`/`enforce` reject missing provider or model pin.
- Invalid threshold ordering is rejected.
- Unknown route mapping is rejected for enforce mode.
- `local` mapped to a cloud registry entry is rejected.
- Tool-risk enforce is rejected when approval capability is false.
- Per-kind enablement cannot bypass global `off`.
- API keys are absent from `repr`, serialization, and persisted config.
- A spec's criteria keys exactly cover its answer enum.
- Question, state, model, threshold, and adapter versions produce the expected cohort ID.
- A deployment disclosure tier cannot be exceeded by a decision spec or state builder.

### Provider response validation

- accepted labels map to the exact AgentX enum;
- unknown, missing, and duplicate labels fail;
- negative, greater-than-one, NaN, and infinite probabilities fail;
- invalid probability sums fail outside documented tolerance;
- missing confidence is accepted only for primitives where it is not defined;
- returned model mismatch fails in enforce mode and is visible in shadow telemetry;
- token usage and request ID are optional without breaking the contract.

### Mode semantics

- provider factory is not called in `off`;
- state builder is not called in `off`;
- shadow invokes the provider but `actual_effect` is false;
- shadow output does not alter the baseline route or authorization;
- shadow records first-token and total latency overhead instead of claiming timing equivalence;
- enforce applies only a validated, configured selection;
- every provider error maps to the decision-specific fallback;
- cancellation does not emit a misleading success event.
- the route run budget allows one single-flight decision and rejects amplification deterministically;
- a late provider response after cancellation cannot alter state or emit an applied disposition;
- receipt fingerprints are omitted without a local key and are installation-scoped when enabled.
- two concurrent runs cannot observe each other's route disposition, model object, or decision ID;
- hot off leaves an inert wrapper with zero provider/state-builder calls, while cold off omits the wrapper from the constructed graph.

## State minimization and privacy tests

- only allowlisted fields survive serialization;
- absolute repository and home prefixes are removed;
- common secrets are replaced with category tokens;
- redaction counts contain no matched content;
- control characters and invalid Unicode are handled deterministically;
- per-field, total-byte, and token budgets are enforced;
- redaction failure prevents transport;
- raw input does not appear in event serialization, logs, exception strings, or test snapshots;
- model-route state excludes message history and tool output;
- tool-risk state excludes full edit content in its first schema;
- decision input fingerprints do not permit raw text recovery and are stable only within the intended scope.

Add sentinel strings such as `DO_NOT_LEAK_SENTINEL` to raw inputs, then assert recursively that they are absent from all logs, events, traces, and raised public errors.

## TypeSafe adapter tests

- lazy import succeeds when optional package is present;
- enabled TypeSafe mode raises a clean configuration error when absent;
- client is constructed once and reused;
- exact model ID is sent on every request;
- base URL and timeout are injectable for tests;
- client closes exactly once;
- HTTP timeout, connection error, `429`, `4xx`, `5xx`, invalid JSON, and invalid typed response map correctly;
- SDK retry settings respect the AgentX total deadline;
- exception sanitization removes payload and credentials;
- sync and async adapters, if both implemented, return equivalent AgentX evidence.

## Model routing tests

### Registry

- `create_llm(provider_id)` constructs a known provider;
- unknown ID fails without changing selection;
- route construction does not call `select` or write the selection file;
- `current` remains available after any route error;
- local/cloud validation uses registry metadata.

### Middleware

- latest top-level human request is classified once per run;
- two turns on one `thread_id` receive different `run_id` and decision IDs;
- nested tool messages do not trigger route changes in v1;
- shadow never constructs or invokes the recommended alternate model;
- below-threshold evidence falls back to current;
- invalid mapping falls back to current;
- accepted enforce route uses the same model for all model calls in the run;
- a new run receives a new decision ID;
- cancellation and stream errors preserve current service callbacks;
- state passed to middleware traces omits raw classifier state.
- `ModelRequest.override(model=...)` changes only the request-local model and never the graph's persisted selection;
- `DecisionRunContext` is not written to the checkpointer;
- an explicitly injected LLM bypasses routing unless the caller supplies baseline provider identity and explicitly enables route override.

### Service parity

Run the same construction/stream assertions for:

- Coding with Deep Agents;
- Coding fallback with `create_agent`;
- ReAct;
- RAG v2 with Deep Agents and subagents;
- RAG v2 fallback;
- an explicitly injected LLM, which must remain authoritative unless route enforcement was explicitly enabled for that service.

## Tool authorization and approval tests

These tests are prerequisites for tool-risk enforcement.

### Authority composition

- deterministic deny plus any probability is deny;
- deterministic review plus low probability remains review;
- deterministic allow maps through low/review/block bands at exact boundary values;
- provider error follows configured fail policy;
- shadow actual action equals the deterministic baseline;
- unguarded tools bypass classification;
- read-only tools bypass classification in the initial policy.
- the compiled tool inventory has no unclassified path to the protected host-workspace action class;
- backend `edit_file`/`write_file` actions are either proven state-backend-only, guarded under their own action class, or disabled;
- any sandbox `execute` capability is explicitly classified rather than inferred from its tool name.

### Approval lifecycle

- review interrupts before the tool handler runs;
- approval displays sanitized arguments and stable reason codes;
- approval resumes the same call exactly once;
- rejection never invokes the handler;
- expired approval cannot resume;
- changed argument hash invalidates approval;
- thread reset and cancellation invalidate pending approval;
- duplicate approval/rejection is idempotent;
- application restart behavior is explicit and tested;
- deny returns a clear tool result without exposing classifier internals.

### Filesystem defense in depth

- authorization path normalization and `_resolve_safe_path` agree on inside/outside cases;
- symlink and traversal cases remain blocked by the tool even if earlier checks are wrong;
- a low-risk answer cannot bypass existing atomic-write protections;
- `file_create` cannot overwrite an existing file;
- risk middleware never mutates tool arguments.

## RAG tests

- relevance and citation support use different question IDs and thresholds;
- one chunk/claim pair is sent per atomic decision;
- retrieval occurs before classification;
- provider failure preserves the baseline retrieval path;
- no result claims verified citation support when the check is unavailable;
- adversarial passage text cannot affect authorization or configuration;
- source IDs remain local and map correctly after filtered results;
- empty filtered context is handled without hallucinated support.

## Telemetry tests

- event schema round-trips and rejects unknown required versions;
- raw state is not a field on `DecisionEvent`;
- actual and counterfactual actions are distinct;
- fallback reason codes are stable;
- writes are thread-safe for the console's worker model;
- rotation enforces size/age limits;
- retention cleanup targets only the configured event files;
- sink failures never change route or authorization outcomes;
- `off` uses the null sink and writes nothing.

## Evaluation harness tests

- fixture split leakage detector catches duplicated semantic-family IDs;
- confusion matrices match a hand-calculated tiny dataset;
- Brier score and calibration bins match golden values;
- abstentions are not counted as correct classifications;
- acceptable-set and preferred-label scores differ correctly;
- cost calculation uses the report's pinned pricing input, not a hidden live constant;
- reports include all cohort-version fields;
- paired-cohort reports produce a correct old-to-new disposition transition matrix;
- protected-scenario regressions remain visible even when aggregate metrics improve;
- Choice and promotion-Noul signals are calibrated separately in the optional route-v2 experiment;
- a second run over the same inputs and fake responses is byte-stable apart from declared timestamps;
- prohibited fixture fields are rejected before a live evaluation.

## Live smoke policy

Live tests:

- are marked separately and excluded from default pytest configuration;
- require an explicit environment switch in addition to `TYPESAFE_API_KEY`;
- send only synthetic, non-sensitive text;
- ask one small question against the exact pinned model;
- assert returned model ID and typed shape;
- have a strict timeout and no automatic broad retry;
- never print request or response payloads;
- skip cleanly when credentials are absent.

## Acceptance criteria by milestone

### Dependency/API spike

- `typesafe-sdk==0.7.0` resolves without changing LangChain pins.
- Python 3.14 sync/async behavior is understood.
- Timeout, cancellation, close, errors, model ID, request ID, and usage are mapped.
- Default logs/traces contain no raw state.
- Full existing suite passes.
- Spike report chooses proceed, alternate dependency, or stop.

### Off and shadow kernel

- AgentX starts and works without the SDK or `TYPESAFE_API_KEY` in `off`.
- Shadow mode does not change the selected model, stream content, authorization, or tool effects.
- Shadow preserves semantic behavior but may add measured first-token latency; the approved budget is satisfied.
- Provider is lazy and reused.
- Every decision event carries the full version tuple.
- Redaction and leak sentinels pass.
- Failures are bounded and decision-specific.

### Route enforcement

- Frozen holdout report is approved.
- Route selections are bounded to validated registry entries.
- Persisted current provider never changes.
- Below-threshold, invalid, or unavailable results use `current`.
- Exact model pin is enforced.
- Kill switch returns behavior to baseline immediately.
- Limited cohort shows accepted task-success and cost/latency results.

### Tool-risk enforcement

- Shared deterministic authorization contract is live.
- Interrupt/resume approval is tested end to end.
- Deterministic deny can never be overridden.
- False-allow ceiling passes with an approved confidence interval.
- Provider failure defaults to review or deny, never unintended execution.
- Approval binding prevents replay and duplicate execution.
- Existing sandbox and atomic-write tests remain green.

### RAG decisions

- Each decision has a separate approved report.
- Provider failure preserves current RAG behavior.
- False-supported citation rate meets its approved ceiling.
- No full repository or conversation is sent.

## Repository verification commands for a future implementation

Use repository-approved `uv` commands only. At minimum:

```text
uv run pytest tests/features/feature_<NNN>.typesafe_jev_decision_layer
uv run pytest
```

Any change to protected dependency artifacts, source, or tests must follow the repository gates active in that implementation session. This proposal does not grant those approvals.
