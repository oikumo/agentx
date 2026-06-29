"""AgentAdapter — factory wiring AgentController ↔ AgentTUIScreen (feature_004 integration, design §10).

Provides a single entry point that the main TUI app calls to push the agent
screen onto the screen stack.  Keeps the wiring self-contained in the agent
module so the existing UI code is not modified.
"""

from __future__ import annotations

from typing import Any, cast

from agentx.agent.controller.agent_controller import AgentController
from agentx.agent.interfaces import IAgentViewPartner
from agentx.agent.model.agent import Agent
from agentx.agent.types import AgentConfig
from agentx.agent.view.tui.agent_screen import AgentTUIScreen


class AgentAdapter:
    """Creates and wires the Agent TUI screen + controller."""

    @staticmethod
    def create(config: AgentConfig) -> tuple[Agent, AgentController, AgentTUIScreen]:
        """Build a fully wired agent triad.

        Returns ``(agent, controller, screen)``.  The caller pushes *screen*
        onto the Textual app stack.
        """
        agent = Agent(config)
        controller = AgentController(agent)
        screen = AgentTUIScreen(controller)
        controller.set_view(cast(IAgentViewPartner, screen))
        return agent, controller, screen

    @staticmethod
    def create_screen(controller: AgentController) -> AgentTUIScreen:
        """Create a TUI screen for an existing controller."""
        screen = AgentTUIScreen(controller)
        controller.set_view(cast(IAgentViewPartner, screen))
        return screen
