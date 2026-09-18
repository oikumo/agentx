# 01 — Full inventory: what lives where, who it serves

> Source: direct tree reads 2026-09-18 (`/`, `src/`, `.meta/`, `scripts/omt/`, `.opencode/`, `.workflows/`, `.projects/`, `tools/`, `shared/`, `tests/`, `sandbox/`, `.sandbox/`, root files). No `omt_*` tools used.

## 1. Product — `agentx` runtime (ships to users)

| Path | What it is | Consumer |
|---|---|---|
| `src/agentx/main.py` | Console entry (`agentx.main:start`), dotenv override, provider boot | user |
| `src/agentx/agent/` | Intelligent/Fast agent: `adapter.py`, `interfaces.py`, `types.py`, `controller/{agent,demo,session,tool}_controller.py`, `demo/scenarios.py`, `model/{agent,ai_adapter,goal,memory,policy,reflection,tools}/`, `persistence/`, `view/` | user |
| `src/agentx/model/` | Feature models: `ai/`, `chat/`, `coding/`, `petri_net/`, `program/`, `rag/`, `rag_v2/`, `react/`, `session/` | user |
| `src/agentx/ui/` | Console UI: `providers.py`, `common/`, `interfaces/`, `screens/*` (main, chat, rag, agent, react, coding, models) | user |
| `src/agentx/utils/` | `constants.py`, `utils*.py` | user |
| `tools/petri-net-studio/` | Standalone TS workbench (`src/`, `scripts/`, `tests/` vitest, `index.html`, `dashboard.html`); engine parity with Python model | user |
| `shared/petri-net/` | **Contract only**: `FORMAT.md` (spec v1 + §8 canonical rules), `petri-net-json-v1.schema.json`, `examples/`, `conformance/` (planned). No code, no cross-imports | both impls |
| `tests/{controllers,model,views,unit}/`, `tests/features/feature_007*,010*,013*,015*,018*,019*,024*,025*,027*,029*` | Product feature + layer tests | dev/agent |
| `tests_automated/`, `test_sandbox/`, `local_sessions/` | Product runtime scratch / automated runs | dev |
| `pyproject.toml [project] agentx 0.2.0` | Runtime deps (langchain*, chroma, faiss, langgraph, deepagents…), `uv run agentx` entry | user |
| `README.md` (product chapters: console, chat, RAG, agents, ReAct, coding, models…) | User manual | user |

## 2. Harness — meta process control plane (constrains the agent)

