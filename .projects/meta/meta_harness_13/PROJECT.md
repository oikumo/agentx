# PROJECT: meta_harness_13 — OpenCode Session Inspector & Labeled Experiments (Tier 2)

> Status: **active** · **v0.1 (2026-09-26)** — created mechanically with `project.py new --slug meta_harness_13`. This is the canonical project proposal; implementation is pending approval. Session history and the resume point live in `CURRENT_STATE.md`.

## New Session Quick Start

**Objective:** Give the META HARNESS a powerful Tier-2 tool to investigate real OpenCode sessions and run reproducible experiments using labeled message logs. Inspect history, recorded reasoning, tool activity, and token usage with evidence down to individual messages and parts.

**Next:** Review the proposed implementation plan below, then allocate the feature through `new_feature.py` after approval. The project is created; no inspector implementation, experiment execution, or Tier-2 promotion has occurred.

**User requirements:** create `meta_harness_13`; build on the developed Harness Reason session-capture work; target Tier 2; make inspection powerful; treat labeled logs for running experiments as a core feature.

## Product and lineage

One tool serves two equally important workflows:

1. **Investigate real work:** find sessions, navigate parent/child activity, search and reconstruct the recorded sequence, inspect prompts/reasoning/tools/results, explain usage spikes and failures, and compare sessions with source references.
2. **Run and evaluate experiments:** declare a trial matrix, emit structured labels into real OpenCode messages, run isolated trials through existing execution controls, collect their logs, validate attribution, and compare quality, tokens, time, and failures across variants.

The baseline is `harness_reason` features 129/130: real-usage provenance, span semantics, a read-only OpenCode SQLite harvester, exact first-message labels, and measured-versus-unavailable reporting. Generalize these contracts beyond six fixed `harness|planner|kernel × H1|H3` sessions. Reuse proven behavior where it fits; inspect implementation only after this project proposal is approved, and extract shared code instead of creating competing token-accounting implementations.

The predecessor project closed its general reasoning-engine Tier-2 promotion after a negative measured result. Its test report records kernel 1,321,729 versus harness 381,919 using its stated aggregation rule, with six independent captures replayed across three repetitions. Those historical results and their limitations remain evidence. This project supplies a separate session-inspection and experimental-measurement capability; it does not reinterpret that outcome as successful promotion.

**Tier 2 means full harness integration**, following the integration meaning in the Harness Reason proposal §7: registered `omt_*` tool, `.omt` declaration, compiler-generated configuration/docs, budget checks, fresh e2e receipt, and tested enforcement behavior. It does not merely mean toolbox visibility under a `--tier 2` filter.

## Inspection capabilities

| Capability | Required behavior |
|---|---|
| Session discovery | Filter by explicit project/directory, time interval, session/parent IDs, model/provider/agent where recorded, completion state, experiment labels, and usage ranges. Return stable IDs, coverage, and pagination. |
| Session tree | Navigate root, child, and nested sessions; show direct usage and inclusive subtree usage separately; detect missing children, cycles, and duplicate membership. |
| Timeline and traces | Interleave messages, recorded reasoning parts, tool calls/results/errors, retries, compaction/resume markers, and model changes when available. Preserve explicit causal links; distinguish them from timestamp ordering. |
| Deep inspection | Retrieve full selected messages/parts and tool arguments/results, with status, timestamps, source IDs, and linked attachments when available. Handle large output through addressable pages or artifacts. |
| Structured search | Combine text search with typed filters over roles, part types, tools, errors, labels, time, models, and numeric usage. Support aggregation, grouping, and top-cost queries across selected sessions. |
| Usage profiling | Break down reported input/output/reasoning/cache-read/cache-write tokens, stored cost, wall time, and available per-message/per-step usage; locate expensive turns and cumulative context growth. |
| Failure investigation | Surface repeated calls/reads, retry loops, errors, blocked operations, and compaction patterns with witnesses and configurable thresholds. Separate observed facts, heuristic diagnoses, and unknown causes. |
| Comparison | Compare sessions, subtrees, labeled trials, or spans; show trace differences, outcomes, call counts, usage, variability, and comparability warnings. |
| Active-session capture | Capture consistent snapshots of running sessions and refresh incrementally with resumable cursors. Mark unfinished coverage and changed records explicitly. No permanently running service is required. |
| Reproducible export | Export a selected snapshot/query/experiment to versioned JSON or JSONL plus a compact report, source references, digests, and a replay manifest. |

