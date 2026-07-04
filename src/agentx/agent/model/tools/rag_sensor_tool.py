"""RagSensorTool — wraps the existing :class:`Rag` model as a hybrid tool (design §6.6, §10).

N12: previously a read-only sensor (availability only). It now also implements
:class:`IActuator` so a policy rule can ``EXECUTE_TOOL rag_query`` with action
``query`` to actually retrieve knowledge from the RAG store.

The agent depends on the tool contract (:class:`ISensor`/:class:`IActuator`),
not on ``Rag`` internals — this is the MVC++ integration point for feature_002.
"""

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
from agentx.agent.types import ActuatorCommand, ActuatorResult, SensorReading


class RagSensorTool(ISensor, IActuator):
    """Hybrid sensor/actuator that queries the RAG knowledge base (feature_002)."""

    def __init__(self, rag: Any | None = None) -> None:
        self.id = "rag_query"
        self._rag = rag

    def set_rag(self, rag: Any) -> None:
        """Inject the RAG instance (deferred wiring until feature_002 is ready)."""
        self._rag = rag

    # ----------------------------------------------------------- ISensor

    def sense(self) -> SensorReading:
        if self._rag is None:
            return SensorReading(
                sensor_id=self.id,
                data={"available": False, "reason": "RAG not configured"},
                timestamp=datetime.now(timezone.utc),
                confidence=0.0,
            )
        try:
            # Rag.query returns a RagChatHistory; we expose availability + last url
            available = self._rag.is_data() if hasattr(self._rag, "is_data") else True
            url = (
                self._rag.get_ingested_url()
                if hasattr(self._rag, "get_ingested_url")
                else None
            )
            return SensorReading(
                sensor_id=self.id,
                data={"available": available, "ingested_url": url},
                timestamp=datetime.now(timezone.utc),
                confidence=0.85,
            )
        except Exception as exc:  # noqa: BLE001 — sensor must not crash the cycle
            return SensorReading(
                sensor_id=self.id,
                data={"available": False, "error": str(exc)},
                timestamp=datetime.now(timezone.utc),
                confidence=0.0,
            )

    def get_sensor_schema(self) -> SensorSchema:
        return SensorSchema(
            sensor_id=self.id,
            description="RAG knowledge-base availability + metadata.",
            output_schema=JsonSchema(type="object"),
            sampling_rate=None,
        )

    # --------------------------------------------------------- IActuator (N12)

    def get_actuator_schema(self) -> ActuatorSchema:
        return ActuatorSchema(
            actuator_id=self.id,
            description="Query the RAG knowledge base and return retrieved context.",
            input_schema=JsonSchema(type="object", required=["action", "prompt"]),
            output_schema=JsonSchema(type="object"),
        )

    def validate(self, command: ActuatorCommand) -> ValidationResult:
        action = command.parameters.get("action")
        if action != "query":
            return ValidationResult(valid=False, errors=[f"unknown action: {action}"])
        if not command.parameters.get("prompt"):
            return ValidationResult(valid=False, errors=["missing 'prompt' parameter"])
        return ValidationResult(valid=True)

    def act(self, command: ActuatorCommand) -> ActuatorResult:
        vr = self.validate(command)
        if not vr.valid:
            return ActuatorResult(success=False, error="; ".join(vr.errors))
        prompt = command.parameters["prompt"]
        history = command.parameters.get("history")
        try:
            result = self.query(prompt, history)
            return ActuatorResult(
                success=True,
                output={"prompt": prompt, "result": result},
            )
        except Exception as exc:  # noqa: BLE001
            return ActuatorResult(success=False, error=str(exc))

    # ----------------------------------------------------------- direct query

    def query(self, prompt: str, history: Any | None = None) -> Any:
        """Direct RAG query (used by EXECUTE_TOOL actions via the actuator)."""
        if self._rag is None:
            return None
        if hasattr(self._rag, "query"):
            return self._rag.query(prompt, history)
        return None
