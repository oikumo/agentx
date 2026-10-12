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
Options: proj:agentx_concurrent_development, proj:feature_kb_akb, proj:meta_harness_14, proj:meta_harness_15, proj:petri_net_studio, proj:project_lifecycle, proj:rag_v2, proj:workflows, unscoped:001, unscoped:002
Lanes: verification 0/1 free 1, integration 0/1 free 1
## Projects (synced by `uv run scripts/omt/project.py sync` — do not hand-edit)

| project | state | features |
|---|---|---|
| agentx_1_0_0 | draft | — |
| agentx_concurrent_development | active | feature_119.ledger_backed_fix_preview |
| harness_wrapper_split | complete | feature_138.split_proof_oracle_firewall_slice, feature_152.t6_multi_root_project_sync |
| petri_net_studio | active | feature_032.petri_net_format, feature_033.petri_net_io, feature_034.studio_v1_editor, feature_035.studio_v2_analysis, feature_036.studio_v3_graph |
| rag_v2 | active | feature_027.rag_v2, feature_029.rag_v2_slash_commands |
| feature_kb_akb | active | feature_kb_akb |
| harness_reason | complete | feature_122.harness_reason_stage_0_contract_extraction, feature_123.harness_reason_stage_1_checker, feature_124.harness_reason_stage_2_composition, feature_125.harness_reason_stage_3_paired_experiment, feature_126.harness_reason_held_out_real_tasks, feature_127.harness_reason_tier_0_renderer, feature_128.harness_reason_tier_1_advisory_pilot, feature_129.harness_reason_real_token_measurement, feature_130.real_token_discharge |
| meta_harness_10 | complete | feature_102.mh10_p1_global_projection, feature_103.mh10_p2_global_gate, feature_104.mh10_p2_rewire_claims_through_fire, feature_105.mh10_p2b2_template_fix_work_release, feature_106.mh10_p2b3_lane_integration_rewire, feature_107.mh10_p2b3b_lane_template_landing, feature_108.mh10_p2c_crash_reorder, feature_109.mh10_p2d_matrix_payback |
| meta_harness_11 | complete | feature_110.whole_project_menu_composer, feature_111.multi_select_directive_protocol, feature_112.identity_aware_pool, feature_113.live_progress_projection, feature_114.concurrent_dispatch_runtime, feature_115.live_progress_full_push_join_view, feature_116.mh11_o6c_wild_payback_measurement, feature_117.dispatch_lane_exploitation_for_harness_verifies, feature_118.mh11_worktree_lifecycle |
| meta_harness_12 | complete | feature_120.toolbox_t1_index_query, feature_121.toolbox_t4_docs_tiers |
| meta_harness_13 | complete | feature_131.opencode_session_inspection_and_experiments, feature_132.pilot_launch_path, feature_133.dispatcher_gate_wiring, feature_134.real_trial_launcher |
| meta_harness_14 | active | feature_135.lean_start_v1_variant, feature_136.json_arg_object_coercion_transport_hardening |
| meta_harness_15 | active | feature_137.trace_bounded_paging |
| meta_harness_2 | complete | feature_020.meta_harness_navigation, feature_021.meta_harness_think_anywhere, feature_022.meta_harness_think_anywhere_v2, feature_023.meta_harness_improvement, feature_026.omt_q_interrogative_first_ops |
| meta_harness_3 | complete | feature_028.feature_scoped_gating |
| meta_harness_4 | complete | feature_037.tdd_testlist_prose_fallback |
| meta_harness_5 | complete | feature_038.tdd_toolchain_aware |
| meta_harness_6 | complete | feature_051.ledger_test_isolation, feature_052.opencode_version_canary, feature_053.net_gate_concurrency_predicate, feature_054.small_task_fast_path, feature_055.gate_preflight, feature_056.skip_taxonomy_phase_hygiene, feature_057.gate_budget_ceremony_meter, feature_058.thought_review_gotcha_root_cause, feature_059.harness_tiered_template |
| meta_harness_7 | complete | feature_060.dangling_active_only, feature_061.nav_cache_hit, feature_062.preflight_on_declare, feature_063.kb_sticky_per_feature, feature_064.named_work_truthful_observation, feature_066.think_batch_consult |
| meta_harness_8 | complete | feature_065.tdd_sync_stranded_red_closer, feature_067.tdd_same_node_lint, feature_068.schema_audit_autolink, feature_069.nav_answer_caps, feature_070.escape_replay_fold, feature_071.delegate_advisory_fold, feature_072.typed_policy_semantics, feature_073.task_prep_op_slice, feature_074.receipt_batch_mode, feature_075.completion_hardening_content_bound_evidence, feature_076.workflow_index_and_repair_quickfix, feature_077.as_of_historical_temporal_replay, feature_078.op_graph_transitive_risk, feature_079.net_transaction_authority, feature_080.task_claim_generation, feature_081.worktree_execution_isolation, feature_082.two_worker_capacity_scope_arbitration, feature_083.verification_integration_lane, feature_084.recovery_and_transaction_journal, feature_085.evidence_dependency_completion, feature_086.ordered_skip_audit_plus_bootstrap_fingerprint, feature_087.skip_scope_alignment, feature_088.g_kb_per_file_read_recency, feature_089.conventions_and_lints_structural_pin_date_literal, feature_090.scaffolds_and_lsp_allowlist, feature_091.budget_diet_bot, feature_092.resume_digest, feature_093.task_cost_benchmark, feature_094.selective_verifiable_knowledge_pilot, feature_095.fresh_review_loop, feature_096.fresh_review_loop_2 |
| meta_harness_9 | complete | feature_097.mh9_s0_rebase_and_isolation_pins, feature_098.mh9_s1_benchmark_follow_up_honest_cost_picture, feature_099.mh9_s2_truthful_boundary_residual, feature_100.mh9_s3_thin_work_contract, feature_101.mh9_s4_frontier_experiment |
| meta_harness_concurrent | complete | feature_039.adaptive_net_engine, feature_040.net_composition_supervisor, feature_041.resource_places_concurrency, feature_042.goal_net_synthesis, feature_043.meta_net_dashboard, feature_044.mined_behavioral_net, feature_045.work_md_net_driven, feature_046.omt_net_session_arg_whitelist, feature_047.wip_limited_pool, feature_048.wip_limited_pool, feature_049.session_start_menu |
| meta_harness_skills | active | feature_153.ci_base_green, feature_154.skill_contract_v1 |
| net_enforced_harness | complete | feature_050.net_as_gate |
| petri_net_library | complete | feature_031.petri_net_library |
| project_lifecycle | active | feature_030.project_lifecycle |
| workflows | active | meta.workflows_definition_layer |

