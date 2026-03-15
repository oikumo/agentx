from agent_x.applications.repl_app.command_line_controller.command import Command, CommandResult
from agent_x.common.logger import log_info, log_warning
from agent_x.utils.utils import safe_int

class SumCommand(Command):
    def __init__(self, key: str):
        super().__init__(key, description="Add two integers: sum <a> <b>")

    def run(self, arguments: list[str]):
        match arguments:
            case (x, y):
                if safe_int(x) is not None and safe_int(y) is not None:
                    result = str(int(x) + int(y))
                    return CommandResultPrint(result)
                else:
                    log_warning("invalid params for sum command")
            case _:
                log_warning("invalid command")
        return None


class CommandResultPrint(CommandResult):
    def __init__(self, message: str):
        self._message = message

    def apply(self):
        log_info(self._message)
