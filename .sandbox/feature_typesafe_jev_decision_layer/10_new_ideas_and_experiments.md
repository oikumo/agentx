# New ideas and experiment portfolio

## How to read this document

These ideas extend the core proposal without silently expanding the first milestone. Each is classified as **adopt now**, **shadow experiment**, **later**, or **reject**. “Adopt now” means include the architectural seam or offline tooling, not enable new production behavior.

## Portfolio

| ID | Idea | Value | Complexity | Recommendation |
|---|---|---:|---:|---|
| N1 | Selective route promotion gate | High | Medium | Shadow experiment after route v1 |
| N2 | Decision budget governor | High | Low | Adopt now |
| N3 | Decision receipts | High | Low | Adopt now |
| N4 | Question-spec linter | Medium | Low | Adopt now |
| N5 | Paired cohort replay | High | Medium | Build into evaluation harness |
| N6 | Deterministic fast-path bypass | High | Medium | Shadow experiment |
| N7 | Risk-signal decomposition | Medium | High | Later shadow experiment |
| N8 | Privacy disclosure tiers | High | Low | Adopt now |
| N9 | Sequential drift monitor | Medium | Medium | Limited-enforce prerequisite |
| N10 | Provider capability registry | Medium | Medium | Later, before a second provider |
| N11 | Human-review learning loop | High | High | Later with strict governance |
| N12 | Multi-model voting | Low initially | High | Reject for first generation |
| N13 | Typed per-invocation route context | High | Low | Adopt now |
| N14 | Effective tool/action inventory | High | Medium | Authorization prerequisite |

## N1 — selective route promotion

### Hypothesis

A route Choice can rank alternatives even when none is clearly better than the current provider. Asking an independent promotion Noul alongside the Choice may reduce unnecessary switching.

### Experiment

- Use the same minimized state and one provider request.
- Compare route v1 (`Choice` including `current`) against v2 (`Choice` plus promotion Noul).
- Calibrate each signal independently.
- Measure alternate-route precision, coverage, cost savings, and task success.
- Prefer the simpler v1 unless v2 materially improves selective risk/coverage.

### Guardrail

Do not multiply the two probabilities or infer that they are mathematically consistent. The official model guidance warns that separate primitives do not guarantee structural probability identities.

## N2 — decision budget governor

### Hypothesis

An explicit local budget prevents latency and cost amplification more reliably than provider rate limits.

### Design

The governor tracks calls, bytes, provider time, and optional estimated cost by run and kind. It grants or denies before transport. Exhaustion uses the decision-specific fallback and emits `run_budget_exhausted`.

Initial defaults should be conservative:

- model route: one call per top-level run;
- tool risk: disabled; later a small cap per run;
- RAG: offline/shadow batch only until cost behavior is known;
- global concurrency: bounded independently from agent worker count.

The governor is deterministic and remains useful with any provider.

## N3 — decision receipts

### Hypothesis

A small immutable receipt makes authorization, telemetry, debugging, and replay joinable without retaining raw content.

### Design

The receipt carries opaque identifiers, cohort, keyed input fingerprint, disposition, and reason code. Approval binds to receipt plus normalized tool-call hash and expiry. Evaluation can join a later outcome to the decision without storing the request.

Receipts are not cryptographic proof that a provider answered correctly. They are local provenance and replay protection.

## N4 — question-spec linter

### Hypothesis

Many decision bugs are specification drift: an enum changes but criteria, fixtures, thresholds, or state builders do not.

### Checks

- every `DecisionKind` has one registered active spec;
- answer enum equals criteria keys;
- question/state/threshold versions match the naming convention;
- exact model ID is used, not an alias;
- each spec links to a builder, fallback policy, and fixture family;
- event schema can represent every answer and reason code;
- disclosure tier does not exceed configuration.

The linter stays structural. Natural-language review and evaluation remain human responsibilities.

## N5 — paired cohort replay

### Hypothesis

Model, prompt, schema, or threshold upgrades are safer when old and new cohorts are evaluated on identical cases and recent sanitized shadow samples.

### Design

The evaluator produces a paired report:

- per-case old/new answer and disposition;
- transition matrix;
- changed-error review queue;
- calibration and coverage deltas;
- latency and token deltas;
- list of safety-critical regressions.

Promotion is blocked when the new cohort improves averages but regresses a protected scenario family such as locality or deterministic-deny composition.

## N6 — deterministic fast-path bypass

### Hypothesis

Some route cases need no semantic model: explicit local-only requests, explicit user model choice, or services that disallow routing.

### Design

