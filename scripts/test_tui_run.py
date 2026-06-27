#!/usr/bin/env python3
"""Simple TUI test - just run the app."""

from agentx.ui.tui.app import TUIApplication

if __name__ == "__main__":
    print("Starting AgentX TUI...")
    app = TUIApplication()
    app.run()
    print("TUI closed.")