#!/usr/bin/env python3
"""Debug TUI to see what's happening."""

from textual.app import App
from agentx.ui.tui.screens.main_screen import MainTUIScreen

class DebugApp(App):
    """Debug app that shows events."""
    
    def on_mount(self) -> None:
        self.push_screen(MainTUIScreen())
        self.notify("Debug mode: Press keys to see events")
    
    def on_key(self, event) -> None:
        """Log all key events."""
        self.notify(f"Key pressed: {event.key}")
        print(f"KEY PRESSED: {event.key}")
    
    def on_button_pressed(self, event) -> None:
        """Log button events."""
        self.notify(f"Button clicked: {event.button.id}")
        print(f"BUTTON CLICKED: {event.button.id}")

if __name__ == "__main__":
    print("Starting DEBUG TUI...")
    print("Press any key - you should see notifications")
    print("Click buttons - you should see notifications")
    print("Press 'q' to quit")
    app = DebugApp()
    app.run()
    print("App closed")