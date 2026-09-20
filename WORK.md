# WORK

> Single-developer + coding-agent roadmap. Machine-parseable, minimal friction, git-friendly.

---

## Convention

| Symbol | Meaning |
|--------|---------|
| `[ ]`  | Pending |
| `[~]`  | In progress (agent working on it) |
| `[x]`  | Done |
| `[!]`  | Blocked / needs decision |

**Hierarchy** - top-level task -> optional subtasks (indented 4 spaces).
**Metadata** - optional inline comment: `<!-- id:T-123 prio:medium agent:true -->`
**Thoughts** - separate `---` line then bullet list; tools can strip it.
**DONE entries** - one line + pointer (feature dir / git log); narrative is paid every session startup (CONV_WORK_DONE).
**DONE rotation** - keep pending + last 5 DONE inline; older rotate to `WORK_ARCHIVE.md` (never auto-read) — CONV_WORK_ROTATE; `harnessc check` errors past @var work_done_max.

---

## Tasks
<!-- net_rev:60 -->
NEXT: proj:agentx_concurrent_development (recommended)
Other enabled: none
Blocked: none
Resources: 4/4 free
Pool: pending=0 active=0 done=7 (places 15/15)
Options: proj:agentx_concurrent_development, proj:feature_kb_akb, proj:meta_harness_10, proj:meta_harness_11, proj:meta_harness_2, proj:meta_harness_3, proj:meta_harness_4, proj:meta_harness_5, proj:meta_harness_6, proj:meta_harness_7, proj:meta_harness_8, proj:meta_harness_9, proj:meta_harness_concurrent, proj:net_enforced_harness, proj:petri_net_library, proj:petri_net_studio, proj:project_lifecycle, proj:rag_v2, proj:workflows, drift:aging-draft:feature_kb_akb, drift:aging-draft:workflows, drift:iteration-log:meta_harness_2, drift:iteration-log:meta_harness_3, drift:iteration-log:meta_harness_5, drift:iteration-log:meta_harness_concurrent, drift:iteration-log:net_enforced_harness, drift:unlinked-project-backed:feature_kb_akb, drift:unlinked-project-backed:meta.workflows_definition_layer, unscoped:001, unscoped:002
Lanes: verification 0/1 free 1, integration 0/1 free 1
## Projects (synced by `uv run scripts/omt/project.py sync` — do not hand-edit)

| project | state | features |
|---|---|---|
| agentx_concurrent_development | draft | — |
| feature_kb_akb | draft | — |
| meta_harness_10 | complete | feature_102.mh10_p1_global_projection, feature_103.mh10_p2_global_gate, feature_104.mh10_p2_rewire_claims_through_fire, feature_105.mh10_p2b2_template_fix_work_release, feature_106.mh10_p2b3_lane_integration_rewire, feature_107.mh10_p2b3b_lane_template_landing, feature_108.mh10_p2c_crash_reorder, feature_109.mh10_p2d_matrix_payback |
| meta_harness_11 | active | feature_110.whole_project_menu_composer, feature_111.multi_select_directive_protocol, feature_112.identity_aware_pool, feature_113.live_progress_projection, feature_114.concurrent_dispatch_runtime, feature_115.live_progress_full_push_join_view, feature_116.mh11_o6c_wild_payback_measurement |
| meta_harness_2 | complete | feature_020.meta_harness_navigation, feature_021.meta_harness_think_anywhere, feature_022.meta_harness_think_anywhere_v2, feature_023.meta_harness_improvement, feature_026.omt_q_interrogative_first_ops |
| meta_harness_3 | complete | feature_028.feature_scoped_gating |
| meta_harness_4 | complete | feature_037.tdd_testlist_prose_fallback |
| meta_harness_5 | complete | feature_038.tdd_toolchain_aware |
| meta_harness_6 | complete | feature_051.ledger_test_isolation, feature_052.opencode_version_canary, feature_053.net_gate_concurrency_predicate, feature_054.small_task_fast_path, feature_055.gate_preflight, feature_056.skip_taxonomy_phase_hygiene, feature_057.gate_budget_ceremony_meter, feature_058.thought_review_gotcha_root_cause, feature_059.harness_tiered_template |
| meta_harness_7 | complete | feature_060.dangling_active_only, feature_061.nav_cache_hit, feature_062.preflight_on_declare, feature_063.kb_sticky_per_feature, feature_064.named_work_truthful_observation, feature_066.think_batch_consult |
| meta_harness_8 | complete | feature_065.tdd_sync_stranded_red_closer, feature_067.tdd_same_node_lint, feature_068.schema_audit_autolink, feature_069.nav_answer_caps, feature_070.escape_replay_fold, feature_071.delegate_advisory_fold, feature_072.typed_policy_semantics, feature_073.task_prep_op_slice, feature_074.receipt_batch_mode, feature_075.completion_hardening_content_bound_evidence, feature_076.workflow_index_and_repair_quickfix, feature_077.as_of_historical_temporal_replay, feature_078.op_graph_transitive_risk, feature_079.net_transaction_authority, feature_080.task_claim_generation, feature_081.worktree_execution_isolation, feature_082.two_worker_capacity_scope_arbitration, feature_083.verification_integration_lane, feature_084.recovery_and_transaction_journal, feature_085.evidence_dependency_completion, feature_086.ordered_skip_audit_plus_bootstrap_fingerprint, feature_087.skip_scope_alignment, feature_088.g_kb_per_file_read_recency, feature_089.conventions_and_lints_structural_pin_date_literal, feature_090.scaffolds_and_lsp_allowlist, feature_091.budget_diet_bot, feature_092.resume_digest, feature_093.task_cost_benchmark, feature_094.selective_verifiable_knowledge_pilot, feature_095.fresh_review_loop, feature_096.fresh_review_loop_2 |
| meta_harness_9 | complete | feature_097.mh9_s0_rebase_and_isolation_pins, feature_098.mh9_s1_benchmark_follow_up_honest_cost_picture, feature_099.mh9_s2_truthful_boundary_residual, feature_100.mh9_s3_thin_work_contract, feature_101.mh9_s4_frontier_experiment |
| meta_harness_concurrent | complete | feature_039.adaptive_net_engine, feature_040.net_composition_supervisor, feature_041.resource_places_concurrency, feature_042.goal_net_synthesis, feature_043.meta_net_dashboard, feature_044.mined_behavioral_net, feature_045.work_md_net_driven, feature_046.omt_net_session_arg_whitelist, feature_047.wip_limited_pool, feature_048.wip_limited_pool, feature_049.session_start_menu |
| net_enforced_harness | complete | feature_050.net_as_gate |
| petri_net_library | complete | feature_031.petri_net_library |
| petri_net_studio | active | feature_032.petri_net_format, feature_033.petri_net_io, feature_034.studio_v1_editor, feature_035.studio_v2_analysis, feature_036.studio_v3_graph |
| project_lifecycle | active | feature_030.project_lifecycle |
| rag_v2 | active | feature_027.rag_v2, feature_029.rag_v2_slash_commands |
| workflows | draft | — |

