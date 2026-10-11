# T1_SIGNOFF_V9 — lanes per-file sign-off table (sandbox only, no moves)

> Status: **sign-off table** (2026-10-10, mechanical enumeration + T1_AUDIT_V8 buckets). No files moved at signing, no renames, no ledger writes. Grandfather rule stood until T2 goldens + T3 lanes land; THIS table is the mapping T1 close-out requires before any move (audit §4). Counts re-measured 2026-10-10.
>
> **First bucket LANDED 2026-10-10b** (T2 goldens + first lane unit): `tests/scripts/toolbox/*` (6 files) → `tests/harness_meta/toolbox/` mirror move; T2 goldens `tests/harness_meta/split_proof_meta/{test_rename_away_meta,test_ledger_contract_meta}.py` (9 tests). LIT fixes in-commit: `hermetic_toolbox.py` (skeleton + docstrings), `test_growth.py` force_cleanup, `scripts/toolbox/toolbox.py` promote/prune scaffold paths. Suite 2118 + 4 triaged drift, check 281/0. Remaining buckets: this table still governs.
>
> **omt bucket LANDED 2026-10-10 (R1–R3, feature_141)**: `tests/scripts/omt/*` (72 files) → `tests/harness_meta/omt/` — `858d4c9` net×28, `8f5a8e6` tdd+q+kb+misc×34, `c2b5e2c` e2e+receipt+template×10 + the `.omt` e2e-vars/harness_paths swap + harnessc init-template segmented swap + 44 referencer LIT fixes (17 harness-source + 27 tests-side, incl. 5 map-missed segmented/mock sites). Suite 2118 + 5 triaged drift, check 281/0, prove both lanes clean, zero-literal sweep 0 (rows stay; dated rows unchanged). Remaining buckets: this table still governs.
>
> **tests/scripts/ RETIRED 2026-10-11 (R1+R2+R3+R3b, feature_142)**: `tests/<pdir>` 17 files → `tests/agentx/<pdir>` (`df585a1` + test_io parents[4]); `tests/scripts/reason/` 3 → `tests/harness_meta/reason/` (`8074515`); `tests/scripts/session_inspect/` 24 → `tests/harness_meta/session_inspect/` (`fe890f1` +2 dotted fixes, `b864dbf` 4 docstring LIT completes 6-site map) + `rm -rf tests/scripts`. Session 72+2, both lanes 1140+same 5 triaged+6 skipped, prove both clean, sweep 0 (2 exempt TA). Remaining: R4/R5/R6 per dry-runs.
>
> **R4 LANDED 2026-10-11 (feature_143)**: `tests/features/` 35 dirs/39 files → `tests/harness_meta/` (`568afdb`: R4a SYS-heavy 22 + R4b LIT-heavy 13) + 5 same-commit fixes (016 run-path, 131/132/134 bridge prose, 016 validate-exit split-args pin). Targeted 016+050 33 passed; lanes 1441+12 HEAD-proven pre-existing (5 known triaged + 054/056/058/060×2/062-parity/103 v2-perm/live-drift, stash-verified at old homes) +6 skipped; 2 DeclareEmbed parallel flakes pass solo; prove both clean. Left untouched (golden fixtures/placeholders): 054 own-dir/evil paths, 055 fake probe path, 056 guard path, 062 preflight message format, sentinel `<feature>` patterns. Remaining: R5/R6 per dry-runs.
>
> **R5 LANDED 2026-10-11 (feature_144)**: `tests/features/` 13 dirs/56 files → `tests/agentx/` (`c881212`) + 5 same-commit fixes (031 4× `tests.model.petri_net`→`tests.agentx.model.petri_net` imports incl conftest + docstring path — stale since R1 product-dirs move). Agentx lane 902+3 (was 8 collection errors); lanes 2097+same stable 12 pre-existing+9 skipped, no new failures; prove both clean; DEPTH intact; fixtures WITH dir. Left untouched: 4 sentinel matcher-pattern placeholders (harness-matcher convention refs, not live paths). Remaining: R6 per dry-run.

## 0. Method