Power comes from composable queries and drill-down: a session summary must lead to the exact expensive turn, the tool/reasoning parts surrounding it, and its experimental context without dumping the entire database into the agent context.

### Questions the feature must answer

- Which sessions and child agents consumed the most tokens for this project, and which messages account for those totals?
- What happened between a specific user instruction and the next successful edit or test, including failures and recorded reasoning?
- Where did a retry loop begin, which calls repeated, and what evidence supports the diagnosis?
- Did a large prompt come from repeated context reads, compaction, a model change, or something the logs cannot establish?
- For experiment run R, which `(case, variant, repetition)` trials and spans are complete, missing, duplicated, or contaminated?
- Did variant B improve measured cost while meeting the same quality criteria as baseline A, and can every reported value be traced to an independent capture?

## Capture and evidence contract

1. **Explicit source selection:** use an explicit DB/export path and bounded session/project/time selectors. The predecessor's `~/.local/share/opencode/opencode.db` is a documented candidate, not a universal storage-format assumption. General inspection also works on unlabeled historical sessions.
2. **Versioned adapters:** inspect schema/version capabilities before extraction. Unsupported schemas/record types, malformed JSON, unavailable attachments, and missing usage produce named coverage findings; they are never silently discarded. Scope the first adapter to the observed OpenCode schema; add export formats through the same normalized contract.
3. **Consistent snapshots:** open the session DB read-only with a SQLite read transaction; account for WAL-backed data. Do not copy only the live main DB file or assume `immutable=1` is valid for an active DB. Output artifacts go to an explicit allowed destination and become visible atomically after validation.
4. **Stable identity:** retain session, parent, message, part, call, and model/agent identifiers where present; use epoch milliseconds only for adapters that establish that unit. Timestamp ties use a stable identity tie-breaker, not an invented causal ordering.
5. **Recorded reasoning:** capture reasoning text or summaries already stored in session parts and preserve availability/redaction flags. Reasoning-token counts and reasoning-text availability are separate observations. Never reconstruct unrecorded private reasoning or label generated explanations as original log content.
6. **Provenance on every finding:** record source IDs, selected interval, adapter/schema versions, snapshot digest, query/metric definition, and coverage. A causal explanation requires supporting links; temporal association alone remains a hypothesis.
7. **Incremental capture:** replaying a cursor is idempotent; updated parts and late-arriving usage replace the corresponding version instead of being counted twice. Detect deletions or report that deletion coverage is unavailable. A growing session remains partial until completion evidence is available.
8. **Content is data:** tool output, message text, and labels never authorize commands. Preserve protected-path rules; default responses omit raw transcript bodies, while explicit inspection can retrieve permitted selected content. Keep raw captures outside tracked fixtures; use reviewed sanitized extracts for regression coverage.

## Token, cost, and attribution contract

- Preserve raw source counters independently: input, output, reasoning, cache read, cache write, and stored monetary cost. Missing values are `null` with a reason; a reported zero is valid. Do not estimate tokens from character counts and label them measured.
- Attach a versioned metric definition to every derived total. Feature 130 used `prompt = input + cache_read` and `completion = output + reasoning`; support this as an explicit legacy comparison metric. Verify each new adapter's inclusion rules before combining counters, including whether output already contains reasoning or input includes cached tokens.
- Distinguish session cumulative counters, incremental message/step counters, and token-bearing parts. Choose one accounting basis for a total; use the others for reconciliation. Never add session totals to their component messages, or message usage to duplicated step-finish usage.
- Report direct-session and subtree totals separately. Count each session once in a subtree union; shared references or overlapping selected roots must not duplicate usage.
- Reconcile per-message totals with recorded session totals where possible and expose discrepancies. Never distribute an unexplained residual across tools or spans.
- Exact span attribution requires compatible usage boundaries. If only final session totals exist, report session-level measurement and `span_usage_unavailable`; do not smear costs across events. Concurrent spans are overlapping scopes, not additive totals, unless exclusive attribution is proven.
- Distinguish end-to-end wall time from summed call durations and parallel child time. Use recorded monetary cost only; prices or savings claims require explicit, versioned inputs and sufficient comparable evidence.
- Every comparison reports independent sample counts. Replaying one capture three times is one observed trial, not three independent trials. Standard median/dispersion definitions are explicit; legacy aggregation is separately named when reproducing historical results.

