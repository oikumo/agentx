import unittest

from agentx.controllers.rag_controller.rag_controller import RagController
from agentx.views.rag_view.rag_view import RagView
from agentx.ui.ui import UIConsoleBase, UIMessage

class TestRagView(unittest.TestCase):
    def test_show(self):
        class Console(UIConsoleBase):
            def print_now(self, message: str) -> None:
                pass

            def capture_input(self, mode_text: str) -> str | None:
                pass

            def print_line(self, line: UIMessage) -> None:
                assert line.message == "close"

        controller = RagController()
        view = RagView(controller, Console())
        controller.view = view
        view.show()
