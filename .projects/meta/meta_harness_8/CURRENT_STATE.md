# CURRENT_STATE: meta_harness_8

> Session-by-session log + resume point. Companion to `PROJECT.md` (canonical).
> Newest entry on top. One `## <date>` block per session.

---

## 2026-09-13 (auto — feature_091.budget_diet_bot Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_091.budget_diet_bot/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-13 (iter — feature_091 T3-7 budget-diet-bot, user-picked resume)

- **T3-7 SHIPPED** (feature_091.budget_diet_bot, minor_feature, mh7 P1-4 → mh8 T3-7):
  - Mechanism: `scripts/omt/harnessc.py` new section after `measure_budgets` — `BUDGET_DIET_PROXIMITY=64`, `per_tool_arg_bytes` (mirror TS scan, pinned measure path untouched), `diet_longest_contributors` (arg describes / payload / longest nav line; lexicographic tie-break), pure `budget_diet_warnings` (warn—never error—headroom ∈ [0,64]; `free ≥65−headroom B` + contributor or generic trim-or-grow hint; over-cap owned by the existing error loop; gates/cap-None/size<0 excluded), `check_budget_diet` wiring into `run_all_checks` → both check+build print.
  - Goldens: `tests/scripts/omt/test_budget_diet.py` — 9 tests (near-cap full suggestion, 64-fires/65-silent boundary, at-cap fires, over-cap silent, scope exclusions, labels+generic hint, sorted multi-budget, hermetic wiring via synthetic @tool corpus + monkeypatched arg scan, tie-break, live pin). **9/9 green on first run.**
  - Live-fire proof (the feature working on the real repo): `budget-diet: tool_args 2454/2464B — 10B headroom (≤64B) — diet: longest @tool omt_net arg describes 657B; free ≥55B…` + agents_md 26B + tool_schemas 44B warn; nav_index 580B / ir_json 401B silent.
  - Verification: staged receipt batch (stage → 2 harnessc.py edits → boundary e2e `test_omt_harness_e2e.py` 1 passed → `stage --clear`); `harnessc check` 0 errors (265 records) + `--verify-projections` green (no .omt edit, projections byte-identical); full suite **2207 passed / 0 failed** (2198 baseline + 9).
  - Dogfood: 091's test_report + impl_notes scaffolded by feature_090's `new_feature.py testing/implementation` subcommands.
  - Deliberate non-change: 6 pre-existing harnessc.py pyright diagnostics (verified at HEAD via `bun x pyright` on `git show HEAD:…`) NOT added to `.meta/lsp_allowlist.json` — suppressing reportCallIssue/reportArgumentType/reportOptionalMemberAccess/reportReturnType file-wide on the most-edited harness file would hide genuine new type errors; documented in test_report as candidate follow-up.
  - Discipline: tests canary per D6 (phase re-declared first) · KB consult attempted (no records for scripts surface) · think-gate consult done (stage-order gotcha followed) · uv-only.
- Remaining per §Status: T3-3 / T3-4 / T3-6 (3); T5-8 loop when backlog empties. Repair flag (self_evaluation.md unindexed) still open.

---


## 2026-09-13 (iter — feature_090 T2-7 scaffolds + LSP allowlist, pause→resume)

