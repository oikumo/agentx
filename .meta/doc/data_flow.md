# Data Flow

> **Scope:** runtime sequences — boot, screen navigation, the agent cycle, RAG
> ingestion/query, chat streaming, session lifecycle, and the demo flow.
> **See also:** [subsystems.md](subsystems.md) for the components involved.

---

## 1. Boot sequence (`main.py`)

```
load_dotenv()
  └─ if OPENROUTER_API_KEY unset → prompt via getpass
main()
  ├─ show() — print "agentx <version>"
  ├─ use_tui = ("--no-tui" not in argv) and stdin.isatty() and stdout.isatty()
  ├─ provider = use_tui ? ProviderRegistry.get_default()   # TUIProvider
  │                          : ProviderRegistry.get("console")
  ├─ provider.initialize()
  ├─ main_controller = MainController(provider=provider)   # loads 10 commands
  ├─ main_view = provider.create_main_view(main_controller) # TUIAdapter | MainView
  ├─ main_controller.view = main_view
  └─ try: main_view.show()                                  # TUI: run TUIApplication
     except KeyboardInterrupt → "Interrupted by user"
     except Exception (TUI) → fallback to ConsoleProvider
     finally: provider.shutdown()
```

---

## 2. Screen navigation (TUI)

```
TUIApplication.on_mount → push MainTUIScreen
   │
   │  c / "chat"      → action_open_chat  → controller.show_chat()
   │                                            + push ChatTUIScreen
   │                                            + TUIChatAdapter.set_screen(...)
   │
   │  r / "rag"       → action_open_rag   → controller.show_rag()
   │                                            + push RagTUIScreen
   │                                            + TUIRagAdapter.set_screen(...)
   │
   │  a               → action_open_agent → controller.show_agent()
   │                                            (AgentAdapter.create_agent, resume=True)
   │                                            + push AgentTUIScreen(controller)
   │
   │  typed input     → on_input_submitted → controller.run_command(text)
   │                                            → CommandParser → Command.run()
   │
   └─ escape/q        → pop_screen / quit
```

**Agent screen → demo:** from `AgentTUIScreen`, `d` / `demo [a|b]` →
`action_open_demo(name)` → `app.push_screen(AgentDemoScreen(controller, name))`.

> **Dual-path navigation:** `MainTUIScreen.action_open_*()` pushes the Textual
> screen directly (navigation) AND calls `controller.show_*()` (wiring side
> effects). This was the fix for TUI navigation freezes (see `WORK.md`).

---

## 3. Agent cycle (`Agent.run_cycle`)

```
perceive()                         ── PERCEIVING
  └─ for each enabled sensor: sensor.sense() → SensorReading
       store perception in volatile memory ({"sensor": sid, "data": ...})
     environment_model = readings → confidence = mean(confidences)
decide()                           ── DECIDING
  └─ ctx = PolicyContext(environment, memory(recent), active_goal, state, autonomy)
     PolicyEngine.evaluate(ctx) → PolicyDecision (selected_action + confidence + reasoning)
command = _decision_to_command(decision)   # EXECUTE_TOOL → ActuatorCommand
  └─ tool_id = params["tool_id"]; action = params["action"]
     parameters = params minus {tool_id, action}
act(command)                       ── ACTING
  └─ ToolRegistry.execute_safely(command) → ActuatorResult
     store action result in memory ({"actuator", "action", "success", "error"})
     if success and active goal's success_criteria matches → complete goal (C6)
reflect(trace, ctx)                ── REFLECTING  (only if AI service wired, N11)
  └─ ReflectionEngine.reflect() → ReflectionEntry (critique + proposals)
     persist ReflectionEntry (refl_repo)
     proposals stay PENDING until approved (N4)
state → PERCEIVING
return CycleResult(perception, decision, action_result, reflection)
```

**Key invariants:**
- A single command is built once (N2) — executed action and traced action share
  a `correlation_id`.
- Goal completion is scoped by `SuccessCriteria.tool_id` (C6): only the acting
  tool that matches (or `None` = any) satisfies the goal.
- Reflection is skipped entirely without an AI service (N11).

---

## 4. Demo flow (feature_010)

