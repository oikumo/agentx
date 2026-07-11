# AgentX Technical Documentation

> **Purpose:** A maintainable, code-accurate reference for the agentx
> application's features, architecture, subsystems, and extension points.
>
> **Audience:** developers and AI coding agents working on agentx.
>
> **Source of truth:** the code. This documentation *describes* the code as it
> exists; when code and doc disagree, the code wins — fix the doc.

---

## What this is

`agentx` is a terminal-based AI workbench: an interactive **Chat**, a **RAG**
(retrieval-augmented generation) knowledge base with web ingestion, a
**Session** manager that persists command history, and an **intelligent Agent**
subsystem that runs a perceive → decide → act → reflect cycle driven by goals,
policy rules, and tools. It runs as a rich **Textual TUI** (with a console
fallback) and is built on the **MVC++** architecture enforced by the **OMT++**
process.

---

## Documentation inventory

Each file maps to a concern so updates stay localised. **Update the file whose
topic changed** — see the "Update when" column.

| File | Covers | Update when |
|------|--------|-------------|
| [architecture.md](architecture.md) | MVC++ layers, dependency rules, provider/adapter pattern, tech stack, configuration & enforcement | the layering, provider pattern, or tech stack changes |
| [features.md](features.md) | Feature catalog — every feature, its status, summary, and key files | a feature is added, completed, or its scope changes |
| [subsystems.md](subsystems.md) | Deep dives: Agent, RAG, Session, AI, UI/Command, common components | a subsystem's internals change |
| [data_flow.md](data_flow.md) | Boot sequence, screen navigation, agent cycle, RAG ingestion/query, chat streaming | a runtime flow changes |
| [persistence.md](persistence.md) | The three SQLite DBs, their schemas, the no-ORM/DP convention, filesystem layout | a DB schema or persistence convention changes |
| [extending.md](extending.md) | How-to guides: add a command / screen / tool / feature + conventions checklist | the extension patterns or conventions change |

---

## How to maintain this documentation

1. **Keep it code-accurate.** Reference real file paths (e.g.
   `src/agentx/agent/model/agent.py`) rather than copying code — copied code
   goes stale silently; paths make drift obvious.
2. **Update on change.** When you touch a subsystem, update its section in
   `subsystems.md`. When you add a feature, add a row to `features.md` and an
   entry to `WORK.md`. The OMT++ process (`omt_phase`) is the natural trigger.
3. **Diagrams over prose for structure.** Use ASCII diagrams for layered
   architecture and flows; they render everywhere and diff cleanly.
4. **Don't duplicate.** Phase artifacts (analysis/design/impl/testing under
   `.meta/software_development_process/`) are the detailed historical record;
   this `doc/` set is the **current-state summary**. Link to phase artifacts for
   depth rather than restating them.
5. **Verify with tests.** The test suite (`tests/`) is the executable
   specification. If a doc claim is uncertain, check the corresponding test.

---

## Related documents (elsewhere in the repo)

| Document | Role |
|----------|------|
| `WORK.md` (root) | Active task roadmap — what's done, in progress, pending |
| `AGENTS.md` (root) | Agent behaviour rules + OMT++ enforcement summary |
| `README.md` (root) | User-facing project overview |
| `.meta/software_development_process/omt_agent_guide.md` | The OMT++ methodology (read before any coding task) |
| `.meta/software_development_process/4.design/structure/STRUCTURE.md` | Older structure overview (pre-agent) |
| `.meta/software_development_process/4.design/behavior/BEHAVIOR.md` | Older behaviour overview (pre-agent) |

> **Note:** `STRUCTURE.md` and `BEHAVIOR.md` (dated 2026-06-27) predate the
> agent subsystem (feature_007) and the demo screen (feature_010). This `doc/`
> set is the **current, comprehensive** reference and supersedes them for
> topics they don't cover.

---

## Quick orientation

```
agentx/
├── src/agentx/
│   ├── main.py                 # Entry point: provider select → MainController → show()
│   ├── model/                  # MODEL layer (no UI imports)
│   │   ├── ai/                 #   LLM providers + vectorstores (LangChain)
│   │   ├── rag/                #   RAG orchestrator + web ingestion + DP_Rag
│   │   ├── session/            #   Session entity + SessionManager + DP_Session
│   │   └── program/            #   (reserved)
│   ├── agent/                  # INTELLIGENT AGENT subsystem (MVC++ triad)
│   │   ├── model/              #   Agent facade, goals, policy, memory, reflection, tools
│   │   ├── controller/         #   AgentController, SessionController, ToolController
│   │   ├── view/               #   AgentView (console) + AgentTUIScreen + AgentDemoScreen
│   │   ├── persistence/        #   agent_session.db (sqlite3) + repositories
│   │   ├── demo/               #   Demo scenarios (feature_010)
│   │   ├── interfaces.py       #   8 Abstract Partners
│   │   └── types.py            #   38 enums + dataclasses
│   ├── ui/                     # VIEW + CONTROLLER layers
│   │   ├── interfaces.py       #   IMainView, IChatView, IRagView, IUIProvider, *Partner
│   │   ├── providers.py        #   ProviderRegistry + ConsoleProvider
│   │   ├── common/             #   UIConsole + 4 reusable input triads
│   │   ├── screens/            #   Screen MVC triads: main, chat, rag (+ commands/)
│   │   └── tui/                #   Textual implementation: app, provider, adapters, screens
│   └── utils/                  # Cross-cutting helpers (dirs, constants, input validation)
├── tests/                      # Unit + integration + Textual pilot e2e
├── scripts/omt/                # OMT++ tooling (mvc_check.py, new_feature.py)
├── .opencode/                  # Process enforcement plugin
└── .meta/                      # This documentation + OMT++ phase artifacts
```

Start reading at [architecture.md](architecture.md) for the big picture, then
[features.md](features.md) for what exists, then [subsystems.md](subsystems.md)
for how each part works.
