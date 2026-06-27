#!/usr/bin/env python3
"""Simple TUI test - works in any terminal."""

import sys
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, Button
from textual.containers import Container, Vertical
from textual.binding import Binding


class SimpleTestScreen(App):
    """Minimal working TUI."""
    
    CSS = """
    Screen {
        background: #1a1a2e;
    }
    
    Header {
        background: #4a4e69;
        color: white;
    }
    
    Footer {
        background: #22223b;
    }
    
    #welcome {
        background: #333355;
        padding: 2;
        margin: 2;
        text-align: center;
    }
    
    #buttons {
        align: center middle;
    }
    
    Button {
        margin: 1;
        width: 20;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("t", "test", "Test", show=True),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container():
            yield Label("🎨 AgentX TUI Test", id="welcome")
            yield Label("If you see this, Textual is working!", id="welcome")
            yield Label("", id="welcome")
            
            with Vertical(id="buttons"):
                yield Button("Click Me!", variant="primary", id="btn1")
                yield Button("Also Click", variant="success", id="btn2")
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn1":
            self.notify("You clicked the first button! ✅", severity="information")
        elif event.button.id == "btn2":
            self.notify("Second button works too! 🎉", severity="information")
    
    async def action_quit(self) -> None:
        self.exit()
    
    async def action_test(self) -> None:
        self.notify("Test notification! Keyboard works! ⌨️", severity="information")


if __name__ == "__main__":
    print("=" * 60)
    print("AgentX TUI - Simple Test")
    print("=" * 60)
    print()
    print("Starting TUI in 2 seconds...")
    print()
    print("What you should see:")
    print("  • A colored terminal UI")
    print("  • Header with clock")
    print("  • Welcome message")
    print("  • Two clickable buttons")
    print("  • Footer with q and t keys")
    print()
    print("Try:")
    print("  • Press 'q' to quit")
    print("  • Press 't' to test keyboard")
    print("  • Click buttons with mouse")
    print()
    print("=" * 60)
    print()
    
    import time
    time.sleep(2)
    
    app = SimpleTestScreen()
    app.run()
    
    print()
    print("✅ TUI closed! Did it work?")
    print("If you saw a colored UI with buttons, Textual is working!")
    print("If you only saw garbage text, your terminal might not support it.")