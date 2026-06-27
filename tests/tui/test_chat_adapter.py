"""TUIChatAdapter (chat_adapter.py) — full mock-based unit tests.

Covers:
  - Construction and initial state
  - ``show()`` — currently a placeholder (no-op)
  - ``show_initial_message``
  - ``show_message``
  - ``show_partial_message`` (streaming, no newline, flush)
  - ``show_stream_message`` (streaming, no newline, flush)
  - ``show_message_chat_error``
  - IChatView ABC compliance
  - Edge cases: empty messages, unicode, multi-line
"""

from __future__ import annotations

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from agentx.ui.interfaces import IChatView
from agentx.ui.tui.adapters.chat_adapter import TUIChatAdapter


# ---------------------------------------------------------------------------
# IChatView ABC compliance
# ---------------------------------------------------------------------------

class TestIChatViewABC:
    """Verify IChatView cannot be instantiated."""

    def test_interface_is_abstract(self):
        with pytest.raises(TypeError, match="show"):
            IChatView()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestTUIChatAdapterConstruction:
    """Verify clean initial state."""

    def test_construction_stores_controller_and_none_screen(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        assert adapter._controller is mock_chat_controller
        assert adapter._screen is None

    def test_implements_ichatview(self, mock_chat_controller):
        """Concrete check: every abstract method from IChatView is present."""
        from agentx.ui.interfaces import IChatView

        for method in ("show", "show_initial_message", "show_message",
                       "show_partial_message", "show_stream_message",
                       "show_message_chat_error"):
            assert hasattr(TUIChatAdapter, method), f"Missing {method}"
            assert callable(getattr(TUIChatAdapter, method)), f"{method} not callable"

    def test_accepts_none_controller(self):
        """Should accept None (duck typing)."""
        adapter = TUIChatAdapter(None)  # type: ignore[arg-type]
        assert adapter._controller is None
        assert adapter._screen is None


# ---------------------------------------------------------------------------
# show() — placeholder
# ---------------------------------------------------------------------------

class TestTUIChatAdapterShow:
    """show() is currently a no-op placeholder."""

    def test_show_is_noop(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        # Should not raise any exception
        result = adapter.show()
        assert result is None


# ---------------------------------------------------------------------------
# show_initial_message
# ---------------------------------------------------------------------------

class TestTUIChatAdapterInitialMessage:
    """show_initial_message prints a fixed welcome string."""

    def test_show_initial_message_prints(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_initial_message()
            output = mock_stdout.getvalue()
            assert "[CHAT]" in output
            assert "Starting interactive chat session" in output


# ---------------------------------------------------------------------------
# show_message
# ---------------------------------------------------------------------------

class TestTUIChatAdapterMessage:
    """show_message prints the message with [CHAT] prefix."""

    def test_show_message_prints_prefix_and_message(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_message("Hello world")
            output = mock_stdout.getvalue()
            assert "[CHAT]" in output
            assert "Hello world" in output

    def test_show_message_empty_string(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout", new_callable=StringIO):
            adapter.show_message("")  # should not raise

    def test_show_message_unicode(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_message("🎉 Unicode ✓")
            assert "🎉 Unicode ✓" in mock_stdout.getvalue()

    def test_show_message_multiple_calls(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_message("first")
            adapter.show_message("second")
            output = mock_stdout.getvalue()
            assert "first" in output
            assert "second" in output
            assert output.count("second") == 1


# ---------------------------------------------------------------------------
# show_partial_message  (streaming — no newline, flush=True)
# ---------------------------------------------------------------------------

class TestTUIChatAdapterPartialMessage:
    """``show_partial_message`` streams output without a trailing newline."""

    def test_partial_message_prints_without_newline(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_partial_message("streaming")
            output = mock_stdout.getvalue()
            assert "[CHAT STREAM]" in output
            assert "streaming" in output
            # Should NOT end with a newline
            assert not output.endswith("\n"), \
                "partial message should not include trailing newline"

    def test_partial_message_calls_flush(self, mock_chat_controller):
        """Verify flush=True is used for streaming output."""
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.write = MagicMock()
            adapter.show_partial_message("partial")

            mock_stdout.flush.assert_called_once()

    def test_partial_message_multiple_calls(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_partial_message("first")
            adapter.show_partial_message("second")
            output = mock_stdout.getvalue()
            assert "first" in output
            assert "second" in output

    def test_partial_message_unicode(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_partial_message("流")
            assert "流" in mock_stdout.getvalue()


# ---------------------------------------------------------------------------
# show_stream_message  (same contract as partial message)
# ---------------------------------------------------------------------------

class TestTUIChatAdapterStreamMessage:
    """``show_stream_message`` behaves identically to partial message."""

    def test_stream_message_prints_without_newline(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_stream_message("stream")
            output = mock_stdout.getvalue()
            assert "[CHAT STREAM]" in output
            assert not output.endswith("\n")

    def test_stream_message_calls_flush(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.write = MagicMock()
            adapter.show_stream_message("data")
            mock_stdout.flush.assert_called_once()


# ---------------------------------------------------------------------------
# show_message_chat_error
# ---------------------------------------------------------------------------

class TestTUIChatAdapterError:
    """show_message_chat_error prints a fixed error string."""

    def test_show_message_chat_error_prints(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_message_chat_error()
            output = mock_stdout.getvalue()
            assert "[CHAT ERROR]" in output
            assert "error occurred" in output.lower()

    def test_show_message_chat_error_ignores_args(self, mock_chat_controller):
        """The method takes no arguments (only self)."""
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout", new_callable=StringIO):
            adapter.show_message_chat_error()  # should not raise TypeError


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestTUIChatAdapterEdgeCases:
    """Boundary conditions for all message types."""

    def test_mixed_message_types(self, mock_chat_controller):
        """All message types can be called in sequence without errors."""
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout", new_callable=StringIO):
            adapter.show_initial_message()
            adapter.show_message("msg")
            adapter.show_partial_message("partial")
            adapter.show_stream_message("stream")
            adapter.show_message_chat_error()
        # All should complete without error

    def test_very_long_message(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        long_msg = "x" * 10000
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_message(long_msg)
            assert len(mock_stdout.getvalue()) > 10000

    def test_message_with_newlines(self, mock_chat_controller):
        adapter = TUIChatAdapter(mock_chat_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_message("line1\nline2\nline3")
            output = mock_stdout.getvalue()
            assert "line1" in output
            assert "line2" in output
            assert "line3" in output
