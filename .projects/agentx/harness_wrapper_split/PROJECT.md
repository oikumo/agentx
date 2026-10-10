# PROJECT: harness_wrapper_split — Harness↔Product Split

> Status: **active** · **v0.1 (2026-10-10)** — promoted from `sandbox/orthogonality_001_wrapper_split` via UC8 (manual scaffold + `link --origin manual`; no `project.py new`, no root-override sync — multi-root sync deferred to T6). Iterate freely (non-gated).

---

## New Session Quick Start

Read `sandbox/orthogonality_001_wrapper_split/PROPOSAL_V7.md` (canonical) → `T1_AUDIT_V8.md` (mapping) → `T1_SIGNOFF_V9.md` (per-file lanes table) → this file's §Scope. The membrane core is DONE (feature_138: Oracle + gate + chain + SECTION); what remains is lanes moves (sign-off table, per-bucket) + T2 goldens + 4 project relocations (T6-gated).

## Scope

Runtime-orthogonal, dev-coupled separation of AgentX product and meta-harness:

- **T1 (audit+mapping):** DONE — `T1_AUDIT_V8.md` (slug map + test buckets + row #1 + bridge backlog) + `T1_SIGNOFF_V9.md` (225-file lanes table, zero moves).
- **T2 (goldens):** OPEN — `test_rename_away_meta`, `test_ta_strip_meta`, `test_ledger_contract_meta` in the new lanes.
- **T3 (lanes):** OPEN — per-bucket moves per the sign-off table (each under tests canary, suite green between).
- **T4–T7:** per PROPOSAL_V7 (TA strip, receipts, multi-root sync, vision fit).
- **Oracle (feature_138):** DONE — `scripts/omt/split_proof.py` (prove/verify/attest-bridge/newcomer-probe) + `split_proof.{cert,attest}` chain kinds + `g.split_proof` (order 37, advisory-local/strict-CI) + `SECTION:split_proof`.

## Decisions log

- **UC8 promotion (2026-10-10):** manual scaffold here (never `project.py new` into `.projects/agentx/`); feature_138 linked → this project (`--origin manual`); 4 project relocations (agentx_concurrent_development, rag_v2, petri_net_studio, agentx_1_0_0) NOT moved — single-root sync would clobber `WORK.md ## Projects` pre-T6 (V7 Alt); dirs move with T6 multi-root sync. `link` ran with `OMT_PROJECTS_ROOT` + `OMT_WORK_PATH=tmp` so neither `WORK.md` nor the agentx `META.md` pending-moves draft was disturbed.
- **Language:** "runtime-orthogonal, dev-coupled" everywhere; bare "orthogonal" rejected in review (V7 D1).
- **Grandfather rule:** everything stays where it is until T2 goldens + T3 lanes land (audit §4).

## Features

- feature_138.split_proof_oracle_firewall_slice (Oracle membrane core — DONE, this session's close-out)