- Enumerated every `tests/**/*.py` (225 files, `__pycache__` excluded) with a script (`/tmp` scratch, not committed). Buckets = T1_AUDIT_V8 §2 + feature_138 → harness_meta (E4 planned home `tests/harness_meta/split_proof_meta/`).
- Risk markers per file: `LIT` = literal `tests/scripts|tests/features` path string (needs content edit on move); `DEPTH:parents[N]` = `__file__` depth arithmetic (safe IFF the move preserves depth); `FILE` = other `__file__` use; `SYS` = `sys.path` surgery; `CONF` = mentions conftest.
- Move rule (depth-preserving mirror): `tests/scripts/<sub> → tests/harness_meta/<sub>`, `tests/features/<dir> → tests/harness_meta/<dir>` or `tests/agentx/<dir>` (bucket), `tests/<pdir> → tests/agentx/<pdir>` EXCEPT the 7 DEPTH-risk product-dir files (see §3). `testpaths=["tests"]` keeps collecting both lanes with zero config change.

## 1. Counts

| Lane | Files | LIT-risk | DEPTH-risk |
|---|---|---|---|
| `tests/agentx/` | 70 | 4 | 7 |
| `tests/harness_meta/` | 146 | 33 | 93 |
| `REVIEW` | 5 | 3 | 2 |
| `EXCLUDE` | 4 | 1 | 0 |

- Non-test helpers (`__init__`/`conftest`/fixtures, 24 files) move WITH their dirs (no separate lane).
- Shared roots stay: `tests/__init__.py`, `tests/conftest.py`, `tests/constants.py`, `tests/testing_utils.py` (EXCLUDE — both lanes import them in place).
- `sys.path` surgery (10 files, all harness-bucket sentinels/gates) assumes repo-root insertion — root-agnostic, safe under mirror moves; re-verify per bucket at move time.

## 2. Pre-move fix list (content edits, each under tests canary)

- 40 LIT files (4 agentx + 33 harness_meta + 3 review): rewrite `tests/scripts|tests/features` literals to the new lane path in the SAME commit as the move (per-bucket commits, suite green between).
- 7 DEPTH-risk product-dir files: `tests/<pdir> → tests/agentx/<pdir>` breaks `parents[N]` (+1 depth). Options per file: (a) flat-move to `tests/agentx/` top (collision-check names first), or (b) keep subdir + bump the index. Decided at move time, one file one line.
- 5 REVIEW files: RESOLVED 2026-10-10b (one file one line, per-file): 015 → `tests/agentx/` (zero harness imports — pure product hardening), 030 conftest+goldens → `tests/harness_meta/` (sentinel re-export of harness goldens; import updates with the omt bucket), 043 → `tests/harness_meta/` (single-lane call: runtime imports scripts/omt/net only; product half exercised via subprocess), kb_akb → `tests/harness_meta/` (harness-source structural pins; product knowledge is index data). Enabling harness edits (receipt-covered, lane-aware): `phase_gate.ts` checkPhaseExitArtifacts + declare-embed probe, `receipt_guard.ts` isOwnTestDir, `tdd/gates.py` _feature_test_dirs (behavioral run + coverage union) — 054 golden extended with lane scenarios.

## 3. Full per-file table

