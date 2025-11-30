from dotenv import load_dotenv

from ai.router_agents.router_agent import router_agent
from src.ai.react_agents.analyze_csv_agent import analyze_csv
from src.ai.react_agents.create_qr_agent import create_qr
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
        "qr": lambda args : create_qr(),
        "csv": lambda args: analyze_csv("../resources/episode_info.csv"),
        "router": lambda args: router_agent(),
    }

    loop = CommandLine(commands)

    while True:
        loop.run()
