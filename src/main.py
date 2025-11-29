import os
from dotenv import load_dotenv

from src.command_line import CommandLine
from src.commands.commands import add
from src.utils.utils import clear_console

load_dotenv()

if __name__ == "__main__":
    commands = {
        "cls": clear_console,
        "q": lambda: print(f"QUIT COMMAND"),
        "h": lambda x: print(f"HELP COMMAND {x}"),
        "sum": lambda args : add(args)
    }

    loop = CommandLine(commands)

    while True:
        loop.run()
