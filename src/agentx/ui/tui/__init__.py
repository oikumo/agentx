"""TUI Module - Isolated Textual-based UI implementation.

This module is completely isolated from the existing UI module.
It provides a modern TUI using the Textual framework with dependency inversion.
"""

# Re-export provider for easy access
from agentx.ui.tui.provider import TUIProvider

__all__ = ["TUIProvider"]