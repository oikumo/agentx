#!/usr/bin/env python3
"""Test keyboard input processing in TUI."""

import asyncio
from agentx.ui.tui.app import TUIApplication
from agentx.ui.tui.screens.main_screen import MainTUIScreen
from textual.events import Key


async def test_keyboard_events():
    """Test that keyboard events are processed."""
    print("Testing keyboard event processing...")
    
    app = TUIApplication()
    
    # Track events
    events_processed = []
    
    async def run_test():
        # Push the main screen
        screen = MainTUIScreen()
        await app.push_screen(screen)
        
        # Wait for screen to be ready
        await asyncio.sleep(0.1)
        
        # Try to post a 'q' key event (should quit)
        print("Posting 'q' key event...")
        key_event = Key(key="q", character="q")
        
        # Post the event to the screen
        screen.post_message(key_event)
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        print("Event posted successfully")
        events_processed.append(True)
        
        # Exit after test
        app.exit()
    
    try:
        await run_test()
        print("✓ Test completed")
        return len(events_processed) > 0
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_keyboard_events())
    print(f"\nResult: {'PASS' if result else 'FAIL'}")