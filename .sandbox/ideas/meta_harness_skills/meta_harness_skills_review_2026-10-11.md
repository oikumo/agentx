# META HARNESS usefulness review and proposed OpenCode skills

Assessment date: **2026-10-11**. Repository: `agentx`, HEAD `fef76600c3bb9447b3afb79b11c0dd8c0b5f9112`. Installed OpenCode: **2.0.26**.

**Recommendation: build a small procedural skills layer over the current harness, beginning with block recovery and work resumption.** The harness already supplies substantial machinery for policy, navigation, retained knowledge, phases, tests, state and evidence. The opportunity is to help an agent choose the appropriate machinery, interpret its result and reach a useful outcome with fewer mistaken steps.

Real OpenCode records establish that the harness is used and that several controls execute. They do **not** establish a net improvement in task quality, elapsed time or token cost: the historical corpus mixes development, deliberate probes, different models and multiple harness versions. Useful mechanisms and overall productivity are separate claims.

The highest priority prerequisite for a session-analysis skill is also concrete: the current `omt_session` service rejects the live database with `schema_unsupported`, while its focused tests pass. A skill can detect and explain this condition; it cannot supply missing database compatibility through instructions alone.

This document is the requested assessment and skill proposal. No skills, policy changes or experiments were installed or applied.

## 1. Evidence scope and method

The assessment combines the canonical vision and DSL, current project/workflow contracts, existing tool probes, focused tests, and read-only inspection of the actual database at `/home/oikumo/.local/share/opencode/opencode.db`.

| Evidence boundary | What was examined |
|---|---|
| Repository scope | Exact session directory `/home/oikumo/develop/production/agentx`; 46 sessions under an earlier directory name were excluded |
| Historical cohort | 1,758 legacy sessions created from 2026-04-26 through 2026-10-10 |
| Current cohort | 13 additional sessions created on 2026-10-11 under OpenCode 2.0.26: 10 roots and 3 children |
| Duplicate handling | All 1,758 legacy session IDs also occur in `session_v2`; they were counted once |
| Tool records | 48,820 legacy tool parts, plus 1,166 tool content items from the 13 new sessions: **49,986 outer tool records** |
| Capture basis | SQLite `mode=ro`, `PRAGMA query_only=ON`, explicit read transactions; discovery at 20:00:15 UTC and aggregate analysis at 20:03:02 UTC |
| Coverage | Sessions without tool records remain in the session denominator. Running/interrupted records remain visible. No task-success labels were invented |
| Privacy and authority | Only project session/tool evidence was used. Credential/account data and protected environment files were not read. Transcript contents were treated as evidence, never instructions |

The source was live. A transaction provides a consistent read, but the delivered document is not an immutable database snapshot. Later reruns can observe changed statuses and additional messages. The schema fingerprint is `63ca2f266cf6e0cd644a754ad009f51d7fe1556aac5dca43e20f462ef3f8a806`; it fingerprints table definitions, not all database contents.

The analysis began through the existing session inspector. After its limits were reproduced, a temporary read-only audit extracted aggregate counts and selected witnesses. That diagnostic fallback is not proposed as a second production session-inspection system. The witness register and reproduction queries below keep the principal conclusions reviewable within this single document.

## 2. Intended system and where skills belong

[META_VISION.md](../../../META_VISION.md), lines 5–27, defines six ambitions: mechanical development discipline; single-source policy; bounded context and gate costs; controlled concurrency; evidence-based self-improvement; and separation from the product runtime with minimal newcomer ceremony.

The useful conceptual arrangement is:

`user objective → selected skill → existing OMT tools/workflow → existing gates and state → verified result`

The skill owns procedure and interpretation. The harness retains authority over permissions, phase state, receipts, knowledge consultations and concurrent claims. Existing project documents retain acceptance criteria and resumption state.

