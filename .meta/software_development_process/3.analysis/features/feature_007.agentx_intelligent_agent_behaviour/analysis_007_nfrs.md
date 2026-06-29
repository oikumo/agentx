# Analysis 007: Non-Functional Requirements — feature_007.agentx_intelligent_agent_behaviour

> **Phase:** Analysis | **Artifact:** analysis_007_nfrs.md
> **Feature:** feature_007.agentx_intelligent_agent_behaviour | **Task:** A7

---

## Performance Requirements

### P1: Perception Cycle Latency
| Metric | Target | Measurement |
|--------|--------|-------------|
| Single sensor sense() call | < 50ms (p95) | Excluding I/O wait |
| Full perception cycle (all sensors) | < 200ms (p95) | 3-5 sensors typical |
| EnvironmentModel update | < 10ms | In-memory aggregation |
| PolicyEngine notification | < 5ms | Event dispatch |

**Rationale:** Agent must feel responsive. Perception runs periodically; user shouldn't notice pauses.

### P2: Decision Making Latency
| Metric | Target | Measurement |
|--------|--------|-------------|
| PolicyEngine.evaluate() | < 50ms (p95) | 100 rules typical |
| Goal selection | < 20ms | GoalTree traversal |
| Actuator validation | < 30ms | Schema validation |
| Total decide→act latency | < 150ms (p95) | Excluding actuator execution |

**Rationale:** Decision loop runs frequently; must not block perception cycle.

### P3: Action Execution
| Metric | Target | Measurement |
|--------|--------|-------------|
| ToolRegistry lookup | < 5ms | Dict lookup |
| Actuator.act() (filesystem) | < 100ms (p95) | Local FS ops |
| Actuator.act() (RAG query) | < 2s (p95) | Vector search + LLM |
| Actuator.act() (session) | < 50ms | DB operations |

**Rationale:** Actuator latency dominates; async where possible.

### P4: Reflection Engine
| Metric | Target | Measurement |
|--------|--------|-------------|
| Prompt construction | < 50ms | Template rendering |
| AIService.complete() | < 30s (p95) | Depends on model |
| Proposal parsing | < 100ms | JSON parsing |
| Safety evaluation | < 20ms | Rule checks |

**Rationale:** Reflection is periodic/async; user-facing latency only when reviewing proposals.

### P5: Memory Operations
| Metric | Target | Measurement |
|--------|--------|-------------|
| Volatile put/get | < 1ms | In-memory dict |
| Persistent store (write) | < 100ms (p95) | SQLite + embedding |
| Persistent query (semantic) | < 500ms (p95) | Vector index search |
| Consolidation batch (100 entries) | < 5s | Embedding generation |

**Rationale:** Volatile must be near-instant; persistent can be slower.

### P6: Persistence
| Metric | Target | Measurement |
|--------|--------|-------------|
| Session save (full snapshot) | < 2s (p95) | Transactional SQLite |
| Session load (full restore) | < 1s (p95) | SQLite reads |
| Incremental checkpoint | < 500ms | Dirty-only write |

**Rationale:** Save occurs periodically; must not block main loop.

---

## Scalability Requirements

### S1: Memory Growth
| Dimension | Limit | Enforcement |
|-----------|-------|-------------|
| Volatile entries per session | 10,000 | LRU eviction at capacity |
| Persistent entries per agent | 100,000 | TTL + importance-based archival |
| Reflection log entries | 10,000 | Rolling window (configurable) |
| Policy rules per agent | 1,000 | Hard limit (configurable) |
| Active goals per session | 10 | GoalConfig.maxActiveGoals |
| Goal tree depth | 5 | GoalConfig.maxDepth |

### S2: Concurrent Operations
| Scenario | Requirement |
|----------|-------------|
| Multiple sensors sensing concurrently | Thread-safe; no shared mutable state |
| Multiple reflection triggers | Queue; process sequentially |
| Session save during perception | Non-blocking; snapshot isolation |
| Tool registration at runtime | Lock-free read; write locks for registry |

### S3: Session Scale
| Metric | Target |
|--------|--------|
| Sessions per user | Unlimited (disk-bound) |
| Agent config size | < 1MB JSON |
| Session snapshot size | < 10MB typical |
| Startup time (resume) | < 3s cold, < 1s warm |

---

## Reliability Requirements

