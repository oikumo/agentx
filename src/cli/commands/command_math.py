from abc import ABC

from src.cli.commands.command_base import CommandBase
from src.utils.utils import safe_int


class CommandMath(CommandBase):
    def __init__(self):
        super().__init__()
        self.key = "sum"

    def run(self, arguments):
        print(f"SUM COMMAND {' '.join(arguments)}")

        match arguments:
            case[x, y]:
                if safe_int(x) and safe_int(y):
                    result = str(int(x) + int(y))
                    print(f"-> {result}")
                else:
                    print("Invalid params for sum command")

            case _:
                print("Invalid command")


