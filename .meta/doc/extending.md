# Extending AgentX

> **Scope:** how-to guides for common additions, plus the conventions checklist.
> Follow the OMT++ process (`omt_agent_guide.md`) for every change.

---

## 0. Before you start (every change)

1. Read `WORK.md` (current state) and `AGENTS.md` (rules).
2. Declare your phase before editing `src/`:
   `omt_phase{ task_type, scope, phase, feature, design_doc? }`.
   - `bug_fix`/`minor_feature`/`refactor` → a phase declaration is enough.
   - `major_feature`/`new_screen` → also requires a `design_doc` path that
     exists on disk. Scaffold with `uv run scripts/omt/new_feature.py "<name>" --type <type>`.
3. Run `uv run scripts/omt/mvc_check.py` after edits (target: 0 errors).
4. Tests need `omt_skip{scope:"tests"}` (tests/ edits are gated).

---

## 1. Add a command (main screen)

Commands are top-level typed-keyword dispatchers.

1. **Create** a `Command` subclass in `src/agentx/ui/screens/main/commands/commands.py`:
   ```python
   class FooCommand(Command):
       def __init__(self, key: str, controller: "MainController"):
           super().__init__(key, "Short description", controller)
       def run(self, arguments: list[str]) -> None:
           self._controller.print_message(f"foo got {arguments}")
   ```
2. **Register** it in `MainController.load_commands()`
   (`ui/screens/main/main_controller.py`):
   ```python
   self.add_command(FooCommand("foo", self))
   ```
3. The command is now reachable by typing `foo <args>` in the main screen's
   command input. It appears in `help` automatically.

> Commands call the controller, never the view directly. For an action that
> opens a new screen, add a `controller.show_<thing>()` and a screen triad
> (§2) — see how `chat`/`rag`/`agent` work.

---

## 2. Add a screen (MVC++ triad)

Each screen is a self-contained Model-View-Controller triad.

1. **Scaffold:** `uv run scripts/omt/new_feature.py "<screen name>" --type new_screen`
   (creates the requirements feature dir; then create a design doc under
   `.meta/.../4.design/features/<feature>/design_001_*.md` + `operation_spec_001_*.md`).
2. **Create the triad** under `src/agentx/ui/screens/<screen>/`:
   - `<screen>_controller.py` — implements `I<Screen>ViewPartner`.
   - `<screen>_view.py` — implements `I<Screen>View`; defines `I<Screen>View(ABC)`
     + `I<Screen>ViewPartner(ABC)` (or add them to `ui/interfaces.py`).
   - `__init__.py`.
3. **Console view:** build a `*View` wrapping `UIConsole`.
4. **TUI view:** add a Textual `Screen` under `ui/tui/screens/` + an adapter
   under `ui/tui/adapters/`; register creation in `TUIProvider`.
5. **Wire navigation:** add a keybinding/button + `action_open_<screen>()` in
   `MainTUIScreen` calling `controller.show_<screen>()` then `app.push_screen()`.
