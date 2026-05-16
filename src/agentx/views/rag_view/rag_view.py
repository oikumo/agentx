from __future__ import annotations
from typing import TYPE_CHECKING

from agentx.ui.ui_console import UIConsole

if TYPE_CHECKING:
    from agentx.controllers.rag_controller.rag_controller import RagController

import time


class RagView:
    controller: RagController

    def __init__(self, controller: RagController):
        self.controller = controller
        self.console = UIConsole("(rag)")

    def show(self):
        while True:
            user_input = self.console.capture_input()
            self.controller.do_web_ingestion()
            time.sleep(3)
            self.controller.close()
            return

    def print_message(self, message: str):
        self.console.info(message).flush()