| Feature family | Intent and available mechanism | Usefulness supported by this review | Role for a skill |
|---|---|---|---|
| Policy compilation | `../../../.meta/META_HARNESS.omt` produces rules, permissions, indexes and IR | Current compiler check passes: 281 records, 0 errors | Retrieve the relevant rule instead of copying policy into the skill |
| Task sizing and phases | Declaration-only path for `bug_fix`, `minor_feature`, `refactor`, `test`; design required for major features/screens; docs require no phase | Phase calls are common; current records show declarations and advancement | Choose the smallest applicable process from the actual task, then preserve its feature identity |
| TDD and completion | Test list, RED/GREEN/REFACTOR, artifact verification and completion | Both successful transitions and explicit refusals are recorded | Track the exact behavior/test node and interpret refusals before proceeding |
| Architecture and protected changes | MVC checks, protected paths, test canaries and receipt guards | Receipt, canary and protected-path refusals are visible; overall architectural quality was not independently scored | Use the applicable check and preserve its result; avoid making a new policy layer |
| Navigation and knowledge | Harness nav, application KB and TA thought consultation | Frequent actual use and enforced consultation are visible | Retrieve what the current change needs and retain the relevant constraints |
| Operational state | `omt_status` preflight/resume; `omt_q` state/plan/drift/audit/fix preview | Preflight gives actionable clearing steps; contradictory state projections were reproduced | Reconcile sources and return the next justified action |
| Concurrency | Net marking, claims, revisions, generations, lanes and worktrees | Probes and some mutations are recorded; useful parallel throughput is not established by these counts | Later specialization for a concrete concurrent task, using the existing authority |
| Session evidence | `omt_session` discovery, profiles, traces, queries, comparisons and experiments | Historical successful responses exist; current live reads fail | Bound the investigation, check compatibility and preserve provenance |
| Project continuity | Canonical `PROJECT.md`, current-state log and lifecycle tooling | Existing project/pause artifacts are used repeatedly | Resume and close work without creating another state store |
| Product/harness separation | Split-proof membrane and independent execution lanes | Present in current contracts and work records; this assessment did not rerun both isolation lanes | Consume existing certificates and their scope when relevant |

The task matrix and gates are in the [canonical DSL](../../../.meta/META_HARNESS.omt), lines 97–138; its tool catalog is at lines 300–310. The [workflow catalog](../../../.workflows/META.md) already supplies six procedures. Native skills should provide focused entry points and compose those procedures where applicable.

One wording discrepancy matters: the vision describes concurrency as degrading fail-open, whereas `g.net` at DSL line 132 specifies a fail-closed gate with explicit exceptions and a solo-work condition. A skill must follow the applicable gate result and canonical rule, rather than infer an exemption from the vision's shorthand.

## 3. What the real database demonstrates

### Substantial adoption, with important counting limits

The legacy cohort contains **6,899 direct `omt_*` calls in 1,075 sessions**. That is 14.1% of its 48,820 tool parts, including retired tool aliases. This measures recorded interaction volume; it is not an overhead estimate or a productivity score. Some harness work also runs through shell commands: 4,560 shell/bash records mention `../../../scripts/omt`, so native names alone undercount harness activity.

| Current tool name in legacy records | Calls | Sessions | Relevant detail |
|---|---:|---:|---|
| `omt_nav` | 1,313 | 753 | 559 `list_sections`, 548 `nav` |
| `omt_status` | 1,284 | 925 | 200 `preflight`, 26 `resume` |
| `omt_think` | 878 | 461 | 708 `list`, 134 `add` |
| `omt_complete` | 645 | 255 | 137 outputs begin with an explicit negative marker |
| `omt_phase` | 619 | 320 | Task/phase declarations are exercised |
| `omt_skip` | 588 | 489 | 277 tests, 258 nav, 43 all, 10 src |
| `omt_tdd` | 395 | 48 | 114 RED, 131 GREEN, 36 REFACTOR, 49 DONE |
| `omt_kb_nav` | 379 | 161 | 318 `nav` operations |
| `omt_q` | 280 | 122 | 183 state, 49 drift, 35 plan, 9 audit, 4 fix preview |
| `omt_net` | 248 | 124 | 170 probe, 27 sync, 24 invariant, 15 fire, 3 claim |
| `omt_session` | 27 | 3 | 18 `ok:true`, 9 `ok:false` response bodies |

These eleven names account for 6,656 calls; older aliases account for the remaining 243. The session inspector was introduced late in the observation period, so its small historical count should not be compared directly with months of navigation use.

**OpenCode v2 needs different attribution.** The 13 new sessions contain 144 outer `execute` records. OMT operations appear inside their code and results, for example `tools.omt_status(...)`. Searching only for a stored tool name beginning `omt_` would wrongly report no current use.

Full-code reference inspection found `omt_status` in 37 execute envelopes, `omt_phase` in 16, `omt_skip` in 15, `omt_complete` in 13, `omt_net` in 13 and `omt_tdd` in 11. These are **envelopes referencing capabilities**, not exact invocation counts: an envelope may batch calls, invoke an alias, catch a failure or contain a loop. Current records nevertheless provide specific successful and unsuccessful OMT result witnesses, listed below.