A local preclassifier returns `terminal` or `needs_semantic_decision`. In shadow, report how often it bypasses Jev and whether bypassed cases disagree with labeled outcomes. Only high-precision rules graduate.

This is not a second policy engine. Rules are narrow, explicit, and auditable.

## N7 — decomposed risk signals

### Hypothesis

Independent named risk questions can be more actionable than one aggregate probability.

### Candidate signals

- insufficient authorization;
- destructiveness/irreversibility;
- sensitive-data disclosure;
- external side effect;
- persistence or security-boundary change.

The disposition policy combines signals in code by action class. This could produce clearer approval explanations and targeted thresholds, but evaluation cost and multiple-comparison risk are significant. Keep it out of the first tool-risk slice.

## N8 — privacy disclosure tiers

### Hypothesis

An explicit tier system makes privacy review and configuration comprehensible and prevents feature code from gradually sending richer state.

### Design

Every decision spec declares its maximum tier. Every deployment declares an allowed tier. Effective disclosure is the lower of the two. A higher tier requires a new state-schema version, evaluation cohort, and user/operator approval.

## N9 — sequential drift monitor

### Hypothesis

Aggregate offline quality can remain stable while live input mix or provider behavior drifts.

### Signals

- answer and fallback distribution by service;
- confidence/calibration proxy distribution;
- provider error and latency rates;
- fraction of decisions changing behavior;
- disagreement rate on a small labeled audit sample;
- returned model-ID mismatch.

Use minimum sample sizes and predeclared alert rules. Do not auto-change thresholds in response to drift; return to shadow or off and re-evaluate.

## N10 — provider capability registry

### Hypothesis

Provider replacement becomes safer if capabilities are explicit rather than inferred from adapter type.

Possible capability fields include supported primitives, multiple questions per request, exact model pinning, cancellation, usage reporting, request IDs, maximum state size, and test-transport support. The decision service validates a spec against capabilities at startup.

Do not build this abstraction until a second real provider or local classifier is evaluated; a protocol plus one adapter is enough initially.

## N11 — governed human-review learning loop

### Hypothesis

Approval outcomes and reviewer labels can improve future evaluation data.

### Constraints

- approval is not automatically a ground-truth safety label;
- examples enter a quarantine queue, not the dataset directly;
- privacy review and consent apply before retaining text;
- near-duplicates stay in the same split family;
- threshold changes require a new policy version and frozen holdout;
- no online self-tuning.

## N12 — multi-model voting

### Decision

Reject for the first generation. Voting adds cost, latency, correlation ambiguity, more external disclosure, and harder calibration. It may be revisited only if a single-provider cohort fails a concrete reliability requirement that a demonstrably diverse second model solves.

## N13 — typed per-invocation route context

### Hypothesis

Separating a top-level `run_id` from the multi-turn `thread_id` makes one-decision-per-turn semantics testable and prevents route choices from leaking across concurrent or later turns.

### Design

The agent service performs route preflight once, creates an immutable context containing the disposition and optional alternate model, and passes it to the compiled graph for that invocation only. LangChain middleware reads the context and overrides the request-local model. Nothing is written to checkpointed conversation state or a mutable module global.

This is a core correctness seam, not an optional optimization.

## N14 — effective tool/action inventory

### Hypothesis

Authorization by literal tool name is incomplete when agent frameworks add built-ins or delegation surfaces. Mapping constructed tools to normalized actions and resource planes prevents alias and subagent bypasses.

### Design

At graph-construction time, record the effective tool names and their declared capability metadata. Tests compare that set to the reviewed action registry. Unknown mutation-capable tools fail enforcement readiness. The registry distinguishes host workspace, agent state backend, remote service, and process/sandbox effects so one threshold is not misapplied across unlike resources.

## Additional anti-ideas

The following should remain out of scope:

- letting the classifier generate policy or route identifiers;
- automatically changing thresholds from live outcomes;
- sending full history because the provider accepts large context;
- chaining classifiers until one returns the desired answer;
- treating high confidence as authorization;
- using a moving model alias in enforcement;
- persisting raw decision state for easier debugging;
- using relevance as proof of safety or citation correctness.

## Recommended additions to the first milestone

Add only these ideas to the first implementation boundary:

1. decision budget interface with route limit of one;
2. decision receipt and keyed local fingerprint support, with omission allowed;
3. disclosure tiers enforced by state builders;
4. structural question-spec linter;
5. paired-cohort report format in the offline evaluator.
6. typed per-invocation route context and effective-tool inventory contracts.

Run N1 and N6 as offline or shadow experiments after route v1 establishes a baseline. Defer all other ideas until their prerequisites exist.
