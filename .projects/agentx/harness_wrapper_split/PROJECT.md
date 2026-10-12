# PROJECT: harness_wrapper_split — Harness↔Product Split

> Status: **complete** · **v0.1 (2026-10-10)** — promoted from `sandbox/orthogonality_001_wrapper_split` via UC8 (manual scaffold + `link --origin manual`; no `project.py new`, no root-override sync — multi-root sync deferred to T6). Iterate freely (non-gated).

---

## New Session Quick Start

Read `sandbox/orthogonality_001_wrapper_split/PROPOSAL_V7.md` (canonical) → `T1_AUDIT_V8.md` (mapping) → `T1_SIGNOFF_V9.md` (per-file lanes table) → this file's §Scope. The membrane core is DONE (feature_138: Oracle + gate + chain + SECTION); what remains is lanes moves (sign-off table, per-bucket) + T2 goldens + 4 project relocations (T6-gated).

## Scope

Runtime-orthogonal, dev-coupled separation of AgentX product and meta-harness:

- **T1 (audit+mapping):** DONE — `T1_AUDIT_V8.md` (slug map + test buckets + row #1 + bridge backlog) + `T1_SIGNOFF_V9.md` (225-file lanes table, zero moves).
- **T2 (goldens):** DONE — `test_firewall_meta`, `test_rename_away_meta`, `test_ledger_contract_meta`, `test_newcomer_meta` (138/R6), `test_ta_strip_meta` 4 tests (146), `test_overlay_meta` 6 + feature147 gate 3 (147), `test_telemetry_isolation_meta` 2 (148) in `tests/harness_meta/split_proof_meta/`.
- **T3 (lanes):** DONE — per-bucket moves per sign-off table (R1-R6: scripts retired, features retired → `harness_meta/omt/` 72, `harness_meta/` 35/39, `agentx/` 13/56) + overlay lane proofs (147) + telemetry isolation (148); lanes 12F/2127P/5S same-12 pre-existing.
- **T4 (TA strip):** DONE — py `ast.dump`-identical + TS comment-only pinned (146); logic-touch-alongside-TA enforcement + index `{location,owner}` + studio stripped-tsc + .opencode bun-parse goldens (150).
- **T5 (per-mechanic receipts):** DONE — `@var receipt_slices_path` + `.meta/templates/receipt_slices.json` (q/net/split_proof) + `omt_shared.ts` slice branch (pure per-slice freshness, legacy byte-compat) + `scripts/omt/receipt.py` mint/status + 10 goldens (feature_151); mapped-file edits re-receipt via `receipt.py mint --slice <name>`.
- **T6 (multi-root sync + relocations):** DONE — `project_state.projects_roots/find_home/all_homes` (archive-anchored discovery; env single-root compat) + per-root manifests + WORK.md `## Projects` union (no-clobber; `OMT_WORK_PATH=tmp` idiom retired) + `move` op (kind extend, state-transparent) + `new --root` + cross-root lookups + harnessc root-aware (feature_152); `harness_wrapper_split` backfilled (D8 revision — root-aware status check demanded it; Options 11 via surgical edit + workc, no net_to_md); 4 relocations executed → `.projects/agentx/` (states preserved, pending-moves draft retired).
- **T7:** per PROPOSAL_V7 (Oracle `split_proof_meta` v2 §E — largely subsumed by the landed T2–T6 goldens + prove/verify chain; residual = program close tail).
- **Oracle (feature_138):** DONE — `scripts/omt/split_proof.py` (prove/verify/attest-bridge/newcomer-probe) + `split_proof.{cert,attest}` chain kinds + `g.split_proof` (order 37, advisory-local/strict-CI) + `SECTION:split_proof`.

## Decisions log

- **UC8 promotion (2026-10-10):** manual scaffold here (never `project.py new` into `.projects/agentx/`); feature_138 linked → this project (`--origin manual`); 4 project relocations (agentx_concurrent_development, rag_v2, petri_net_studio, agentx_1_0_0) NOT moved — single-root sync would clobber `WORK.md ## Projects` pre-T6 (V7 Alt); dirs move with T6 multi-root sync. `link` ran with `OMT_PROJECTS_ROOT` + `OMT_WORK_PATH=tmp` so neither `WORK.md` nor the agentx `META.md` pending-moves draft was disturbed.
- **Language:** "runtime-orthogonal, dev-coupled" everywhere; bare "orthogonal" rejected in review (V7 D1).
- **Grandfather rule:** everything stays where it is until T2 goldens + T3 lanes land (audit §4).

## Features

- feature_138.split_proof_oracle_firewall_slice (Oracle membrane core — DONE, this session's close-out)
- feature_143.r4_harness_features_bucket, feature_144.r5_product_features_bucket, feature_145.r6_138_goldens_bucket (lanes buckets — DONE)
- feature_146.t2_ta_strip_golden, feature_147.t3_overlay_lane_proofs, feature_148.omt_q_telemetry_isolation (goldens+lanes+isolation — DONE)
- feature_149.triage_12_residual (triage-only: 12/12 fail solo, owned outside split — DONE)
- feature_150.t4_ta_logic_touch_and_index (T4 closeout — DONE)
- feature_151.t5_per_mechanic_receipts (T5 per-mechanic receipts — DONE)
- feature_152.t6_multi_root_project_sync (T6 multi-root sync + move op + 4 relocations — DONE)
