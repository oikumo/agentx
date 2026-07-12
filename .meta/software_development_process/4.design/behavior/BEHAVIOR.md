# BEHAVIOR.md — Application Behavior (compressed)

**LIFECYCLE:**
```
STARTUP: load .env → prompt API key → detect TTY → select provider (TUI|Console)
         → create MainController + View → start main loop
SHUTDOWN: quit command / Ctrl+C / TUI exception → fallback to console
```

---

## 1. MAIN SCREEN

**STATE MACHINE:**
```
STARTED → WAITING → PARSING → EXECUTING → COMPLETED → WAITING
                              ↘ QUIT → EXIT
```

**COMMAND FLOW:**
`Input → CommandParser.parse() → CommandData(key,args) → MainController.run_command() → commands[key].run(args) → record history (SQLite)`

**COMMANDS:**
| Key | Action |
|-----|--------|
| help | List commands |
| quit | Exit app |
| clear | Clear screen |
| history | Show session history |
| sum a b | Add integers |
| chat | Launch chat screen |
| rag | Launch RAG screen |
| new [name] | Create/switch session |
| ls | List RAG repos |
| version | Show version |

---

## 2. CHAT SCREEN

**STATE MACHINE:**
```
STARTED → WAITING → PROCESSING → STREAMING → COMPLETED → WAITING
                            ↘ QUIT → EXIT
```

**MESSAGE FLOW:**
`User input → append HumanMessage → LLM stream → display chunks → append AIMessage → repeat`

---

## 3. RAG SCREEN

**STATE MACHINE:**
```
STARTED → SELECT_REPO | CREATE_REPO | QUIT
SELECT_REPO → REPO_READY
CREATE_REPO → REPO_CREATED
REPO_READY/REPO_CREATED → SUB_MENU {CHAT | INGEST | BACK}
```

**REPO OPS:**
| Op | Behavior |
|----|----------|
| Select | Browse existing, load chosen |
| Create | Wizard: name → location → init |
| Chat | RAG-enabled chat with repo |
| Ingest | Fetch URL → parse → chunk → vector store |

---

## 4. SESSION MANAGEMENT

**LIFECYCLE:**
```
NO_SESSION → new [name] → CREATING → ACTIVE
ACTIVE → new [name] → CREATING (replaces)
```

**PERSISTENCE:**
| Data | Storage | Lifetime |
|------|---------|----------|
| Command history | SQLite (session.db) | Per session |
| RAG repositories | FS (rag/) | Permanent |
| Vector embeddings | Chroma DB | Permanent |
| Ingested docs | FS | Permanent |

---

## 5. PROVIDER SELECTION

**RUNTIME:**
```
if --no-tui NOT passed AND TTY detected:
    → TUIProvider (Textual)
else:
    → ConsoleProvider (fallback)
```

**FALLBACK:**
```python
try: main_view.show()  # TUI
except: fallback to ConsoleProvider.create_main_view().show()
```

---

## 6. COMPONENT COLLABORATIONS

**CHAT:**
`User → ChatView → ChatController → AIService → LLM API → (stream) → AIService → ChatController → ChatView`

**RAG REPO SELECTION:**
`User → RagView → RagController → RepositorySelection → list → user selects → RagController → RagView`

---

## 7. ERROR HANDLING

| Error | Handling |
|-------|----------|
| KeyboardInterrupt | Graceful shutdown |
| ValueError (bad input) | Error msg, retry |
| ConnectionError (LLM) | Error msg, retry option |
| FileNotFoundError | Error msg |
| TUI exception | Fallback to console |

---

## 8. USER INTERACTION

**CONSOLE:**
```
(agentx) > chat
Welcome to Chat! Type 'quit' to exit.
You: Hello
Assistant: Hi there!
You: quit
(agentx) >
```

**TUI:**
```
┌─ AgentX TUI ────────────────────┐
│  [c] Chat  [r] RAG  [h] Help  [q] Quit
└─────────────────────────────────┘
Keys: q/c/r/h
```

---

## REFS
- Structure: `../structure/STRUCTURE.md`
- Feature designs: `./features/feature_*/design_*.md`
- OMT++ behavioral modeling: `../../omt_agent_guide.md §3, §7-9`