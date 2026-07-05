"""AgentX TUI framework — reusable base classes for TUI development.

This package is the "library for agentx TUI development": base classes that
absorb the boilerplate duplicated across the existing TUI screens/adapters, plus
reusable widgets and helpers.  New TUI screens (and new TUI variants) inherit
from these bases instead of re-implementing the same scaffolding.

Public API:

    - :class:`BaseAgentXScreen`        — base for full (non-modal) screens.
    - :class:`BaseAgentXModalScreen`   — base for modal dialogs (dismiss guard).
    - :class:`BaseAgentXApp`           — base TUI application (TTY check + initial screen).
    - :class:`BaseScreenAdapter`       — base for view adapters that delegate to a Screen.
    - :class:`NavigationMixin`         — ``navigate_to_child`` for host screens.
    - :func:`register_partner`         — metaclass-safe ABC partner registration.
    - :class:`SessionStatusBar`, :class:`WelcomePanel`, :class:`MenuGrid`,
      :class:`CommandInput`, :class:`ChatMessage` — reusable widgets.

Design: ``design_001_tui_framework.md``.
"""

from __future__ import annotations

from agentx.ui.tui.framework.base_adapter import BaseScreenAdapter
from agentx.ui.tui.framework.base_app import BaseAgentXApp
from agentx.ui.tui.framework.base_modal import BaseAgentXModalScreen
from agentx.ui.tui.framework.base_screen import BaseAgentXScreen, NavigationMixin
from agentx.ui.tui.framework.partner import register_partner
from agentx.ui.tui.framework.widgets import (
    ChatMessage,
    CommandInput,
    MenuGrid,
    SessionStatusBar,
    WelcomePanel,
)

__all__ = [
    "BaseAgentXScreen",
    "BaseAgentXModalScreen",
    "BaseAgentXApp",
    "BaseScreenAdapter",
    "NavigationMixin",
    "register_partner",
    "SessionStatusBar",
    "WelcomePanel",
    "MenuGrid",
    "CommandInput",
    "ChatMessage",
]
