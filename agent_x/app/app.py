from agent_x.app.controlllers.main_controller.main_controller import MainController
from agent_x.core.common.logger import log_info
from agent_x.core.controllers.command_line_controller.command_line import CommandLine


class App:
    def __init__(self):
        pass
    def run(self):
        log_info("App running")
        controller = MainController()
        loop = CommandLine(controller)

        while True:
            loop.run()
