#!/usr/bin/env python3
"""Test the full MainTUIScreen implementation."""

from agentx.ui.tui.app import TUIApplication

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Full MainTUIScreen Implementation")
    print("=" * 60)
    print()
    print("Starting TUI with:")
    print("  ✓ Header with clock")
    print("  ✓ Welcome panel")
    print("  ✓ Menu buttons (Chat, RAG, Help)")
    print("  ✓ Command input field")
    print("  ✓ Session status bar")
    print("  ✓ Footer with key bindings")
    print()
    print("Press 'q' to quit, or try:")
    print("  • Click buttons with mouse")
    print("  • Press 'c' for Chat")
    print("  • Press 'r' for RAG")
    print("  • Press 'h' for Help")
    print("  • Type commands in input field")
    print()
    print("=" * 60)
    print()
    
    app = TUIApplication()
    app.run()
    
    print()
    print("✅ TUI closed successfully!")