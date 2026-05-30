"""
ReAct Controller — Application logic layer.

Implements IReActViewPartner (Abstract Partner).
Orchestrates between ReActView and ReActAgent.

Rules followed (OMT++ Agent Guide):
  - Controller implements Abstract Partner interface (§6)
  - Controller creates View + Model (§5)
  - Controller contains orchestration, not UI, not SQL (§5)
"""

from __future__ import annotations

from agentx.ui.screens.react.react_view import ReActView, IReActViewPartner
from agentx.model.react.react_agent import ReActAgent


class ReActController(IReActViewPartner):
    """Controller for the ReAct screen.

    Operation: show()
      Preconditions:  None
      Postconditions: View REPL loop runs; returns when user quits

    Operation: process_task(task)
      Preconditions:
        - task is non-empty
        - ReActAgent is initialized
      Exceptions:
        - Agent execution fails: error displayed, loop continues
      Postconditions:
        - Agent events streamed to View
        - User sees reasoning, tool calls, observations, and final answer
    """

    def __init__(self) -> None:
        self._view = ReActView(self)          # Pass self as Abstract Partner
        self._agent = ReActAgent()

    # ── Entry point ───────────────────────────────────────

    def show(self) -> None:
        """Start the ReAct screen. Takes over the REPL until user quits."""
        self._view.show()

    # ── IReActViewPartner implementation ──────────────────

    def process_task(self, task: str) -> bool:
        """Process a user task through the ReAct agent (callback from View)."""
        try:
            for event in self._agent.stream(task):
                event_type = event["event_type"]
                content = event["content"]

                match event_type:
                    case "thought":
                        self._view.display_thought(content)
                    case "tool_call":
                        self._view.display_tool_call(content)
                    case "observation":
                        self._view.display_observation(content)
                    case "answer":
                        self._view.display_answer(content)
                    case _:
                        self._view.display_thought(content)

            return True

        except Exception as e:
            self._view.display_error(f"Agent execution failed: {e}")
            return True

    def close(self) -> None:
        """Clean up and prepare to exit (callback from View)."""
        pass
