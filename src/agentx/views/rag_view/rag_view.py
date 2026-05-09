from abc import ABC, abstractmethod

import time

from agentx.views.ui.ui import UIConsoleBase

class RagViewPartner(ABC):
    @abstractmethod
    def close(self) -> None: ...


class RagView:
    def __init__(self, partner: RagViewPartner, console: UIConsoleBase):
        self.partner = partner
        self.console = console

    def show(self):
        self.console.capture_input("(agentx/rag) ")
        time.sleep(3)
        self.partner.close()

    def print_message(self, message: str):
        self.console.info(message).flush()