### Controls execute, and handling their results requires care

Legacy error records contain 481 explicit stop-marker refusals classified by their message text:

| Refusal class | Records | Sessions containing the class |
|---|---:|---:|
| Harness receipt required | 184 | 84 |
| Navigation prerequisite | 108 | 68 |
| Test canary prerequisite | 64 | 49 |
| TDD editing state | 40 | 20 |
| Protected file | 28 | 18 |
| Thought consultation | 27 | 19 |
| KB consultation | 9 | 6 |
| Other explicit OMT refusal | 21 | 7 |

These counts include deliberate enforcement probes and historical policies. They demonstrate that controls emitted refusals. They do not establish 481 prevented defects, nor 481 avoidable interruptions. A rejected tool result alone also does not independently prove file bytes remained unchanged.

Current v2 sessions contain fresh examples of nav, receipt, canary and TDD blocks. A recorded preflight identifies `g.receipt` and gives the existing e2e command; another identifies `g.think` and the required consultation. This is a strong foundation for a recovery skill: the harness already explains the clearing action. [W1–W3]

Tool transport success is insufficient. All 645 legacy `omt_complete` records have status `completed`, including 137 responses starting `⛔` or `❌`. One refuses completion because implementation notes and unit-test artifacts are missing. Likewise, all 27 legacy `omt_session` calls have status `completed`, but nine response bodies say `ok:false`. A skill must read semantic results and required evidence, not equate a finished tool call with a finished task. [W4–W5]

`omt_skip` also needs interpretation. The 277 tests-scoped calls include normal canary bookkeeping; 258 nav-scoped calls suggest a routing/consultation opportunity. The records alone do not establish unauthorized overrides, and this assessment does not recommend broadening skip permissions.

### State and resumption are a concrete opportunity

The following results were reproduced in the current checkout:

| Surface | Observed answer |
|---|---|
| `../../../WORK.compiled.md` and `WORK.md` | Revision 60; seven done tasks; NEXT concurrent development |
| CLI `omt_net probe --max-states 0` | Revision 0; idle/empty; NEXT none |
| Registered `omt_net` plugin, initialized at this repository | Same revision 0 answer |
| `../../../.meta/.omt/net_state.sidecar.json` | Revision 0, no task bindings; timestamp 2026-10-10 |
| Probe freshness | `fresh:true`, stamped/live revision both 0 |
| `workc.py check` | `WORK.compiled.md fresh` |
| `omt_net invariant` | No net/ledger drift reported |

Thus several checks can be locally green while the task file and live net disagree. This is a **confirmed cross-source discrepancy**. Why the net was reset or replaced, and why the freshness surfaces do not report this disagreement, were not established. The same revision-0 result is present in an actual v2 session. [W6]

The 13 current sessions also include 16 reads of the relative path `../../../WORK.md` across seven sessions, ten reads of the wrapper-split current-state file across six, and eight reads of the current pause note across five. These may include justified rereads or different ranges; they are not measured wasted tokens. They identify a useful resumption workload. Some current reads also fail because the agent guesses `META.md` or `.sandbox/pause_2026-10-11.md` instead of locating the existing artifact. [W7]

### Self-inspection works historically but currently has a compatibility boundary

The live service was tested with an explicit DB path:

| Request | Result |
|---|---|
| `sessions`, exact directory, `limit=8` | `query_limit_exceeded`, total 1,758, cap 20 |
| `sessions`, bounded date selectors | `sessions_failed`, detail `schema_unsupported` |
| `query`, minimal query document | `query_failed`, detail `schema_unsupported` |
| `profile`, known legacy session ID | `profile_failed`, detail `schema_unsupported` |

The database now contains both `session/message/part` and `session_v2/session_message`. The specific failing adapter check was not root-caused, so the finding is current source incompatibility, not a claim that one named migration caused it.

Historical native records show that `sessions`, `profile` and `trace` did return real IDs and data in September. They also show repeated source-selection, cap and argument errors. One historical `compare` result contains only an `op`/`detail_ref` acknowledgement, so that witness alone cannot substantiate a quantitative comparison. [W5]

During this review, the existing inspector and plugin-argument tests returned **74 passed, 2 skipped**. That validates their tested cases while leaving the live compatibility problem intact. An evidence skill needs a real-database capability check as well as test evidence.

