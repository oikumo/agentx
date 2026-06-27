"""
Shared fixtures and mocks for TUI tests.

Provides reusable mock objects so each test file doesn't need to
redefine the same mock controllers, mock apps, and helper assertions.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, create_autospec

import pytest

from agentx.ui.interfaces import (
    IChatView,
    IChatViewPartner,
    IMainView,
    IMainViewPartner,
    IRagView,
    IRagViewPartner,
    IUIProvider,
)


# ---------------------------------------------------------------------------
# Mock controllers  (implements the *Partner interfaces)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_main_controller() -> MagicMock:
    """Fully featured mock of a MainController (IMainViewPartner)."""
    mock = MagicMock(spec=IMainViewPartner)
    mock.run_command = MagicMock()
    mock.print_message = MagicMock()
    mock.print_warring_message = MagicMock()
    mock.print_error_message = MagicMock()
    mock.error = MagicMock()
    return mock


@pytest.fixture
def mock_chat_controller() -> MagicMock:
    """Fully featured mock of a ChatController (IChatViewPartner)."""
    return MagicMock(spec=IChatViewPartner)


@pytest.fixture
def mock_rag_controller() -> MagicMock:
    """Fully featured mock of a RagController (IRagViewPartner)."""
    return MagicMock(spec=IRagViewPartner)


# ---------------------------------------------------------------------------
# Mock Textual app / screen
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_textual_app() -> MagicMock:
    """Emulate a Textual ``App`` instance with the subset of APIs we use."""
    app = MagicMock()
    app.exit = MagicMock()
    app.notify = MagicMock()
    app.push_screen = MagicMock()
    app.screen = MagicMock()
    app.dom = MagicMock()
    # Allow ``hasattr(self._app, 'notify')`` checks to pass
    app.notify.__bool__ = lambda self: True  # type: ignore[assignment]
    return app


@pytest.fixture
def mock_textual_screen() -> MagicMock:
    """Emulate a Textual ``Screen`` instance."""
    screen = MagicMock()
    screen.query_one = MagicMock()
    screen.app = MagicMock()
    screen.app.exit = MagicMock()
    screen.app.notify = MagicMock()
    screen.dom = MagicMock()
    return screen


# ---------------------------------------------------------------------------
# Helper: verify every abstract method raises TypeError on direct instantiation
# ---------------------------------------------------------------------------

def assert_abstract(cls: type, method_name: str) -> None:
    """Assert that *cls* cannot be instantiated because *method_name* is abstract."""
    import re
    try:
        cls()  # type: ignore[abstract]
    except TypeError as exc:
        assert method_name in str(exc), (
            f"Expected TypeError to mention {method_name!r}, got: {exc}"
        )
    else:
        pytest.fail(f"{cls.__name__} should have been abstract due to {method_name}")


def assert_concrete_implements(
    concrete: type,
    interface: type,
    *method_names: str,
) -> None:
    """Assert that *concrete* (instantiable) implements the given methods."""
    obj = concrete.__new__(concrete)
    for m in method_names:
        assert hasattr(obj, m), (
            f"{concrete.__name__} is missing method {m!r} "
            f"required by {interface.__name__}"
        )


# ---------------------------------------------------------------------------
# Clean registry fixture
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_provider_registry():
    """Reset ``ProviderRegistry`` before & after every test that imports it.

    We monkey-patch the internal dict and default name so tests that register
    providers don't leak across test boundaries.
    """
    import agentx.ui.providers as providers_mod

    old_providers = providers_mod.ProviderRegistry._providers.copy()
    old_default = providers_mod.ProviderRegistry._default

    providers_mod.ProviderRegistry._providers = {}
    providers_mod.ProviderRegistry._default = None

    yield

    providers_mod.ProviderRegistry._providers = old_providers
    providers_mod.ProviderRegistry._default = old_default
