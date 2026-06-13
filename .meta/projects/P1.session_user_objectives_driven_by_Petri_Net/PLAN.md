# AgentX User Objectives - Implementation Plan

> **Project:** Internal State Management with Adaptive Petri Nets  
> **Status:** Planning Phase  
> **Created:** 2026-06-07  
> **OMT++ Phase:** Analysis → Design → Programming → Testing

---

## 1. Project Overview

### 1.1 Purpose
Implement an internal state management system for AgentX using adaptive Petri Nets to handle concurrent state transitions in a structured, verifiable way.

### 1.2 Scope
- **Module:** `src/agentx/model/internal_state`
- **Input Source:** `local_sessions/current/USER_OBJECTIVES.md`
- **Trigger:** CRC change detection on input file
- **Core Concept:** Adaptive Petri Net for concurrent state management

### 1.3 Key Requirements (from PROJECT.md)
1. ✅ Internal state with **context**, **sensors**, and **actuators**
2. ✅ **Adaptive Petri Net** for concurrent state handling
3. ✅ Single module implementation: `src/agentx/model/internal_state`
4. ✅ Input stored in: `local_sessions/current/USER_OBJECTIVES.md`
5. ✅ Auto-update on CRC change detection

---

## 2. Feasibility Study

### 2.1 Requirements Understanding
| Question | Answer |
|----------|--------|
| Do I understand the requirements? | ✅ Yes - Petri Net-based state management with CRC-triggered updates |
| Is the scope clear? | ✅ Yes - Single module, defined input location, clear trigger mechanism |
| Do I know the files affected? | ⚠️ Partially - Need to create new module, may need to integrate with existing session management |
| What's the risk level? | 🟡 **Medium-High** - New architecture pattern (Petri Nets), concurrent state management complexity |

### 2.2 Effort Estimate
| Phase | Estimated Time |
|-------|----------------|
| Analysis | 2-3 hours |
| Design | 3-4 hours |
| Programming | 8-12 hours |
| Testing | 4-6 hours |
| **Total** | **17-25 hours** |

### 2.3 Dependencies
- ✅ Python 3.14+ (available)
- ✅ Existing session infrastructure (`src/agentx/model/session/`)
- ⚠️ Petri Net library (needs research: `petri-net`, `petrinet`, or custom implementation)
- ⚠️ CRC calculation utility (may need to implement or use `hashlib`)

### 2.4 Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|------------|
| Petri Net complexity | High | Start with simple implementation, add adaptivity incrementally |
| Concurrent state conflicts | High | Use thread-safe data structures, proper locking |
| CRC change detection performance | Medium | Implement efficient file watching, debounce rapid changes |
| Integration with existing RAG | Medium | Design clear interfaces, use Abstract Partner pattern |

---

## 3. Analysis Phase Artifacts

### 3.1 Use Cases

#### UC-01: Initialize Internal State
- **Actor:** System (on startup)
- **Precondition:** `USER_OBJECTIVES.md` exists
- **Flow:**
  1. System reads `USER_OBJECTIVES.md`
  2. Calculate initial CRC
  3. Parse Petri Net structure from file content
  4. Initialize InternalState module with Petri Net
  5. Store CRC for change detection
- **Postcondition:** Internal State is initialized and ready

#### UC-02: Detect CRC Change
- **Actor:** File System Watcher / Polling Mechanism
- **Precondition:** Internal State is initialized
- **Flow:**
  1. Periodically check `USER_OBJECTIVES.md` CRC
  2. Compare with stored CRC
  3. If different → trigger update (UC-03)
  4. If same → no action
- **Postcondition:** Change detected or confirmed unchanged

#### UC-03: Update Petri Net on CRC Change
- **Actor:** InternalState Module
- **Precondition:** CRC change detected
- **Flow:**
  1. Read new `USER_OBJECTIVES.md` content
  2. Parse new Petri Net structure
  3. Validate Petri Net consistency
  4. Transition to new Petri Net (adaptive update)
  5. Update stored CRC
  6. Notify observers of state change