### R1: Data Integrity
| Requirement | Implementation |
|-------------|----------------|
| Session persistence atomicity | SQLite transactions (BEGIN/COMMIT) |
| Memory entry durability | WAL mode; fsync on commit |
| Policy rule versioning | Immutable rules; new version on change |
| Goal tree consistency | Parent-child references validated on load |
| Reflection log append-only | No updates; new entries only |

### R2: Fault Tolerance
| Failure Mode | Behavior |
|--------------|----------|
| Sensor sense() throws | Log error; use cached reading; continue cycle |
| Actuator act() throws | Store failure result; trigger re-planning; continue |
| AIService unavailable | Defer reflection; cache trace; retry on interval |
| SQLite corruption | Detect on load; offer recovery from backup |
| Config migration failure | Halt startup; show migration error; manual fix |

### R3: Recovery
| Scenario | RTO | RPO |
|----------|-----|-----|
| Process crash mid-cycle | < 5s (restart) | Last checkpoint (≤5min) |
| Disk full during persist | Graceful pause | No data loss (transaction rollback) |
| Invalid config on resume | Immediate (fallback to defaults) | User config preserved |
| Reflection proposal corrupts policy | Rejected at safety check | Policy unchanged |

---

## Security Requirements

### SEC1: Tool Sandboxing
| Requirement | Implementation |
|-------------|----------------|
| Filesystem actuator scope | Restricted to session working directory |
| Command execution actuator | Disabled by default; explicit enable |
| Network actuator | Not in v1; future: allowlist only |
| Tool parameter validation | JSON Schema validation on every call |

### SEC2: Policy Safety
| Requirement | Implementation |
|-------------|----------------|
| Reflection proposal evaluation | Safety rules: no file delete, no network, no config overwrite without confirmation |
| Autonomy level enforcement | CONFIRMATION_REQUIRED blocks high-risk actions |
| User override | Always available via PAUSED state |

### SEC3: Data Privacy
| Requirement | Implementation |
|-------------|----------------|
| Session data encryption | Optional: AES-256 at rest (configurable) |
| Memory content | User data never sent to AIService without explicit reflection trigger |
| AIService prompts | Sanitized: no secrets, paths relative to session dir |

---

## Usability Requirements

### U1: Observability
| Requirement | Target |
|-------------|--------|
| Decision reasoning visible | Every PolicyDecision includes `reasoning` string |
| Reflection critique readable | Critique.summary + strengths/weaknesses in plain language |
| Policy rule inspection | `"/policy list"` shows all rules with source/priority |
| Memory browse | Semantic search + temporal filter in TUI |
| Goal progress tracking | Real-time progress % in Agent Dashboard |

### U2: Controllability
| Requirement | Target |
|-------------|--------|
| Pause agent anytime | Single keystroke (Ctrl+P) → PAUSED state |
| Redirect agent | In PAUSED, user submits new goal or policy |
| Adjust autonomy | `"/autonomy <level>"` immediate effect |
| Disable tool | `"/tool disable <id>"` immediate effect |
| Reset agent identity | `"/agent reset"` → new AgentId, clean state |

### U3: Learnability
| Requirement | Target |
|-------------|--------|
| Built-in help | `"/help agent"` shows command reference |
| Tooltips in TUI | Hover keybindings show action |
| Example policies | Shipped with commented examples |
| Guided first run | Wizard on first session creation |

---

## Maintainability Requirements

### M1: Code Quality
| Metric | Target |
|--------|--------|
| MVC++ compliance | 0 errors from `mvc_check.py` |
| Test coverage | >80% branch coverage |
| Cyclomatic complexity | < 10 per method |
| God controller limit | < 300 lines per controller |

### M2: Extensibility
| Extension Point | Mechanism |
|-----------------|-----------|
| New sensor | Implement ISensor, register via ToolRegistry |
| New actuator | Implement IActuator, register via ToolRegistry |
| New policy action type | Extend ActionType enum + PolicyEngine handler |
| New memory tier | Extend MemoryTier enum + MemoryManager |
| New reflection proposal | Extend ProposalType + handlers |
| New AI provider | Implement IAIService |

### M3: Configuration
| Aspect | Approach |
|--------|----------|
| Agent config | YAML file + env var overrides |
| Tool parameters | Per-tool JSON Schema |
| Policy rules | JSON file (hot-reloadable) |
| Reflection prompts | Jinja2 template files |

---

## Compatibility Requirements

