"""Fast Agent modal dialogs (feature_011).

Four :class:`textual.screen.ModalScreen` subclasses that form the Fast Agent
flow: ``GoalModal`` → ``RunningModal`` → ``ReflectionModal`` → ``ResultModal``.

These are pure View components — they import **no** Model module
(``agentx.agent.model.*``, ``agentx.agent.types``).  The ``RunningModal``
receives an :class:`AgentController` (duck-typed as ``Any``) and queries it via
``run_cycle()`` / ``get_cycle_summary()`` / ``list_pending_proposals()`` /
``approve_proposal()``.  The other modals receive only plain dicts and strings.

Design: ``design_001_fast_agent.md`` §5–§6.
Operation spec: ``operation_spec_001_fast_agent.md``.
"""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

# Safety cap: prevents an infinite auto-run if the goal never terminates and
# the user walks away (design §9).
MAX_CYCLES = 50

# Goal statuses that terminate the auto-run (design §5).
_TERMINAL_STATUSES = frozenset({"COMPLETED", "FAILED", "ABANDONED"})


# ============================================================================
# GoalModal
# ============================================================================


class GoalModal(ModalScreen[dict | None]):
    """Capture the user's natural-language goal (+ optional constraints).

    Dismisses with ``{"description": str, "constraints": str}`` on Start, or
    ``None`` on Cancel / Escape.
    """

    BINDINGS = [Binding("escape", "cancel", "Cancel", show=False)]

    DEFAULT_CSS = """
    GoalModal {
        align: center middle;
    }
    GoalModal > Vertical {
        width: 70;
        max-width: 90%;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 1 2;
    }
    GoalModal #goal-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin-bottom: 1;
    }
    GoalModal #goal-hint {
        color: $text-muted;
        text-style: italic;
        margin-bottom: 1;
    }
    GoalModal Input {
        width: 100%;
        margin-bottom: 1;
    }
    GoalModal #constraints-hint {
        color: $text-muted;
        text-style: italic;
    }
    GoalModal Horizontal {
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    GoalModal Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("⚡ What do you want the agent to do?", id="goal-title")
            yield Static(
                "Describe your goal in plain English. The agent runs until you press Stop.",
                id="goal-hint",
            )
            yield Input(
                placeholder="e.g. Find Python files with TODO comments and list them",
                id="goal-input",
            )
            yield Static("Advanced (optional, not used yet):", id="constraints-hint")
            yield Input(
                placeholder="Any constraints… (optional)",
                id="constraints-input",
            )
            with Horizontal():
                yield Button("▶ Start", id="btn-start", variant="success")
                yield Button("✕ Cancel", id="btn-cancel", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-start":
            self.action_start()
        elif event.button.id == "btn-cancel":
            self.action_cancel()

    def action_start(self) -> None:
        """Validate and dismiss with the goal description."""
        goal_input = self.query_one("#goal-input", Input)
        description = goal_input.value.strip()
        if not description:
            self.notify("Please enter a goal description.", severity="warning")
            goal_input.focus()
            return
        constraints = self.query_one("#constraints-input", Input).value.strip()
        self.dismiss({"description": description, "constraints": constraints})

    def action_cancel(self) -> None:
        """Dismiss with None — caller will pop the host screen."""
        self.dismiss(None)


# ============================================================================
# RunningModal
# ============================================================================


class RunningModal(ModalScreen[dict]):
    """Auto-run agent cycles and show live status.

    Dismisses with ``{"outcome": str, "summary": dict}`` when the goal reaches a
    terminal status, the user presses Stop, or the cycle cap is hit.
    """

    BINDINGS = [
        Binding("escape", "stop", "Stop", show=True),
    ]

    DEFAULT_CSS = """
    RunningModal {
        align: center middle;
    }
    RunningModal > Vertical {
        width: 72;
        max-width: 92%;
        height: auto;
        background: $surface;
        border: solid $accent;
        padding: 1 2;
    }
    RunningModal #run-goal {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    RunningModal #run-status {
        background: $boost;
        padding: 1;
        margin-bottom: 1;
        height: 3;
    }
    RunningModal Horizontal {
        height: auto;
        align: center middle;
    }
    RunningModal Button {
        margin: 0 1;
    }
    """

    def __init__(self, controller: Any, goal_description: str) -> None:
        super().__init__()
        self._controller = controller
        self._goal_description = goal_description
        self._paused: bool = False
        self._running: bool = True
        self._cycle_count: int = 0
        self._last_summary: dict[str, Any] = {}
        # Pending proposals captured during _tick for _on_reflection to use.
        self._pending: list[Any] = []

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(f"🎯 {self._goal_description}", id="run-goal")
            yield Static("Starting…", id="run-status")
            with Horizontal():
                yield Button("⏸ Pause", id="btn-pause", variant="default")
                yield Button("⏹ Stop", id="btn-stop", variant="error")

    def on_mount(self) -> None:
        """Start the auto-run loop."""
        self._tick()

    def on_unmount(self) -> None:
        """Stop scheduled ticks when the modal is popped."""
        self._running = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-pause":
            self.action_pause_resume()
        elif event.button.id == "btn-stop":
            self.action_stop()

    # ----------------------------------------------------------- auto-run loop

    def _tick(self) -> None:
        """Run one cycle, refresh display, check termination, schedule next."""
        if not self._running or self._paused:
            return

        try:
            self._controller.run_cycle()
        except Exception as exc:  # noqa: BLE001 — surface to user, don't crash
            self._last_summary = self._controller.get_cycle_summary()
            self.dismiss({"outcome": "error", "summary": self._last_summary,
                          "error": str(exc)})
            return

        self._cycle_count += 1
        self._last_summary = self._controller.get_cycle_summary()
        self._refresh_status()

        # 1. Check for pending reflection proposals → pause + show ReflectionModal.
        pending = self._controller.list_pending_proposals()
        if pending:
            self._pending = pending
            proposals_as_dicts = [
                {
                    "entry_id": entry_id,
                    "idx": idx,
                    "type": proposal.type.value,
                    "rationale": proposal.rationale or "(no rationale)",
                    "content": proposal.content,
                }
                for entry_id, idx, proposal in pending[:3]  # show first 3
            ]
            self.app.push_screen(
                ReflectionModal(proposals_as_dicts),
                callback=self._on_reflection,
            )
            return  # pause — _on_reflection will resume or dismiss

        # 2. Check goal terminal status.
        goal_status = self._last_summary.get("goal_status", "NONE")
        if goal_status in _TERMINAL_STATUSES:
            self.dismiss({"outcome": goal_status.lower(), "summary": self._last_summary})
            return

        # 3. Safety cap.
        if self._cycle_count >= MAX_CYCLES:
            self.dismiss({"outcome": "capped", "summary": self._last_summary})
            return

        # 4. Schedule next cycle (cooperative — yields to the event loop).
        self.call_after_refresh(self._tick)

    def _refresh_status(self) -> None:
        """Update the status line widget from the last summary."""
        s = self._last_summary
        tool = s.get("last_tool") or "—"
        action = s.get("last_action", "(none)")
        phase = s.get("phase", "?")
        cycle = s.get("cycle", 0)
        line = f"Cycle {cycle} · {phase} · tool: {tool}\n{action}"
        try:
            self.query_one("#run-status", Static).update(line)
        except Exception:
            pass  # widget not mounted yet — skip

    # ----------------------------------------------------------- reflection callback

    def _on_reflection(self, choice: str | None) -> None:
        """Called when ReflectionModal dismisses with 'approve'/'dismiss'/'stop'."""
        if not self._running:
            return
        if choice is None:
            choice = "dismiss"  # treat None as dismiss (shouldn't happen)
        if choice == "approve" and self._pending:
            entry_id, idx, _ = self._pending[0]
            try:
                self._controller.approve_proposal(entry_id, idx)
            except Exception as exc:  # noqa: BLE001
                self.notify(f"Approval failed: {exc}", severity="warning")
        elif choice == "stop":
            self.dismiss({"outcome": "stopped", "summary": self._last_summary})
            return
        # "approve" or "dismiss" → resume the loop.
        self._pending = []
        self.call_after_refresh(self._tick)

    # ----------------------------------------------------------- actions

    def action_pause_resume(self) -> None:
        """Toggle pause/resume."""
        self._paused = not self._paused
        btn = self.query_one("#btn-pause", Button)
        if self._paused:
            btn.label = "▶ Resume"
            self.notify("Paused", timeout=1)
        else:
            btn.label = "⏸ Pause"
            self.notify("Resumed", timeout=1)
            self.call_after_refresh(self._tick)

    def action_stop(self) -> None:
        """Stop the run and dismiss with outcome 'stopped'."""
        self._running = False
        self.dismiss({"outcome": "stopped", "summary": self._last_summary})


# ============================================================================
# ReflectionModal
# ============================================================================


class ReflectionModal(ModalScreen[str]):
    """Show a pending self-improvement proposal and ask the user what to do.

    Constructor receives proposals as ``list[dict]`` (already converted by
    ``RunningModal`` so this modal imports no Model types).

    Dismisses with ``"approve"``, ``"dismiss"``, or ``"stop"``.
    """

    BINDINGS = [Binding("escape", "dismiss_choice", "Dismiss", show=False)]

    DEFAULT_CSS = """
    ReflectionModal {
        align: center middle;
    }
    ReflectionModal > Vertical {
        width: 72;
        max-width: 92%;
        height: auto;
        background: $surface;
        border: solid $warning;
        padding: 1 2;
    }
    ReflectionModal #refl-title {
        text-style: bold;
        color: $warning;
        margin-bottom: 1;
    }
    ReflectionModal .proposal {
        background: $boost;
        padding: 0 1;
        margin-bottom: 1;
    }
    ReflectionModal .prop-type {
        text-style: bold;
        color: $warning;
    }
    ReflectionModal .prop-rationale {
        color: $text;
    }
    ReflectionModal .prop-content {
        color: $text-muted;
    }
    ReflectionModal Horizontal {
        height: auto;
        align: center middle;
    }
    ReflectionModal Button {
        margin: 0 1;
    }
    """

    def __init__(self, proposals: list[dict[str, Any]]) -> None:
        super().__init__()
        self._proposals = proposals

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("🤔 The agent wants to improve itself:", id="refl-title")
            for n, prop in enumerate(self._proposals, 1):
                with Vertical(classes="proposal"):
                    yield Static(
                        f"#{n} [{prop['type']}]", classes="prop-type"
                    )
                    yield Static(prop["rationale"], classes="prop-rationale")
                    yield Static(
                        f"content: {prop['content']}", classes="prop-content"
                    )
            if len(self._proposals) < self._full_count_hint():
                yield Static(
                    f"(showing first {len(self._proposals)} proposals)",
                    classes="prop-content",
                )
            with Horizontal():
                yield Button("✓ Approve", id="btn-approve", variant="success")
                yield Button("✕ Dismiss", id="btn-dismiss", variant="default")
                yield Button("⏹ Stop", id="btn-stop", variant="error")

    def _full_count_hint(self) -> int:
        """Placeholder for future use — currently equals len(proposals)."""
        return len(self._proposals)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-approve":
            self.dismiss("approve")
        elif event.button.id == "btn-dismiss":
            self.dismiss("dismiss")
        elif event.button.id == "btn-stop":
            self.dismiss("stop")

    def action_dismiss_choice(self) -> None:
        """Escape → Dismiss (leave proposal pending, resume run)."""
        self.dismiss("dismiss")


# ============================================================================
# ResultModal
# ============================================================================


class ResultModal(ModalScreen[str]):
    """Show the run outcome and offer next actions.

    Dismisses with ``"save"``, ``"new"``, or ``"back"``.
    """

    BINDINGS = [Binding("escape", "back", "Back", show=True)]

    DEFAULT_CSS = """
    ResultModal {
        align: center middle;
    }
    ResultModal > Vertical {
        width: 68;
        max-width: 90%;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 1 2;
    }
    ResultModal #result-outcome {
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }
    ResultModal #result-detail {
        color: $text-muted;
        margin-bottom: 1;
    }
    ResultModal Horizontal {
        height: auto;
        align: center middle;
    }
    ResultModal Button {
        margin: 0 1;
    }
    """

    # Outcome → (icon, label, color-class)
    _OUTCOME_LABELS: dict[str, tuple[str, str]] = {
        "completed": ("✓", "Goal achieved"),
        "failed": ("✗", "Goal failed"),
        "abandoned": ("○", "Goal abandoned"),
        "stopped": ("■", "Goal stopped"),
        "capped": ("⏸", "Reached cycle cap (50)"),
        "error": ("⚠", "Error during run"),
    }

    def __init__(self, outcome: str, summary: dict[str, Any]) -> None:
        super().__init__()
        self._outcome = outcome
        self._summary = summary

    def compose(self) -> ComposeResult:
        icon, label = self._OUTCOME_LABELS.get(self._outcome, ("?", self._outcome))
        cycle = self._summary.get("cycle", 0)
        last_action = self._summary.get("last_action", "(none)")
        proposals = self._summary.get("pending_proposals", 0)

        with Vertical():
            yield Static(f"{icon} {label}", id="result-outcome")
            yield Static(
                f"Cycles run: {cycle}  ·  Pending proposals: {proposals}",
                id="result-detail",
            )
            yield Static(f"Last action: {last_action}", id="result-last-action")
            with Horizontal():
                yield Button("💾 Save session", id="btn-save", variant="primary")
                yield Button("⚡ New goal", id="btn-new", variant="success")
                yield Button("← Back to menu", id="btn-back", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self.dismiss("save")
        elif event.button.id == "btn-new":
            self.dismiss("new")
        elif event.button.id == "btn-back":
            self.dismiss("back")

    def action_back(self) -> None:
        """Escape → Back to menu."""
        self.dismiss("back")
