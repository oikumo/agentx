from sympy.strategies.core import switch

from src.controllers.base_controller import BaseController
from src.utils.utils import safe_int

class CommandLine:
    controller: BaseController

    def __init__(self, controller: BaseController):
        self.controller = controller

    def run(self):
        while True:
            self.show(f"(agent-x)/{self.controller.info()}")
            command = list(map(str, input().split()))
            if command == ["quit"] or command == ["q"]:
                self.show("Finish")
                break

            match command:
                case ["sum", x, y]:
                    if safe_int(x) and safe_int(y):
                        result = str(int(x) + int(y))
                        self.show(" ".join(command) + " -> " + result)
                    else:
                        self.show("Invalid params for sum command")
                case ["help"]:
                    self.show("HELP:")
                case _:
                    self.show(f"Invalid command: {command}")


    def show(self, message: str):
        print(message)