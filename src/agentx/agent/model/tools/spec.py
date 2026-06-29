"""Tool specifications and sensor/actuator interfaces (design §6).

A :class:`ToolSpec` is the unified, serializable descriptor the registry stores
for every tool.  :class:`ISensor` and :class:`IActuator` are the Abstract
Partner contracts that concrete tools implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from agentx.agent.types import (
    ActuatorCommand,
    ActuatorResult,
    JsonSchema,
    SensorReading,
    ToolKind,
)


@dataclass
class ToolSpec:
    """Unified, serializable tool descriptor (single source of truth)."""

    tool_id: str
    name: str
    description: str
    kind: ToolKind
    input_schema: JsonSchema | None = None  # None for pure sensors
    output_schema: JsonSchema = field(default_factory=JsonSchema)
    side_effects: bool = False
    sampling_rate: float | None = None  # seconds; sensors only
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ISensor(ABC):
    """Abstract Partner: sensor contract (read from environment)."""

    id: str

    @abstractmethod
    def sense(self) -> SensorReading:
        """Read data from the environment → :class:`SensorReading`."""

    @abstractmethod
    def get_sensor_schema(self) -> "SensorSchema":
        """Return the sensor's schema descriptor."""


class IActuator(ABC):
    """Abstract Partner: actuator contract (act on environment)."""

    id: str

    @abstractmethod
    def get_actuator_schema(self) -> "ActuatorSchema":
        """Return the actuator's schema descriptor."""

    @abstractmethod
    def validate(self, command: ActuatorCommand) -> ValidationResult:
        """Check command safety/resources BEFORE execution."""

    @abstractmethod
    def act(self, command: ActuatorCommand) -> ActuatorResult:
        """Execute the command → :class:`ActuatorResult`."""


@dataclass
class SensorSchema:
    sensor_id: str
    description: str
    output_schema: JsonSchema = field(default_factory=JsonSchema)
    sampling_rate: float | None = None


@dataclass
class ActuatorSchema:
    actuator_id: str
    description: str
    input_schema: JsonSchema = field(default_factory=JsonSchema)
    output_schema: JsonSchema = field(default_factory=JsonSchema)


class ToolSchemaError(Exception):
    """Raised when a tool's schema fails structural validation (fail-fast)."""


class DuplicateToolError(Exception):
    """Raised when a tool id is already registered."""


class ToolExecutionError(Exception):
    """Raised when an actuator raises during execution."""
