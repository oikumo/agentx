"""ToolController — tool registration and execution (operation_spec §3).

N14: delegates to the :class:`IAgentModelPartner` facade instead of reaching
into the Agent's ``tool_registry`` attribute directly.
"""

from __future__ import annotations

from typing import Any

from agentx.agent.model.agent import Agent
from agentx.agent.types import ActuatorCommand, ActuatorResult


class ToolController:
    """Handles tool registration and actuator command execution."""

    def __init__(self, agent: Agent) -> None:
        self._agent = agent

    def register_tool(self, tool: Any) -> Any:
        """Register a sensor/actuator with the registry (operation spec §3.1)."""
        return self._agent.register_tool(tool)  # N14: via facade

    def unregister_tool(self, tool_id: str) -> bool:
        return self._agent.unregister_tool(tool_id)  # N14

    def execute_action(self, command: ActuatorCommand) -> ActuatorResult:
        """Validate and run an actuator command (operation spec §3.2)."""
        return self._agent.execute_tool_action(command)  # N14

    def list_tools(self) -> list[Any]:
        return self._agent.list_tools()  # N14

    def health_check(self) -> dict[str, bool]:
        return self._agent.tool_health_check()  # N14
