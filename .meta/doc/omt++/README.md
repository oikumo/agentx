# doc/omt++ — AgentX Technical Documentation (grep-friendly)

> **Purpose**: Maintainable, code-accurate reference for agentx features, architecture, subsystems, and extension points.
> **Audience**: Developers and AI coding agents working on agentx.
> **Source of truth**: The code. Docs describe code as it exists; when code and doc disagree, code wins — fix the doc.

---

# SECTION:INVENTORY — Documentation Inventory (grep:INV_)
| File | Covers | Update When |
|------|--------|-------------|
| `architecture.md` | MVC++ layers, dependency rules, provider/adapter pattern, tech stack, configuration & enforcement | layering, provider pattern, or tech stack changes |
| `features.md` | Feature catalog — every feature, its status, summary, and key files | feature added, completed, or scope changes |
| `subsystems.md` | Deep dives: Agent, RAG, Session, AI, UI/Command, common components | subsystem internals change |
| `data_flow.md` | Boot sequence, screen navigation, agent cycle, RAG ingestion/query, chat streaming | runtime flow changes |
| `persistence.md` | Three SQLite DBs, schemas, no-ORM/DP convention, filesystem layout | DB schema or persistence convention changes |
| `extending.md` | How-to guides: add command/screen/tool/feature + conventions checklist | extension patterns or conventions change |

---

# SECTION:ARCH — Application Overview (grep:ARCH_)
`agentx` = terminal AI workbench: interactive **Chat**, **RAG** (retrieval-augmented generation) with web ingestion, **Session** manager persisting command history, **intelligent Agent** subsystem running perceive→decide→act→reflect cycle driven by goals, policy rules, tools. Runs as rich **Textual TUI** (console fallback). Built on **MVC++** architecture enforced by **OMT++** process.

---

# SECTION:MAINT — Maintenance Rules (grep:MAINT_)
1. **Code-accurate** — Reference real file paths (e.g., `src/agentx/agent/model/agent.py`), not copied code. Paths make drift obvious.
2. **Update on change** — Touch subsystem → update its `subsystems.md` section. Add feature → add row to `features.md` + entry to `WORK.md`. `omt_phase` is the natural trigger.
3. **Diagrams over prose** — ASCII diagrams for layered architecture and flows (render everywhere, diff cleanly).
4. **Don't duplicate** — Phase artifacts (analysis/design/impl/testing under `.meta/software_development_process/`) are detailed historical record; this `doc/` set is **current-state summary**. Link to phase artifacts for depth.
5. **Verify with tests** — Test suite (`tests/`) is executable specification. Uncertain doc claim → check corresponding test.

---

# SECTION:RELATED — Related Documents (grep:REL_)
| Document | Role |
|----------|------|
| `WORK.md` (root) | Active task roadmap — done, in progress, pending |
| `AGENTS.md` (root) | Agent behavior rules + OMT++ enforcement summary |
| `README.md` (root) | User-facing project overview |
| `.meta/software_development_process/omt_agent_guide.md` | OMT++ methodology (read before any coding task) |
| `.meta/software_development_process/4.design/structure/STRUCTURE.md` | Older structure overview (pre-agent) |
| `.meta/software_development_process/4.design/behavior/BEHAVIOR.md` | Older behavior overview (pre-agent) |

> **Note**: `STRUCTURE.md` and `BEHAVIOR.md` (2026-06-27) predate agent subsystem (feature_007) and demo screen (feature_010). This `doc/` set is **current, comprehensive** reference and supersedes them.

---

# SECTION:ORIENT — Quick Orientation (grep:ORIENT_)
```
agentx/
├── src/agentx/
│   ├── main.py                 # Entry: provider select → MainController → show()
│   ├── model/                  # MODEL (no UI imports)
│   │   ├── ai/                 # LLM providers + vectorstores (LangChain)
│   │   ├── rag/                # RAG orchestrator + web ingestion + DP_Rag
│   │   ├── session/            # Session entity + SessionManager + DP_Session
│   │   └── program/            # (reserved)
│   ├── agent/                  # INTELLIGENT AGENT (MVC++ triad)
│   │   ├── model/              # Agent facade, goals, policy, memory, reflection, tools
│   │   ├── controller/         # AgentController, SessionController, ToolController
│   │   ├── view/               # AgentView (console) + AgentTUIScreen + AgentDemoScreen
│   │   ├── persistence/        # agent_session.db (sqlite3) + repositories
│   │   ├── demo/               # Demo scenarios (feature_010)
│   │   ├── interfaces.py       # 8 Abstract Partners
│   │   └── types.py            # 38 enums + dataclasses
│   ├── ui/                     # VIEW + CONTROLLER
│   │   ├── interfaces.py       # IMainView, IChatView, IRagView, IUIProvider, *Partner
│   │   ├── providers.py        # ProviderRegistry + ConsoleProvider
│   │   ├── common/             # UIConsole + 4 reusable input triads
│   │   ├── screens/            # Screen MVC triads: main, chat, rag (+ commands/)
│   │   └── tui/                # Textual: app, provider, adapters, screens
│   └── utils/                  # Cross-cutting helpers (dirs, constants, input validation)
├── tests/                      # Unit + integration + Textual pilot e2e
├── scripts/omt/                # OMT++ tooling (mvc_check.py, new_feature.py)
├── .opencode/                  # Process enforcement plugin
└── .meta/                      # Documentation + OMT++ phase artifacts
```

**Reading order**: `architecture.md` → `features.md` → `subsystems.md`

---

# SECTION:XREF — Cross-References (grep:XREF_)
XREF_HARNESS: `.meta/META_HARNESS.md` — SECTION:RULES, SECTION:TDD, SECTION:ERRORS, SECTION:CMDS
XREF_GUIDE: `omt_agent_guide.md` — §5(MVC++), §6(Partner), §7(Screen), §8(Command), §9(Model), §11(Testing)
XREF_SDP: `.meta/software_development_process/` — phase artifacts (historical record)
XREF_ROOT: `WORK.md`, `AGENTS.md`