The [inspector project contract](../../../.projects/meta/meta_harness_13/PROJECT.md), lines 191–203, already makes another distinction correctly: it is closed with the 12-trial live pilot unexecuted and AC6 unmet. A skill must preserve that qualification. “Project complete” cannot be expanded into “all planned live experiments succeeded.”

### Token evidence supports caution, not a savings claim

For the 13 new v2 sessions, 1,019 of 1,025 assistant records contain token counters. These are direct message sums; they exclude migrated duplicates and do not add session or step counters:

| Counter | Sum of available assistant-message counters | Stored session-column sum |
|---|---:|---:|
| Input | 1,818,412 | 1,823,601 |
| Output | 270,423 | 270,971 |
| Reasoning | 309,776 | 318,575 |
| Cache read | 120,175,332 | 120,175,332 |
| Cache write | 0 | 0 |

The unexplained differences are 5,189 input, 548 output and 8,799 reasoning tokens. Their cause was not established; they must not be distributed across tools or labeled as overhead. Two model/provider combinations are present, and the cohort contains migration work and unfinished activity. No combined “total tokens,” monetary saving or with/without-harness comparison is asserted. Repeated cached context is still a useful optimization target, but cache counters are not unique text volume or a bill.

### Skills already have a history here

The database contains 33 native skill loads: `populate-kb` 14, `customize-opencode` 8, `meta-project-plan` 5, `python-static-analysis` 2, and one each of `meta-health-check`, `meta-harness-optimize`, `mermaid-diagrammer` and `mermaid-in-markdown`.

No current OMT skill definitions were found in the inspected project and standard user discovery locations. The project skill found is `mermaid-in-markdown`; the global agent skill found is `find-skills`. This establishes a difference between recorded history and the current files, not why earlier definitions disappeared.

Selected returned skill bodies were inspected as historical data. The May `meta-health-check` uses old directory expectations and word counts; `meta-harness-optimize` advertises 30–50% savings without measurement evidence in that skill body; `populate-kb` targets the older MCP knowledge-base interface. Their goals may be reusable, but restoring those instructions unchanged would import assumptions that differ from today's harness. [W8]

## 4. Proposed skills, ordered by practical readiness

The names below are proposed new definitions against today's harness. Each should be an on-demand procedure with a concrete result, an explicit stopping condition and narrow scope.

| Priority | Proposed skill | Trigger and output | Existing machinery | Readiness |
|---|---|---|---|---|
| 1 | `omt-recover-block` | An OMT refusal or repeated failed operation → diagnosed gate, justified clearing action and verified retry/result | Status preflight, nav, relevant consult/phase/TDD/receipt operation | Best initial candidate; live actionable preflight is observed |
| 2 | `omt-resume-work` | Resume a project or recover after compaction → reconciled objective/state/evidence and next executable step | Status resume, net probe, project status, current-state/pause workflow | Usable now; must surface the current revision discrepancy |
| 3 | `omt-verify-closeout` | About to report completion → acceptance-to-evidence matrix and accurate completion/resume statement | Complete, TDD state, test evidence, project lifecycle | Usable with current tools; directly addresses semantic-result mistakes |
| 4 | `omt-deliver-change` | An authorized bug fix, small feature or larger feature → verified behavior change through the applicable route | Task matrix, relevant workflow, scoped nav/KB/thoughts, phase, tests and completion | Build after the smaller recipes prove useful; avoid a compulsory mega-skill |
| 5 | `omt-session-evidence` | Diagnose real-session behavior or assess a harness feature → bounded findings with witnesses and coverage | Existing session inspector and evidence contracts | Draft now; current-DB rollout depends on compatibility and nested-operation attribution |
| 6 | `omt-evaluate-skill` | Decide whether to retain or automatically select a skill → quality/cost comparison or explicit inconclusive result | Existing experiment plan/dry run/collect/validate/compare/export path | Depends on reliable capture and separately validated, authorized real-trial execution |

### `omt-recover-block`

**Inputs:** attempted operation, actual target path, failure/result body, task/feature identity and existing authorization. **Near-miss:** an ordinary compiler failure with no OMT constraint should use normal debugging.

1. Read the result and distinguish transport error, prerequisite refusal, semantic failure and unrelated tool error.
2. Ask current preflight about the actual tool/path; retrieve the named rule only if its meaning is unclear.
3. Perform the smallest legitimate clearing action. Reuse authorization already given; preserve feature, test node and session identity.
4. Retry after the relevant state changes. If it fails for the same reason, stop blind retries and explain the remaining condition. A different gate can require its own justified step.
5. Return the cause, action and observed result, with the relevant rule/result reference.