- **T2-7 SHIPPED** (feature_090.scaffolds_and_lsp_allowlist, minor_feature, mh3 P3-10/P3-11):
  - P3-10 (pre-pause session): `new_feature.py testing/implementation` subcommands — argv exact-match pre-scan, legacy positional path byte-identical, unknown-slug/refuse-overwrite rc=2, `PROCESS_ROOT` monkeypatchable. Verified with 23/23 lifecycle tests + fresh e2e receipt at pause.
  - P3-11 (this resume): `.opencode/lib/enforcer/lsp_filter.ts` (parse/load/apply pure core + `lspAfterEdit` thin entry; fail-open on ANY surprise) + `.meta/lsp_allowlist.json` seeded with the 9 live pyright entries + enforcer after-hook registration (ONE receipt round) + `HARNESS_FILES` coverage.
  - Render contract re-pinned LIVE from opencode.db (pyright 1.1.408): per-file blocks with own headers joined by blank lines, only non-empty arrays render, multi-line messages continue on `\u00a0`-indented raw lines, text ends without trailing newline. Fixtures A (this-file 4 errors) + B (provider 5 + main 4 + rag control 1) embedded in the goldens.
  - Goldens: `tests/scripts/omt/test_scaffolds_lsp_allowlist.py` — 25 tests: 8 hermetic scaffolder + 13 bun probes (A all-suppressed → base-only text; planted `reportGeneralTypeIssues` surfaces + trailing-newline byte-preservation; B 9-dropped with control survivor; partial-allowlist byte-preservation; no-op; severity-2 never suppressed; desync/WARNING/missing-header/missing-separator fail-opens) + 4 allowlist-IO probes + 4 source pins. **25/25 green on first run.**
  - Verification: `harnessc check` 265 records 0 errors · `build` OK (nav_index 64956/65536 unchanged) · e2e receipt refreshed post-registration · full suite **2198 passed / 0 failed** (2173 baseline + 25).
  - Incidental stray repair: feature_089's repo-root `6.testing/.../test_report.md` (the §3.11 mis-creation class this feature eliminates) `git mv`'d to the canonical `.meta/software_development_process/6.testing/features/` path — cleared the `harnessc check` root_allowlist hygiene error AND feature_089's dangling report pointer.
  - Dogfood: feature_090's own impl_notes/test_report scaffolded by the new subcommands.
  - Discipline notes: tests canary re-recorded per D6 in the resume session (phase re-declared first); receipt round-robin held (registration batch inside one round); `opencode.jsonc` picked up an unrelated runtime `"sqlite3 *": "allow"` from the evidence queries (flagged for the user's commit decision, not feature surface).
  - Remaining per §Status: T3-3 / T3-4 / T3-6 / T3-7 (4); T5-8 loop when backlog empties.

---


## 2026-09-13 (auto — feature_089.conventions_and_lints_structural_pin_date_literal Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_089.conventions_and_lints_structural_pin_date_literal/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-13 (auto — feature_087.skip_scope_alignment Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_087.skip_scope_alignment/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-13 (auto — feature_086.ordered_skip_audit_plus_bootstrap_fingerprint Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_086.ordered_skip_audit_plus_bootstrap_fingerprint/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-13 (auto — feature_085.evidence_dependency_completion Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_085.evidence_dependency_completion/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-13 (auto — feature_084.recovery_and_transaction_journal Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_084.recovery_and_transaction_journal/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-13 (auto — feature_083.verification_integration_lane Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_083.verification_integration_lane/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-13 (auto — feature_082.two_worker_capacity_scope_arbitration Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_082.two_worker_capacity_scope_arbitration/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-13 (auto — feature_081.worktree_execution_isolation Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_081.worktree_execution_isolation/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-13 (auto — feature_080.task_claim_generation Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_080.task_claim_generation/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-13 (auto — feature_079.net_transaction_authority Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_079.net_transaction_authority/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-13 (auto — feature_078.op_graph_transitive_risk Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_078.op_graph_transitive_risk/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-13 (auto — feature_077.as_of_historical_temporal_replay Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_077.as_of_historical_temporal_replay/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-12 (auto — feature_076.workflow_index_and_repair_quickfix Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_076.workflow_index_and_repair_quickfix/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-12 (auto — feature_075.completion_hardening_content_bound_evidence Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_075.completion_hardening_content_bound_evidence/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-12 (auto — feature_074.receipt_batch_mode Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_074.receipt_batch_mode/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-12 (auto — feature_073.task_prep_op_slice Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_073.task_prep_op_slice/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-12 (auto — feature_072.typed_policy_semantics Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_072.typed_policy_semantics/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-12 (auto — feature_071.delegate_advisory_fold Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_071.delegate_advisory_fold/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-12 (auto — feature_070.escape_replay_fold Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_070.escape_replay_fold/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-12 (auto — feature_069.nav_answer_caps Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_069.nav_answer_caps/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-12 (auto — feature_068.schema_audit_autolink Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_068.schema_audit_autolink/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-12 (auto — feature_067.tdd_same_node_lint Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_067.tdd_same_node_lint/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-12 (iter 3 — T5 expanded 3→8 per NEXT_STEP, user-directed)

### Done

- **Reviewed `.sandbox/meta/META_HARNESS_CONCURRENT_NEXT_STEP.md` (2150 lines):** endorsed transaction-authority-first, claim+generation (no lease), revision≠generation, solo-preserved/managed-opt-in, ≤15-place discipline, idempotency, multiprocess + model-based tests; flagged stale §23 home + D3/`agent_attention=1` conflicts + lock-coverage/CLI-enum/worktree-lifecycle/journal-testability gaps.
- **Patched `PROJECT.md`:** T5 table 3→8 rows (T5-1 2A … T5-7 3C + T5-8 loop) with strict slice order + per-slice acceptance; §Scope ≈31 items + design-note list (T5-1/T5-6 added); §Status T5-expanded line; D8–D14 locked (D8 re-admits managed concurrency amending D3; D9 claim/gen; D10 lock-first; D11 coord-root/worktree; D12 managed gates; D13 topology-last; D14 command_id); References link NEXT_STEP with §23 superseded by D8.
- **Docs-only session:** no src/tests/net edits; `.projects/` non-gated (preflight clear, 0 thoughts).

### In progress / Blocked

- _(nothing — backlog redefined, nothing newly scaffolded)_

### Next

1. T2-2 / T1-2 / T1-5 (cheapest unblocked) in §Scope order unless reprioritized; T3-4 benchmark anytime. Within T5, T5-1 2A (`net transaction authority`) is first.
2. Resume entry point: `PROJECT.md` §New Session Quick Start → §The 5 tracks (T5) → this entry → §Next.

---

## 2026-09-12 (iter 2 — mh7 closed, residual absorbed, user-directed)

### Done

- **meta_harness_7 CLOSED** (`project.py close meta_harness_7`, clean — 060/061/062/063/064/066 all `complete`, no --force); header auto-flipped active→complete, manifest + WORK.md re-synced.
- **Residual mapping verified, zero new rows:** P1-2→T2-2, P1-3→T1-2, P1-4→T3-7, P2-1+F→T1-6, P2-2→T3-2, P2-3+D→T4-2, A→T3-4, B→T3-5, C→T4-1, E→T3-6, slices 2–3→T5-1/T5-2 (D7).
- **DONE-zero-carry recorded:** T2-1 via feature_065 (mh8-linked); T2-3 via mh7 feature_066; slice-1 via mh7 feature_064; Wave-0 via 060–063. PROJECT.md §Status + §Quick Start Next + D7 updated.
- **Docs-only session:** no src/tests/net edits; `.projects/` non-gated (no `omt_phase`).

### In progress / Blocked

- _(nothing — backlog defined, nothing newly scaffolded)_

### Next

1. T2-2 / T1-2 / T1-5 (cheapest unblocked) in §Scope order unless reprioritized; T3-4 benchmark anytime.
2. Resume entry point: `PROJECT.md` §New Session Quick Start → §The 5 tracks → this entry → §Next.

---

## 2026-09-12 (auto — feature_065.tdd_sync_stranded_red_closer Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_065.tdd_sync_stranded_red_closer/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-12 (iter 1 — consolidation COMPLETE, 6 closed → mh8 v1.0)

### Done

- **Closed 6 active meta-harness projects (user-approved "Close 6 active only"):** `meta_harness_3, meta_harness_5, meta_harness_7, net_enforced_harness` clean-close (all linked features have `complete`); `meta_harness_2 --force` (020/022/023 lack full-slug completes — short-slug era) + `meta_harness_concurrent --force` (047 tombstone, renamed 048 per D20). mh4/mh6 already complete, untouched.
- **Created `meta_harness_8` (`project.py new --slug meta_harness_8`, draft)** + wrote PROJECT.md v1.0: 5-track condensed backlog (≈26 items) from 6 homes; deferred trio DROPPED per "Drop deferred" (U15, modified body-hash, multi_session_concurrency); concurrent core + 050 recorded done-zero-carry; merges (U14+P1-3, U16+P2-2, D+P2-3, F+P2-1) + per-item acceptance + order proposal (T2-1/T1-2/T1-5 first).
- **Approval gate held:** 3-question gate (close scope / 5 tracks / deferred) answered before any `close`/`new` mutation, per `meta_harness_project` workflow.

### In progress / Blocked

- _(nothing — backlog defined, nothing scaffolded)_

### Next

1. User picks first build: default T2-1 `op:sync` (`new_feature.py "tdd sync stranded red closer" --type minor_feature --project meta_harness_8`) with D5 overlap check, OR T1-2 schema-autolink, OR T1-5 nav caps.
2. Then wave in §Scope order unless reprioritized; T3-4 benchmark anytime (no policy change).

### Notes / context

- Resume entry point: `PROJECT.md` §New Session Quick Start → §The 5 tracks → this entry → §Next.
- Inventory evidence this session: mh2 U4/U5/U12/U14/U16–U18/HQL pending (Phase-A done); mh3 P2×4+T2 + P3×4+T3 pending (Phase-A 028 done); mh5 empty (038 done, fresh-review loop only); mh7 Wave-1 P1-1–P1-4 + Wave-2 P2-1–P2-3 + A–F inbox + slices 2–3 pending (Wave-0 + 064 done); concurrent zero pending (039–046/048/049 + 042–044 done); net zero carry (050 done, Phase-B dropped).
- Ledger note: `feature_047.wip_limited_pool` remains without `complete` (tombstone by design); mh2 short-slug completes (`feature_021/022/023`) predate full-slug links — both forced closes logged with rationale in PROJECT.md D1.
- Wired into WORK.md daily work (user: include projects in WORK.md/general): scaffolded feature_065.tdd_sync_stranded_red_closer (T2-1 op:sync stranded-red closer, minor_feature, origin:scaffold, D5 overlap-clear vs gates.py dangling derivation); PROJECT header draft->active flipped; WORK.md Projects now active+feature_065; omt_status derived active project=mh8; net rev57 pool drained_complete (pending 0/active 0/done 7) — pool nets carry counts not subnets (D20), no splice; next: Analysis doc then implement cmd_sync per T2-1 acceptance

---

## 2026-09-12 (iter 0 — project created)

### Done

- Project home created (`project.py new`, state: draft).

### In progress / Blocked

- _(nothing)_ — superseded by iter 1 consolidation above.

### Notes / context

- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.
