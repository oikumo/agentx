from __future__ import annotations

import getpass
import os

from dotenv import load_dotenv

from app.commands import (
    QuitCommand,
    ClearCommand,
    ReadFile,
    HelpCommand,
    AIChat,
    AIRouterAgents,
    AIReactTools,
    AISearch,
    AIFunction,
    RagPDF,
    AIGraphSimple,
    AIGraphChains,
    AIGraphReflexion,
    SumCommand,
)
from app.repl import IMainController, ReplApp

load_dotenv()

if not os.getenv("OPENROUTER_API_KEY"):
    os.environ["OPENROUTER_API_KEY"] = getpass.getpass(
        "Enter your OpenRouter API key: "
    )


def create_controller() -> IMainController:
    main_controller = IMainController()
    main_controller.add_command(SumCommand("sum", main_controller))
    main_controller.add_command(QuitCommand("quit", main_controller))
    main_controller.add_command(ClearCommand("clear", main_controller))
    main_controller.add_command(AIChat("chat", main_controller))
    main_controller.add_command(AIRouterAgents("router", main_controller))
    main_controller.add_command(AIReactTools("react", main_controller))
    main_controller.add_command(AISearch("search", main_controller))
    main_controller.add_command(ReadFile("read", main_controller))
    main_controller.add_command(AIFunction("function", main_controller))
    main_controller.add_command(RagPDF("rag", main_controller))
    main_controller.add_command(AIGraphSimple("graph", main_controller))
    main_controller.add_command(AIGraphChains("chains", main_controller))
    main_controller.add_command(AIGraphReflexion("reflex", main_controller))
    main_controller.add_command(HelpCommand("help", main_controller))

    return main_controller


def main():
    controller = create_controller()
    ReplApp(controller).run()


if __name__ == "__main__":
    main()
