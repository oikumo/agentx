"""FileSystemTool — sandboxed hybrid sensor/actuator (design §6.6)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
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


class FileSystemTool(ISensor, IActuator):
    """Filesystem sensor/actuator. Sandboxed to ``sandbox_root``."""

    #: m10: cap on files returned per sense() to avoid unbounded scans on huge trees.
    MAX_FILES = 2000

    def __init__(self, sandbox_root: str | Path) -> None:
        self.id = "filesystem"
        self._root = Path(sandbox_root).resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------------------------- ISensor

    def sense(self) -> SensorReading:
        files: dict[str, Any] = {}
        if self._root.exists():
            count = 0
            for p in self._root.rglob("*"):
                if p.is_file():
                    try:
                        files[str(p.relative_to(self._root))] = p.stat().st_size
                    except (OSError, ValueError):
                        continue
                    count += 1
                    if count >= self.MAX_FILES:  # m10: stop pathological scans
                        break
        return SensorReading(
            sensor_id=self.id,
            data=files,
            timestamp=datetime.now(timezone.utc),
            confidence=0.95,
        )

    def get_sensor_schema(self) -> SensorSchema:
        return SensorSchema(
            sensor_id=self.id,
            description="Filesystem listing (sandboxed).",
            output_schema=JsonSchema(type="object"),
            sampling_rate=None,
        )

    # --------------------------------------------------------- IActuator

    def get_actuator_schema(self) -> ActuatorSchema:
        """Unified schema for the hybrid tool (covers sensor + actuator)."""
        return ActuatorSchema(
            actuator_id=self.id,
            description="Filesystem CRUD + listing (sandboxed).",
            input_schema=JsonSchema(
                type="object",
                required=["action", "path"],
            ),
            output_schema=JsonSchema(type="object"),
        )

    def validate(self, command: ActuatorCommand) -> ValidationResult:
        path = command.parameters.get("path")
        if not path:
            return ValidationResult(valid=False, errors=["missing 'path' parameter"])
        target = (self._root / path).resolve()
        # C1 (feature_015): use is_relative_to for true path-containment.
        # str().startswith() is a string-prefix check — a sibling directory
        # whose name starts with the sandbox name (e.g. sandbox_evil) bypasses it.
        if not target.is_relative_to(self._root):
            return ValidationResult(valid=False, errors=["path escapes sandbox"])
        # Read the canonical command.action (set by _decision_to_command); fall
        # back to parameters for backward compat with direct callers (feature_010
        # bug fix: previously only read parameters, so EXECUTE_TOOL create/update
        # silently defaulted to "read" at runtime).
        action = command.action or command.parameters.get("action", "read")
        if action not in {"create", "read", "update", "delete"}:
            return ValidationResult(
                valid=False, errors=[f"unknown action: {action}"]
            )
        return ValidationResult(valid=True)

    def act(self, command: ActuatorCommand) -> ActuatorResult:
        vr = self.validate(command)
        if not vr.valid:
            return ActuatorResult(success=False, error="; ".join(vr.errors))
        path = command.parameters["path"]
        target = (self._root / path).resolve()
        action = command.action or command.parameters.get("action", "read")
        content = command.parameters.get("content", "")
        side_effects: list[EnvironmentChange] = []
        try:
            if action == "read":
                if not target.is_file():
                    return ActuatorResult(success=False, error="file not found")
                text = target.read_text(encoding="utf-8")
                return ActuatorResult(success=True, output={"content": text, "path": path})
            if action == "create":
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(str(content), encoding="utf-8")
                side_effects.append(EnvironmentChange(ChangeType.CREATE, path, content))
            elif action == "update":
                target.write_text(str(content), encoding="utf-8")
                side_effects.append(EnvironmentChange(ChangeType.UPDATE, path, content))
            elif action == "delete":
                if target.is_file():
                    target.unlink()
                    side_effects.append(EnvironmentChange(ChangeType.DELETE, path))
            return ActuatorResult(success=True, output={"path": path, "action": action}, side_effects=side_effects)
        except OSError as exc:
            return ActuatorResult(success=False, error=str(exc))