---


## Paused (resumable)

- [x] **meta_harness_10 P2 CLOSED 2026-09-19** — P1 + A/B/B2/B3/B3b/C/D shipped (feature_108 6 goldens suite 1788 C1 CLOSED; feature_109 13 goldens suite 1801 deny matrix proven; rev 60 drained_complete; check 265/0). Residual: payback (a) needs wild sessions N≥10.
- [x] **meta_harness_8 execution — T3-4 (feature_093.task_cost_benchmark)** — SHIPPED 2026-09-14: probe double-encode fix + stale-rev placeholder + harness golden narrow; 17/17 goldens, first-numbers 6/6 green @3478bb2 (TP=13/FP=0/missed=0), suite 2231/2231; test report @ 6.testing/features/feature_093.task_cost_benchmark/test_report.md. Done-chain @ `.projects/meta/meta_harness_8/CURRENT_STATE.md`.
- [x] **meta_harness_8 execution — T3-3 (feature_092.resume_digest)** — SHIPPED 2026-09-13, same-day pause→resume: one-line probe fix (JSON.stringify; GOTCHA_PROBE_SERIALIZATION TA'd) + 3 follow-on pin re-pins (055 static, budget_diet live, 059 NAV_INDEX 64956→64990); 7 goldens + boundary e2e green, stage cleared, check/build 0 errors, suite 2214/2214; `op:resume` dogfooded for its own resume session. Next per §Scope: T3-4 / T3-6, then T5-8 loop. Done-chain @ `.projects/meta/meta_harness_8/CURRENT_STATE.md`.
- [x] **meta_harness_8 execution — T1-6 (feature_076.workflow_index_and_repair_quickfix)** — SHIPPED 2026-09-12 (canonical-target fix, authority markers on 6 workflows, `harnessc check_workflows` + `workflows [--subject|--plan]` subcommand; 16 goldens + boundary e2e green; suite 2079/2080, pre-existing 059 pin only). T4-3 (feature_075) shipped earlier. Next per §Scope: T1-4 / T1-3 → T5-1 2A; open repair flag: `meta_harness_development_self_evaluation.md` unindexed (drift warning). Done-chain @ `.projects/meta/meta_harness_8/CURRENT_STATE.md`.
- [x] **meta_harness_6 program execution** — PROGRAM COMPLETE + CLOSED 2026-09-06 (feature_051..059, all 13 items; suite 1979/0, KNOWN=0 held; delta report @ `.projects/meta/meta_harness_6/CURRENT_STATE.md` iter 10; verdicts D4–D6 @ PROJECT.md Decisions log). ⚠ Working tree uncommitted — user commit pending.

## Agent Scratchpad (auto-managed, do not edit manually)

```
FEATURES DONE (docs in each .meta/.../FEATURE.md + test_report.md; pre-2026-08-23 rotated to WORK_ARCHIVE.md):
- feature_032..feature_036 (petri_net_format/io, studio_v1/2/3) — DONE 2026-08-23→29 · details @ Tasks [x] rows + FEATURE.md/test_report.md + git log.

RECURRING GOTCHAS — 18 nav-indexed: omt_nav{op:nav, query:"GOTCHA_"} (improvement002/OPT-B → .omt @doc gotcha.*). Top-3 by cost kept inline:
- **TDD node-granularity:** declare red/green/refactor at the SAME test_node — red at `f.py::C::t` + green at `f.py` strands latest=red → omt_tdd{op:done} blocked (recovery: omt_tdd{op:green} at the exact red node).
- **omt_tdd testlist behaviors:** JSON array canonical; newline/bullet prose auto-split by tdd/cli.py `_parse_behaviors` — no re-format required.
- **Receipt round-robin (harness edits):** per-file SECOND-edit guard on harness surface → ONE edit per file per e2e receipt (parallel OK), ONE refresh per round; the e2e test file itself is receipt-EXEMPT. Multi-site transforms: uv-run python script via bash (guards hook edit-tools only) — keep the same round discipline manually.

PENDING FEATURES (next work):
- feature_001.session_user_objectives_driven_by_Petri_Net — scope & success criteria unset.
- feature_002.rag_retrieval_augmented_generation — scope & success criteria unset.
```