6. **Test:** Textual pilot e2e under `tests/features/<feature>/` (see
   `feature_007`'s `test_tui_agent_screen.py` for the pattern).

**Agent screen example:** `agent/view/tui/agent_screen.py` + `agent_screen.py`
registers as a virtual `IAgentViewPartner` subclass (avoids Textual/abc
metaclass conflict). The agent's `AgentAdapter` is the factory.

---

## 3. Add an agent tool

Tools are sensors (`ISensor`), actuators (`IActuator`), or hybrid (both).

1. **Implement** the tool in `src/agentx/agent/model/tools/<your_tool>.py`:
   ```python
   class YourTool:
       id = "your_tool"
       def sense(self) -> SensorReading: ...        # if sensor
       def get_sensor_schema(self) -> SensorSchema: ...
       def validate(self, command: ActuatorCommand) -> ValidationResult: ...  # if actuator
       def act(self, command: ActuatorCommand) -> ActuatorResult: ...
       def get_actuator_schema(self) -> ActuatorSchema: ...
   ```
2. **Register** it in `Agent._register_builtin_tools()`
   (`model/agent.py`): `self._safe_register_sensor(tool)` and/or
   `_safe_register_actuator(tool)`.
3. **Read `command.action`** (the canonical field), not
   `command.parameters.get("action")` — the latter is stripped at runtime by
   `_decision_to_command` (this was a latent bug; see feature_010 notes).
4. **Use it from a policy rule:** `EXECUTE_TOOL {tool_id:"your_tool",
   action:"<action>", ...params}` — the policy DSL dispatches it.
5. **Optional:** entry-point discovery (`tools/discovery.py`) for plugin tools.

**Built-in tools:** `FileSystemTool` (`filesystem`), `RagSensorTool`
(`rag_query`), `SessionTool` (`session`).

---

## 4. Add a feature (OMT++ process)

1. **Scaffold:** `uv run scripts/omt/new_feature.py "<name>" --type <type>`
   → creates `.meta/.../2.requirements/features/feature_NNN.<slug>/` with
   `FEATURE.md` + `plan/PLAN.md`.
2. **Analysis** → write use cases + operation list under
   `3.analysis/features/<feature>/analysis_001_*.md`.
3. **Design** → write `4.design/features/<feature>/design_001_*.md` +
   `operation_spec_001_*.md` (required for `new_screen`/`major_feature`).
4. **Declare** `omt_phase{task_type, scope, phase:"Design", feature, design_doc}`.
5. **Programming** → `omt_complete{feature, advance_to:"Programming"}`; implement;
   write impl notes under `5.implementation/features/<feature>/` + unit tests
   under `tests/features/<feature>/`.
6. **Testing** → `omt_complete{advance_to:"Testing"}`; write
   `6.testing/features/<feature>/test_report.md`.
7. **Done** → `omt_complete{advance_to:"Done"}`.
8. Update `WORK.md` and this doc set (`features.md` + relevant subsystem doc).

**Phase-exit artifact checks** (enforced by `omt_enforcer.ts`):
- Analysis→Design: `FEATURE.md` + `analysis_001_*.md`
- Design→Programming: `design_001_*.md` + `operation_spec_*.md`
- Programming→Testing: impl notes `*.md` + unit tests `test_*.py`
- Testing→Done: `test_report.md`

---

## 5. Add an AI provider

1. **Implement** `LLMProvider(ABC)` in `src/agentx/model/ai/` (see
   `providers.py`): `create_llm() -> BaseChatModel`.
2. **Expose** it via `AIService` (`model/ai/service.py`) as a factory method.
3. For the agent, the `AIServiceAdapter` (`agent/model/ai_adapter.py`)
   implements `IAIServicePartner` — inject with `agent.set_ai_service(...)`.
4. Configure API keys in `.env`; `main.py` prompts for `OPENROUTER_API_KEY` if
   missing.

---

## 6. Conventions checklist (MVC++ self-check)

Run `uv run scripts/omt/mvc_check.py [path]` — target 0 errors. Manual checks:

- [ ] View does **not** import Model (`from agent.model...`, `from ...model...`).
- [ ] Model does **not** import `ui` / `agent.view`.
- [ ] Abstract Partners are `ABC` with `@abstractmethod` (no plain classes).
- [ ] View receives its partner via constructor injection (never `new Controller()`).
- [ ] SQL only in `*_db.py` / `DP_*` / `*Database` classes.
- [ ] No `*Controller` class under `model/` (use `*Manager` / `*Service`).
- [ ] Controllers stay small (<300 loc) — extract sub-controllers if they grow.
- [ ] Every public controller method that handles a user operation has an
      operation spec docstring (pre/exceptions/post).
- [ ] File naming: `<screen>_<layer>.py` (`*_controller.py`, `*_view.py`);
      model files omit the suffix.
- [ ] Run Python via `uv` only (bare `python`/`pytest` are denied).

---

## 7. Common gotchas

- **Textual + abc metaclass conflict:** Textual `Screen` can't inherit from an
  `ABC` directly. Register the screen as a **virtual subclass**:
  `IAgentViewPartner.register(MyScreen)` (see `agent_screen.py` footer).
- **TUI navigation freeze:** never use blocking console input inside a Textual
  screen. Push a TUI sub-screen instead (see the RAG freeze fix in `WORK.md`).
- **Tool action dispatch:** `_decision_to_command` strips `tool_id` and
  `action` from `PolicyAction.parameters` into `ActuatorCommand.action`. Tools
  must read `command.action`, not `command.parameters["action"]`.
- **Goal completion scope:** a goal with `SuccessCriteria(tool_id=...)` only
  completes when *that* tool succeeds (C6). Use `tool_id=None` for "any tool".
- **Reflection without AI:** `run_cycle` skips reflection entirely when no AI
  service is wired (N11) — cycles run cleanly offline.
- **`uv` only:** `python`/`pip`/`pytest` are denied by `opencode.jsonc`. Use
  `uv run python`, `uv run pytest`, `uv run scripts/omt/mvc_check.py`.