## Labeled experiments — first-class delivery requirement

Labels must live in the **message logs themselves**, allowing collection from real sessions even when titles change or auxiliary session-input tables are empty. A manifest defines intended trials; observed labels bind those trials to actual sessions/messages. Session titles remain a convenience, never the sole attribution key.

### Label protocol v1 (proposed)

A label is one standalone message-text line beginning with `[mh13.experiment]`, followed by a JSON object. Parse an exact prefix plus validated fields, not fuzzy matching of arbitrary prose. Preserve the original label and its session/message/part IDs.

```text
[mh13.experiment] {"v":1,"experiment":"context_strategy","run":"run_001","trial":"case01_baseline_rep01","case":"case01","variant":"baseline","rep":1,"attempt":1,"event":"trial_start"}
[mh13.experiment] {"v":1,"run":"run_001","trial":"case01_baseline_rep01","attempt":1,"event":"span_start","span":"inspect","parent_span":null}
[mh13.experiment] {"v":1,"run":"run_001","trial":"case01_baseline_rep01","attempt":1,"event":"span_end","span":"inspect"}
[mh13.experiment] {"v":1,"run":"run_001","trial":"case01_baseline_rep01","attempt":1,"event":"trial_end","outcome":"completed"}
```

- Required trial identity: protocol version, experiment/run/trial IDs, case, variant, repetition, and attempt. `trial_start` establishes the complete identity; later events resolve against that identity and must agree with the manifest. Events are the closed set `trial_start|trial_end|span_start|span_end|checkpoint`; `checkpoint` requires a named checkpoint ID.
- Label emission is part of the experiment runner contract. Establish where OpenCode records each submitted marker and verify it after capture. Store emitter/source identity and distinguish manifest-bound markers from unverified observed text; quoted examples and tool-output echoes do not become new trials.
- End markers state observed completion/abort, not task correctness. Independent outcome checks supply quality status. Missing end events mean incomplete coverage, never implicit success.
- Nested spans have unique IDs, valid parent links, and matched boundaries. Repeated event identity is idempotent only when payloads match; conflicting duplicates, reversed intervals, orphan ends, and cross-trial events are validation failures.
- Child sessions inherit trial membership only through a recorded parent/delegation relation or explicit verified binding. Do not infer identity from temporal proximity. Attribute unrelated sessions to exclusions; unexpected children within a selected trial remain visible as contamination or unresolved scope.
- Support historical `[harness_reason:discharge arm=<arm> case=<case>]` first-user-message labels through a legacy adapter. Require an explicit run mapping; mark absent repetition/attempt/span boundaries as unavailable. Do not manufacture independent repetitions from the old ledger.

### Experiment lifecycle

| Step | Required behavior |
|---|---|
| Plan | Create a versioned manifest: hypothesis, cases, baseline/variants, real repetition count, model/provider/settings, task and repository/input digests, budgets, isolation, order seed, outcome checks, metrics, and decision rule. Only intended experimental factors may differ. |
| Dry run | Expand the exact trial matrix, rendered prompts/label lines, execution commands, isolation paths, resource bounds, collection selectors, and expected labels without launching OpenCode. Flag missing prerequisites. |
| Run | On an explicit experiment invocation, launch independent real trials through supported OpenCode execution and existing META HARNESS dispatch/claim controls. Inject markers, record actual runtime identity/settings, checkpoint progress, enforce concurrency/token/time bounds, and support cancellation/resume. |
| Collect | Read real session/message logs, bind labels to the manifest, build trial/span/session membership, retain raw usage and source references, and snapshot evidence consistently. |
| Validate | Compare expected and observed trial sets; reject conflicting/duplicate identities, missing trials, drifted tasks/models/settings, unexpected scope, and fabricated repetitions. Classify incomplete, invalid, excluded, and usable trials with reasons. |
| Compare | Report paired per-case/per-repetition results, independent N, quality outcomes, tokens/cache/cost, latency, errors/retries, and variability. Evaluate a predeclared decision rule only when its quality and comparability requirements hold; otherwise return inconclusive with the missing evidence. |
| Replay | Recompute from saved snapshots/manifests without new model calls; semantic results and digests remain stable. Replay never increases independent N. |