```
AgentTUIScreen: d / "demo [a|b]"
  └─ action_open_demo(name) → push AgentDemoScreen(controller, name)

AgentDemoScreen.on_mount()
  └─ controller.load_demo_scenario_by_name(name)
       ├─ agent.clear_state()              # clear goals/rules/volatile memory
       ├─ seed_sandbox_files(scenario, sandbox_root)   # write target.txt/notes.txt
       ├─ controller.submit_goal(...)       # scenario goal (ACTIVE)
       └─ controller.update_policy(...)     # scenario rules
  └─ refresh (render scenario summary + status)
  └─ action_run_cycle()                    # auto-run 1 cycle, narrate

Run Cycle (r)   → controller.run_cycle() → render decide/act/reflect in log
Reset (x)       → controller.load_demo_scenario_by_name(current)  # clear + re-seed
Back (Escape)   → app.pop_screen() → back to AgentTUIScreen
```

**Scenario A** (File Reader): `goal.active → filesystem read target.txt` → goal
completes in one cycle.

**Scenario B** (Knowledge Assistant):
- cycle 1: `goal.active → read notes.txt` (goal completes)
- cycle 2: `memory_contains("notes.txt") AND NOT memory_contains("summary.txt") → create summary.txt`
- cycle 3: `summary.txt` now in perception → rule 2 condition false → idle

---

## 5. Chat flow (streaming)

```
User types message
  └─ ChatTUIScreen → ChatController.process_user_message(msg)
       ├─ append HumanMessage to history
       ├─ for chunk in get_streaming_response(llm, history):
       │     view.show_partial_message(chunk)   # stream into growing widget
       ├─ append AIMessage to history
       └─ view.show_stream_message(final)
  └─ repeat until user types quit/exit (Escape pops back to Main)
```

`ChatController` builds `AIService().openrouter_llm_provider().create_llm()` in
its constructor. `_extract_chunk_content` handles list/None LLM chunk content.

---

## 6. RAG ingestion flow

```
RagTUIScreen: Ingest button / "i"
  └─ RagWebIngestionController → InputUrlController (URL) + InputOptionsController (level)
       └─ Rag.web_ingestion(extract_level: Low|Mid|High)
            ├─ RagDatabase.insert_ingestion_entry(info)         # rag.db
            ├─ vectorstore = AIService.rag_chromadb(directory)
            ├─ WebExtract(max_depth, max_breadth, max_pages)     # TavilyMap + TavilyExtract
            ├─ WebIngestionApp.run(site_url, jsonl_path)
            │     ├─ data_ingestion()    # crawl map
            │     ├─ save_docs()         # JSONL
            │     ├─ process_documents() # RecursiveCharacterTextSplitter(4000, 200)
            │     └─ index_documents_async()  # concurrent aadd_documents → Chroma
            └─ return True/False
```

---

## 7. RAG query flow

```
RagTUIScreen: question input
  └─ RagChatController → Rag.query(prompt, history: RagChatHistory)
       └─ RagQuery.ask(prompt, history)
            ├─ retriever = create_history_aware_retriever(llm, vectorstore.as_retriever(), prompt)
            ├─ chain = create_retrieval_chain(
            │              create_history_aware_retriever(...),
            │              create_stuff_documents_chain(llm, RagChatPrompts.create_rag_template())
            │            )
            ├─ result = chain.invoke({"input": prompt, "chat_history": history})
            ├─ append answer + sources
            └─ return RagChatHistory (answers + prompts + chat history)
```

---

## 8. Session lifecycle

```
no session (default "current" dir under local_sessions/)
  └─ "new [name]" → NewSessionCommand
       └─ SessionManager.create_new_session()
            ├─ backup current → current_backup_<timestamp>
            └─ create timestamped dir + init SessionDatabase (session.db)

each run_command:
  └─ session_controller.insert_history_entry(key)   # recorded in session.db history table
```

Sessions are the working directory root: RAG repos live under
`<session>/rag/`, and the agent's persistence (`agent_session.db`) lives in the
session dir (or `.` if no session).

---

## 9. Agent persistence flow

```
Agent.persist()                     ── PERSISTING
  └─ SessionSnapshot(snapshot_id, agent_id, config_version,
       volatility_data = {state, config (N7), volatile_memory (N1)},
       policy_store = [rules],
       goal_tree = {root},
       reflection_log_position = len(log))
  └─ SessionDatabase.save_snapshot_with_retry(snapshot)
  └─ state → PERCEIVING

Agent.resume_session(snapshot_id)   ── rebuild
  └─ clear pre-existing in-memory state (N9)
     restore config (N7), policy (repo-first, N3), goal tree (honour root, N8),
     volatile memory (N1), reflection log (M2), re-register tools (C1)
     state → PERCEIVING
     (AI service is non-serialisable — caller re-injects via set_ai_service, C3)
```

`AgentAdapter.create_agent(resume=True)` resumes the latest snapshot on open
(C5/I1) so agent state survives a close/reopen.
