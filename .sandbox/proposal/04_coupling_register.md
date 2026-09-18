# 04 — Coupling register (violations found 2026-09-18 + fix per item)

> Severity: 🔴 breaks the boundary (import/test/config) · 🟡 mixes narratives (docs/pools/scratch) · 🟢 exemplary (keep as pattern).

| # | Location | Finding | Severity | Fix (→ proposal §3 phase) |
|---|---|---|---|---|
| 1 | `src/agentx/test_omt_mvc_gate.py`, `src/agentx/ui/test_omt_mvc_gate.py` | Harness gate tests live INSIDE product source; product tree imports harness concerns | 🔴 | Move → `tests/scripts/omt/` (Phase 1.4) |
| 2 | `README.md:47–321` | Product manual + full harness spec (components table, DSL, token budgets, MH6→MH9 history, TDD/nav/think/net chapters) in the user-facing file | 🟡 | Shrink to pointer table → `.meta/doc/harness/` (Phase 1.3) |
| 3 | `sandbox/` vs `.sandbox/` | TWO scratch roots: workflows spec mandates `./sandbox/` (§5), reality is `.sandbox/` (50+ entries: pauses, bench, frontier, global_state, work_contract, meta) | 🟡 | Single root `.sandbox/` + domain folders; `sandbox/` → archive pointer (Phase 1.1–1.2) |
| 4 | `.meta/doc/` flat mix | Product arch (`omt++/`, `petri_nets/`) co-located with harness design (`harness/`, `opencode_plugins/`, `tdd/`) | 🟡 | Split `doc/product/` vs `doc/harness/` + indexes (Phase 1.5) |
| 5 | `WORK.md` single pool | Product + harness tasks, `## Projects` (18 folders both systems), net pool `net_rev:57`, scratchpad gotchas all in one machine-parseable file | 🟡 | Keep pool; add per-domain header views (Phase 3). No split now |
| 6 | `.projects/meta/` flat namespace | Product (`rag_v2`, `petri_net_studio`, `petri_net_library`, `project_lifecycle`, `agentx_concurrent_development`, `feature_kb_akb`, `workflows`) + harness (`meta_harness_*`, `net_enforced_harness`, `meta_harness_concurrent`) share one level | 🟡 | Prefix rule for NEW projects; legacy grandfathered (Phase 3) |
| 7 | `tests/` flat root | Product layer/feature tests + `tests/scripts/omt/` (~60 harness files) + harness feature dirs share one `pytest` root/config | 🟡 | Logical split `tests/product/` vs `tests/scripts/omt/` (Phase 1, moves only) |
| 8 | `pyproject.toml` / `uv.lock` | ONE env for product runtime (langchain, chroma…) + harness dev (pytest) | 🟡 | Keep (explicit non-goal). Split only if B ever triggers |
| 9 | `opencode.jsonc` + `AGENTS.md` at root | Harness projections live at repo root next to product files; root is the agent's first read | 🟡 | Keep (required by opencode); mark clearly as GENERATED in both headers (already done) |
| 10 | `GETTING_STARTED.md` (gitignored, present) | Harness tier doc at root with product-looking name; easy to mistake for product onboarding | 🟡 | Header line stating generated tier + pointer to product quickstart in `README.md` |
| 11 | `local_sessions/`, `test_sandbox/`, `.venv/`, `.mypy_cache/` etc. at root | Runtime/tool scratch at root alongside harness state `.meta/.omt/` | 🟡 | Document in root map; no move (tool-owned) |
| 12 | `shared/petri-net/` + `shared/META.md` | Contract-only dir, no code, canonical-bytes rule — Python ↔ TS parity WITHOUT imports | 🟢 | Keep as THE pattern; cite in every future cross-impl decision |
| 13 | `.workflows/` subject split | `agentx/` vs `meta_harness/` vs `app_knowledge_base/` already namespaces ops by system + stance line 1 per file | 🟢 | Keep; only fix `./sandbox/` output-path references (Phase 1.2) |
| 14 | `.meta/META_HARNESS.omt` single source + `harnessc check/build` | Deny/protect/gates/budgets/tools declared once, projected to `AGENTS.md`/`opencode.jsonc`/IR/nav-index, drift-tested | 🟢 | Keep; extend `harness_paths`/`root_allowlist` for new paths (Phase 1.6) |

## How this was verified

- Tree reads: `/`, `src/agentx/{agent,model,ui,utils}`, `scripts/omt/{net,tdd}`, `.meta/`, `.workflows/META.md`, `.projects/meta/`, `tools/petri-net-studio/`, `shared/META.md`, `tests/`, `tests/scripts/omt/`, `sandbox/`, `.sandbox/`, root files (`AGENTS.md`, `opencode.jsonc`, `pyproject.toml`, `README.md`, `GETTING_STARTED.md`, `.gitignore`).
- Content spot-reads: `src/agentx/main.py`, `.meta/META.md`, `.meta/META_HARNESS.md`, `.workflows/META.md`, `shared/META.md`, `.sandbox/meta_harness_refactor_plan.md` (§0–§3), `.meta/META_HARNESS.omt` header records.
- Deliberately NOT used: `omt_*` tools, `grep` over docs, `src/` edits, ledger writes (independent mode per request).
