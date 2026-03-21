from dotenv import load_dotenv

from app.repl.command_line_controller.commands_controller import CommandsController
from app.repl.commands.cli_commands import QuitCommand, ClearCommand, ReadFile, HelpCommand

from app.repl.commands.llm_chat_commands import AIChat, AITools, AIRouterAgents, AIReactTools, AISearch, AIFunction, RagPDF
from app.repl.commands.llm_graph_commands import AIGraphSimple, AIGraphChains, AIGraphReflexion
from app.repl.commands.math_commands import SumCommand
from app.repl.controllers.main_controller.main_controller import MainController, Actions
from app.repl.replapp import ReplApp

load_dotenv()

def create_controller() -> CommandsController:
    main_controller = MainController()
    main_controller.add_command(SumCommand("sum"))
    main_controller.add_command(QuitCommand("quit"))
    main_controller.add_command(ClearCommand("clear"))
    main_controller.add_command(AIChat("chat"))
    main_controller.add_command(AITools("tools"))
    main_controller.add_command(AIRouterAgents("router"))
    main_controller.add_command(AIReactTools("react"))
    main_controller.add_command(AISearch("search"))
    main_controller.add_command(ReadFile("read"))
    main_controller.add_command(AIFunction("function"))
    main_controller.add_command(RagPDF("rag"))
    main_controller.add_command(AIGraphSimple("graph"))
    main_controller.add_command(AIGraphChains("chains"))
    main_controller.add_command(AIGraphReflexion("reflex"))
    main_controller.add_command(HelpCommand("help", main_controller))

    return main_controller

if __name__ == "__main__":
    controller = create_controller()

    actions = Actions()
    for command in controller.commands.values():
        command.set_actions_controller(actions)

    ReplApp(controller).run()
