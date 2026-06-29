"""RagSensorTool — wraps the existing :class:`Rag` model as an ISensor (design §6.6, §10).

The agent depends on the tool contract (:class:`ISensor`), not on ``Rag``
internals — this is the MVC++ integration point for feature_002.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from agentx.agent.model.tools.spec import ISensor, JsonSchema, SensorSchema
from agentx.agent.types import SensorReading


class RagSensorTool(ISensor):
    """Sensor that queries the RAG knowledge base (feature_002 integration)."""

    def __init__(self, rag: Any | None = None) -> None:
        self.id = "rag_query"
        self._rag = rag

    def set_rag(self, rag: Any) -> None:
        """Inject the RAG instance (deferred wiring until feature_002 is ready)."""
        self._rag = rag

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

    def query(self, prompt: str, history: Any | None = None) -> Any:
        """Direct RAG query (used by EXECUTE_TOOL actions via the actuator)."""
        if self._rag is None:
            return None
        if hasattr(self._rag, "query"):
            return self._rag.query(prompt, history)
        return None