| File | Lane | Basis | Risks |
|---|---|---|---|
| `tests/__init__.py` | `EXCLUDE` | out-of-scope | - |
| `tests/conftest.py` | `EXCLUDE` | out-of-scope | LIT:path-literal |
| `tests/constants.py` | `EXCLUDE` | out-of-scope | - |
| `tests/controllers/__init__.py` | `tests/agentx/` | product-dir | - |
| `tests/controllers/main_controller/test_main_controller.py` | `tests/agentx/` | product-dir | - |
| `tests/controllers/rag_controller/__init__.py` | `tests/agentx/` | product-dir | - |
| `tests/controllers/rag_controller/test_rag_controller.py` | `tests/agentx/` | product-dir | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/__init__.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/conftest.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_agent_facade.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_axr03_policy_acceptance.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_axr04_axr08_axr09_session_lifecycle.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_axr10_single_active_goal.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_axr11_safe_execution_recovery.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_bug_fixes.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_goal_manager.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_memory_manager.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_mvc_compliance.py` | `tests/agentx/` | product-bucket | DEPTH:parents[3] |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_persistence.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_policy_engine.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_reflection_engine.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_tool_registry.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_types.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_010.agent_demo_screen/__init__.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_010.agent_demo_screen/conftest.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_010.agent_demo_screen/test_demo_controller.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_010.agent_demo_screen/test_demo_scenarios.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_013.ai_model_provider_selector/__init__.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_013.ai_model_provider_selector/test_model_registry.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_013.ai_model_provider_selector/test_mvc_model_selector.py` | `tests/agentx/` | product-bucket | DEPTH:parents[3] |
| `tests/features/feature_015.agentx_security_and_quality_hardening/test_feature_015_hardening.py` | `REVIEW` | review-bucket | - |
| `tests/features/feature_016.tdd_enforcement/test_tdd_enforcement.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal, DEPTH:parents[3] |
| `tests/features/feature_018.react_screen/__init__.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_018.react_screen/test_react_agent_service.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_018.react_screen/test_react_controller.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_019.coding_agent_screen/test_axr01_axr02_axr12_filesystem_containment.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_019.coding_agent_screen/test_coding_integration.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_019.coding_agent_screen/test_coding_tools.py` | `tests/agentx/` | product-bucket | FILE:__file__ |
| `tests/features/feature_024.no_tui_full_features/__init__.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_024.no_tui_full_features/test_axr06_provider_dispatch.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_024.no_tui_full_features/test_axr07_chat_persistence.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_024.no_tui_full_features/test_chat_error_surfacing.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_024.no_tui_full_features/test_console_commands_and_views.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_024.no_tui_full_features/test_console_provider_and_views.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_025.coding_context_window_optimization/test_deepagent_context_optimization.py` | `tests/agentx/` | product-bucket | FILE:__file__ |
| `tests/features/feature_026.omt_q_interrogative_first_ops/test_omt_q_golden_smoke.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal |
| `tests/features/feature_027.rag_v2/__init__.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_027.rag_v2/fixtures/__init__.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_027.rag_v2/test_axr05_rag_file_handoff.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_027.rag_v2/test_rag_v2_agent_service.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_027.rag_v2/test_rag_v2_commands_and_views.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_027.rag_v2/test_rag_v2_console_repl_regression.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_027.rag_v2/test_rag_v2_gaps_closure_matrix.py` | `tests/agentx/` | product-bucket | FILE:__file__ |
| `tests/features/feature_027.rag_v2/test_rag_v2_ingestion_persist_fix.py` | `tests/agentx/` | product-bucket | FILE:__file__ |
| `tests/features/feature_027.rag_v2/test_rag_v2_mvc_contract.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_027.rag_v2/test_rag_v2_retrieval_tool.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_029.rag_v2_slash_commands/__init__.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_029.rag_v2_slash_commands/test_rag_v2_slash_commands.py` | `tests/agentx/` | product-bucket | DEPTH:parents[3] |
| `tests/features/feature_030.project_lifecycle/conftest.py` | `REVIEW` | review-bucket | - |
| `tests/features/feature_030.project_lifecycle/test_project_lifecycle_goldens.py` | `REVIEW` | review-bucket | LIT:path-literal |
| `tests/features/feature_031.petri_net_library/conftest.py` | `tests/agentx/` | product-bucket | - |
| `tests/features/feature_031.petri_net_library/test_petri_net_library_sentinel.py` | `tests/agentx/` | product-bucket | LIT:path-literal |
| `tests/features/feature_034.studio_v1_editor/test_studio_v1_editor_sentinel.py` | `tests/agentx/` | product-bucket | LIT:path-literal, DEPTH:parents[3] |
| `tests/features/feature_035.studio_v2_analysis/test_studio_v2_analysis_sentinel.py` | `tests/agentx/` | product-bucket | LIT:path-literal, DEPTH:parents[3] |
| `tests/features/feature_036.studio_v3_graph/test_studio_v3_graph_sentinel.py` | `tests/agentx/` | product-bucket | LIT:path-literal, DEPTH:parents[3] |
| `tests/features/feature_039.adaptive_net_engine/test_feature_039_sentinel.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal, DEPTH:parents[3] |
| `tests/features/feature_040.net_composition_supervisor/test_feature_040_sentinel.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal, DEPTH:parents[3] |
| `tests/features/feature_041.resource_places_concurrency/test_feature_041_sentinel.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal, DEPTH:parents[3] |
| `tests/features/feature_043.meta_net_dashboard/test_dashboard_sentinel.py` | `REVIEW` | review-bucket | LIT:path-literal, DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_050.net_as_gate/test_net_gate.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_051.ledger_test_isolation/test_ledger_isolation.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal, DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_052.opencode_version_canary/test_version_canary.py` | `tests/harness_meta/` | harness-bucket | FILE:__file__ |
| `tests/features/feature_053.net_gate_concurrency_predicate/test_net_concurrency_predicate.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_054.small_task_fast_path/test_small_task_fast_path.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal |
| `tests/features/feature_055.gate_preflight/test_gate_preflight.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal |
| `tests/features/feature_056.skip_taxonomy_phase_hygiene/test_phase_hygiene.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal, DEPTH:parents[3] |
| `tests/features/feature_056.skip_taxonomy_phase_hygiene/test_skip_taxonomy.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_057.gate_budget_ceremony_meter/test_gate_budget_ceremony.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_058.thought_review_gotcha_root_cause/test_thought_review.py` | `tests/harness_meta/` | harness-bucket | FILE:__file__ |
| `tests/features/feature_059.harness_tiered_template/test_budget_pins.py` | `tests/harness_meta/` | harness-bucket | FILE:__file__, SYS:sys.path |
| `tests/features/feature_059.harness_tiered_template/test_init_fs.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal, SYS:sys.path |
| `tests/features/feature_059.harness_tiered_template/test_mvc_profile.py` | `tests/harness_meta/` | harness-bucket | FILE:__file__ |
| `tests/features/feature_059.harness_tiered_template/test_tier_filter.py` | `tests/harness_meta/` | harness-bucket | FILE:__file__, SYS:sys.path |
| `tests/features/feature_060.dangling_active_only/test_dangling_active_only.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3] |
| `tests/features/feature_061.nav_cache_hit/test_nav_cache_hit.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3] |
| `tests/features/feature_062.preflight_on_declare/test_preflight_on_declare.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal, DEPTH:parents[3] |
| `tests/features/feature_063.kb_sticky_per_feature/test_kb_sticky_per_feature.py` | `tests/harness_meta/` | harness-bucket | FILE:__file__ |
| `tests/features/feature_064.named_work_truthful_observation/test_named_work_truthful_observation.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_066.think_batch_consult/test_think_batch_consult.py` | `tests/harness_meta/` | harness-bucket | FILE:__file__ |
| `tests/features/feature_103.mh10_p2_global_gate/test_managed_ops.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_104.mh10_p2_rewire_claims_through_fire/test_rewire.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_105.mh10_p2b2_template_fix_work_release/test_b2_template.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_106.mh10_p2b3_lane_integration_rewire/test_b3_lane.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_107.mh10_p2b3b_lane_template_landing/test_b3b_template.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_108.mh10_p2c_crash_reorder/test_c_crash_reorder.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_109.mh10_p2d_matrix_payback/test_d_matrix.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_114.concurrent_dispatch_runtime/test_dispatch_o4.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal, DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_118.mh11_worktree_lifecycle/test_lifecycle_smoke.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal, DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_131.opencode_session_inspection_and_experiments/test_slice1_bridge.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal, DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_132.pilot_launch_path/test_bridge_132.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal, DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_133.dispatcher_gate_wiring/test_bridge_133.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_134.real_trial_launcher/test_bridge_134.py` | `tests/harness_meta/` | harness-bucket | LIT:path-literal, DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_135.lean_start_v1_variant/test_lean_start_swap.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_138.split_proof_oracle_firewall_slice/test_firewall_meta.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3], SYS:sys.path |
| `tests/features/feature_138.split_proof_oracle_firewall_slice/test_newcomer_meta.py` | `tests/harness_meta/` | harness-bucket | DEPTH:parents[3] |
| `tests/features/feature_kb_akb.application_knowledge_base/test_kb_feature_acceptance.py` | `REVIEW` | review-bucket | LIT:path-literal, DEPTH:parents[3] |
| `tests/model/__init__.py` | `tests/agentx/` | product-dir | - |
| `tests/model/petri_net/__init__.py` | `tests/agentx/` | product-dir | - |
| `tests/model/petri_net/test_analysis.py` | `tests/agentx/` | product-dir | - |
| `tests/model/petri_net/test_coverability.py` | `tests/agentx/` | product-dir | - |
| `tests/model/petri_net/test_io.py` | `tests/agentx/` | product-dir | DEPTH:parents[3] |
| `tests/model/petri_net/test_model.py` | `tests/agentx/` | product-dir | - |
| `tests/model/program/__init__.py` | `tests/agentx/` | product-dir | - |
| `tests/model/program/test_program.py` | `tests/agentx/` | product-dir | - |
| `tests/scripts/omt/test_argv_value_guard_pins.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3] |
| `tests/scripts/omt/test_budget_diet.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal, DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_completion_hardening.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal, DEPTH:parents[3], SYS:sys.path, CONF:mentions-conftest |
| `tests/scripts/omt/test_conventions_and_lints.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_delegate_advisory_fold.py` | `tests/harness_meta/` | harness-dir | FILE:__file__ |
| `tests/scripts/omt/test_done_baseline_regressions.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal, DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_escape_replay_fold.py` | `tests/harness_meta/` | harness-dir | FILE:__file__ |
| `tests/scripts/omt/test_gate_two_hats_message.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_gkb_read_recency.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3] |
| `tests/scripts/omt/test_harnessc.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal, DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_harnessc_workflows.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal, DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_kb_ast_extract.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_kb_compiler.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_kb_pilot.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal |
| `tests/scripts/omt/test_ledger_rotation.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_mvc_check.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal, SYS:sys.path |
| `tests/scripts/omt/test_nav_answer_caps.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3] |
| `tests/scripts/omt/test_net_apply_o2.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_claim_o3.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_cli.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_conformance.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_dispatch_o4.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_engine.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_evidence_dependency.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_followup_o5.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_fresh_o5.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_history.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_menu.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_menu_o1.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_mine.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_pool.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_recovery_journal.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_resources.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_splice.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_state.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_sync.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_sync_md.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_synthesize.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_task_claim_generation.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_transaction_authority.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_two_worker_capacity_scope.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_verification_integration_lane.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_verify_dispatch_117.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_worktree_isolation.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_net_worktree_lifecycle_b.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_omt_docs_drift_pins.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal, DEPTH:parents[3] |
| `tests/scripts/omt/test_omt_enforcer_guard_source_pins.py` | `tests/harness_meta/` | harness-dir | FILE:__file__ |
| `tests/scripts/omt/test_omt_harness_e2e.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal, DEPTH:parents[3] |
| `tests/scripts/omt/test_omt_live_opencode_guards.py` | `tests/harness_meta/` | harness-dir | FILE:__file__ |
| `tests/scripts/omt/test_omt_net_plugin_args.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3] |
| `tests/scripts/omt/test_omt_q.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal |
| `tests/scripts/omt/test_omt_q_audit.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3] |
| `tests/scripts/omt/test_omt_q_audit_t1_1.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3] |
| `tests/scripts/omt/test_omt_q_state_summary.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3] |
| `tests/scripts/omt/test_omt_session_plugin_args.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_opencode_sdk_contract.py` | `tests/harness_meta/` | harness-dir | FILE:__file__ |
| `tests/scripts/omt/test_project_lifecycle.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal, DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_receipt_batch_mode.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal, DEPTH:parents[3] |
| `tests/scripts/omt/test_resume_digest.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal |
| `tests/scripts/omt/test_scaffolds_lsp_allowlist.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal, DEPTH:parents[3] |
| `tests/scripts/omt/test_skip_scope_alignment.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path, CONF:mentions-conftest |
| `tests/scripts/omt/test_split_proof_gate.py` | `tests/harness_meta/` | harness-dir | FILE:__file__ |
| `tests/scripts/omt/test_task_cost_benchmark.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_task_prep_slice.py` | `tests/harness_meta/` | harness-dir | FILE:__file__ |
| `tests/scripts/omt/test_tasks_options_drift.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal, DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_tdd_check.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal, SYS:sys.path |
| `tests/scripts/omt/test_tdd_feature_scoped_state.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_tdd_same_node_lint.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_tdd_sync.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/omt/test_thought_pattern_pin.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3] |
| `tests/scripts/omt/test_typed_policy_semantics.py` | `tests/harness_meta/` | harness-dir | FILE:__file__ |
| `tests/scripts/omt/test_validate_exit_coverage_on_diff.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path, CONF:mentions-conftest |
| `tests/scripts/reason/test_argv_whitelist.py` | `tests/harness_meta/` | harness-dir | - |
| `tests/scripts/reason/test_cert_replay.py` | `tests/harness_meta/` | harness-dir | - |
| `tests/scripts/reason/test_probes_fixtures.py` | `tests/harness_meta/` | harness-dir | - |
| `tests/scripts/session_inspect/conftest.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path |
| `tests/scripts/session_inspect/test_adapter.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_dispatcher_gate.py` | `tests/harness_meta/` | harness-dir | - |
| `tests/scripts/session_inspect/test_fake_launcher.py` | `tests/harness_meta/` | harness-dir | - |
| `tests/scripts/session_inspect/test_hierarchy_usage.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_inspect_trace.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_labels.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_normalize.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_pipeline.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_run_gate.py` | `tests/harness_meta/` | harness-dir | - |
| `tests/scripts/session_inspect/test_schema.py` | `tests/harness_meta/` | harness-dir | - |
| `tests/scripts/session_inspect/test_slice2_cli.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_slice2_inspect_trace.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_slice2_query.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_slice3_compare.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_slice3_exporter.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_slice3_integration.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_slice3_profile.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_slice4_collect.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_slice4_evaluate.py` | `tests/harness_meta/` | harness-dir | - |
| `tests/scripts/session_inspect/test_slice4_manifest.py` | `tests/harness_meta/` | harness-dir | - |
| `tests/scripts/session_inspect/test_slice5_session_service.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path, CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_slice6_s6_acceptance.py` | `tests/harness_meta/` | harness-dir | DEPTH:parents[3], SYS:sys.path, CONF:mentions-conftest |
| `tests/scripts/session_inspect/test_trace_bounded_paging.py` | `tests/harness_meta/` | harness-dir | CONF:mentions-conftest |
| `tests/scripts/toolbox/hermetic_toolbox.py` | `tests/harness_meta/` | harness-dir | LIT:path-literal, DEPTH:parents[3], CONF:mentions-conftest |
| `tests/scripts/toolbox/test_docs_tiers.py` | `tests/harness_meta/` | harness-dir | - |
| `tests/scripts/toolbox/test_growth.py` | `tests/harness_meta/` | harness-dir | - |
| `tests/scripts/toolbox/test_query.py` | `tests/harness_meta/` | harness-dir | - |
| `tests/scripts/toolbox/test_recent_log.py` | `tests/harness_meta/` | harness-dir | - |
| `tests/scripts/toolbox/test_run_metering.py` | `tests/harness_meta/` | harness-dir | - |
| `tests/testing_utils.py` | `EXCLUDE` | out-of-scope | - |
| `tests/unit/model/test_chat_history.py` | `tests/agentx/` | product-dir | - |
| `tests/unit/model/test_rag_chat_history.py` | `tests/agentx/` | product-dir | - |
| `tests/unit/test_safe_int_hardening.py` | `tests/agentx/` | product-dir | - |
| `tests/views/__init__.py` | `tests/agentx/` | product-dir | - |
| `tests/views/test_rag_view.py` | `tests/agentx/` | product-dir | - |

## 4. What remains (not done in this pass)

- Per-bucket move commits (agentx dirs → harness scripts → harness features → review singles), each: move + LIT fixes + `uv run pytest tests/agentx tests/harness_meta -q` green + firewall re-prove. Each move commit needs `omt_skip{scope:tests}` canary.
- E4 golden migration `tests/features/feature_138.* → tests/harness_meta/split_proof_meta/` rides the harness-features bucket (REPO parents[3] depth preserved by the mirror rule — no golden edit needed).
- T2 goldens (`test_rename_away_meta`, `test_ta_strip_meta`, `test_ledger_contract_meta`) land FIRST in the new lanes (they cannot run against the mixed layout).