- **Postcondition:** Petri Net updated, observers notified

#### UC-04: Query Internal State
- **Actor:** Controller / Other Modules
- **Precondition:** Internal State is initialized
- **Flow:**
  1. Request state information (context, sensors, actuators)
  2. InternalState queries Petri Net current marking
  3. Return structured state data
- **Postcondition:** State information returned

#### UC-05: Fire Transition (State Change)
- **Actor:** InternalState Module (triggered by sensors/actuators)
- **Precondition:** Valid transition exists in Petri Net
- **Flow:**
  1. Evaluate transition conditions (sensors)
  2. If enabled → fire transition
  3. Update Petri Net marking
  4. Execute associated actions (actuators)
  5. Notify observers
- **Postcondition:** State transitioned, actions executed

### 3.2 Domain Concepts

| Concept | Description | Responsibility |
|---------|-------------|----------------|
| **InternalState** | Main module class | Manages Petri Net, CRC, state queries |
| **PetriNet** | Petri Net structure | Places, transitions, arcs, markings |
| **AdaptiveEngine** | Adaptivity logic | Handles Petri Net updates on CRC change |
| **CRCWatcher** | Change detection | Monitors file CRC, triggers updates |
| **Context** | State context | Current situation/environment data |
| **Sensor** | Input detectors | Read external/internal conditions |
| **Actuator** | Output executors | Execute actions based on state |
| **Transition** | State change rule | Conditions + actions for state transitions |

### 3.3 Analysis Class Diagram (Conceptual)

```
┌─────────────────────┐       ┌─────────────────────┐
│   InternalState     │──────▶│   AdaptiveEngine    │
├─────────────────────┤       ├─────────────────────┤
│ - petri_net         │       │ - update_net()      │
│ - crc_watcher       │       │ - validate_net()    │
│ - context           │       └─────────────────────┘
│ - sensors[]         │                ▲
│ - actuators[]       │                │
├─────────────────────┤       ┌─────────────────────┐
│ + initialize()      │──────▶│     PetriNet        │
│ + query_state()     │       ├─────────────────────┤
│ + fire_transition() │       │ - places{}          │
│ + get_context()     │       │ - transitions{}     │
└─────────────────────┘       │ - arcs[]            │
           │                  │ - marking{}         │
           │                  ├─────────────────────┤
           │                  │ + enable_transition()│
           │                  │ + fire()            │
           │                  │ + get_marking()     │
           │                  └─────────────────────┘
           │
           │                  ┌─────────────────────┐
           └─────────────────▶│    CRCWatcher       │
                              ├─────────────────────┤
                              │ - current_crc       │
                              │ - file_path         │
                              ├─────────────────────┤
                              │ + check_crc()       │
                              │ + get_crc()         │
                              └─────────────────────┘
```

---

## 4. Design Phase Artifacts

### 4.1 Module Structure

```
src/agentx/model/internal_state/
├── __init__.py                    # Package exports
├── internal_state.py              # Main InternalState class (MVC++ Model)
├── petri_net/
│   ├── __init__.py
│   ├── petri_net.py               # Core Petri Net implementation
│   ├── place.py                   # Place class
│   ├── transition.py              # Transition class with conditions/actions
│   ├── arc.py                     # Arc class (input/output)
│   └── marking.py                 # Current marking state
├── adaptive/
│   ├── __init__.py
│   ├── adaptive_engine.py         # Adaptivity logic
│   └── net_parser.py              # Parse Petri Net from USER_OBJECTIVES.md
├── monitoring/
│   ├── __init__.py
│   ├── crc_watcher.py             # CRC change detection
│   └── file_observer.py           # File system observer (optional)
├── components/
│   ├── __init__.py
│   ├── context.py                 # State context
│   ├── sensor.py                  # Sensor ABC + implementations
│   └── actuator.py                # Actuator ABC + implementations
└── utils/
    ├── __init__.py
    └── crc_utils.py               # CRC calculation utilities
```

### 4.2 Interface Definitions (Abstract Partners)

