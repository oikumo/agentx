from __future__ import annotations
import getpass
import os
import warnings

# Suppress upstream pydantic.v1 compatibility warning on Python 3.14+.
# This warning originates from langchain_core importing pydantic.v1 for
# backward compatibility — it is outside our control and adds noise to
# every agent invocation. The actual functionality is unaffected.
warnings.filterwarnings(
    "ignore",
    message=r"Core Pydantic V1 functionality isn't compatible with Python 3\.14",
    category=UserWarning,
)

from dotenv import load_dotenv

from agentx.ui.screens.main.main_controller import MainController
from agentx.ui.providers import ProviderRegistry

# ``override=True`` makes the ``.env`` file authoritative for secrets/config:
# ``python-dotenv`` by default does NOT overwrite an existing ``os.environ``
# value, so a stale shell export (e.g. a dead ``NVIDIA_API_KEY`` left over in
# ``~/.bashrc``) would silently mask the valid key written in this repo's
# ``.env`` — and ``ChatNVIDIA`` would then 403 with no actionable hint.
# Passing ``override=True`` means the ``.env`` value always wins, which is the
# intent of having a committed ``.env`` for credentials in the first place.
# (Also fixes the symmetric case at ``llama_cpp_factory.py:6``.)
load_dotenv(override=True)

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

    # Console REPL is the only UI (TUI removed). Legacy --tui/--no-tui
    # flags are accepted as no-ops for backwards compatibility.
    ui_provider = ProviderRegistry.get("console")

    print("💻 Using console mode.")
    print()
    
    # Initialize UI
    ui_provider.initialize()
    
    # Create controller with provider for sub-view creation
    main_controller = MainController(provider=ui_provider)
    
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
    finally:
        # Cleanup
        ui_provider.shutdown()


def start():
    main()

if __name__ == "__main__":
    main()