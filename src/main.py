from dotenv import load_dotenv

from ai.router_agents.router_react_agent import router_agent
from src.command_line import CommandLine
from src.commands.commands import add
from src.utils.utils import clear_console

load_dotenv()

if __name__ == "__main__":
    commands = {
        "cls": lambda _ : clear_console(),
        "q": lambda _ : print(f"QUIT COMMAND"),
        "h": lambda _ : print(f"HELP COMMAND"),
        "sum": lambda args : add(args),
        "router": lambda args: router_agent(),
    }

    loop = CommandLine(commands)

    while True:
        loop.run()
