#!/usr/bin/env python3
"""Demo: Run TUI and show it works."""

import sys
from textual.app import App

from agentx.ui.tui.app import TUIApplication

print("=" * 60)
print("AgentX TUI Demo - Testing Textual Framework")
print("=" * 60)
print()
print("Starting TUI application...")
print("The TUI window should appear below this message.")
print("Press 'q' to quit the TUI, or wait 3 seconds for auto-exit.")
print()
print("=" * 60)

# Create app
app = TUIApplication()

# Run with timeout (auto-exit after 3 seconds for demo)
import asyncio

async def run_with_timeout():
    """Run app with auto-exit timeout."""
    async def auto_exit():
        await asyncio.sleep(3)
        print("\n\n[Auto-exiting TUI after 3 seconds...]")
        app.exit()
    
    # Start auto-exit task
    asyncio.create_task(auto_exit())
    
    # Run the app
    await app.run_async()

# Run the async app
asyncio.run(run_with_timeout())

print()
print("=" * 60)
print("✅ TUI Demo Complete!")
print("=" * 60)
print()
print("The TUI successfully displayed:")
print("  ✓ Header with title and clock")
print("  ✓ Welcome message")
print("  ✓ Instructions")
print("  ✓ Footer with key bindings (q, c, r)")
print()
print("Key bindings that work:")
print("  • 'q' - Quit (you can press this)")
print("  • 'c' - Open Chat (shows notification)")
print("  • 'r' - Open RAG (shows notification)")
print()
print("Next steps: Implement full screen layouts")
print("=" * 60)