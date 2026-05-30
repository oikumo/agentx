"""
ReAct Agent — Model layer.

ReAct = Reason + Act: an LLM agent loop that reasons, calls tools,
observes results, and produces a final answer.

This module is UI-independent. It knows nothing about Views or Controllers.
"""

from __future__ import annotations

from typing import Any, Generator

from langchain_core.tools import tool
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent

from agentx.model.ai.service import AIService


# ──────────────────────────────────────────────
# Tools (concepts from the Analysis class diagram)
# ──────────────────────────────────────────────


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression. Accepts Python arithmetic."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"


_AVAILABLE_TOOLS = [calculator]


# ──────────────────────────────────────────────
# ReAct Agent — domain logic + orchestration
# ──────────────────────────────────────────────


class ReActAgent:
    """ReAct agent model. Encapsulates LLM, tools, and the agent loop.

    Operation: invoke(task)
      Preconditions:
        - LLM provider is configured (via AIService)
        - Tools list is non-empty
      Exceptions:
        - LLM unavailable: raises, caller handles
        - Tool execution fails: agent reports error as observation
      Postconditions:
        - Generator yields structured events (no side effects on this object)
    """

    def __init__(self) -> None:
        self.llm = AIService().openrouter_llm_provider().create_llm()
        self._tools = _AVAILABLE_TOOLS
        self._agent = create_react_agent(self.llm, self._tools)

    def stream(self, task: str) -> Generator[dict[str, Any], None, None]:
        """Execute a task through the ReAct agent loop.

        Yields dicts with:
          - event_type: ``"thought"`` | ``"tool_call"`` | ``"observation"`` | ``"answer"``
          - content: displayable string
          - metadata: dict with event-specific data (tool name, args, ...)

        Usage:
            for event in agent.stream("What is 2 + 2?"):
                print(event["event_type"], event["content"])
        """
        messages: list[dict[str, str]] = [
            {"role": "user", "content": task}
        ]
        seen_ids: set[int] = set()

        for step in self._agent.stream({"messages": messages}):
            for node_name, value in step.items():
                if not isinstance(value, dict):
                    continue
                for msg in value.get("messages", []):
                    msg_id = id(msg)
                    if msg_id in seen_ids:
                        continue
                    seen_ids.add(msg_id)

                    if isinstance(msg, AIMessage):
                        yield from self._yield_ai_events(msg, node_name)
                    elif isinstance(msg, ToolMessage):
                        yield from self._yield_tool_events(msg)

    # ── Private helpers ──────────────────────────────────────────

    @staticmethod
    def _yield_ai_events(msg: AIMessage, node_name: str) -> Generator[dict[str, Any], None, None]:
        """Yield events from an AIMessage (thoughts + tool calls).

        Rules:
          - If the message has tool_calls → yield ``"tool_call"`` for each.
          - If the message has text content AND tool_calls → content is ``"thought"``
            (the reasoning step before calling a tool).
          - If the message has text content AND no tool_calls → content is ``"answer"``
            (the final response to the user).
        """
        has_tool_calls = hasattr(msg, "tool_calls") and bool(msg.tool_calls)

        # Tool calls (agent deciding to use a tool)
        if has_tool_calls:
            for tc in msg.tool_calls:
                yield {
                    "event_type": "tool_call",
                    "content": f"🔧 {tc['name']}({tc['args']})",
                    "metadata": {"name": tc["name"], "args": tc["args"]},
                }

        # Text content
        if msg.content:
            event_type = "thought" if has_tool_calls else "answer"
            yield {
                "event_type": event_type,
                "content": str(msg.content),
                "metadata": {},
            }

    @staticmethod
    def _yield_tool_events(msg: ToolMessage) -> Generator[dict[str, Any], None, None]:
        """Yield events from a ToolMessage (observation)."""
        yield {
            "event_type": "observation",
            "content": str(msg.content),
            "metadata": {"tool": getattr(msg, "name", "unknown")},
        }
