from agent_x.common.logger import log_info
from agent_x.applications.repl_app.command_line_controller.command_line import CommandLine
from agent_x.applications.repl_app.controlllers.main_controller.main_controller import MainController


class ReplApp:
    def __init__(self):
        pass
    def run(self):
        log_info("App running")
        controller = MainController()
        loop = CommandLine(controller)

        while True:
            loop.run()
