from agent_x.app.commands.cli_commands import QuitCommand, HelpCommand, ClearCommand
from agent_x.app.commands.llm_chat_commands import AIChat, AITools, AIRouterAgents, AIReactTools, AISearch
from agent_x.app.commands.math_commands import SumCommand
from agent_x.core.repl.command_line import CommandLine
from agent_x.core.repl.commands_table import CommandsTable


class App:
    def __init__(self):
        pass
    def run(self):
        commands_table = CommandsTable()
        commands_table.add_command(SumCommand("sum"))
        commands_table.add_command(QuitCommand("q"))
        commands_table.add_command(HelpCommand("h"))
        commands_table.add_command(ClearCommand("cls"))
        commands_table.add_command(AIChat("chat"))
        commands_table.add_command(AITools("tools"))
        commands_table.add_command(AIRouterAgents("router"))
        commands_table.add_command(AIReactTools("react"))
        commands_table.add_command(AISearch("search"))

        """
        commands_list = list(commands.keys())
        def print_commands():
            for command in commands_list:
                print(command)
        """
        # commands["list"] = lambda _ : print_commands()

        loop = CommandLine(commands_table)

        while True:
            loop.run()
