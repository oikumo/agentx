"""Unit tests for the ReAct agent Model layer.

Tests:
  - react_tools: calculator + get_current_time
  - ReactAgentService: agent creation, streaming, cancel, reset, history
"""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, patch

import pytest

# ── react_tools ────────────────────────────────────────────────────────────────


class TestCalculatorTool:
    """Tests for the calculator tool."""

    def test_calculator_evaluates_simple_expression(self) -> None:
        from agentx.model.react.react_tools import calculator

        result = calculator.invoke({"expression": "2+2"})
        assert "4" in result

    def test_calculator_evaluates_multiplication(self) -> None:
        from agentx.model.react.react_tools import calculator

        result = calculator.invoke({"expression": "240*0.15"})
        assert "36" in result

    def test_calculator_rejects_unsafe_input(self) -> None:
        from agentx.model.react.react_tools import calculator

        result = calculator.invoke({"expression": "__import__('os')"})
        # Should return an error message, not execute the code
        assert "error" in result.lower() or "invalid" in result.lower()


class TestGetCurrentTimeTool:
    """Tests for the get_current_time tool."""

    def test_get_current_time_returns_iso_format(self) -> None:
        from agentx.model.react.react_tools import get_current_time

        result = get_current_time.invoke({})
        # Should contain a date-like string (ISO 8601 or similar)
        assert len(result) > 10
        # Should contain digits (year, etc.)
        assert any(c.isdigit() for c in result)


class TestReactToolsFunctions:
    """Explicit tests for react_tools.py module functions."""

    def test_safe_calculate_evaluates_addition(self) -> None:
        from agentx.model.react.react_tools import safe_calculate

        result = safe_calculate("2+2")
        assert result == "4"

    def test_safe_calculate_evaluates_subtraction(self) -> None:
        from agentx.model.react.react_tools import safe_calculate

        result = safe_calculate("10-3")
        assert result == "7"

    def test_safe_calculate_evaluates_multiplication(self) -> None:
        from agentx.model.react.react_tools import safe_calculate

        result = safe_calculate("6*7")
        assert result == "42"

    def test_safe_calculate_evaluates_division(self) -> None:
        from agentx.model.react.react_tools import safe_calculate

        result = safe_calculate("20/4")
        assert result == "5"

    def test_safe_calculate_evaluates_power(self) -> None:
        from agentx.model.react.react_tools import safe_calculate

        result = safe_calculate("2**10")
        assert result == "1024"

    def test_safe_calculate_evaluates_float_result(self) -> None:
        from agentx.model.react.react_tools import safe_calculate

        result = safe_calculate("10/4")
        assert result == "2.5"

    def test_safe_calculate_rejects_function_call(self) -> None:
        from agentx.model.react.react_tools import safe_calculate

        result = safe_calculate("__import__('os')")
        assert "error" in result.lower()

    def test_safe_calculate_rejects_attribute_access(self) -> None:
        from agentx.model.react.react_tools import safe_calculate

        result = safe_calculate("os.system('ls')")
        assert "error" in result.lower()

    def test_safe_calculate_rejects_invalid_syntax(self) -> None:
        """safe_calculate should handle invalid syntax gracefully."""
        from agentx.model.react.react_tools import safe_calculate

        # "2 ++ 2" is valid (unary plus), use truly invalid
        result = safe_calculate("2 + * 3")
        assert "error" in result.lower() or "invalid" in result.lower()

    def test_calculator_tool_invokes_safe_calculate(self) -> None:
        from agentx.model.react.react_tools import calculator

        result = calculator.invoke({"expression": "3*4"})
        assert "12" in result

    def test_get_current_time_tool_invokes_datetime(self) -> None:
        from agentx.model.react.react_tools import get_current_time

        result = get_current_time.invoke({})
        assert len(result) > 10
        assert any(c.isdigit() for c in result)


# ── ReactAgentService ──────────────────────────────────────────────────────────


class TestReactAgentServiceCreation:
    """Tests for ReactAgentService __init__ and basic properties."""

    def test_react_agent_service_creates_agent(self) -> None:
        from langgraph.graph.state import CompiledStateGraph

        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        service = ReactAgentService(llm=mock_llm)
        assert isinstance(service._agent, CompiledStateGraph)

    def test_react_agent_service_has_thread_id(self) -> None:
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        service = ReactAgentService(llm=mock_llm)
        assert isinstance(service.thread_id, str)
        assert len(service.thread_id) > 0

    def test_react_agent_service_has_checkpointer(self) -> None:
        from langgraph.checkpoint.memory import InMemorySaver

        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        service = ReactAgentService(llm=mock_llm)
        assert isinstance(service._checkpointer, InMemorySaver)

    def test_react_agent_service_uses_default_tools(self) -> None:
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        service = ReactAgentService(llm=mock_llm)
        # Should have at least the two built-in tools
        assert len(service._tools) >= 2

    def test_react_agent_service_uses_custom_system_prompt(self) -> None:
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        custom_prompt = "You are a custom test agent."
        service = ReactAgentService(llm=mock_llm, system_prompt=custom_prompt)
        assert service._system_prompt == custom_prompt


