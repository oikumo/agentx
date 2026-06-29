"""Tool registry — dict-backed O(1) lookup (design §6.4).

Registration is fail-fast: schemas are structurally validated before insert.
Implements :class:`IToolRegistryPartner` so the controller and TUI depend on
the abstraction, not the concrete registry.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from agentx.agent.interfaces import IToolRegistryPartner
from agentx.agent.model.tools.spec import (
    ActuatorSchema,
    DuplicateToolError,
    IActuator,
    ISensor,
    JsonSchema,
    SensorSchema,
    ToolKind,
    ToolSchemaError,
    ToolSpec,
    ValidationResult,
)
from agentx.agent.types import ActuatorCommand, ActuatorResult, EnvironmentChange, ChangeType


class ToolRegistry(IToolRegistryPartner):
    """Model-layer registry. Dict-backed (O(1) lookup, <5ms per NFR P3)."""

    def __init__(self) -> None:
        self._sensors: dict[str, ISensor] = {}
        self._actuators: dict[str, IActuator] = {}
        self._specs: dict[str, ToolSpec] = {}

    # ---------------------------------------------------------- registration

    def register_sensor(self, sensor: ISensor) -> ToolSpec:
        schema = sensor.get_sensor_schema()
        self._validate_schema(schema.output_schema)
        if sensor.id in self._sensors:
            raise DuplicateToolError(f"sensor already registered: {sensor.id}")
        self._sensors[sensor.id] = sensor
        spec = self._build_sensor_spec(sensor, schema)
        # upgrade to hybrid if an actuator with the same id exists
        if sensor.id in self._actuators:
            spec.kind = ToolKind.HYBRID
        self._specs[sensor.id] = spec
        return spec

    def register_actuator(self, actuator: IActuator) -> ToolSpec:
        schema = actuator.get_actuator_schema()
        self._validate_schema(schema.input_schema)
        self._validate_schema(schema.output_schema)
        if actuator.id in self._actuators:
            raise DuplicateToolError(f"actuator already registered: {actuator.id}")
        self._actuators[actuator.id] = actuator
        spec = self._build_actuator_spec(actuator, schema)
        # upgrade to hybrid if a sensor with the same id exists
        if actuator.id in self._sensors:
            spec.kind = ToolKind.HYBRID
        self._specs[actuator.id] = spec
        return spec

    def unregister(self, tool_id: str) -> bool:
        removed = False
        if tool_id in self._sensors:
            del self._sensors[tool_id]
            removed = True
        if tool_id in self._actuators:
            del self._actuators[tool_id]
            removed = True
        if tool_id in self._specs:
            del self._specs[tool_id]
            removed = True
        return removed

    # ------------------------------------------------------------- discovery

    def get_sensor(self, sid: str) -> ISensor:
        return self._sensors[sid]

    def get_actuator(self, aid: str) -> IActuator:
        return self._actuators[aid]

    def list_sensors(self) -> list[str]:
        return list(self._sensors)

    def list_actuators(self) -> list[str]:
        return list(self._actuators)

    def get_spec(self, tool_id: str) -> ToolSpec:
        return self._specs[tool_id]

    def list_specs(self) -> list[ToolSpec]:
        return list(self._specs.values())

    # --------------------------------------------------------------- health

    def health_check(self) -> dict[str, bool]:
        alive: dict[str, bool] = {}
        for sid, sensor in self._sensors.items():
            try:
                sensor.get_sensor_schema()
                alive[sid] = True
            except Exception:
                alive[sid] = False
        for aid, actuator in self._actuators.items():
            if aid not in alive:
                try:
                    actuator.get_actuator_schema()
                    alive[aid] = True
                except Exception:
                    alive[aid] = False
        return alive

    # ------------------------------------------------------- safe execution

    def execute_safely(self, command: ActuatorCommand) -> ActuatorResult:
        """Validate and run an actuator command (design §11.1)."""
        actuator = self._actuators.get(command.actuator_id)
        if actuator is None:
            return ActuatorResult(
                success=False, error=f"unknown actuator: {command.actuator_id}"
            )
        vr = actuator.validate(command)
        if not vr.valid:
            return ActuatorResult(
                success=False, error="; ".join(vr.errors) or "validation failed"
            )
        start = datetime.now(timezone.utc)
        try:
            result = actuator.act(command)
        except Exception as exc:  # noqa: BLE001 — non-fatal per design §11.1
            elapsed = (datetime.now(timezone.utc) - start).total_seconds()
            return ActuatorResult(
                success=False,
                error=f"Tool {command.actuator_id} failed: {exc}",
                duration_ms=int(elapsed * 1000),
            )
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        if result.duration_ms == 0:
            result.duration_ms = int(elapsed * 1000)
        return result

    # ------------------------------------------------------------- internals

    def _build_sensor_spec(
        self, sensor: ISensor, schema: SensorSchema
    ) -> ToolSpec:
        return ToolSpec(
            tool_id=sensor.id,
            name=sensor.id,
            description=schema.description,
            kind=ToolKind.SENSOR,
            input_schema=None,
            output_schema=schema.output_schema,
            side_effects=False,
            sampling_rate=schema.sampling_rate,
        )

    def _build_actuator_spec(
        self, actuator: IActuator, schema: ActuatorSchema
    ) -> ToolSpec:
        return ToolSpec(
            tool_id=actuator.id,
            name=actuator.id,
            description=schema.description,
            kind=ToolKind.ACTUATOR,
            input_schema=schema.input_schema,
            output_schema=schema.output_schema,
            side_effects=True,
        )

    @staticmethod
    def _validate_schema(schema: JsonSchema | None) -> None:
        """Structural validation; raise :class:`ToolSchemaError` on mismatch."""
        if schema is None:
            return
        if not isinstance(schema.type, str) or not schema.type:
            raise ToolSchemaError("schema.type must be a non-empty string")
        if schema.type == "object" and schema.properties is None:
            raise ToolSchemaError("object schema requires properties")
