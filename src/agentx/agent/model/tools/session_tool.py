"""SessionTool — hybrid sensor/actuator for session meta + snapshot persistence (design §6.6)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from agentx.agent.model.tools.spec import (
    ActuatorSchema,
    IActuator,
    ISensor,
    JsonSchema,
    SensorSchema,
    ValidationResult,
)
from agentx.agent.types import (
    ActuatorCommand,
    ActuatorResult,
    ChangeType,
    EnvironmentChange,
    SensorReading,
)


class SessionTool(ISensor, IActuator):
    """Sense current session meta; act by persisting / restoring snapshots."""

    def __init__(self, agent_ref: Any | None = None) -> None:
        self.id = "session"
        self._agent = agent_ref

    def set_agent(self, agent: Any) -> None:
        self._agent = agent

    # ----------------------------------------------------------- ISensor

    def sense(self) -> SensorReading:
        if self._agent is None:
            return SensorReading(
                sensor_id=self.id,
                data={"active": False},
                timestamp=datetime.now(timezone.utc),
                confidence=0.5,
            )
        return SensorReading(
            sensor_id=self.id,
            data={
                "active": True,
                "agent_id": getattr(self._agent, "id", ""),
                "state": getattr(getattr(self._agent, "state", None), "value", ""),
            },
            timestamp=datetime.now(timezone.utc),
            confidence=0.9,
        )

    def get_sensor_schema(self) -> SensorSchema:
        return SensorSchema(
            sensor_id=self.id,
            description="Current session metadata.",
            output_schema=JsonSchema(type="object"),
            sampling_rate=None,
        )

    # --------------------------------------------------------- IActuator

    def get_actuator_schema(self) -> ActuatorSchema:
        return ActuatorSchema(
            actuator_id=self.id,
            description="Persist or restore a session snapshot.",
            input_schema=JsonSchema(type="object", required=["action"]),
            output_schema=JsonSchema(type="object"),
        )

    def validate(self, command: ActuatorCommand) -> ValidationResult:
        action = command.parameters.get("action")
        if action not in {"persist", "restore"}:
            return ValidationResult(valid=False, errors=[f"unknown action: {action}"])
        return ValidationResult(valid=True)

    def act(self, command: ActuatorCommand) -> ActuatorResult:
        vr = self.validate(command)
        if not vr.valid:
            return ActuatorResult(success=False, error="; ".join(vr.errors))
        action = command.parameters["action"]
        try:
            if action == "persist":
                if self._agent and hasattr(self._agent, "persist"):
                    snapshot_id = self._agent.persist()
                    return ActuatorResult(
                        success=True,
                        output={"snapshot_id": snapshot_id},
                        side_effects=[
                            EnvironmentChange(ChangeType.CREATE, "snapshot", snapshot_id)
                        ],
                    )
                return ActuatorResult(success=False, error="agent cannot persist")
            if action == "restore":
                snapshot_id = command.parameters.get("snapshot_id", "")
                if self._agent and hasattr(self._agent, "resume"):
                    self._agent.resume(snapshot_id)
                    return ActuatorResult(success=True, output={"restored": snapshot_id})
                return ActuatorResult(success=False, error="agent cannot restore")
            return ActuatorResult(success=False, error=f"unhandled action: {action}")
        except Exception as exc:  # noqa: BLE001
            return ActuatorResult(success=False, error=str(exc))