The runner is an **explicitly effectful operation**, separate from read-only inspection: trial execution can invoke tools and consume tokens. It must not receive the inspection operations' blanket read passthrough. Use existing authorization, protected paths, resource claims, and isolation rules; never create a second scheduler or bypass gates. If safe OpenCode launch or budget enforcement is unavailable, retain plan/collect/compare functionality and return a named unavailable result for run.

Additional experiment rules:

- Counterbalance or randomize execution order using a recorded seed. Separate warm-up/cache conditions, incomplete attempts, and independent trials. A retried attempt receives a new attempt identity; the manifest fixes which attempt-selection rule applies.
- Record both task cost and experiment/inspection overhead. Label instrumentation itself has cost and must be identical across comparable arms or reported as a confounder.
- Paired comparisons bind to task/input digests and quality checks, not just matching label strings. A cheaper failed task cannot win a quality-preserving optimization experiment.
- Report all attempted trials and exclusion reasons. Do not cherry-pick successful/cheap attempts or infer statistical significance from a small pilot. New experiments may supply evidence for a separate future Harness Reason reopening; this project cannot change its closed promotion decision automatically.

## Proposed architecture and Tier-2 surface

One Python implementation owns source adapters, normalized evidence, queries, attribution, labels, and experiment evaluation. Suggested home: `scripts/session_inspect/`, finalized during design. A local snapshot/query index is derived and rebuildable; source logs and immutable snapshots remain the evidence. No `src/agentx/` dependency or second runtime is needed.

The proposed registered surface is **`omt_session`** in `.opencode/plugins/omt_session.ts`, a thin proxy with an explicit operation enum and per-operation argv whitelist. A toolbox entry provides on-demand detailed schemas/examples and calls the same core.

| Operation | Responsibility |
|---|---|
| `sessions` | Discover/filter sessions and their hierarchy. |
| `capture` | Snapshot explicitly selected logs, or refresh a previous capture. Writes only requested artifacts. |
| `query` | Search, filter, group, and aggregate normalized records with typed query documents and bounded execution. |
| `inspect` | Retrieve an exact session/message/part/call or labeled trial/span, including selected full content. |
| `trace` | Reconstruct a timeline or traverse recorded causal/parent links. |
| `profile` | Compute usage breakdowns and evidence-backed diagnostic findings. |
| `compare` | Compare selected sessions/spans or validated experiment trials. |
| `experiment` | Closed suboperations `plan|dry_run|run|collect|validate|replay`, with effect classification per suboperation. |
| `export` | Write a selected evidence/report bundle to an explicitly allowed destination. |

All names and schemas here are proposals, not registered tools. Use a compact request schema plus on-demand operation contracts; validation occurs before database access or command dispatch. No arbitrary SQL or shell fragments in query documents. Bound query time, selected rows, content pages, and nesting; explicit limits/cursors preserve completeness information.

Default machine-readable summary budget: **≤2 KiB UTF-8** with counts, coverage, metric definitions, findings, and a digest-bound `detail_ref`. Full evidence is accessible by typed selection and cursor; overflow is never silently truncated. A cursor binds to its snapshot and query; stale cursors fail explicitly. Human-readable reports are derived views of the same result.

Tier-2 integration requires an intentional budget plan: the current compiler check reports only **39 bytes** of `tool_args` headroom. Measure the new schema/IR/nav cost, perform a reviewed description/schema reduction or explicitly justified cap change, register the `.omt` tool declaration, build generated surfaces, and pin description/argv parity. Read operations pass through enforcement; artifact writes and experiment execution follow their appropriate existing checks. Verify the distinction end to end.

## Alternatives and recommendation

