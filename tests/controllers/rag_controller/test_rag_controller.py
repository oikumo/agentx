from __future__ import annotations

import unittest
from agentx.controllers.rag_controller.rag_controller import RagController
from agentx.views.rag_view.rag_view import RagView
from agentx.views.ui.ui import UIConsoleBase, UIMessage


class TestRagController(unittest.TestCase):
    def test_something(self):

        class Console(UIConsoleBase):
            def print_now(self, message: str) -> None:
                pass

            def print_line(self, line: UIMessage) -> None:
                pass

            def capture_input(self, mode_text: str) -> str | None:
                pass

        class StubRagView(RagView):
            def __init__(self, controller: RagController) -> None:
                super().__init__(controller, Console())
                self.controller = controller

            def show(self) -> None:
                pass

            def print_message(self, message: str) -> None:
                pass

        rag = RagController()
        rag.view = StubRagView(rag)
        rag.show()



