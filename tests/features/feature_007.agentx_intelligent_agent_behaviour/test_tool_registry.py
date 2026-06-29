"""Unit tests for the Tool Registry and built-in tools."""

from __future__ import annotations

import pytest

from agentx.agent.model.tools.filesystem_tool import FileSystemTool
from agentx.agent.model.tools.registry import (
    DuplicateToolError,
    ToolRegistry,
    ToolSchemaError,
)
from agentx.agent.model.tools.rag_sensor_tool import RagSensorTool
from agentx.agent.model.tools.session_tool import SessionTool
from agentx.agent.model.tools.spec import (
    ActuatorSchema,
    IActuator,
    ISensor,
    JsonSchema,
    SensorSchema,
    SensorReading,
    ValidationResult,
)
from agentx.agent.types import (
    ActuatorCommand,
    ActuatorResult,
    ToolKind,
)


# ---------------------------------------------------------------------------
# Stub sensor / actuator for testing
# ---------------------------------------------------------------------------


class StubSensor(ISensor):
    def __init__(self, sid: str = "stub_sensor") -> None:
        self.id = sid

    def sense(self) -> SensorReading:
        return SensorReading(sensor_id=self.id, data={"value": 42}, confidence=0.9)

    def get_sensor_schema(self) -> SensorSchema:
        return SensorSchema(sensor_id=self.id, description="stub", output_schema=JsonSchema(type="object"))


class StubActuator(IActuator):
    def __init__(self, aid: str = "stub_actuator") -> None:
        self.id = aid

    def get_actuator_schema(self) -> ActuatorSchema:
        return ActuatorSchema(
            actuator_id=self.id,
            description="stub",
            input_schema=JsonSchema(type="object"),
            output_schema=JsonSchema(type="object"),
        )

    def validate(self, command: ActuatorCommand) -> ValidationResult:
        return ValidationResult(valid=True)

    def act(self, command: ActuatorCommand) -> ActuatorResult:
        return ActuatorResult(success=True, output={"echo": command.action})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestToolRegistryRegistration:
    def test_register_sensor(self):
        reg = ToolRegistry()
        spec = reg.register_sensor(StubSensor())
        assert spec.tool_id == "stub_sensor"
        assert spec.kind == ToolKind.SENSOR
        assert "stub_sensor" in reg.list_sensors()

    def test_register_actuator(self):
        reg = ToolRegistry()
        spec = reg.register_actuator(StubActuator())
        assert spec.kind == ToolKind.ACTUATOR
        assert "stub_actuator" in reg.list_actuators()

    def test_duplicate_sensor_rejected(self):
        reg = ToolRegistry()
        reg.register_sensor(StubSensor())
        with pytest.raises(DuplicateToolError):
            reg.register_sensor(StubSensor())

    def test_unregister(self):
        reg = ToolRegistry()
        reg.register_sensor(StubSensor())
        assert reg.unregister("stub_sensor") is True
        assert "stub_sensor" not in reg.list_sensors()

    def test_hybrid_tool_upgrade(self):
        reg = ToolRegistry()
        reg.register_sensor(StubSensor("shared"))
        reg.register_actuator(StubActuator("shared"))
        assert reg.get_spec("shared").kind == ToolKind.HYBRID


class TestToolRegistryExecution:
    def test_execute_safely_success(self):
        reg = ToolRegistry()
        reg.register_actuator(StubActuator())
        result = reg.execute_safely(
            ActuatorCommand(actuator_id="stub_actuator", action="ping")
        )
        assert result.success is True
        assert result.output == {"echo": "ping"}

    def test_execute_safely_unknown_actuator(self):
        reg = ToolRegistry()
        result = reg.execute_safely(
            ActuatorCommand(actuator_id="nope", action="x")
        )
        assert result.success is False
        assert result.error is not None
        assert "unknown actuator" in result.error

    def test_health_check(self):
        reg = ToolRegistry()
        reg.register_sensor(StubSensor())
        health = reg.health_check()
        assert health["stub_sensor"] is True


class TestFileSystemTool:
    def test_sense_returns_files(self, sandbox_dir):
        from pathlib import Path

        (Path(sandbox_dir) / "a.txt").write_text("hello")
        tool = FileSystemTool(sandbox_dir)
        reading = tool.sense()
        assert "a.txt" in reading.data
        assert reading.confidence > 0.8

    def test_act_create_and_read(self, sandbox_dir):
        from pathlib import Path

        tool = FileSystemTool(sandbox_dir)
        create_result = tool.act(
            ActuatorCommand(
                actuator_id="filesystem",
                action="create",
                parameters={"action": "create", "path": "note.txt", "content": "data"},
            )
        )
        assert create_result.success is True
        assert (Path(sandbox_dir) / "note.txt").exists()

        read_result = tool.act(
            ActuatorCommand(
                actuator_id="filesystem",
                action="read",
                parameters={"action": "read", "path": "note.txt"},
            )
        )
        assert read_result.success is True
        assert read_result.output["content"] == "data"

    def test_sandbox_escape_rejected(self, sandbox_dir):
        tool = FileSystemTool(sandbox_dir)
        result = tool.act(
            ActuatorCommand(
                actuator_id="filesystem",
                action="read",
                parameters={"action": "read", "path": "../../etc/passwd"},
            )
        )
        assert result.success is False
        assert result.error is not None
        assert "sandbox" in result.error


class TestRagSensorTool:
    def test_sense_without_rag(self):
        tool = RagSensorTool()
        reading = tool.sense()
        assert reading.data["available"] is False
        assert reading.confidence == 0.0

    def test_set_rag(self):
        tool = RagSensorTool()

        class FakeRag:
            def is_data(self):
                return True

            def get_ingested_url(self):
                return "http://example.com"

        tool.set_rag(FakeRag())
        reading = tool.sense()
        assert reading.data["available"] is True
        assert reading.data["ingested_url"] == "http://example.com"


class TestSessionTool:
    def test_sense_without_agent(self):
        tool = SessionTool()
        reading = tool.sense()
        assert reading.data["active"] is False

    def test_validate_unknown_action(self):
        tool = SessionTool()
        vr = tool.validate(ActuatorCommand(actuator_id="session", action="x", parameters={"action": "bogus"}))
        assert vr.valid is False
