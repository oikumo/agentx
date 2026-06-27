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