from __future__ import annotations
import getpass
import os

from dotenv import load_dotenv

from agentx.controllers.main_controller.main_controller import MainController

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
    main_controller = MainController()
    main_controller.run()


def start():
    main()

if __name__ == "__main__":
    main()
