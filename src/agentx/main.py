from __future__ import annotations

import getpass
import os

from dotenv import load_dotenv

from agentx.controllers.main_controller.commands import (
    QuitCommand,
    ClearCommand,
    HelpCommand,
    AIChat,
    SumCommand, HistoryCommand,
    NewCommand, PetriNetStatusCommand, PetriNetPrintCommand,
    GoalCommand,
)
from agentx.controllers.main_controller.main_controller import MainController


load_dotenv()

if not os.getenv("OPENROUTER_API_KEY"):
    os.environ["OPENROUTER_API_KEY"] = getpass.getpass(
        "Enter your OpenRouter API key: "
    )


def create_controller() -> MainController:
    main_controller = MainController()
    main_controller.add_command(SumCommand("sum", main_controller))
    main_controller.add_command(QuitCommand("quit", main_controller))
    main_controller.add_command(ClearCommand("clear", main_controller))
    main_controller.add_command(HelpCommand("help", main_controller))
    main_controller.add_command(HistoryCommand("history", main_controller))
    main_controller.add_command(AIChat("chat", main_controller))
    main_controller.add_command(NewCommand("new", main_controller))
    main_controller.add_command(PetriNetStatusCommand("status", main_controller))
    main_controller.add_command(PetriNetPrintCommand("petri-print", main_controller))
    main_controller.add_command(GoalCommand("goal", main_controller))

    return main_controller

def show():
    import importlib.metadata
    version = importlib.metadata.version("agentx")
    print(f"agentx {version}")
    print()

def main():
    show()
    
    main_controller = create_controller()
    main_controller.run()


def start():
    main()

if __name__ == "__main__":
    main()
