"""ToolController — tool registration and execution (operation_spec §3)."""

from __future__ import annotations

from typing import Any

from agentx.agent.model.agent import Agent
from agentx.agent.model.tools.spec import IActuator, ISensor, ToolSpec
from agentx.agent.types import ActuatorCommand, ActuatorResult


class ToolController:
    """Handles tool registration and actuator command execution."""

    def __init__(self, agent: Agent) -> None:
        self._agent = agent

    def register_tool(self, tool: ISensor | IActuator) -> ToolSpec:
        """Register a sensor/actuator with the ToolRegistry (operation spec §3.1)."""
        if hasattr(tool, "sense"):
            return self._agent.tool_registry.register_sensor(tool)  # type: ignore[arg-type]
        return self._agent.tool_registry.register_actuator(tool)  # type: ignore[arg-type]

    def unregister_tool(self, tool_id: str) -> bool:
        return self._agent.tool_registry.unregister(tool_id)

    def execute_action(self, command: ActuatorCommand) -> ActuatorResult:
        """Validate and run an actuator command (operation spec §3.2)."""
        return self._agent.tool_registry.execute_safely(command)

    def list_tools(self) -> list[ToolSpec]:
        return self._agent.tool_registry.list_specs()

    def health_check(self) -> dict[str, bool]:
        return self._agent.tool_registry.health_check()
