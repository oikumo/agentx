import os
from src.cli.command_line import CommandLine
from dotenv import load_dotenv

from src.controllers.main_controller import MainController

load_dotenv()

if __name__ == "__main__":
    controller = MainController()
    loop = CommandLine(controller)
    loop.run()