#### ISensor (ABC)
```python
class ISensor(ABC):
    @abstractmethod
    def read(self) -> Any:
        """Read sensor value."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return sensor name."""
        pass
```

#### IActuator (ABC)
```python
class IActuator(ABC):
    @abstractmethod
    def execute(self, action_data: Any) -> None:
        """Execute action."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return actuator name."""
        pass
```

### 4.3 Petri Net File Format (USER_OBJECTIVES.md)

Proposed YAML-based format:

```yaml
# USER_OBJECTIVES.md - Petri Net Definition
metadata:
  version: "1.0"
  description: "AgentX Internal State Petri Net"

places:
  - id: "idle"
    initial_marking: 1
    description: "System is idle"
  - id: "processing"
    initial_marking: 0
    description: "Processing user request"
  - id: "waiting"
    initial_marking: 0
    description: "Waiting for external input"

transitions:
  - id: "start_processing"
    guard: "sensor.has_request()"
    actions:
      - "actuator.log('Processing started')"
    input_places: ["idle"]
    output_places: ["processing"]
  
  - id: "complete_processing"
    guard: "sensor.is_complete()"
    actions:
      - "actuator.send_response()"
    input_places: ["processing"]
    output_places: ["idle"]
```

### 4.4 Component Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                        InternalState Module                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │   Context    │    │   Sensors    │    │  Actuators   │           │
│  │  (context.py)│    │ (sensor.py)  │    │ (actuator.py)│           │
│  └──────────────┘    └──────────────┘    └──────────────┘           │
│         │                   │                    │                    │
│         └───────────────────┼────────────────────┘                    │
│                             │                                         │
│                      ┌──────▼──────┐                                  │
│                      │InternalState│                                  │
│                      │  (main)     │                                  │
│                      └──────┬──────┘                                  │
│                             │                                         │
│         ┌───────────────────┼────────────────────┐                    │
│         │                   │                    │                    │
│  ┌──────▼──────┐    ┌──────▼──────┐    ┌──────────────┐              │
│  │  PetriNet   │    │  Adaptive   │    │   CRC        │              │
│  │   (core)    │    │   Engine    │    │   Watcher    │              │
│  └─────────────┘    └─────────────┘    └──────────────┘              │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  local_sessions/current/      │
              │  USER_OBJECTIVES.md           │
              └───────────────────────────────┘
```

### 4.5 Sequence Diagram: CRC Change → Petri Net Update

```
FileObserver  CRCWatcher  InternalState  AdaptiveEngine  PetriNet
     │            │            │               │             │
     │─check─────▶│            │               │             │
     │            │─calc_crc──▶│               │             │
     │            │◀─changed───│               │             │
     │            │            │─parse────────▶│             │
     │            │            │               │─validate───▶│
     │            │            │               │◀─valid──────│
     │            │            │◀─new_net──────│             │
     │            │            │─update─────────────────────▶│
     │            │            │◀─updated────────────────────│
     │            │            │─notify_observers           │
     │            │            │                             │
