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

Threading note (feature_011 freeze fix): ``run_cycle()`` makes a synchronous
LLM HTTP call inside ``reflection_engine.reflect()`` →
``AIServiceAdapter.complete()`` → ``llm.invoke()``.  Running it on the Textual
UI thread freezes the entire event loop (Stop/Pause become unresponsive).
``RunningModal`` therefore runs the cycle loop on a **worker thread** and
communicates with the UI thread via a :class:`queue.Queue`; the UI thread polls
that queue with :meth:`set_timer` and refreshes widgets.  The worker never
touches Textual widgets directly (that would race the event loop).
"""

from __future__ import annotations

import queue
import threading
from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label, Static

from agentx.ui.tui.framework import BaseAgentXModalScreen

# Safety cap: prevents an infinite auto-run if the goal never terminates and
# the user walks away (design §9).
MAX_CYCLES = 50

# Goal statuses that terminate the auto-run (design §5).
_TERMINAL_STATUSES = frozenset({"COMPLETED", "FAILED", "ABANDONED"})


# Worker → UI thread messages.  The worker thread pushes these onto a
# ``queue.Queue``; the UI thread drains the queue inside its ``_poll`` callback
# (scheduled via ``set_timer``).  Keeping them as tiny plain objects means the
# worker never touches a Textual widget and never crosses the GIL with anything
# the event loop also mutates.
class _MsgCycle:
    """One cycle finished.  Carries the summary dict for the status line."""

    __slots__ = ("summary",)

    def __init__(self, summary: dict[str, Any]) -> None:
        self.summary = summary


class _MsgPending:
    """Reflection produced pending proposals — UI should show ReflectionModal."""

    __slots__ = ("proposals",)

    def __init__(self, proposals: list[Any]) -> None:
        # Raw ``Proposal`` objects — converted to dicts on the UI thread so the
        # worker does not need to know about the display schema.
        self.proposals = proposals


class _MsgDone:
    """The worker has exited.  ``outcome`` mirrors the dismiss schema."""

    __slots__ = ("outcome", "summary", "error")

    def __init__(
        self,
        outcome: str,
        summary: dict[str, Any],
        error: str | None = None,
    ) -> None:
        self.outcome = outcome
        self.summary = summary
        self.error = error


# ============================================================================
# GoalModal
# ============================================================================


class GoalModal(BaseAgentXModalScreen[dict | None]):
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


class RunningModal(BaseAgentXModalScreen[dict]):
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
        # UI-side state — mutated only on the UI thread.
        self._paused: bool = False
        self._auto_running: bool = True
        self._cycle_count: int = 0
        self._last_summary: dict[str, Any] = {}
        # Pending proposals captured from the worker for _on_reflection to use.
        self._pending: list[Any] = []
        # True once dismiss() has been called — guards against the worker
        # queueing a _MsgDone after Stop has already dismissed the modal.
        self._dismissed: bool = False
        # Worker communication: a thread-safe queue + two events.
        self._queue: "queue.Queue[Any]" = queue.Queue()
        self._stop_evt = threading.Event()       # set by Stop / unmount
        self._pause_evt = threading.Event()      # set when NOT paused (worker waits)
        self._pause_evt.set()                    # start un-paused
        self._worker: threading.Thread | None = None
        # True while a ReflectionModal is up; the poller is paused so it does not
        # drain the queue concurrently with the reflection callback.
        self._awaiting_reflection: bool = False

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(f"🎯 {self._goal_description}", id="run-goal")
            yield Static("Starting…", id="run-status")
            with Horizontal():
                yield Button("⏸ Pause", id="btn-pause", variant="default")
                yield Button("⏹ Stop", id="btn-stop", variant="error")

    def on_mount(self) -> None:
        """Start the worker thread + schedule the first poll."""
        self._worker = threading.Thread(
            target=self._worker_loop,
            name="FastAgent run_cycle",
            daemon=True,
        )
        self._worker.start()
        # Schedule the poller on the UI thread — fires even while the worker
        # is blocked inside llm.invoke().
        self.set_timer(0.05, self._poll)

    def on_unmount(self) -> None:
        """Signal the worker to stop so it does not outlive the modal."""
        # feature_014: call super() so BaseAgentXScreen cancels any
        # run_blocking handles (none today, but future-proofs the modal).
        super().on_unmount()
        self._auto_running = False
        self._stop_evt.set()
        self._pause_evt.set()  # release the worker if parked on pause

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-pause":
            self.action_pause_resume()
        elif event.button.id == "btn-stop":
            self.action_stop()

    # ----------------------------------------------------------- worker (off UI thread)

    def _worker_loop(self) -> None:
        """Run cycles until told to stop, the goal terminates, or the cap hits.

        Runs on a background thread — MUST NOT touch Textual widgets or call
        ``query_one`` / ``dismiss``; it only posts path messages onto the queue.
        """
        cycle_count = 0
        last_summary: dict[str, Any] = {}
        try:
            while not self._stop_evt.is_set():
                # 0. Pause gate — block here while paused, but yield to Stop.
                if not self._pause_evt.is_set():
                    while not self._pause_evt.is_set():
                        if self._stop_evt.is_set():
                            return
                        # Light sleep so Stop is observed within ~50ms.
                        self._stop_evt.wait(0.05)
                    if self._stop_evt.is_set():
                        return
                # 1. Run one cycle.  This is the blocking call (llm.invoke).
                try:
                    self._controller.run_cycle()
                except Exception as exc:  # noqa: BLE001 — surface, don't crash
                    try:
                        last_summary = self._controller.get_cycle_summary()
                    except Exception:  # noqa: BLE001
                        last_summary = {}
                    self._queue.put(_MsgDone("error", last_summary, str(exc)))
                    return
                cycle_count += 1
                last_summary = self._controller.get_cycle_summary()

                # 2. Pending reflection proposals → pause + tell the UI.
                pending = self._controller.list_pending_proposals()
                if pending:
                    # Hand the raw tuples to the UI thread for display.  We do
                    # NOT dismiss here; the UI takes over and the worker parks
                    # until _on_reflection clears the pause (or Stop fires).
                    self._queue.put(_MsgPending(pending))
                    self._pause_evt.clear()
                    while not self._pause_evt.is_set():
                        if self._stop_evt.is_set():
                            return
                        self._stop_evt.wait(0.05)
                    continue  # re-check stop, then run the next cycle

                # 3. Tell the UI about the cycle (status-line update).
                self._queue.put(_MsgCycle(last_summary))

                # 4. Goal terminal status?
                goal_status = last_summary.get("goal_status", "NONE")
                if goal_status in _TERMINAL_STATUSES:
                    self._queue.put(_MsgDone(goal_status.lower(), last_summary))
                    return

                # 5. Cycle cap.
                if cycle_count >= MAX_CYCLES:
                    self._queue.put(_MsgDone("capped", last_summary))
                    return

                # 6. Small breath so the UI can paint + process Stop/Pause
                # between cycles (also observable on the worker side).
                self._stop_evt.wait(0.1)
        finally:
            # Defensive: make sure unmount/unpause never deadlocks on us.
            self._pause_evt.set()

    # ----------------------------------------------------------- poller (UI thread)

    def _poll(self) -> None:
        """Drain the worker queue and update widgets / dismiss as needed.

        Scheduled by :meth:`on_mount` and re-scheduled by itself.  Runs on the
        UI thread, so it is the only place that calls ``query_one`` / ``dismiss``.
        """
        if self._dismissed:
            return  # already dismissing — stop polling
        # While a ReflectionModal is up, the user drives the next step — do not
        # drain the queue until _on_reflection resumes polling.
        if self._awaiting_reflection:
            self.set_timer(0.05, self._poll)
            return

        while True:
            try:
                msg = self._queue.get_nowait()
            except queue.Empty:
                break
            if isinstance(msg, _MsgCycle):
                self._last_summary = msg.summary
                self._cycle_count = msg.summary.get("cycle", self._cycle_count)
                self._refresh_status()
            elif isinstance(msg, _MsgPending):
                self._pending = msg.proposals
                self._awaiting_reflection = True
                proposals_as_dicts = [
                    {
                        "entry_id": entry_id,
                        "idx": idx,
                        "type": (
                            proposal.type.value
                            if hasattr(proposal.type, "value")
                            else str(proposal.type)
                        ),
                        "rationale": proposal.rationale or "(no rationale)",
                        "content": proposal.content,
                    }
                    for entry_id, idx, proposal in msg.proposals[:3]
                ]
                self.app.push_screen(
                    ReflectionModal(proposals_as_dicts),
                    callback=self._on_reflection,
                )
            elif isinstance(msg, _MsgDone):
                self._last_summary = msg.summary
                self._do_dismiss(msg.outcome, msg.summary, error=msg.error)
                return  # modal is dismissing — stop polling

        if not self._dismissed:
            self.set_timer(0.05, self._poll)

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
        """Called when ReflectionModal dismisses with 'approve'/'dismiss'/'stop'.

        Runs on the UI thread — safe to drive the controller and resume polling.
        """
        self._awaiting_reflection = False
        if not self._auto_running:
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
            self._stop_evt.set()
            self._do_dismiss("stopped", self._last_summary)
            return
        # "approve" or "dismiss" → release the worker from the proposal pause
        # and resume polling on the UI thread.
        self._pending = []
        self._pause_evt.set()
        self.set_timer(0.05, self._poll)

    # ----------------------------------------------------------- actions

    def action_pause_resume(self) -> None:
        """Toggle pause/resume — flips the pause event the worker waits on."""
        self._paused = not self._paused
        if self._paused:
            self._pause_evt.clear()  # worker gates on this being clear
        else:
            self._pause_evt.set()
        btn = self.query_one("#btn-pause", Button)
        if self._paused:
            btn.label = "▶ Resume"
            self.notify("Paused", timeout=1)
        else:
            btn.label = "⏸ Pause"
            self.notify("Resumed", timeout=1)

    def action_stop(self) -> None:
        """Stop the run: signal the worker, dismiss with outcome 'stopped'."""
        self._auto_running = False
        self._stop_evt.set()
        self._pause_evt.set()  # unstick the worker if parked on pause
        self._do_dismiss("stopped", self._last_summary)

    def _do_dismiss(self, outcome: str, summary: dict[str, Any],
                    error: str | None = None) -> None:
        """Single dismissal path — guarded against double-dismiss."""
        if self._dismissed:
            return
        self._dismissed = True
        payload: dict[str, Any] = {"outcome": outcome, "summary": summary}
        if error is not None:
            payload["error"] = error
        self.dismiss(payload)


# ============================================================================
# ReflectionModal
# ============================================================================


class ReflectionModal(BaseAgentXModalScreen[str]):
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


class ResultModal(BaseAgentXModalScreen[str]):
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
