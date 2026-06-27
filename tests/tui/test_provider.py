"""TUIProvider — unit tests with mocked sub-dependencies.

Tests cover:
  - Construction and initial state
  - ``create_main_view`` / ``create_rag_view`` / ``create_chat_view``
  - ``initialize`` and ``shutdown`` lifecycle
  - Automatic registration with ``ProviderRegistry`` (module-level side-effect)
  - Adherence to the ``IUIProvider`` ABC
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentx.ui.interfaces import IUIProvider
from agentx.ui.tui.provider import TUIProvider
from agentx.ui.providers import ProviderRegistry


# ---------------------------------------------------------------------------
# ABC compliance
# ---------------------------------------------------------------------------

class TestIUIProviderABC:
    """Verify that *IUIProvider* itself cannot be instantiated."""

    def test_interface_is_abstract(self):
        with pytest.raises(TypeError, match="create_main_view"):
            IUIProvider()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestTUIProviderConstruction:
    """Verify the provider starts in a clean state."""

    def test_default_state(self):
        provider = TUIProvider()
        assert provider._app is None
        assert provider._initialized is False

    def test_concrete_class_implements_interface(self):
        """TUIProvider provides all 5 abstract methods from IUIProvider."""
        from agentx.ui.tui.provider import TUIProvider
        from agentx.ui.interfaces import IUIProvider

        p = TUIProvider()
        for method in ("create_main_view", "create_rag_view", "create_chat_view",
                       "initialize", "shutdown"):
            assert hasattr(p, method), f"Missing method: {method}"
            assert callable(getattr(p, method)), f"{method} is not callable"


# ---------------------------------------------------------------------------
# Lifecycle: initialize / shutdown
# ---------------------------------------------------------------------------

class TestTUIProviderLifecycle:
    """Verify initialize / shutdown flip the internal flag."""

    def test_initialize_sets_flag(self):
        provider = TUIProvider()
        assert provider._initialized is False
        provider.initialize()
        assert provider._initialized is True

    def test_shutdown_clears_flag(self):
        provider = TUIProvider()
        provider.initialize()
        assert provider._initialized is True
        provider.shutdown()
        assert provider._initialized is False

    def test_double_initialize_is_idempotent(self):
        provider = TUIProvider()
        provider.initialize()
        provider.initialize()  # should not raise
        assert provider._initialized is True

    def test_double_shutdown_is_idempotent(self):
        provider = TUIProvider()
        provider.shutdown()
        provider.shutdown()  # should not raise
        assert provider._initialized is False


# ---------------------------------------------------------------------------
# Factory methods: create_main_view / create_rag_view / create_chat_view
# ---------------------------------------------------------------------------

class TestTUIProviderFactoryMethods:
    """Verify that each *create_xxx_view* returns the correct adapter type."""

    def test_create_main_view_returns_tui_adapter(self, mock_main_controller):
        provider = TUIProvider()
        view = provider.create_main_view(mock_main_controller)

        from agentx.ui.tui.adapters.main_adapter import TUIAdapter
        assert isinstance(view, TUIAdapter)
        assert view._controller is mock_main_controller
        assert view._app is None

    def test_create_main_view_passes_controller(self, mock_main_controller):
        provider = TUIProvider()
        view = provider.create_main_view(mock_main_controller)
        assert view._controller is mock_main_controller

    def test_create_rag_view_returns_rag_adapter(self, mock_rag_controller):
        provider = TUIProvider()
        view = provider.create_rag_view(mock_rag_controller)

        from agentx.ui.tui.adapters.rag_adapter import TUIRagAdapter
        assert isinstance(view, TUIRagAdapter)
        assert view._controller is mock_rag_controller

    def test_create_chat_view_returns_chat_adapter(self, mock_chat_controller):
        provider = TUIProvider()
        view = provider.create_chat_view(mock_chat_controller)

        from agentx.ui.tui.adapters.chat_adapter import TUIChatAdapter
        assert isinstance(view, TUIChatAdapter)
        assert view._controller is mock_chat_controller

    def test_create_main_view_uses_lazy_import(self, mock_main_controller):
        """The adapter import happens inside the method body (lazy)."""
        provider = TUIProvider()
        with patch("agentx.ui.tui.adapters.main_adapter.TUIAdapter") as mock_adapter_cls:
            mock_adapter_cls.return_value = MagicMock()
            provider.create_main_view(mock_main_controller)
            # Verify TUIAdapter was called with the controller
            mock_adapter_cls.assert_called_once_with(mock_main_controller)


# ---------------------------------------------------------------------------
# IMainView return type contract
# ---------------------------------------------------------------------------

class TestTUIProviderReturnTypes:
    """Verify returned objects implement the correct interface."""

    def test_main_view_is_imainview(self, mock_main_controller):
        provider = TUIProvider()
        view = provider.create_main_view(mock_main_controller)
        from agentx.ui.interfaces import IMainView
        # Check it has all abstract methods
        for method in ("show", "print_message", "print_error_message",
                       "print_warring_message", "print_response",
                       "print_response_error"):
            assert hasattr(view, method)

    def test_rag_view_is_iragview(self, mock_rag_controller):
        provider = TUIProvider()
        view = provider.create_rag_view(mock_rag_controller)
        for method in ("show", "print_message", "print_message_error",
                       "show_repository_state", "show_menu"):
            assert hasattr(view, method)

    def test_chat_view_is_ichatview(self, mock_chat_controller):
        provider = TUIProvider()
        view = provider.create_chat_view(mock_chat_controller)
        for method in ("show", "show_initial_message", "show_message",
                       "show_partial_message", "show_stream_message",
                       "show_message_chat_error"):
            assert hasattr(view, method)


# ---------------------------------------------------------------------------
# Registry integration (module-level side-effect)
# ---------------------------------------------------------------------------

class TestTUIProviderRegistration:
    """Verify the module-level registration code in provider.py."""

    def test_registered_as_tui(self):
        """The module registers itself as 'tui' in ProviderRegistry."""
        # Re-execute the side-effect (already imported; conftest resets registry)
        import importlib
        import agentx.ui.tui.provider as tui_provider_mod
        importlib.reload(tui_provider_mod)

        providers = ProviderRegistry.list_providers()
        assert "tui" in providers, (
            f"'tui' should be registered, got: {providers}"
        )

    def test_set_as_default(self):
        """The module registers itself as the *default* provider."""
        import importlib
        import agentx.ui.tui.provider as tui_provider_mod
        importlib.reload(tui_provider_mod)

        default = ProviderRegistry.get_default()
        assert type(default).__name__ == "TUIProvider", (
            f"Expected TUIProvider, got {type(default).__name__}"
        )

    def test_get_tui_provider(self):
        """ProviderRegistry.get('tui') returns the same TUIProvider instance."""
        import importlib
        import agentx.ui.tui.provider as tui_provider_mod
        importlib.reload(tui_provider_mod)

        provider = ProviderRegistry.get("tui")
        assert type(provider).__name__ == "TUIProvider", (
            f"Expected TUIProvider, got {type(provider).__name__}"
        )

    def test_registration_does_not_raise_on_reimport(self):
        """Re-loading the module should not crash (idempotent register)."""
        import importlib
        import agentx.ui.tui.provider

        # First load (happened at import time) — reload to trigger again
        importlib.reload(agentx.ui.tui.provider)

        # Should still be registered
        assert "tui" in ProviderRegistry.list_providers()
