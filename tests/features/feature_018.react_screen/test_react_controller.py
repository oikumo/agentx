"""Unit tests for the ReAct Controller layer.

Tests:
  - ReactController: send_message, cancel, is_running, start_new_conversation, close
  - IReactViewPartner: ABC structure verification
"""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, patch, call

import pytest


class TestReactControllerCreation:
    """Tests for ReactController initialization."""

    def test_react_controller_creates_service(self) -> None:
        from agentx.ui.screens.react.react_controller import ReactController

        with patch("agentx.ui.screens.react.react_controller.ReactAgentService") as mock_svc_cls:
            mock_svc = MagicMock()
            mock_svc_cls.return_value = mock_svc
            controller = ReactController()
            assert controller._service is mock_svc

    def test_react_controller_accepts_injected_service(self) -> None:
        from agentx.ui.screens.react.react_controller import ReactController

        mock_service = MagicMock()
        controller = ReactController(service=mock_service)
        assert controller._service is mock_service


class TestReactControllerSendMessage:
    """Tests for ReactController.send_message()."""

    def test_react_controller_send_message_returns_true(self) -> None:
        from agentx.ui.screens.react.react_controller import ReactController

        mock_service = MagicMock()
        mock_service.is_running = False
        controller = ReactController(service=mock_service)

        result = controller.send_message("Hello")
        assert result is True

    def test_react_controller_rejects_when_running(self) -> None:
        from agentx.ui.screens.react.react_controller import ReactController

        mock_service = MagicMock()
        mock_service.is_running = True
        controller = ReactController(service=mock_service)

        result = controller.send_message("Hello")
        assert result is False

    def test_react_controller_send_message_starts_worker(self) -> None:
        from agentx.ui.screens.react.react_controller import ReactController

        mock_service = MagicMock()
        mock_service.is_running = False
        controller = ReactController(service=mock_service)

        controller.send_message("Hello")
        # Worker thread should have been started
        assert controller._worker_thread is not None
        assert controller._worker_thread.is_alive() or controller._worker_thread.daemon


class TestReactControllerCancel:
    """Tests for ReactController.cancel()."""

    def test_react_controller_cancel_calls_service_cancel(self) -> None:
        from agentx.ui.screens.react.react_controller import ReactController

        mock_service = MagicMock()
        mock_service.is_running = False
        controller = ReactController(service=mock_service)

        controller.cancel()
        mock_service.cancel.assert_called_once()

    def test_react_controller_is_running_matches_service(self) -> None:
        from agentx.ui.screens.react.react_controller import ReactController

        mock_service = MagicMock()
        mock_service.is_running = True
        controller = ReactController(service=mock_service)
        assert controller.is_running is True

        mock_service.is_running = False
        assert controller.is_running is False


class TestReactControllerConversation:
    """Tests for conversation management."""

    def test_react_controller_start_new_conversation_resets(self) -> None:
        from agentx.ui.screens.react.react_controller import ReactController

        mock_service = MagicMock()
        mock_service.is_running = False
        controller = ReactController(service=mock_service)

        controller.start_new_conversation()
        mock_service.reset_conversation.assert_called_once()

    def test_react_controller_get_history_returns_list(self) -> None:
        from agentx.ui.screens.react.react_controller import ReactController

        mock_service = MagicMock()
        mock_service.get_history.return_value = []
        controller = ReactController(service=mock_service)

        history = controller.get_history()
        assert isinstance(history, list)
        mock_service.get_history.assert_called_once()

    def test_react_controller_close_cancels(self) -> None:
        from agentx.ui.screens.react.react_controller import ReactController

        mock_service = MagicMock()
        mock_service.is_running = True
        controller = ReactController(service=mock_service)

        controller.close()
        mock_service.cancel.assert_called_once()


class TestReactControllerStreaming:
    """Tests for the worker thread streaming behavior."""

    def test_react_controller_run_agent_calls_stream(self) -> None:
        """The worker thread should call service.stream_agent with callbacks."""
        from agentx.ui.screens.react.react_controller import ReactController

        mock_service = MagicMock()
        mock_service.is_running = False
        controller = ReactController(service=mock_service)

        # Mock the view and app
        mock_view = MagicMock()
        mock_app = MagicMock()
        controller._app = mock_app

        # Run _run_agent directly (synchronously)
        controller._run_agent("test message", mock_view)

        # stream_agent should have been called
        mock_service.stream_agent.assert_called_once()
        # Check the user_message was passed
        call_kwargs = mock_service.stream_agent.call_args
        assert call_kwargs[1]["user_message"] == "test message" or call_kwargs[0][0] == "test message"

    def test_react_controller_run_agent_marshals_via_app(self) -> None:
        """Callbacks should be marshalled to the UI thread via app.call_from_thread."""
        from agentx.ui.screens.react.react_controller import ReactController

        mock_service = MagicMock()
        mock_service.is_running = False
        controller = ReactController(service=mock_service)

        mock_view = MagicMock()
        mock_app = MagicMock()
        controller._app = mock_app

        # Capture the callbacks
        controller._run_agent("test", mock_view)
        
        # Check stream_agent was called with callbacks
        call_args = mock_service.stream_agent.call_args
        if call_args[0]:
            # Positional args
            on_reasoning = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("on_reasoning")
            on_answer = call_args[0][4] if len(call_args[0]) > 4 else call_args[1].get("on_answer")
        else:
            # Keyword args
            on_reasoning = call_args[1]["on_reasoning"]
            on_answer = call_args[1]["on_answer"]

        # Call the callbacks
        on_reasoning("thinking...")
        on_answer("answer chunk")

        # app.call_from_thread should have been called for each callback
        assert mock_app.call_from_thread.call_count >= 2

    def test_react_controller_run_agent_handles_error(self) -> None:
        """If stream_agent raises, the error should be marshalled to the view."""
        from agentx.ui.screens.react.react_controller import ReactController

        mock_service = MagicMock()
        mock_service.is_running = False
        mock_service.stream_agent.side_effect = RuntimeError("Test error")
        controller = ReactController(service=mock_service)

        mock_view = MagicMock()
        mock_app = MagicMock()
        controller._app = mock_app

        # Should not raise — error is handled internally
        controller._run_agent("test", mock_view)

        # app.call_from_thread should be called with show_error
        assert mock_app.call_from_thread.call_count >= 1


class TestIReactViewPartner:
    """Tests for the IReactViewPartner ABC."""

    def test_ireact_view_partner_is_abc(self) -> None:
        from abc import ABC
        from agentx.ui.interfaces import IReactViewPartner

        assert issubclass(IReactViewPartner, ABC)

    def test_ireact_view_partner_has_abstract_methods(self) -> None:
        from agentx.ui.interfaces import IReactViewPartner

        # Should have abstract methods
        abstract_methods = IReactViewPartner.__abstractmethods__
        assert "send_message" in abstract_methods
        assert "cancel" in abstract_methods
        assert "is_running" in abstract_methods or "close" in abstract_methods or "start_new_conversation" in abstract_methods

    def test_ireact_view_partner_cannot_instantiate(self) -> None:
        from agentx.ui.interfaces import IReactViewPartner

        with pytest.raises(TypeError):
            IReactViewPartner()
