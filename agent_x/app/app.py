from agent_x.app.commands.cli_commands import QuitCommand, HelpCommand, ClearCommand
from agent_x.app.commands.llm_chat_commands import AIChat, AITools, AIRouterAgents, AIReactTools, AISearch
from agent_x.app.commands.math_commands import SumCommand
from agent_x.core.repl.command_line import CommandLine
from agent_x.core.repl.controllers.commands_controller import CommandsController


class App:
    def __init__(self):
        pass
    def run(self):
        commands_controller = CommandsController()
        commands_controller.add_command(SumCommand("sum"))
        commands_controller.add_command(QuitCommand("q"))
        commands_controller.add_command(ClearCommand("cls"))
        commands_controller.add_command(AIChat("chat"))
        commands_controller.add_command(AITools("tools"))
        commands_controller.add_command(AIRouterAgents("router"))
        commands_controller.add_command(AIReactTools("react"))
        commands_controller.add_command(AISearch("search"))
        commands_controller.add_command(HelpCommand("help", commands_controller))

        loop = CommandLine(commands_controller)

        while True:
            loop.run()
