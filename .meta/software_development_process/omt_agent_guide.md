# OMT++ Agent Guide

> **Purpose:** The complete OMT++ methodology, condensed for coding agents.
> Every rule here is actionable. Follow all of them. No exceptions.
>
> **Target:** AI coding agents | **Version:** 2.0 | **Based on:** OMT++ v2.0

---

## Table of Contents

1. [The OMT++ Mindset for Agents](#1-the-omt-mindset-for-agents)
2. [Phase Model — How an Agent Moves Through Work](#2-phase-model--how-an-agent-moves-through-work)
3. [The Two Parallel Paths — Static + Functional](#3-the-two-parallel-paths--static--functional)
4. [Feasibility Study — Before You Code Anything](#4-feasibility-study--before-you-code-anything)
5. [Core Architecture: MVC++](#5-core-architecture-mvc)
6. [Abstract Partner Pattern](#6-abstract-partner-pattern)
7. [Screen MVC Triad Rules](#7-screen-mvc-triad-rules)
8. [Command Pattern (Top-Level Dispatch)](#8-command-pattern-top-level-dispatch)
9. [Model Layer Patterns](#9-model-layer-patterns)
10. [Operation Specifications](#10-operation-specifications)
11. [Testing Strategy — Three Stages](#11-testing-strategy--three-stages)
    - [11.4 TDD Workflow (feature_016)](#114-tdd-workflow-feature_016)
12. [Essential vs. Optional — Decision Guide for Agents](#12-essential-vs-optional--decision-guide-for-agents)
13. [Artifact Production Checklist](#13-artifact-production-checklist)
14. [Quick Reference — Do/Don't](#14-quick-reference--dodont)
15. [File Tree Template](#15-file-tree-template)
16. [Common Mistakes to Catch](#16-common-mistakes-to-catch)

---

## 1. The OMT++ Mindset for Agents

Before you write a single line of code, internalize these six beliefs. They govern every decision you make.

| # | Principle | What It Means For You |
|---|---|---|
| 1 | **Practical over theoretical** | Write code that works. Don't over-abstract. If a pattern adds complexity without value, skip it. |
| 2 | **Adaptable** | Different tasks need different process models. A bug fix ≠ a new feature ≠ a new project. Adjust your approach accordingly. |
| 3 | **Complete coverage** | You must cover the full cycle: understand the problem → design → implement → test. Never skip straight to coding. |
| 4 | **Visible artifacts** | Every phase produces something tangible: a use case, a diagram sketch, a test plan. These are not bureaucracy — they are your deliverables. |
| 5 | **Controlled process** | You plan your work, execute in defined phases, and verify before moving on. No rushing. No half-done work. |
| 6 | **Architecture first** | High-quality architecture enables late modifications. Get the structure right before you fill in details. Bad architecture = never-ending fixes. |

### How These Apply to Agent Work

When a user gives you a request, your first thought must **not** be "what code do I write?" Your first thought must be **"which OMT++ phase am I in?"**

- If the request is **vague or conceptual** → You are in **Analysis** — clarify requirements, write use cases first.
- If the request is **a clear feature** → You are in **Design** — plan architecture, interfaces, components.
- If the request is **an implementation task** → You are in **Programming** — but still verify the design exists.
- If the request is **a fix or verification** → You are in **Testing** — reproduce, isolate, fix, verify.

---

## 2. Phase Model — How an Agent Moves Through Work

OMT++ defines four sequential but iterative phases. Every task you do maps to one of these phases.

```
┌──────────────────────────────────────────────────────────────────────┐
│               Feasibility Study (Pre-Phase)                          │
│   Purpose: Should we even do this? How hard is it? What's the risk? │
│   Output: Go/no-go decision, effort estimate, preliminary design     │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│  PHASE 1: ANALYSIS                                                   │
│  Question: WHAT is the problem? WHAT do users need?                  │
│  Your job: Understand domain, gather requirements, write use cases,  │
│            model concepts, specify UI behavior.                      │
│  Output: Use cases, analysis class diagram, UI spec                  │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│  PHASE 2: DESIGN                                                     │
│  Question: HOW will we implement the solution?                       │
│  Your job: Architecture, components, interfaces, detailed classes    │
│  Output: Component diagram, design class diagram, sequence diagrams  │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│  PHASE 3: PROGRAMMING                                                │
│  Question: Write the code.                                           │
│  Your job: Implement classes, methods, unit tests                    │
│  Output: Source code, compiled modules, unit test results             │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│  PHASE 4: TESTING                                                    │
│  Question: Does it work? Did we meet requirements?                   │
│  Your job: Find errors, verify use cases, validate requirements      │
│  Output: Test reports, defect logs, verified system                  │
└──────────────────────────────────────────────────────────────────────┘
```

### Phase Rules for Agents

**Rule 1: You must identify which phase you are entering.** State it explicitly:
> *"This request puts me in the Analysis phase. I need to clarify requirements before designing."*

**Rule 2: You may iterate between phases**, but never skip one entirely.
- If you discover a missing requirement during Programming → go back to Analysis.
- If you find a design flaw during Testing → go back to Design.

**Rule 3: Each phase produces a visible artifact.** If your current phase doesn't produce output you can show the user, you're not done.

**Rule 4: Phase products are frozen after project completion** (not maintained). They exist as historical record. Only the architecture document and code are maintained long-term.

### Phase Transition Cheat Sheet

| Current Phase | Valid Next Phases | Invalid |
|---|---|---|
| Analysis | Design (normal), Testing (only if prototyping) | Programming (skip design = chaos) |
| Design | Programming, Analysis (if gaps found) | Testing (code doesn't exist yet) |
| Programming | Testing, Design (if design fails), Analysis (if requirements shift) | Nothing (must test before done) |
| Testing | Analysis (if requirements wrong), Design (if design wrong), Programming (if bug found) | Done (only when all tests pass) |

---

## 3. The Two Parallel Paths — Static + Functional

OMT++ works along **two complementary paths** at all times. You must model both.

```
STATIC PATH (Structural View)          FUNCTIONAL PATH (Behavioral View)
┌─────────────────────────┐            ┌─────────────────────────┐
│ ANALYSIS:                │            │ ANALYSIS:                │
│ Analysis class diagram   │            │ Use cases                │
│ Data dictionary          │            │ Operation specifications │
└─────────────────────────┘            └─────────────────────────┘
           │                                        │
           ▼                                        ▼
┌─────────────────────────┐            ┌─────────────────────────┐
│ DESIGN:                  │            │ DESIGN:                  │
│ Component diagram        │            │ Sequence diagrams        │
│ Design class diagram     │            │ Collaboration scenarios  │
└─────────────────────────┘            └─────────────────────────┘
           │                                        │
           ▼                                        ▼
┌─────────────────────────┐            ┌─────────────────────────┐
│ PROGRAMMING:             │            │ PROGRAMMING:             │
│ Class implementations    │            │ Method implementations   │
│ File structure           │            │ Control flow             │
└─────────────────────────┘            └─────────────────────────┘
           │                                        │
           ▼                                        ▼
┌─────────────────────────┐            ┌─────────────────────────┐
│ TESTING:                 │            │ TESTING:                 │
│ Component tests          │            │ Use case tests           │
│ Interface tests          │            │ Workflow tests           │
└─────────────────────────┘            └─────────────────────────┘
```

### Why Both Matters for Agents

- **Static path alone** = you know what classes/files exist, but you don't know how they interact at runtime. You'll write isolated code that doesn't connect.
- **Functional path alone** = you know the flow, but you'll create a messy file structure with no clear ownership of concepts.

**Always produce both.** For every coding task:
1. **First sketch the static structure** — what components/classes/files are needed?
2. **Then sketch the functional flow** — how do they interact step by step?
3. **Then code.**

### What This Looks Like in Practice

```
TASK: "Add a /sum command that adds two numbers"

STATIC ANALYSIS (you think this):
  - New class: SumCommand(Command) in commands.py
  - MainController already has command registry
  - No new screens needed

FUNCTIONAL ANALYSIS (you think this):
  1. User types "/sum 3 5"
  2. CommandParser parses → CommandData("sum", "3 5")
  3. MainController.run_command() → SumCommand.run("3 5")
  4. SumCommand parses args, computes, calls controller.print_message("8")
  5. MainView prints result

IMPLEMENT (you write both):
  - Static: class SumCommand(Command) in commands.py + register it
  - Functional: run() method with the flow above
```

---

## 4. Feasibility Study — Before You Code Anything

Before diving into any task, do a mini feasibility study. This is **not optional** — it is the pre-phase that prevents wasted work.

### The 4 Questions

| Question | What to do |
|---|---|
| **1. Do I understand the requirements?** | If no → ask the user. Never guess. |
| **2. Is the scope clear?** | Can you state in one sentence what "done" looks like? If not, scope is unclear. |
| **3. Do I know where in the codebase this goes?** | Identify the exact files you'll touch. If you can't, explore first. |
| **4. What's the risk level?** | High = new feature, new screen, data model changes. Low = bug fix, minor extension. |

### Feasibility Output

State this to the user before writing any code:

> **Feasibility:**
> - **Phase:** Design (clear feature)
> - **Files affected:** `main_controller.py`, `commands.py`
> - **Risk:** Low (adds one command, no new screens)
> - **Effort estimate:** ~15 min implementation, ~15 min testing

### When to Say "No" (or "Not Yet")

| Situation | Response |
|---|---|
| Requirements are vague | "I need to clarify requirements before I can design this. Can you tell me more about X?" |
| Scope is too large | "This touches multiple screens and a new data model. I recommend splitting into increments." |
| Missing dependencies | "I need to know how X works before I can implement Y. Let me research first." |
| Effort is underestimated | "This looks like 3+ hours of work. Let me outline a plan before starting." |

---

## 5. Core Architecture: MVC++

Every feature is split into exactly three layers. No mixing.

```
┌──────────────────────────────────────────────────────┐
│                    CONTROLLER                         │
│  Application logic, orchestration, command dispatch   │
│  Knows: View + Model                                  │
│  Seen by: View (as Abstract Partner interface)        │
├──────────────────────────────────────────────────────┤
│                       VIEW                            │
│  UI rendering, input capture, display                 │
│  Knows: Controller (only via Abstract Partner)        │
│  Seen by: nobody (controller delegates to it)         │
├──────────────────────────────────────────────────────┤
│                      MODEL                            │
│  Domain logic, business rules, data persistence       │
│  Knows: nothing about UI layers                       │
│  Seen by: Controller                                  │
└──────────────────────────────────────────────────────┘
```

### Layer Rules — Absolute

| What | Controller | View | Model |
|---|---|---|---|
| Imports Model? | ✅ Yes | ❌ Never | N/A |
| Imports View? | ✅ Yes | N/A | ❌ Never |
| Imports Controller? | N/A | ❌ Only via Abstract Partner | ❌ Never |
| Can be tested alone? | ✅ With mock View + Model | ✅ With mock Controller | ✅ Yes |
| Contains UI code? | ❌ Never | ✅ Yes | ❌ Never |
| Contains business logic? | ✅ Orchestration only | ❌ Never | ✅ Core logic |
| Contains SQL/database code? | ❌ Never | ❌ Never | ✅ In DP classes only |
| Lifecycle responsibility | Creates View + accesses Model | Exists only when controller creates it | Independent of UI lifecycle |

### File Naming Convention

```
<layer>/<screen>/<screen>_<layer>.py
ui/screens/main/main_controller.py
ui/screens/main/main_view.py
model/session/session.py
```

Every file is named after its layer at the end: `*_controller.py`, `*_view.py`. Model files omit suffix (e.g., `session.py`, not `session_model.py`).

### What is NOT in MVC++ (Anti-Patterns)

| Anti-pattern | Why it violates OMT++ |
|---|---|
| Fat View with logic | View must only render and capture. Logic in View = untestable. |
| Anemic Model with getters/setters only | Model must contain domain logic, not just data holders. |
| Controller with SQL | Every SQL statement is a separate concern. Use DP classes. |
| View creating its own Controller | View receives controller via constructor injection. Never `new Controller()` inside View. |
| Model referencing View | Creates circular dependency. Model must be UI-independent. |

---

## 6. Abstract Partner Pattern

This is the **only** way View talks to Controller. No exceptions.

### The Contract (ABC — never a plain class)

```python
from abc import ABC, abstractmethod

class IScreenPartner(ABC):
    """Abstract Partner Interface for a Screen."""
    # Methods the Controller must implement for the View to call

    @abstractmethod
    def on_user_input(self, user_input: str) -> None:
        """Process input captured by View."""
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        """Return the prompt prefix for this screen."""
        pass
```

### Rules — Absolute

1. **Always `ABC`** — never a plain class. Every method gets `@abstractmethod`. No exceptions.
2. **Name starts with `I`**: `IMainViewPartner`, `IChatViewPartner`, `IRagViewPartner`.
3. **Define it in the same file as the View** — top of file, before the View class.
4. **View constructor receives partner** — never creates the controller.
5. **Controller implements the interface** — `class MyController(IMyViewPartner)`.
6. **Partner methods are the complete API** between View and Controller. No back channels.

### Wiring (Constructor Injection)

```python
# --- View file ---
class MyView:
    def __init__(self, partner: IMyViewPartner):  # Interface type, not concrete
        self._partner = partner
        self._console = UIConsole(partner.get_prompt())  # Call back to controller

    def show(self):
        while True:
            inp = self._console.capture_input()
            self._partner.on_user_input(inp)  # Delegate to controller

# --- Controller file ---
class MyController(IMyViewPartner):  # Implements the interface
    def __init__(self):
        self._view = MyView(self)  # Pass self as partner

    def on_user_input(self, user_input: str) -> None:
        ...
    def get_prompt(self) -> str:
        return "(my-screen)"
```

### Testing the Wiring

```python
class MockPartner(IMyViewPartner):
    def on_user_input(self, user_input): ...
    def get_prompt(self): return "(test)"

def test_view_delegates_to_partner():
    partner = MockPartner()
    view = MyView(partner)
    # View called with input → partner.on_user_input is invoked
```

### Common Mistake Detection

```
❌ BAD: class IMainViewPartner:  # plain class, no ABC
❌ BAD: class MainView(MainController):  # View inherits from Controller
❌ BAD: def __init__(self): self.controller = MainController()  # View creates Controller
✅ GOOD: class IMainViewPartner(ABC): ...  # ABC with @abstractmethod
✅ GOOD: class MainView: def __init__(self, partner: IMainViewPartner):  # injection
```

---

## 7. Screen MVC Triad Rules

Each screen (Main, Chat, RAG, etc.) is a **self-contained MVC triad**.

### Creating a New Screen

1. Create folder: `ui/screens/<screen_name>/`
2. Create three files:
   - `ui/screens/<screen_name>/<screen_name>_controller.py`
   - `ui/screens/<screen_name>/<screen_name>_view.py`
   - `ui/screens/<screen_name>/__init__.py`
3. Define `I<ScreenName>ViewPartner(ABC)` in the view file.
4. Controller implements the partner interface.
5. View receives partner in constructor.

### Screen Lifecycle

```
ParentController.show_child():
  1. child = ChildController()       # Create triad
  2. child.show()                    # Takes over REPL
  3. # User interacts...             # Child loop runs
  4. # User quits → return           # Control goes back to parent
```

- Sub-screens **do not** leak references to parent.
- Sub-screens **do not** need to know about parent structure.
- When sub-screen exits, parent controller resumes its own loop.

### Input Components (Mini MVC Triads)

For reusable input patterns (URL entry, option selection, folder name, text list):

```
ui/common/input/<input_type>/
  input_<input_type>_controller.py
  input_<input_type>_view.py
```

- Same Abstract Partner pattern applies.
- Controller exposes a public property for the result (e.g., `controller.url`, `controller.selected_option`).
- Parent controller creates the input controller, calls `.show()`, then reads the result property.

---

## 8. Command Pattern (Top-Level Dispatch)

Used **only** at the main screen level for routing user input. This is the implementation of OMT++ Behavior Analysis at the top level.

### Structure

```
ui/screens/main/commands/
├── commands_base.py       # Command ABC
├── commands.py            # Concrete commands
└── commands_parser.py     # CommandParser + CommandData
```

### Command ABC

```python
class Command(ABC):
    def __init__(self, key: str, controller: "MainController"):
        self.key = key                # The string that triggers this command
        self._controller = controller  # Reference back to controller

    @abstractmethod
    def run(self, arguments: str) -> None:
        pass
```

### Rules

- Each command is a **single class** in `commands.py`.
- Command constructor takes `(key: str, controller: MainController)`.
- `run()` executes the operation — may create sub-screens (Chat, RAG).
- Commands are registered in `MainController.load_commands()`.
- Commands **do not** call the View directly — they call the Controller, which calls the View.

### Flow

```
User input → CommandParser.parse() → CommandData(key, args)
  → MainController.run_command()
    → Look up command by key in dict
    → command.run(arguments)
```

### When to Add a Command vs. When to Add a Screen

| Scenario | Do this |
|---|---|
| User types a keyword and gets a response | New `Command` class |
| User types a keyword and enters a new interface | New `Command` + new `Screen MVC triad` |
| User types a keyword and modifies data | New `Command` + new `Operation` in Model |
| User types a keyword and sees a list | New `Command` + use existing View methods |

---

## 9. Model Layer Patterns

### Persistent Objects

Every entity that persists across sessions has the standard CRUD lifecycle:

```python
class Session:
    def __init__(self):
        self.oid: int = None         # Object Identifier — unique across all instances
        self.name: str = ""
        self.directory: str = ""

    def create(self) -> bool: ...     # INSERT into database
    def load(self, oid: int) -> "Session": ...  # SELECT by OID
    def update(self) -> bool: ...     # UPDATE existing row
    def delete(self) -> bool: ...     # DELETE from database
```

### Database Partner (DP) Pattern

Encapsulate **all** SQL/database access in a `DP_*` class. No SQL outside DP classes.

| File | Contains |
|---|---|
| `model/session/session_db.py` | `DP_Session` — all session CRUD |
| `model/rag/rag_db.py` | `DP_Rag` — all RAG CRUD |

```python
class DP_Session:
    """Database Partner for Session. All SQL lives here."""

    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)

    def insert(self, session: Session) -> int:
        """Persist a new Session. Returns new OID."""
        cur = self.conn.execute("INSERT INTO sessions (name, directory) VALUES (?, ?)",
                                 (session.name, session.directory))
        return cur.lastrowid

    def load(self, oid: int) -> Session:
        """Load Session by OID."""
        row = self.conn.execute("SELECT oid, name, directory FROM sessions WHERE oid = ?", (oid,)).fetchone()
        if not row:
            raise ValueError(f"Session {oid} not found")
        session = Session()
        session.oid, session.name, session.directory = row
        return session

    def update(self, session: Session) -> None:
        self.conn.execute("UPDATE sessions SET name = ?, directory = ? WHERE oid = ?",
                          (session.name, session.directory, session.oid))

    def delete(self, oid: int) -> None:
        self.conn.execute("DELETE FROM sessions WHERE oid = ?", (oid,))
```

### Navigation with Persistent Objects

Associations between entities are represented as OID references:

```python
class LibraryUser:
    def __init__(self):
        self.oid: int = None
        self.room_oid: int = None  # Foreign key to Room

    def get_resides_in(self) -> Room:
        """Navigate to associated Room via OID."""
        if self.room_oid:
            return Room.load(self.room_oid)
        return None
```

### SQLite to Class Mapping

| OMT++ Concept | SQLite Implementation |
|---|---|
| Class → Table | `CREATE TABLE session (oid INTEGER PRIMARY KEY, ...)` |
| Object → Row | One row per object instance |
| Attribute → Column | One column per attribute |
| Association → Foreign Key | `resides_in INTEGER REFERENCES room(oid)` |
| Inheritance → 1 table | Single table with NULLable columns for subclass-specific fields |

### Collections

Groups of objects are modeled as lists/sets in the controller or model:

```python
class CommandHistory:
    """Collection of command entries (ordered, allows duplicates)."""
    def __init__(self):
        self.entries: list[HistoryEntry] = []

    def add(self, entry: HistoryEntry) -> None:
        self.entries.append(entry)

    def get_all(self) -> list[HistoryEntry]:
        return self.entries
```

---

## 10. Operation Specifications

Every public method in a Controller that handles user operations must have an **operation specification** as a docstring.

### Template

```python
def send_message(self, recipient: str, message: str) -> bool:
    """
    Operation: Send a message to a recipient.

    Preconditions:
      - Message length <= 160 characters
      - Recipient exists in contact list

    Exceptions:
      - Message too long: trim or reject with error
      - Network unavailable: queue for later delivery
      - Unknown recipient: return error to user

    Postconditions:
      - Message stored in sent_messages table
      - Recipient receives message (async)
    """
```

### Rules

1. **Every** user-facing method in a Controller needs this.
2. **Preconditions** — what must be true before the operation starts.
3. **Exceptions** — everything that can go wrong and how it's handled.
4. **Postconditions** — what is guaranteed to be true after the operation.
5. Keep it concise — one sentence per item is enough.

### Where Operations Come From

Operations are extracted from Use Cases during the Analysis phase:

```
Use Case: "Sending a Short Message"
  1. User writes message
  2. User adds signature
  3. User selects recipients
  4. User sends message

→ Operations list:
  - write_message(content)
  - add_signature()
  - select_recipients(list)
  - send_message()

Each → becomes a method in a Controller with an Operation Specification.
```

---

## 11. Testing Strategy — Three Stages

### Stage 1: Unit/Component Testing

| What | Details |
|---|---|
| Who writes | You (the agent) |
| What to test | One class at a time, in isolation |
| How to isolate | Mock Abstract Partner for Views, Mock DP for Models |
| Coverage target | >80% of all branches |

```python
# Mock the Abstract Partner interface, NOT the concrete Controller
class MockMainPartner(IMainViewPartner):
    def __init__(self):
        self.commands = []
    def on_user_input(self, inp):
        self.commands.append(inp)
    def get_prompt(self):
        return "(test)"

def test_view_captures_input():
    partner = MockMainPartner()
    view = MainView(partner)
    # ... simulate input ...
    assert partner.commands == ["/help"]
```

### Stage 2: Integration Testing

| What | Details |
|---|---|
| Who writes | You (the agent) |
| What to test | Component interactions |
| Scenarios | Controller + View (real View, mock Model), Controller + Model (real Model, mock View), DP + real SQLite (in-memory) |

```python
def test_command_execution():
    controller = MainController()
    view = MockView()
    controller.view = view  # Swap in mock
    controller.run_command("quit")
    assert view.was_closed()
```

### Stage 3: System Testing

| What | Details |
|---|---|
| Who writes | You (the agent) |
| What to test | Full workflows against Use Cases |
| Approach | Follow use case steps as test script |

```python
def test_sending_message_use_case():
    """Follow the 'Sending a Short Message' use case."""
    app.start()
    app.write_message("Hello")
    app.add_signature()
    app.select_recipient("John")
    app.send()
    assert app.confirmation_shown()
```

### Test Planning

Before writing tests, produce a quick test plan:

```
Component Test Plan for "SendMessage" operation:
  Normal path:
    - Send valid message → message sent, confirmation shown
  Exception paths:
    - Empty message → error shown, no send attempted
    - No recipient → error shown
    - Network failure → message queued, user notified
```

### 11.4 TDD Workflow (feature_016)

For `major_feature` and `new_screen` tasks in the Programming phase, TDD mode
auto-activates. The gate mechanically enforces the Kent Beck Red → Green → Refactor
cycle using five tools. You **must** follow this order:

```
omt_testlist  →  omt_red  →  omt_green  →  omt_refactor  →  omt_done
  (plan)         (write       (write code   (improve code     (verify
                  failing       to pass         keeping tests     full suite)
                  test)         the test)       green)
```

#### The Five TDD Tools

| Tool | State | Hat | What you do |
|------|-------|-----|-------------|
| `omt_testlist` | TESTLIST | — | List the behaviors (test names) you will implement |
| `omt_red` | RED | test | Write ONE failing test under `tests/`. Gate verifies it truly fails (AST + pytest). |
| `omt_green` | GREEN | code | Write the minimum code under `src/` to make the test pass. |
| `omt_refactor` | REFACTOR | code | Improve the code. Tests must stay green. If a refactor breaks tests, the edit is **auto-reverted**. |
| `omt_done` | DONE | — | Full suite + checklist pass. Phase exit validated. |

#### Two-Hats Gate

The gate tracks which "hat" you're wearing and blocks edits to the wrong layer:

| State | `tests/` edits | `src/` edits |
|-------|----------------|--------------|
| RED | ✅ Allowed | ❌ Blocked |
| GREEN | ❌ Blocked | ✅ Allowed |
| REFACTOR | ❌ Blocked | ✅ Allowed (reverted if tests break) |

If you try to edit the wrong layer, the gate tells you which hat to switch to.

#### True-RED Verification

`omt_red` doesn't just run pytest — it also performs AST analysis to verify the test
is a **true** RED (not a false red from an import error or syntax mistake). The test
must:
1. Import or reference the target source module (inferred from the test file path).
2. Fail because the target behavior doesn't exist yet (not because of a typo).

#### REFACTOR Auto-Revert

When in REFACTOR state, the gate snapshots the file before each edit. After the edit,
it runs the tests. If any test fails:
1. The file is **automatically reverted** to its pre-edit state.
2. The edit is blocked with a message: "REFACTOR broke tests — edit reverted."
3. You can try a different refactoring approach.

This makes refactoring safe — you can't accidentally introduce a regression.

#### Coverage Gap Analysis

On `omt_done` (or `omt_complete`), the gate runs `tdd_check.py validate-exit` which:
- Finds all public methods/functions in your `src/` modules.
- Checks which ones have test coverage (by AST-extracting test function calls).
- Reports **coverage gaps** — public methods with no test calling them.
- Reports **dangling reds** — tests declared RED but never turned GREEN.

If gaps or dangling reds exist, the phase exit is blocked until you write the missing
tests or call `omt_skip` to override.

#### TDD CLI (scripts/omt/tdd_check.py)

The TDD engine is a stdlib-only Python script with 9 subcommands:

```
uv run scripts/omt/tdd_check.py testlist --behaviors "..." --feature feature_NNN
uv run scripts/omt/tdd_check.py start --test-node tests/... --target-src src/... --feature feature_NNN
uv run scripts/omt/tdd_check.py green --test-node tests/... --feature feature_NNN
uv run scripts/omt/tdd_check.py refactor --test-node tests/... --feature feature_NNN
uv run scripts/omt/tdd_check.py done --feature feature_NNN
uv run scripts/omt/tdd_check.py gate --path <rel> --session <id>
uv run scripts/omt/tdd_check.py after-edit --path <rel> --session <id>
uv run scripts/omt/tdd_check.py status --session <id>
uv run scripts/omt/tdd_check.py validate-exit --feature feature_NNN
```

The five `omt_*` wrapper tools delegate to the first five subcommands. The `gate` and
`after-edit` subcommands are called by the enforcer hooks automatically.

---

## 12. Essential vs. Optional — Decision Guide for Agents

Not every OMT++ artifact is needed for every task. This table tells you what to produce based on task type.

| Artifact | Bug Fix | Minor Feature | Major Feature | New Screen | New Project |
|---|---|---|---|---|---|
| Feasibility statement | ✅ Quick | ✅ Quick | ✅ Yes | ✅ Yes | ✅ Yes |
| Use case | ❌ | ❌ | ✅ Yes | ✅ Yes | ✅ Yes |
| Operation list | ❌ | ✅ Quick | ✅ Yes | ✅ Yes | ✅ Yes |
| Analysis class diagram | ❌ | ❌ | ✅ If new concepts | ✅ If new concepts | ✅ Yes |
| Dialog diagram | ❌ | ❌ | ❌ | ✅ Yes | ✅ Yes |
| Component diagram | ❌ | ❌ | ❌ | ✅ If new deps | ✅ Yes |
| Design class diagram | ❌ | ✅ Quick | ✅ Yes | ✅ Yes | ✅ Yes |
| Sequence diagram | ❌ | ❌ | ✅ For complex flows | ✅ For complex flows | ✅ Yes |
| Operation spec | ❌ | ✅ Quick | ✅ Yes | ✅ Yes | ✅ Yes |
| Unit tests | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Integration tests | ❌ | ✅ If new deps | ✅ Yes | ✅ Yes | ✅ Yes |
| System tests | ❌ | ❌ | ✅ Yes | ✅ Yes | ✅ Yes |

**Legend:** ✅ = produce this | ❌ = safe to skip | "Quick" = 1-2 line summary, not a full document

### General Rule of Thumb

- **Is the change in one existing file?** → Skip analysis artifacts, write tests.
- **Is the change across 2-3 files?** → Quick operation list + design sketch.
- **Is the change creating new files/screens?** → Full artifact set for that screen.
- **Is the change a new project/feature?** → Full methodology, all phases.

---

## 13. Artifact Production Checklist

Use this checklist for every task. Check off what applies.

### Before Starting (Feasibility)

- [ ] I understand the requirements (if not, I asked the user)
- [ ] I know the scope ("done" = one clear sentence)
- [ ] I know exactly which files will be affected
- [ ] I've assessed risk level (low/medium/high)
- [ ] I've stated the phase I'm entering

### Analysis Phase

- [ ] Written a use case (if new screen or major feature)
- [ ] Listed operations extracted from the use case
- [ ] Identified key domain concepts (classes)
- [ ] Specified UI dialog structure (if UI changes)

### Design Phase

- [ ] Identified which components/screens are affected
- [ ] Defined interfaces between components (Abstract Partners)
- [ ] Designed class structures (what classes, what methods)
- [ ] Planned data persistence (if new entities)
- [ ] Written operation specifications for new methods

### Programming Phase

- [ ] All Abstract Partner interfaces are `ABC`
- [ ] View receives partner via constructor injection
- [ ] View has zero knowledge of Model
- [ ] Controller orchestrates View and Model
- [ ] SQL is in DP classes, not in Controller
- [ ] Every `*_controller.py` and `*_view.py` is in the right directory

### Testing Phase

- [ ] Unit tests for each new class (>80% coverage)
- [ ] Tests mock the interface, not the concrete class
- [ ] Integration tests for component interactions
- [ ] System tests mapped to use cases (if applicable)
- [ ] All tests pass

---

## 14. Quick Reference — Do/Don't

### Do Table

| When you want to... | Do this |
|---|---|
| Route a user command | Use Command Pattern (main screen only) |
| Display output to user | Call `self._view.print_something()` from controller |
| Read user input | View captures it, calls `partner.on_user_input()` |
| Access the database | Use `DP_*` class, never raw SQL in controller |
| Create a new screen | Create folder + 3 files (controller, view, ABC) |
| Pass data between screens | Controller reads sub-controller's public properties |
| Test the UI | Mock the Abstract Partner interface |
| Add a new command | Add class to `commands.py`, register in `load_commands()` |
| Persist an object | Add `create/load/update/delete` methods + DP class |
| Model a collection | Use `list[...]` or `dict[str, ...]` typed collections |
| Navigate between objects | Use OID references, not direct object pointers |
| Start a new feature | Identify the phase first, then produce phase artifacts |
| Handle vague requirements | Switch to Analysis phase, write a use case, ask user |

### Never Do Table

| Never do this | Why |
|---|---|
| Import Model in View | Violates MVC++ — View must not know about Model |
| Import View in Model | Creates circular dependency, breaks reusability |
| Use a plain class as Abstract Partner | Must be `ABC` with `@abstractmethod` — no exceptions |
| Put business logic in View | Makes logic untestable |
| Put UI code in Controller | Controller becomes untestable |
| Put SQL in Controller | Scatters persistence logic across files |
| Create circular dependencies | Makes code impossible to test and refactor |
| Skip a phase entirely | Analysis → Design → Programming → Testing. Never jump straight from idea to code. |
| Code without knowing the file structure | Explore the codebase first. Never write blindly. |
| Skip tests for a new feature | Untested code = broken code. Tests are not optional. |

---

## 15. File Tree Template

```
src/agentx/
├── main.py                          # Entry point: creates MainController, calls run()
│
├── model/                           # MODEL LAYER — no UI imports ever
│   ├── ai/                          #   LLM providers, service facade
│   │   ├── service.py               #   AIService (facade/factory)
│   │   └── providers.py             #   LLMProvider ABC + implementations
│   ├── rag/                         #   RAG domain logic
│   │   ├── rag.py                   #   Rag orchestrator
│   │   ├── rag_db.py                #   DP_Rag — all RAG SQL
│   │   ├── rag_provider.py          #   Repository listing
│   │   ├── rag_repository.py        #   RagRepository dataclass
│   │   └── query/                   #   Query engine
│   └── session/
│       ├── session.py               #   Session entity (create/load/update/delete)
│       ├── session_manager.py       #   Session manager (NOT "Controller")
│       └── session_db.py            #   DP_Session — all session SQL
│
├── ui/                              # VIEW + CONTROLLER LAYERS
│   ├── common/
│   │   ├── ui_console.py            #   Terminal rendering engine
│   │   └── input/                   #   Mini MVC triads (reusable)
│   │       ├── text_list/           #     InputTextListController + View
│   │       ├── url_entry/           #     InputUrlController + View
│   │       ├── options/             #     InputOptionsController + View
│   │       └── create_folder/       #     InputCreateFolderController + View
│   └── screens/                     #   Screen MVC triads
│       ├── main/                    #   ── MAIN SCREEN ──
│       │   ├── main_controller.py   #     Implements IMainViewPartner
│       │   ├── main_view.py         #     IMainViewPartner(ABC) defined here
│       │   └── commands/            #     Command pattern
│       │       ├── commands_base.py #       Command ABC
│       │       ├── commands.py      #       Concrete commands
│       │       └── commands_parser.py
│       ├── chat/                    #   ── CHAT SCREEN ──
│       │   ├── chat_controller.py   #     Implements IChatViewPartner
│       │   └── chat_view.py         #     IChatViewPartner(ABC) defined here
│       └── rag/                     #   ── RAG SCREEN ──
│           ├── rag_controller.py
│           ├── rag_view.py
│           ├── rag_chat_controller.py
│           ├── rag_chat_view.py
│           ├── rag_web_ingestion_controller.py
│           ├── rag_web_ingestion_view.py
│           ├── rag_repository_selection_controller.py
│           └── rag_repostitory_selection_view.py
│
└── utils/                           # Cross-cutting utilities
    ├── constants.py
    ├── utils.py
    └── utils_directories.py
```

---

## 16. Common Mistakes to Catch

| # | Mistake | How to Detect (grep/review) | Fix |
|---|---|---|---|
| 1 | View imports Model | `grep -r "from.*model" ui/screens/*/view.py` | Move logic to Controller |
| 2 | Controller has UI code | `grep -r "console\|print" ui/screens/*/controller.py` | Move to View |
| 3 | Model imports UI layer | `grep -r "from.*ui" model/` | Invert the dependency |
| 4 | Plain class Abstract Partner | Check if interface class inherits `ABC` | Add `(ABC)`, add `@abstractmethod` |
| 5 | SQL in Controller | `grep -r "execute\|SELECT\|INSERT\|UPDATE\|DELETE" ui/screens/*/controller.py` | Move to DP class |
| 6 | Circular screen references | Child screen holds parent controller reference | Remove; use return value |
| 7 | God Controller (>300 lines) | `wc -l *controller.py` | Extract sub-controllers |
| 8 | Missing operation spec | Check public methods for pre/post docstring | Add specification |
| 9 | `*Controller` name in model/ | `ls model/**/*controller*` | Rename to `*Manager` or `*Service` |
| 10 | View creates Controller | `grep -r "Controller()" ui/screens/*/view.py` | Must receive via injection |
| 11 | Phase skipping | Did you go from idea to code without design? | produce the phase artifact first |
| 12 | No tests for new feature | `grep -r "test.*yournewclass" tests/` | Write unit + integration tests |

---

*End of OMT++ Agent Guide v2.0 — all rules are here. No other reference needed.*
