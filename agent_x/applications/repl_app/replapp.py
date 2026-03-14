from agent_x.applications.repl_app.controllers.main_controller.main_controller import \
    MainController
from agent_x.applications.repl_app.tui.app import TextualReplApp
from agent_x.common.logger import log_info


class ReplApp:
    def __init__(self):
        pass

    def run(self):
        log_info("App running")
        controller = MainController()
        tui = TextualReplApp(controller=controller)
        tui.run()