```

---

## 5. Programming Phase Plan

### 5.1 Implementation Order (MVC++ Compliant)

**Priority:** Model first → then integration → then testing

#### Sprint 1: Core Petri Net (4-6 hours)
1. `petri_net/place.py` - Place class
2. `petri_net/transition.py` - Transition with guards/actions
3. `petri_net/arc.py` - Arc class
4. `petri_net/marking.py` - Marking management
5. `petri_net/petri_net.py` - Core Petri Net engine
6. Unit tests for Petri Net components

#### Sprint 2: Monitoring & Adaptivity (4-6 hours)
1. `utils/crc_utils.py` - CRC calculation
2. `monitoring/crc_watcher.py` - CRC change detection
3. `adaptive/net_parser.py` - Parse YAML to Petri Net
4. `adaptive/adaptive_engine.py` - Update logic
5. Unit tests for monitoring and adaptivity

#### Sprint 3: Components & Integration (4-6 hours)
1. `components/context.py` - Context management
2. `components/sensor.py` - Sensor ABC + examples
3. `components/actuator.py` - Actuator ABC + examples
4. `internal_state.py` - Main InternalState class
5. Integration tests

#### Sprint 4: Testing & Validation (4-6 hours)
1. System tests (full workflow)
2. Performance tests (CRC polling frequency)
3. Edge case tests (concurrent updates, invalid YAML)
4. Documentation

### 5.2 File Creation Checklist

- [ ] `src/agentx/model/internal_state/__init__.py`
- [ ] `src/agentx/model/internal_state/internal_state.py`
- [ ] `src/agentx/model/internal_state/petri_net/__init__.py`
- [ ] `src/agentx/model/internal_state/petri_net/place.py`
- [ ] `src/agentx/model/internal_state/petri_net/transition.py`
- [ ] `src/agentx/model/internal_state/petri_net/arc.py`
- [ ] `src/agentx/model/internal_state/petri_net/marking.py`
- [ ] `src/agentx/model/internal_state/petri_net/petri_net.py`
- [ ] `src/agentx/model/internal_state/adaptive/__init__.py`
- [ ] `src/agentx/model/internal_state/adaptive/adaptive_engine.py`
- [ ] `src/agentx/model/internal_state/adaptive/net_parser.py`
- [ ] `src/agentx/model/internal_state/monitoring/__init__.py`
- [ ] `src/agentx/model/internal_state/monitoring/crc_watcher.py`
- [ ] `src/agentx/model/internal_state/monitoring/file_observer.py`
- [ ] `src/agentx/model/internal_state/components/__init__.py`
- [ ] `src/agentx/model/internal_state/components/context.py`
- [ ] `src/agentx/model/internal_state/components/sensor.py`
- [ ] `src/agentx/model/internal_state/components/actuator.py`
- [ ] `src/agentx/model/internal_state/utils/__init__.py`
- [ ] `src/agentx/model/internal_state/utils/crc_utils.py`

### 5.3 Test Files

- [ ] `tests/unit/internal_state/test_petri_net.py`
- [ ] `tests/unit/internal_state/test_adaptive_engine.py`
- [ ] `tests/unit/internal_state/test_crc_watcher.py`
- [ ] `tests/unit/internal_state/test_components.py`
- [ ] `tests/integration/internal_state/test_internal_state_integration.py`
- [ ] `tests/system/internal_state/test_full_workflow.py`

---

## 6. Testing Strategy

### 6.1 Unit Tests (Layer 1)
- **Petri Net:** Place/Transition/Arc creation, firing logic, marking updates
- **CRC Watcher:** CRC calculation, change detection, file reading
- **Components:** Sensor read, Actuator execute, Context management
- **Adaptive Engine:** Net parsing, validation, update logic

### 6.2 Integration Tests (Layer 2)
- **InternalState + PetriNet:** State queries, transition firing
- **InternalState + CRCWatcher:** Automatic updates on file change
- **InternalState + Components:** Sensor-triggered transitions, actuator execution

### 6.3 System Tests (Layer 3)
- **Full Workflow:** File change → CRC detection → Net update → State transition
- **Concurrency:** Multiple simultaneous transitions
- **Error Handling:** Invalid YAML, missing files, malformed Petri Nets

### 6.4 Test Coverage Goals
| Component | Minimum Coverage |
|-----------|------------------|
| Petri Net core | 90% |
| Adaptive Engine | 85% |
| CRC Watcher | 95% |
| Components | 80% |
| InternalState | 85% |
| **Overall** | **≥85%** |

---

## 7. Integration Points

### 7.1 With Existing Modules

| Module | Integration Point | Type |
|--------|-------------------|------|
| `session/` | Access to session context | Model → Model |
| `rag/` | Potential state-based RAG queries | Future extension |
| `ui/` | State display (future View layer) | Future extension |

### 7.2 Extension Points

1. **Custom Sensors:** Extend `ISensor` ABC for domain-specific sensors
2. **Custom Actuators:** Extend `IActuator` ABC for domain-specific actions
3. **Petri Net Formats:** Extend `net_parser.py` for alternative formats (JSON, XML)
4. **Persistence:** Add database backing for Petri Net state (future)

---

## 8. Risks & Open Questions

### 8.1 Technical Risks
- ⚠️ **Petri Net Library:** Should we use existing library or custom implementation?
  - **Recommendation:** Custom implementation for full control and adaptivity
- ⚠️ **Concurrency:** Thread safety for concurrent transitions
  - **Mitigation:** Use `threading.Lock`, queue-based transition firing
- ⚠️ **Performance:** CRC polling frequency vs. CPU usage
  - **Mitigation:** Configurable polling interval, consider `watchdog` library

### 8.2 Open Questions
1. **File Format:** YAML vs. JSON vs. custom DSL for Petri Net definition?
2. **Adaptivity Scope:** What changes are allowed during runtime? (Only markings? Structure?)
3. **Persistence:** Should Petri Net state survive restarts?
4. **Visualization:** Need graphical Petri Net viewer for debugging?

---

## 9. Definition of Done

### 9.1 Functional Requirements
- [ ] InternalState module created at `src/agentx/model/internal_state`
- [ ] Petri Net loads from `USER_OBJECTIVES.md`
- [ ] CRC change detection works automatically
- [ ] Petri Net updates adaptively on CRC change
- [ ] Sensors can trigger transitions
- [ ] Actuators execute on transition firing
- [ ] Context is accessible to external modules

### 9.2 Non-Functional Requirements
- [ ] All unit tests pass (≥85% coverage)
- [ ] Integration tests pass
- [ ] System tests pass
- [ ] No circular dependencies
- [ ] Follows MVC++ architecture
- [ ] Uses Abstract Partner pattern for components
- [ ] Thread-safe for concurrent transitions

### 9.3 Documentation
- [ ] Module docstrings complete (Google style)
- [ ] Petri Net file format documented
- [ ] Example `USER_OBJECTIVES.md` provided
- [ ] Usage examples in module README
- [ ] Architecture decisions documented (this PLAN.md)
- [ ] Concurrency strategy documented
- [ ] Integration guide for Session module

---

## 10. Timeline & Milestones (Updated) (Updated)

| Milestone | Target Date | Deliverables | Status |
|-----------|-------------|--------------|--------|
| **M1: Analysis Complete** | Day 1 | Use cases, domain model, class diagram | ✅ Done |
| **M2: Design Complete** | Day 2-3 | Module structure, interfaces, sequence diagrams, concurrency strategy | ✅ Done |
| **M3: Core Implementation** | Day 4-7 | Petri Net + ConcurrencyManager + CRC Watcher + Adaptive Engine | ⏳ Pending |
| **M4: Components Complete** | Day 8-10 | Sensors, Actuators, Context, Observers, InternalState | ⏳ Pending |
| **M5: Service Layer** | Day 11-12 | InternalStateService + Session integration | ⏳ Pending |
| **M6: Testing Complete** | Day 13-16 | All tests passing, coverage ≥90% | ⏳ Pending |
| **M7: Documentation** | Day 17 | Docs, examples, README, integration guide | ⏳ Pending |

**Total Estimated Duration:** 17 working days (refined from 10 days due to added complexity)

**Critical Path:**
```
M1 → M2 → M3 → M4 → M5 → M6 → M7
         ↑         ↑         ↑
      Core PN   Service   Testing