| Option | Scope and tradeoff |
|---|---|
| **A — Dedicated Tier-2 inspector with labeled experiments (recommended)** | Build the focused `omt_session` capability above, reuse capture contracts, and deliver both inspection and experimental workflows. Meets the requested power and integration target with a separate acceptance case. |
| B — Toolbox-only inspector first | Same data/query/experiment core with on-demand access; useful as a staged prototype when budgets prevent registration. Tier-2 completion remains pending; this is not a substitute for the requested final delivery. |
| C — Reopen and expand the general reasoning engine | Requires new evidence and a separate reopening decision for `harness_reason`; larger semantic scope and cost. Unnecessary for source-backed session investigation and labeled trial measurement. |

The requested capability and Tier-2 destination are fixed requirements. Option A is the proposed implementation route; no alternative has been executed by creating this project.

## Implementation plan for approval

Plan one new `major_feature`, working name **`opencode_session_inspection_and_experiments`**, linked to `meta_harness_13`. Allocate its numeric ID mechanically at implementation start; none is reserved here. A design document and TDD apply before Programming. Milestones below are work slices of this feature, not invented feature IDs.

| Milestone | Deliverable | Exit evidence |
|---|---|---|
| M1 — Contracts and real-log inventory | Approved normalized schema, capability/version discovery, token semantics, query contract, label schema, trial manifest, failure vocabulary, and permitted source fixtures. | A real captured session and a legacy labeled capture mapped field by field; ambiguities recorded before coding assumptions. |
| M2 — Capture and deep inspection | Read-only adapters, immutable snapshots, hierarchy, typed queries, full-content drill-down, causal trace, pagination, and incremental refresh. | Deterministic replay, source immutability, late updates/idempotence, unsupported-schema and large-output coverage checks. |
| M3 — Usage and diagnosis | Reconciled raw/derived metrics, subtree/span accounting, usage hotspots, loop/failure witnesses, session comparison, and bounded exports. | Hand-audited real examples plus adversarial duplicate/missing/overlapping counter cases; exact versus unavailable attribution verified. |
| M4 — Labeled experiment lifecycle | Manifest and label emit/parse/bind, dry run, guarded real execution, checkpoint/resume, validation, quality-aware comparison, and replay. | At least two variants × two cases × three independently captured repetitions (12 trials); nested spans/child session coverage and negative label tests. |
| M5 — Full Tier-2 integration | Thin plugin, `.omt` registration, shared-core toolbox discovery, compact schemas, compiler build, and effect-specific enforcement. | Budget checks green, fresh boundary receipt, argv/description parity, read/write/run boundaries exercised, no authority minted by reports. |
| M6 — Real-session acceptance and release | Reproduce user investigations and the pilot experiment through the registered tool; document source compatibility, limits, and resume instructions. | Acceptance matrix below, regression results, overhead measurement, and one complete auditable report bundle. |

M1–M3 may use a local CLI while the Tier-2 surface is prepared; completion requires M4 **and** M5. Do not defer labeled experiments to an optional later project. Retain original Harness Reason fixtures/reports unchanged and test any extracted shared behavior against them.

## Scope & success criteria

| ID | Required acceptance |
|---|---|
| AC1 | Inspect at least three distinct real session shapes: ordinary development, a failure/retry sequence, and parent/child work. Every normalized record retains its source identity; coverage gaps are explicit. |
| AC2 | Starting with a summary, locate a costly or failing message, retrieve its full selected tool/reasoning parts, and traverse its surrounding trace. Missing reasoning remains unavailable; no inference is presented as recorded text. |
| AC3 | Typed text/field search and grouped usage queries work across sessions, survive pagination without missing/duplicate records, and return named resource-limit failures. Benchmark on a disclosed ≥100,000-record corpus; report cold/warm latency and memory separately from real-session acceptance. |
| AC4 | Reconcile message/session usage when supported; avoid reasoning/cache/cumulative/subtree double counting; handle valid zeroes, absent counters, unknown inclusion semantics, and overlapping spans correctly. |
| AC5 | Re-capture an active session with a late-updated message: stable IDs, no duplicate usage, versioned snapshot digest, explicit incomplete coverage, and source DB unchanged. |
| AC6 | A planned 12-trial pilot produces 12 independent real captures with manifest-bound message labels, controlled tasks/settings/order, quality results, and per-trial metrics. Replays do not increase N; all attempted/failed/excluded trials remain visible. |
| AC7 | Negative experiment cases detect duplicate/conflicting labels, missing/aborted trials, wrong variants/repetitions, contamination, drifted inputs/models, orphan/reversed spans, spoofed echoes, and resumed attempts. Each invalid trial is excluded from the primary comparison with a reason. |
| AC8 | A real nested-span/child-session trial demonstrates supported attribution and explicitly unavailable fine-grained usage. Legacy feature-130 labels import without inventing repetitions or correcting history silently. |
| AC9 | A saved snapshot/manifest replays without model calls and reproduces semantic report digests; source references remain navigable. Capture timestamps/run IDs are provenance, not accidental nondeterminism in metric results. |
| AC10 | A Tier-2 call works in OpenCode with registration/build/budgets/e2e checks green. Read-only inspection requires no feature phase; artifact writes respect destination rules; experiment execution cannot bypass normal authority/isolation controls. |
| AC11 | Default responses meet the 2 KiB cap with usable detail references; large histories/tool output remain retrievable. Profiling and experiment instrumentation overhead is measured and disclosed separately from trial cost. |
| AC12 | Quality-aware comparison returns a supported conclusion or an explicit inconclusive result. No token-saving promise, promotion decision, or automatic harness change follows merely from collecting logs. |

