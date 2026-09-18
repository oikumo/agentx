# Separation proposal: agentx product vs meta harness — index

> Location: `.sandbox/proposal/` · Status: DRAFT for review · Mode: independent of the meta harness (no `omt_*` ceremony, no ledger writes, no `src/` edits).
> Date: 2026-09-18.

## Problem

One repo currently hosts **two systems** with different lifecycles, consumers, and correctness criteria:

1. **`agentx` product** — a Python console REPL (chat, RAG, agents, ReAct, coding, models, Petri sessions) + a standalone TS Petri Studio, consumed by end users.
2. **meta harness** — an opencode control plane (OMT-HDL DSL + TS plugins + Python engines + methodology store + ops catalog) that constrains *how the coding agent edits the repo*, consumed by the agent, not by end users.

They share root config, task pool, docs, tests, and scratch dirs. Every product change pays harness tax and every harness change risks product breakage.

## What is in this proposal

| File | Contents |
|---|---|
| `01_inventory.md` | Full path-by-path map: what exists, who owns it today, which system it really belongs to |
| `02_boundary_model.md` | Boundary principles, ownership contract, gate-applicability matrix, toolchain/test/doc/state rules |
| `03_separation_proposal.md` | Options (A/B/C), recommendation, target tree, phased migration, risks |
| `04_coupling_register.md` | Concrete violations found on disk (file:line where possible) + fix per violation |

## One-picture summary

```text
┌─ PRODUCT (ships to users) ──────────────┐   ┌─ HARNESS (constrains the agent) ───────┐
│ src/agentx/**  tools/petri-net-studio/  │   │ .meta/META_HARNESS.omt  .opencode/**   │
│ shared/petri-net/ (contract)            │   │ scripts/omt/**  .meta/sdp/**           │
│ tests/{product}  pyproject (runtime)    │   │ tests/scripts/omt/**  .meta/.omt/*     │
│ README (product chapters)               │   │ AGENTS.md  opencode.jsonc (projections)│
└──────────────────┬──────────────────────┘   └───────────────┬────────────────────────┘
                   │  clean contract only                     │  observes, never imports
                   ▼                                          ▼
            shared/petri-net/ FORMAT.md + schema (ONLY legal coupling product↔studio)
┌─ TRANSVERSE (namespaced, not split) ───────────────────────────────────────────────┐
│ .workflows/{agentx,meta_harness,app_knowledge_base}/  .projects/meta/<ns>_*  WORK.md │
│ sandbox scratch (ONE root — see §3)     .meta/doc/{product|harness} (split by dir)   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## How to review

1. Read `01_inventory.md` for facts, `02_boundary_model.md` for rules.
2. Read `03_separation_proposal.md` §3 (recommendation) + §5 (migration).
3. Pick an option (or amend), then promote this draft into a `.projects/` project if it should become tracked work.
4. Do NOT execute moves from this doc directly — it is advisory until you approve.