---


## Paused (resumable)

- [~] **pause 2026-10-12 — meta_harness_skills @ feature_154 Programming** — resume: `sandbox/pause_2026-10-12_meta_harness_skills.md` (§0/§3/§5). Next: TDD done → report → complete → commit → 155.

- [x] **feature_151 close-out — T5 per-mechanic receipts DONE 2026-10-11** — `@var receipt_slices_path` + `.meta/templates/receipt_slices.json` (3 seed slices) + `omt_shared.ts` slice branch (PURE passed_at vs mtime, digest-if-present, results_passed, policy_ver global; legacy byte-compat; fallback const OPT-E) + NEW `scripts/omt/receipt.py` mint/status (fail-closed, atomic, `--slice all` never touches global); 10 goldens (real-git-dirty roots); net ghost-path corrected (live mint fail-closed exposed it); TDD same-node RED→GREEN→REFACTOR→DONE; boundary e2e 1 + self-mints q/net/split_proof (digests 1/3/1); split_proof_meta 39, lanes 12F/2144P/5S same-12 zero-new, prove both clean verify STALE-valid certs rm'd, check 282/0. Detail: `.projects/agentx/harness_wrapper_split/CURRENT_STATE.md`. Next: T6 + program close.

- [x] **pause 2026-10-12 — program close tail, nothing in-flight** — T6 landed (`6718e45`+`8965049`), tree clean, check 282/0, lanes 12F/2154P/5S; resume: `sandbox/pause_2026-10-12.md` (§0 read-order, §3 next, §5 baselines). Next: STALE reconciliation + UC0 + bridge: + CI pinning + Q5 + phantom-link.

- [x] **feature_148 close-out — telemetry isolation DONE 2026-10-11** — `omt_q.ts` OMT_Q_TELEMETRY=off guard + 3 live probes live→off + new `test_telemetry_isolation_meta.py` 2 passed; targeted 35/36 (1 triaged bootstrap), overlay 6, lanes 12F/2127P/5S same-12, prove both clean verify STALE-valid cert-growth (+0q 242→246), check 281/0, receipt FRESH. Detail: `.projects/agentx/harness_wrapper_split/CURRENT_STATE.md`. Next: 12-triage + T4–T6.

- [x] **feature_152 close-out — T6 multi-root project sync DONE 2026-10-11** — `project_state` projects_roots/find_home/all_homes + archive-anchored default (hermetic) + per-root manifests + WORK.md ## Projects UNION (shape locked) + derive_state move-transparent; `project.py` move op (kind extend, no-op, archived-guard-first) + new --root + cross-root lookups; `harnessc` 4 checks + manifest byte-compare per root; 10 goldens (union, per-root, move+guards, row-invariant, --root, lookups, env compat, FSM); 030 43 zero-edits; harness_wrapper_split BACKFILLED (D8 revision — root-aware check demanded it; Options +1 surgical, no net_to_md); 4 relocations → .projects/agentx (states preserved, WORK rows byte-identical, pending-moves draft retired); lanes 12F/2154P/5S same-12 zero-new, prove both clean verify STALE-valid certs rm'd, check 282/0. Detail: `.projects/agentx/harness_wrapper_split/CURRENT_STATE.md`. Next: program close tail (UC0, bridge:, CI pinning, Q5, phantom-link, rev60-vs-live STALE).

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
