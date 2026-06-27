from __future__ import annotations
import getpass
import os
import sys

from dotenv import load_dotenv

from agentx.ui.screens.main.main_controller import MainController
from agentx.ui.providers import ProviderRegistry

load_dotenv()

if not os.getenv("OPENROUTER_API_KEY"):
    os.environ["OPENROUTER_API_KEY"] = getpass.getpass(
        "Enter your OpenRouter API key: "
    )

def show():
    import importlib.metadata
    version = importlib.metadata.version("agentx")
    print(f"agentx {version}")
    print()

def main():
    show()
    
    # Check if running in a proper terminal for TUI
    use_tui = "--no-tui" not in sys.argv
    has_tty = sys.stdin.isatty() and sys.stdout.isatty()
    
    if use_tui:
        if not has_tty:
            print("⚠️  Warning: Not running in a proper terminal (TTY not detected).")
            print("   TUI keyboard/mouse input will not work correctly.")
            print("   Falling back to console mode...")
            print("   To use TUI, run directly in a terminal (not piped).")
            print()
            use_tui = False
    
    if use_tui:
        print("🎨 Starting modern TUI... (press 'q' to quit, 'h' for help)")
        print()
        ui_provider = ProviderRegistry.get_default()
    else:
        print("💻 Using console mode...")
        print()
        ui_provider = ProviderRegistry.get("console")
    
    # Initialize UI
    ui_provider.initialize()
    
    # Create controller first (with console view as fallback)
    main_controller = MainController()
    
    # Create view via provider
    main_view = ui_provider.create_main_view(main_controller)
    
    # Replace controller's view
    main_controller.view = main_view
    
    # Start application
    try:
        main_view.show()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if use_tui:
            print("Falling back to console mode...")
            # Try console fallback
            console_provider = ProviderRegistry.get("console")
            console_view = console_provider.create_main_view(main_controller)
            main_controller.view = console_view
            console_view.show()
    finally:
        # Cleanup
        ui_provider.shutdown()


def start():
    main()

if __name__ == "__main__":
    main()