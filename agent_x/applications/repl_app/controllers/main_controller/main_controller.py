from agent_x.applications.repl_app.command_line_controller.commands_controller import CommandsController
from agent_x.common.logger import log_info

class Actions:
    def close(self) -> None:
        log_info("CLOSE")
        exit(0)


class MainController(CommandsController):
    def __init__(self):
        super().__init__()