```

---

## 11. Appendix

### 11.1 Glossary (Updated)
- **Petri Net:** Mathematical modeling language for concurrent systems
- **Place:** State holder in Petri Net (circles in diagrams), holds tokens
- **Transition:** Event that changes state (bars in diagrams), fires when enabled
- **Marking:** Current distribution of tokens across places
- **Guard:** Boolean condition for transition enabling (uses Sensors)
- **Action:** Code executed when transition fires (uses Actuators)
- **Arc:** Directed connection between Place and Transition (input/output)
- **Adaptive:** Capable of modifying structure at runtime (on CRC change)
- **Service Layer:** Facade pattern for clean external access (follows AIService)
- **Observer:** Decoupled listener for state changes (IStateObserver)
- **ConcurrencyManager:** Handles thread safety (RLock + Queue + Debounce)
- **CRC32:** Fast checksum algorithm (zlib.crc32) for change detection

### 11.2 References (Updated)
- OMT++ Guide: `.meta/doc/omt_agent_guide.md`
- PROJECT.md: `.meta/projects/agentx_user_objectives/PROJECT.md`
- Petri Net Theory: [Wikipedia](https://en.wikipedia.org/wiki/Petri_net)
- Python threading: [docs.python.org/3/library/threading.html](https://docs.python.org/3/library/threading.html)
- Python queue: [docs.python.org/3/library/queue.html](https://docs.python.org/3/library/queue.html)
- Python zlib: [docs.python.org/3/library/zlib.html](https://docs.python.org/3/library/zlib.html)
- YAML frontmatter: [Jekyll documentation](https://jekyllrb.com/docs/front-matter/)
- Service Layer Pattern: [Martin Fowler](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- Observer Pattern: [Gang of Four](https://en.wikipedia.org/wiki/Observer_pattern)

### 11.3 Change Log (Updated)
| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-06-07 | 1.0 | Initial plan created | Agent |
| 2026-06-07 | 2.0 | **Refined Plan** - Added Service Layer, Concurrency Strategy, Observer Pattern, Session Integration, detailed testing strategy | Agent |

**Key Changes in v2.0:**
1. ✅ Added `InternalStateService` (service layer following AIService pattern)
2. ✅ Added `IStateObserver` ABC for decoupled notifications
3. ✅ Added `ConcurrencyManager` with RLock + Queue + Debounce
4. ✅ Specified `zlib.crc32()` as CRC algorithm
5. ✅ Finalized file format: YAML frontmatter in Markdown
6. ✅ Detailed Session integration (composition pattern)
7. ✅ Enhanced testing strategy with concurrency tests
8. ✅ Resolved all open questions from v1.0
9. ✅ Updated timeline: 10 days → 17 days (realistic estimate)
10. ✅ Updated coverage goal: 85% → 90%

### 11.4 Quick Reference: Architectural Decisions

| Decision | Choice | Location |
|----------|--------|----------|
| **Session Ownership** | Composition (per-session) | Section 1.4 |
| **File Format** | YAML frontmatter in .md | Section 4.3 |
| **Access Pattern** | Service Layer | Section 4.2 |
| **Concurrency** | RLock + Queue + Debounce | Section 4.4 |
| **CRC Algorithm** | zlib.crc32() | Section 4.4 |
| **Observer Pattern** | IStateObserver ABC | Section 4.2 |
| **Persistence** | Session lifetime (v1) | Section 8.2 |
| **Adaptivity** | Structure + Markings | Section 8.2 |

### 11.5 Implementation Checklist (Quick View)

**Phase 1: Core (Days 4-7)**
- [ ] Petri Net: Place, Transition, Arc, Marking, PetriNet
- [ ] ConcurrencyManager
- [ ] CRC utils + watcher
- [ ] Adaptive engine + parser

**Phase 2: Components (Days 8-10)**
- [ ] Context, Sensor (ABC + Mock), Actuator (ABC + Mock)
- [ ] StateObserver (ABC)
- [ ] InternalState (main class)

**Phase 3: Service + Integration (Days 11-12)**
- [ ] InternalStateService
- [ ] Session integration
- [ ] Integration tests

**Phase 4: Testing (Days 13-16)**
- [ ] Unit tests (all components)
- [ ] Integration tests
- [ ] System tests (concurrency, workflow)
- [ ] Coverage ≥90%

**Phase 5: Documentation (Day 17)**
- [ ] Docstrings
- [ ] Example USER_OBJECTIVES.md
- [ ] README
- [ ] Integration guide

---

## 12. Reference Implementation: Software Development Consortium

### 12.1 Overview

A **complete, production-ready example** of a complex Petri Net demonstrating all InternalState capabilities is available in:

**📄 File:** `.meta/projects/agentx_user_objectives/examples/software_development_consortium.md`

This example implements a **Multi-Agent Software Development Consortium** with:
- **6 specialized AI agents** (Architect, Backend, Frontend, QA, Security, DevOps)
- **22 Places** (agents, coordination states, resource pools, quality gates)
- **28 Transitions** (full SDLC from sprint planning to emergency hotfix)
- **5 Resource pools** with contention and negotiation
- **3 Quality gates** with feedback loops
- **1 Emergency transition** (P0 incident handling from ANY state)

### 12.2 How to Use This Example

#### **Option A: Quick Start (Test the Petri Net)**
```bash
# Copy the example to active configuration
cp .meta/projects/agentx_user_objectives/examples/software_development_consortium.md \
   local_sessions/current/USER_OBJECTIVES.md

