from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentx.controllers.rag_controller.rag_controller import RagController

from agentx.ui.ui import UIConsoleBase
import time


class RagView:
    controller: RagController

    def __init__(self, controller: RagController, console: UIConsoleBase):
        self.partner = controller
        self.console = console

    def show(self):
        self.console.capture_input()
        time.sleep(3)
        self.partner.close()

    def print_message(self, message: str):
        self.console.info(message).flush()