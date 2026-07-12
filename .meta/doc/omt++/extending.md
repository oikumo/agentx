# Extending AgentX (compressed)

> **Scope:** how-to guides for common additions + conventions checklist. Follow OMT++ process (`omt_agent_guide.md`) for every change.

---

## 0. Before You Start (Every Change)
1. Read `WORK.md` (current state) + `AGENTS.md` (rules).
2. Declare phase before editing `src/`:
   `omt_phase{ task_type, scope, phase, feature, design_doc? }`
   - `bug_fix` / `minor_feature` / `refactor` → phase declaration sufficient
   - `major_feature` / `new_screen` → also requires `design_doc` path that exists on disk. Scaffold: `uv run scripts/omt/new_feature.py "<name>" --type <type>`
3. Run `uv run scripts/omt/mvc_check.py` after edits (target: 0 errors).
4. Tests need `omt_skip{scope:"tests"}` (tests/ edits are gated).

---

## 1. Add a Command (Main Screen)
Commands = top-level typed-keyword dispatchers.

1. **Create** `Command` subclass in `src/agentx/ui/screens/main/commands/commands.py`:
   ```python
   class FooCommand(Command):
       def __init__(self, key: str, controller: "MainController"):
           super().__init__(key, "Short description", controller)
       def run(self, arguments: list[str]) -> None:
           self._controller.print_message(f"foo got {arguments}")
   ```
2. **Register** in `MainController.load_commands()` (`ui/screens/main/main_controller.py`):
   ```python
   self.add_command(FooCommand("foo", self))
   ```
3. Reachable by typing `foo <args>` in main screen; appears in `help` automatically.

> Commands call controller, never view directly. To open a new screen, add `controller.show_<thing>()` and a screen triad (§2) — see `chat`/`rag`/`agent`.

---

## 2. Add a Screen (MVC++ Triad)
Each screen = self-contained Model-View-Controller triad.

1. **Scaffold:** `uv run scripts/omt/new_feature.py "<screen name>" --type new_screen` (creates requirements feature dir; then create design doc under `.meta/.../4.design/features/<feature>/design_001_*.md` + `operation_spec_001_*.md`).
2. **Create triad** under `src/agentx/ui/screens/<screen>/`:
   - `<screen>_controller.py` — implements `I<Screen>ViewPartner`
   - `<screen>_view.py` — implements `I<Screen>View`; defines `I<Screen>View(ABC)` + `I<Screen>ViewPartner(ABC)` (or add to `ui/interfaces.py`)
   - `__init__.py`
3. **Console view:** wrap `UIConsole`.
4. **TUI view:** add Textual `Screen` under `ui/tui/screens/` + adapter under `ui/tui/adapters/`; register creation in `TUIProvider`.
5. **Wire navigation:** keybinding/button + `action_open_<screen>()` in `MainTUIScreen` calling `controller.show_<screen>()` then `app.push_screen()`.
6. **Test:** Textual pilot e2e under `tests/features/<feature>/` (see `feature_007`'s `test_tui_agent_screen.py` pattern).

**Agent screen example:** `agent/view/tui/agent_screen.py` + `agent_screen.py` registers as virtual `IAgentViewPartner` subclass (avoids Textual/abc metaclass conflict). Factory = `AgentAdapter`.

---

## 3. Add an Agent Tool
Tools = sensors (`ISensor`), actuators (`IActuator`), or hybrid (both).

1. **Implement** in `src/agentx/agent/model/tools/<your_tool>.py`:
   ```python
   class YourTool:
       id = "your_tool"
       def sense(self) -> SensorReading: ...              # if sensor
       def get_sensor_schema(self) -> SensorSchema: ...
       def validate(self, command: ActuatorCommand) -> ValidationResult: ...  # if actuator
       def act(self, command: ActuatorCommand) -> ActuatorResult: ...
       def get_actuator_schema(self) -> ActuatorSchema: ...
   ```
2. **Register** in `Agent._register_builtin_tools()` (`model/agent.py`):
   ```python
   self._safe_register_sensor(tool)  # and/or
   self._safe_register_actuator(tool)
   ```

---

## 4. Conventions Checklist (Verify Before Complete)

| Area | Rule |
|------|------|
| **MVC++** | View imports Model? → NO. Controller imports View directly? → NO (only via Partner ABC). SQL in Controller/View? → NO (DP classes only). |
| **Abstract Partner** | Partner interface = `ABC` + `@abstractmethod`. Name = `I*ViewPartner`. Defined in view file (or `ui/interfaces.py` for agent). Controller implements it. View receives via constructor injection. |
| **Naming** | Files: `<layer>/<screen>/<screen>_<layer>.py` (model omits suffix). Classes: `*Controller`, `*View`, `*Adapter`, `DP_*`, `*Repository`. |
| **Commands** | Main screen only. `Command(ABC)` with `key`, `controller`, `run(args)`. Registered in `MainController.load_commands()`. |
| **DP Pattern** | All SQL in `DP_*` / `*Database` classes. Idempotent DDL (`CREATE TABLE IF NOT EXISTS`). stdlib `sqlite3` only. |
| **TDD** | `major_feature` / `new_screen` in Programming phase → auto-TDD: `omt_testlist` → `omt_red` → `omt_green` → `omt_refactor` → `omt_done`. Two-hats: RED=tests/ only, GREEN/REFACTOR=src/ only (auto-revert on break). |
| **Process** | `omt_phase` before `src/` edits. `omt_complete` to advance phases (validates artifacts). `omt_skip` logged escape hatch. |
| **Tests** | Unit: mock Partner ABC (not concrete). Integration: real View + mock Model, or real Model + mock View. E2E: Textual Pilot. All isolated, no external deps. |

---

## 5. Quick Ref: Key Files to Touch

| Task | Files |
|------|-------|
| New main command | `ui/screens/main/commands/commands.py` + `ui/screens/main/main_controller.py` |
| New screen (console) | `ui/screens/<name>/<name>_controller.py`, `<name>_view.py` |
| New screen (TUI) | + `ui/tui/screens/<name>_screen.py` + `ui/tui/adapters/<name>_adapter.py` + `ui/tui/provider.py` |
| New agent tool | `agent/model/tools/<tool>.py` + `agent/model/agent.py` (`_register_builtin_tools`) |
| New DP table | `agent/persistence/schema_db.py` (`Table*`) + `agent/persistence/repositories_db.py` + `agent/persistence/agent_db.py` |
| New AI provider | `model/ai/providers.py` (implement `LLMProvider`) + `model/ai/service.py` (factory method) |

---

## 6. Related Docs
- Process: `omt_agent_guide.md` (§2 Phase Model, §12 Essential vs Optional, §13 Checklist)
- Architecture: `architecture.md` (layering, patterns, tech stack)
- Data flows: `data_flow.md` (boot, navigation, agent cycle, RAG, chat, session, persistence)
- Subsystem internals: `subsystems.md`
- Persistence: `persistence.md`
- Feature catalog: `features.md`