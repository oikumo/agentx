from agent_x.applications.repl_app.command_line_controller.commands_controller import \
    CommandsController
from agent_x.applications.repl_app.commands.cli_commands import (ClearCommand,
                                                                 HelpCommand,
                                                                 QuitCommand,
                                                                 ReadFile)
from agent_x.applications.repl_app.commands.llm_chat_commands import (
    AIChat, AIFunction, AIReactTools, AIRouterAgents, AISearch, AITools,
    RagPDF)
from agent_x.applications.repl_app.commands.llm_graph_commands import (
    AIGraphChains, AIGraphReflexion, AIGraphSimple)
from agent_x.applications.repl_app.commands.math_commands import SumCommand
from agent_x.applications.repl_app.controllers.main_controller.imain_controller import \
    IMainController
from agent_x.common.logger import log_info


class MainController(CommandsController, IMainController):
    def close(self) -> None:
        log_info("CLOSE")

    def __init__(self):
        super().__init__()
        self.add_command(SumCommand("sum"))
        self.add_command(QuitCommand("quit", self))
        self.add_command(ClearCommand("clear"))
        self.add_command(AIChat("chat"))
        self.add_command(AITools("tools"))
        self.add_command(AIRouterAgents("router"))
        self.add_command(AIReactTools("react"))
        self.add_command(AISearch("search"))
        self.add_command(ReadFile("read"))
        self.add_command(AIFunction("function"))
        self.add_command(RagPDF("rag"))
        self.add_command(AIGraphSimple("graph"))
        self.add_command(AIGraphChains("chains"))
        self.add_command(AIGraphReflexion("reflex"))
        self.add_command(HelpCommand("help", self))