| Path | What it is | Consumer |
|---|---|---|
| `.meta/META_HARNESS.omt` (319 lines on disk) | **Single source of truth** (OMT-HDL v1): `@var`, `@deny`, `@protect`, `@always`, `@phase`, `@fsm`, `@pred`, `@gate`, `@tool`, `@budget`, `@comp`, `@path` records | compiler |
| `scripts/omt/harnessc.py` | DSL compiler: `check` (schema/refs/budgets/lints) → `build` (projections). Owns `TIERS` table | agent/dev |
| Generated projections (never hand-edit) | `AGENTS.md`, `opencode.jsonc` harnessc blocks, `.meta/.omt/harness.ir.json`, `.meta/.omt/nav.index.jsonl` | agent runtime |
| `.opencode/plugins/` (7 TS) | `omt_enforcer.ts`, `omt_think.ts`, `omt_status.ts`, `omt_nav.ts`, `omt_net.ts`, `omt_q.ts`, `omt_kb_nav.ts` | opencode |
| `.opencode/lib/enforcer/` (12 TS) | `gate_driver.ts`, `phase_gate.ts`, `tdd_hats.ts`, `think_gate.ts`, `nav_gate.ts`, `receipt_guard.ts`, `mvc_after.ts`, `session_state.ts`, `preflight.ts`, `task_prep.ts`, `policy_decision.ts`, `lsp_filter.ts` | opencode |
| `scripts/omt/` engines | `tdd/` (`cli,state,gates,ast_checks`), `net/` (16 files: `cli,state,gate,model,managed_ops,sync_md,workspace,history,lock,…`), `mvc_check.py`, `new_feature.py`, `project.py`, `project_state.py`, `kb_compiler.py`, `kb_ast_extract.py`, `kb_pilot/`, `task_cost_benchmark.py`, `bench/` | agent/dev |
| `.meta/software_development_process/` | OMT++ store: `1.project/`…`7.integration/` + `omt_agent_guide.md` + per-dir `META.md`; per-feature dirs under `3.analysis/`, `4.design/`, `6.testing/` | agent |
| `.meta/templates/` | `analysis,current_state,design,feature,operation_spec,project,test_plan,use_case.md` scaffolds | agent |
| `.meta/doc/{harness,opencode_plugins,tdd}/` | Harness design docs | agent |
| `tests/scripts/omt/` (~60 files) + `tests/features/feature_016*,026*,039*–041*,043*,050*–103*,kb_akb` | Harness gate/engine/e2e/live tests + harness feature dirs | agent/dev |
| `.meta/.omt/*` (gitignored except 2 projections) | Local runtime state: `ledger.jsonl`, `thoughts.jsonl`, `omt_harness_e2e_last_run.json`, `tdd_snapshots/` | agent session |
| `.projects/meta/meta_harness_{2..10,concurrent}/`, `net_enforced_harness/` | Harness program homes (`PROJECT.md` + `CURRENT_STATE.md`) | agent |
| `.sandbox/meta/improvement00{1..7}/`, `.sandbox/meta_harness_*idea*.md`, `.sandbox/meta_harness_refactor_plan.md`, `.sandbox/pause_*.md`, `sandbox/meta/*`, `sandbox/META_HARNESS_*.md` | Harness audit/proposal/pause trail | agent |
| `.agents/`, `.agents_prompts/build.md`, `opencode.jsonc`, `.opencode/{package.json,bun.lock}` | Agent runtime wiring | opencode |
| `GETTING_STARTED.md` | Generated per-tier onboarding (`harnessc init --tier 3`); gitignored, present on disk | agent |

## 3. Transverse — sits above/beside both, must stay namespaced

| Path | What it is | Rule today |
|---|---|---|
| `.workflows/` | Ops catalog (markdown recipes, NOT a runtime): root `META.md` + subjects `agentx/` (2 loops), `meta_harness/` (2 loops + 1 one-shot), `app_knowledge_base/` (1 loop). Each file declares OMT stance in `# Rules` line 1 + mandatory approval gate | two-level read, no parser |
| `.projects/meta/` | Design homes for BOTH systems: product (`rag_v2`, `petri_net_studio`, `petri_net_library`, `project_lifecycle`, `agentx_concurrent_development`, `feature_kb_akb`, `workflows`) + harness (`meta_harness_*`, `net_enforced_harness`, `meta_harness_concurrent`) | `project.py sync` → `WORK.md ## Projects` |
| `WORK.md` | Single task pool (`net_rev`, pool places 12/15, `## Projects` synced table, `## Paused`, scratchpad) | machine-parseable |
| `.meta/doc/omt++/`, `.meta/doc/petri_nets/` | **Product** architecture docs (`architecture,features,subsystems,data_flow,persistence,extending.md` + `*.kb.omt` AKB sources) | co-located with harness docs above |
| `.sandbox/` vs `sandbox/` | TWO scratch roots: `.sandbox/` (actual: proposals, pauses, bench, frontier, global_state, work_contract) vs `sandbox/` (workflows-spec outputs: `consistency_enforcement/`, `meta/`, readiness docs) | ambiguous; workflows spec says `./sandbox/` |

## 4. Counts (order-of-magnitude, from this inspection)

- Product source: `src/agentx/` ≈ 6 areas (agent/model/ui/utils + main); studio TS app + `shared/petri-net` contract.
- Harness source: 7 plugins + 12 enforcer libs + ~16 net engine files + tdd package + ~10 top-level scripts + 319-line DSL + ~60 harness test files + 30+ harness feature dirs.
- Docs: `.meta/` (META + stub + SDP 7 phases + doc 5 areas + templates 8) + `.workflows/` (3 subjects, 6 workflows) + `.projects/meta/` (18 folders) + `.sandbox/` (50+ entries) + `sandbox/` (4 entries).
