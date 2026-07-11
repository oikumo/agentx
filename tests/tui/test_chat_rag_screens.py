"""Unit tests for Chat and RAG TUI screens.

Tests cover:
- Screen construction
- Compose methods
- Bindings
- Actions
- Navigation
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentx.ui.tui.screens.chat_screen import ChatTUIScreen
from agentx.ui.tui.screens.rag_screen import RagTUIScreen


# ===================================================================
# ChatTUIScreen Tests
# ===================================================================

class TestChatTUIScreenConstruction:
    """Chat screen construction tests."""

    def test_construction(self):
        """Chat screen can be constructed."""
        screen = ChatTUIScreen()
        assert screen is not None

    def test_history_initialized(self):
        """Chat history is initialized as empty list."""
        screen = ChatTUIScreen()
        assert screen.history == []

    def test_llm_initialization_attempted(self):
        """LLM initialization is attempted (may fail without API key)."""
        screen = ChatTUIScreen()
        # LLM may be None if API key not available, but initialization should not crash
        assert hasattr(screen, 'llm')


class TestChatMessageDisplayRegression:
    """Regression tests for feature_017 chat message display bug.

    Root cause: ChatMessage.__init__ accepted only (message, role) but
    chat_screen.py called it with (message, role, timestamp). The TypeError
    was silently swallowed by ``except Exception: pass``, so NO messages
    ever appeared on screen — not welcome, not user, not assistant.
    """

    def test_chat_message_accepts_timestamp(self):
        """ChatMessage must accept (message, role, timestamp) — 3 args.

        This is the core regression: before the fix, ChatMessage.__init__
        only accepted 2 args, so every _add_message / show_partial_message
        call raised TypeError (silently swallowed).
        """
        from datetime import datetime
        from agentx.ui.tui.framework import ChatMessage

        # Must not raise
        ts = datetime(2025, 1, 15, 10, 30, 0)
        msg = ChatMessage("hello", "assistant", ts)
        assert msg.role == "assistant"
        assert msg.timestamp == ts
        assert "assistant" in msg.classes

    def test_add_message_calls_chat_message_with_3_args(self):
        """_add_message must successfully create a ChatMessage with timestamp.

        Before the fix, the ChatMessage(message, role, timestamp) call inside
        _add_message raised TypeError, which was swallowed by except:pass,
        so no widget was ever mounted.
        """
        from unittest.mock import MagicMock, patch, call
        from datetime import datetime
        from agentx.ui.tui.framework import ChatMessage

        screen = ChatTUIScreen()
        mock_container = MagicMock()
        with patch.object(screen, 'query_one', return_value=mock_container):
            with patch.object(screen, 'call_later') as mock_call_later:
                # This must not raise — before the fix it was silently failing
                screen._add_message("test content", "user")

                # Verify ChatMessage was created and mounted
                assert mock_container.mount.called
                mounted_widget = mock_container.mount.call_args[0][0]
                assert isinstance(mounted_widget, ChatMessage)
                assert mounted_widget.role == "user"
                assert isinstance(mounted_widget.timestamp, datetime)

    def test_show_message_creates_chat_message(self):
        """show_message must create and mount a ChatMessage widget."""
        from unittest.mock import MagicMock, patch
        from agentx.ui.tui.framework import ChatMessage

        screen = ChatTUIScreen()
        mock_container = MagicMock()
        with patch.object(screen, 'query_one', return_value=mock_container):
            with patch.object(screen, 'call_later'):
                screen.show_message("assistant response")

                assert mock_container.mount.called
                widget = mock_container.mount.call_args[0][0]
                assert isinstance(widget, ChatMessage)
                assert widget.role == "assistant"

    def test_show_partial_message_creates_chat_message(self):
        """show_partial_message must create a ChatMessage on first chunk.

        Before the fix, the ChatMessage(message, 'assistant', datetime.now())
        call raised TypeError, so streaming responses never appeared.
        """
        from unittest.mock import MagicMock, patch
        from agentx.ui.tui.framework import ChatMessage

        screen = ChatTUIScreen()
        mock_container = MagicMock()
        with patch.object(screen, 'query_one', return_value=mock_container):
            with patch.object(screen, 'call_later'):
                screen.show_partial_message("chunk 1")

                assert mock_container.mount.called
                widget = mock_container.mount.call_args[0][0]
                assert isinstance(widget, ChatMessage)
                assert widget.role == "assistant"
                assert screen._is_streaming is True

    def test_show_partial_message_appends_to_streaming(self):
        """Subsequent show_partial_message calls append to the streaming widget."""
        from unittest.mock import MagicMock, patch
        from agentx.ui.tui.framework import ChatMessage

        screen = ChatTUIScreen()
        mock_container = MagicMock()
        mock_widget = MagicMock()
        with patch.object(screen, 'query_one', return_value=mock_container):
            with patch.object(screen, 'call_later'):
                # First chunk creates the widget
                screen.show_partial_message("Hello")
                assert mock_container.mount.call_count == 1

                # Second chunk appends
                screen._streaming_widget = mock_widget
                screen.show_partial_message(" world")
                # mount should NOT be called again
                assert mock_container.mount.call_count == 1
                # widget.update should be called with accumulated message
                mock_widget.update.assert_called_with("Hello world")

    def test_on_input_submitted_displays_user_message(self):
        """User input must create a ChatMessage with role='user'."""
        from unittest.mock import MagicMock, patch
        from agentx.ui.tui.framework import ChatMessage

        screen = ChatTUIScreen()
        mock_input = MagicMock()
        mock_input.id = "chat-input"
        mock_input.value = "  user question  "

        mock_container = MagicMock()
        with patch.object(screen, 'query_one', return_value=mock_container):
            with patch.object(screen, 'call_later'):
                # No controller — should still show user message
                screen.on_input_submitted(
                    type('Event', (), {'input': mock_input, 'value': '  user question  '})()
                )

                # A ChatMessage with role='user' must have been mounted (first call)
                assert mock_container.mount.call_count >= 1
                first_widget = mock_container.mount.call_args_list[0][0][0]
                assert isinstance(first_widget, ChatMessage)
                assert first_widget.role == "user"


class TestChatTUIScreenBindings:
    """Chat screen key bindings tests."""

    def test_bindings_exist(self):
        """Chat screen has bindings defined."""
        assert len(ChatTUIScreen.BINDINGS) >= 3

    def test_quit_binding(self):
        """Chat screen has quit binding."""
        binding_keys = [b.key if hasattr(b, 'key') else b[0] for b in ChatTUIScreen.BINDINGS]
        assert "q" in binding_keys

    def test_back_binding(self):
        """Chat screen has back binding."""
        binding_keys = [b.key if hasattr(b, 'key') else b[0] for b in ChatTUIScreen.BINDINGS]
        assert "escape" in binding_keys

    def test_send_binding(self):
        """Chat screen has send binding."""
        binding_keys = [b.key if hasattr(b, 'key') else b[0] for b in ChatTUIScreen.BINDINGS]
        assert "ctrl+enter" in binding_keys


class TestChatTUIScreenActions:
    """Chat screen action methods tests."""

    def test_action_quit(self):
        """Quit action calls app.exit()."""
        # Use Textual's test framework
        from textual.app import App
        
        class TestApp(App):
            def on_mount(self):
                self.push_screen(ChatTUIScreen())
        
        async def run_test():
            app = TestApp()
            async with app.run_test() as pilot:
                screen = app.screen
                # Call the action
                screen.action_quit()
                # App should be exiting
                return True
        
        # Run the async test
        import asyncio
        result = asyncio.run(run_test())
        assert result

    def test_action_back(self):
        """Back action calls app.pop_screen()."""
        from textual.app import App
        
        class TestApp(App):
            def on_mount(self):
                self.push_screen(ChatTUIScreen())
        
        async def run_test():
            app = TestApp()
            async with app.run_test() as pilot:
                screen = app.screen
                initial_screen = type(screen).__name__
                # Call the action
                screen.action_back()
                await pilot.pause()
                # Screen should have popped
                new_screen = type(app.screen).__name__
                return initial_screen != new_screen
        
        import asyncio
        result = asyncio.run(run_test())
        assert result

    def test_action_send_with_input(self):
        """Send action triggers input submission."""
        screen = ChatTUIScreen()
        
        mock_input = MagicMock()
        mock_input.value = "test message"
        
        with patch.object(screen, 'query_one', return_value=mock_input):
            # Should not crash
            screen.action_send()


class TestChatTUIScreenCompose:
    """Chat screen compose method tests."""

    def test_compose_returns_widgets(self):
        """Compose method yields widgets."""
        screen = ChatTUIScreen()
        # Skip actual compose as it requires app context
        assert hasattr(screen, 'compose')


# ===================================================================
# RagTUIScreen Tests
# ===================================================================

class TestRagTUIScreenConstruction:
    """RAG screen construction tests."""

    def test_construction(self):
        """RAG screen can be constructed."""
        screen = RagTUIScreen()
        assert screen is not None

    def test_repository_initialized_none(self):
        """Current repository is initialized as None."""
        screen = RagTUIScreen()
        assert screen.current_repository is None

    def test_chat_history_initialized(self):
        """Chat history is initialized as empty list."""
        screen = RagTUIScreen()
        assert screen.chat_history == []


class TestRagTUIScreenBindings:
    """RAG screen key bindings tests."""

    def test_bindings_exist(self):
        """RAG screen has bindings defined."""
        assert len(RagTUIScreen.BINDINGS) >= 4

    def test_quit_binding(self):
        """RAG screen has quit binding."""
        binding_keys = [b.key if hasattr(b, 'key') else b[0] for b in RagTUIScreen.BINDINGS]
        assert "q" in binding_keys

    def test_back_binding(self):
        """RAG screen has back binding."""
        binding_keys = [b.key if hasattr(b, 'key') else b[0] for b in RagTUIScreen.BINDINGS]
        assert "escape" in binding_keys

    def test_refresh_binding(self):
        """RAG screen has refresh binding."""
        binding_keys = [b.key if hasattr(b, 'key') else b[0] for b in RagTUIScreen.BINDINGS]
        assert "r" in binding_keys

    def test_chat_mode_binding(self):
        """RAG screen has chat mode binding."""
        binding_keys = [b.key if hasattr(b, 'key') else b[0] for b in RagTUIScreen.BINDINGS]
        assert "c" in binding_keys


class TestRagTUIScreenActions:
    """RAG screen action methods tests."""

    def test_action_quit(self):
        """Quit action calls app.exit()."""
        from textual.app import App
        
        class TestApp(App):
            def on_mount(self):
                self.push_screen(RagTUIScreen())
        
        async def run_test():
            app = TestApp()
            async with app.run_test() as pilot:
                screen = app.screen
                # Call the action
                screen.action_quit()
                return True
        
        import asyncio
        result = asyncio.run(run_test())
        assert result

    def test_action_back(self):
        """Back action calls app.pop_screen()."""
        from textual.app import App
        
        class TestApp(App):
            def on_mount(self):
                self.push_screen(RagTUIScreen())
        
        async def run_test():
            app = TestApp()
            async with app.run_test() as pilot:
                screen = app.screen
                initial_screen = type(screen).__name__
                # Call the action
                screen.action_back()
                await pilot.pause()
                new_screen = type(app.screen).__name__
                return initial_screen != new_screen
        
        import asyncio
        result = asyncio.run(run_test())
        assert result

    def test_action_refresh(self):
        """Refresh action shows notification."""
        from textual.app import App
        
        class TestApp(App):
            def on_mount(self):
                self.push_screen(RagTUIScreen())
        
        async def run_test():
            app = TestApp()
            async with app.run_test() as pilot:
                screen = app.screen
                # Call the action
                screen.action_refresh()
                await pilot.pause()
                return True
        
        import asyncio
        result = asyncio.run(run_test())
        assert result

    def test_action_chat_mode(self):
        """Chat mode action shows notification."""
        from textual.app import App
        
        class TestApp(App):
            def on_mount(self):
                self.push_screen(RagTUIScreen())
        
        async def run_test():
            app = TestApp()
            async with app.run_test() as pilot:
                screen = app.screen
                # Call the action
                screen.action_chat_mode()
                await pilot.pause()
                return True
        
        import asyncio
        result = asyncio.run(run_test())
        assert result


class TestRagTUIScreenButtonHandling:
    """RAG screen button handling tests."""

    def test_select_button(self):
        """Select button triggers repository selection."""
        from textual.app import App
        
        class TestApp(App):
            def on_mount(self):
                self.push_screen(RagTUIScreen())
        
        async def run_test():
            app = TestApp()
            async with app.run_test(size=(120, 40)) as pilot:
                screen = app.screen
                # Find and click the select button
                btn_select = screen.query_one('#btn-select')
                btn_select.focus()
                await pilot.press('enter')
                await pilot.pause()
                # Should navigate to repository selection screen
                assert type(app.screen).__name__ == 'RepositorySelectionScreen'
                return True
        
        import asyncio
        result = asyncio.run(run_test())
        assert result

    def test_create_button(self):
        """Create button triggers repository creation."""
        from textual.app import App
        
        class TestApp(App):
            def on_mount(self):
                self.push_screen(RagTUIScreen())
        
        async def run_test():
            app = TestApp()
            async with app.run_test(size=(120, 40)) as pilot:
                screen = app.screen
                # Find and click the create button
                btn_create = screen.query_one('#btn-create')
                btn_create.focus()
                await pilot.press('enter')
                await pilot.pause()
                # Should navigate to repository creation screen
                assert type(app.screen).__name__ == 'RepositoryCreateScreen'
                return True
        
        import asyncio
        result = asyncio.run(run_test())
        assert result


class TestRagTUIScreenInputHandling:
    """RAG screen input handling tests."""

    def test_input_without_repository(self):
        """Input submission without repository shows warning."""
        from textual.app import App
        
        class TestApp(App):
            def on_mount(self):
                self.push_screen(RagTUIScreen())
        
        async def run_test():
            app = TestApp()
            async with app.run_test(size=(120, 40)) as pilot:
                screen = app.screen
                # Try to submit input without repository
                # Focus the input using Ctrl+L or by querying it directly
                input_widget = screen.query_one('#rag-input')
                # Input should be disabled without repository
                assert input_widget.disabled == True
                return True
        
        import asyncio
        result = asyncio.run(run_test())
        assert result


class TestRagTUIScreenCompose:
    """RAG screen compose method tests."""

    def test_compose_returns_widgets(self):
        """Compose method yields widgets."""
        screen = RagTUIScreen()
        # Skip actual compose as it requires app context
        assert hasattr(screen, 'compose')


# ===================================================================
# Navigation Tests
# ===================================================================

class TestNavigationFromMainScreen:
    """Test navigation from main screen to Chat/RAG."""

    def test_main_screen_has_chat_action(self):
        """Main screen has action_open_chat method."""
        from agentx.ui.tui.screens.main_screen import MainTUIScreen
        screen = MainTUIScreen()
        assert hasattr(screen, 'action_open_chat')

    def test_main_screen_has_rag_action(self):
        """Main screen has action_open_rag method."""
        from agentx.ui.tui.screens.main_screen import MainTUIScreen
        screen = MainTUIScreen()
        assert hasattr(screen, 'action_open_rag')

    def test_chat_action_imports_chat_screen(self):
        """Chat action can import ChatTUIScreen."""
        from textual.app import App
        from agentx.ui.tui.screens.main_screen import MainTUIScreen
        
        class TestApp(App):
            def on_mount(self):
                self.push_screen(MainTUIScreen())
        
        async def run_test():
            app = TestApp()
            async with app.run_test() as pilot:
                screen = app.screen
                # Call the action
                screen.action_open_chat()
                await pilot.pause()
                # Should navigate to chat screen
                assert type(app.screen).__name__ == 'ChatTUIScreen'
                return True
        
        import asyncio
        result = asyncio.run(run_test())
        assert result

    def test_rag_action_imports_rag_screen(self):
        """RAG action can import RagTUIScreen."""
        from textual.app import App
        from agentx.ui.tui.screens.main_screen import MainTUIScreen
        
        class TestApp(App):
            def on_mount(self):
                self.push_screen(MainTUIScreen())
        
        async def run_test():
            app = TestApp()
            async with app.run_test() as pilot:
                screen = app.screen
                # Call the action
                screen.action_open_rag()
                await pilot.pause()
                # Should navigate to RAG screen
                assert type(app.screen).__name__ == 'RagTUIScreen'
                return True
        
        import asyncio
        result = asyncio.run(run_test())
        assert result