# AgentX automatically detects CRC change and loads the new Petri Net
# Internal State now models software development workflow
```

#### **Option B: Study the Design**
Read the example file to understand:
- How to define **places** with initial markings
- How to specify **transitions** with guards and actions
- How to model **resource contention** and negotiation
- How to implement **quality gates** with feedback loops
- How to handle **emergencies** that interrupt any state

#### **Option C: Customize for Your Team**
1. Copy the example to your project
2. Modify resource pool sizes (more CI slots, more reviewers)
3. Add/remove agents (Mobile, ML, Data Engineering)
4. Adjust quality gates (compliance review, performance tests)
5. Add transitions for your specific workflow

### 12.3 What This Example Demonstrates

| Feature | Location in Example | Related Plan Section |
|---------|---------------------|---------------------|
| **Resource Contention** | T8-T10 (CI slot negotiation) | Section 4.4 (Concurrency Strategy) |
| **Quality Gates** | T19-T21 (tests, security, review) | Section 6 (Testing Strategy) |
| **Feedback Loops** | T15 → T18 → T14 (test failures) | Section 3.1 (Use Cases) |
| **Emergency Handling** | T28 (P0 incident from ANY state) | Section 4.2 (Interface Definitions) |
| **Synchronization** | T3, T10, T24 (multi-token transitions) | Section 4.5 (Sequence Diagrams) |
| **Dynamic Reconfiguration** | CRC-based updates | Section 4.3 (File Format) |

### 12.4 Simulation Results

A **complete discrete event simulation** of this Petri Net is available in:

**📄 File:** `.meta/projects/agentx_user_objectives/examples/software_development_consortium_simulation.md`

**Key Metrics from Simulation:**
- **Total sprint duration:** 5 hours 30 minutes
- **Quality gates passed:** 3/3 (tests, security, review)
- **Feedback loops:** 2 (test fix, security fix)
- **Emergency response:** P0 incident resolved in 18 minutes
- **Revenue saved:** ~$135,000 (via emergency hotfix)
- **No deadlocks:** All transitions eventually fired
- **Resource efficiency:** 72% average utilization

### 12.5 Integration with Implementation

When implementing the InternalState module, this example serves as:

1. **Test Input:** Use the example file as input for integration tests
   ```python
   # tests/integration/internal_state/test_software_consortium.py
   def test_load_software_development_petri_net():
       petri_net = load_petri_net('examples/software_development_consortium.md')
       assert petri_net.place_count == 22
       assert petri_net.transition_count == 28
   ```

2. **Sensor/Actuator Templates:** The example defines 18 sensors and 28 actuators
   - Implement these as concrete classes in `components/sensor.py` and `components/actuator.py`
   - Use the example's guard conditions and action specifications

3. **Observer Examples:** The 6 observers defined can be implemented as:
   - `ResourceUsageObserver` - Tracks resource consumption
   - `ConflictObserver` - Logs resource/contention events
   - `QualityGateObserver` - Monitors gate pass/fail
   - `SprintMetricsObserver` - Collects velocity, cycle time
   - `EmergencyObserver` - Tracks incident response times

4. **Dashboard Specification:** The simulation's real-time status updates provide a UI spec:
   ```
   State: Integration in Progress
   Resources: CI/CD Slots: ██░░░░░░░░ 1/3 available
   Quality Gates: ✅ Tests | ⏳ Security | ⏳ Review
   Blockers: ⚠️  2 HIGH vulnerabilities
   ```

### 12.6 Validation Checklist

Before considering the InternalState implementation complete, verify it can:

- [ ] **Load** the software development consortium Petri Net without errors
- [ ] **Execute** all 28 transitions in the correct sequence
- [ ] **Handle** resource contention (T8-T10 negotiation)
- [ ] **Enforce** quality gates (T19-T24)
- [ ] **Support** feedback loops (failed tests → revisions → retest)
- [ ] **Trigger** emergency hotfix (T28) from any state
- [ ] **Checkpoint** state before emergency, resume after
- [ ] **Release** resources correctly (T27)
- [ ] **Track** metrics matching simulation results

### 12.7 Extension Ideas

The example provides a foundation for additional scenarios:

1. **Multi-Project Coordination:** Extend to handle 2-3 concurrent sprints
2. **Compliance Gates:** Add SOC2, HIPAA, or GDPR compliance checks
3. **Performance Testing:** Add load testing as a quality gate
4. **A/B Testing:** Model feature flag deployment and analysis
5. **Incident Management:** Expand T28 to full ITIL-style incident workflow

---

## 13. Next Steps (Action Items)

### Immediate (Before Programming)
1. ✅ **Review this refined plan** with stakeholder
2. ✅ **Confirm architectural decisions** (Service Layer, Concurrency, Observers)
3. ⏳ **Verify `pyyaml` dependency** (check if already installed or needs addition)
4. ✅ **Study the reference example** - Read `examples/software_development_consortium.md` (see Section 12)

### Programming Phase Entry Criteria
- [ ] Plan reviewed and approved
- [ ] All design questions answered
- [ ] Reference example validated ✅ (see Section 12)
- [ ] Test environment ready
- [ ] Feasibility confirmed (all risks mitigated)
- [ ] **Example file accessible** - `examples/software_development_consortium.md` exists and is valid

### First Programming Task (Sprint 1, Task 1)
**Create:** `src/agentx/model/internal_state/petri_net/place.py`

**Requirements:**
- Class `Place` with `id`, `description`, `tokens` (int)
- Methods: `add_token()`, `remove_token()`, `get_tokens()`
- Validation: tokens ≥ 0
- Unit test: test_place.py

**Acceptance Criteria:**
- Place can be created with initial tokens
- Tokens can be added/removed
- Cannot remove more tokens than available (raises exception)
- 100% test coverage for Place class

💡 **Pro Tip:** Study how places are used in the **[Software Development Consortium example](#12-reference-implementation-software-development-consortium)** - see transitions T1-T28 for real-world usage patterns. For instance:
- T1 shows place self-loop (architect → sprint_planned + architect)
- T3 shows multi-place synchronization (backend + frontend + security → awaiting_integration)
- T27 shows resource release pattern (all agents → all resource pools)

---

## 14. Appendix

### 14.1 Quick Reference: Example Integration

**📄 Reference Example:** `examples/software_development_consortium.md`

| When You Need... | See Example Section | Transition IDs |
|------------------|---------------------|----------------|
| Resource contention pattern | Phase 2: Parallel Development | T8, T9, T10 |
| Quality gate with feedback | Phase 4: Quality Gates | T15 → T18 → T19 |
| Emergency from any state | Phase 5: Emergency | T28 |
| Multi-agent synchronization | Phase 3: Integration | T3, T10, T24 |
| Resource release pattern | Phase 5: Release | T27 |
| Merge conflict resolution | Phase 3: Integration | T11, T13 |
| Security vulnerability handling | Phase 4: Quality Gates | T16, T20 |

**💡 Usage:** When implementing a feature, first study the corresponding pattern in the example.

### 14.2 Glossary (Updated)