"""
ReAct View — Presentation layer.

Defines IReActViewPartner (Abstract Partner) at the top,
then ReActView which depends only on that interface.

Rules followed (OMT++ Agent Guide §6):
  - Abstract Partner is ABC, not plain class
  - View receives partner via constructor injection
  - View has ZERO knowledge of Model or Controller
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from agentx.ui.common.ui_console import UIConsole


# ─────────────────────────────────────────────────────────
# Abstract Partner Interface (contract between View and Controller)
# ─────────────────────────────────────────────────────────


class IReActViewPartner(ABC):
    """Abstract Partner for ReActView.

    The Controller implements this interface.
    The View calls back to the Controller through it.
    """

    @abstractmethod
    def process_task(self, task: str) -> bool:
        """Process a user task through the ReAct agent. Return True to continue."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Clean up and signal the view to exit."""
        ...


# ─────────────────────────────────────────────────────────
# View
# ─────────────────────────────────────────────────────────


class ReActView:
    """ReAct screen view.

    Responsibilities:
      - Capture user input
      - Display agent responses (thoughts, tool calls, observations, answers)
      - Delegate to Controller via IReActViewPartner

    KNOWS:  IReActViewPartner (interface only)
    KNOWS:  UIConsole (infrastructure)
    KNOWS:  NOTHING about Model or concrete Controller
    """

    def __init__(self, partner: IReActViewPartner) -> None:
        self._partner = partner
        self.console = UIConsole("(react)")

    # ── Screen lifecycle ──────────────────────────────────

    def show(self) -> None:
        """Main REPL loop. Calls back to partner on each input."""
        self.console.success("ReAct Agent — Reason + Act Loop")
        self.console.info(
            "Describe a task. The agent will reason, use tools, and produce an answer."
        )
        self.console.info("Type 'quit' or 'exit' to return.\n")

        while True:
            user_input = self.console.capture_input()
            if not user_input:
                continue

            if user_input.strip().lower() in ("quit", "exit"):
                self._partner.close()
                return

            self._partner.process_task(user_input)

    # ── Display helpers ───────────────────────────────────

    def display_thought(self, content: str) -> None:
        """Show the agent's reasoning step."""
        self.console.info(f"  {content}")

    def display_tool_call(self, content: str) -> None:
        """Show a tool being called."""
        self.console.waning(f"  ⚡ {content}")

    def display_observation(self, content: str) -> None:
        """Show the result returned by a tool."""
        self.console.success(f"  📥 {content}")

    def display_answer(self, content: str) -> None:
        """Show the agent's final answer."""
        self.console.header("ANSWER")
        self.console.success(content)

    def display_error(self, message: str) -> None:
        """Show an error message."""
        self.console.error(message)
