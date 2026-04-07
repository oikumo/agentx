from __future__ import annotations

import getpass
import os

from dotenv import load_dotenv

from controllers.main_controller.commands import (
    QuitCommand,
    ClearCommand,
    HelpCommand,
    AIChat,
    SumCommand,
)
from controllers.main_controller.main_controller import MainController
from controllers.main_controller.repl import ReplApp

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
    main_controller.add_command(AIChat("chat", main_controller))
    main_controller.add_command(HelpCommand("help", main_controller))

    return main_controller


def main():
    controller = create_controller()
    ReplApp(controller).run()


if __name__ == "__main__":
    main()