Out of scope for this project: reconstructing unrecorded reasoning; a general theorem/proof engine; automatic policy or source-code changes from diagnoses; a new scheduler; a mandatory GUI; remote log services. The query/core contract can support a future UI without making it a prerequisite for the agent's inspection power.

## Status

- [x] Project home and lifecycle record created as `meta_harness_13`.
- [x] Reviewed Harness Reason capture evidence, its closed promotion outcome, project workflow, and current toolbox discovery/budget results.
- [x] Defined deep inspection and labeled experiments as joint core requirements, with concrete contracts, alternatives, implementation milestones, and acceptance criteria.
- [ ] Implementation route/plan approved.
- [ ] First feature allocated and linked; design/TDD implementation begins.
- [ ] Real-session/experiment acceptance, Tier-2 integration, and release complete.

## Decisions log

- **D1 — Powerful inspection and labeled experiments are core:** the user's two refinements are delivery requirements; a totals-only report or label-parser-only milestone is insufficient.
- **D2 — Full Tier-2 destination:** integration includes compiler, registry, budgets, and tested enforcement; toolbox tier filtering alone does not satisfy it.
- **D3 — Source-backed truth:** preserve raw counters, stored reasoning availability, exact references, independent trial counts, and named unknowns. Never convert proxies or replays into measurements.
- **D4 — Separate inspection from execution:** read-only log access is the default; explicitly invoked experiment runs retain the existing execution authority and isolation rules.
- **D5 — Preserve lineage:** reuse features 129/130 capture lessons; keep Harness Reason's negative result and closed general promotion decision intact.
- **D6 — Creation scope:** this session creates the project proposal. Implementation, new real trials, and Tier-2 registration await the project's implementation decision.

## References

- Project workflow: [meta_harness_project.md](../../../.workflows/meta_harness/loops/meta_harness_project.md), especially steps 3–7 (create → propose/refine → implementation approval → execute).
- Prior project and closure: [harness_reason/PROJECT.md](../harness_reason/PROJECT.md) and [CURRENT_STATE.md](../harness_reason/CURRENT_STATE.md), 2026-09-26 closure and feature-130 entries.
- Integration tiers and single-core rule: [category_theory_meta_harness.md §7](../../../.sandbox/category_theory_meta_harness.md).
- Real usage/span contract: [stage_real_tokens_design.md](../../../.sandbox/harness_reason/stage_real_tokens_design.md).
- Legacy label/capture design: [discharge_design.md](../../../.sandbox/harness_reason/discharge_design.md). Its timestamp formula is superseded by the verified millisecond correction in the test report below.
- Verified legacy capture behavior and measurement limits: [feature_130 test report](../../../.meta/software_development_process/6.testing/features/feature_130.real_token_discharge/test_report.md).
- Toolbox integration precedent: [meta_harness_12/PROJECT.md](../meta_harness_12/PROJECT.md).
- Harness source of rules: [.meta/META_HARNESS.omt](../../../.meta/META_HARNESS.omt); query through `omt_nav`.
