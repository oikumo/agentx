from agent_x.core.repl.command import Command
from agent_x.core.utils.utils import safe_int


class SumCommand(Command):
    def __init__(self, key: str):
        super().__init__(key)

    def run(self, arguments: list[str]):
        print(f"sum command args: {arguments}")
        match arguments:
            case (x, y):
                if safe_int(x) and safe_int(y):
                    result = str(int(x) + int(y))
                    print(f"{result}")
                else:
                    print(f"invalid params for sum command")
            case _:
                print("invalid command")