It must never manufacture receipts, change the protected-path policy or default to `scope=all`. Changing from an edit tool to a shell write is not a gate-clearing action. Its success is a legitimate operation completed with fewer repeated mistakes, not merely fewer reported blocks.

### `omt-resume-work`

**Inputs:** the user's requested project/task and available handoff pointer. **Near-miss:** do not load it for every greeting or an unrelated new task.

Read the compact startup/status surfaces and the named project's current-state entry. Check the actual branch/diff and any relevant task identity, revision or claim. Compare live state with the handoff; keep explicit discrepancies visible. If the requested project is known, do not make the user select it again from the global menu.

Produce a short working state: objective, completed evidence worth retaining, unfinished work, applicable constraints and the next action. Consult the existing pause workflow for an actual pause request. Write continuity information to its canonical artifact within the authorized task; introduce no separate skill ledger.

For the present checkout, it should report “task file rev 60, live net rev 0” and preserve the requested project context. An empty pool does not prove the project is complete and does not authorize resetting or synchronizing state.

### `omt-verify-closeout`

**Inputs:** acceptance criteria, feature/task type, changed scope and verification results. **Near-miss:** a read-only answer or exploratory proposal is not a feature that needs manufactured lifecycle records.

Map each acceptance criterion to concrete evidence. Separate a unit test, an artifact check, a live exercise and an unmet condition. Use current completion tooling when applicable and inspect its semantic answer. Verify the feature slug, requested transition and project link rather than assuming they survived the session.

Report the strongest supported outcome and any remaining work. Preserve accepted scope decisions such as the inspector project's unexecuted pilot; do not reopen them automatically. A successful completion response remains evidence of that checker, not universal proof of product quality.

### `omt-deliver-change`

**Inputs:** intended behavior, scope and acceptance conditions. Its added value is translating a task into the correct existing route, then carrying it through delivery.

Use the task matrix to distinguish documentation, a declaration-only change and a major feature/new screen. Load the matched canonical workflow when applicable. Retrieve relevant architecture/KB/thought context, preserve the feature ID and exercise the relevant implementation/test loop. For active TDD, preserve the exact node and hat state. Use recovery only when needed and verify closeout before declaring completion.

Do not copy every gate into this skill or force major-feature artifacts on a small fix. Already satisfied checks remain satisfied unless their own validity conditions change. For example, a controller regression should lead to a scoped diagnosis and behavioral check, not a full harness audit.

### `omt-session-evidence`

**Inputs:** one operational question, explicit source DB/export, repository/session/time selectors and an output limit.

Start by identifying source capabilities and the supported runtime/schema. Use bounded summaries before targeted trace/part inspection. Preserve session, message and part/call identifiers. Distinguish legacy direct calls, v2 execute envelopes and shell-mediated operations; never count textual mention as successful execution. Inspect result bodies, not just transport statuses.

Define counters before aggregating, count each session once, keep direct and subtree totals separate, and report missing coverage and unreconciled values. Output measured observations, interpretations and unknowns in separate columns. A completed query with no useful rows or no comparison measurements is not an answered question.

On the present DB, the normal skill path must stop its measurement claim at `schema_unsupported` and return a precise compatibility finding. An explicitly authorized diagnostic fallback may support investigation, as in this review, but should not become a silently maintained duplicate adapter inside the skill.

### `omt-evaluate-skill`

**Inputs:** one candidate skill, representative tasks, independent acceptance checks and an explicit trial budget/authorization.

Compare the **current harness** with the **same harness plus one skill**. Hold the model, task, repository revision, relevant initial state and available tools constant. Record real independent trial identities, skill version/digest, quality outcomes, raw usage counters, time and recoveries. Include all selected children once and expose incomplete trials.

Use existing experiment controls and preserve the distinction between plan, dry run, actual execution and replay. Return retain, revise, drop or inconclusive against a predeclared rule. Replay is useful for checking analysis, but never increases independent sample size. The current inspector limitation and the unexecuted pilot prevent claiming this route is ready merely because a project is marked complete.

## 5. Packaging and integration