### C1: Existing Feature Integration
| Feature | Compatibility |
|---------|---------------|
| feature_004 (Modern UI) | New AgentTUIScreen + AgentAdapter; no breaking changes |
| feature_002 (RAG) | RagSensorTool wraps existing Rag.query() |
| feature_001 (Session Objectives) | IGoalManager interface; stub impl until 001 ready |
| feature_006 (Process Enforcement) | Agent code passes mvc_check.py |

### C2: Python Version
- **Minimum:** Python 3.11+
- **Target:** Python 3.12+

### C3: Dependencies
| Category | Constraint |
|----------|------------|
| Core | textual, pydantic, numpy (persistence via stdlib `sqlite3` — no SQLAlchemy/Alembic) |
| AI | Existing AIService providers (no new deps) |
| Vector | chromadb or faiss (configurable) |
| Testing | pytest, textual-pilot |

---

## Deployment Requirements

### D1: Installation
- Single `pip install agentx` (or `uv pip install`)
- No system dependencies beyond Python
- Optional: Ollama/LlamaCPP for local AI

### D2: Data Directory
- Default: `~/.agentx/`
- Configurable via `AGENTX_DATA_DIR` env var
- Structure:
  ```
  ~/.agentx/
  ├── agents/
  │   └── <agent_id>/
  │       ├── config.yaml
  │       ├── session_<id>.sqlite
  │       ├── memory/
  │       ├── policies.json
  │       └── reflections.jsonl
  └── global_config.yaml
  ```

---

## Traceability to FEATURE.md Success Criteria

| Success Criterion | NFR Reference |
|-------------------|---------------|
| Persistent identity across sessions | R1, R3, D2 |
| Perceive environment state | P1, S1 |
| Configurable policies | P2, SEC2, M2 |
| Goal-directed behavior | P2, S1, U2 |
| Memory system (volatile + persistent) | P5, S1, R1 |
| Tool integration | P3, SEC1, M2 |
| Observable decision-making | U1, P2 |

---

## Acceptance Test Scenarios (Non-Functional)

### AT-PERF-01: Perception Cycle Under Load
- **Setup:** 5 sensors, 1000 volatile entries, 50 policy rules
- **Action:** Trigger perception cycle
- **Assert:** Completes < 200ms p95

### AT-PERF-02: Decision Latency
- **Setup:** 100 policy rules, complex conditions
- **Action:** PolicyEngine.evaluate() with full context
- **Assert:** Returns < 50ms p95

### AT-PERF-03: Session Resume Time
- **Setup:** Session with 10k persistent memories, 500 reflections, 50 goals
- **Action:** resume_session()
- **Assert:** Ready < 3s cold, < 1s warm

### AT-REL-01: Sensor Failure Handling
- **Setup:** Filesystem sensor throws PermissionError
- **Action:** Perception cycle runs
- **Assert:** Cycle completes; error logged; cached reading used; other sensors unaffected

### AT-REL-02: Crash Recovery
- **Setup:** Agent running, kill -9 mid-cycle
- **Action:** Restart agent, resume session
- **Assert:** State restored to last checkpoint; no data corruption

### AT-SEC-01: Filesystem Sandbox
- **Setup:** Actuator command to write outside session dir
- **Action:** Actuator validation
- **Assert:** ValidationResult.valid = false; error explains sandbox violation

### AT-SEC-02: Reflection Proposal Safety
- **Setup:** Reflection proposes PolicyRule to delete files
- **Action:** Safety evaluation
- **Assert:** Proposal rejected; logged with rationale

### AT-USAB-01: Pause Responsiveness
- **Setup:** Agent in ACTING state (long filesystem op)
- **Action:** User presses Ctrl+P
- **Assert:** PAUSED state entered < 100ms; actuator receives interrupt

### AT-USAB-02: Autonomy Change Immediate
- **Setup:** Agent in DECIDING, autonomy=SUPERVISED
- **Action:** User runs `/autonomy CONFIRMATION_REQUIRED`
- **Assert:** Next decision requires confirmation

---

## Notes

- All latency targets are **p95** (95th percentile) under typical load
- "Typical load" = 3-5 sensors, 10-50 policy rules, 1-3 active goals
- Targets validated during Testing phase (T5: Performance tests)
- NFRs may be adjusted based on Implementation phase profiling
- Security requirements are **minimum baseline** — can be strengthened per deployment