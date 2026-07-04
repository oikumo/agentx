"""FastAgentTUIScreen — host Screen for the Fast Agent modal flow (feature_011).

This is a plain :class:`textual.screen.Screen` (not a ``ModalScreen``) that owns
the :class:`AgentController` and orchestrates the modal stack:

    GoalModal → RunningModal → [ReflectionModal] → ResultModal

It receives the controller from :meth:`MainController.show_fast_agent` and
pushes the first modal (``GoalModal``) on mount.  Each modal's ``dismiss``
value triggers a callback that pushes the next modal (or pops the host).

Design: ``design_001_fast_agent.md`` §5–§6.
Operation spec: ``operation_spec_001_fast_agent.md`` (FastAgentTUIScreen ops).

MVC++: this is a View — it imports no Model module.  The controller is
duck-typed as ``Any`` (matches ``AgentDemoScreen`` / ``AgentTUIScreen``).
"""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from agentx.agent.view.tui.fast_agent_modals import (
    GoalModal,
    ResultModal,
    RunningModal,
)


class FastAgentTUIScreen(Screen):
    """Host screen for the Fast Agent modal-dialog flow.

    Owns the controller and drives the modal stack via push-screen callbacks.
    The screen itself is mostly invisible (modals cover it) but provides an
    escape hatch back to the Main screen.
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
    ]

    DEFAULT_CSS = """
    FastAgentTUIScreen {
        layout: vertical;
    }
    FastAgentTUIScreen #fast-agent-bg {
        height: 1fr;
        padding: 2 4;
        color: $text-muted;
        text-align: center;
    }
    """

    def __init__(self, controller: Any | None = None) -> None:
        super().__init__()
        self._controller = controller
        # Stash the last outcome/summary so "Save" can re-push ResultModal.
        self._last_outcome: str = ""
        self._last_summary: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "⚡ Fast Agent\n\nPress Escape to return to the menu.",
            id="fast-agent-bg",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Push the first modal — the goal input."""
        self.app.push_screen(GoalModal(), callback=self._on_goal)

    # ----------------------------------------------------------- modal callbacks

    def _on_goal(self, value: dict | None) -> None:
        """Called when GoalModal dismisses."""
        if value is None:
            # Cancelled — pop the host screen → back to Main.
            self.app.pop_screen()
            return
        description = value.get("description", "")
        constraints = value.get("constraints", "")
        # Submit the goal to the controller.  Fast Agent uses manual success
        # criteria (the user presses Stop when done).
        if self._controller:
            try:
                # SuccessCriteria with kind="manual" — goal never auto-completes.
                self._controller.submit_goal(description)
            except Exception as exc:  # noqa: BLE001
                self.notify(f"Failed to submit goal: {exc}", severity="error")
                self.app.pop_screen()
                return
        # Constraints are captured but unused in v1 (design §5 note).
        if constraints:
            self.notify("Constraints noted (not used in v1)", timeout=2)
        # Push the RunningModal — it auto-runs cycles.
        self.app.push_screen(
            RunningModal(self._controller, description),
            callback=self._on_running,
        )

    def _on_running(self, value: dict | None) -> None:
        """Called when RunningModal dismisses with an outcome."""
        if value is None:
            value = {"outcome": "stopped", "summary": {}}
        self._last_outcome = value.get("outcome", "stopped")
        self._last_summary = value.get("summary", {})
        error = value.get("error")
        if error:
            self.notify(f"Error: {error}", severity="error", timeout=5)
        self.app.push_screen(
            ResultModal(self._last_outcome, self._last_summary),
            callback=self._on_result,
        )

    def _on_result(self, action: str | None) -> None:
        """Called when ResultModal dismisses with 'save'/'new'/'back'."""
        if action is None:
            action = "back"
        if action == "save":
            # Save is a side-effect — save and re-show the ResultModal.
            if self._controller:
                try:
                    snap_id = self._controller.save_snapshot()
                    self.notify(f"Session saved ({snap_id[:8]}…)", timeout=3)
                except Exception as exc:  # noqa: BLE001
                    self.notify(f"Save failed: {exc}", severity="error")
            self.app.push_screen(
                ResultModal(self._last_outcome, self._last_summary),
                callback=self._on_result,
            )
        elif action == "new":
            # Fresh goal, same agent/controller.
            self.app.push_screen(GoalModal(), callback=self._on_goal)
        elif action == "back":
            # Pop the host screen → back to Main.
            self.app.pop_screen()

    # ----------------------------------------------------------- actions

    def action_back(self) -> None:
        """Escape — return to the Main screen.

        This only fires when no modal is on top (edge case, e.g. between
        modals).  Normally Escape is swallowed by the active modal.
        """
        self.app.pop_screen()
