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
from textual.widgets import Footer, Header, Static

from agentx.agent.view.tui.fast_agent_modals import (
    GoalModal,
    ResultModal,
    RunningModal,
)
from agentx.ui.tui.framework import BaseAgentXScreen


class FastAgentTUIScreen(BaseAgentXScreen):
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
        super().__init__(controller)
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
        # S3+S8 (feature_015): pass constraints and manual=True so the goal
        # is created with kind="manual" and constraints are visible.
        if self._controller:
            try:
                self._controller.submit_goal(description, constraints=constraints, manual=True)
            except Exception as exc:  # noqa: BLE001
                self.notify(f"Failed to submit goal: {exc}", severity="error")
                self.app.pop_screen()
                return
        # S3: constraints are now passed to the controller (no longer dead).
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
            # S4 (feature_015): save asynchronously via run_blocking so the
            # UI thread is not blocked on SQLite I/O (mirrors AgentTUIScreen).
            if self._controller:
                self.run_blocking(
                    self._controller.save_snapshot,
                    on_result=self._on_save_done,
                    on_error=self._on_save_error,
                )
            else:
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

    def _on_save_done(self, snap_id: str) -> None:
        """S4 (feature_015): callback for successful async save."""
        if snap_id:
            self.notify(f"Session saved ({snap_id[:8]}…)", timeout=3)
        else:
            self.notify("Save failed (persistence error)", severity="error")
        self.app.push_screen(
            ResultModal(self._last_outcome, self._last_summary),
            callback=self._on_result,
        )

    def _on_save_error(self, exc: Exception) -> None:
        """S4 (feature_015): callback for failed async save."""
        self.notify(f"Save failed: {exc}", severity="error")
        self.app.push_screen(
            ResultModal(self._last_outcome, self._last_summary),
            callback=self._on_result,
        )

    # ----------------------------------------------------------- actions

    def action_back(self) -> None:
        """Escape — return to the Main screen.

        This only fires when no modal is on top (edge case, e.g. between
        modals).  Normally Escape is swallowed by the active modal.
        """
        self.app.pop_screen()