class TestReactAgentServiceStreaming:
    """Tests for ReactAgentService.stream_agent()."""

    def test_react_agent_service_stream_invokes_callbacks(self) -> None:
        """stream_agent should route events to the provided callbacks."""
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        service = ReactAgentService(llm=mock_llm)

        # Mock the agent's stream_events to yield a simple text message
        mock_stream = MagicMock()
        mock_message = MagicMock()
        mock_message.reasoning = iter([])  # no reasoning
        mock_message.text = iter(["Hello "])  # one text chunk
        mock_message.tool_calls = MagicMock()
        mock_message.tool_calls.get = MagicMock(return_value=[])
        mock_stream.messages = [mock_message]
        mock_stream.tool_calls = iter([])
        mock_stream.output = {"messages": []}

        service._agent.stream_events = MagicMock(return_value=mock_stream)

        on_answer = MagicMock()
        on_done = MagicMock()
        on_reasoning = MagicMock()

        service.stream_agent(
            user_message="Hi",
            on_reasoning=on_reasoning,
            on_tool_call=MagicMock(),
            on_tool_result=MagicMock(),
            on_answer=on_answer,
            on_done=on_done,
            on_error=MagicMock(),
        )

        on_answer.assert_called_with("Hello ")
        on_done.assert_called_once()

    def test_react_agent_service_cancel_stops_streaming(self) -> None:
        """cancel() should cause the stream loop to break."""
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        service = ReactAgentService(llm=mock_llm)

        # Pre-set cancel before streaming starts
        service._cancel_event.set()

        on_done = MagicMock()
        on_answer = MagicMock()

        # Mock stream_events to return an empty stream
        mock_stream = MagicMock()
        mock_stream.messages = []
        mock_stream.tool_calls = iter([])
        mock_stream.output = {}
        service._agent.stream_events = MagicMock(return_value=mock_stream)

        service.stream_agent(
            user_message="Hi",
            on_reasoning=MagicMock(),
            on_tool_call=MagicMock(),
            on_tool_result=MagicMock(),
            on_answer=on_answer,
            on_done=on_done,
            on_error=MagicMock(),
        )

        # on_done should NOT be called because we were cancelled
        on_done.assert_not_called()

    def test_react_agent_service_reset_conversation_changes_thread(self) -> None:
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        service = ReactAgentService(llm=mock_llm)
        old_thread = service.thread_id
        service.reset_conversation()
        new_thread = service.thread_id
        assert old_thread != new_thread

    def test_react_agent_service_get_history_returns_list(self) -> None:
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        service = ReactAgentService(llm=mock_llm)
        history = service.get_history()
        assert isinstance(history, list)

    def test_react_agent_service_is_running_property(self) -> None:
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        service = ReactAgentService(llm=mock_llm)
        assert service.is_running is False

    def test_react_agent_service_stream_routes_reasoning(self) -> None:
        """stream_agent should route reasoning deltas to on_reasoning."""
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        service = ReactAgentService(llm=mock_llm)

        mock_stream = MagicMock()
        mock_message = MagicMock()
        mock_message.reasoning = iter(["Thinking..."])
        mock_message.text = iter(["Answer"])
        mock_message.tool_calls = MagicMock()
        mock_message.tool_calls.get = MagicMock(return_value=[])
        mock_stream.messages = [mock_message]
        mock_stream.tool_calls = iter([])
        mock_stream.output = {"messages": []}

        service._agent.stream_events = MagicMock(return_value=mock_stream)

        on_reasoning = MagicMock()
        on_answer = MagicMock()

        service.stream_agent(
            user_message="Why?",
            on_reasoning=on_reasoning,
            on_tool_call=MagicMock(),
            on_tool_result=MagicMock(),
            on_answer=on_answer,
            on_done=MagicMock(),
            on_error=MagicMock(),
        )

        on_reasoning.assert_called_with("Thinking...")
        on_answer.assert_called_with("Answer")

    def test_react_agent_service_stream_routes_tool_calls(self) -> None:
        """stream_agent should route tool call execution to on_tool_call/result."""
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        service = ReactAgentService(llm=mock_llm)

        mock_stream = MagicMock()
        mock_message = MagicMock()
        mock_message.reasoning = iter([])
        mock_message.text = iter([])
        mock_message.tool_calls = MagicMock()
        # Model emits a tool call
        mock_message.tool_calls.get = MagicMock(
            return_value=[{"name": "calculator", "args": {"expression": "2+2"}}]
        )
        mock_stream.messages = [mock_message]

        # Tool execution lifecycle
        mock_tool_call = MagicMock()
        mock_tool_call.tool_name = "calculator"
        mock_tool_call.input = {"expression": "2+2"}
        mock_tool_call.output = "4"
        mock_tool_call.error = None
        mock_stream.tool_calls = iter([mock_tool_call])
        mock_stream.output = {"messages": []}

        service._agent.stream_events = MagicMock(return_value=mock_stream)

        on_tool_call = MagicMock()
        on_tool_result = MagicMock()

        service.stream_agent(
            user_message="What is 2+2?",
            on_reasoning=MagicMock(),
            on_tool_call=on_tool_call,
            on_tool_result=on_tool_result,
            on_answer=MagicMock(),
            on_done=MagicMock(),
            on_error=MagicMock(),
        )

        on_tool_call.assert_called_with("calculator", str({"expression": "2+2"}))
        on_tool_result.assert_called_with("calculator", "4")

    def test_react_agent_service_stream_handles_error(self) -> None:
        """stream_agent should call on_error if stream_events raises."""
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        service = ReactAgentService(llm=mock_llm)

        service._agent.stream_events = MagicMock(
            side_effect=RuntimeError("LLM connection failed")
        )

        on_error = MagicMock()
        on_done = MagicMock()

        service.stream_agent(
            user_message="Hi",
            on_reasoning=MagicMock(),
            on_tool_call=MagicMock(),
            on_tool_result=MagicMock(),
            on_answer=MagicMock(),
            on_done=on_done,
            on_error=on_error,
        )

        on_error.assert_called_once()
        on_done.assert_not_called()
