#!/usr/bin/env python3
"""
Interactive TUI Test Script

This script tests the TUI in a proper terminal environment.
Run this DIRECTLY in a terminal (not piped) to test:

    uv run python scripts/test_tui_interactive.py

DO NOT run like this (will fail):
    uv run python scripts/test_tui_interactive.py | cat

Requirements:
- Must be run in a proper terminal (TTY)
- Textual framework installed
- Terminal supports ANSI escape codes

Test Checklist:
□ TUI renders correctly
□ Press 'q' - should quit application
□ Press 'c' - should show "Opening Chat" notification
□ Press 'r' - should show "Opening RAG" notification  
□ Press 'h' - should show help message
□ Click buttons with mouse - should trigger actions
□ Type in input field and press Enter - should process command
□ Press Ctrl+L - should focus input field
"""

import sys
import os

# Add src to path
src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(src_path, "src"))


def check_environment():
    """Check if running in a proper terminal."""
    print("=" * 60)
    print("TUI Environment Check")
    print("=" * 60)
    
    stdin_tty = sys.stdin.isatty()
    stdout_tty = sys.stdout.isatty()
    stderr_tty = sys.stderr.isatty()
    
    print(f"stdin is TTY:  {stdin_tty}")
    print(f"stdout is TTY: {stdout_tty}")
    print(f"stderr is TTY: {stderr_tty}")
    print()
    
    if not (stdin_tty and stdout_tty):
        print("❌ ERROR: Not running in a proper terminal!")
        print()
        print("The TUI requires a proper terminal (TTY) to receive")
        print("keyboard and mouse input. You are likely running this")
        print("script with piped output or in an unsupported environment.")
        print()
        print("To fix:")
        print("  1. Run directly in a terminal:")
        print("     uv run python scripts/test_tui_interactive.py")
        print()
        print("  2. Do NOT pipe the output:")
        print("     ❌ uv run python scripts/test_tui_interactive.py | cat")
        print()
        return False
    
    print("✓ Environment OK - TUI should work correctly")
    print()
    return True


def main():
    """Run the TUI test."""
    if not check_environment():
        return 1
    
    print("=" * 60)
    print("Starting TUI Test")
    print("=" * 60)
    print()
    print("Instructions:")
    print("  • Press 'q' to quit")
    print("  • Press 'c' to test Chat action")
    print("  • Press 'r' to test RAG action")
    print("  • Press 'h' to show help")
    print("  • Click buttons with mouse")
    print("  • Type commands in the input field")
    print("  • Press Ctrl+L to focus input")
    print()
    print("Starting TUI in 3 seconds...")
    print()
    
    import time
    time.sleep(3)
    
    from agentx.ui.tui.app import TUIApplication
    
    app = TUIApplication()
    
    try:
        app.run()
        print()
        print("✓ TUI closed successfully!")
        return 0
    except KeyboardInterrupt:
        print()
        print("✓ Interrupted by user")
        return 0
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())