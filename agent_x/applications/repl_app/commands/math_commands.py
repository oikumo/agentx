from agent_x.applications.repl_app.command_line_controller.command import Command
from agent_x.common.logger import log_info, log_warning
from agent_x.utils.utils import safe_int


class SumCommand(Command):
    def __init__(self, key: str):
        super().__init__(key)

    def run(self, arguments: list[str]):
        match arguments:
            case (x, y):
                if safe_int(x) and safe_int(y):
                    result = str(int(x) + int(y))
                    log_info(f"{result}")
                else:
                    log_warning("invalid params for sum command")
            case _:
                log_warning("invalid command")
