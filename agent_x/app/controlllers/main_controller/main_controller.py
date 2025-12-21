from agent_x.app.controlllers.main_controller.imain_controller import IMainController
from agent_x.app.controlllers.main_controller.commands.cli_commands import QuitCommand, ClearCommand, ReadFile, \
    HelpCommand
from agent_x.app.controlllers.main_controller.commands.llm_chat_commands import AIChat, AITools, AIRouterAgents, \
    AIReactTools, AISearch, AIFunction
from agent_x.app.controlllers.main_controller.commands.math_commands import SumCommand
from agent_x.core.controllers.command_line_controller.commands_controller import CommandsController

class MainController(CommandsController, IMainController):
    def close(self) -> None:
        print("CLOSE")

    def __init__(self):
        super().__init__()
        self.add_command(SumCommand("sum"))
        self.add_command(QuitCommand("q", self))
        self.add_command(ClearCommand("cls"))
        self.add_command(AIChat("chat"))
        self.add_command(AITools("tools"))
        self.add_command(AIRouterAgents("router"))
        self.add_command(AIReactTools("react"))
        self.add_command(AISearch("search"))
        self.add_command(ReadFile("read"))
        self.add_command(AIFunction("f"))
        self.add_command(HelpCommand("help", self))