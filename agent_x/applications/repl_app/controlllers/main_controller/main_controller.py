from agent_x.applications.repl_app.commands.cli_commands import QuitCommand, ClearCommand, HelpCommand, \
    ReadFile
from agent_x.applications.repl_app.commands.llm_chat_commands import AIChat, AITools, AIRouterAgents, \
    AIReactTools, AISearch, AIFunction, RagPDF
from agent_x.applications.repl_app.commands.llm_graph_commands import AIGraphSimple, AIGraphChains, AIGraphReflexion
from agent_x.applications.repl_app.commands.math_commands import SumCommand
from agent_x.applications.repl_app.controlllers.main_controller.imain_controller import IMainController
from agent_x.applications.repl_app.command_line_controller.commands_controller import CommandsController

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
        self.add_command(RagPDF("rag"))
        self.add_command(AIGraphSimple("graph"))
        self.add_command(AIGraphChains("chains"))
        self.add_command(AIGraphReflexion("reflex"))
        self.add_command(HelpCommand("help", self))