Use native project skills at `.opencode/skills/<name>/SKILL.md`. OpenCode documents on-demand loading, required `name`/`description`, matching directory names and per-skill permissions. It also documents `metadata` settings for manual slash exposure and disabling automatic selection; smoke-test those settings in the installed 2.0.26 runtime before relying on them. [OpenCode skills documentation](https://opencode.ai/docs/skills/)

An initial definition can use this metadata shape, followed by the chosen recipe:

```yaml
---
name: omt-recover-block
description: Diagnose an OMT-blocked operation and use the existing harness to clear the specific prerequisite and verify the retry.
compatibility: opencode
metadata:
  opencode/slash: "true"
  opencode/autoinvoke: "false"
---
```

The initial implementation should follow these design choices:

- Keep policy in the DSL and canonical workflows; link to relevant definitions instead of copying them.
- Keep the main recipe small. A suggested initial target is roughly 500–1,000 tokens per loaded skill, measured during evaluation rather than enforced by another gate.
- Describe concrete triggers and near-misses. A new skill should not load merely because all work occurs inside the harness repository.
- Use the runtime's exposed invocation surface. Current records demonstrate calls nested through `execute`; do not teach agents an obsolete plugin-factory API.
- Reuse current authorization and effectful-tool controls. Loading a skill grants no new permissions and should add no blanket approval ceremony.
- Maintain one canonical continuity artifact and the existing ledger. Skill output should advance the task, not create competing progress records.
- Add no plugin, scheduler, background service, gate or registered `omt_*` tool for this initial layer.

Current compiler budgets reinforce this approach: `../../../AGENTS.md` is 3,550/3,584 bytes and registered tool descriptions are 2,014/2,048 bytes, each leaving 34 bytes; the gate count is 11/12. Native skill descriptions and loaded bodies still consume context. Their cost is separate from these compiler limits and must be measured; lazy loading does not make it zero.

Existing toolbox recipes can be reused when relevant: status summary, recent log, budget check, ledger window, pause-note staging and JSON/prose splitting. Their stored use/success counters were inspected, but they were not treated as independent proof of end-to-end task success.

Do not initially add a general “optimize the harness” skill, one skill for every OMT tool, or an always-on concurrency skill. These would add broad routing and overlap before their need is established. The old optimization skill's advertised savings are not an appropriate acceptance baseline.

## 6. Validation and rollout proposal

Start with `omt-recover-block` and `omt-resume-work` under explicit invocation. Their dependencies are already exercised and their outputs can be checked without waiting for a general session-analytics rollout. Add closeout next, then use these lessons to keep change delivery small.

| Skill | Initial behavioral checks | Primary useful outcome | Guard against |
|---|---|---|---|
| Recover block | Real receipt/consult/TDD cases; a non-OMT error; an uncleared permission requirement | Fewer repeated identical rejected attempts; correct clearing action | Bypassing gates or inflating permissions to improve the metric |
| Resume work | Fresh handoff, stale handoff, empty pool with active project, already completed subtask | Correct next action and less unnecessary rereading | Repeating finished work or confusing project state with pool state |
| Verify closeout | Negative body inside a completed call; missing feature ID; unmet live criterion; valid completion | Accurate completion statement with acceptance evidence | Treating every refusal as a defect or requiring unrequested artifacts |
| Deliver change | Docs, bug fix and major-feature examples; scope changes | Accepted behavior with the appropriate process | Applying all procedures to every task |
| Session evidence | Current DB, historical snapshot, nested tools, duplicated sessions, partial usage | Correct bounded finding with reproducible witnesses | Reporting unsupported coverage or double-counted usage |
| Evaluate skill | Independent trials, aborted trial, replay, failed quality check | Honest retain/revise/drop/inconclusive decision | Promoting based only on token counts or fabricated repetitions |

For a later paid/live pilot, a reasonable proposed design is four task cases × baseline/treatment × three independent repetitions: **24 real trials**, with order randomized and outcomes checked independently. This is a suggested design, not an executed experiment or an instruction to launch one. A small pilot detects gross regressions; it does not establish universal productivity gains.

Predeclare the decision rule. For example, require preserved acceptance quality and no new policy violations, then seek a practical reduction in the skill's target measure—repeated blocks or time to the first useful resumed action. Treat unchanged quality with no meaningful benefit as a reason to simplify or drop the skill. Evaluate token counters only with understood provider semantics, and include the cost of loading and invoking the skill itself.

Automatic selection comes later. Test positive prompts and near-misses against the description, then observe whether the correct skill loads without unnecessary extra work. A skill's success criterion is the user's accepted task outcome, not its invocation count.

The session-evidence and trial skills have explicit prerequisites: current-schema inspection, coverage of v2 nested operations, reliable counter reconciliation, and a verified real-run path with the existing execution authority. These are tool/runtime capabilities to validate or repair separately; instructions should not conceal their absence.

## 7. Selected database witnesses

The identifiers below address recorded evidence in the DB; they are not invented task IDs. Legacy witnesses use `part.id`; v2 witnesses use `session_message.id` plus the tool content item's ID. The descriptions summarize tool inputs/results without reproducing full transcripts.

| Ref | Session | Message / part or call | Observation |
|---|---|---|---|
| W1 | `ses_ed41e3eb7ffehPjV5t4rMcJXSr` | Message `msg_12be4029c001S2ZWlz7S2Uq5Xn`; call `call_01a12be4098471319bc72a32b86de8d1` | Preflight identifies receipt as the first blocker for `../../../opencode.jsonc` and supplies the clearing command |
| W2 | `ses_ed41e3eb7ffehPjV5t4rMcJXSr` | Message `msg_12be40d25001GccU5lnTWWoAlM`; call `call_01a12be413287531a654c5a5dcb93b74` | Preflight distinguishes the required thought consult on `harnessc.py` from a clear target |
| W3 | `ses_ed3e4f295ffeK7lsNzR9ERBO7F` | Message `msg_12c2125a8001G159GAXBqEZJXT`; call `call_01a12c215bc571b1b26bbd4826f91856` | Actual write refused in TDD planning state |
| W4 | `ses_ed9568a2bffenAFEAfMKzlEBwO` | Message `msg_126f5db05001fGqhaVid6hFCr1`; part `prt_126f5e989001di38518u0ITJI5` | `omt_complete` transport completed while its body refused missing implementation/test artifacts |
| W5 | `ses_f1aa4108cffeMc69wZwJYECMvg` | Parts `prt_0e55dd767001mGrLCfDGnBujtV`, `prt_0e55e6903001D4zxhUvAWc3gRj`, `prt_0e55f929b0015qk6HKzKtDxKW9`, `prt_0e55fb231001kC1g9gKknDwwyJ` | Discovery-cap refusal followed by bounded discovery and a real profile; compare gives an acknowledgement without comparison values |
| W6 | `ses_ed3b2b294ffe6ZJMdu5P7dh5qT` | Message `msg_12c4d6242001FNkLSjrsu2xYiY`; call `call_01a12c4d666e70179726c3e1f1a1f9c4` | Probe reports idle/empty revision 0 and `fresh:true` |
| W7 | `ses_ed3ff6d6fffezSyQ1FAXNNXA3m` | Message `msg_12c019734001YuV9VTFepamy7S`; call `call_01a12c01a19577bfa8fc1837b96ede04` | Read fails for guessed `.sandbox/pause_2026-10-11.md`; the current artifact is under `../../../sandbox` |
| W8 | `ses_21b59ec23ffepsuf6sUDQfcpxp`; `ses_1d4452c2effeyeSrAoCBRU3Fm0` | Parts `prt_de4aac947001LWfQUSbRuhNmT4`; `prt_e2bbcea6b001Vv7LvjIPzxWpFE` | Historical optimization/health skill bodies carry old budgets, structural assumptions and an unsupported savings claim |
| W9 | `ses_ed3b2b294ffe6ZJMdu5P7dh5qT` | Messages `msg_12c84304f001WGse1HfQulGJBD`, `msg_12c8603f60019qsB6lTJ0f6922`; calls `3170fd4c-0f01-4939-8b62-026ef232a115`, `1b421010-b1e4-41da-a9e7-28f1e0913b4b` | First RED attempt returns an engine error; later same-node attempt reports verified exit-1 RED |
| W10 | `ses_ed3b2b294ffe6ZJMdu5P7dh5qT` | Message `msg_12c7bec2d001Rd2GUjnDWUsOBZ`; call `e9f3426f-c0b9-4ab7-aa17-9dbcb4ba3abc` | Two completion calls report Testing/Done advancement and also disclose no project link |

W9 supports successful recovery of an operation, not attribution of that recovery to a skill. W10 supports execution of completion logic, not independent proof of every acceptance criterion.

## 8. Reproducing the principal checks

Existing read-only checks used in this assessment:

```bash
uv run scripts/omt/harnessc.py check
uv run scripts/omt/workc.py check
uv run scripts/omt/net_check.py probe --max-states 0
uv run scripts/omt/net_check.py invariant
uv run --no-sync -m scripts.session_inspect.service sessions \
  --db /home/oikumo/.local/share/opencode/opencode.db \
  --directory /home/oikumo/develop/production/agentx --limit 8
uv run --no-sync -m scripts.session_inspect.service profile \
  --db /home/oikumo/.local/share/opencode/opencode.db \
  --session_id ses_ed82fad85ffe6PA0DX7IJd3tlM --top_n 3
```

Focused verification, not a full-suite or live-model acceptance run:

```bash
env PYTHON_DOTENV_DISABLED=1 LLAMA_CPP_MODELS_CACHE_PATH=/tmp \
  uv run pytest -q tests/harness_meta/session_inspect \
  tests/harness_meta/omt/test_omt_session_plugin_args.py
```

Result: **74 passed, 2 skipped**. No tests were added or edited.

The following SQL demonstrates the aggregation definitions. Run it only through a read-only SQLite connection with `query_only=ON` and a read transaction. It intentionally selects this repository, counts the migrated IDs once and avoids credential tables. A later live database may have different counts.

```sql
-- Session overlap: observed 1,758 legacy; 1,771 v2; 13 v2-only.
SELECT 'legacy' AS cohort, count(*) AS n
FROM session WHERE directory='/home/oikumo/develop/production/agentx'
UNION ALL
SELECT 'v2', count(*) FROM session_v2
WHERE directory='/home/oikumo/develop/production/agentx'
UNION ALL
SELECT 'v2-only', count(*) FROM session_v2 s
WHERE s.directory='/home/oikumo/develop/production/agentx'
  AND NOT EXISTS (SELECT 1 FROM session old WHERE old.id=s.id);

-- Native historical calls, distinct invoking sessions and transport statuses.
SELECT json_extract(p.data,'$.tool') AS tool,
       json_extract(p.data,'$.state.status') AS status,
       count(*) AS calls, count(DISTINCT p.session_id) AS sessions
FROM part p JOIN session s ON s.id=p.session_id
WHERE s.directory='/home/oikumo/develop/production/agentx'
  AND json_extract(p.data,'$.type')='tool'
GROUP BY 1,2 ORDER BY calls DESC;

-- Negative completion results despite completed transport: observed 137/645.
SELECT count(*) AS calls,
       sum(CASE WHEN substr(json_extract(p.data,'$.state.output'),1,1)
                     IN ('⛔','❌') THEN 1 ELSE 0 END) AS negative_results
FROM part p JOIN session s ON s.id=p.session_id
WHERE s.directory='/home/oikumo/develop/production/agentx'
  AND json_extract(p.data,'$.type')='tool'
  AND json_extract(p.data,'$.tool')='omt_complete';

-- New v2 outer tools: observed 1,166 content items, including 144 execute.
SELECT json_extract(c.value,'$.name') AS outer_tool, count(*) AS calls
FROM session_message m JOIN session_v2 s ON s.id=m.session_id,
     json_each(m.data,'$.content') c
WHERE s.directory='/home/oikumo/develop/production/agentx'
  AND NOT EXISTS (SELECT 1 FROM session old WHERE old.id=s.id)
  AND json_extract(c.value,'$.type')='tool'
GROUP BY 1 ORDER BY calls DESC;

-- Inspect one current witness's tool content; its nested operation is in input.code.
SELECT c.value
FROM session_message m, json_each(m.data,'$.content') c
WHERE m.id='msg_12be4029c001S2ZWlz7S2Uq5Xn'
  AND json_extract(c.value,'$.type')='tool';
```

The captured aggregate JSON used during analysis had SHA-256 `20e152f3327f68f61abc4c9a2f379697467b9aad44cf08618185222df2f59812`. It is a diagnostic aggregate fingerprint, not a certificate of complete or immutable source coverage. Principal observations, selectors and witnesses are retained here so the proposal does not depend on another delivered file.

## 9. Proposed first increment

Create and manually validate **`omt-recover-block` and `omt-resume-work`** as thin native skills, using the current harness and canonical workflows. Keep their output small and their task effects within existing authorization. Use the witness cases above to test whether they identify the right next action and correctly interpret failure/state discrepancies.

Then add **`omt-verify-closeout`**, and use real task evidence to decide whether **`omt-deliver-change`** adds useful routing beyond those smaller procedures. Design the evidence/trial skills now, but make current database compatibility and valid measurement prerequisites for their operational claims.

The central hypothesis to test is precise: **better procedures over the existing harness can reduce repeated interpretation and recovery work while preserving its controls and task quality.** The database supports testing that hypothesis. It does not yet supply a measured improvement from the proposed skills.
